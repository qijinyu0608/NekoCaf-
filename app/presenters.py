from urllib.parse import urlencode

from fastapi import Request

from app.core.constants import DEFAULT_DATE, DEFAULT_MEMBER_ID
from app.repositories.cats import list_member_cats
from app.repositories.members import get_member, get_point_account
from app.repositories.slots import list_available_slots
from app.repositories.stores import list_cities, list_stores
from app.services.recommendations import list_member_recommendations
from app.web import ASSET_VERSION


CITY_REGIONS = {
    "核心城市": {"上海", "北京", "南京", "杭州", "成都"},
    "华东": {"苏州", "无锡", "宁波", "合肥", "福州", "济南", "青岛", "厦门"},
    "华南": {"广州", "深圳"},
    "华中西南": {"武汉", "长沙", "郑州", "重庆", "昆明", "西安"},
    "华北东北": {"天津", "沈阳"},
}


def preview_context(
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
    selected_store_label = store_scope_label(default_store)
    selected_recommendation = next(
        (recommendation for recommendation in recommendations if recommendation["storeId"] == default_store_id),
        store_recommendation_fallback(default_store),
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


def base_template_context(request: Request, actor=None) -> dict[str, object]:
    session = actor.to_session_payload() if actor else {"sessionStatus": "anonymous"}
    brand_home_href = "/"
    if actor and "staff.reservations.read" in actor.permissions and actor.role == "staff":
        brand_home_href = "/staff"
    elif actor and "permissions.manage" in actor.permissions:
        brand_home_href = "/admin"
    return {
        "request": request,
        "session": session,
        "actor": actor,
        "selectedCity": "上海",
        "catStoreHref": "/cats",
        "assetVersion": ASSET_VERSION,
        "brandHomeHref": brand_home_href,
    }


def status_label(status_value: str) -> str:
    return {
        "BOOKED": "已预约",
        "CHECKED_IN": "已到店",
        "CANCELLED": "已取消",
    }.get(status_value, status_value)


def store_recommendation_fallback(store: dict[str, object]) -> dict[str, object]:
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


def store_scope_label(store: dict[str, object]) -> str:
    return f"{store['cityName']}{store['storeName']}"


def city_groups(cities: list[str]) -> list[dict[str, object]]:
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


def page_url(path: str, params: dict[str, object], page: int) -> str:
    query_params = {
        key: value
        for key, value in {**params, "page": page}.items()
        if value not in (None, "", "ALL")
    }
    if not query_params:
        return path
    return f"{path}?{urlencode(query_params)}"


def display_visit_time(slot_start_at: object) -> str:
    value = str(slot_start_at)
    if len(value) >= 16 and "T" in value:
        return f"{value[5:10].replace('-', '/')} {value[11:16]}"
    return value


def decorate_reservation(reservation: dict[str, object]) -> dict[str, object]:
    return {
        **reservation,
        "statusLabel": status_label(str(reservation["status"])),
        "displayStartAt": display_visit_time(reservation["slotStartAt"]),
    }


def reservation_state_message(status_value: str, action: str) -> str:
    current_status_label = status_label(status_value)
    if action == "cancel":
        return f"当前预约状态为{current_status_label}，只能取消已预约的记录。"
    if action == "check-in":
        return f"当前预约状态为{current_status_label}，只能确认已预约的记录到店。"
    return f"当前预约状态为{current_status_label}，无法执行该操作。"


def member_reservation_summary(reservations: list[dict[str, object]]) -> dict[str, object]:
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
