import math

import pytest

from crypto_mm_engine.quoting.avellaneda_stoikov import (
    compute_quotes,
    optimal_spread,
    reservation_price,
)
from crypto_mm_engine.quoting.models import QuotingParams

BASE_PARAMS = QuotingParams(
    risk_aversion=0.1,
    order_arrival_intensity=1.5,
    volatility=0.02,
    time_horizon_s=3600.0,
    max_inventory=10.0,
    quote_size=1.0,
)
MID = 30_000.0


def test_reservation_price_equals_mid_when_flat() -> None:
    assert reservation_price(MID, 0.0, BASE_PARAMS, 1800.0) == MID


def test_reservation_price_below_mid_when_long() -> None:
    assert reservation_price(MID, 5.0, BASE_PARAMS, 1800.0) < MID


def test_reservation_price_above_mid_when_short() -> None:
    assert reservation_price(MID, -5.0, BASE_PARAMS, 1800.0) > MID


def test_reservation_price_penalty_scales_with_inventory_and_time() -> None:
    penalty_small_q = MID - reservation_price(MID, 1.0, BASE_PARAMS, 1800.0)
    penalty_large_q = MID - reservation_price(MID, 5.0, BASE_PARAMS, 1800.0)
    assert penalty_large_q == pytest.approx(5 * penalty_small_q)

    penalty_less_time = MID - reservation_price(MID, 5.0, BASE_PARAMS, 900.0)
    assert penalty_less_time < penalty_large_q


def test_optimal_spread_matches_closed_form() -> None:
    time_remaining = 1800.0
    expected = BASE_PARAMS.risk_aversion * BASE_PARAMS.volatility**2 * time_remaining + (
        2 / BASE_PARAMS.risk_aversion
    ) * math.log(1 + BASE_PARAMS.risk_aversion / BASE_PARAMS.order_arrival_intensity)

    assert optimal_spread(BASE_PARAMS, time_remaining) == pytest.approx(expected)


def test_optimal_spread_widens_with_risk_aversion() -> None:
    low_gamma = QuotingParams(
        risk_aversion=0.05,
        order_arrival_intensity=1.5,
        volatility=0.02,
        time_horizon_s=3600.0,
        max_inventory=10.0,
        quote_size=1.0,
    )
    high_gamma = QuotingParams(
        risk_aversion=0.5,
        order_arrival_intensity=1.5,
        volatility=0.02,
        time_horizon_s=3600.0,
        max_inventory=10.0,
        quote_size=1.0,
    )
    assert optimal_spread(high_gamma, 1800.0) > optimal_spread(low_gamma, 1800.0)


def test_optimal_spread_tightens_with_higher_arrival_intensity() -> None:
    low_kappa = QuotingParams(
        risk_aversion=0.1,
        order_arrival_intensity=0.5,
        volatility=0.02,
        time_horizon_s=3600.0,
        max_inventory=10.0,
        quote_size=1.0,
    )
    high_kappa = QuotingParams(
        risk_aversion=0.1,
        order_arrival_intensity=5.0,
        volatility=0.02,
        time_horizon_s=3600.0,
        max_inventory=10.0,
        quote_size=1.0,
    )
    assert optimal_spread(high_kappa, 1800.0) < optimal_spread(low_kappa, 1800.0)


def test_compute_quotes_symmetric_around_reservation_price_when_flat() -> None:
    quote = compute_quotes(MID, 0.0, BASE_PARAMS, 1800.0)
    assert quote.bid_price is not None and quote.ask_price is not None
    assert quote.bid_price < MID < quote.ask_price
    assert (MID - quote.bid_price) == pytest.approx(quote.ask_price - MID)
    assert quote.bid_size == BASE_PARAMS.quote_size
    assert quote.ask_size == BASE_PARAMS.quote_size


def test_compute_quotes_skews_down_when_long() -> None:
    flat = compute_quotes(MID, 0.0, BASE_PARAMS, 1800.0)
    long = compute_quotes(MID, 5.0, BASE_PARAMS, 1800.0)
    assert long.bid_price is not None and flat.bid_price is not None
    assert long.ask_price is not None and flat.ask_price is not None
    assert long.bid_price < flat.bid_price
    assert long.ask_price < flat.ask_price


def test_compute_quotes_shrinks_size_approaching_limit_without_hitting_it() -> None:
    quote = compute_quotes(MID, 8.0, BASE_PARAMS, 1800.0)  # 80% of max_inventory=10
    assert quote.bid_price is not None
    assert 0.0 < quote.bid_size < BASE_PARAMS.quote_size
    assert quote.ask_size == BASE_PARAMS.quote_size  # selling reduces inventory, stays full


def test_compute_quotes_drops_bid_at_long_position_limit() -> None:
    quote = compute_quotes(MID, BASE_PARAMS.max_inventory, BASE_PARAMS, 1800.0)
    assert quote.bid_price is None
    assert quote.bid_size == 0.0
    assert quote.ask_price is not None
    assert quote.ask_size == BASE_PARAMS.quote_size


def test_compute_quotes_drops_ask_at_short_position_limit() -> None:
    quote = compute_quotes(MID, -BASE_PARAMS.max_inventory, BASE_PARAMS, 1800.0)
    assert quote.ask_price is None
    assert quote.ask_size == 0.0
    assert quote.bid_price is not None
    assert quote.bid_size == BASE_PARAMS.quote_size


def test_quoting_params_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        QuotingParams(
            risk_aversion=0.0,
            order_arrival_intensity=1.5,
            volatility=0.02,
            time_horizon_s=3600.0,
            max_inventory=10.0,
            quote_size=1.0,
        )
    with pytest.raises(ValueError):
        QuotingParams(
            risk_aversion=0.1,
            order_arrival_intensity=1.5,
            volatility=0.02,
            time_horizon_s=3600.0,
            max_inventory=0.0,
            quote_size=1.0,
        )
