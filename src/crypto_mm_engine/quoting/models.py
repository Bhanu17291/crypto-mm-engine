from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QuotingParams:
    """Inputs to the Avellaneda-Stoikov model, plus the risk limit that sits
    on top of it. gamma/kappa/sigma are typically fit or calibrated per
    symbol; max_inventory and quote_size are risk/desk decisions."""

    risk_aversion: float  # gamma: higher = wider spread, stronger inventory skew
    # kappa: higher = fills decay faster with distance from mid, tighter spread
    order_arrival_intensity: float
    volatility: float  # sigma: price volatility, same time units as time_horizon_s
    time_horizon_s: float  # T: total quoting horizon (e.g. one trading session)
    max_inventory: float  # hard cap on |position|, in base asset units
    quote_size: float  # base order size per side, before inventory skew

    def __post_init__(self) -> None:
        if self.risk_aversion <= 0:
            raise ValueError("risk_aversion must be positive")
        if self.order_arrival_intensity <= 0:
            raise ValueError("order_arrival_intensity must be positive")
        if self.volatility < 0:
            raise ValueError("volatility cannot be negative")
        if self.time_horizon_s <= 0:
            raise ValueError("time_horizon_s must be positive")
        if self.max_inventory <= 0:
            raise ValueError("max_inventory must be positive")
        if self.quote_size <= 0:
            raise ValueError("quote_size must be positive")


@dataclass(frozen=True, slots=True)
class Quote:
    """A side is None when the corresponding risk limit is fully hit; size
    is independently skewed down as inventory approaches (but hasn't yet
    hit) that limit."""

    bid_price: float | None
    bid_size: float
    ask_price: float | None
    ask_size: float
