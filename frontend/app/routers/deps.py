import uuid

from fastapi import Cookie, Request

from app.config import settings


def get_session_id(
    request: Request,
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        request.state.new_session_id = session_id
    return session_id
