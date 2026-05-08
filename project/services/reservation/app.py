from copy import deepcopy

from fastapi import FastAPI, Header, HTTPException, Query, Response, status
from pydantic import BaseModel

from libs.common.demo_data import MEMBERS, STORE_SLOTS


class CreateReservationRequest(BaseModel):
    memberId: str
    storeId: str
    slotId: str
    partySize: int
    preferredTheme: str | None = None
    catInteractionMode: str | None = None


_INITIAL_STATE = {
    "reservations": {},
    "next_reservation_id": 1,
}

_STATE = deepcopy(_INITIAL_STATE)

app = FastAPI(title="reservation-service")


def reset_demo_state() -> None:
    _STATE["reservations"] = {}
    _STATE["next_reservation_id"] = 1


def _find_slot(store_id: str, slot_id: str, tenant_id: str) -> dict[str, object]:
    for slot in STORE_SLOTS.get(store_id, []):
        if slot["slotId"] == slot_id and slot["tenantId"] == tenant_id:
            return slot
    raise HTTPException(
        status_code=404,
        detail={
            "code": "SLOT_NOT_FOUND",
            "message": "Reservation slot does not exist in the current tenant.",
        },
    )


def _ensure_member_exists(member_id: str, tenant_id: str) -> None:
    member = MEMBERS.get(member_id)
    if not member or member["tenantId"] != tenant_id:
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
    return [
        {
            "slotId": slot["slotId"],
            "startAt": slot["startAt"],
            "capacity": slot["capacity"],
            "theme": slot["theme"],
        }
        for slot in STORE_SLOTS.get(store_id, [])
        if slot["tenantId"] == x_tenant_id
        and slot["startAt"].startswith(date)
        and slot["capacity"] >= party_size
    ]


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

    reservation_id = f"res-{_STATE['next_reservation_id']:04d}"
    _STATE["next_reservation_id"] += 1
    reservation = {
        "reservationId": reservation_id,
        "tenantId": x_tenant_id,
        "memberId": payload.memberId,
        "status": "BOOKED",
        "tableCode": "T1",
        "storeId": payload.storeId,
        "slotId": payload.slotId,
        "slotStartAt": slot["startAt"],
        "partySize": payload.partySize,
        "checkedInAt": None,
    }
    _STATE["reservations"][reservation_id] = reservation
    response.status_code = status.HTTP_201_CREATED
    return _build_reservation_detail(reservation)


@app.get("/reservation/v1/reservations/{reservation_id}")
def get_reservation_detail(
    reservation_id: str,
    x_tenant_id: str = Header(alias="X-Tenant-Id"),
) -> dict[str, object]:
    reservation = _STATE["reservations"].get(reservation_id)
    if not reservation or reservation["tenantId"] != x_tenant_id:
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

    items = []
    for reservation in _STATE["reservations"].values():
        if reservation["tenantId"] != x_tenant_id or reservation["memberId"] != member_id:
            continue
        if status_filter and reservation["status"] != status_filter:
            continue
        if business_date and not str(reservation["slotStartAt"]).startswith(business_date):
            continue
        items.append(
            {
                "reservationId": reservation["reservationId"],
                "status": reservation["status"],
                "storeId": reservation["storeId"],
                "slotStartAt": reservation["slotStartAt"],
                "partySize": reservation["partySize"],
            }
        )
    return items
