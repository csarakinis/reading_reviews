from datetime import date, datetime

from pydantic import BaseModel, field_validator, model_validator

from app.models.book import ReadingStatus


def _blank_to_none(v: object) -> object:
    """Strip whitespace and coerce empty strings to None."""
    if isinstance(v, str):
        stripped = v.strip()
        return stripped if stripped else None
    return v


class BookBase(BaseModel):
    title: str
    author: str
    genre: str | None = None
    isbn: str | None = None
    total_pages: int | None = None
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    rating: int | None = None
    review: str | None = None
    date_started: date | None = None
    date_completed: date | None = None

    @field_validator("title", "author", mode="before")
    @classmethod
    def normalize_required_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("genre", "isbn", "review", "total_pages", "rating", "date_started", "date_completed", mode="before")
    @classmethod
    def normalize_optional_fields(cls, v: object) -> object:
        return _blank_to_none(v)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("total_pages")
    @classmethod
    def validate_pages(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("Total pages must be a positive integer")
        return v

    @model_validator(mode="after")
    def validate_date_order(self) -> "BookBase":
        if (
            self.date_started is not None
            and self.date_completed is not None
            and self.date_completed < self.date_started
        ):
            raise ValueError("date_completed cannot be earlier than date_started")
        return self


BookCreate = BookBase


class BookUpdate(BookBase):
    title: str | None = None
    author: str | None = None
    status: ReadingStatus | None = None


class BookResponse(BookBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    books: list[BookResponse]
    total: int
