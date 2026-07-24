from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import websockets

from crypto_mm_engine.data.config import MarketDataConfig, ReconnectPolicy
from crypto_mm_engine.data.models import DepthUpdate, PriceLevel, Trade

logger = logging.getLogger(__name__)

DepthHandler = Callable[[DepthUpdate], Awaitable[None]]
TradeHandler = Callable[[Trade], Awaitable[None]]


def next_backoff_delay(attempt: int, policy: ReconnectPolicy) -> float:
    """attempt is 0-indexed: the delay before the (attempt+1)-th retry."""
    delay = policy.initial_delay_s * (policy.multiplier**attempt)
    return min(delay, policy.max_delay_s)


def parse_depth_update(data: dict[str, Any]) -> DepthUpdate:
    return DepthUpdate(
        symbol=data["s"],
        first_update_id=data["U"],
        final_update_id=data["u"],
        event_time_ms=data["E"],
        bids=tuple(PriceLevel(float(p), float(q)) for p, q in data["b"]),
        asks=tuple(PriceLevel(float(p), float(q)) for p, q in data["a"]),
    )


def parse_trade(data: dict[str, Any]) -> Trade:
    return Trade(
        symbol=data["s"],
        trade_id=data["t"],
        price=float(data["p"]),
        quantity=float(data["q"]),
        trade_time_ms=data["T"],
        is_buyer_maker=data["m"],
    )


def parse_combined_stream_message(raw: str) -> DepthUpdate | Trade | None:
    """Returns None for event types we don't have a model for yet."""
    envelope = json.loads(raw)
    data = envelope["data"]
    event_type = data.get("e")
    if event_type == "depthUpdate":
        return parse_depth_update(data)
    if event_type == "trade":
        return parse_trade(data)
    return None


class BinanceMarketDataClient:
    """Owns the combined-stream WS connection and reconnects with backoff.

    Sequencing (snapshot fetch, buffering, gap detection) is the caller's
    job via OrderBookSynchronizer — this class only turns wire messages into
    typed events and hands them off.
    """

    def __init__(
        self,
        config: MarketDataConfig,
        on_depth_update: DepthHandler,
        on_trade: TradeHandler,
    ) -> None:
        self._config = config
        self._on_depth_update = on_depth_update
        self._on_trade = on_trade
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        attempt = 0
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self._config.combined_stream_url) as ws:
                    attempt = 0
                    async for raw in ws:
                        if self._stop_event.is_set():
                            break
                        await self._dispatch(raw)
            except (websockets.ConnectionClosed, OSError) as exc:
                if self._stop_event.is_set():
                    break
                delay = next_backoff_delay(attempt, self._config.reconnect)
                logger.warning("market data stream dropped (%s), reconnecting in %.1fs", exc, delay)
                attempt += 1
                await asyncio.sleep(delay)

    async def _dispatch(self, raw: str | bytes) -> None:
        if isinstance(raw, bytes):
            raw = raw.decode()
        event = parse_combined_stream_message(raw)
        if isinstance(event, DepthUpdate):
            await self._on_depth_update(event)
        elif isinstance(event, Trade):
            await self._on_trade(event)
