from __future__ import annotations

from crypto_mm_engine.backtest.models import Fill, Side

_EPSILON = 1e-9


class PnLTracker:
    """Weighted-average-cost P&L accounting: realized P&L is booked as
    inventory is closed against its average entry price, unrealized P&L is
    whatever's left marked against the current mid."""

    def __init__(self) -> None:
        self.realized_pnl = 0.0
        self.inventory = 0.0
        self.avg_entry_price = 0.0
        self.fees_paid = 0.0

    def on_fill(self, fill: Fill) -> None:
        self.fees_paid += fill.fee
        self.realized_pnl -= fill.fee

        signed_qty = fill.quantity if fill.side is Side.BID else -fill.quantity
        opening_or_adding = self.inventory == 0 or (self.inventory > 0) == (signed_qty > 0)

        if opening_or_adding:
            new_inventory = self.inventory + signed_qty
            self.avg_entry_price = (
                self.avg_entry_price * self.inventory + fill.price * signed_qty
            ) / new_inventory
            self.inventory = new_inventory
            return

        closing_qty = min(abs(signed_qty), abs(self.inventory))
        direction = 1.0 if self.inventory > 0 else -1.0
        self.realized_pnl += direction * closing_qty * (fill.price - self.avg_entry_price)

        new_inventory = self.inventory + signed_qty
        if abs(new_inventory) < _EPSILON:
            self.inventory = 0.0
            self.avg_entry_price = 0.0
        elif (new_inventory > 0) != (self.inventory > 0):
            # flipped through zero: the leftover opens a fresh position at this fill's price
            self.inventory = new_inventory
            self.avg_entry_price = fill.price
        else:
            self.inventory = new_inventory

    def unrealized_pnl(self, mark_price: float) -> float:
        return self.inventory * (mark_price - self.avg_entry_price)

    def equity(self, mark_price: float) -> float:
        return self.realized_pnl + self.unrealized_pnl(mark_price)
