from datetime import date, datetime

from pydantic import BaseModel, field_validator, model_validator

from app.models.book import ReadingStatus


def _blank_to_none(v: object) -> object:
    """Strip whitespace and coerce empty strings to None.

    HTML forms always send a string, including for optional fields the user
    left empty. This helper converts those empty strings into proper None
    values so Pydantic doesn't try to parse "" as an int or a date.
    """
    if isinstance(v, str):
        stripped = v.strip()
        return stripped if stripped else None
    return v


class BookBase(BaseModel):
    """Base schema shared by create and update operations.

    All validation logic lives here once. BookCreate and BookUpdate inherit
    from this class so they don't have to repeat the same validators.
    """

    title: str
    author: str
    genre: str | None = None
    isbn: str | None = None
    total_pages: int | None = None
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    rating: int | None = None
    review: str | None = None
    cover_url: str | None = None
    date_started: date | None = None
    date_completed: date | None = None

    # mode="before" means the validator runs before Pydantic's own type conversion.
    # This is needed so we can coerce "" -> None before Pydantic tries to parse
    # the value as an int or a date (which would raise a ValidationError).
    @field_validator("title", "author", mode="before")
    @classmethod
    def normalize_required_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("genre", "isbn", "review", "total_pages", "rating", "date_started", "date_completed", mode="before")
    @classmethod
    def normalize_optional_fields(cls, v: object) -> object:
        # Handles all optional fields in one decorator rather than repeating
        # the same validator seven times.
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
        # model_validator runs after all field validators, so both dates are
        # already coerced to `date` objects (or None) at this point.
        if (
            self.date_started is not None
            and self.date_completed is not None
            and self.date_completed < self.date_started
        ):
            raise ValueError("date_completed cannot be earlier than date_started")
        return self


# BookCreate is identical to BookBase — an alias rather than an empty subclass.
# To add create-only fields (e.g. a source URL) just change this to a class.
BookCreate = BookBase


class BookUpdate(BookBase):
    """Schema for partial updates. Title, author, and status become optional
    so callers only need to send the fields they want to change."""

    # Override required fields from BookBase to make them optional here.
    title: str | None = None
    author: str | None = None
    status: ReadingStatus | None = None


class BookResponse(BookBase):
    """Shape of a book returned by the API. Adds server-managed fields."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    # from_attributes=True lets Pydantic read values from SQLAlchemy model
    # attributes instead of requiring a plain dict.
    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    books: list[BookResponse]
    total: int


class OLSearchResult(BaseModel):
    title: str
    author: str
    isbn: str | None = None
    total_pages: int | None = None
    cover_url: str | None = None