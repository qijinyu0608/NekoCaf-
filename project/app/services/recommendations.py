import json
from typing import Any

from app.auth import DEFAULT_TENANT_ID
from app.core.constants import DEFAULT_DATE, DEFAULT_MEMBER_ID
from app.db.connection import connect
from app.repositories.cats import list_member_cats
from app.repositories.members import get_member
from app.repositories.slots import list_available_slots_for_stores
from app.repositories.stores import list_stores


def list_member_recommendations(
    member_id: str = DEFAULT_MEMBER_ID,
    *,
    business_date: str = DEFAULT_DATE,
    party_size: int = 2,
    city_name: str | None = None,
    store_id: str | None = None,
) -> list[dict[str, Any]]:
    with connect() as connection:
        seeded_rows = connection.execute(
            """
            SELECT r.recommendation_id, r.store_id, r.headline, r.summary, r.detail,
                   r.reason_tags_json, s.store_name, s.district
            FROM recommendations r
            JOIN stores s ON s.tenant_id = ? AND s.store_id = r.store_id
            WHERE r.member_id = ?
            ORDER BY r.recommendation_id
            """,
            (DEFAULT_TENANT_ID, member_id),
        ).fetchall()
    seeded = {
        row["store_id"]: {
            "recommendationId": row["recommendation_id"],
            "headline": row["headline"],
            "summary": row["summary"],
            "detail": row["detail"],
            "reasonTags": json.loads(row["reason_tags_json"]),
        }
        for row in seeded_rows
    }
    member = get_member(member_id)
    cats = list_member_cats(member_id)
    preference_terms = _recommendation_terms(member["preferences"], cats)
    scored: list[dict[str, Any]] = []
    stores = list_stores(city_name)
    if store_id:
        stores = [store for store in stores if store["storeId"] == store_id]
    slots_by_store = list_available_slots_for_stores(
        [str(store["storeId"]) for store in stores],
        business_date,
        party_size,
    )

    for store in stores:
        seeded_recommendation = seeded.get(str(store["storeId"]))
        haystack = " ".join(
            [
                str(store["cityName"]),
                str(store["storeName"]),
                str(store["district"]),
                str(store["summary"]),
                " ".join(str(tag) for tag in store["featureTags"]),
            ]
        )
        score = 58
        reasons: list[str] = []
        matched_terms = [term for term in preference_terms if term and term in haystack]
        if matched_terms:
            score += min(18, len(matched_terms) * 6)
            reasons.append(f"偏好命中：{'、'.join(matched_terms[:3])}")
        if seeded_recommendation:
            score += 14
            reasons.append("历史推荐记录匹配")
        available_slots = slots_by_store.get(str(store["storeId"]), [])
        if available_slots:
            score += min(10, len(available_slots) * 3)
            reasons.append(f"可约时段 {len(available_slots)} 个（{business_date} · {party_size}人）")
        else:
            reasons.append(f"当前筛选下暂无可约时段（{business_date} · {party_size}人）")
        if any(cat["storeId"] == store["storeId"] for cat in cats):
            score += 8
            reasons.append("常看猫咪所在门店")
        if not reasons:
            reasons.append("门店信息完整，适合探索")

        match_score = max(60, min(99, score))
        reason_tags = (
            seeded_recommendation["reasonTags"]
            if seeded_recommendation
            else list(store["featureTags"])[:3]
        )
        scored.append(
            {
                "recommendationId": seeded_recommendation["recommendationId"] if seeded_recommendation else f"score-{store['storeId']}",
                "storeId": store["storeId"],
                "storeName": store["storeName"],
                "district": store["district"],
                "headline": seeded_recommendation["headline"] if seeded_recommendation else "按偏好计算推荐",
                "summary": seeded_recommendation["summary"] if seeded_recommendation else f"NekoCafé {store['storeName']}",
                "detail": seeded_recommendation["detail"] if seeded_recommendation else f"{store['summary']} 结合你的到店偏好、门店标签和当前可约时段，适合作为备选门店。",
                "reasonTags": reason_tags,
                "matchScore": match_score,
                "scoreReasons": reasons[:3],
            }
        )
    scored.sort(key=lambda item: (-int(item["matchScore"]), str(item["storeName"])))
    return scored[:8]


def _recommendation_terms(preferences: list[str], cats: list[dict[str, Any]]) -> list[str]:
    term_map = {
        "window-seat": ["窗", "采光", "阳光"],
        "sunny-zone": ["阳光", "采光"],
        "calm-cats": ["安静", "轻声", "慢节奏"],
    }
    terms: list[str] = []
    for preference in preferences:
        terms.extend(term_map.get(preference, [preference]))
    for cat in cats:
        terms.extend(str(tag).replace("喜欢", "").replace("适合", "") for tag in cat["personalityTags"])
        terms.append(str(cat["companionSummary"]).replace("适合", ""))
    return list(dict.fromkeys(term.strip() for term in terms if term.strip()))
