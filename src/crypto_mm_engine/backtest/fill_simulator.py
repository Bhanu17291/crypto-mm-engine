from __future__ import annotations

from crypto_mm_engine.backtest.models import FeeSchedule, Fill, RestingOrder, Side
from crypto_mm_engine.data.models import Trade


class FillSimulator:
    """Simulates our resting limit orders against the replayed trade tape
    using price-time-priority queue position, not a naive "if price
    crosses, fill" check.

    A new order's queue position is seeded with whatever size was already
    displayed at that price when we placed it - we assume we join at the
    back of an existing queue. Trade prints at that price then consume the
    queue from the front; once the size ahead of us is exhausted, further
    trade volume at that price fills our order (partial fills included). A
    resting-order size decrease from a depth update that ISN'T accompanied
    by a matching trade print is a cancellation, and we assume it happens
    behind us - the conservative assumption, since it never makes our fills
    more optimistic than reality would allow.

    Binance's trade stream tags which side was the resting maker via
    is_buyer_maker: True means a resting bid got hit by an aggressor sell,
    False means a resting ask got hit by an aggressor buy.
    """

    def __init__(self, fees: FeeSchedule) -> None:
        self._fees = fees
        self._orders: dict[int, RestingOrder] = {}
        self._next_id = 1

    def place_order(
        self, side: Side, price: float, size: float, queue_ahead: float, now_ms: int
    ) -> int:
        order_id = self._next_id
        self._next_id += 1
        self._orders[order_id] = RestingOrder(
            order_id=order_id,
            side=side,
            price=price,
            remaining=size,
            queue_ahead=queue_ahead,
            placed_at_ms=now_ms,
        )
        return order_id

    def cancel_order(self, order_id: int) -> None:
        self._orders.pop(order_id, None)

    def has_order(self, order_id: int) -> bool:
        return order_id in self._orders

    def on_trade(self, trade: Trade, mid_price: float) -> list[Fill]:
        target_side = Side.BID if trade.is_buyer_maker else Side.ASK
        matching = sorted(
            (o for o in self._orders.values() if o.side is target_side and o.price == trade.price),
            key=lambda o: o.placed_at_ms,
        )

        remaining_trade_qty = trade.quantity
        fills: list[Fill] = []
        for order in matching:
            if remaining_trade_qty <= 0:
                break

            consumed_from_queue = min(remaining_trade_qty, order.queue_ahead)
            order.queue_ahead -= consumed_from_queue
            remaining_trade_qty -= consumed_from_queue
            if remaining_trade_qty <= 0 or order.queue_ahead > 0:
                continue

            fill_qty = min(remaining_trade_qty, order.remaining)
            order.remaining -= fill_qty
            remaining_trade_qty -= fill_qty
            fills.append(
                Fill(
                    order_id=order.order_id,
                    side=order.side,
                    price=order.price,
                    quantity=fill_qty,
                    fee=fill_qty * order.price * self._fees.maker_fee_rate,
                    timestamp_ms=trade.trade_time_ms,
                    mid_price_at_fill=mid_price,
                )
            )
            if order.remaining <= 0:
                del self._orders[order.order_id]

        return fills
