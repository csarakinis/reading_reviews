"""
models/user.py — SQLAlchemy ORM model for a reading-list user.

`id`           — permanent unique identifier, never changes.
`email`        — login credential, unique across all users.
`display_name` — shown in the UI; purely cosmetic, no uniqueness required.
`session_id`   — set when the user logs in, cleared (NULL) on logout.
               Used only to authenticate in-flight requests via a cookie.

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

    # Permanent identity — never shown to the outside world, never changes.
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Login credential — unique and required.
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Display label — shown in the navbar; no uniqueness constraint needed.
    display_name: Mapped[str] = mapped_column(String, default="Reader")

    # Active session token — set on login, set to NULL on logout.
    # nullable=True means a user with session_id=None is simply logged out.
    session_id: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    books: Mapped[list["Book"]] = relationship("Book", back_populates="user", cascade="all, delete-orphan")
