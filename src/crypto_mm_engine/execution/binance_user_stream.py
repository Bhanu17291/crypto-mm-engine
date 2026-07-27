from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import websockets

from crypto_mm_engine.data.binance_ws import next_backoff_delay
from crypto_mm_engine.data.config import ReconnectPolicy
from crypto_mm_engine.execution.binance_rest_adapter import BinanceTestnetExecutionAdapter
from crypto_mm_engine.execution.models import LiveFill, parse_execution_report

logger = logging.getLogger(__name__)

FillHandler = Callable[[LiveFill], Awaitable[None]]

_KEEPALIVE_INTERVAL_S = 30 * 60  # Binance requires a keepalive within 60 minutes


class BinanceUserDataStream:
    """Listens for our own order execution reports - the only correct
    source of live fills, since a real exchange decides matching itself
    rather than us guessing at queue position the way the backtest does.

    Manages the listenKey lifecycle (create, periodic keepalive) alongside
    the WS connection, reconnecting with the same backoff policy the
    market data client uses.
    """

    def __init__(
        self,
        rest_adapter: BinanceTestnetExecutionAdapter,
        ws_base_url: str,
        on_fill: FillHandler,
        reconnect: ReconnectPolicy | None = None,
    ) -> None:
        self._rest_adapter = rest_adapter
        self._ws_base_url = ws_base_url
        self._on_fill = on_fill
        self._reconnect = reconnect or ReconnectPolicy()
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        attempt = 0
        while not self._stop_event.is_set():
            try:
                listen_key = self._rest_adapter.create_listen_key()
                async with websockets.connect(f"{self._ws_base_url}/ws/{listen_key}") as ws:
                    attempt = 0
                    keepalive_task = asyncio.create_task(self._keepalive_loop(listen_key))
                    try:
                        async for raw in ws:
                            if self._stop_event.is_set():
                                break
                            await self._dispatch(raw)
                    finally:
                        keepalive_task.cancel()
            except (websockets.ConnectionClosed, OSError) as exc:
                if self._stop_event.is_set():
                    break
                delay = next_backoff_delay(attempt, self._reconnect)
                logger.warning("user data stream dropped (%s), reconnecting in %.1fs", exc, delay)
                attempt += 1
                await asyncio.sleep(delay)

    async def _keepalive_loop(self, listen_key: str) -> None:
        while True:
            await asyncio.sleep(_KEEPALIVE_INTERVAL_S)
            self._rest_adapter.keepalive_listen_key(listen_key)

    async def _dispatch(self, raw: str | bytes) -> None:
        if isinstance(raw, bytes):
            raw = raw.decode()
        fill = parse_execution_report(json.loads(raw))
        if fill is not None:
            await self._on_fill(fill)
