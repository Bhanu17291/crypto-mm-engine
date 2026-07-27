import pytest

from crypto_mm_engine.quoting.models import Quote
from crypto_mm_engine.risk.models import RiskLimits
from crypto_mm_engine.risk.risk_manager import RiskManager

QUOTE = Quote(bid_price=99.0, bid_size=1.0, ask_price=101.0, ask_size=1.0)


def make_manager(**overrides: object) -> RiskManager:
    defaults: dict[str, object] = dict(
        max_position=10.0,
        max_daily_loss=100.0,
        max_stale_data_ms=1000,
        expected_fill_rate=(0.1, 0.9),
        fill_rate_window=4,
    )
    defaults.update(overrides)
    return RiskManager(RiskLimits(**defaults))  # type: ignore[arg-type]


def test_gate_quote_passes_through_when_healthy() -> None:
    manager = make_manager()
    gated = manager.gate_quote(QUOTE, inventory=0.0, last_market_data_ms=1000, now_ms=1200)
    assert gated == QUOTE


def test_gate_quote_blocks_bid_at_long_position_limit() -> None:
    manager = make_manager(max_position=5.0)
    gated = manager.gate_quote(QUOTE, inventory=5.0, last_market_data_ms=1000, now_ms=1200)

    assert gated.bid_price is None
    assert gated.bid_size == 0.0
    assert gated.ask_price == QUOTE.ask_price


def test_gate_quote_blocks_ask_at_short_position_limit() -> None:
    manager = make_manager(max_position=5.0)
    gated = manager.gate_quote(QUOTE, inventory=-5.0, last_market_data_ms=1000, now_ms=1200)

    assert gated.ask_price is None
    assert gated.ask_size == 0.0
    assert gated.bid_price == QUOTE.bid_price


def test_gate_quote_blocks_everything_when_data_is_stale() -> None:
    manager = make_manager(max_stale_data_ms=500)
    gated = manager.gate_quote(QUOTE, inventory=0.0, last_market_data_ms=1000, now_ms=1600)

    assert gated.bid_price is None and gated.ask_price is None
    assert gated.bid_size == 0.0 and gated.ask_size == 0.0


def test_daily_loss_trips_kill_switch_and_halts_all_quoting() -> None:
    manager = make_manager(max_daily_loss=50.0)
    manager.check_daily_loss(daily_pnl=-51.0)

    assert manager.is_kill_switch_tripped
    gated = manager.gate_quote(QUOTE, inventory=0.0, last_market_data_ms=1000, now_ms=1200)
    assert gated.bid_price is None and gated.ask_price is None


def test_daily_loss_within_limit_does_not_trip() -> None:
    manager = make_manager(max_daily_loss=50.0)
    manager.check_daily_loss(daily_pnl=-49.0)
    assert not manager.is_kill_switch_tripped


def test_reset_kill_switch_resumes_quoting() -> None:
    manager = make_manager(max_daily_loss=50.0)
    manager.check_daily_loss(daily_pnl=-51.0)
    manager.reset_kill_switch()

    assert not manager.is_kill_switch_tripped
    gated = manager.gate_quote(QUOTE, inventory=0.0, last_market_data_ms=1000, now_ms=1200)
    assert gated == QUOTE


def test_circuit_breaker_trips_when_fill_rate_too_low() -> None:
    manager = make_manager(expected_fill_rate=(0.5, 1.0), fill_rate_window=4)
    for filled in (False, False, False, True):  # 25% fill rate, below the 50% floor
        manager.record_quote_cycle(filled)

    assert manager.is_circuit_breaker_tripped


def test_circuit_breaker_trips_when_fill_rate_too_high() -> None:
    manager = make_manager(expected_fill_rate=(0.0, 0.5), fill_rate_window=4)
    for filled in (True, True, True, False):  # 75% fill rate, above the 50% ceiling
        manager.record_quote_cycle(filled)

    assert manager.is_circuit_breaker_tripped


def test_circuit_breaker_does_not_trip_before_window_fills_up() -> None:
    manager = make_manager(expected_fill_rate=(0.5, 1.0), fill_rate_window=4)
    manager.record_quote_cycle(False)
    manager.record_quote_cycle(False)

    assert not manager.is_circuit_breaker_tripped


def test_reset_circuit_breaker_clears_window_and_resumes() -> None:
    manager = make_manager(expected_fill_rate=(0.5, 1.0), fill_rate_window=4)
    for _ in range(4):
        manager.record_quote_cycle(False)
    assert manager.is_circuit_breaker_tripped

    manager.reset_circuit_breaker()

    assert not manager.is_circuit_breaker_tripped
    gated = manager.gate_quote(QUOTE, inventory=0.0, last_market_data_ms=1000, now_ms=1200)
    assert gated == QUOTE


def test_fill_rate_is_none_before_any_cycles_recorded() -> None:
    manager = make_manager()
    assert manager.fill_rate is None


def test_fill_rate_reflects_recent_cycles() -> None:
    manager = make_manager(fill_rate_window=4)
    for filled in (True, False, True, False):
        manager.record_quote_cycle(filled)

    assert manager.fill_rate == 0.5


def test_risk_limits_rejects_invalid_fill_rate_bounds() -> None:
    with pytest.raises(ValueError):
        RiskLimits(
            max_position=10.0,
            max_daily_loss=100.0,
            max_stale_data_ms=1000,
            expected_fill_rate=(0.9, 0.1),
        )
