# deps.py — FastAPI dependencies shared across frontend routes.
#
# A "dependency" in FastAPI is a function declared in a route's parameter list
# with Depends(...). FastAPI calls it automatically and passes the return value
# in. This keeps auth/session logic out of every individual route handler.
import uuid

from fastapi import Cookie, Request

from app.config import settings


def get_session_id(
    request: Request,
    # FastAPI reads the cookie from the browser request automatically.
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> str:
    """Return the current session ID, creating a new one if the browser has none."""
    if not session_id:
        # First visit: generate a unique ID for this browser.
        session_id = str(uuid.uuid4())
        # Store it on request.state so SessionCookieMiddleware can write the
        # Set-Cookie header once the route finishes.
        request.state.new_session_id = session_id
    return session_id
