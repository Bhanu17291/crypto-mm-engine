from __future__ import annotations

from pydantic import BaseModel

from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.execution.models import LiveFill
from crypto_mm_engine.quoting.models import Quote
from crypto_mm_engine.risk.risk_manager import RiskManager


class QuoteStatus(BaseModel):
    bid_price: float | None
    bid_size: float
    ask_price: float | None
    ask_size: float


class RiskStatus(BaseModel):
    halted: bool
    kill_switch_tripped: bool
    circuit_breaker_tripped: bool


class StatusSnapshot(BaseModel):
    timestamp_ms: int
    symbol: str
    mid_price: float
    inventory: float
    max_position: float
    realized_pnl: float
    unrealized_pnl: float
    equity: float
    fees_paid: float
    quote: QuoteStatus
    risk: RiskStatus


class FillEvent(BaseModel):
    order_id: str
    side: str
    price: float
    quantity: float
    fee: float
    timestamp_ms: int


def build_status_snapshot(
    symbol: str,
    mid_price: float,
    max_position: float,
    pnl: PnLTracker,
    quote: Quote,
    risk: RiskManager,
    timestamp_ms: int,
) -> StatusSnapshot:
    """Pulled out of the runner so it's testable without a live connection:
    given the same state the runner already has (a PnLTracker, a Quote, a
    RiskManager), builds the exact payload the API/dashboard consumes."""
    return StatusSnapshot(
        timestamp_ms=timestamp_ms,
        symbol=symbol,
        mid_price=mid_price,
        inventory=pnl.inventory,
        max_position=max_position,
        realized_pnl=pnl.realized_pnl,
        unrealized_pnl=pnl.unrealized_pnl(mid_price),
        equity=pnl.equity(mid_price),
        fees_paid=pnl.fees_paid,
        quote=QuoteStatus(
            bid_price=quote.bid_price,
            bid_size=quote.bid_size,
            ask_price=quote.ask_price,
            ask_size=quote.ask_size,
        ),
        risk=RiskStatus(
            halted=risk.is_halted,
            kill_switch_tripped=risk.is_kill_switch_tripped,
            circuit_breaker_tripped=risk.is_circuit_breaker_tripped,
        ),
    )


def build_fill_event(fill: LiveFill) -> FillEvent:
    return FillEvent(
        order_id=fill.order_id,
        side=fill.side.value,
        price=fill.price,
        quantity=fill.quantity,
        fee=fill.fee,
        timestamp_ms=fill.timestamp_ms,
    )
