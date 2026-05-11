import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.auth import DEFAULT_TENANT_ID


DEFAULT_MEMBER_ID = "member-1001"
DEFAULT_CITY = "上海"
DEFAULT_DATE = "2026-05-20"


def get_database_path() -> Path:
    configured_path = os.environ.get("NEKOCAFE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / "data" / "nekocafe.sqlite3"


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
                avatar_label TEXT NOT NULL,
                preferences_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS point_accounts (
                member_id TEXT PRIMARY KEY,
                current_points INTEGER NOT NULL,
                pending_points INTEGER NOT NULL,
                level_code TEXT NOT NULL,
                coupon_count INTEGER NOT NULL,
                growth_value INTEGER NOT NULL,
                growth_target INTEGER NOT NULL,
                benefit_summary_json TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            );

            CREATE TABLE IF NOT EXISTS stores (
                store_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                city_name TEXT NOT NULL,
                store_name TEXT NOT NULL,
                district TEXT NOT NULL,
                summary TEXT NOT NULL,
                feature_tags_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS store_slots (
                slot_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                start_at TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                zone_name TEXT NOT NULL,
                interaction_label TEXT NOT NULL,
                table_code TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(store_id)
            );

            CREATE TABLE IF NOT EXISTS cats (
                cat_id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                name TEXT NOT NULL,
                english_name TEXT NOT NULL,
                age_label TEXT NOT NULL,
                breed TEXT NOT NULL,
                gender TEXT NOT NULL,
                personality_tags_json TEXT NOT NULL,
                companion_summary TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT NOT NULL,
                detail TEXT NOT NULL,
                reason_tags_json TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (store_id) REFERENCES stores(store_id)
            );

            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                slot_start_at TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL,
                zone_name TEXT NOT NULL,
                interaction_label TEXT NOT NULL,
                table_code TEXT NOT NULL,
                checked_in_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (slot_id) REFERENCES store_slots(slot_id)
            );
            """
        )
        _seed_database(connection)


def reset_demo_state() -> None:
    initialize_database(reset=True)


def _seed_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO members (
            member_id, tenant_id, nickname, mobile_masked, loyalty_level, avatar_label, preferences_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            DEFAULT_MEMBER_ID,
            DEFAULT_TENANT_ID,
            "Momo",
            "138****1024",
            "GOLD",
            "MO",
            json.dumps(["window-seat", "calm-cats", "sunny-zone"]),
        ),
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO point_accounts (
            member_id, current_points, pending_points, level_code, coupon_count,
            growth_value, growth_target, benefit_summary_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            DEFAULT_MEMBER_ID,
            2560,
            120,
            "GOLD",
            2,
            860,
            1500,
            json.dumps(["预约保障", "到店优先", "会员日优惠"]),
        ),
    )
    connection.executemany(
        """
        INSERT OR IGNORE INTO stores (
            store_id, tenant_id, city_name, store_name, district, summary, feature_tags_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "store-shanghai-jingan",
                DEFAULT_TENANT_ID,
                DEFAULT_CITY,
                "静安店",
                "静安",
                "采光充足，适合安静放松。",
                json.dumps(["采光充足", "安静畅适", "人气推荐"]),
            ),
            (
                "store-shanghai-pudong",
                DEFAULT_TENANT_ID,
                DEFAULT_CITY,
                "浦东店",
                "浦东",
                "更适合轻社交和周末约会。",
                json.dumps(["江景氛围", "轻社交", "周末热门"]),
            ),
        ],
    )
    connection.executemany(
        """
        INSERT OR IGNORE INTO store_slots (
            slot_id, tenant_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "slot-jingan-20260520-1800",
                DEFAULT_TENANT_ID,
                "store-shanghai-jingan",
                "2026-05-20",
                "2026-05-20T18:00:00+08:00",
                4,
                "阳光房",
                "轻陪伴",
                "J1",
            ),
            (
                "slot-jingan-20260520-1930",
                DEFAULT_TENANT_ID,
                "store-shanghai-jingan",
                "2026-05-20",
                "2026-05-20T19:30:00+08:00",
                2,
                "靠窗双人位",
                "安静陪伴",
                "J2",
            ),
            (
                "slot-pudong-20260520-1830",
                DEFAULT_TENANT_ID,
                "store-shanghai-pudong",
                "2026-05-20",
                "2026-05-20T18:30:00+08:00",
                4,
                "露台内侧",
                "轻互动",
                "P1",
            ),
            (
                "slot-pudong-20260521-1800",
                DEFAULT_TENANT_ID,
                "store-shanghai-pudong",
                "2026-05-21",
                "2026-05-21T18:00:00+08:00",
                6,
                "江景长桌",
                "团体互动",
                "P2",
            ),
        ],
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO cats (
            cat_id, member_id, name, english_name, age_label, breed, gender,
            personality_tags_json, companion_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "cat-001",
            DEFAULT_MEMBER_ID,
            "布丁",
            "Pudding",
            "3岁",
            "布偶猫",
            "♀",
            json.dumps(["喜欢安静与阳光", "适合轻声互动"]),
            "擅长陪伴与治愈",
        ),
    )
    connection.executemany(
        """
        INSERT OR IGNORE INTO recommendations (
            recommendation_id, member_id, store_id, headline, summary, detail, reason_tags_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "rec-001",
                DEFAULT_MEMBER_ID,
                "store-shanghai-jingan",
                "你可能会喜欢",
                "NekoCafé 静安店",
                "与布丁偏好的安静阳光区更匹配，晚间到店动线也更从容。",
                json.dumps(["采光充足", "安静畅适", "人气推荐"]),
            ),
            (
                "rec-002",
                DEFAULT_MEMBER_ID,
                "store-shanghai-pudong",
                "如果你想把到店变得更松弛",
                "NekoCafé 浦东店",
                "更适合偏松弛、带一点互动感的晚间到店节奏，适合把用餐和轻社交放在同一场体验里。",
                json.dumps(["江景氛围", "轻社交", "互动更自然"]),
            ),
        ],
    )


