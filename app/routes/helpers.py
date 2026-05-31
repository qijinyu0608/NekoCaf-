from fastapi import HTTPException

from app.auth import ensure_permission
from app.core.constants import DEFAULT_MEMBER_ID
from app.repositories.reservations import get_reservation_detail


def get_scoped_customer_reservation(actor, reservation_id: str) -> dict[str, object]:
    ensure_permission(actor, "reservation.read.self")
    try:
        reservation = get_reservation_detail(reservation_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "RESERVATION_NOT_FOUND",
                "message": "Reservation does not exist.",
            },
        ) from exc
    if reservation["memberId"] != (actor.member_id or DEFAULT_MEMBER_ID):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )
    return reservation
