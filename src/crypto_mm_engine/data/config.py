from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ReconnectPolicy:
    initial_delay_s: float = 1.0
    max_delay_s: float = 60.0
    multiplier: float = 2.0


@dataclass(frozen=True, slots=True)
class MarketDataConfig:
    symbols: tuple[str, ...]
    ws_base_url: str = "wss://stream.binance.com:9443"
    rest_base_url: str = "https://api.binance.com"
    snapshot_depth: int = 1000
    data_dir: Path = field(default_factory=lambda: Path("data/market_data"))
    reconnect: ReconnectPolicy = field(default_factory=ReconnectPolicy)

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("MarketDataConfig requires at least one symbol")
        normalized = tuple(s.lower() for s in self.symbols)
        object.__setattr__(self, "symbols", normalized)

    @property
    def combined_stream_url(self) -> str:
        streams = "/".join(f"{s}@depth@100ms/{s}@trade" for s in self.symbols)
        return f"{self.ws_base_url}/stream?streams={streams}"

    def depth_snapshot_url(self, symbol: str) -> str:
        return (
            f"{self.rest_base_url}/api/v3/depth"
            f"?symbol={symbol.upper()}&limit={self.snapshot_depth}"
        )