def get_member(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, tenant_id, nickname, mobile_masked, loyalty_level, avatar_label, preferences_json
            FROM members
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
    if row is None:
        raise KeyError(member_id)
    return {
        "memberId": row["member_id"],
        "tenantId": row["tenant_id"],
        "nickname": row["nickname"],
        "mobileMasked": row["mobile_masked"],
        "loyaltyLevel": row["loyalty_level"],
        "avatarLabel": row["avatar_label"],
        "preferences": json.loads(row["preferences_json"]),
    }


def get_point_account(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, current_points, pending_points, level_code, coupon_count,
                   growth_value, growth_target, benefit_summary_json
            FROM point_accounts
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
    if row is None:
        raise KeyError(member_id)
    return {
        "memberId": row["member_id"],
        "currentPoints": row["current_points"],
        "pendingPoints": row["pending_points"],
        "levelCode": row["level_code"],
        "couponCount": row["coupon_count"],
        "growthValue": row["growth_value"],
        "growthTarget": row["growth_target"],
        "benefitSummary": json.loads(row["benefit_summary_json"]),
    }


def list_stores() -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT store_id, city_name, store_name, district, summary, feature_tags_json
            FROM stores
            WHERE tenant_id = ?
            ORDER BY store_name
            """,
            (DEFAULT_TENANT_ID,),
        ).fetchall()
    return [
        {
            "storeId": row["store_id"],
            "cityName": row["city_name"],
            "storeName": row["store_name"],
            "district": row["district"],
            "summary": row["summary"],
            "featureTags": json.loads(row["feature_tags_json"]),
        }
        for row in rows
    ]


def list_available_slots(store_id: str, business_date: str, party_size: int) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT slot_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
            FROM store_slots
            WHERE tenant_id = ?
              AND store_id = ?
              AND business_date = ?
              AND capacity >= ?
            ORDER BY start_at
            """,
            (DEFAULT_TENANT_ID, store_id, business_date, party_size),
        ).fetchall()
    return [
        {
            "slotId": row["slot_id"],
            "storeId": row["store_id"],
            "businessDate": row["business_date"],
            "startAt": row["start_at"],
            "capacity": row["capacity"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
        }
        for row in rows
    ]


def get_slot(slot_id: str) -> dict[str, Any] | None:
    initialize_database()
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


def create_reservation(member_id: str, store_id: str, slot_id: str, party_size: int) -> dict[str, Any]:
    initialize_database()
    slot = get_slot(slot_id)
    if slot is None or slot["storeId"] != store_id:
        raise ValueError("slot-not-found")
    if party_size > int(slot["capacity"]):
        raise OverflowError("slot-capacity")

    with connect() as connection:
        next_number = connection.execute("SELECT COUNT(*) + 1 FROM reservations").fetchone()[0]
        reservation_id = f"res-{next_number:04d}"
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
                slot["businessDate"],
                slot["startAt"],
                party_size,
                "BOOKED",
                slot["zoneName"],
                slot["interactionLabel"],
                slot["tableCode"],
                None,
            ),
        )
    return get_reservation_detail(reservation_id)


