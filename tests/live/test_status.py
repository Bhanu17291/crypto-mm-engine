from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.data.models import PriceLevel, Trade
from crypto_mm_engine.execution.models import LiveFill, Side
from crypto_mm_engine.live.status import (
    StatusSnapshot,
    build_cancel_event,
    build_fill_event,
    build_status_snapshot,
    build_trade_tape_event,
)
from crypto_mm_engine.quoting.avellaneda_stoikov import optimal_spread, reservation_price
from crypto_mm_engine.quoting.models import Quote, QuotingParams
from crypto_mm_engine.risk.models import RiskLimits
from crypto_mm_engine.risk.risk_manager import RiskManager

QUOTING_PARAMS = QuotingParams(
    risk_aversion=0.1,
    order_arrival_intensity=1.5,
    volatility=0.001,
    time_horizon_s=3600.0,
    max_inventory=0.05,
    quote_size=0.001,
)


def _make_risk(**overrides: object) -> RiskManager:
    defaults: dict[str, object] = dict(
        max_position=10.0,
        max_daily_loss=100.0,
        max_stale_data_ms=1000,
        expected_fill_rate=(0.0, 1.0),
    )
    defaults.update(overrides)
    return RiskManager(RiskLimits(**defaults))  # type: ignore[arg-type]


def _build(
    pnl: PnLTracker,
    quote: Quote,
    risk: RiskManager,
    mid_price: float = 105.0,
    timestamp_ms: int = 1234,
) -> StatusSnapshot:
    return build_status_snapshot(
        symbol="btcusdt",
        mid_price=mid_price,
        max_position=10.0,
        pnl=pnl,
        quote=quote,
        risk=risk,
        timestamp_ms=timestamp_ms,
        quoting_params=QUOTING_PARAMS,
        time_remaining_s=1800.0,
        bid_order_id="b1",
        ask_order_id="a1",
        requote_latency_ms=12.5,
        book_bids=[PriceLevel(104.0, 1.0), PriceLevel(103.0, 2.0)],
        book_asks=[PriceLevel(106.0, 1.5)],
    )


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
    risk = _make_risk()
    quote = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)

    snapshot = _build(pnl, quote, risk)

    assert snapshot.symbol == "btcusdt"
    assert snapshot.inventory == 2.0
    assert snapshot.unrealized_pnl == pnl.unrealized_pnl(105.0)
    assert snapshot.equity == pnl.equity(105.0)
    assert snapshot.quote.bid_price == 99.0
    assert snapshot.risk.halted is False


def test_build_status_snapshot_reflects_halted_risk_state() -> None:
    pnl = PnLTracker()
    risk = _make_risk(max_daily_loss=50.0)
    risk.check_daily_loss(daily_pnl=-51.0)
    quote = Quote(bid_price=None, bid_size=0.0, ask_price=None, ask_size=0.0)

    snapshot = _build(pnl, quote, risk, mid_price=100.0, timestamp_ms=0)

    assert snapshot.risk.halted is True
    assert snapshot.risk.kill_switch_tripped is True


def test_build_status_snapshot_includes_reservation_price_and_spread() -> None:
    pnl = PnLTracker()
    risk = _make_risk()
    quote = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)

    snapshot = _build(pnl, quote, risk)

    assert snapshot.reservation_price == reservation_price(105.0, 0.0, QUOTING_PARAMS, 1800.0)
    assert snapshot.optimal_spread == optimal_spread(QUOTING_PARAMS, 1800.0)


def test_build_status_snapshot_includes_book_depth_and_order_ids() -> None:
    pnl = PnLTracker()
    risk = _make_risk()
    quote = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)

    snapshot = _build(pnl, quote, risk)

    assert [level.price for level in snapshot.book.bids] == [104.0, 103.0]
    assert [level.price for level in snapshot.book.asks] == [106.0]
    assert snapshot.bid_order_id == "b1"
    assert snapshot.ask_order_id == "a1"
    assert snapshot.requote_latency_ms == 12.5


def test_build_status_snapshot_includes_static_params_and_limits() -> None:
    pnl = PnLTracker()
    risk = _make_risk(max_position=7.0, expected_fill_rate=(0.2, 0.8))
    quote = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)

    snapshot = _build(pnl, quote, risk)

    assert snapshot.quoting_params.risk_aversion == QUOTING_PARAMS.risk_aversion
    assert snapshot.risk_limits.max_position == 7.0
    assert snapshot.risk_limits.min_fill_rate == 0.2
    assert snapshot.risk_limits.max_fill_rate == 0.8


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


def test_build_trade_tape_event_maps_trade_fields() -> None:
    trade = Trade(
        symbol="BTCUSDT",
        trade_id=1,
        price=100.0,
        quantity=0.01,
        trade_time_ms=555,
        is_buyer_maker=True,
    )

    event = build_trade_tape_event(trade)

    assert event.price == 100.0
    assert event.quantity == 0.01
    assert event.is_buyer_maker is True
    assert event.timestamp_ms == 555


def test_build_cancel_event() -> None:
    event = build_cancel_event("7", 111)

    assert event.order_id == "7"
    assert event.timestamp_ms == 111
