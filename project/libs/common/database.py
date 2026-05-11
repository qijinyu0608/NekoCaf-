import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


DEFAULT_TENANT_ID = "tenant-nekocafe"


def get_database_path() -> Path:
    configured_path = os.environ.get("NEKOCAFE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[2] / "data" / "nekocafe.sqlite3"


def connect() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(*, reset: bool = False) -> None:
    database_path = get_database_path()
    if reset and database_path.exists():
        database_path.unlink()

    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                nickname TEXT NOT NULL,
                mobile_masked TEXT NOT NULL,
                loyalty_level TEXT NOT NULL,
                preferences_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS point_accounts (
                member_id TEXT PRIMARY KEY,
                current_points INTEGER NOT NULL,
                pending_points INTEGER NOT NULL,
                level_code TEXT NOT NULL,
                benefit_summary_json TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            );

            CREATE TABLE IF NOT EXISTS store_slots (
                slot_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                start_at TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                theme TEXT NOT NULL,
                table_code TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                slot_start_at TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL,
                table_code TEXT NOT NULL,
                checked_in_at TEXT,
                preferred_theme TEXT,
                cat_interaction_mode TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (slot_id) REFERENCES store_slots(slot_id)
            );
            """
        )
        _seed_database(connection)


def reset_database() -> None:
    initialize_database(reset=True)


def _seed_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO members (
            member_id, tenant_id, nickname, mobile_masked, loyalty_level, preferences_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "member-1001",
            DEFAULT_TENANT_ID,
            "Momo",
            "138****1024",
            "GOLD",
            json.dumps(["window-seat", "calm-cats"]),
        ),
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO point_accounts (
            member_id, current_points, pending_points, level_code, benefit_summary_json
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "member-1001",
            1280,
            80,
            "GOLD",
            json.dumps(["priority-booking", "birthday-coupon"]),
        ),
    )
    connection.executemany(
        """
        INSERT OR IGNORE INTO store_slots (
            slot_id, tenant_id, store_id, start_at, capacity, theme, table_code
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "slot-20260520-1800",
                DEFAULT_TENANT_ID,
                "store-shanghai-001",
                "2026-05-20T18:00:00+08:00",
                4,
                "sunset-window",
                "T1",
            ),
            (
                "slot-20260520-1930",
                DEFAULT_TENANT_ID,
                "store-shanghai-001",
                "2026-05-20T19:30:00+08:00",
                2,
                "quiet-corner",
                "T2",
            ),
            (
                "slot-20260521-1800",
                DEFAULT_TENANT_ID,
                "store-shanghai-001",
                "2026-05-21T18:00:00+08:00",
                4,
                "garden-calm",
                "T3",
            ),
        ],
    )


def get_member(member_id: str, tenant_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, tenant_id, nickname, mobile_masked, loyalty_level, preferences_json
            FROM members
            WHERE member_id = ? AND tenant_id = ?
            """,
            (member_id, tenant_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "memberId": row["member_id"],
        "tenantId": row["tenant_id"],
        "nickname": row["nickname"],
        "mobileMasked": row["mobile_masked"],
        "loyaltyLevel": row["loyalty_level"],
        "preferences": json.loads(row["preferences_json"]),
    }


def get_point_account(member_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, current_points, pending_points, level_code, benefit_summary_json
            FROM point_accounts
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "memberId": row["member_id"],
        "currentPoints": row["current_points"],
        "pendingPoints": row["pending_points"],
        "levelCode": row["level_code"],
        "benefitSummary": json.loads(row["benefit_summary_json"]),
    }


def list_available_slots(
    *,
    tenant_id: str,
    store_id: str,
    business_date: str,
    party_size: int,
) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT slot_id, start_at, capacity, theme
            FROM store_slots
            WHERE tenant_id = ?
              AND store_id = ?
              AND start_at LIKE ?
              AND capacity >= ?
            ORDER BY start_at
            """,
            (tenant_id, store_id, f"{business_date}%", party_size),
        ).fetchall()
    return [
        {
            "slotId": row["slot_id"],
            "startAt": row["start_at"],
            "capacity": row["capacity"],
            "theme": row["theme"],
        }
        for row in rows
    ]


