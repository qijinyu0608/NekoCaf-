from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.auth import COOKIE_NAME, create_session, ensure_role, get_optional_session_actor, get_required_session_actor
from app.data import DEFAULT_DATE
from app.data import DEFAULT_MEMBER_ID
from app.data import cancel_reservation
from app.data import check_in_reservation
from app.data import create_reservation
from app.data import get_database_path
from app.data import get_member
from app.data import get_point_account
from app.data import list_available_slots
from app.data import list_member_cats
from app.data import list_member_recommendations
from app.data import list_member_reservations
from app.data import list_staff_reservations
from app.data import list_stores
from app.data import reset_demo_state
from libs.common.observability import install_observability


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class SessionLoginRequest(BaseModel):
    persona: str


class CreateReservationRequest(BaseModel):
    storeId: str
    slotId: str
    partySize: int


app = FastAPI(title="NekoCafe")
install_observability(app, service_name="nekocafe-web")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "nekocafe-web",
        "application": "full-stack-monolith",
    }


def _preview_context(store_id: str | None = None) -> dict[str, object]:
    stores = list_stores()
    store_ids = {store["storeId"] for store in stores}
    default_store_id = store_id if store_id in store_ids else stores[0]["storeId"]
    recommendations = list_member_recommendations(DEFAULT_MEMBER_ID)
    selected_recommendation = next(
        (recommendation for recommendation in recommendations if recommendation["storeId"] == default_store_id),
        recommendations[0] if recommendations else None,
    )
    return {
        "stores": stores,
        "defaultStoreId": default_store_id,
        "defaultDate": DEFAULT_DATE,
        "defaultPartySize": 2,
        "member": get_member(DEFAULT_MEMBER_ID),
        "points": get_point_account(DEFAULT_MEMBER_ID),
        "cats": list_member_cats(DEFAULT_MEMBER_ID),
        "recommendations": recommendations,
        "selectedRecommendation": selected_recommendation,
        "slots": list_available_slots(default_store_id, DEFAULT_DATE, 2),
    }


def _base_template_context(request: Request, actor=Depends(get_optional_session_actor)) -> dict[str, object]:
    session = actor.to_session_payload() if actor else {"sessionStatus": "anonymous"}
    return {
        "request": request,
        "session": session,
        "actor": actor,
    }


def _status_label(status_value: str) -> str:
    return {
        "BOOKED": "已预约",
        "CHECKED_IN": "已到店",
        "CANCELLED": "已取消",
    }.get(status_value, status_value)


def _member_reservation_summary(reservations: list[dict[str, object]]) -> dict[str, object]:
    booked = [reservation for reservation in reservations if reservation["status"] == "BOOKED"]
    checked_in = [reservation for reservation in reservations if reservation["status"] == "CHECKED_IN"]
    cancelled = [reservation for reservation in reservations if reservation["status"] == "CANCELLED"]
    next_visit = booked[0] if booked else None
    return {
        "nextVisit": next_visit,
        "bookedCount": len(booked),
        "checkedInCount": len(checked_in),
        "cancelledCount": len(cancelled),
    }


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    preview = _preview_context(store_id)
    latest_reservation = None
    if actor and actor.role == "customer":
        reservations = list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID)
        latest_reservation = reservations[0] if reservations else None
    bootstrap = {
        "session": actor.to_session_payload() if actor else {"sessionStatus": "anonymous"},
        "defaultStoreId": preview["defaultStoreId"],
        "defaultDate": preview["defaultDate"],
        "defaultPartySize": preview["defaultPartySize"],
        "stores": preview["stores"],
        "recommendations": preview["recommendations"],
    }
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            **_base_template_context(request, actor),
            **preview,
            "page": "home",
            "bootstrap": bootstrap,
            "heroCity": "上海",
            "latestReservation": latest_reservation,
        },
    )


@app.get("/member", response_class=HTMLResponse)
def member_center(request: Request, actor=Depends(get_optional_session_actor)) -> HTMLResponse:
    if actor is None or actor.role != "customer":
        return templates.TemplateResponse(
            request,
            "member.html",
            {
                **_base_template_context(request, actor),
                "page": "member",
                "member": None,
                "points": None,
                "reservations": [],
                "reservationSummary": None,
            },
        )
    reservations = [
        {
            **reservation,
            "statusLabel": _status_label(str(reservation["status"])),
        }
        for reservation in list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID)
    ]
    return templates.TemplateResponse(
        request,
        "member.html",
        {
            **_base_template_context(request, actor),
            "page": "member",
            "member": get_member(actor.member_id or DEFAULT_MEMBER_ID),
            "points": get_point_account(actor.member_id or DEFAULT_MEMBER_ID),
            "reservations": reservations,
            "reservationSummary": _member_reservation_summary(reservations),
        },
    )


