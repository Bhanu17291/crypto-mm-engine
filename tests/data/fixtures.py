"""Hand-recorded sample payloads shaped like Binance's documented message
formats, used so tests never touch the network. Not pulled from a live
session — just representative fixtures."""

from __future__ import annotations

from typing import Any

from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, PriceLevel, Trade

RAW_DEPTH_UPDATE_MESSAGE: dict[str, Any] = {
    "stream": "btcusdt@depth",
    "data": {
        "e": "depthUpdate",
        "E": 1700000000000,
        "s": "BTCUSDT",
        "U": 157,
        "u": 160,
        "b": [["30000.00", "1.5"], ["29999.50", "0.0"]],
        "a": [["30001.00", "2.0"]],
    },
}

RAW_TRADE_MESSAGE: dict[str, Any] = {
    "stream": "btcusdt@trade",
    "data": {
        "e": "trade",
        "E": 1700000000100,
        "s": "BTCUSDT",
        "t": 5001,
        "p": "30000.50",
        "q": "0.01",
        "b": 88,
        "a": 50,
        "T": 1700000000050,
        "m": True,
        "M": True,
    },
}

RAW_DEPTH_SNAPSHOT_PAYLOAD: dict[str, Any] = {
    "lastUpdateId": 159,
    "bids": [["30000.00", "1.0"], ["29900.00", "3.0"]],
    "asks": [["30001.00", "2.0"], ["30100.00", "5.0"]],
}


def make_snapshot(last_update_id: int = 159) -> DepthSnapshot:
    return DepthSnapshot(
        symbol="BTCUSDT",
        last_update_id=last_update_id,
        bids=(PriceLevel(30000.0, 1.0), PriceLevel(29900.0, 3.0)),
        asks=(PriceLevel(30001.0, 2.0), PriceLevel(30100.0, 5.0)),
    )


def make_update(
    first_update_id: int, final_update_id: int, event_time_ms: int = 1700000000000
) -> DepthUpdate:
    return DepthUpdate(
        symbol="BTCUSDT",
        first_update_id=first_update_id,
        final_update_id=final_update_id,
        event_time_ms=event_time_ms,
        bids=(PriceLevel(29999.0, 0.5),),
        asks=(PriceLevel(30002.0, 0.5),),
    )


def make_trade(trade_id: int = 1, trade_time_ms: int = 1700000000050) -> Trade:
    return Trade(
        symbol="BTCUSDT",
        trade_id=trade_id,
        price=30000.5,
        quantity=0.01,
        trade_time_ms=trade_time_ms,
        is_buyer_maker=True,
    )
