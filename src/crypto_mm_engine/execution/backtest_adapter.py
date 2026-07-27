from __future__ import annotations

from crypto_mm_engine.backtest.fill_simulator import FillSimulator
from crypto_mm_engine.data.order_book import OrderBook
from crypto_mm_engine.execution.models import Side


class BacktestExecutionAdapter:
    """Adapts FillSimulator - which needs queue_ahead and now_ms to seed a
    resting order's queue position - to the plain OrderExecutionAdapter
    shape the shared QuoteManager expects. The backtest engine updates
    now_ms each tick before handing a quote to the QuoteManager.
    """

    def __init__(self, fill_sim: FillSimulator, book: OrderBook) -> None:
        self._fill_sim = fill_sim
        self._book = book
        self.now_ms = 0

    def place_order(self, side: Side, price: float, size: float) -> str:
        queue_ahead = (
            self._book.bid_quantity_at(price)
            if side is Side.BID
            else self._book.ask_quantity_at(price)
        )
        order_id = self._fill_sim.place_order(side, price, size, queue_ahead, self.now_ms)
        return str(order_id)

    def cancel_order(self, order_id: str) -> None:
        self._fill_sim.cancel_order(int(order_id))
