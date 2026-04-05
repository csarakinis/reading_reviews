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
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> User:
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
