from __future__ import annotations

import logging

from crypto_mm_engine.execution.models import OrderExecutionAdapter, Side
from crypto_mm_engine.quoting.models import Quote

logger = logging.getLogger(__name__)


class QuoteManager:
    """Cancel-and-replace bookkeeping shared between backtest and live:
    given a new Quote, cancels whatever's resting on each side and places
    the replacement, tracking the adapter's order id per side. This is the
    part of the strategy loop that stays identical between backtest and
    live - only the adapter underneath differs.
    """

    def __init__(self, adapter: OrderExecutionAdapter) -> None:
        self._adapter = adapter
        self.bid_order_id: str | None = None
        self.ask_order_id: str | None = None

    def apply_quote(self, quote: Quote) -> None:
        if self.bid_order_id is not None:
            self._cancel(self.bid_order_id)
            self.bid_order_id = None
        if self.ask_order_id is not None:
            self._cancel(self.ask_order_id)
            self.ask_order_id = None

        if quote.bid_price is not None and quote.bid_size > 0:
            self.bid_order_id = self._adapter.place_order(Side.BID, quote.bid_price, quote.bid_size)
        if quote.ask_price is not None and quote.ask_size > 0:
            self.ask_order_id = self._adapter.place_order(Side.ASK, quote.ask_price, quote.ask_size)

    def _cancel(self, order_id: str) -> None:
        try:
            self._adapter.cancel_order(order_id)
        except Exception as exc:
            # The order may already be gone on the venue - filled,
            # canceled, or expired before we got to it, an inherent race
            # in live trading (a fill notification and our next requote
            # can cross in flight). Either way it's not "resting" from our
            # perspective anymore, so the caller clears the id regardless -
            # retrying the same doomed cancel forever would permanently
            # stall this side.
            logger.warning("cancel failed for order %s, dropping it: %s", order_id, exc)

    def clear_if_closed(self, side: Side, order_id: str, still_open: bool) -> None:
        """Call when a fill notification arrives for order_id; clears our
        tracked id once the venue reports it's no longer resting."""
        if still_open:
            return
        if side is Side.BID and self.bid_order_id == order_id:
            self.bid_order_id = None
        if side is Side.ASK and self.ask_order_id == order_id:
            self.ask_order_id = None
