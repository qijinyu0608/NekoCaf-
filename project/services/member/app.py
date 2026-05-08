from fastapi import FastAPI, Header, HTTPException

from libs.common.demo_data import MEMBERS, POINT_ACCOUNTS
from libs.common.observability import install_observability


app = FastAPI(title="member-service")
install_observability(app, service_name="member-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "member-service",
        "bounded_context": "BC-MEMBER",
    }


def _get_member_or_404(member_id: str, tenant_id: str) -> dict[str, object]:
    member = MEMBERS.get(member_id)
    if not member or member["tenantId"] != tenant_id:
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
    return POINT_ACCOUNTS[member_id]
