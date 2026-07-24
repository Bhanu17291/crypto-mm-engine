from crypto_mm_engine.data.models import DepthUpdate, PriceLevel
from crypto_mm_engine.data.order_book import OrderBook
from tests.data.fixtures import make_snapshot


def test_apply_snapshot_sets_levels_and_drops_zero_qty() -> None:
    book = OrderBook("BTCUSDT")
    book.apply_snapshot(make_snapshot(last_update_id=100))

    assert book.last_update_id == 100
    assert book.best_bid() == PriceLevel(30000.0, 1.0)
    assert book.best_ask() == PriceLevel(30001.0, 2.0)


def test_apply_update_adds_and_removes_levels() -> None:
    book = OrderBook("BTCUSDT")
    book.apply_snapshot(make_snapshot(last_update_id=100))

    update = DepthUpdate(
        symbol="BTCUSDT",
        first_update_id=101,
        final_update_id=101,
        event_time_ms=0,
        bids=(PriceLevel(30000.0, 0.0), PriceLevel(29950.0, 4.0)),
        asks=(PriceLevel(30001.0, 1.5),),
    )
    book.apply_update(update)

    assert book.last_update_id == 101
    assert book.best_bid() == PriceLevel(29950.0, 4.0)  # 30000 was removed
    assert book.best_ask() == PriceLevel(30001.0, 1.5)  # quantity updated in place


def test_mid_price_is_none_until_both_sides_present() -> None:
    book = OrderBook("BTCUSDT")
    assert book.mid_price() is None

    book.apply_snapshot(make_snapshot())
    assert book.mid_price() == (30000.0 + 30001.0) / 2


def test_depth_returns_sorted_and_limited_levels() -> None:
    book = OrderBook("BTCUSDT")
    book.apply_snapshot(make_snapshot())

    bids, asks = book.depth(levels=1)
    assert bids == [PriceLevel(30000.0, 1.0)]  # highest bid first
    assert asks == [PriceLevel(30001.0, 2.0)]  # lowest ask first
