import uuid

from fastapi import Cookie, Request, Response

from app.config import settings


def get_session_id(
    request: Request,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key=settings.session_cookie_name,
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 365,
        )
    return session_id
