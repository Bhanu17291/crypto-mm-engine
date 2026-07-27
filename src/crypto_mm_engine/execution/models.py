from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class Side(Enum):
    BID = "bid"
    ASK = "ask"


class OrderExecutionAdapter(Protocol):
    """The one seam between strategy and exchange: backtest and live each
    implement this the same way, so nothing above it - quoting, risk
    gating, cancel/replace bookkeeping - needs to know which one it's
    talking to."""

    def place_order(self, side: Side, price: float, size: float) -> str: ...

    def cancel_order(self, order_id: str) -> None: ...


@dataclass(frozen=True, slots=True)
class LiveFill:
    order_id: str
    side: Side
    price: float
    quantity: float
    fee: float
    timestamp_ms: int
    order_status: str


def parse_execution_report(data: dict[str, Any]) -> LiveFill | None:
    """Binance's user data stream reports every order state transition, not
    just fills - x is the event's execution type (NEW, TRADE, CANCELED, ...)
    and only "TRADE" represents an actual fill, so anything else is None."""
    if data.get("e") != "executionReport" or data.get("x") != "TRADE":
        return None
    return LiveFill(
        order_id=str(data["i"]),
        side=Side.BID if data["S"] == "BUY" else Side.ASK,
        price=float(data["L"]),
        quantity=float(data["l"]),
        fee=float(data["n"]),
        timestamp_ms=data["T"],
        order_status=data["X"],
    )
