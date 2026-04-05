from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    display_name: str = "Reader"


class UserCreate(UserBase):
    session_id: str


class UserUpdate(BaseModel):
    display_name: str | None = None


class UserResponse(UserBase):
    id: str
    session_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
