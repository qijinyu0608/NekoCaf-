from typing import Any

from app.auth import DEFAULT_TENANT_ID
from app.db.connection import connect


def list_available_slots(store_id: str, business_date: str, party_size: int) -> list[dict[str, Any]]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                   s.zone_name, s.interaction_label, s.table_code,
                   s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            JOIN stores st
              ON st.tenant_id = s.tenant_id
             AND st.store_id = s.store_id
             AND st.operating_status = 'OPEN'
            WHERE s.tenant_id = ?
              AND s.store_id = ?
              AND s.business_date = ?
            GROUP BY s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                     s.zone_name, s.interaction_label, s.table_code
            HAVING remaining_capacity >= ?
            ORDER BY start_at
            """,
            (DEFAULT_TENANT_ID, store_id, business_date, party_size),
        ).fetchall()
    return [_slot_from_row(row) for row in rows]


def _slot_from_row(row) -> dict[str, Any]:
    return {
        "slotId": row["slot_id"],
        "storeId": row["store_id"],
        "businessDate": row["business_date"],
        "startAt": row["start_at"],
        "capacity": row["capacity"],
        "zoneName": row["zone_name"],
        "interactionLabel": row["interaction_label"],
        "tableCode": row["table_code"],
        "remainingCapacity": row["remaining_capacity"],
    }


def list_available_slots_for_stores(
    store_ids: list[str],
    business_date: str,
    party_size: int,
) -> dict[str, list[dict[str, Any]]]:
    if not store_ids:
        return {}
    placeholders = ", ".join("?" for _ in store_ids)
    with connect() as connection:
        rows = connection.execute(
            f"""
            SELECT s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                   s.zone_name, s.interaction_label, s.table_code,
                   s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            JOIN stores st
              ON st.tenant_id = s.tenant_id
             AND st.store_id = s.store_id
             AND st.operating_status = 'OPEN'
            WHERE s.tenant_id = ?
              AND s.store_id IN ({placeholders})
              AND s.business_date = ?
            GROUP BY s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                     s.zone_name, s.interaction_label, s.table_code
            HAVING remaining_capacity >= ?
            ORDER BY s.store_id, s.start_at
            """,
            [DEFAULT_TENANT_ID, *store_ids, business_date, party_size],
        ).fetchall()
    slots_by_store = {store_id: [] for store_id in store_ids}
    for row in rows:
        slots_by_store.setdefault(row["store_id"], []).append(_slot_from_row(row))
    return slots_by_store


def get_slot(slot_id: str) -> dict[str, Any] | None:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT slot_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
            FROM store_slots
            WHERE tenant_id = ? AND slot_id = ?
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "slotId": row["slot_id"],
        "storeId": row["store_id"],
        "businessDate": row["business_date"],
        "startAt": row["start_at"],
        "capacity": row["capacity"],
        "zoneName": row["zone_name"],
        "interactionLabel": row["interaction_label"],
        "tableCode": row["table_code"],
    }


def _get_remaining_capacity(slot_id: str) -> int:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            WHERE s.tenant_id = ? AND s.slot_id = ?
            GROUP BY s.slot_id, s.capacity
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
    if row is None:
        return 0
    return int(row["remaining_capacity"])
