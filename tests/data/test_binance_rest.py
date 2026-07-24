from crypto_mm_engine.data.binance_rest import parse_depth_snapshot
from crypto_mm_engine.data.models import DepthSnapshot, PriceLevel
from tests.data.fixtures import RAW_DEPTH_SNAPSHOT_PAYLOAD


def test_parse_depth_snapshot() -> None:
    snapshot = parse_depth_snapshot("BTCUSDT", RAW_DEPTH_SNAPSHOT_PAYLOAD)

    assert snapshot == DepthSnapshot(
        symbol="BTCUSDT",
        last_update_id=159,
        bids=(PriceLevel(30000.0, 1.0), PriceLevel(29900.0, 3.0)),
        asks=(PriceLevel(30001.0, 2.0), PriceLevel(30100.0, 5.0)),
    )
