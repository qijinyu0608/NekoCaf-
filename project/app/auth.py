from dataclasses import dataclass

from fastapi import Cookie, HTTPException


COOKIE_NAME = "nekocafe_session"
DEFAULT_TENANT_ID = "tenant-nekocafe"


@dataclass(frozen=True)
class SessionActor:
    actor_id: str
    tenant_id: str
    display_name: str
    role: str
    member_id: str | None = None
    store_id: str | None = None

    def to_session_payload(self) -> dict[str, object]:
        return {
            "sessionStatus": "authenticated",
            "tenantId": self.tenant_id,
            "actorId": self.actor_id,
            "displayName": self.display_name,
            "role": self.role,
            "memberId": self.member_id,
            "storeId": self.store_id,
        }


PERSONAS = {
    "customer": SessionActor(
        actor_id="member-1001",
        tenant_id=DEFAULT_TENANT_ID,
        display_name="Momo",
        role="customer",
        member_id="member-1001",
    ),
    "staff": SessionActor(
        actor_id="staff-sh-001",
        tenant_id=DEFAULT_TENANT_ID,
        display_name="Aki",
        role="staff",
        store_id="store-shanghai-jingan",
    ),
}

SESSION_TOKENS = {
    "mock-customer-token": PERSONAS["customer"],
    "mock-staff-token": PERSONAS["staff"],
}

PERSONA_TOKENS = {
    "customer": "mock-customer-token",
    "staff": "mock-staff-token",
}


def create_session(persona: str) -> dict[str, object]:
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
