from crypto_mm_engine.execution.binance_user_stream import extract_event


def test_extract_event_returns_event_payload() -> None:
    payload = {
        "subscriptionId": 0,
        "event": {"e": "executionReport", "s": "BTCUSDT"},
    }

    assert extract_event(payload) == {"e": "executionReport", "s": "BTCUSDT"}


def test_extract_event_returns_none_for_subscribe_acknowledgement() -> None:
    payload = {"id": "abc-123", "status": 200, "result": {"subscriptionId": 0}}

    assert extract_event(payload) is None
