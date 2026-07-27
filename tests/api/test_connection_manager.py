import pytest

from crypto_mm_engine.api.connection_manager import ConnectionManager


class FakeWebSocket:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.received: list[str] = []

    async def send_text(self, data: str) -> None:
        if self.fail:
            raise RuntimeError("connection closed")
        self.received.append(data)


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_connections() -> None:
    manager = ConnectionManager()
    a, b = FakeWebSocket(), FakeWebSocket()
    manager.connect(a)
    manager.connect(b)

    await manager.broadcast("hello")

    assert a.received == ["hello"]
    assert b.received == ["hello"]


@pytest.mark.asyncio
async def test_broadcast_prunes_connections_that_raise() -> None:
    manager = ConnectionManager()
    good, bad = FakeWebSocket(), FakeWebSocket(fail=True)
    manager.connect(good)
    manager.connect(bad)

    await manager.broadcast("hello")

    assert manager.connection_count == 1
    assert good.received == ["hello"]


def test_disconnect_removes_connection() -> None:
    manager = ConnectionManager()
    ws = FakeWebSocket()
    manager.connect(ws)

    manager.disconnect(ws)

    assert manager.connection_count == 0


def test_disconnect_is_a_no_op_for_unknown_connection() -> None:
    manager = ConnectionManager()
    manager.disconnect(FakeWebSocket())
    assert manager.connection_count == 0
