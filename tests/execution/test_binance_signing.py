import hashlib
import hmac
from urllib.parse import urlencode

from crypto_mm_engine.execution.binance_signing import build_signed_params, sign_query


def test_sign_query_matches_independent_hmac_computation() -> None:
    # Recomputed independently (not via sign_query's own implementation)
    # so this actually checks the algorithm, not just that the function
    # returns whatever it returns.
    params = {"symbol": "LTCBTC", "side": "BUY", "timestamp": "1499827319559"}
    secret = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
    expected = hmac.new(secret.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()

    assert sign_query(params, secret) == expected


def test_sign_query_is_sensitive_to_params_and_secret() -> None:
    base = {"symbol": "LTCBTC", "timestamp": "1"}
    secret = "a-secret"

    assert sign_query(base, secret) != sign_query({**base, "symbol": "ETHBTC"}, secret)
    assert sign_query(base, secret) != sign_query(base, "a-different-secret")
    assert sign_query(base, secret) == sign_query(base, secret)  # deterministic


def test_build_signed_params_adds_timestamp_and_signature() -> None:
    result = build_signed_params({"symbol": "BTCUSDT"}, "secret", timestamp_ms=123)

    assert result["symbol"] == "BTCUSDT"
    assert result["timestamp"] == "123"
    assert len(result["signature"]) == 64  # sha256 hex digest length


def test_build_signed_params_signature_excludes_itself() -> None:
    # The signature must be computed over params+timestamp only - if it
    # accidentally included itself, this would be circular/inconsistent.
    result = build_signed_params({"symbol": "BTCUSDT"}, "secret", timestamp_ms=123)
    expected = sign_query({"symbol": "BTCUSDT", "timestamp": "123"}, "secret")

    assert result["signature"] == expected
