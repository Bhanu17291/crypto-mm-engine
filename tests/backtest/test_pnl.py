import pytest

from crypto_mm_engine.backtest.models import Fill, Side
from crypto_mm_engine.backtest.pnl import PnLTracker


def make_fill(side: Side, price: float, quantity: float, fee: float = 0.0) -> Fill:
    return Fill(
        order_id=1,
        side=side,
        price=price,
        quantity=quantity,
        fee=fee,
        timestamp_ms=0,
        mid_price_at_fill=price,
    )


def test_opening_position_sets_average_entry_price() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=2.0))

    assert tracker.inventory == 2.0
    assert tracker.avg_entry_price == 100.0


def test_adding_to_position_updates_weighted_average() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=1.0))
    tracker.on_fill(make_fill(Side.BID, price=110.0, quantity=1.0))

    assert tracker.inventory == 2.0
    assert tracker.avg_entry_price == pytest.approx(105.0)


def test_partial_close_realizes_pnl_and_keeps_average_price() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=2.0))
    tracker.on_fill(make_fill(Side.ASK, price=110.0, quantity=1.0))

    assert tracker.inventory == 1.0
    assert tracker.avg_entry_price == 100.0  # unchanged cost basis on partial close
    assert tracker.realized_pnl == pytest.approx(10.0)  # 1 unit closed at a $10 profit


def test_full_close_realizes_pnl_and_resets_state() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=1.0))
    tracker.on_fill(make_fill(Side.ASK, price=95.0, quantity=1.0))

    assert tracker.inventory == 0.0
    assert tracker.avg_entry_price == 0.0
    assert tracker.realized_pnl == pytest.approx(-5.0)


def test_flip_through_zero_opens_fresh_position_at_fill_price() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=1.0))
    tracker.on_fill(make_fill(Side.ASK, price=105.0, quantity=3.0))  # closes 1, opens -2 short

    assert tracker.inventory == -2.0
    assert tracker.avg_entry_price == 105.0
    assert tracker.realized_pnl == pytest.approx(5.0)


def test_fees_reduce_realized_pnl() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=1.0, fee=0.5))

    assert tracker.realized_pnl == pytest.approx(-0.5)
    assert tracker.fees_paid == pytest.approx(0.5)


def test_unrealized_pnl_and_equity_mark_against_current_price() -> None:
    tracker = PnLTracker()
    tracker.on_fill(make_fill(Side.BID, price=100.0, quantity=2.0))

    assert tracker.unrealized_pnl(mark_price=105.0) == pytest.approx(10.0)
    assert tracker.equity(mark_price=105.0) == pytest.approx(10.0)
