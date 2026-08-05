from dataclasses import dataclass

from instagram_agent.security import verify_payload


@dataclass(frozen=True)
class ApprovalDecision:
    package_id: int
    decision: str
    user_id: str


def authorize_callback(
    token: str,
    secret: str,
    acting_user: str,
    allowed_users: set[str],
    used_nonces: set[str],
    now: int | None = None,
) -> ApprovalDecision:
    if acting_user not in allowed_users:
        raise PermissionError("Telegram user is not authorised")
    payload = verify_payload(token, secret, now=now, used_nonces=used_nonces)
    if payload.get("user_id") != acting_user:
        raise PermissionError("Callback user mismatch")
    decision = payload.get("decision")
    if decision not in {"approve", "reject", "regenerate", "sources", "cancel"}:
        raise ValueError("Unsupported approval decision")
    return ApprovalDecision(int(payload["package_id"]), decision, acting_user)
