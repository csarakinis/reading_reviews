# login.py — user selection and logout.
#
# Authentication here is a two-user POC: clicking "User 1" or "User 2" sets
# a fixed session cookie ("user-1" or "user-2"). The backend auto-creates a
# User row for each session ID the first time it sees it, so each user gets
# their own separate book list.
#
# To upgrade to real auth later:
#   1. Replace the two buttons with a username/password form.
#   2. Verify credentials in login_submit() and only set the cookie on success.
#   3. Use a UUID or opaque token as the cookie value instead of "user-1" etc.
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.routers.pages.common import LOGGED_IN_SESSIONS, templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login_submit(user_id: str = Form(...)):
    """Set the session cookie to the chosen user and redirect to their book list."""
    # Only allow the two known user IDs; ignore anything else.
    if user_id not in LOGGED_IN_SESSIONS:
        user_id = "user-1"

    # Set the cookie directly on the RedirectResponse.
    # (SessionCookieMiddleware only adds cookies created in get_session_id;
    # here we're creating the session ourselves, so we set it manually.)
    response = RedirectResponse(url="/books", status_code=303)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=user_id,
        httponly=True,
        samesite="lax",
        max_age=settings.session_cookie_max_age,
    )
    return response


@router.get("/logout")
def logout():
    """Clear the session cookie and return the user to the landing page."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key=settings.session_cookie_name)
    return response