from dataclasses import dataclass

from fastapi import Header, HTTPException

from libs.common.database import DEFAULT_TENANT_ID


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
        store_id="store-shanghai-001",
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
    return {
        "sessionToken": token,
        **actor.to_session_payload(),
    }


def parse_session_token(authorization: str | None) -> SessionActor | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return SESSION_TOKENS.get(token)


def get_required_session_actor(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> SessionActor:
    actor = parse_session_token(authorization)
    if actor is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "SESSION_REQUIRED",
                "message": "A valid session token is required for this resource.",
            },
        )
    return actor


def resolve_tenant_id(
    *,
    authorization: str | None,
    x_tenant_id: str | None,
) -> str:
    actor = parse_session_token(authorization)
    if actor is not None:
        return actor.tenant_id
    if x_tenant_id:
        return x_tenant_id
    raise HTTPException(
        status_code=401,
        detail={
            "code": "TENANT_CONTEXT_REQUIRED",
            "message": "Provide a session token or tenant header for this resource.",
        },
    )


def ensure_role(actor: SessionActor, *roles: str) -> None:
    if actor.role not in roles:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )
