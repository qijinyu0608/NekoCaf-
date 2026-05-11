from fastapi import FastAPI, Header, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from libs.common.database import cancel_reservation_record
from libs.common.database import check_in_reservation_record
from libs.common.database import create_reservation_record
from libs.common.database import find_slot
from libs.common.database import get_member
from libs.common.database import get_reservation
from libs.common.database import list_available_slots
from libs.common.database import list_member_reservation_records
from libs.common.database import list_store_reservation_records
from libs.common.database import reset_database
from libs.common.observability import install_observability


class CreateReservationRequest(BaseModel):
    memberId: str
    storeId: str
    slotId: str
    partySize: int
    preferredTheme: str | None = None
    catInteractionMode: str | None = None


app = FastAPI(title="reservation-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_observability(app, service_name="reservation-service")


def reset_demo_state() -> None:
    reset_database()


def _find_slot(store_id: str, slot_id: str, tenant_id: str) -> dict[str, object]:
    slot = find_slot(tenant_id=tenant_id, store_id=store_id, slot_id=slot_id)
    if slot:
        return slot
    raise HTTPException(
        status_code=404,
        detail={
            "code": "SLOT_NOT_FOUND",
            "message": "Reservation slot does not exist in the current tenant.",
        },
    )


def _ensure_member_exists(member_id: str, tenant_id: str) -> None:
    member = get_member(member_id, tenant_id)
    if not member:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "MEMBER_NOT_FOUND",
                "message": "Member does not exist in the current tenant.",
            },
        )


def _build_reservation_detail(reservation: dict[str, object]) -> dict[str, object]:
    return {
        "reservationId": reservation["reservationId"],
        "status": reservation["status"],
        "tableCode": reservation["tableCode"],
        "storeId": reservation["storeId"],
        "slotId": reservation["slotId"],
        "partySize": reservation["partySize"],
        "checkedInAt": reservation["checkedInAt"],
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "reservation-service",
        "bounded_context": "BC-RESERVATION",
    }


@app.get("/reservation/v1/stores/{store_id}/slots")
def get_store_slots(
    store_id: str,
    date: str = Query(),
    party_size: int = Query(alias="partySize"),
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> list[dict[str, object]]:
    return list_available_slots(
        tenant_id=x_tenant_id,
        store_id=store_id,
        business_date=date,
        party_size=party_size,
    )


@app.post("/reservation/v1/reservations")
def create_reservation(
    payload: CreateReservationRequest,
    response: Response,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    _ensure_member_exists(payload.memberId, x_tenant_id)
    slot = _find_slot(payload.storeId, payload.slotId, x_tenant_id)

    if payload.partySize > slot["capacity"]:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SLOT_CONFLICT",
                "message": "Requested party size exceeds slot capacity.",
            },
        )

    reservation = create_reservation_record(
        tenant_id=x_tenant_id,
        member_id=payload.memberId,
        store_id=payload.storeId,
        slot=slot,
        party_size=payload.partySize,
        preferred_theme=payload.preferredTheme,
        cat_interaction_mode=payload.catInteractionMode,
    )
    response.status_code = status.HTTP_201_CREATED
    return _build_reservation_detail(reservation)


@app.get("/reservation/v1/reservations/{reservation_id}")
def get_reservation_detail(
    reservation_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    reservation = get_reservation(reservation_id, x_tenant_id)
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESERVATION_NOT_FOUND",
                "message": "Reservation does not exist in the current tenant.",
            },
        )
    return _build_reservation_detail(reservation)


@app.post("/reservation/v1/reservations/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    reservation = cancel_reservation_record(reservation_id, x_tenant_id)
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESERVATION_NOT_FOUND",
                "message": "Reservation does not exist in the current tenant.",
            },
        )
    return _build_reservation_detail(reservation)


@app.post("/reservation/v1/reservations/{reservation_id}/check-in")
def check_in_reservation(
    reservation_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    reservation = check_in_reservation_record(reservation_id, x_tenant_id)
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESERVATION_NOT_FOUND",
                "message": "Reservation does not exist in the current tenant.",
            },
        )
    return _build_reservation_detail(reservation)


@app.get("/reservation/v1/members/{member_id}/reservations")
def list_member_reservations(
    member_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
    status_filter: str | None = Query(default=None, alias="status"),
    business_date: str | None = Query(default=None, alias="businessDate"),
) -> list[dict[str, object]]:
    _ensure_member_exists(member_id, x_tenant_id)

    return list_member_reservation_records(
        tenant_id=x_tenant_id,
        member_id=member_id,
        status_filter=status_filter,
        business_date=business_date,
    )


@app.get("/staff/v1/stores/{store_id}/reservations")
def list_store_reservations_for_staff(
    store_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
    business_date: str = Query(alias="businessDate"),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[dict[str, object]]:
    return list_store_reservation_records(
        tenant_id=x_tenant_id,
        store_id=store_id,
        business_date=business_date,
        status_filter=status_filter,
    )
