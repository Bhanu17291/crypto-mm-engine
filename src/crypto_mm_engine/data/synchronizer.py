from __future__ import annotations

from enum import Enum, auto

from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate
from crypto_mm_engine.data.order_book import OrderBook


class OrderBookOutOfSyncError(Exception):
    """Raised when a diff-depth event doesn't chain onto the book we have.

    The only correct response is to drop the current state and resync from
    a fresh REST snapshot — there's no way to patch a gap in a diff stream.
    """


class _State(Enum):
    BUFFERING = auto()
    SYNCED = auto()


class OrderBookSynchronizer:
    """Implements Binance's documented local-book sync procedure.

    Diff events arrive on the WS stream before we've fetched a REST
    snapshot, so early events get buffered. Once the snapshot lands, we
    drop anything the snapshot already covers and replay the rest. See
    https://binance-docs.github.io/apidocs/spot/en/#how-to-manage-a-local-order-book-correctly
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.book = OrderBook(symbol)
        self._buffer: list[DepthUpdate] = []
        self._state = _State.BUFFERING

    @property
    def is_synced(self) -> bool:
        return self._state is _State.SYNCED

    def apply_snapshot(self, snapshot: DepthSnapshot) -> None:
        relevant = [u for u in self._buffer if u.final_update_id > snapshot.last_update_id]
        self.book.apply_snapshot(snapshot)
        self._state = _State.SYNCED
        self._buffer.clear()
        for update in relevant:
            self._apply_synced(update)

    def apply_update(self, update: DepthUpdate) -> None:
        if self._state is _State.BUFFERING:
            self._buffer.append(update)
            return
        self._apply_synced(update)

    def _apply_synced(self, update: DepthUpdate) -> None:
        expected_next = self.book.last_update_id + 1
        if update.final_update_id < expected_next:
            return  # already covered by the snapshot or a prior update
        if update.first_update_id > expected_next:
            self._state = _State.BUFFERING
            raise OrderBookOutOfSyncError(
                f"{self.symbol}: gap in depth stream, expected update starting at "
                f"{expected_next} but got U={update.first_update_id}"
            )
        self.book.apply_update(update)