def find_slot(*, tenant_id: str, store_id: str, slot_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT slot_id, store_id, start_at, capacity, theme, table_code
            FROM store_slots
            WHERE tenant_id = ? AND store_id = ? AND slot_id = ?
            """,
            (tenant_id, store_id, slot_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "slotId": row["slot_id"],
        "storeId": row["store_id"],
        "startAt": row["start_at"],
        "capacity": row["capacity"],
        "theme": row["theme"],
        "tableCode": row["table_code"],
    }


def create_reservation_record(
    *,
    tenant_id: str,
    member_id: str,
    store_id: str,
    slot: dict[str, Any],
    party_size: int,
    preferred_theme: str | None,
    cat_interaction_mode: str | None,
) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        next_number = connection.execute("SELECT COUNT(*) + 1 FROM reservations").fetchone()[0]
        reservation_id = f"res-{next_number:04d}"
        connection.execute(
            """
            INSERT INTO reservations (
                reservation_id, tenant_id, member_id, store_id, slot_id, slot_start_at,
                party_size, status, table_code, checked_in_at, preferred_theme, cat_interaction_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reservation_id,
                tenant_id,
                member_id,
                store_id,
                slot["slotId"],
                slot["startAt"],
                party_size,
                "BOOKED",
                slot["tableCode"],
                None,
                preferred_theme,
                cat_interaction_mode,
            ),
        )
    return get_reservation(reservation_id, tenant_id)  # type: ignore[return-value]


def get_reservation(reservation_id: str, tenant_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT reservation_id, status, table_code, store_id, slot_id, slot_start_at,
                   party_size, checked_in_at
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, tenant_id),
        ).fetchone()
    if row is None:
        return None
    return _reservation_detail_from_row(row)


def list_member_reservation_records(
    *,
    tenant_id: str,
    member_id: str,
    status_filter: str | None = None,
    business_date: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT reservation_id, status, store_id, slot_start_at, party_size, table_code
        FROM reservations
        WHERE tenant_id = ? AND member_id = ?
    """
    params: list[Any] = [tenant_id, member_id]
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if business_date:
        query += " AND slot_start_at LIKE ?"
        params.append(f"{business_date}%")
    query += " ORDER BY slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "status": row["status"],
            "storeId": row["store_id"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "tableCode": row["table_code"],
        }
        for row in rows
    ]


def cancel_reservation_record(reservation_id: str, tenant_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        existing = connection.execute(
            "SELECT status FROM reservations WHERE reservation_id = ? AND tenant_id = ?",
            (reservation_id, tenant_id),
        ).fetchone()
        if existing is None:
            return None
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, tenant_id),
        )
    return get_reservation(reservation_id, tenant_id)


def check_in_reservation_record(reservation_id: str, tenant_id: str) -> dict[str, Any] | None:
    initialize_database()
    checked_in_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        existing = connection.execute(
            "SELECT status FROM reservations WHERE reservation_id = ? AND tenant_id = ?",
            (reservation_id, tenant_id),
        ).fetchone()
        if existing is None:
            return None
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CHECKED_IN', checked_in_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (checked_in_at, reservation_id, tenant_id),
        )
    return get_reservation(reservation_id, tenant_id)


def list_store_reservation_records(
    *,
    tenant_id: str,
    store_id: str,
    business_date: str,
    status_filter: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT r.reservation_id, r.member_id, m.nickname, r.status, r.slot_start_at,
               r.party_size, r.table_code
        FROM reservations r
        JOIN members m ON m.member_id = r.member_id
        WHERE r.tenant_id = ?
          AND r.store_id = ?
          AND r.slot_start_at LIKE ?
    """
    params: list[Any] = [tenant_id, store_id, f"{business_date}%"]
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
            "status": row["status"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "tableCode": row["table_code"],
        }
        for row in rows
    ]


def _reservation_detail_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "reservationId": row["reservation_id"],
        "status": row["status"],
        "tableCode": row["table_code"],
        "storeId": row["store_id"],
        "slotId": row["slot_id"],
        "partySize": row["party_size"],
        "checkedInAt": row["checked_in_at"],
    }
