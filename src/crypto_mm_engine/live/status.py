from __future__ import annotations

from pydantic import BaseModel

from crypto_mm_engine.backtest.pnl import PnLTracker
from crypto_mm_engine.data.models import PriceLevel, Trade
from crypto_mm_engine.execution.models import LiveFill
from crypto_mm_engine.quoting.avellaneda_stoikov import optimal_spread, reservation_price
from crypto_mm_engine.quoting.models import Quote, QuotingParams
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
    fill_rate: float | None


class PriceLevelStatus(BaseModel):
    price: float
    quantity: float


class OrderBookStatus(BaseModel):
    bids: list[PriceLevelStatus]
    asks: list[PriceLevelStatus]


class QuotingParamsStatus(BaseModel):
    risk_aversion: float
    order_arrival_intensity: float
    volatility: float
    time_horizon_s: float
    max_inventory: float
    quote_size: float


class RiskLimitsStatus(BaseModel):
    max_position: float
    max_daily_loss: float
    max_stale_data_ms: int
    min_fill_rate: float
    max_fill_rate: float
    fill_rate_window: int


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
    reservation_price: float
    optimal_spread: float
    time_remaining_s: float
    bid_order_id: str | None
    ask_order_id: str | None
    requote_latency_ms: float
    book: OrderBookStatus
    quoting_params: QuotingParamsStatus
    risk_limits: RiskLimitsStatus


class FillEvent(BaseModel):
    order_id: str
    side: str
    price: float
    quantity: float
    fee: float
    timestamp_ms: int


class TradeTapeEvent(BaseModel):
    price: float
    quantity: float
    is_buyer_maker: bool
    timestamp_ms: int


class CancelEvent(BaseModel):
    order_id: str
    timestamp_ms: int


def _level_statuses(levels: list[PriceLevel]) -> list[PriceLevelStatus]:
    return [PriceLevelStatus(price=level.price, quantity=level.quantity) for level in levels]


def build_status_snapshot(
    symbol: str,
    mid_price: float,
    max_position: float,
    pnl: PnLTracker,
    quote: Quote,
    risk: RiskManager,
    timestamp_ms: int,
    quoting_params: QuotingParams,
    time_remaining_s: float,
    bid_order_id: str | None,
    ask_order_id: str | None,
    requote_latency_ms: float,
    book_bids: list[PriceLevel],
    book_asks: list[PriceLevel],
) -> StatusSnapshot:
    """Pulled out of the runner so it's testable without a live connection:
    given the same state the runner already has, builds the exact payload
    the API/dashboard consumes."""
    low, high = risk.limits.expected_fill_rate
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
            fill_rate=risk.fill_rate,
        ),
        reservation_price=reservation_price(
            mid_price, pnl.inventory, quoting_params, time_remaining_s
        ),
        optimal_spread=optimal_spread(quoting_params, time_remaining_s),
        time_remaining_s=time_remaining_s,
        bid_order_id=bid_order_id,
        ask_order_id=ask_order_id,
        requote_latency_ms=requote_latency_ms,
        book=OrderBookStatus(bids=_level_statuses(book_bids), asks=_level_statuses(book_asks)),
        quoting_params=QuotingParamsStatus(
            risk_aversion=quoting_params.risk_aversion,
            order_arrival_intensity=quoting_params.order_arrival_intensity,
            volatility=quoting_params.volatility,
            time_horizon_s=quoting_params.time_horizon_s,
            max_inventory=quoting_params.max_inventory,
            quote_size=quoting_params.quote_size,
        ),
        risk_limits=RiskLimitsStatus(
            max_position=risk.limits.max_position,
            max_daily_loss=risk.limits.max_daily_loss,
            max_stale_data_ms=risk.limits.max_stale_data_ms,
            min_fill_rate=low,
            max_fill_rate=high,
            fill_rate_window=risk.limits.fill_rate_window,
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


def build_trade_tape_event(trade: Trade) -> TradeTapeEvent:
    return TradeTapeEvent(
        price=trade.price,
        quantity=trade.quantity,
        is_buyer_maker=trade.is_buyer_maker,
        timestamp_ms=trade.trade_time_ms,
    )


def build_cancel_event(order_id: str, timestamp_ms: int) -> CancelEvent:
    return CancelEvent(order_id=order_id, timestamp_ms=timestamp_ms)
