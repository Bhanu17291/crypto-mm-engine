from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PriceLevel:
    price: float
    quantity: float


@dataclass(frozen=True, slots=True)
class DepthSnapshot:
    symbol: str
    last_update_id: int
    bids: tuple[PriceLevel, ...]
    asks: tuple[PriceLevel, ...]


@dataclass(frozen=True, slots=True)
class DepthUpdate:
    """One diff-depth event off the combined stream.

    first_update_id/final_update_id are Binance's U/u fields — the range of
    internal book updates this event covers. Consecutive events must chain
    U == previous.u + 1; a gap means we lost a message and have to resync.
    """

    symbol: str
    first_update_id: int
    final_update_id: int
    event_time_ms: int
    bids: tuple[PriceLevel, ...]
    asks: tuple[PriceLevel, ...]


@dataclass(frozen=True, slots=True)
class Trade:
    symbol: str
    trade_id: int
    price: float
    quantity: float
    trade_time_ms: int
    is_buyer_maker: bool
