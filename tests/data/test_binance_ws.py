import json

from crypto_mm_engine.data.binance_ws import (
    next_backoff_delay,
    parse_combined_stream_message,
    parse_depth_update,
    parse_trade,
)
from crypto_mm_engine.data.config import ReconnectPolicy
from crypto_mm_engine.data.models import DepthUpdate, PriceLevel, Trade
from tests.data.fixtures import RAW_DEPTH_UPDATE_MESSAGE, RAW_TRADE_MESSAGE


def test_parse_depth_update() -> None:
    update = parse_depth_update(RAW_DEPTH_UPDATE_MESSAGE["data"])

    assert update == DepthUpdate(
        symbol="BTCUSDT",
        first_update_id=157,
        final_update_id=160,
        event_time_ms=1700000000000,
        bids=(PriceLevel(30000.0, 1.5), PriceLevel(29999.5, 0.0)),
        asks=(PriceLevel(30001.0, 2.0),),
    )


def test_parse_trade() -> None:
    trade = parse_trade(RAW_TRADE_MESSAGE["data"])

    assert trade == Trade(
        symbol="BTCUSDT",
        trade_id=5001,
        price=30000.5,
        quantity=0.01,
        trade_time_ms=1700000000050,
        is_buyer_maker=True,
    )


def test_parse_combined_stream_message_dispatches_by_event_type() -> None:
    depth_event = parse_combined_stream_message(json.dumps(RAW_DEPTH_UPDATE_MESSAGE))
    trade_event = parse_combined_stream_message(json.dumps(RAW_TRADE_MESSAGE))

    assert isinstance(depth_event, DepthUpdate)
    assert isinstance(trade_event, Trade)


def test_parse_combined_stream_message_unknown_event_returns_none() -> None:
    envelope = {"stream": "btcusdt@bookTicker", "data": {"e": "bookTicker"}}
    assert parse_combined_stream_message(json.dumps(envelope)) is None


def test_backoff_delay_grows_geometrically_and_caps() -> None:
    policy = ReconnectPolicy(initial_delay_s=1.0, max_delay_s=10.0, multiplier=2.0)

    assert next_backoff_delay(0, policy) == 1.0
    assert next_backoff_delay(1, policy) == 2.0
    assert next_backoff_delay(2, policy) == 4.0
    assert next_backoff_delay(10, policy) == 10.0  # capped
