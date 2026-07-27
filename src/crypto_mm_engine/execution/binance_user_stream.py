from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import websockets

from crypto_mm_engine.data.binance_ws import next_backoff_delay
from crypto_mm_engine.data.config import ReconnectPolicy
from crypto_mm_engine.execution.binance_signing import build_signed_params
from crypto_mm_engine.execution.models import LiveFill, parse_execution_report

logger = logging.getLogger(__name__)

FillHandler = Callable[[LiveFill], Awaitable[None]]


def extract_event(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Binance's WebSocket API wraps pushed user-data events as
    {"subscriptionId": ..., "event": {...}} on the same connection used to
    subscribe; the subscribe acknowledgement itself ({"id", "status",
    "result"}) has no "event" key. Pulled out as a pure function so the
    envelope handling is testable without a live connection.
    """
    return payload.get("event")


class BinanceUserDataStream:
    """Listens for our own order execution reports - the only correct
    source of live fills, since a real exchange decides matching itself
    rather than us guessing at queue position the way the backtest does.

    Binance retired the old listenKey REST flow (POST /api/v3/userDataStream
    now returns 410 Gone); user data now arrives by subscribing directly
    on the WebSocket API connection with a signed request, no separate
    listenKey lifecycle to manage.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        ws_api_base_url: str,
        on_fill: FillHandler,
        reconnect: ReconnectPolicy | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._ws_api_base_url = ws_api_base_url
        self._on_fill = on_fill
        self._reconnect = reconnect or ReconnectPolicy()
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        attempt = 0
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self._ws_api_base_url) as ws:
                    await self._subscribe(ws)
                    attempt = 0
                    async for raw in ws:
                        if self._stop_event.is_set():
                            break
                        await self._dispatch(raw)
            except (websockets.ConnectionClosed, OSError) as exc:
                if self._stop_event.is_set():
                    break
                delay = next_backoff_delay(attempt, self._reconnect)
                logger.warning("user data stream dropped (%s), reconnecting in %.1fs", exc, delay)
                attempt += 1
                await asyncio.sleep(delay)

    async def _subscribe(self, ws: websockets.ClientConnection) -> None:
        signed = build_signed_params({"apiKey": self._api_key}, self._api_secret, _now_ms())
        request = {
            "id": str(uuid.uuid4()),
            "method": "userDataStream.subscribe.signature",
            "params": signed,
        }
        await ws.send(json.dumps(request))

    async def _dispatch(self, raw: str | bytes) -> None:
        if isinstance(raw, bytes):
            raw = raw.decode()
        event = extract_event(json.loads(raw))
        if event is None:
            return
        fill = parse_execution_report(event)
        if fill is not None:
            await self._on_fill(fill)


def _now_ms() -> int:
    return int(time.time() * 1000)
