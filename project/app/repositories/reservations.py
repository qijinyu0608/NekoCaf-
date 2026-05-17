from typing import Any

from app.auth import DEFAULT_TENANT_ID
from app.db.connection import connect


def get_reservation_detail(reservation_id: str) -> dict[str, Any]:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT r.reservation_id, r.member_id, r.store_id, s.store_name, s.city_name, s.district,
                   s.address, s.business_hours, s.phone, r.slot_id, r.business_date,
                   r.slot_start_at, r.party_size, r.status, r.zone_name,
                   r.interaction_label, r.table_code, r.checked_in_at
            FROM reservations r
            JOIN stores s ON s.tenant_id = r.tenant_id AND s.store_id = r.store_id
            WHERE r.reservation_id = ? AND r.tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
    if row is None:
        raise KeyError(reservation_id)
    return {
        "reservationId": row["reservation_id"],
        "memberId": row["member_id"],
        "storeId": row["store_id"],
        "storeName": row["store_name"],
        "cityName": row["city_name"],
        "district": row["district"],
        "address": row["address"],
        "businessHours": row["business_hours"],
        "phone": row["phone"],
        "slotId": row["slot_id"],
        "businessDate": row["business_date"],
        "slotStartAt": row["slot_start_at"],
        "partySize": row["party_size"],
        "status": row["status"],
        "zoneName": row["zone_name"],
        "interactionLabel": row["interaction_label"],
        "tableCode": row["table_code"],
        "checkedInAt": row["checked_in_at"],
    }


def list_member_reservations(member_id: str, status_filter: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT r.reservation_id, r.member_id, r.store_id, s.store_name, s.city_name, s.district,
               r.slot_id, r.business_date, r.slot_start_at, r.party_size,
               r.status, r.zone_name, r.interaction_label, r.table_code, r.checked_in_at
        FROM reservations r
        JOIN stores s ON s.tenant_id = r.tenant_id AND s.store_id = r.store_id
        WHERE r.tenant_id = ? AND r.member_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, member_id]
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    query += " ORDER BY slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "memberId": row["member_id"],
            "storeId": row["store_id"],
            "storeName": row["store_name"],
            "cityName": row["city_name"],
            "district": row["district"],
            "slotId": row["slot_id"],
            "businessDate": row["business_date"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "status": row["status"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
            "checkedInAt": row["checked_in_at"],
        }
        for row in rows
    ]


def list_staff_reservations(
    store_id: str,
    business_date: str,
    status_filter: str | None = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT r.reservation_id, r.member_id, m.nickname, r.store_id, r.slot_start_at, r.party_size,
               r.status, r.zone_name, r.interaction_label, r.table_code, r.checked_in_at
        FROM reservations r
        JOIN members m ON m.tenant_id = r.tenant_id AND m.member_id = r.member_id
        WHERE r.tenant_id = ? AND r.store_id = ? AND r.business_date = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, store_id, business_date]
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    query += " ORDER BY r.slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "memberId": row["member_id"],
            "memberNickname": row["nickname"],
            "storeId": row["store_id"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "status": row["status"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
            "checkedInAt": row["checked_in_at"],
        }
        for row in rows
    ]


def get_staff_reservation_stats(store_id: str, business_date: str) -> dict[str, int]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM reservations
            WHERE tenant_id = ? AND store_id = ? AND business_date = ?
            GROUP BY status
            """,
            (DEFAULT_TENANT_ID, store_id, business_date),
        ).fetchall()
    by_status = {row["status"]: int(row["count"]) for row in rows}
    booked = by_status.get("BOOKED", 0)
    checked_in = by_status.get("CHECKED_IN", 0)
    cancelled = by_status.get("CANCELLED", 0)
    return {
        "total": booked + checked_in + cancelled,
        "booked": booked,
        "checkedIn": checked_in,
        "cancelled": cancelled,
    }
