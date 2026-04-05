from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    display_name: str = "Reader"


class UserCreate(UserBase):
    # The session cookie value is used as the unique identifier for a new user.
    session_id: str


class UserUpdate(BaseModel):
    # All fields are optional for updates — callers only send what changed.
    display_name: str | None = None


class UserResponse(UserBase):
    id: str
    session_id: str
    created_at: datetime
    updated_at: datetime

    # from_attributes=True lets Pydantic read field values from SQLAlchemy ORM
    # attributes directly (e.g. user.id) instead of requiring a plain dict.
    model_config = {"from_attributes": True}
