"""
services/user_service.py — database operations for users.

Four clear responsibilities:
  get_user_by_email()   — look up by login credential.
  get_user_by_session() — look up by active session token (used on every request).
  create_user()         — registration: insert a new row, no session yet.
  login_user()          — assign a fresh session_id to an existing user.
  end_session()         — logout: set session_id to NULL by user id.
  update_user()         — profile updates.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------

def get_user_by_email(db: Session, email: str) -> User | None:
    """Find a user by their email address (the login credential)."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_session(db: Session, session_id: str) -> User | None:
    """Find a user by their active session token.

    Returns None if the token doesn't match any row — either it was never
    issued or the user has logged out and the field was cleared.
    """
    return db.query(User).filter(User.session_id == session_id).first()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def create_user(db: Session, email: str, display_name: str = "Reader") -> User:
    """Insert a new user row. No session is created at this point."""
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        display_name=display_name,
        session_id=None,  # not logged in yet
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def login_user(db: Session, email: str) -> tuple[User, str] | None:
    """Find the user with this email and assign them a fresh session token.

    Returns (user, session_id) on success, or None if the email is not found.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    session_id = str(uuid.uuid4())
    user.session_id = session_id
    db.commit()
    db.refresh(user)
    return user, session_id


def end_session(db: Session, user_id: str) -> None:
    """Log out by setting session_id to NULL, looked up by the user's id.

    Using user_id (the permanent identifier) rather than session_id means
    the caller doesn't need access to the current cookie value — useful
    for admin actions or forced logouts.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.session_id = None
        db.commit()


# ---------------------------------------------------------------------------
# Profile updates
# ---------------------------------------------------------------------------

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Apply a partial update to an existing user's profile fields."""
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

    db.commit()
    db.refresh(user)
    return user
