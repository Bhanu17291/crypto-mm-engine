from decimal import Decimal

from crypto_mm_engine.execution.binance_rest_adapter import round_to_step


def test_round_to_step_floors_price_to_tick_size() -> None:
    assert round_to_step(64879.34943479, Decimal("0.01")) == "64879.34"


def test_round_to_step_floors_quantity_to_lot_size() -> None:
    assert round_to_step(0.0016789, Decimal("0.00001")) == "0.00167"


def test_round_to_step_exact_multiple_is_unchanged() -> None:
    # Decimal division doesn't always preserve trailing zeros (100.50 can
    # come back as "100.5") - that's a cosmetic difference, not a wrong
    # value, so this checks numeric equality rather than exact string form.
    assert float(round_to_step(100.50, Decimal("0.01"))) == 100.50


def test_round_to_step_never_rounds_up() -> None:
    # Rounding up could quote a price/size larger than what the strategy
    # actually intended - flooring is the only safe direction.
    result = round_to_step(1.999999, Decimal("1"))
    assert result == "1"


def test_round_to_step_handles_zero_padded_tick_size_from_exchange_info() -> None:
    # Binance's exchangeInfo returns filter values zero-padded like
    # "0.01000000" regardless of the symbol's actual precision. This must
    # still floor to the 0.01 granularity, not to 8 decimal places - the
    # exact bug that let unrounded prices through to a live order.
    result = round_to_step(64865.35944146, Decimal("0.01000000"))
    assert float(result) == 64865.35
