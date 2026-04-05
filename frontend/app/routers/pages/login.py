# login.py — login, registration, and logout routes.
import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api_client import APIClient
from app.config import settings
from app.routers.pages.common import templates

router = APIRouter()


def _set_session_cookie(response: RedirectResponse, session_id: str) -> None:
    """Helper: attach the session cookie to any RedirectResponse."""
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=settings.session_cookie_max_age,
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"errors": []})


@router.post("/login")
def login_submit(request: Request, email: str = Form(...)):
    """Look up the account by email, start a session, and redirect to the book list."""
    try:
        user = APIClient().login_user(email=email)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        msg = "No account found with that email." if status == 404 else f"Login failed: {e.response.text}"
        return templates.TemplateResponse(
            request, "login.html", {"errors": [msg], "email": email}, status_code=status
        )
    response = RedirectResponse(url="/books", status_code=303)
    _set_session_cookie(response, user["session_id"])
    return response


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"errors": []})


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    display_name: str = Form(default="Reader"),
):
    """Create a new account and immediately log in."""
    try:
        user = APIClient().register_user(email=email, display_name=display_name)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        msg = "An account with that email already exists." if status == 409 else f"Registration failed: {e.response.text}"
        return templates.TemplateResponse(
            request, "register.html",
            {"errors": [msg], "email": email, "display_name": display_name},
            status_code=status,
        )
    response = RedirectResponse(url="/books", status_code=303)
    _set_session_cookie(response, user["session_id"])
    return response


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@router.get("/logout")
def logout(request: Request):
    """Invalidate the session in the database, clear the cookie, redirect home."""
    session_id = request.cookies.get(settings.session_cookie_name)
    if session_id:
        try:
            APIClient(session_id=session_id).logout()
        except httpx.HTTPError:
            pass  # best-effort — still clear the cookie regardless
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key=settings.session_cookie_name)
    return response


def add_book_submit(
    request: Request,
    # Form(...) means the field is required — FastAPI returns 422 if it's missing.
    # Form(default="") means the field is optional; an empty string is fine.
    # The backend schema will coerce empty strings to None where appropriate.
    display_name: str = Form(...), 
    client: APIClient = Depends(make_client),
):
    user_data = {
        "display_name": display_name,
    }
    try:
        client.register_user(user_data)
        # Success: redirect to the home page so the user sees their new book.
        return RedirectResponse(url="/", status_code=303)
    except httpx.HTTPStatusError as e:
        # Failure (e.g. validation error from backend): re-render the form
        # with the original values pre-filled and an error message shown.
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "status_labels": STATUS_LABELS,
                "errors": [f"Failed to register user: {e.response.text}"],
                "form_data": user_data,  # keeps user's input so they don't retype everything
            },
            status_code=400,
        )
