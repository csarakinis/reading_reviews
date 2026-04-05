"""
models/user.py — SQLAlchemy ORM model for a reading-list user.

A User is created automatically on first request using the browser session
cookie as a unique key (no login required).  All books belong to a user.

TODO: add fields like preferred_language, reading_goal_per_year, avatar_url.
TODO: when authentication is added, replace session_id with hashed password /
      OAuth provider fields and update routers/deps.py accordingly.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String, default="Reader")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    books: Mapped[list["Book"]] = relationship("Book", back_populates="user", cascade="all, delete-orphan")
