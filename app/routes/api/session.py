from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from app.auth import COOKIE_NAME, create_session, get_required_session_actor


router = APIRouter()


class SessionLoginRequest(BaseModel):
    persona: str
    identifier: str | None = None
    accessCode: str | None = None
    verificationCode: str | None = None


@router.post("/api/session/login")
def login_session(payload: SessionLoginRequest, response: Response) -> dict[str, object]:
    session = create_session(
        payload.persona,
        identifier=payload.identifier,
        access_code=payload.accessCode,
        verification_code=payload.verificationCode,
    )
    response.set_cookie(
        COOKIE_NAME,
        session["sessionToken"],
        httponly=True,
        samesite="lax",
        path="/",
    )
    return session


@router.get("/api/session/me")
def get_session_me(actor=Depends(get_required_session_actor)) -> dict[str, object]:
    return actor.to_session_payload()


@router.post("/api/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_session(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
