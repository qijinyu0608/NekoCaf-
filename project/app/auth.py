from dataclasses import dataclass
from hmac import compare_digest

from fastapi import Cookie, HTTPException


COOKIE_NAME = "nekocafe_session"
DEFAULT_TENANT_ID = "tenant-nekocafe"


@dataclass(frozen=True)
class SessionActor:
    actor_id: str
    tenant_id: str
    display_name: str
    role: str
    permissions: tuple[str, ...]
    member_id: str | None = None
    store_id: str | None = None

    def to_session_payload(self) -> dict[str, object]:
        scope = {
            "memberId": self.member_id,
            "storeId": self.store_id,
        }
        return {
            "sessionStatus": "authenticated",
            "tenantId": self.tenant_id,
            "actorId": self.actor_id,
            "displayName": self.display_name,
            "role": self.role,
            "memberId": self.member_id,
            "storeId": self.store_id,
            "permissions": list(self.permissions),
            "scope": scope,
        }


PERSONAS = {
    "customer": SessionActor(
        actor_id="member-1001",
        tenant_id=DEFAULT_TENANT_ID,
        display_name="Momo",
        role="customer",
        permissions=(
            "member.profile.read.self",
            "member.profile.update.self",
            "member.points.read.self",
            "reservation.create.self",
            "reservation.read.self",
            "reservation.cancel.self",
            "cat.read.self",
            "recommendation.read.self",
        ),
        member_id="member-1001",
    ),
    "staff": SessionActor(
        actor_id="staff-sh-001",
        tenant_id=DEFAULT_TENANT_ID,
        display_name="Aki",
        role="staff",
        permissions=(
            "staff.reservations.read",
            "staff.reservations.check_in",
        ),
        store_id="store-shanghai-jingan",
    ),
    "admin": SessionActor(
        actor_id="admin-001",
        tenant_id=DEFAULT_TENANT_ID,
        display_name="Rin",
        role="admin",
        permissions=(
            "permissions.manage",
            "store.operations.manage",
            "staff.reservations.read",
        ),
    ),
}

SESSION_TOKENS = {
    "mock-customer-token": PERSONAS["customer"],
    "mock-staff-token": PERSONAS["staff"],
    "mock-admin-token": PERSONAS["admin"],
}

PERSONA_TOKENS = {
    "customer": "mock-customer-token",
    "staff": "mock-staff-token",
    "admin": "mock-admin-token",
}

AUTH_CREDENTIALS = {
    "customer": {
        "identifier": "13800001001",
        "verificationCode": "260520",
    },
    "staff": {
        "identifier": "staff-sh-001",
        "accessCode": "SH-NEKO-2026",
    },
    "admin": {
        "identifier": "admin-001",
        "accessCode": "ADMIN-NEKO-2026",
    },
}


def _normalize(value: str | None) -> str:
    return (value or "").strip()


def _require_matching_credential(
    persona: str,
    *,
    identifier: str | None,
    access_code: str | None,
    verification_code: str | None,
) -> None:
    expected = AUTH_CREDENTIALS.get(persona)
    submitted_identifier = _normalize(identifier)
    if expected is None or not compare_digest(submitted_identifier, expected["identifier"]):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTHENTICATION_FAILED",
                "message": "身份信息或访问码不正确，请重新输入。",
            },
        )

    secret_field = "verificationCode" if persona == "customer" else "accessCode"
    submitted_secret = _normalize(verification_code if persona == "customer" else access_code)
    if not compare_digest(submitted_secret, expected[secret_field]):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTHENTICATION_FAILED",
                "message": "身份信息或访问码不正确，请重新输入。",
            },
        )


def create_session(
    persona: str,
    *,
    identifier: str | None = None,
    access_code: str | None = None,
    verification_code: str | None = None,
) -> dict[str, object]:
    actor = PERSONAS.get(persona)
    token = PERSONA_TOKENS.get(persona)
    if actor is None or token is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PERSONA_NOT_FOUND",
                "message": "Requested persona does not exist in the mock session catalog.",
            },
        )
    _require_matching_credential(
        persona,
        identifier=identifier,
        access_code=access_code,
        verification_code=verification_code,
    )
    return {"sessionToken": token, **actor.to_session_payload()}


def parse_session_token(token: str | None) -> SessionActor | None:
    if not token:
        return None
    return SESSION_TOKENS.get(token)


def get_optional_session_actor(
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> SessionActor | None:
    return parse_session_token(session_token)


def get_required_session_actor(
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> SessionActor:
    actor = parse_session_token(session_token)
    if actor is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "SESSION_REQUIRED",
                "message": "A valid session is required for this resource.",
            },
        )
    return actor


def ensure_role(actor: SessionActor, *roles: str) -> None:
    if actor.role not in roles:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )


def ensure_permission(actor: SessionActor, permission: str) -> None:
    if permission not in actor.permissions:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )


def list_permission_profiles() -> list[dict[str, object]]:
    return [
        {
            "persona": persona,
            "actorId": actor.actor_id,
            "displayName": actor.display_name,
            "role": actor.role,
            "permissions": list(actor.permissions),
            "scope": {
                "memberId": actor.member_id,
                "storeId": actor.store_id,
            },
        }
        for persona, actor in PERSONAS.items()
    ]
