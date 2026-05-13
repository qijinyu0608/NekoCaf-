from pathlib import Path
from urllib.parse import parse_qs, urlencode

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.auth import COOKIE_NAME
from app.auth import create_session
from app.auth import ensure_permission
from app.auth import ensure_role
from app.auth import get_optional_session_actor
from app.auth import get_required_session_actor
from app.auth import list_permission_profiles
from app.data import DEFAULT_DATE
from app.data import DEFAULT_MEMBER_ID
from app.data import DEFAULT_STORE_ID
from app.data import InvalidReservationRequestError
from app.data import ReservationStateError
from app.data import StoreUnavailableError
from app.data import cancel_reservation
from app.data import check_in_reservation
from app.data import create_reservation
from app.data import get_database_path
from app.data import get_member
from app.data import get_point_account
from app.data import get_reservation_detail
from app.data import get_staff_reservation_stats
from app.data import list_cities
from app.data import list_available_slots
from app.data import list_member_cats
from app.data import list_member_recommendations
from app.data import list_member_reservations
from app.data import list_staff_reservations
from app.data import list_store_availability
from app.data import list_stores
from app.data import reset_demo_state
from app.data import set_store_operating_status
from app.data import update_member_profile
from libs.common.observability import install_observability


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
STORE_PAGE_SIZE = 20
CITY_REGIONS = {
    "核心城市": {"上海", "北京", "南京", "杭州", "成都"},
    "华东": {"苏州", "无锡", "宁波", "合肥", "福州", "济南", "青岛", "厦门"},
    "华南": {"广州", "深圳"},
    "华中西南": {"武汉", "长沙", "郑州", "重庆", "昆明", "西安"},
    "华北东北": {"天津", "沈阳"},
}


class SessionLoginRequest(BaseModel):
    persona: str


class CreateReservationRequest(BaseModel):
    storeId: str
    slotId: str
    partySize: int = Field(gt=0)


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


def _preview_context(
    store_id: str | None = None,
    city_name: str | None = None,
    business_date: str = DEFAULT_DATE,
    party_size: int = 2,
) -> dict[str, object]:
    cities = list_cities()
    stores = list_stores()
    store_ids = {store["storeId"] for store in stores}
    selected_city = city_name if city_name in cities else cities[0]
    if store_id in store_ids:
        selected_city = str(next(store["cityName"] for store in stores if store["storeId"] == store_id))
    city_stores = list_stores(selected_city)
    recommendations = list_member_recommendations(
        DEFAULT_MEMBER_ID,
        business_date=business_date,
        party_size=party_size,
        city_name=selected_city,
    )
    city_recommendation = next(
        (recommendation for recommendation in recommendations if recommendation["storeId"] in {store["storeId"] for store in city_stores}),
        None,
    )
    recommended_store_id = (
        city_recommendation["storeId"]
        if city_recommendation
        else city_stores[0]["storeId"]
    )
    default_store_id = store_id if store_id in store_ids else recommended_store_id
    default_store = next(store for store in stores if store["storeId"] == default_store_id)
    selected_city = str(default_store["cityName"])
    city_stores = list_stores(selected_city)
    selected_store_label = _store_scope_label(default_store)
    selected_recommendation = next(
        (recommendation for recommendation in recommendations if recommendation["storeId"] == default_store_id),
        _store_recommendation_fallback(default_store),
    )
    return {
        "stores": stores,
        "cityStores": city_stores,
        "cities": cities,
        "selectedCity": selected_city,
        "defaultStoreId": default_store_id,
        "selectedStore": default_store,
        "selectedStoreLabel": selected_store_label,
        "catStoreHref": f"/cats?storeId={default_store_id}",
        "defaultDate": business_date,
        "defaultPartySize": party_size,
        "member": get_member(DEFAULT_MEMBER_ID),
        "points": get_point_account(DEFAULT_MEMBER_ID),
        "cats": list_member_cats(DEFAULT_MEMBER_ID, default_store_id),
        "recommendations": recommendations,
        "selectedRecommendation": selected_recommendation,
        "slots": list_available_slots(default_store_id, business_date, party_size),
    }


