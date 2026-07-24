import pytest

from crypto_mm_engine.data.synchronizer import OrderBookOutOfSyncError, OrderBookSynchronizer
from tests.data.fixtures import make_snapshot, make_update


def test_updates_are_buffered_until_snapshot_arrives() -> None:
    sync = OrderBookSynchronizer("BTCUSDT")
    sync.apply_update(make_update(150, 155))

    assert not sync.is_synced
    assert sync.book.last_update_id == -1


def test_snapshot_discards_events_it_already_covers() -> None:
    sync = OrderBookSynchronizer("BTCUSDT")
    sync.apply_update(make_update(140, 145))  # entirely stale once snapshot lands
    sync.apply_update(make_update(146, 159))  # straddles the snapshot's lastUpdateId
    sync.apply_update(make_update(160, 161))  # first genuinely new event

    sync.apply_snapshot(make_snapshot(last_update_id=159))

    assert sync.is_synced
    assert sync.book.last_update_id == 161


def test_synced_updates_apply_in_sequence() -> None:
    sync = OrderBookSynchronizer("BTCUSDT")
    sync.apply_snapshot(make_snapshot(last_update_id=159))

    sync.apply_update(make_update(160, 161))
    sync.apply_update(make_update(162, 165))

    assert sync.book.last_update_id == 165


def test_update_fully_covered_by_current_state_is_ignored() -> None:
    sync = OrderBookSynchronizer("BTCUSDT")
    sync.apply_snapshot(make_snapshot(last_update_id=159))
    sync.apply_update(make_update(160, 165))

    sync.apply_update(make_update(161, 163))  # already-applied range, should be a no-op

    assert sync.book.last_update_id == 165


def test_gap_raises_and_forces_resync() -> None:
    sync = OrderBookSynchronizer("BTCUSDT")
    sync.apply_snapshot(make_snapshot(last_update_id=159))
    sync.apply_update(make_update(160, 161))

    with pytest.raises(OrderBookOutOfSyncError):
        sync.apply_update(make_update(165, 170))  # skipped 162-164

    assert not sync.is_synced

    # after the gap, the synchronizer should buffer again rather than apply
    sync.apply_update(make_update(171, 172))
    assert sync.book.last_update_id == 161  # unchanged, still buffering
