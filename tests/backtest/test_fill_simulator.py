from crypto_mm_engine.backtest.fill_simulator import FillSimulator
from crypto_mm_engine.backtest.models import FeeSchedule, Side
from crypto_mm_engine.data.models import Trade


def make_trade(
    price: float, quantity: float, is_buyer_maker: bool, trade_time_ms: int = 1000
) -> Trade:
    return Trade(
        symbol="BACKTEST",
        trade_id=1,
        price=price,
        quantity=quantity,
        trade_time_ms=trade_time_ms,
        is_buyer_maker=is_buyer_maker,
    )


def test_bid_fills_immediately_when_queue_ahead_is_zero() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    order_id = sim.place_order(Side.BID, price=100.0, size=1.0, queue_ahead=0.0, now_ms=0)

    fills = sim.on_trade(
        make_trade(price=100.0, quantity=1.0, is_buyer_maker=True), mid_price=100.5
    )

    assert len(fills) == 1
    assert fills[0].order_id == order_id
    assert fills[0].quantity == 1.0
    assert not sim.has_order(order_id)


def test_bid_waits_until_queue_ahead_is_consumed() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    order_id = sim.place_order(Side.BID, price=100.0, size=1.0, queue_ahead=3.0, now_ms=0)

    fills = sim.on_trade(
        make_trade(price=100.0, quantity=2.0, is_buyer_maker=True), mid_price=100.5
    )
    assert fills == []
    assert sim.has_order(order_id)

    fills = sim.on_trade(
        make_trade(price=100.0, quantity=2.0, is_buyer_maker=True), mid_price=100.5
    )
    assert len(fills) == 1
    assert fills[0].quantity == 1.0  # 1 unit left of queue, then our full size fills


def test_partial_fill_leaves_order_resting() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    order_id = sim.place_order(Side.BID, price=100.0, size=5.0, queue_ahead=0.0, now_ms=0)

    fills = sim.on_trade(
        make_trade(price=100.0, quantity=2.0, is_buyer_maker=True), mid_price=100.5
    )

    assert len(fills) == 1
    assert fills[0].quantity == 2.0
    assert sim.has_order(order_id)


def test_ask_only_fills_on_buyer_taker_trades() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    sim.place_order(Side.ASK, price=101.0, size=1.0, queue_ahead=0.0, now_ms=0)

    # is_buyer_maker=True means a resting BID was hit, not our ask
    fills = sim.on_trade(
        make_trade(price=101.0, quantity=1.0, is_buyer_maker=True), mid_price=100.5
    )
    assert fills == []

    fills = sim.on_trade(
        make_trade(price=101.0, quantity=1.0, is_buyer_maker=False), mid_price=100.5
    )
    assert len(fills) == 1
    assert fills[0].side is Side.ASK


def test_trade_at_different_price_does_not_fill() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    sim.place_order(Side.BID, price=100.0, size=1.0, queue_ahead=0.0, now_ms=0)

    fills = sim.on_trade(
        make_trade(price=99.5, quantity=10.0, is_buyer_maker=True), mid_price=100.5
    )
    assert fills == []


def test_cancel_order_removes_it_from_book() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    order_id = sim.place_order(Side.BID, price=100.0, size=1.0, queue_ahead=0.0, now_ms=0)

    sim.cancel_order(order_id)

    assert not sim.has_order(order_id)
    fills = sim.on_trade(
        make_trade(price=100.0, quantity=1.0, is_buyer_maker=True), mid_price=100.5
    )
    assert fills == []


def test_fee_is_charged_at_maker_rate() -> None:
    sim = FillSimulator(FeeSchedule(maker_fee_rate=0.001))
    sim.place_order(Side.BID, price=100.0, size=1.0, queue_ahead=0.0, now_ms=0)

    fills = sim.on_trade(
        make_trade(price=100.0, quantity=1.0, is_buyer_maker=True), mid_price=100.5
    )

    assert fills[0].fee == 1.0 * 100.0 * 0.001
