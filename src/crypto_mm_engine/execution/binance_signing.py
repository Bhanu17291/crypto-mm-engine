from __future__ import annotations

import hashlib
import hmac
from urllib.parse import urlencode


def sign_query(params: dict[str, str], api_secret: str) -> str:
    """Binance's REST signing scheme: HMAC-SHA256 over the exact query
    string that gets sent, hex-encoded. Pulled out as a pure function so
    it's testable against Binance's documented example without a live
    connection or real credentials."""
    query = urlencode(params)
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
