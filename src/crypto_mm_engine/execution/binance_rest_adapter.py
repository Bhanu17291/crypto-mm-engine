from __future__ import annotations

import time
from typing import Any

import httpx

from crypto_mm_engine.execution.binance_signing import build_signed_params
from crypto_mm_engine.execution.models import Side

_SIDE_TO_BINANCE = {Side.BID: "BUY", Side.ASK: "SELL"}


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

    def close(self) -> None:
        self._client.close()

    def place_order(self, side: Side, price: float, size: float) -> str:
        params = {
            "symbol": self._symbol,
            "side": _SIDE_TO_BINANCE[side],
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": f"{size:.8f}",
            "price": f"{price:.8f}",
        }
        result = self._signed_request("POST", "/api/v3/order", params)
        return str(result["orderId"])

    def cancel_order(self, order_id: str) -> None:
        params = {"symbol": self._symbol, "orderId": order_id}
        self._signed_request("DELETE", "/api/v3/order", params)

    def _signed_request(self, method: str, path: str, params: dict[str, str]) -> dict[str, Any]:
        signed = build_signed_params(params, self._api_secret, int(time.time() * 1000))
        response = self._client.request(method, path, params=signed)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result
