from fastapi import APIRouter, Depends

from app.auth import ensure_permission, get_required_session_actor, list_permission_profiles


router = APIRouter()


@router.get("/api/permissions/me")
def get_current_permission_profile(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return {
        "actorId": actor.actor_id,
        "displayName": actor.display_name,
        "role": actor.role,
        "permissions": list(actor.permissions),
        "scope": {
            "memberId": actor.member_id,
            "storeId": actor.store_id,
        },
    }


@router.get("/api/permissions/profiles")
def get_permission_profiles(actor=Depends(get_required_session_actor)) -> list[dict[str, object]]:
    ensure_permission(actor, "permissions.manage")
    return list_permission_profiles()
