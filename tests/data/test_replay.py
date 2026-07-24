from pathlib import Path

from crypto_mm_engine.data.models import DepthUpdate, Trade
from crypto_mm_engine.data.persistence import ParquetWriter
from crypto_mm_engine.data.replay import (
    replay_depth_updates,
    replay_market_data,
    replay_snapshots,
    replay_trades,
)
from tests.data.fixtures import make_snapshot, make_trade, make_update


def test_replay_trades_round_trips_through_parquet(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    original = [make_trade(trade_id=i, trade_time_ms=100 + i) for i in range(3)]
    for trade in original:
        writer.record_trade(trade)
    writer.flush_trades()

    replayed = list(replay_trades(tmp_path, "BTCUSDT"))
    assert replayed == original


def test_replay_depth_updates_round_trips_through_parquet(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    original = [make_update(i, i, event_time_ms=100 + i) for i in range(3)]
    for update in original:
        writer.record_depth_update(update)
    writer.flush_depth_updates()

    replayed = list(replay_depth_updates(tmp_path, "BTCUSDT"))
    assert replayed == original


def test_replay_snapshots_round_trips_through_parquet(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    writer.record_snapshot(make_snapshot(last_update_id=42))

    replayed = list(replay_snapshots(tmp_path, "BTCUSDT"))
    assert len(replayed) == 1
    assert replayed[0].last_update_id == 42


def test_replay_missing_symbol_returns_empty(tmp_path: Path) -> None:
    assert list(replay_trades(tmp_path, "ETHUSDT")) == []


def test_replay_market_data_merges_depth_and_trades_in_time_order(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    writer.record_depth_update(make_update(1, 1, event_time_ms=100))
    writer.record_trade(make_trade(trade_id=1, trade_time_ms=150))
    writer.record_depth_update(make_update(2, 2, event_time_ms=200))
    writer.flush_all()

    merged = list(replay_market_data(tmp_path, "BTCUSDT"))
    timestamps = [
        event.event_time_ms if isinstance(event, DepthUpdate) else event.trade_time_ms
        for event in merged
    ]

    assert timestamps == [100, 150, 200]
    assert isinstance(merged[0], DepthUpdate)
    assert isinstance(merged[1], Trade)
    assert isinstance(merged[2], DepthUpdate)
