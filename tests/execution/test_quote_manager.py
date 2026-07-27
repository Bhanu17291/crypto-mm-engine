from crypto_mm_engine.execution.models import Side
from crypto_mm_engine.execution.quote_manager import QuoteManager
from crypto_mm_engine.quoting.models import Quote


class FakeAdapter:
    def __init__(self, fail_cancel_for: set[str] | None = None) -> None:
        self.placed: list[tuple[Side, float, float]] = []
        self.cancelled: list[str] = []
        self._next_id = 1
        self._fail_cancel_for = fail_cancel_for or set()

    def place_order(self, side: Side, price: float, size: float) -> str:
        order_id = str(self._next_id)
        self._next_id += 1
        self.placed.append((side, price, size))
        return order_id

    def cancel_order(self, order_id: str) -> None:
        if order_id in self._fail_cancel_for:
            raise RuntimeError("Unknown order sent.")
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


def test_apply_quote_drops_order_id_even_when_cancel_fails() -> None:
    # A cancel can fail because the order is already gone on the venue
    # (filled/expired before we got to it) - if we didn't clear the id
    # here, every future requote would retry the same doomed cancel
    # forever and this side would never place a fresh order again.
    adapter = FakeAdapter(fail_cancel_for={"1"})
    manager = QuoteManager(adapter)
    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=None, ask_size=0.0))
    assert manager.bid_order_id == "1"

    manager.apply_quote(Quote(bid_price=98.5, bid_size=1.0, ask_price=None, ask_size=0.0))

    assert manager.bid_order_id == "2"  # moved on to a fresh order, not stuck on "1"
    assert adapter.placed[-1] == (Side.BID, 98.5, 1.0)


def test_on_cancel_hook_fires_only_for_successful_cancels() -> None:
    adapter = FakeAdapter(fail_cancel_for={"1"})
    cancelled: list[str] = []
    manager = QuoteManager(adapter, on_cancel=cancelled.append)
    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0))

    manager.apply_quote(Quote(bid_price=98.5, bid_size=1.0, ask_price=101.5, ask_size=1.0))

    assert cancelled == ["2"]  # "1"'s cancel failed, so it never fires the hook


def test_clear_if_closed_only_clears_when_not_open() -> None:
    adapter = FakeAdapter()
    manager = QuoteManager(adapter)
    manager.apply_quote(Quote(bid_price=99.0, bid_size=1.0, ask_price=None, ask_size=0.0))

    manager.clear_if_closed(Side.BID, "1", still_open=True)
    assert manager.bid_order_id == "1"

    manager.clear_if_closed(Side.BID, "1", still_open=False)
    assert manager.bid_order_id is None
