from __future__ import annotations

from typing import Any

import httpx

from crypto_mm_engine.data.config import MarketDataConfig
from crypto_mm_engine.data.models import DepthSnapshot, PriceLevel


def parse_depth_snapshot(symbol: str, payload: dict[str, Any]) -> DepthSnapshot:
    """Pulled out of fetch_depth_snapshot so tests can feed it a recorded
    JSON payload instead of hitting the network."""
    return DepthSnapshot(
        symbol=symbol,
        last_update_id=payload["lastUpdateId"],
        bids=tuple(PriceLevel(float(p), float(q)) for p, q in payload["bids"]),
        asks=tuple(PriceLevel(float(p), float(q)) for p, q in payload["asks"]),
    )


async def fetch_depth_snapshot(
    client: httpx.AsyncClient, config: MarketDataConfig, symbol: str
) -> DepthSnapshot:
    response = await client.get(config.depth_snapshot_url(symbol))
    response.raise_for_status()
    return parse_depth_snapshot(symbol, response.json())
