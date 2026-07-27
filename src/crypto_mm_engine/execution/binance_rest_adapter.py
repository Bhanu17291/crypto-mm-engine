from __future__ import annotations

import logging
import time
from decimal import ROUND_DOWN, Decimal
from typing import Any

import httpx

from crypto_mm_engine.execution.binance_signing import build_signed_params
from crypto_mm_engine.execution.models import Side

logger = logging.getLogger(__name__)

_SIDE_TO_BINANCE = {Side.BID: "BUY", Side.ASK: "SELL"}
_RECV_WINDOW_MS = "60000"  # generous tolerance for local clock drift


def round_to_step(value: float, step: Decimal) -> str:
    """Floors value to the exchange's tick/lot size. Binance rejects any
    price or quantity that isn't an exact multiple of the symbol's
    PRICE_FILTER.tickSize / LOT_SIZE.stepSize - our quoting math has no
    idea what those are, so this has to happen at the execution boundary.
    Rounding down (not to nearest) means we never quote a size or price
    outside what was actually intended.
    """
    return str(Decimal(str(value)).quantize(step, rounding=ROUND_DOWN))


class BinanceTestnetExecutionAdapter:
    """Places real (paper-money) limit orders against Binance's Spot
    Testnet via signed REST calls - the same OrderExecutionAdapter shape
    the backtest adapter implements, so nothing upstream (quoting, risk
    gating, QuoteManager) needs to know it's talking to a live exchange
    instead of a simulator.

    Deliberately synchronous (httpx.Client) rather than async: this is a
    paper-trading runner, not a latency-sensitive production system, and a
    blocking call from inside an async WS callback keeps the call site
    simple. A production version would move this off the event loop.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        symbol: str,
        base_url: str = "https://testnet.binance.vision",
    ) -> None:
        self._api_secret = api_secret
        self._symbol = symbol.upper()
        self._client = httpx.Client(
            base_url=base_url, headers={"X-MBX-APIKEY": api_key}, timeout=5.0
        )
        self._tick_size: Decimal | None = None
        self._step_size: Decimal | None = None

    def close(self) -> None:
        self._client.close()

    def place_order(self, side: Side, price: float, size: float) -> str:
        tick_size, step_size = self._symbol_filters()
        params = {
            "symbol": self._symbol,
            "side": _SIDE_TO_BINANCE[side],
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": round_to_step(size, step_size),
            "price": round_to_step(price, tick_size),
        }
        result = self._signed_request("POST", "/api/v3/order", params)
        return str(result["orderId"])

    def cancel_order(self, order_id: str) -> None:
        params = {"symbol": self._symbol, "orderId": order_id}
        self._signed_request("DELETE", "/api/v3/order", params)

    def _symbol_filters(self) -> tuple[Decimal, Decimal]:
        if self._tick_size is not None and self._step_size is not None:
            return self._tick_size, self._step_size

        response = self._client.get("/api/v3/exchangeInfo", params={"symbol": self._symbol})
        response.raise_for_status()
        filters = response.json()["symbols"][0]["filters"]
        tick_size = next(
            Decimal(f["tickSize"]) for f in filters if f["filterType"] == "PRICE_FILTER"
        )
        step_size = next(Decimal(f["stepSize"]) for f in filters if f["filterType"] == "LOT_SIZE")
        self._tick_size, self._step_size = tick_size, step_size
        return tick_size, step_size

    def _signed_request(self, method: str, path: str, params: dict[str, str]) -> dict[str, Any]:
        payload = dict(params)
        payload.setdefault("recvWindow", _RECV_WINDOW_MS)
        signed = build_signed_params(payload, self._api_secret, int(time.time() * 1000))
        response = self._client.request(method, path, params=signed)
        if response.is_error:
            logger.error(
                "Binance API error %s %s -> %s: %s",
                method,
                path,
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result
