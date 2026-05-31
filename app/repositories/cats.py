import json
from typing import Any

from app.auth import DEFAULT_TENANT_ID
from app.core.constants import CAT_AVATAR_URLS, DEFAULT_MEMBER_ID
from app.db.connection import connect


def list_member_cats(member_id: str = DEFAULT_MEMBER_ID, store_id: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT c.cat_id, c.store_id, s.city_name, s.store_name, s.district,
               c.name, c.english_name, c.age_label, c.breed, c.gender,
               c.personality_tags_json, c.companion_summary
        FROM cats c
        JOIN stores s ON s.tenant_id = ? AND s.store_id = c.store_id
        WHERE c.member_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, member_id]
    if store_id:
        query += " AND c.store_id = ?"
        params.append(store_id)
    query += " ORDER BY s.city_name, s.store_name, c.name"
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "catId": row["cat_id"],
            "storeId": row["store_id"],
            "cityName": row["city_name"],
            "storeName": row["store_name"],
            "district": row["district"],
            "name": row["name"],
            "englishName": row["english_name"],
            "ageLabel": row["age_label"],
            "breed": row["breed"],
            "gender": row["gender"],
            "personalityTags": json.loads(row["personality_tags_json"]),
            "companionSummary": row["companion_summary"],
            "avatarUrl": CAT_AVATAR_URLS.get(row["cat_id"]),
        }
        for row in rows
    ]
