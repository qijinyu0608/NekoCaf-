from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from libs.common.database import get_member, get_point_account
from libs.common.observability import install_observability


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
