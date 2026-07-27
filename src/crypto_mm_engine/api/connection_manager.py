from __future__ import annotations

from typing import Protocol


class _WebSocketLike(Protocol):
    async def send_text(self, data: str) -> None: ...


class ConnectionManager:
    """Tracks connected WS clients and broadcasts to all of them; a client
    that drops mid-broadcast (send raises) is pruned rather than taking the
    rest of the broadcast down with it."""

    def __init__(self) -> None:
        self._connections: list[_WebSocketLike] = []

    def connect(self, websocket: _WebSocketLike) -> None:
        self._connections.append(websocket)

    def disconnect(self, websocket: _WebSocketLike) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def broadcast(self, message: str) -> None:
        stale: list[_WebSocketLike] = []
        for connection in self._connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)