def get_reservation_detail(reservation_id: str) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT reservation_id, member_id, store_id, slot_id, business_date, slot_start_at, party_size,
                   status, zone_name, interaction_label, table_code, checked_in_at
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
    if row is None:
        raise KeyError(reservation_id)
    return {
        "reservationId": row["reservation_id"],
        "memberId": row["member_id"],
        "storeId": row["store_id"],
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
    initialize_database()
    query = """
        SELECT reservation_id, member_id, store_id, slot_id, business_date, slot_start_at, party_size,
               status, zone_name, interaction_label, table_code, checked_in_at
        FROM reservations
        WHERE tenant_id = ? AND member_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, member_id]
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    query += " ORDER BY slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "memberId": row["member_id"],
            "storeId": row["store_id"],
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


def cancel_reservation(member_id: str, reservation_id: str) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        scope = connection.execute(
            """
            SELECT member_id
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["member_id"] != member_id:
            raise PermissionError("wrong-member")
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        )
    return get_reservation_detail(reservation_id)


def list_staff_reservations(
    store_id: str,
    business_date: str,
    status_filter: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT r.reservation_id, r.member_id, m.nickname, r.store_id, r.slot_start_at, r.party_size,
               r.status, r.zone_name, r.interaction_label, r.table_code, r.checked_in_at
        FROM reservations r
        JOIN members m ON m.member_id = r.member_id
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


def check_in_reservation(store_id: str, reservation_id: str) -> dict[str, Any]:
    initialize_database()
    checked_in_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        scope = connection.execute(
            """
            SELECT store_id
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["store_id"] != store_id:
            raise PermissionError("wrong-store")
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CHECKED_IN', checked_in_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (checked_in_at, reservation_id, DEFAULT_TENANT_ID),
        )
    return get_reservation_detail(reservation_id)


def list_member_cats(member_id: str = DEFAULT_MEMBER_ID) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT cat_id, name, english_name, age_label, breed, gender, personality_tags_json, companion_summary
            FROM cats
            WHERE member_id = ?
            ORDER BY name
            """,
            (member_id,),
        ).fetchall()
    return [
        {
            "catId": row["cat_id"],
            "name": row["name"],
            "englishName": row["english_name"],
            "ageLabel": row["age_label"],
            "breed": row["breed"],
            "gender": row["gender"],
            "personalityTags": json.loads(row["personality_tags_json"]),
            "companionSummary": row["companion_summary"],
        }
        for row in rows
    ]


def list_member_recommendations(member_id: str = DEFAULT_MEMBER_ID) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT r.recommendation_id, r.store_id, r.headline, r.summary, r.detail,
                   r.reason_tags_json, s.store_name, s.district
            FROM recommendations r
            JOIN stores s ON s.store_id = r.store_id
            WHERE r.member_id = ?
            ORDER BY r.recommendation_id
            """,
            (member_id,),
        ).fetchall()
    return [
        {
            "recommendationId": row["recommendation_id"],
            "storeId": row["store_id"],
            "storeName": row["store_name"],
            "district": row["district"],
            "headline": row["headline"],
            "summary": row["summary"],
            "detail": row["detail"],
            "reasonTags": json.loads(row["reason_tags_json"]),
        }
        for row in rows
    ]
