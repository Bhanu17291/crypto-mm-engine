from __future__ import annotations

import asyncio
import logging
from collections import deque

import httpx

from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.data.binance_rest import fetch_depth_snapshot
from crypto_mm_engine.data.binance_ws import BinanceMarketDataClient
from crypto_mm_engine.data.config import MarketDataConfig
from crypto_mm_engine.data.models import DepthUpdate, Trade
from crypto_mm_engine.data.synchronizer import OrderBookSynchronizer
from crypto_mm_engine.execution.binance_rest_adapter import BinanceTestnetExecutionAdapter
from crypto_mm_engine.execution.binance_user_stream import BinanceUserDataStream
from crypto_mm_engine.execution.models import LiveFill
from crypto_mm_engine.execution.quote_manager import QuoteManager
from crypto_mm_engine.live.config import LiveConfig
from crypto_mm_engine.live.status import (
    FillEvent,
    StatusSnapshot,
    build_fill_event,
    build_status_snapshot,
)
from crypto_mm_engine.quoting.avellaneda_stoikov import compute_quotes
from crypto_mm_engine.risk.risk_manager import RiskManager

logger = logging.getLogger(__name__)

_CLOSED_ORDER_STATUSES = {"FILLED", "CANCELED", "REJECTED", "EXPIRED"}
_RECENT_FILLS_LIMIT = 200


class PaperTradingRunner:
    """Wires market data ingestion into the AS quoting engine, through the
    risk gate, out to Binance's Spot Testnet: the same compute_quotes,
    RiskManager, QuoteManager and PnLTracker the backtest harness exercises
    - only the execution adapter, and the source of fills (the exchange's
    own user data stream instead of a queue-position simulator), differ.
    """

    def __init__(self, config: LiveConfig) -> None:
        self.config = config
        self.sync = OrderBookSynchronizer(config.symbol)
        self.pnl = PnLTracker()
        self.risk = RiskManager(config.risk)
        self.rest_adapter = BinanceTestnetExecutionAdapter(
            config.api_key, config.api_secret, config.symbol, config.rest_base_url
        )
        self.quotes = QuoteManager(self.rest_adapter)
        self._last_market_data_ms = 0
        self._start_ms: int | None = None
        self.latest_status: StatusSnapshot | None = None
        self.recent_fills: deque[FillEvent] = deque(maxlen=_RECENT_FILLS_LIMIT)

    async def run(self) -> None:
        market_data_config = MarketDataConfig(
            symbols=(self.config.symbol,),
            ws_base_url=self.config.ws_base_url,
            rest_base_url=self.config.rest_base_url,
        )
        async with httpx.AsyncClient(base_url=self.config.rest_base_url) as client:
            snapshot = await fetch_depth_snapshot(client, market_data_config, self.config.symbol)
        self.sync.apply_snapshot(snapshot)
        logger.info("bootstrapped order book from snapshot symbol=%s", self.config.symbol)

        market_client = BinanceMarketDataClient(
            market_data_config, on_depth_update=self._on_depth_update, on_trade=self._on_trade
        )
        user_stream = BinanceUserDataStream(
            self.config.api_key,
            self.config.api_secret,
            self.config.ws_api_base_url,
            on_fill=self._on_fill,
        )

        try:
            await asyncio.gather(market_client.run(), user_stream.run())
        finally:
            self.rest_adapter.close()

    async def _on_depth_update(self, update: DepthUpdate) -> None:
        self.sync.apply_update(update)
        self._last_market_data_ms = update.event_time_ms
        await self._requote(update.event_time_ms)

    async def _on_trade(self, trade: Trade) -> None:
        # The public trade tape isn't our fills live (those come from the
        # user data stream) - it still counts as evidence market data is fresh.
        self._last_market_data_ms = max(self._last_market_data_ms, trade.trade_time_ms)

    async def _on_fill(self, fill: LiveFill) -> None:
        self.pnl.on_fill(fill)
        still_open = fill.order_status not in _CLOSED_ORDER_STATUSES
        self.quotes.clear_if_closed(fill.side, fill.order_id, still_open)
        self.risk.record_quote_cycle(filled=True)
        self.recent_fills.appendleft(build_fill_event(fill))
        logger.info(
            "fill side=%s price=%s qty=%s inventory=%.6f realized_pnl=%.4f",
            fill.side.value,
            fill.price,
            fill.quantity,
            self.pnl.inventory,
            self.pnl.realized_pnl,
        )

    async def _requote(self, now_ms: int) -> None:
        mid = self.sync.book.mid_price()
        if mid is None:
            return
        if self._start_ms is None:
            self._start_ms = now_ms

        time_remaining = max(
            0.0, self.config.quoting.time_horizon_s - (now_ms - self._start_ms) / 1000
        )
        quote = compute_quotes(mid, self.pnl.inventory, self.config.quoting, time_remaining)
        gated = self.risk.gate_quote(quote, self.pnl.inventory, self._last_market_data_ms, now_ms)
        self.quotes.apply_quote(gated)
        self.risk.check_daily_loss(self.pnl.equity(mid))

        self.latest_status = build_status_snapshot(
            symbol=self.config.symbol,
            mid_price=mid,
            max_position=self.config.risk.max_position,
            pnl=self.pnl,
            quote=gated,
            risk=self.risk,
            timestamp_ms=now_ms,
        )

        logger.info(
            "status mid=%.2f inventory=%.6f bid=%s ask=%s equity=%.4f halted=%s",
            mid,
            self.pnl.inventory,
            gated.bid_price,
            gated.ask_price,
            self.pnl.equity(mid),
            self.risk.is_halted,
        )
