"""
routers/deps.py — shared FastAPI dependencies.

get_current_user() is injected into every route that needs an authenticated user.
It reads the session cookie, looks up the matching User row, and raises 401 if
the cookie is missing or the session has been invalidated (logged out).
"""
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.user_service import get_user_by_session


def get_current_user(
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> User:
    """Return the authenticated User for this request, or raise 401.

    Users are never auto-created here. Anonymous requests are rejected so
    protected routes always receive a real, explicitly-logged-in User.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session not found or expired — please log in again")
    return user
