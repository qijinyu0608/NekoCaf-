import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.auth import DEFAULT_TENANT_ID
from app.core.constants import CHECK_IN_POINTS_PER_GUEST
from app.core.errors import InvalidReservationRequestError, ReservationStateError, StoreUnavailableError
from app.db.connection import connect
from app.repositories.reservations import get_reservation_detail


def _generate_reservation_id(connection: sqlite3.Connection) -> str:
    while True:
        reservation_id = f"res-{uuid4().hex[:12]}"
        exists = connection.execute(
            "SELECT 1 FROM reservations WHERE tenant_id = ? AND reservation_id = ?",
            (DEFAULT_TENANT_ID, reservation_id),
        ).fetchone()
        if exists is None:
            return reservation_id


def create_reservation(member_id: str, store_id: str, slot_id: str, party_size: int) -> dict[str, Any]:
    if party_size <= 0:
        raise InvalidReservationRequestError("invalid-party-size")

    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        store = connection.execute(
            """
            SELECT store_id, operating_status
            FROM stores
            WHERE tenant_id = ? AND store_id = ?
            """,
            (DEFAULT_TENANT_ID, store_id),
        ).fetchone()
        if store is None:
            raise ValueError("store-not-found")
        if store["operating_status"] != "OPEN":
            raise StoreUnavailableError("store-not-bookable")

        slot = connection.execute(
            """
            SELECT slot_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
            FROM store_slots
            WHERE tenant_id = ? AND slot_id = ?
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
        if slot is None or slot["store_id"] != store_id:
            raise ValueError("slot-not-found")

        remaining_row = connection.execute(
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
        remaining_capacity = int(remaining_row["remaining_capacity"]) if remaining_row is not None else 0
        if party_size > remaining_capacity:
            raise OverflowError("slot-capacity")

        reservation_id = _generate_reservation_id(connection)
        connection.execute(
            """
            INSERT INTO reservations (
                reservation_id, tenant_id, member_id, store_id, slot_id, business_date, slot_start_at,
                party_size, status, zone_name, interaction_label, table_code, checked_in_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reservation_id,
                DEFAULT_TENANT_ID,
                member_id,
                store_id,
                slot_id,
                slot["business_date"],
                slot["start_at"],
                party_size,
                "BOOKED",
                slot["zone_name"],
                slot["interaction_label"],
                slot["table_code"],
                None,
            ),
        )
    return get_reservation_detail(reservation_id)


def cancel_reservation(member_id: str, reservation_id: str) -> dict[str, Any]:
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        scope = connection.execute(
            """
            SELECT member_id, status
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["member_id"] != member_id:
            raise PermissionError("wrong-member")
        if scope["status"] != "BOOKED":
            raise ReservationStateError(scope["status"])
        cursor = connection.execute(
            """
            UPDATE reservations
            SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ? AND status = 'BOOKED'
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        )
        if cursor.rowcount == 0:  # pragma: no cover - guarded by transaction and status predicate
            raise ReservationStateError(scope["status"])
    return get_reservation_detail(reservation_id)


def check_in_reservation(store_id: str, reservation_id: str) -> dict[str, Any]:
    checked_in_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        scope = connection.execute(
            """
            SELECT store_id, status, member_id, party_size
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["store_id"] != store_id:
            raise PermissionError("wrong-store")
        if scope["status"] != "BOOKED":
            raise ReservationStateError(scope["status"])
        cursor = connection.execute(
            """
            UPDATE reservations
            SET status = 'CHECKED_IN', checked_in_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ? AND status = 'BOOKED'
            """,
            (checked_in_at, reservation_id, DEFAULT_TENANT_ID),
        )
        if cursor.rowcount == 0:  # pragma: no cover - guarded by transaction and status predicate
            raise ReservationStateError(scope["status"])
        connection.execute(
            """
            UPDATE point_accounts
            SET current_points = current_points + ?,
                pending_points = pending_points + 0
            WHERE member_id = ?
            """,
            (int(scope["party_size"]) * CHECK_IN_POINTS_PER_GUEST, scope["member_id"]),
        )
    return get_reservation_detail(reservation_id)
