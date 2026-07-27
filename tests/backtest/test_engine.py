import pytest

from crypto_mm_engine.backtest.engine import BacktestEngine
from crypto_mm_engine.backtest.models import BacktestConfig, FeeSchedule, Side
from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, PriceLevel, Trade
from crypto_mm_engine.quoting.avellaneda_stoikov import compute_quotes
from crypto_mm_engine.quoting.models import QuotingParams

# volatility=0 makes both the reservation-price skew and the spread's
# inventory term vanish, so quotes are a fixed, time-independent distance
# from mid - which keeps this test's expected prices exact and simple.
PARAMS = QuotingParams(
    risk_aversion=0.1,
    order_arrival_intensity=1.0,
    volatility=0.0,
    time_horizon_s=1000.0,
    max_inventory=100.0,
    quote_size=1.0,
)


def make_snapshot() -> DepthSnapshot:
    return DepthSnapshot(
        symbol="BACKTEST",
        last_update_id=1,
        bids=(PriceLevel(100.0, 5.0),),
        asks=(PriceLevel(101.0, 5.0),),
    )


def noop_update(update_id: int, event_time_ms: int) -> DepthUpdate:
    return DepthUpdate(
        symbol="BACKTEST",
        first_update_id=update_id,
        final_update_id=update_id,
        event_time_ms=event_time_ms,
        bids=(),
        asks=(),
    )


def expected_quote() -> tuple[float, float]:
    quote = compute_quotes(mid_price=100.5, inventory=0.0, params=PARAMS, time_remaining_s=1000.0)
    assert quote.bid_price is not None and quote.ask_price is not None
    return quote.bid_price, quote.ask_price


def test_bid_fill_updates_inventory_and_realized_spread_capture() -> None:
    bid_price, _ = expected_quote()
    config = BacktestConfig(fees=FeeSchedule(maker_fee_rate=0.0), latency_ms=100)
    engine = BacktestEngine(PARAMS, config)

    events: list[DepthUpdate | Trade] = [
        noop_update(2, event_time_ms=0),
        Trade(
            symbol="BACKTEST",
            trade_id=1,
            price=bid_price,
            quantity=1.0,
            trade_time_ms=200,
            is_buyer_maker=True,
        ),
    ]

    result = engine.run(make_snapshot(), events)

    assert len(result.fills) == 1
    assert result.fills[0].side is Side.BID
    assert engine.pnl.inventory == 1.0
    assert engine.pnl.avg_entry_price == bid_price
    assert result.average_spread_capture == pytest.approx(100.5 - bid_price)


def test_ask_fill_updates_inventory_downward() -> None:
    _, ask_price = expected_quote()
    config = BacktestConfig(fees=FeeSchedule(maker_fee_rate=0.0), latency_ms=100)
    engine = BacktestEngine(PARAMS, config)

    events: list[DepthUpdate | Trade] = [
        noop_update(2, event_time_ms=0),
        Trade(
            symbol="BACKTEST",
            trade_id=1,
            price=ask_price,
            quantity=1.0,
            trade_time_ms=200,
            is_buyer_maker=False,
        ),
    ]

    result = engine.run(make_snapshot(), events)

    assert len(result.fills) == 1
    assert result.fills[0].side is Side.ASK
    assert engine.pnl.inventory == -1.0


def test_trade_before_latency_delay_elapses_does_not_fill() -> None:
    bid_price, _ = expected_quote()
    config = BacktestConfig(fees=FeeSchedule(maker_fee_rate=0.0), latency_ms=100)
    engine = BacktestEngine(PARAMS, config)

    events: list[DepthUpdate | Trade] = [
        noop_update(2, event_time_ms=0),
        # fires before apply_at_ms=100, so our order isn't resting yet
        Trade(
            symbol="BACKTEST",
            trade_id=1,
            price=bid_price,
            quantity=1.0,
            trade_time_ms=50,
            is_buyer_maker=True,
        ),
    ]

    result = engine.run(make_snapshot(), events)

    assert result.fills == []
    assert engine.pnl.inventory == 0.0


def test_equity_curve_has_one_point_per_event_with_valid_mid() -> None:
    config = BacktestConfig(latency_ms=100)
    engine = BacktestEngine(PARAMS, config)

    events = [noop_update(2, event_time_ms=0), noop_update(3, event_time_ms=100)]
    result = engine.run(make_snapshot(), events)

    assert len(result.equity_curve) == 2
    assert all(point.mid_price == 100.5 for point in result.equity_curve)
