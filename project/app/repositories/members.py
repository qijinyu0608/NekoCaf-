import json
from typing import Any

from app.core.constants import DEFAULT_MEMBER_ID
from app.db.connection import connect


def get_member(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
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


def update_member_profile(
    member_id: str,
    *,
    nickname: str,
    mobile_masked: str,
    preferences: list[str],
) -> dict[str, Any]:
    normalized_nickname = nickname.strip() or "Momo"
    normalized_mobile = mobile_masked.strip() or "138****1024"
    normalized_preferences = [item.strip() for item in preferences if item.strip()]
    if not normalized_preferences:
        normalized_preferences = ["安静猫咪", "靠窗座"]

    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE members
            SET nickname = ?, mobile_masked = ?, avatar_label = ?, preferences_json = ?
            WHERE member_id = ?
            """,
            (
                normalized_nickname,
                normalized_mobile,
                normalized_nickname[:2].upper(),
                json.dumps(normalized_preferences),
                member_id,
            ),
        )
        if cursor.rowcount == 0:
            raise KeyError(member_id)

    return get_member(member_id)


def get_point_account(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
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
