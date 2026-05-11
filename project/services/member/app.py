from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from libs.common.auth import create_session
from libs.common.auth import ensure_role
from libs.common.auth import get_required_session_actor
from libs.common.database import get_member, get_point_account
from libs.common.observability import install_observability


class SessionLoginRequest(BaseModel):
    persona: str


app = FastAPI(title="member-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_observability(app, service_name="member-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "member-service",
        "bounded_context": "BC-MEMBER",
    }


def _get_member_or_404(member_id: str, tenant_id: str) -> dict[str, object]:
    member = get_member(member_id, tenant_id)
    if not member:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "MEMBER_NOT_FOUND",
                "message": "Member does not exist in the current tenant.",
            },
        )
    return member


@app.get("/member/v1/members/{member_id}")
def get_member_detail(
    member_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    return _get_member_or_404(member_id, x_tenant_id)


@app.get("/member/v1/members/{member_id}/points")
def get_member_points(
    member_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    _get_member_or_404(member_id, x_tenant_id)
    point_account = get_point_account(member_id)
    if not point_account:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "POINT_ACCOUNT_NOT_FOUND",
                "message": "Point account does not exist for this member.",
            },
        )
    return point_account


@app.post("/member/v1/session/login")
def login_session(payload: SessionLoginRequest) -> dict[str, object]:
    return create_session(payload.persona)


@app.get("/member/v1/session/me")
def get_session_me(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return actor.to_session_payload()


@app.post("/member/v1/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_session(response: Response) -> Response:
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@app.get("/member/v1/me")
def get_current_member_detail(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "customer")
    return _get_member_or_404(actor.member_id or actor.actor_id, actor.tenant_id)


@app.get("/member/v1/me/points")
def get_current_member_points(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "customer")
    member_id = actor.member_id or actor.actor_id
    _get_member_or_404(member_id, actor.tenant_id)
    point_account = get_point_account(member_id)
    if not point_account:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "POINT_ACCOUNT_NOT_FOUND",
                "message": "Point account does not exist for this member.",
            },
        )
    return point_account
