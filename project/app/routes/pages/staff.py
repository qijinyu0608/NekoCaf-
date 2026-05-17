from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from app.auth import get_optional_session_actor
from app.core.constants import DEFAULT_DATE
from app.presenters import base_template_context, decorate_reservation
from app.repositories.reservations import get_staff_reservation_stats, list_staff_reservations
from app.repositories.stores import list_stores
from app.web import templates


router = APIRouter()


@router.get("/staff", response_class=HTMLResponse)
def staff_console(
    request: Request,
    business_date: str = Query(default=DEFAULT_DATE, alias="businessDate"),
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    stores = list_stores()
    active_store_id = actor.store_id if actor and "staff.reservations.read" in actor.permissions and actor.store_id else stores[0]["storeId"]
    reservations = (
        [
            decorate_reservation(reservation)
            for reservation in list_staff_reservations(active_store_id, business_date, status_filter)
        ]
        if actor and "staff.reservations.read" in actor.permissions
        else []
    )
    stats = get_staff_reservation_stats(active_store_id, business_date) if actor and "staff.reservations.read" in actor.permissions else None
    return templates.TemplateResponse(
        request,
        "staff.html",
        {
            **base_template_context(request, actor),
            "page": "staff",
            "stores": stores,
            "activeStoreId": active_store_id,
            "businessDate": business_date,
            "statusFilter": status_filter or "",
            "reservations": reservations,
            "stats": stats,
        },
    )
