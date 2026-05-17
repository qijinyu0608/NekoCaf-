from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth import ensure_permission, get_required_session_actor
from app.core.constants import DEFAULT_MEMBER_ID
from app.core.errors import InvalidReservationRequestError, ReservationStateError, StoreUnavailableError
from app.presenters import reservation_state_message
from app.repositories.reservations import list_member_reservations
from app.routes.helpers import get_scoped_customer_reservation
from app.services.booking import cancel_reservation, create_reservation


router = APIRouter()


class CreateReservationRequest(BaseModel):
    storeId: str
    slotId: str
    partySize: int = Field(gt=0)


@router.post("/api/reservations", status_code=status.HTTP_201_CREATED)
def create_customer_reservation(
    payload: CreateReservationRequest,
    actor=Depends(get_required_session_actor),
) -> dict[str, object]:
    ensure_permission(actor, "reservation.create.self")
    try:
        return create_reservation(actor.member_id or DEFAULT_MEMBER_ID, payload.storeId, payload.slotId, payload.partySize)
    except InvalidReservationRequestError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_PARTY_SIZE",
                "message": "预约人数必须大于 0，请重新选择人数。",
            },
        ) from exc
    except StoreUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "STORE_NOT_BOOKABLE",
                "message": "门店当前暂停预约，请选择其他门店或稍后再试。",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SLOT_NOT_FOUND",
                "message": "Reservation slot does not exist.",
            },
        ) from exc
    except OverflowError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SLOT_CONFLICT",
                "message": "当前时段剩余容量不足，请选择其他时段或减少人数。",
            },
        ) from exc


@router.get("/api/reservations/me")
def get_my_reservations(
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "reservation.read.self")
    return list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID, status_filter)


@router.get("/api/reservations/{reservation_id}")
def get_my_reservation_detail(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return get_scoped_customer_reservation(actor, reservation_id)


@router.post("/api/reservations/{reservation_id}/cancel")
def cancel_my_reservation(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "reservation.cancel.self")
    try:
        return cancel_reservation(actor.member_id or DEFAULT_MEMBER_ID, reservation_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESERVATION_NOT_FOUND",
                "message": "Reservation does not exist.",
            },
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        ) from exc
    except ReservationStateError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RESERVATION_STATE_CONFLICT",
                "message": reservation_state_message(exc.current_status, "cancel"),
            },
        ) from exc
