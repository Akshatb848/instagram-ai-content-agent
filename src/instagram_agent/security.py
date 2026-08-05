import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any


class TokenError(ValueError):
    pass


def sign_payload(payload: dict[str, Any], secret: str) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    encoded = urlsafe_b64encode(body).rstrip(b"=")
    signature = hmac.new(secret.encode(), encoded, hashlib.sha256).digest()
    return f"{encoded.decode()}.{urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def verify_payload(
    token: str, secret: str, *, now: int | None = None, used_nonces: set[str] | None = None
) -> dict[str, Any]:
    try:
        encoded, supplied = token.split(".", 1)
        expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).digest()
        supplied_bytes = urlsafe_b64decode(supplied + "=" * (-len(supplied) % 4))
        if not hmac.compare_digest(expected, supplied_bytes):
            raise TokenError("Invalid signature")
        body = urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        payload: dict[str, Any] = json.loads(body)
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        if isinstance(exc, TokenError):
            raise
        raise TokenError("Malformed token") from exc
    current = int(time.time()) if now is None else now
    if not isinstance(payload.get("exp"), int) or payload["exp"] < current:
        raise TokenError("Expired token")
    nonce = payload.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        raise TokenError("Missing nonce")
    if used_nonces is not None:
        if nonce in used_nonces:
            raise TokenError("Replayed token")
        used_nonces.add(nonce)
    return payload
