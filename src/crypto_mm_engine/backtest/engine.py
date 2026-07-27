from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

from crypto_mm_engine.backtest.fill_simulator import FillSimulator
from crypto_mm_engine.backtest.models import BacktestConfig, BacktestResult, EquityPoint, Fill, Side
from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, Trade
from crypto_mm_engine.data.synchronizer import OrderBookSynchronizer
from crypto_mm_engine.quoting.avellaneda_stoikov import compute_quotes
from crypto_mm_engine.quoting.models import Quote, QuotingParams


@dataclass(slots=True)
class _PendingQuote:
    apply_at_ms: int
    quote: Quote


class BacktestEngine:
    """Replays a recorded book against the AS quoting engine: at each depth
    update we recompute quotes off the reconstructed book, delay them by
    latency_ms before they actually rest (cancel-replace), and resolve fills
    against the trade tape via queue-position matching.
    """

    def __init__(
        self, quoting_params: QuotingParams, config: BacktestConfig, symbol: str = "BACKTEST"
    ) -> None:
        self.quoting_params = quoting_params
        self.config = config
        self.fill_sim = FillSimulator(config.fees)
        self.pnl = PnLTracker()
        self.sync = OrderBookSynchronizer(symbol)
        self._bid_order_id: int | None = None
        self._ask_order_id: int | None = None
        self._pending: deque[_PendingQuote] = deque()

    def run(
        self, initial_snapshot: DepthSnapshot, events: Iterable[DepthUpdate | Trade]
    ) -> BacktestResult:
        self.sync.apply_snapshot(initial_snapshot)
        equity_curve: list[EquityPoint] = []
        all_fills: list[Fill] = []
        start_ms: int | None = None

        for event in events:
            now_ms = event.event_time_ms if isinstance(event, DepthUpdate) else event.trade_time_ms
            if start_ms is None:
                start_ms = now_ms
            self._apply_due_quotes(now_ms)

            if isinstance(event, DepthUpdate):
                self.sync.apply_update(event)
                self._schedule_requote(now_ms, start_ms)
            else:
                all_fills.extend(self._process_trade(event))

            mid = self.sync.book.mid_price()
            if mid is not None:
                equity_curve.append(
                    EquityPoint(
                        timestamp_ms=now_ms,
                        mid_price=mid,
                        inventory=self.pnl.inventory,
                        realized_pnl=self.pnl.realized_pnl,
                        unrealized_pnl=self.pnl.unrealized_pnl(mid),
                        equity=self.pnl.equity(mid),
                    )
                )

        return BacktestResult(equity_curve=equity_curve, fills=all_fills)

    def _schedule_requote(self, now_ms: int, start_ms: int) -> None:
        mid = self.sync.book.mid_price()
        if mid is None:
            return
        time_remaining = max(0.0, self.quoting_params.time_horizon_s - (now_ms - start_ms) / 1000)
        quote = compute_quotes(mid, self.pnl.inventory, self.quoting_params, time_remaining)
        self._pending.append(_PendingQuote(now_ms + self.config.latency_ms, quote))

    def _apply_due_quotes(self, now_ms: int) -> None:
        while self._pending and self._pending[0].apply_at_ms <= now_ms:
            self._replace_quotes(self._pending.popleft().quote, now_ms)

    def _replace_quotes(self, quote: Quote, now_ms: int) -> None:
        if self._bid_order_id is not None:
            self.fill_sim.cancel_order(self._bid_order_id)
            self._bid_order_id = None
        if self._ask_order_id is not None:
            self.fill_sim.cancel_order(self._ask_order_id)
            self._ask_order_id = None

        book = self.sync.book
        if quote.bid_price is not None and quote.bid_size > 0:
            queue_ahead = book.bid_quantity_at(quote.bid_price)
            self._bid_order_id = self.fill_sim.place_order(
                Side.BID, quote.bid_price, quote.bid_size, queue_ahead, now_ms
            )
        if quote.ask_price is not None and quote.ask_size > 0:
            queue_ahead = book.ask_quantity_at(quote.ask_price)
            self._ask_order_id = self.fill_sim.place_order(
                Side.ASK, quote.ask_price, quote.ask_size, queue_ahead, now_ms
            )

    def _process_trade(self, trade: Trade) -> list[Fill]:
        mid = self.sync.book.mid_price()
        if mid is None:
            return []
        fills = self.fill_sim.on_trade(trade, mid)
        for fill in fills:
            self.pnl.on_fill(fill)
            if fill.side is Side.BID and not self.fill_sim.has_order(fill.order_id):
                self._bid_order_id = None
            if fill.side is Side.ASK and not self.fill_sim.has_order(fill.order_id):
                self._ask_order_id = None
        return fills
