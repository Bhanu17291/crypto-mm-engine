from pathlib import Path

from crypto_mm_engine.data.persistence import ParquetWriter
from tests.data.fixtures import make_snapshot, make_trade, make_update


def test_flush_trades_writes_one_file_per_flush(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    writer.record_trade(make_trade(trade_id=1, trade_time_ms=100))
    writer.record_trade(make_trade(trade_id=2, trade_time_ms=200))
    writer.flush_trades()

    files = list((tmp_path / "btcusdt" / "trade").glob("*.parquet"))
    assert len(files) == 1
    assert files[0].name == "100-200.parquet"


def test_auto_flush_triggers_at_configured_threshold(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT", flush_every=2)
    writer.record_depth_update(make_update(1, 1, event_time_ms=10))
    writer.record_depth_update(make_update(2, 2, event_time_ms=20))  # should trigger flush

    files = list((tmp_path / "btcusdt" / "depth_update").glob("*.parquet"))
    assert len(files) == 1


def test_record_snapshot_writes_immediately(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    writer.record_snapshot(make_snapshot())

    files = list((tmp_path / "btcusdt" / "snapshot").glob("*.parquet"))
    assert len(files) == 1


def test_flush_with_no_buffered_rows_writes_nothing(tmp_path: Path) -> None:
    writer = ParquetWriter(tmp_path, "BTCUSDT")
    writer.flush_all()

    assert not (tmp_path / "btcusdt").exists()
