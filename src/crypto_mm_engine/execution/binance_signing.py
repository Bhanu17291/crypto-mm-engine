from __future__ import annotations

import hashlib
import hmac
from urllib.parse import urlencode


def _sorted_query_string(params: dict[str, str]) -> str:
    return urlencode(sorted(params.items()))


def sign_query(params: dict[str, str], api_secret: str) -> str:
    """Binance's signing scheme: HMAC-SHA256 over the params as an
    alphabetically-sorted query string, hex-encoded. Required by the
    WebSocket API; harmless for REST as long as whatever gets sent matches
    this exact string byte-for-byte (see build_signed_query_string - a
    second encoder re-serializing the same dict in a different order or
    escaping is exactly what breaks that).
    """
    query = _sorted_query_string(params)
    return hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()


def build_signed_params(
    params: dict[str, str], api_secret: str, timestamp_ms: int
) -> dict[str, str]:
    """For callers that need a dict (e.g. a JSON payload, where key order
    is irrelevant). timestamp must be part of what gets signed; signature
    itself can't be, so it's computed after and appended last."""
    payload = dict(params)
    payload["timestamp"] = str(timestamp_ms)
    payload["signature"] = sign_query(payload, api_secret)
    return payload


def build_signed_query_string(params: dict[str, str], api_secret: str, timestamp_ms: int) -> str:
    """For callers that send a literal query string (REST requests), where
    the sent bytes must exactly match what was signed. Returns the
    complete, ready-to-send string (signature included) built from a
    single encoding pass, so there's no second serializer in the request
    path that could produce different order or escaping than what was
    signed.
    """
    payload = dict(params)
    payload["timestamp"] = str(timestamp_ms)
    query = _sorted_query_string(payload)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"
