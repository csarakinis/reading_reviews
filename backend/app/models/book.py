"""
models/book.py — SQLAlchemy ORM model for a book in a reading list.

ReadingStatus is an enum column; its values drive the filter tabs in the UI.

TODO: add fields like cover_image_url, notes (list of timestamped notes),
      page_progress (current page), or a tags many-to-many relationship.
TODO: add a Series model and a foreign key here if you want series tracking.
"""
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReadingStatus(str, enum.Enum):
    """Inheriting from str makes the enum JSON-serialisable automatically."""

    WANT_TO_READ = "want_to_read"
    READING = "reading"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Book(Base):
    __tablename__ = "books"

    # Mapped[T] is the modern SQLAlchemy 2.x way to declare column types.
    # The Python type hint on the left and the mapped_column() on the right
    # must agree; SQLAlchemy uses both for type checking and schema generation.
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # ForeignKey("users.id") enforces referential integrity at the database level.
    # index=True creates a database index so lookups by user_id are fast.
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(500), nullable=False)
    genre: Mapped[str | None] = mapped_column(String(200), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus), default=ReadingStatus.WANT_TO_READ
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_started: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_completed: Mapped[date | None] = mapped_column(Date, nullable=True)
    # server_default=func.now() lets the database set these timestamps so they
    # are accurate even if multiple app instances are running.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationship() lets you access book.user to get the User object without
    # writing a JOIN query manually. SQLAlchemy handles the query for you.
    # back_populates="books" means User.books is the other side of this link.
    user: Mapped["User"] = relationship("User", back_populates="books")
