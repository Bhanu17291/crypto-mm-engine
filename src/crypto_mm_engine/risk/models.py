from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RiskLimits:
    max_position: float
    # positive number; realized+unrealized PnL at or below -max_daily_loss trips the kill switch
    max_daily_loss: float
    # quotes are withheld once market data is older than this
    max_stale_data_ms: int
    # (low, high) acceptable fraction of quote cycles that get filled
    expected_fill_rate: tuple[float, float]
    # number of recent quote cycles the fill-rate check looks back over
    fill_rate_window: int = 100

    def __post_init__(self) -> None:
        if self.max_position <= 0:
            raise ValueError("max_position must be positive")
        if self.max_daily_loss <= 0:
            raise ValueError("max_daily_loss must be positive")
        if self.max_stale_data_ms <= 0:
            raise ValueError("max_stale_data_ms must be positive")
        low, high = self.expected_fill_rate
        if not (0.0 <= low <= high <= 1.0):
            raise ValueError("expected_fill_rate must be a (low, high) pair within [0, 1]")
        if self.fill_rate_window <= 0:
            raise ValueError("fill_rate_window must be positive")
