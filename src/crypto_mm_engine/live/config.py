from __future__ import annotations

import os
from dataclasses import dataclass

from crypto_mm_engine.quoting.models import QuotingParams
from crypto_mm_engine.risk.models import RiskLimits


class MissingCredentialsError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LiveConfig:
    api_key: str
    api_secret: str
    symbol: str
    rest_base_url: str
    ws_base_url: str
    quoting: QuotingParams
    risk: RiskLimits


def _env_float(name: str, default: str) -> float:
    return float(os.environ.get(name, default))


def load_live_config() -> LiveConfig:
    """Reads Binance Testnet credentials and strategy/risk parameters from
    the environment (see .env.example). Credentials are required; every
    strategy/risk knob has a conservative default so this can run with just
    the two API variables set."""
    api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")
    if not api_key or not api_secret:
        raise MissingCredentialsError(
            "BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET must be set "
            "(see .env.example)"
        )

    quoting = QuotingParams(
        risk_aversion=_env_float("RISK_AVERSION", "0.1"),
        order_arrival_intensity=_env_float("ORDER_ARRIVAL_INTENSITY", "1.5"),
        volatility=_env_float("VOLATILITY", "0.001"),
        time_horizon_s=_env_float("TIME_HORIZON_S", "3600"),
        max_inventory=_env_float("MAX_INVENTORY", "0.05"),
        quote_size=_env_float("QUOTE_SIZE", "0.001"),
    )
    risk = RiskLimits(
        max_position=_env_float("MAX_POSITION", "0.05"),
        max_daily_loss=_env_float("MAX_DAILY_LOSS", "50"),
        max_stale_data_ms=int(_env_float("MAX_STALE_DATA_MS", "5000")),
        expected_fill_rate=(
            _env_float("MIN_FILL_RATE", "0.0"),
            _env_float("MAX_FILL_RATE", "1.0"),
        ),
        fill_rate_window=int(_env_float("FILL_RATE_WINDOW", "50")),
    )

    return LiveConfig(
        api_key=api_key,
        api_secret=api_secret,
        symbol=os.environ.get("SYMBOL", "btcusdt"),
        rest_base_url=os.environ.get("BINANCE_TESTNET_REST_URL", "https://testnet.binance.vision"),
        ws_base_url=os.environ.get("BINANCE_TESTNET_WS_URL", "wss://stream.testnet.binance.vision"),
        quoting=quoting,
        risk=risk,
    )
