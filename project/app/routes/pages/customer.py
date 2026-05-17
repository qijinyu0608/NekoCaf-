from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import ensure_permission, get_optional_session_actor, get_required_session_actor
from app.core.constants import DEFAULT_DATE, DEFAULT_MEMBER_ID, DEFAULT_STORE_ID
from app.core.errors import ReservationStateError
from app.presenters import base_template_context, city_groups, decorate_reservation, page_url
from app.presenters import member_reservation_summary, preview_context, reservation_state_message, store_scope_label
from app.repositories.cats import list_member_cats
from app.repositories.members import get_member, get_point_account, update_member_profile
from app.repositories.reservations import list_member_reservations
from app.repositories.slots import list_available_slots
from app.repositories.stores import list_cities, list_stores
from app.routes.helpers import get_scoped_customer_reservation
from app.services.booking import cancel_reservation
from app.services.catalog import list_store_availability
from app.services.recommendations import list_member_recommendations
from app.web import templates


router = APIRouter()
STORE_PAGE_SIZE = 20


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    store_id: str | None = Query(default=None, alias="storeId"),
    city_name: str | None = Query(default=None, alias="city"),
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    if actor and actor.role == "staff":
        return RedirectResponse(url="/staff", status_code=status.HTTP_303_SEE_OTHER)
    if actor and actor.role == "admin":
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    preview = preview_context(store_id, city_name, business_date, party_size)
    if actor is None:
        return templates.TemplateResponse(
            request,
            "public_home.html",
            {
                **base_template_context(request, actor),
                "page": "public",
                "selectedCity": "上海",
                "preview": preview,
            },
        )
    latest_reservation = None
    if actor and actor.role == "customer":
        reservations = [
            decorate_reservation(reservation)
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
            **base_template_context(request, actor),
            **preview,
            "page": "home",
            "bootstrap": bootstrap,
            "selectedCity": preview["selectedCity"],
            "bookingCity": preview["selectedCity"],
            "heroCity": preview["selectedStoreLabel"],
            "latestReservation": latest_reservation,
        },
    )


@router.get("/member", response_class=HTMLResponse)
def member_center(request: Request, actor=Depends(get_optional_session_actor)) -> HTMLResponse:
    if actor is None or "member.profile.read.self" not in actor.permissions:
        return templates.TemplateResponse(
            request,
            "member.html",
            {
                **base_template_context(request, actor),
                "page": "member",
                "member": None,
                "points": None,
                "reservations": [],
                "reservationSummary": None,
            },
        )
    reservations = [
        decorate_reservation(reservation)
        for reservation in list_member_reservations(actor.member_id or DEFAULT_MEMBER_ID)
    ]
    return templates.TemplateResponse(
        request,
        "member.html",
        {
            **base_template_context(request, actor),
            "page": "member",
            "member": get_member(actor.member_id or DEFAULT_MEMBER_ID),
            "points": get_point_account(actor.member_id or DEFAULT_MEMBER_ID),
            "reservations": reservations,
            "reservationSummary": member_reservation_summary(reservations),
        },
    )


@router.get("/member/profile/edit", response_class=HTMLResponse)
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
            **base_template_context(request, actor),
            "page": "member",
            "member": member,
            "preferencesText": "，".join(member["preferences"]),
        },
    )


@router.post("/member/profile")
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


@router.get("/cats", response_class=HTMLResponse)
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
            **base_template_context(request, actor),
            "page": "cats",
            "cats": cats,
            "stores": stores,
            "selectedStore": selected_store,
            "selectedStoreLabel": store_scope_label(selected_store),
            "selectedCity": store_scope_label(selected_store),
            "catStoreHref": f"/cats?storeId={selected_store['storeId']}",
        },
    )


@router.get("/recommendations", response_class=HTMLResponse)
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
            **base_template_context(request, actor),
            "page": "recommendations",
            "recommendations": recommendations,
            "recommendationDate": business_date,
            "recommendationPartySize": party_size,
        },
    )


@router.get("/stores", response_class=HTMLResponse)
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
    all_availability = list_store_availability(
        active_city,
        business_date,
        party_size,
        search_query=search_query,
    )
    total_count = len(all_availability)
    total_pages = max(1, (total_count + STORE_PAGE_SIZE - 1) // STORE_PAGE_SIZE)
    active_page = min(max(1, page), total_pages)
    start_index = (active_page - 1) * STORE_PAGE_SIZE
    end_index = min(total_count, start_index + STORE_PAGE_SIZE)
    page_params = {
        "city": active_city,
        "q": (search_query or "").strip(),
        "date": business_date,
        "partySize": party_size,
    }
    page_links = [
        {
            "page": page_number,
            "url": page_url("/stores", page_params, page_number),
            "isCurrent": page_number == active_page,
        }
        for page_number in range(1, total_pages + 1)
    ]
    return templates.TemplateResponse(
        request,
        "stores.html",
        {
            **base_template_context(request, actor),
            "page": "stores",
            "cities": cities,
            "cityGroups": city_groups(cities),
            "activeCity": active_city,
            "selectedCity": selected_city,
            "defaultDate": business_date,
            "defaultPartySize": party_size,
            "storeSearchQuery": (search_query or "").strip(),
            "storesWithAvailability": all_availability[start_index:end_index],
            "totalStoreCount": total_count,
            "pageStartStore": start_index + 1 if total_count else 0,
            "pageEndStore": end_index,
            "currentStorePage": active_page,
            "totalStorePages": total_pages,
            "storePageLinks": page_links,
            "prevStorePageUrl": page_url("/stores", page_params, active_page - 1) if active_page > 1 else None,
            "nextStorePageUrl": page_url("/stores", page_params, active_page + 1) if active_page < total_pages else None,
        },
    )


@router.get("/stores/{store_id}", response_class=HTMLResponse)
def store_detail(
    request: Request,
    store_id: str,
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    actor=Depends(get_optional_session_actor),
) -> HTMLResponse:
    stores = list_stores()
    store = next((item for item in stores if item["storeId"] == store_id), None)
    if store is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STORE_NOT_FOUND",
                "message": "Store does not exist.",
            },
        )
    slots = list_available_slots(store_id, business_date, party_size)
    return templates.TemplateResponse(
        request,
        "store_detail.html",
        {
            **base_template_context(request, actor),
            "page": "stores",
            "selectedCity": store["cityName"],
            "store": store,
            "slots": slots,
            "defaultDate": business_date,
            "defaultPartySize": party_size,
        },
    )


@router.get("/reservations/{reservation_id}", response_class=HTMLResponse)
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
                **base_template_context(request, actor),
                "page": "reservation",
                "reservation": None,
                "reservationId": reservation_id,
            },
        )
    reservation = decorate_reservation(get_scoped_customer_reservation(actor, reservation_id))
    return templates.TemplateResponse(
        request,
        "reservation_detail.html",
        {
            **base_template_context(request, actor),
            "page": "reservation",
            "selectedCity": reservation["cityName"],
            "reservation": reservation,
            "reservationId": reservation_id,
        },
    )


@router.post("/reservations/{reservation_id}/cancel")
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
                "message": reservation_state_message(exc.current_status, "cancel"),
            },
        ) from exc
    return RedirectResponse(url=f"/reservations/{reservation_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/member/reservations/{reservation_id}/cancel")
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
                "message": reservation_state_message(exc.current_status, "cancel"),
            },
        ) from exc
    return RedirectResponse(url="/member", status_code=status.HTTP_303_SEE_OTHER)
