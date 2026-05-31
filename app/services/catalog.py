from typing import Any

from app.core.constants import DEFAULT_DATE
from app.repositories.slots import list_available_slots_for_stores
from app.repositories.stores import list_stores


def list_store_availability(
    city_name: str | None = None,
    business_date: str = DEFAULT_DATE,
    party_size: int = 2,
    *,
    include_paused: bool = False,
    search_query: str | None = None,
) -> list[dict[str, Any]]:
    stores = list_stores(city_name, include_paused=include_paused, search_query=search_query)
    slots_by_store = list_available_slots_for_stores(
        [str(store["storeId"]) for store in stores],
        business_date,
        party_size,
    )
    availability: list[dict[str, Any]] = []
    for store in stores:
        slots = slots_by_store.get(str(store["storeId"]), [])
        slot_preview = [
            {
                **slot,
                "displayTime": str(slot["startAt"])[11:16],
            }
            for slot in slots[:4]
        ]
        availability.append(
            {
                **store,
                "businessDate": business_date,
                "partySize": party_size,
                "availableSlotCount": len(slots),
                "earliestAvailableTime": str(slots[0]["startAt"])[11:16] if slots else None,
                "slotPreview": slot_preview,
            }
        )
    return availability
