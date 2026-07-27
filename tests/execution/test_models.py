from crypto_mm_engine.execution.models import Side, parse_execution_report


def test_parse_execution_report_returns_none_for_non_trade_events() -> None:
    data = {"e": "executionReport", "x": "NEW", "X": "NEW"}
    assert parse_execution_report(data) is None


def test_parse_execution_report_returns_none_for_unrelated_event_types() -> None:
    assert parse_execution_report({"e": "outboundAccountPosition"}) is None


def test_parse_execution_report_parses_a_buy_fill() -> None:
    data = {
        "e": "executionReport",
        "s": "BTCUSDT",
        "S": "BUY",
        "x": "TRADE",
        "X": "PARTIALLY_FILLED",
        "i": 4293153,
        "l": "0.50000000",
        "L": "30000.10000000",
        "n": "0.00050000",
        "T": 1499405658657,
    }

    fill = parse_execution_report(data)

    assert fill is not None
    assert fill.order_id == "4293153"
    assert fill.side is Side.BID
    assert fill.price == 30000.1
    assert fill.quantity == 0.5
    assert fill.fee == 0.0005
    assert fill.order_status == "PARTIALLY_FILLED"


def test_parse_execution_report_parses_a_sell_fill() -> None:
    data = {
        "e": "executionReport",
        "s": "BTCUSDT",
        "S": "SELL",
        "x": "TRADE",
        "X": "FILLED",
        "i": 1,
        "l": "1.0",
        "L": "100.0",
        "n": "0.001",
        "T": 0,
    }

    fill = parse_execution_report(data)

    assert fill is not None
    assert fill.side is Side.ASK
    assert fill.order_status == "FILLED"
