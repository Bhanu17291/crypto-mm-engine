from crypto_mm_engine.backtest.fill_simulator import FillSimulator
from crypto_mm_engine.backtest.models import FeeSchedule
from crypto_mm_engine.data.models import DepthSnapshot, PriceLevel, Trade
from crypto_mm_engine.data.order_book import OrderBook
from crypto_mm_engine.execution.backtest_adapter import BacktestExecutionAdapter
from crypto_mm_engine.execution.models import Side


def test_place_order_seeds_queue_ahead_from_existing_book_depth() -> None:
    book = OrderBook("BTCUSDT")
    book.apply_snapshot(
        DepthSnapshot(
            symbol="BTCUSDT",
            last_update_id=1,
            bids=(PriceLevel(100.0, 3.0),),
            asks=(PriceLevel(101.0, 2.0),),
        )
    )
    fill_sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    adapter = BacktestExecutionAdapter(fill_sim, book)

    order_id = adapter.place_order(Side.BID, price=100.0, size=1.0)

    # 3 units already resting ahead of us per the snapshot; a 3-unit trade
    # should drain that queue without reaching our order yet.
    fills = fill_sim.on_trade(
        Trade(
            symbol="BTCUSDT",
            trade_id=1,
            price=100.0,
            quantity=3.0,
            trade_time_ms=0,
            is_buyer_maker=True,
        ),
        mid_price=100.5,
    )
    assert fills == []
    assert fill_sim.has_order(int(order_id))

    fills = fill_sim.on_trade(
        Trade(
            symbol="BTCUSDT",
            trade_id=2,
            price=100.0,
            quantity=1.0,
            trade_time_ms=0,
            is_buyer_maker=True,
        ),
        mid_price=100.5,
    )
    assert len(fills) == 1


def test_place_order_at_empty_price_level_fills_immediately() -> None:
    book = OrderBook("BTCUSDT")
    fill_sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    adapter = BacktestExecutionAdapter(fill_sim, book)

    order_id = adapter.place_order(Side.ASK, price=101.0, size=1.0)

    fills = fill_sim.on_trade(
        Trade(
            symbol="BTCUSDT",
            trade_id=1,
            price=101.0,
            quantity=1.0,
            trade_time_ms=0,
            is_buyer_maker=False,
        ),
        mid_price=100.5,
    )
    assert len(fills) == 1
    assert fills[0].order_id == int(order_id)


def test_cancel_order_forwards_to_fill_simulator() -> None:
    book = OrderBook("BTCUSDT")
    fill_sim = FillSimulator(FeeSchedule(maker_fee_rate=0.0))
    adapter = BacktestExecutionAdapter(fill_sim, book)
    order_id = adapter.place_order(Side.BID, price=100.0, size=1.0)

    adapter.cancel_order(order_id)

    assert not fill_sim.has_order(int(order_id))
