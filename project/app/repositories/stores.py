import json
import sqlite3
from typing import Any

from app.auth import DEFAULT_TENANT_ID
from app.core.constants import DEFAULT_CITY, STORE_STATUS_LABELS
from app.db.connection import connect


def list_cities() -> list[str]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT city_name
            FROM stores
            WHERE tenant_id = ?
            ORDER BY CASE WHEN city_name = ? THEN 0 ELSE 1 END, city_name
            """,
            (DEFAULT_TENANT_ID, DEFAULT_CITY),
        ).fetchall()
    return [row["city_name"] for row in rows]


def _store_from_row(row: sqlite3.Row) -> dict[str, Any]:
    operating_status = row["operating_status"]
    return {
        "storeId": row["store_id"],
        "cityName": row["city_name"],
        "storeName": row["store_name"],
        "district": row["district"],
        "summary": row["summary"],
        "featureTags": json.loads(row["feature_tags_json"]),
        "address": row["address"],
        "businessHours": row["business_hours"],
        "phone": row["phone"],
        "operatingStatus": operating_status,
        "operatingStatusLabel": STORE_STATUS_LABELS.get(operating_status, operating_status),
        "operatingNote": row["operating_note"],
        "isBookable": operating_status == "OPEN",
    }


def list_stores(
    city_name: str | None = None,
    *,
    include_paused: bool = False,
    search_query: str | None = None,
    operating_status: str | None = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT store_id, city_name, store_name, district, summary, feature_tags_json,
               address, business_hours, phone, operating_status, operating_note
        FROM stores
        WHERE tenant_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID]
    if not include_paused:
        query += " AND operating_status = 'OPEN'"
    if city_name:
        query += " AND city_name = ?"
        params.append(city_name)
    if search_query and search_query.strip():
        query += """
            AND (
                city_name LIKE ?
                OR store_name LIKE ?
                OR district LIKE ?
                OR address LIKE ?
                OR summary LIKE ?
            )
        """
        keyword = f"%{search_query.strip()}%"
        params.extend([keyword, keyword, keyword, keyword, keyword])
    if operating_status:
        normalized_status = operating_status.strip().upper()
        if normalized_status in STORE_STATUS_LABELS:
            query += " AND operating_status = ?"
            params.append(normalized_status)
    query += """
        ORDER BY
            CASE
                WHEN city_name = ? THEN 0
                WHEN city_name = '成都' THEN 1
                WHEN city_name = '杭州' THEN 2
                WHEN city_name = '南京' THEN 3
                WHEN city_name = '北京' THEN 4
                ELSE 5
            END,
            city_name,
            store_name
    """
    params.append(DEFAULT_CITY)
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [_store_from_row(row) for row in rows]


def get_store(store_id: str, *, include_paused: bool = False) -> dict[str, Any]:
    query = """
        SELECT store_id, city_name, store_name, district, summary, feature_tags_json,
               address, business_hours, phone, operating_status, operating_note
        FROM stores
        WHERE tenant_id = ? AND store_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, store_id]
    if not include_paused:
        query += " AND operating_status = 'OPEN'"
    with connect() as connection:
        row = connection.execute(query, params).fetchone()
    if row is None:
        raise KeyError(store_id)
    return _store_from_row(row)


def set_store_operating_status(
    store_id: str,
    operating_status: str,
    operating_note: str = "",
) -> dict[str, Any]:
    normalized_status = operating_status.strip().upper()
    if normalized_status not in STORE_STATUS_LABELS:
        raise ValueError("invalid-store-status")
    normalized_note = operating_note.strip()
    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE stores
            SET operating_status = ?, operating_note = ?
            WHERE tenant_id = ? AND store_id = ?
            """,
            (normalized_status, normalized_note, DEFAULT_TENANT_ID, store_id),
        )
        if cursor.rowcount == 0:
            raise KeyError(store_id)
    return get_store(store_id, include_paused=True)
