from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import polars as pl

from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, PriceLevel, Trade


def _levels_to_rows(levels: tuple[PriceLevel, ...]) -> list[dict[str, float]]:
    return [{"price": lvl.price, "quantity": lvl.quantity} for lvl in levels]


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _trade_row(trade: Trade) -> dict[str, Any]:
    return {
        "ts_ms": trade.trade_time_ms,
        "trade_id": trade.trade_id,
        "price": trade.price,
        "quantity": trade.quantity,
        "is_buyer_maker": trade.is_buyer_maker,
    }


def _depth_update_row(update: DepthUpdate) -> dict[str, Any]:
    return {
        "ts_ms": update.event_time_ms,
        "first_update_id": update.first_update_id,
        "final_update_id": update.final_update_id,
        "bids": _levels_to_rows(update.bids),
        "asks": _levels_to_rows(update.asks),
    }


def _snapshot_row(snapshot: DepthSnapshot) -> dict[str, Any]:
    return {
        "ts_ms": _now_ms(),
        "last_update_id": snapshot.last_update_id,
        "bids": _levels_to_rows(snapshot.bids),
        "asks": _levels_to_rows(snapshot.asks),
    }


class ParquetWriter:
    """Buffers raw stream events and flushes them to parquet, one file per
    flush per event type. We persist the raw depth updates and trades
    (not the reconstructed book) so replay can rebuild the book exactly
    the way the live synchronizer would.
    """

    def __init__(self, data_dir: Path, symbol: str, flush_every: int = 1000) -> None:
        self.data_dir = data_dir
        self.symbol = symbol.lower()
        self.flush_every = flush_every
        self._trades: list[dict[str, Any]] = []
        self._depth_updates: list[dict[str, Any]] = []

    def record_trade(self, trade: Trade) -> None:
        self._trades.append(_trade_row(trade))
        if len(self._trades) >= self.flush_every:
            self.flush_trades()

    def record_depth_update(self, update: DepthUpdate) -> None:
        self._depth_updates.append(_depth_update_row(update))
        if len(self._depth_updates) >= self.flush_every:
            self.flush_depth_updates()

    def record_snapshot(self, snapshot: DepthSnapshot) -> None:
        # Rare relative to updates/trades, so write it out immediately
        # rather than holding it in the buffer.
        self._write([_snapshot_row(snapshot)], "snapshot")

    def flush_trades(self) -> None:
        self._write(self._trades, "trade")
        self._trades = []

    def flush_depth_updates(self) -> None:
        self._write(self._depth_updates, "depth_update")
        self._depth_updates = []

    def flush_all(self) -> None:
        self.flush_trades()
        self.flush_depth_updates()

    def _write(self, rows: list[dict[str, Any]], event_type: str) -> None:
        if not rows:
            return
        out_dir = self.data_dir / self.symbol / event_type
        out_dir.mkdir(parents=True, exist_ok=True)
        first_ts, last_ts = rows[0]["ts_ms"], rows[-1]["ts_ms"]
        path = out_dir / f"{first_ts}-{last_ts}.parquet"
        pl.DataFrame(rows).write_parquet(path)
