from urllib.parse import parse_qs
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import ensure_permission, get_required_session_actor, list_permission_profiles
from app.core.constants import DEFAULT_DATE, DEFAULT_STORE_ID
from app.presenters import base_template_context, city_groups
from app.repositories.reservations import get_staff_reservation_stats
from app.repositories.stores import list_cities, list_stores, set_store_operating_status
from app.services.catalog import list_store_availability
from app.web import templates


router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
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
    paused_store_count = len(all_stores) - open_store_count
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
    open_store_percent = round(open_store_count / len(all_stores) * 100) if all_stores else 0
    paused_store_percent = 100 - open_store_percent if all_stores else 0
    city_store_counts = Counter(str(store["cityName"]) for store in all_stores)
    max_city_store_count = max(city_store_counts.values()) if city_store_counts else 1
    city_store_bars = [
        {
            "city": city,
            "count": city_store_counts[city],
            "percent": round(city_store_counts[city] / max_city_store_count * 100),
        }
        for city in cities
        if city in city_store_counts
    ]
    availability = list_store_availability(
        business_date=DEFAULT_DATE,
        party_size=2,
        include_paused=True,
    )
    total_available_slots = sum(int(store["availableSlotCount"]) for store in availability)
    average_slots_per_open_store = round(total_available_slots / open_store_count, 1) if open_store_count else 0
    top_available_stores = sorted(
        availability,
        key=lambda store: int(store["availableSlotCount"]),
        reverse=True,
    )[:5]
    max_available_slots = max(
        [int(store["availableSlotCount"]) for store in top_available_stores],
        default=1,
    )
    top_store_bars = [
        {
            "label": f"{store['cityName']} · {store['storeName']}",
            "count": int(store["availableSlotCount"]),
            "percent": round(int(store["availableSlotCount"]) / max_available_slots * 100) if max_available_slots else 0,
        }
        for store in top_available_stores
    ]
    reservation_total = max(staff_stats["total"], 1)
    reservation_mix = [
        {
            "label": "待到店",
            "count": staff_stats["booked"],
            "percent": round(staff_stats["booked"] / reservation_total * 100),
        },
        {
            "label": "已到店",
            "count": staff_stats["checkedIn"],
            "percent": round(staff_stats["checkedIn"] / reservation_total * 100),
        },
        {
            "label": "已取消",
            "count": staff_stats["cancelled"],
            "percent": round(staff_stats["cancelled"] / reservation_total * 100),
        },
    ]
    max_permission_count = max([len(profile["permissions"]) for profile in permission_profiles], default=1)
    permission_profile_bars = [
        {
            "label": profile["displayName"],
            "role": profile["role"],
            "count": len(profile["permissions"]),
            "percent": round(len(profile["permissions"]) / max_permission_count * 100),
        }
        for profile in permission_profiles
    ]
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
            **base_template_context(request, actor),
            "page": "admin",
            "selectedCity": "全局",
            "systems": systems,
            "storeCount": len(all_stores),
            "openStoreCount": open_store_count,
            "pausedStoreCount": paused_store_count,
            "openStorePercent": open_store_percent,
            "pausedStorePercent": paused_store_percent,
            "cityCount": len(cities),
            "roleCount": len(permission_profiles),
            "defaultDate": DEFAULT_DATE,
            "staffStats": staff_stats,
            "totalAvailableSlots": total_available_slots,
            "averageSlotsPerOpenStore": average_slots_per_open_store,
            "cityStoreBars": city_store_bars,
            "topStoreBars": top_store_bars,
            "reservationMix": reservation_mix,
            "permissionProfileBars": permission_profile_bars,
            "permissionProfiles": permission_profiles,
            "stores": stores,
            "cities": cities,
            "cityGroups": city_groups(cities),
            "activeCity": active_city or "",
            "activeStoreStatus": active_status,
            "storeSearchQuery": (search_query or "").strip(),
            "filteredStoreCount": len(stores),
        },
    )


@router.post("/admin/stores/{store_id}/status")
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


@router.get("/permissions", response_class=HTMLResponse)
def permissions_page(request: Request, actor=Depends(get_required_session_actor)) -> HTMLResponse:
    ensure_permission(actor, "permissions.manage")
    return templates.TemplateResponse(
        request,
        "permissions.html",
        {
            **base_template_context(request, actor),
            "page": "permissions",
            "permissionProfiles": list_permission_profiles(),
        },
    )
