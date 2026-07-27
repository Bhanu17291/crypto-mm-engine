from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.execution.models import LiveFill, Side
from crypto_mm_engine.live.status import build_fill_event, build_status_snapshot
from crypto_mm_engine.quoting.models import Quote
from crypto_mm_engine.risk.models import RiskLimits
from crypto_mm_engine.risk.risk_manager import RiskManager


def test_build_status_snapshot_reflects_pnl_and_quote_state() -> None:
    pnl = PnLTracker()
    pnl.on_fill(
        LiveFill(
            order_id="1",
            side=Side.BID,
            price=100.0,
            quantity=2.0,
            fee=0.1,
            timestamp_ms=0,
            order_status="FILLED",
        )
    )
    risk = RiskManager(
        RiskLimits(
            max_position=10.0,
            max_daily_loss=100.0,
            max_stale_data_ms=1000,
            expected_fill_rate=(0.0, 1.0),
        )
    )
    quote = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)

    snapshot = build_status_snapshot(
        symbol="btcusdt",
        mid_price=105.0,
        max_position=10.0,
        pnl=pnl,
        quote=quote,
        risk=risk,
        timestamp_ms=1234,
    )

    assert snapshot.symbol == "btcusdt"
    assert snapshot.inventory == 2.0
    assert snapshot.unrealized_pnl == pnl.unrealized_pnl(105.0)
    assert snapshot.equity == pnl.equity(105.0)
    assert snapshot.quote.bid_price == 99.0
    assert snapshot.risk.halted is False


def test_build_status_snapshot_reflects_halted_risk_state() -> None:
    pnl = PnLTracker()
    risk = RiskManager(
        RiskLimits(
            max_position=10.0,
            max_daily_loss=50.0,
            max_stale_data_ms=1000,
            expected_fill_rate=(0.0, 1.0),
        )
    )
    risk.check_daily_loss(daily_pnl=-51.0)
    quote = Quote(bid_price=None, bid_size=0.0, ask_price=None, ask_size=0.0)

    snapshot = build_status_snapshot(
        symbol="btcusdt",
        mid_price=100.0,
        max_position=10.0,
        pnl=pnl,
        quote=quote,
        risk=risk,
        timestamp_ms=0,
    )

    assert snapshot.risk.halted is True
    assert snapshot.risk.kill_switch_tripped is True


def test_build_fill_event_maps_live_fill_fields() -> None:
    fill = LiveFill(
        order_id="42",
        side=Side.ASK,
        price=200.0,
        quantity=0.5,
        fee=0.02,
        timestamp_ms=999,
        order_status="TRADE",
    )

    event = build_fill_event(fill)

    assert event.order_id == "42"
    assert event.side == "ask"
    assert event.price == 200.0
    assert event.quantity == 0.5
    assert event.fee == 0.02
    assert event.timestamp_ms == 999
