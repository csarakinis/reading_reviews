from datetime import datetime

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Request bodies (inbound)
# ---------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    """Fields a user submits when creating a new account."""
    email: str  # required — used as the login identifier
    display_name: str = "Reader"  # optional — shown in the UI


class UserLoginRequest(BaseModel):
    """Fields a user submits when logging in."""
    email: str


class UserUpdate(BaseModel):
    """Fields a user can change on their profile (all optional)."""
    display_name: str | None = None
    email: str | None = None


# ---------------------------------------------------------------------------
# Response bodies (outbound)
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Public user profile returned by GET /users/me and PUT /users/me."""
    id: str
    email: str
    display_name: str
    created_at: datetime
    updated_at: datetime

    # from_attributes=True lets Pydantic read values from SQLAlchemy ORM
    # attributes directly instead of requiring a plain dict.
    model_config = {"from_attributes": True}


class UserAuthResponse(UserResponse):
    """Extended response returned only by login and register.

    Includes session_id so the frontend can store it as a cookie.
    This field is intentionally absent from UserResponse (the public profile)
    because it is an internal session token, not user data.
    """
    session_id: str
