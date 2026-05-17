from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import ensure_permission, get_required_session_actor
from app.core.errors import ReservationStateError
from app.presenters import reservation_state_message
from app.repositories.reservations import list_staff_reservations
from app.services.booking import check_in_reservation


router = APIRouter()


@router.get("/api/staff/reservations")
def get_staff_reservations(
    store_id: str = Query(alias="storeId"),
    business_date: str = Query(alias="businessDate"),
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "staff.reservations.read")
    if actor.store_id != store_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )
    return list_staff_reservations(store_id, business_date, status_filter)


@router.post("/api/staff/reservations/{reservation_id}/check-in")
def check_in_staff_reservation(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "staff.reservations.check_in")
    try:
        return check_in_reservation(actor.store_id or "", reservation_id)
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
                "message": reservation_state_message(exc.current_status, "check-in"),
            },
        ) from exc
