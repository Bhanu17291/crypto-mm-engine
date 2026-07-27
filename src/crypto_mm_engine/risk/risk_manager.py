from __future__ import annotations

from collections import deque

from crypto_mm_engine.quoting.models import Quote
from crypto_mm_engine.risk.models import RiskLimits

_HALTED_QUOTE = Quote(bid_price=None, bid_size=0.0, ask_price=None, ask_size=0.0)


class RiskManager:
    """Sits between the quoting engine and the exchange connector: every
    quote is expected to pass through gate_quote before it becomes an order,
    so this is the one place that can veto what the strategy wants to do.

    Two independent ways to halt trading, both requiring a manual reset:
      - kill switch: daily P&L has breached max_daily_loss
      - circuit breaker: fill rate over the recent window has drifted
        outside expected_fill_rate (either direction - too low suggests
        quotes are mispriced or the market's moved on; too high suggests
        we're being adversely selected)

    Position limits and the stale-data check don't need a reset - they
    clear on their own once inventory or data freshness recovers.
    """

    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits
        self._kill_switch_tripped = False
        self._circuit_breaker_tripped = False
        self._recent_cycles: deque[bool] = deque(maxlen=limits.fill_rate_window)

    @property
    def is_halted(self) -> bool:
        return self._kill_switch_tripped or self._circuit_breaker_tripped

    @property
    def is_kill_switch_tripped(self) -> bool:
        return self._kill_switch_tripped

    @property
    def is_circuit_breaker_tripped(self) -> bool:
        return self._circuit_breaker_tripped

    @property
    def fill_rate(self) -> float | None:
        """None until the window has enough samples to mean anything -
        distinct from 0.0, which would claim "definitely no fills"."""
        if not self._recent_cycles:
            return None
        return sum(self._recent_cycles) / len(self._recent_cycles)

    def check_daily_loss(self, daily_pnl: float) -> None:
        if daily_pnl <= -self.limits.max_daily_loss:
            self._kill_switch_tripped = True

    def record_quote_cycle(self, filled: bool) -> None:
        self._recent_cycles.append(filled)
        if len(self._recent_cycles) < self.limits.fill_rate_window:
            return
        rate = sum(self._recent_cycles) / len(self._recent_cycles)
        low, high = self.limits.expected_fill_rate
        if rate < low or rate > high:
            self._circuit_breaker_tripped = True

    def reset_kill_switch(self) -> None:
        self._kill_switch_tripped = False

    def reset_circuit_breaker(self) -> None:
        self._circuit_breaker_tripped = False
        self._recent_cycles.clear()

    def gate_quote(
        self, quote: Quote, inventory: float, last_market_data_ms: int, now_ms: int
    ) -> Quote:
        if self.is_halted:
            return _HALTED_QUOTE
        if now_ms - last_market_data_ms > self.limits.max_stale_data_ms:
            return _HALTED_QUOTE

        bid_price, bid_size = quote.bid_price, quote.bid_size
        ask_price, ask_size = quote.ask_price, quote.ask_size
        if inventory >= self.limits.max_position:
            bid_price, bid_size = None, 0.0
        if inventory <= -self.limits.max_position:
            ask_price, ask_size = None, 0.0

        return Quote(bid_price=bid_price, bid_size=bid_size, ask_price=ask_price, ask_size=ask_size)