@app.get("/cats", response_class=HTMLResponse)
def cat_archive(request: Request, actor=Depends(get_optional_session_actor)) -> HTMLResponse:
    if actor is None or actor.role != "customer":
        cats: list[dict[str, object]] = []
    else:
        cats = list_member_cats(actor.member_id or DEFAULT_MEMBER_ID)
    return templates.TemplateResponse(
        request,
        "cats.html",
        {
            **_base_template_context(request, actor),
            "page": "cats",
            "cats": cats,
        },
    )


@app.get("/recommendations", response_class=HTMLResponse)
def recommendations_page(request: Request, actor=Depends(get_optional_session_actor)) -> HTMLResponse:
    if actor is None or actor.role != "customer":
        recommendations: list[dict[str, object]] = []
    else:
        recommendations = list_member_recommendations(actor.member_id or DEFAULT_MEMBER_ID)
    return templates.TemplateResponse(
        request,
        "recommendations.html",
        {
            **_base_template_context(request, actor),
            "page": "recommendations",
            "recommendations": recommendations,
        },
    )


@app.post("/member/reservations/{reservation_id}/cancel")
def cancel_member_reservation_page(
    reservation_id: str,
    actor=Depends(get_required_session_actor),
) -> RedirectResponse:
    ensure_role(actor, "customer")
    try:
        cancel_reservation(actor.member_id or DEFAULT_MEMBER_ID, reservation_id)
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
    return RedirectResponse(url="/member", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/staff", response_class=HTMLResponse)
def staff_console(
    request: Request,
    business_date: str = Query(default=DEFAULT_DATE, alias="businessDate"),
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    stores = list_stores()
    active_store_id = actor.store_id if actor and actor.role == "staff" and actor.store_id else stores[0]["storeId"]
    reservations = (
        list_staff_reservations(active_store_id, business_date, status_filter)
        if actor and actor.role == "staff"
        else []
    )
    return templates.TemplateResponse(
        request,
        "staff.html",
        {
            **_base_template_context(request, actor),
            "page": "staff",
            "stores": stores,
            "activeStoreId": active_store_id,
            "businessDate": business_date,
            "statusFilter": status_filter or "",
            "reservations": reservations,
        },
    )


@app.post("/api/session/login")
def login_session(payload: SessionLoginRequest, response: Response) -> dict[str, object]:
    session = create_session(payload.persona)
    response.set_cookie(
        COOKIE_NAME,
        session["sessionToken"],
        httponly=True,
        samesite="lax",
        path="/",
    )
    return session


@app.get("/api/session/me")
def get_session_me(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return actor.to_session_payload()


@app.post("/api/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_session(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@app.get("/api/stores")
def get_stores() -> list[dict[str, object]]:
    return list_stores()


@app.get("/api/slots")
def get_slots(
    store_id: str = Query(alias="storeId"),
    date: str = Query(),
    party_size: int = Query(alias="partySize"),
) -> list[dict[str, object]]:
    return list_available_slots(store_id, date, party_size)


@app.get("/api/member/me")
def get_current_member(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "customer")
    return get_member(actor.member_id or DEFAULT_MEMBER_ID)


@app.get("/api/member/me/points")
def get_current_points(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "customer")
    return get_point_account(actor.member_id or DEFAULT_MEMBER_ID)


@app.get("/api/cats/me")
def get_current_cats(actor=Depends(get_required_session_actor)) -> list[dict[str, object]]:
    ensure_role(actor, "customer")
    return list_member_cats(actor.member_id or DEFAULT_MEMBER_ID)


@app.get("/api/recommendations/me")
def get_current_recommendations(actor=Depends(get_required_session_actor)) -> list[dict[str, object]]:
    ensure_role(actor, "customer")
    return list_member_recommendations(actor.member_id or DEFAULT_MEMBER_ID)


@app.post("/api/reservations", status_code=status.HTTP_201_CREATED)
def create_customer_reservation(
    payload: CreateReservationRequest,
    actor=Depends(get_required_session_actor),
) -> dict[str, object]:
    ensure_role(actor, "customer")
    try:
        return create_reservation(actor.member_id or DEFAULT_MEMBER_ID, payload.storeId, payload.slotId, payload.partySize)
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
                "message": "Requested party size exceeds slot capacity.",
            },
        ) from exc


@app.get("/api/reservations/me")
def get_my_reservations(
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_role(actor, "customer")
    return list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID, status_filter)


@app.post("/api/reservations/{reservation_id}/cancel")
def cancel_my_reservation(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "customer")
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


@app.get("/api/staff/reservations")
def get_staff_reservations(
    store_id: str = Query(alias="storeId"),
    business_date: str = Query(alias="businessDate"),
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_role(actor, "staff")
    if actor.store_id != store_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Current session does not have access to this resource.",
            },
        )
    return list_staff_reservations(store_id, business_date, status_filter)


@app.post("/api/staff/reservations/{reservation_id}/check-in")
def check_in_staff_reservation(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_role(actor, "staff")
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
