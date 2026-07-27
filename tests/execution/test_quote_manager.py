from crypto_mm_engine.execution.models import Side
from crypto_mm_engine.execution.quote_manager import QuoteManager
from crypto_mm_engine.quoting.models import Quote


class FakeAdapter:
    def __init__(self) -> None:
        self.placed: list[tuple[Side, float, float]] = []
        self.cancelled: list[str] = []
        self._next_id = 1

    def place_order(self, side: Side, price: float, size: float) -> str:
        order_id = str(self._next_id)
        self._next_id += 1
        self.placed.append((side, price, size))
        return order_id

    def cancel_order(self, order_id: str) -> None:
        self.cancelled.append(order_id)


def test_apply_quote_places_both_sides() -> None:
    adapter = FakeAdapter()
    manager = QuoteManager(adapter)

    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0))

    assert adapter.placed == [(Side.BID, 99.0, 1.0), (Side.ASK, 101.0, 1.0)]
    assert manager.bid_order_id == "1"
    assert manager.ask_order_id == "2"


def test_apply_quote_cancels_previous_orders_before_replacing() -> None:
    adapter = FakeAdapter()
    manager = QuoteManager(adapter)
    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0))

    manager.apply_quote(Quote(bid_price=98.5, bid_size=1.0, ask_price=101.5, ask_size=1.0))

    assert adapter.cancelled == ["1", "2"]
    assert manager.bid_order_id == "3"
    assert manager.ask_order_id == "4"


def test_apply_quote_skips_side_with_no_price() -> None:
    adapter = FakeAdapter()
    manager = QuoteManager(adapter)

    manager.apply_quote(Quote(bid_price=None, bid_size=0.0, ask_price=101.0, ask_size=1.0))

    assert manager.bid_order_id is None
    assert manager.ask_order_id == "1"


def test_clear_if_closed_only_clears_when_not_open() -> None:
    adapter = FakeAdapter()
    manager = QuoteManager(adapter)
    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=None, ask_size=0.0))

    manager.clear_if_closed(Side.BID, "1", still_open=True)
    assert manager.bid_order_id == "1"

    manager.clear_if_closed(Side.BID, "1", still_open=False)
    assert manager.bid_order_id is None
