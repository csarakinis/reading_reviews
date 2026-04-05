"""
services/user_service.py — database operations for users.

get_or_create_user() is the main entry point: called on every request via
the get_current_user dependency, it ensures every browser session maps to
exactly one User row in the database.

TODO: add lookup_by_email / lookup_by_username when authentication is added.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_session(db: Session, session_id: str) -> User | None:
    return db.query(User).filter(User.session_id == session_id).first()


def get_or_create_user(db: Session, session_id: str) -> User:
    user = get_user_by_session(db, session_id)
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            session_id=session_id,
            display_name="Reader",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        id=str(uuid.uuid4()),
        session_id=user_in.session_id,
        display_name=user_in.display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
