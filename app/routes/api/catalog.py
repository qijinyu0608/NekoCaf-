from fastapi import APIRouter, Query

from app.core.constants import DEFAULT_DATE
from app.repositories.slots import list_available_slots
from app.repositories.stores import list_cities, list_stores
from app.services.catalog import list_store_availability


router = APIRouter()


@router.get("/api/stores")
def get_stores(
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
) -> list[dict[str, object]]:
    return list_stores(city_name, search_query=search_query)


@router.get("/api/stores/availability")
def get_store_availability(
    city_name: str | None = Query(default=None, alias="city"),
    search_query: str | None = Query(default=None, alias="q"),
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
) -> list[dict[str, object]]:
    active_city = city_name if city_name in list_cities() else None
    return list_store_availability(active_city, business_date, party_size, search_query=search_query)


@router.get("/api/cities")
def get_cities() -> list[str]:
    return list_cities()


@router.get("/api/slots")
def get_slots(
    store_id: str = Query(alias="storeId"),
    date: str = Query(),
    party_size: int = Query(alias="partySize", ge=1),
) -> list[dict[str, object]]:
    return list_available_slots(store_id, date, party_size)
