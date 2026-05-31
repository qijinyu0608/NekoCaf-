from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.core.constants import DEFAULT_DATE
from app.db.schema import initialize_database
from app.repositories.slots import list_available_slots
from libs.common.observability import install_observability


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(title="reservation-service", lifespan=lifespan)
install_observability(app, service_name="reservation-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "reservation-service",
        "bounded_context": "BC-RESERVATION",
    }


@app.get("/stores/{store_id}/slots")
def available_slots(
    store_id: str,
    date: str = Query(default=DEFAULT_DATE),
    party_size: int = Query(default=2, alias="partySize", ge=1),
) -> list[dict[str, object]]:
    return list_available_slots(store_id, date, party_size)
