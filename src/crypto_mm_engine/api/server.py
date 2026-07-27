from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from crypto_mm_engine.api.connection_manager import ConnectionManager
from crypto_mm_engine.live.runner import PaperTradingRunner
from crypto_mm_engine.live.status import CancelEvent, FillEvent, StatusSnapshot, TradeTapeEvent

logger = logging.getLogger(__name__)

_BROADCAST_INTERVAL_S = 0.5
_DEV_ORIGINS = ["http://localhost:5180", "http://127.0.0.1:5180"]


def create_app(runner: PaperTradingRunner) -> FastAPI:
    """The dashboard's only view into the engine: a status snapshot the
    runner already builds every requote, and the fills it's already
    tracking. This module doesn't compute anything itself - it just serves
    what PaperTradingRunner exposes.
    """
    manager = ConnectionManager()

    async def _broadcast_loop() -> None:
        last_sent: StatusSnapshot | None = None
        while True:
            await asyncio.sleep(_BROADCAST_INTERVAL_S)
            current = runner.latest_status
            if current is not None and current != last_sent:
                last_sent = current
                await manager.broadcast(current.model_dump_json())

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = asyncio.create_task(_broadcast_loop())
        try:
            yield
        finally:
            task.cancel()

    app = FastAPI(title="crypto-mm-engine live status API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_DEV_ORIGINS,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/api/status")
    def get_status() -> StatusSnapshot | None:
        return runner.latest_status

    @app.get("/api/fills")
    def get_fills() -> list[FillEvent]:
        return list(runner.recent_fills)

    @app.get("/api/trades")
    def get_trades() -> list[TradeTapeEvent]:
        return list(runner.recent_trades)

    @app.get("/api/cancellations")
    def get_cancellations() -> list[CancelEvent]:
        return list(runner.cancelled_orders)

    @app.websocket("/ws/status")
    async def ws_status(websocket: WebSocket) -> None:
        await websocket.accept()
        manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app
