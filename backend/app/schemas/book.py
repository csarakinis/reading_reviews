from datetime import date, datetime

from pydantic import BaseModel, field_validator

from app.models.book import ReadingStatus


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


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    isbn: str | None = None
    total_pages: int | None = None
    status: ReadingStatus | None = None
    rating: int | None = None
    review: str | None = None
    date_started: date | None = None
    date_completed: date | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class BookResponse(BookBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    books: list[BookResponse]
    total: int
