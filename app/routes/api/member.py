from fastapi import APIRouter, Depends, Query

from app.auth import ensure_permission, get_required_session_actor
from app.core.constants import DEFAULT_DATE, DEFAULT_MEMBER_ID
from app.repositories.cats import list_member_cats
from app.repositories.members import get_member, get_point_account
from app.repositories.stores import list_cities
from app.services.recommendations import list_member_recommendations


router = APIRouter()


@router.get("/api/member/me")
def get_current_member(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "member.profile.read.self")
    return get_member(actor.member_id or DEFAULT_MEMBER_ID)


@router.get("/api/member/me/points")
def get_current_points(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    ensure_permission(actor, "member.points.read.self")
    return get_point_account(actor.member_id or DEFAULT_MEMBER_ID)


@router.get("/api/cats/me")
def get_current_cats(
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "cat.read.self")
    return list_member_cats(actor.member_id or DEFAULT_MEMBER_ID, store_id)


@router.get("/api/recommendations/me")
def get_current_recommendations(
    business_date: str = Query(default=DEFAULT_DATE, alias="date"),
    party_size: int = Query(default=2, alias="partySize", ge=1),
    city_name: str | None = Query(default=None, alias="city"),
    store_id: str | None = Query(default=None, alias="storeId"),
    actor=Depends(get_required_session_actor),
) -> list[dict[str, object]]:
    ensure_permission(actor, "recommendation.read.self")
    active_city = city_name if city_name in list_cities() else None
    return list_member_recommendations(
        actor.member_id or DEFAULT_MEMBER_ID,
        business_date=business_date,
        party_size=party_size,
        city_name=active_city,
        store_id=store_id,
    )