def _base_template_context(request: Request, actor=Depends(get_optional_session_actor)) -> dict[str, object]:
    session = actor.to_session_payload() if actor else {"sessionStatus": "anonymous"}
    return {
        "request": request,
        "session": session,
        "actor": actor,
        "selectedCity": "上海",
        "catStoreHref": "/cats",
        "assetVersion": "20260513-booking-hardening-1",
    }


def _status_label(status_value: str) -> str:
    return {
        "BOOKED": "已预约",
        "CHECKED_IN": "已到店",
        "CANCELLED": "已取消",
    }.get(status_value, status_value)


def _store_recommendation_fallback(store: dict[str, object]) -> dict[str, object]:
    return {
        "recommendationId": f"fallback-{store['storeId']}",
        "storeId": store["storeId"],
        "storeName": store["storeName"],
        "district": store["district"],
        "headline": "当前城市推荐",
        "summary": f"{store['storeName']} · {store['district']}",
        "detail": store["summary"],
        "reasonTags": store["featureTags"],
    }


def _store_scope_label(store: dict[str, object]) -> str:
    return f"{store['cityName']}{store['storeName']}"


def _city_groups(cities: list[str]) -> list[dict[str, object]]:
    grouped: list[dict[str, object]] = []
    used: set[str] = set()
    for region_name, region_cities in CITY_REGIONS.items():
        items = [city for city in cities if city in region_cities]
        if items:
            grouped.append({"name": region_name, "cities": items})
            used.update(items)
    remaining = [city for city in cities if city not in used]
    if remaining:
        grouped.append({"name": "其他城市", "cities": remaining})
    return grouped


def _load_more_url(path: str, params: dict[str, object], next_page: int) -> str:
    query_params = {
        key: value
        for key, value in {**params, "page": next_page}.items()
        if value not in (None, "", "ALL")
    }
    if not query_params:
        return path
    return f"{path}?{urlencode(query_params)}"


def _display_visit_time(slot_start_at: object) -> str:
    value = str(slot_start_at)
    if len(value) >= 16 and "T" in value:
        return f"{value[5:10].replace('-', '/')} {value[11:16]}"
    return value


def _decorate_reservation(reservation: dict[str, object]) -> dict[str, object]:
    return {
        **reservation,
        "statusLabel": _status_label(str(reservation["status"])),
        "displayStartAt": _display_visit_time(reservation["slotStartAt"]),
    }


def _reservation_state_message(status_value: str, action: str) -> str:
    status_label = _status_label(status_value)
    if action == "cancel":
        return f"当前预约状态为{status_label}，只能取消已预约的记录。"
    if action == "check-in":
        return f"当前预约状态为{status_label}，只能确认已预约的记录到店。"
    return f"当前预约状态为{status_label}，无法执行该操作。"


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


def _get_scoped_customer_reservation(actor, reservation_id: str) -> dict[str, object]:
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


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    store_id: str | None = Query(default=None, alias="storeId"),
    city_name: str | None = Query(default=None, alias="city"),
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    preview = _preview_context(store_id, city_name, business_date, party_size)
    latest_reservation = None
    if actor and actor.role == "customer":
        reservations = [
            _decorate_reservation(reservation)
            for reservation in list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID)
        ]
        latest_reservation = reservations[0] if reservations else None
    bootstrap = {
        "session": actor.to_session_payload() if actor else {"sessionStatus": "anonymous"},
        "defaultStoreId": preview["defaultStoreId"],
        "defaultDate": preview["defaultDate"],
        "defaultPartySize": preview["defaultPartySize"],
        "stores": preview["stores"],
        "cities": preview["cities"],
        "selectedCity": preview["selectedCity"],
        "recommendations": preview["recommendations"],
        "recommendationQuery": {
            "date": business_date,
            "partySize": party_size,
        },
    }
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            **_base_template_context(request, actor),
            **preview,
            "page": "home",
            "bootstrap": bootstrap,
            "selectedCity": preview["selectedCity"],
            "bookingCity": preview["selectedCity"],
            "heroCity": preview["selectedStoreLabel"],
            "latestReservation": latest_reservation,
        },
    )


@app.get("/member", response_class=HTMLResponse)
def member_center(request: Request, actor=Depends(get_optional_session_actor)) -> HTMLResponse:
    if actor is None or "member.profile.read.self" not in actor.permissions:
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
        _decorate_reservation(reservation)
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


