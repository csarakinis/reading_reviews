from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.user import UserAuthResponse, UserLoginRequest, UserRegisterRequest, UserResponse, UserUpdate
from app.services.user_service import create_user, end_session, get_user_by_email, login_user, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserAuthResponse, status_code=201)
def register(
    user_in: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Create a new account and immediately start a session.

    Returns UserAuthResponse which includes session_id so the frontend
    can store it as a cookie for subsequent authenticated requests.
    """
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    create_user(db, email=user_in.email, display_name=user_in.display_name)
    # Auto-login: generate a session immediately after creating the account.
    user, _ = login_user(db, user_in.email)
    return user


@router.post("/login", response_model=UserAuthResponse)
def login(
    user_in: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Log in with an email address and receive a session token.

    A new session_id is generated each time, invalidating any previous session
    (a user can only be logged in from one place at a time).
    """
    result = login_user(db, user_in.email)
    if not result:
        raise HTTPException(status_code=404, detail="No account found with that email")
    user, _ = result
    return user


@router.post("/logout", status_code=204)
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invalidate the current session by setting session_id to NULL.

    Uses the authenticated user's id (not the cookie value) so the lookup
    is stable regardless of the session token in use.
    """
    end_session(db, current_user.id)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(db, current_user, user_in)
