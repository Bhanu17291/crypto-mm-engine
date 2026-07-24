from __future__ import annotations

import heapq
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import polars as pl

from crypto_mm_engine.data.models import DepthSnapshot, DepthUpdate, PriceLevel, Trade


def _levels_from_rows(rows: list[dict[str, Any]]) -> tuple[PriceLevel, ...]:
    return tuple(PriceLevel(float(r["price"]), float(r["quantity"])) for r in rows)


def _read_event_dir(data_dir: Path, symbol: str, event_type: str) -> Iterator[dict[str, Any]]:
    event_dir = data_dir / symbol.lower() / event_type
    if not event_dir.exists():
        return
    # Filenames are "{first_ts}-{last_ts}.parquet"; sorting by name sorts by
    # time since both halves are zero-free millisecond epoch integers.
    for path in sorted(event_dir.glob("*.parquet")):
        yield from pl.read_parquet(path).iter_rows(named=True)


def replay_trades(data_dir: Path, symbol: str) -> Iterator[Trade]:
    for row in _read_event_dir(data_dir, symbol, "trade"):
        yield Trade(
            symbol=symbol.upper(),
            trade_id=row["trade_id"],
            price=row["price"],
            quantity=row["quantity"],
            trade_time_ms=row["ts_ms"],
            is_buyer_maker=row["is_buyer_maker"],
        )


def replay_depth_updates(data_dir: Path, symbol: str) -> Iterator[DepthUpdate]:
    for row in _read_event_dir(data_dir, symbol, "depth_update"):
        yield DepthUpdate(
            symbol=symbol.upper(),
            first_update_id=row["first_update_id"],
            final_update_id=row["final_update_id"],
            event_time_ms=row["ts_ms"],
            bids=_levels_from_rows(row["bids"]),
            asks=_levels_from_rows(row["asks"]),
        )


def replay_snapshots(data_dir: Path, symbol: str) -> Iterator[DepthSnapshot]:
    for row in _read_event_dir(data_dir, symbol, "snapshot"):
        yield DepthSnapshot(
            symbol=symbol.upper(),
            last_update_id=row["last_update_id"],
            bids=_levels_from_rows(row["bids"]),
            asks=_levels_from_rows(row["asks"]),
        )


def _event_ts(event: DepthUpdate | Trade) -> int:
    return event.event_time_ms if isinstance(event, DepthUpdate) else event.trade_time_ms


def replay_market_data(data_dir: Path, symbol: str) -> Iterator[DepthUpdate | Trade]:
    """Merges the depth-update and trade streams back into time order, the
    shape a backtester actually wants to consume events in."""
    # Annotated so mypy unifies heapq.merge's TypeVar as the union rather
    # than falling back to `object` (DepthUpdate and Trade share no other base).
    depth_events: Iterator[DepthUpdate | Trade] = replay_depth_updates(data_dir, symbol)
    trade_events: Iterator[DepthUpdate | Trade] = replay_trades(data_dir, symbol)
    yield from heapq.merge(depth_events, trade_events, key=_event_ts)
