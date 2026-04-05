"""
routers/deps.py — shared FastAPI dependencies.

get_current_user() is injected into every route that needs to know who is
making the request.  It reads the session cookie, creates a new User row the
first time it sees a new session, then returns the User object.

This is the right place to add authentication later: swap the cookie lookup
for a JWT decode or OAuth token validation and return the verified user.
"""
import uuid

from fastapi import Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.user_service import get_or_create_user

# One year expressed in seconds (accounts for leap years)
_SESSION_COOKIE_MAX_AGE = int(60 * 60 * 24 * 365.25)


def get_current_user(
    response: Response,
    db: Session = Depends(get_db),
    # FastAPI reads the named cookie from the incoming request automatically.
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> User:
    """Return the User for this browser session, creating one if it's new.

    On the very first visit the browser has no cookie, so we:
      1. Generate a new UUID to use as the session identifier.
      2. Set a long-lived cookie so the browser sends it on future requests.
      3. Create a User row tied to that session ID (or return the existing one).

    This pattern gives every visitor a persistent identity without requiring
    them to register — useful for a personal or small-group app.
    To add proper authentication, replace the cookie lookup here with a JWT
    decode or OAuth token validation.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key=settings.session_cookie_name,
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=_SESSION_COOKIE_MAX_AGE,
        )
    return get_or_create_user(db, session_id)
