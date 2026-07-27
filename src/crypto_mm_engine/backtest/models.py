from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Side(Enum):
    BID = "bid"
    ASK = "ask"


@dataclass(frozen=True, slots=True)
class FeeSchedule:
    # Binance spot VIP0 maker rate. We only model resting (maker) fills here,
    # since a market maker crossing the spread itself isn't in scope yet.
    maker_fee_rate: float = 0.001


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    fees: FeeSchedule = field(default_factory=FeeSchedule)
    latency_ms: int = 50  # delay between a quote decision and the order resting in the book


@dataclass(slots=True)
class RestingOrder:
    order_id: int
    side: Side
    price: float
    remaining: float
    queue_ahead: float
    placed_at_ms: int


@dataclass(frozen=True, slots=True)
class Fill:
    order_id: int
    side: Side
    price: float
    quantity: float
    fee: float
    timestamp_ms: int
    mid_price_at_fill: float


@dataclass(frozen=True, slots=True)
class EquityPoint:
    timestamp_ms: int
    mid_price: float
    inventory: float
    realized_pnl: float
    unrealized_pnl: float
    equity: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    equity_curve: list[EquityPoint]
    fills: list[Fill]

    @property
    def total_fees(self) -> float:
        return sum(f.fee for f in self.fills)

    @property
    def average_spread_capture(self) -> float:
        """Mean of (our price - mid at fill time), signed so a profitable
        maker fill - selling above mid or buying below mid - is positive."""
        if not self.fills:
            return 0.0
        captures = [
            (
                (f.price - f.mid_price_at_fill)
                if f.side is Side.ASK
                else (f.mid_price_at_fill - f.price)
            )
            for f in self.fills
        ]
        return sum(captures) / len(captures)
