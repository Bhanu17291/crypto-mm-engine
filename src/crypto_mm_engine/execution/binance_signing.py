from __future__ import annotations

import hashlib
import hmac
from urllib.parse import urlencode


def sign_query(params: dict[str, str], api_secret: str) -> str:
    """Binance's signing scheme: HMAC-SHA256 over the params as an
    alphabetically-sorted query string, hex-encoded. The WebSocket API
    requires sorted params; sorting doesn't break REST signing either
    (REST just needs the signed string to match what's actually sent, and
    we always send whatever we signed), so this is used for both.
    """
    query = urlencode(sorted(params.items()))
    return hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()


def build_signed_params(
    params: dict[str, str], api_secret: str, timestamp_ms: int
) -> dict[str, str]:
    """timestamp must be part of what gets signed; signature itself can't
    be, so it's computed after and appended last."""
    payload = dict(params)
    payload["timestamp"] = str(timestamp_ms)
    payload["signature"] = sign_query(payload, api_secret)
    return payload
