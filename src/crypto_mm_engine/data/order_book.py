from __future__ import annotations

from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, PriceLevel


class OrderBook:
    """Maintains one side-keyed price->quantity view of a symbol's book.

    Deliberately dumb: it applies whatever snapshot/update it's given and
    trusts the caller to have sequenced things correctly. Gap detection and
    resync live in OrderBookSynchronizer, one layer up, so this class stays
    trivial to unit test.
    """

    __slots__ = ("symbol", "last_update_id", "_bids", "_asks")

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.last_update_id = -1
        self._bids: dict[float, float] = {}
        self._asks: dict[float, float] = {}

    def apply_snapshot(self, snapshot: DepthSnapshot) -> None:
        self._bids = {level.price: level.quantity for level in snapshot.bids if level.quantity > 0}
        self._asks = {level.price: level.quantity for level in snapshot.asks if level.quantity > 0}
        self.last_update_id = snapshot.last_update_id

    def apply_update(self, update: DepthUpdate) -> None:
        for level in update.bids:
            self._set_level(self._bids, level)
        for level in update.asks:
            self._set_level(self._asks, level)
        self.last_update_id = update.final_update_id

    @staticmethod
    def _set_level(side: dict[float, float], level: PriceLevel) -> None:
        if level.quantity == 0:
            side.pop(level.price, None)
        else:
            side[level.price] = level.quantity

    def best_bid(self) -> PriceLevel | None:
        if not self._bids:
            return None
        price = max(self._bids)
        return PriceLevel(price, self._bids[price])

    def best_ask(self) -> PriceLevel | None:
        if not self._asks:
            return None
        price = min(self._asks)
        return PriceLevel(price, self._asks[price])

    def mid_price(self) -> float | None:
        bid, ask = self.best_bid(), self.best_ask()
        if bid is None or ask is None:
            return None
        return (bid.price + ask.price) / 2

    def depth(self, levels: int = 10) -> tuple[list[PriceLevel], list[PriceLevel]]:
        bids = sorted(
            (PriceLevel(p, q) for p, q in self._bids.items()),
            key=lambda level: level.price,
            reverse=True,
        )[:levels]
        asks = sorted(
            (PriceLevel(p, q) for p, q in self._asks.items()), key=lambda level: level.price
        )[:levels]
        return bids, asks
