from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.schema import initialize_database
from app.repositories.members import get_member, get_point_account
from libs.common.observability import install_observability


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(title="member-service", lifespan=lifespan)
install_observability(app, service_name="member-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "member-service",
        "bounded_context": "BC-MEMBER",
    }


@app.get("/members/{member_id}")
def member_detail(member_id: str) -> dict[str, object]:
    return get_member(member_id)


@app.get("/members/{member_id}/points")
def member_points(member_id: str) -> dict[str, object]:
    return get_point_account(member_id)