@app.get("/member/profile/edit", response_class=HTMLResponse)
def edit_member_profile(
    request: Request,
    actor=Depends(get_required_session_actor),
) -> HTMLResponse:
    ensure_permission(actor, "member.profile.update.self")
    member = get_member(actor.member_id or DEFAULT_MEMBER_ID)
    return templates.TemplateResponse(
        request,
        "member_profile_edit.html",
        {
            **_base_template_context(request, actor),
            "page": "member",
            "member": member,
            "preferencesText": "，".join(member["preferences"]),
        },
    )


@app.post("/member/profile")
async def update_member_profile_page(
    request: Request,
    actor=Depends(get_required_session_actor),
) -> RedirectResponse:
    ensure_permission(actor, "member.profile.update.self")
    form = parse_qs((await request.body()).decode("utf-8"))
    preferences_text = form.get("preferencesText", [""])[0]
    preferences = [
        item.strip()
        for item in preferences_text.replace("，", ",").split(",")
        if item.strip()
    ]
    update_member_profile(
        actor.member_id or DEFAULT_MEMBER_ID,
        nickname=form.get("nickname", [""])[0],
        mobile_masked=form.get("mobileMasked", [""])[0],
        preferences=preferences,
    )
    return RedirectResponse(url="/member", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/cats", response_class=HTMLResponse)
def cat_archive(
    request: Request,
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    stores = list_stores()
    store_ids = {store["storeId"] for store in stores}
    selected_store_id = store_id if store_id in store_ids else DEFAULT_STORE_ID
    selected_store = next(
        (store for store in stores if store["storeId"] == selected_store_id),
        stores[0],
    )
    if actor is None or "cat.read.self" not in actor.permissions:
        cats: list[dict[str, object]] = []
    else:
        cats = list_member_cats(actor.member_id or DEFAULT_MEMBER_ID, str(selected_store["storeId"]))
    return templates.TemplateResponse(
        request,
        "cats.html",
        {
            **_base_template_context(request, actor),
            "page": "cats",
            "cats": cats,
            "stores": stores,
            "selectedStore": selected_store,
            "selectedStoreLabel": _store_scope_label(selected_store),
            "selectedCity": _store_scope_label(selected_store),
            "catStoreHref": f"/cats?storeId={selected_store['storeId']}",
        },
    )


@app.get("/recommendations", response_class=HTMLResponse)
def recommendations_page(
    request: Request,
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    if actor is None or "recommendation.read.self" not in actor.permissions:
        recommendations: list[dict[str, object]] = []
    else:
        recommendations = list_member_recommendations(
            actor.member_id or DEFAULT_MEMBER_ID,
            business_date=business_date,
            party_size=party_size,
        )
    return templates.TemplateResponse(
        request,
        "recommendations.html",
        {
            **_base_template_context(request, actor),
            "page": "recommendations",
            "recommendations": recommendations,
            "recommendationDate": business_date,
            "recommendationPartySize": party_size,
        },
    )


@app.get("/stores", response_class=HTMLResponse)
def store_directory(
    request: Request,
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    page: int = Query(default=1),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    cities = list_cities()
    active_city = city_name if city_name in cities else None
    selected_city = active_city or "全部城市"
    active_page = max(1, page)
    all_availability = list_store_availability(
        active_city,
        business_date,
        party_size,
        search_query=search_query,
    )
    total_count = len(all_availability)
    visible_count = min(total_count, active_page * STORE_PAGE_SIZE)
    page_params = {
        "city": active_city,
        "q": (search_query or "").strip(),
        "date": business_date,
        "partySize": party_size,
    }
    return templates.TemplateResponse(
        request,
        "stores.html",
        {
            **_base_template_context(request, actor),
            "page": "stores",
            "cities": cities,
            "cityGroups": _city_groups(cities),
            "activeCity": active_city,
            "selectedCity": selected_city,
            "defaultDate": business_date,
            "defaultPartySize": party_size,
            "storeSearchQuery": (search_query or "").strip(),
            "storesWithAvailability": all_availability[:visible_count],
            "totalStoreCount": total_count,
            "visibleStoreCount": visible_count,
            "hasMoreStores": visible_count < total_count,
            "loadMoreUrl": _load_more_url("/stores", page_params, active_page + 1),
        },
    )


@app.get("/reservations/{reservation_id}", response_class=HTMLResponse)
def reservation_confirmation(
    request: Request,
    reservation_id: str,
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    if actor is None:
        return templates.TemplateResponse(
            request,
            "reservation_detail.html",
            {
                **_base_template_context(request, actor),
                "page": "reservation",
                "reservation": None,
                "reservationId": reservation_id,
            },
        )
    reservation = _decorate_reservation(_get_scoped_customer_reservation(actor, reservation_id))
    return templates.TemplateResponse(
        request,
        "reservation_detail.html",
        {
            **_base_template_context(request, actor),
            "page": "reservation",
            "selectedCity": reservation["cityName"],
            "reservation": reservation,
            "reservationId": reservation_id,
        },
    )


@app.post("/reservations/{reservation_id}/cancel")
def cancel_reservation_confirmation_page(
    reservation_id: str,
    actor=Depends(get_required_session_actor),
) -> RedirectResponse:
    ensure_permission(actor, "reservation.cancel.self")
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
    except ReservationStateError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RESERVATION_STATE_CONFLICT",
                "message": _reservation_state_message(exc.current_status, "cancel"),
            },
        ) from exc
    return RedirectResponse(url=f"/reservations/{reservation_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/member/reservations/{reservation_id}/cancel")
def cancel_member_reservation_page(
    reservation_id: str,
    actor=Depends(get_required_session_actor),
) -> RedirectResponse:
    ensure_permission(actor, "reservation.cancel.self")
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
    except ReservationStateError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RESERVATION_STATE_CONFLICT",
                "message": _reservation_state_message(exc.current_status, "cancel"),
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
    active_store_id = actor.store_id if actor and "staff.reservations.read" in actor.permissions and actor.store_id else stores[0]["storeId"]
    reservations = (
        [
            _decorate_reservation(reservation)
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
            **_base_template_context(request, actor),
            "page": "staff",
            "stores": stores,
            "activeStoreId": active_store_id,
            "businessDate": business_date,
            "statusFilter": status_filter or "",
            "reservations": reservations,
            "stats": stats,
        },
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
    store_status: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> HTMLResponse:
    ensure_permission(actor, "permissions.manage")
    cities = list_cities()
    active_city = city_name if city_name in cities else None
    active_status = store_status if store_status in {"OPEN", "PAUSED"} else ""
    all_stores = list_stores(include_paused=True)
    stores = list_stores(
        active_city,
        include_paused=True,
        search_query=search_query,
        operating_status=active_status,
    )
    open_store_count = len([store for store in all_stores if store["isBookable"]])
    permission_profiles = list_permission_profiles()
    staff_store_id = next(
        (
            profile["scope"]["storeId"]
            for profile in permission_profiles
            if profile["role"] == "staff" and profile["scope"]["storeId"]
        ),
        DEFAULT_STORE_ID,
    )
    staff_stats = get_staff_reservation_stats(str(staff_store_id), DEFAULT_DATE)
    systems = [
        {
            "name": "顾客系统",
            "description": "预约、会员信息、猫咪档案与推荐入口。",
            "owner": "会员",
            "entry": "/",
        },
        {
            "name": "店员系统",
            "description": "本店预约、筛选与到店确认。",
            "owner": "店员",
            "entry": "/staff",
        },
        {
            "name": "管理员系统",
            "description": "角色权限、系统范围与运营概览。",
            "owner": "管理员",
            "entry": "/admin",
        },
    ]
    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            **_base_template_context(request, actor),
            "page": "admin",
            "selectedCity": "全局",
            "systems": systems,
            "storeCount": len(all_stores),
            "openStoreCount": open_store_count,
            "cityCount": len(cities),
            "roleCount": len(permission_profiles),
            "staffStats": staff_stats,
            "permissionProfiles": permission_profiles,
            "stores": stores,
            "cities": cities,
            "cityGroups": _city_groups(cities),
            "activeCity": active_city or "",
            "activeStoreStatus": active_status,
            "storeSearchQuery": (search_query or "").strip(),
            "filteredStoreCount": len(stores),
        },
    )


@app.post("/admin/stores/{store_id}/status")
async def update_admin_store_status(
    store_id: str,
    request: Request,
    actor=Depends(get_required_session_actor),
) -> RedirectResponse:
    ensure_permission(actor, "store.operations.manage")
    raw_body = (await request.body()).decode("utf-8")
    form_data = parse_qs(raw_body)
    operating_status = form_data.get("operatingStatus", ["OPEN"])[0]
    operating_note = form_data.get("operatingNote", [""])[0]
    try:
        set_store_operating_status(store_id, operating_status, operating_note)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STORE_NOT_FOUND",
                "message": "Store does not exist.",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STORE_STATUS",
                "message": "门店运营状态不正确，请重新选择。",
            },
        ) from exc
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/permissions", response_class=HTMLResponse)
def permissions_page(request: Request, actor=Depends(get_required_session_actor)) -> HTMLResponse:
    ensure_permission(actor, "permissions.manage")
    return templates.TemplateResponse(
        request,
        "permissions.html",
        {
            **_base_template_context(request, actor),
            "page": "permissions",
            "permissionProfiles": list_permission_profiles(),
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
def get_stores(
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
) -> list[dict[str, object]]:
    return list_stores(city_name, search_query=search_query)


@app.get("/api/stores/availability")
def get_store_availability(
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
) -> list[dict[str, object]]:
    active_city = city_name if city_name in list_cities() else None
    return list_store_availability(active_city, business_date, party_size, search_query=search_query)


@app.get("/api/cities")
def get_cities() -> list[str]:
    return list_cities()


@app.get("/api/slots")
def get_slots(
    store_id: str = Query(alias="storeId"),
    date: str = Query(),
    party_size: int = Query(alias="partySize", ge=1),
) -> list[dict[str, object]]:
    return list_available_slots(store_id, date, party_size)


@app.get("/api/member/me")
def get_current_member(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "member.profile.read.self")
    return get_member(actor.member_id or DEFAULT_MEMBER_ID)


@app.get("/api/member/me/points")
def get_current_points(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "member.points.read.self")
    return get_point_account(actor.member_id or DEFAULT_MEMBER_ID)


@app.get("/api/cats/me")
def get_current_cats(
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "cat.read.self")
    return list_member_cats(actor.member_id or DEFAULT_MEMBER_ID, store_id)


@app.get("/api/recommendations/me")
def get_current_recommendations(
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    city_name: str | None = Query(default=None, alias="city"),
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "recommendation.read.self")
    active_city = city_name if city_name in list_cities() else None
    return list_member_recommendations(
        actor.member_id or DEFAULT_MEMBER_ID,
        business_date=business_date,
        party_size=party_size,
        city_name=active_city,
        store_id=store_id,
    )


@app.post("/api/reservations", status_code=status.HTTP_201_CREATED)
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


@app.get("/api/reservations/me")
def get_my_reservations(
    status_filter: str | None = Query(default=None, alias="status"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "reservation.read.self")
    return list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID, status_filter)


@app.get("/api/reservations/{reservation_id}")
def get_my_reservation_detail(reservation_id: str, actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return _get_scoped_customer_reservation(actor, reservation_id)


@app.post("/api/reservations/{reservation_id}/cancel")
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
                "message": _reservation_state_message(exc.current_status, "cancel"),
            },
        ) from exc


@app.get("/api/staff/reservations")
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


@app.post("/api/staff/reservations/{reservation_id}/check-in")
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
                "message": _reservation_state_message(exc.current_status, "check-in"),
            },
        ) from exc


@app.get("/api/permissions/me")
def get_current_permission_profile(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return {
        "actorId": actor.actor_id,
        "displayName": actor.display_name,
        "role": actor.role,
        "permissions": list(actor.permissions),
        "scope": {
            "memberId": actor.member_id,
            "storeId": actor.store_id,
        },
    }


@app.get("/api/permissions/profiles")
def get_permission_profiles(actor=Depends(get_required_session_actor)) -> list[dict[str, object]]:
    ensure_permission(actor, "permissions.manage")
    return list_permission_profiles()
