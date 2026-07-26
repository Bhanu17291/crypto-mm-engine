from __future__ import annotations

import math

from crypto_mm_engine.quoting.models import Quote, QuotingParams


def reservation_price(
    mid_price: float, inventory: float, params: QuotingParams, time_remaining_s: float
) -> float:
    """Avellaneda-Stoikov (2008) reservation price:

        r(s, q, t) = s - q * gamma * sigma^2 * (T - t)

    A market maker carrying inventory q is exposed to sigma^2*(T-t) worth of
    price variance over the rest of the horizon. gamma converts that variance
    into a price penalty. Being long (q > 0) pulls the reservation price
    below mid, which skews both quotes down and makes the ask relatively more
    attractive to hit - i.e. it biases the desk toward selling down the
    position. Being short does the opposite. At q = 0 the reservation price
    is just the mid.
    """
    return mid_price - inventory * params.risk_aversion * params.volatility**2 * time_remaining_s


def optimal_spread(params: QuotingParams, time_remaining_s: float) -> float:
    """Avellaneda-Stoikov optimal total bid-ask spread:

        delta = gamma * sigma^2 * (T - t) + (2 / gamma) * ln(1 + gamma / kappa)

    The first term is the same inventory-risk quantity as in the reservation
    price, spread symmetrically around it - more time left or more variance
    means a wider book. The second term falls out of assuming an exponential
    fill-arrival rate lambda(delta) = A * exp(-kappa * delta): kappa is how
    fast your fill probability decays as you quote further from mid, so a
    larger kappa (fills die off quickly with distance) tightens the spread,
    while higher risk aversion widens it.
    """
    inventory_term = params.risk_aversion * params.volatility**2 * time_remaining_s
    arrival_term = (2 / params.risk_aversion) * math.log(
        1 + params.risk_aversion / params.order_arrival_intensity
    )
    return inventory_term + arrival_term


def _inventory_skew_factor(inventory: float, max_inventory: float, side_sign: float) -> float:
    """Shrinks quote size toward zero as inventory approaches the limit that
    side's fill would push toward, on top of the price skew above.

    side_sign is +1 for the bid (buying increases inventory, so it should
    shrink as inventory -> +max_inventory) and -1 for the ask (selling
    decreases inventory, so it shrinks as inventory -> -max_inventory). The
    side moving inventory back toward zero keeps full size.
    """
    utilization = inventory / max_inventory
    return max(0.0, min(1.0, 1 - side_sign * utilization))


def compute_quotes(
    mid_price: float, inventory: float, params: QuotingParams, time_remaining_s: float
) -> Quote:
    """Combines the AS reservation price/spread with a hard position limit:
    a side is dropped entirely once inventory reaches max_inventory on that
    side, with size skewed down as it approaches that limit."""
    r = reservation_price(mid_price, inventory, params, time_remaining_s)
    delta = optimal_spread(params, time_remaining_s)
    raw_bid = r - delta / 2
    raw_ask = r + delta / 2

    at_long_limit = inventory >= params.max_inventory
    at_short_limit = inventory <= -params.max_inventory

    bid_size = params.quote_size * _inventory_skew_factor(inventory, params.max_inventory, 1.0)
    ask_size = params.quote_size * _inventory_skew_factor(inventory, params.max_inventory, -1.0)

    return Quote(
        bid_price=None if at_long_limit else raw_bid,
        bid_size=0.0 if at_long_limit else bid_size,
        ask_price=None if at_short_limit else raw_ask,
        ask_size=0.0 if at_short_limit else ask_size,
    )
