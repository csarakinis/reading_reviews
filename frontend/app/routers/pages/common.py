# common.py — objects shared by every page router module.
#
# Import from here to avoid repeating the same setup in home.py, books.py, etc.
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from app.api_client import APIClient
from app.config import settings
from app.routers.deps import get_session_id

# Maps backend enum values to human-readable strings for the UI.
# Templates receive this dict and display e.g. STATUS_LABELS[book.status].
STATUS_LABELS = {
    "want_to_read": "Want to Read",
    "reading": "Currently Reading",
    "completed": "Completed",
    "abandoned": "Abandoned",
}

# The two fixed session IDs used by the login page.
# Each maps to a separate user row in the database.
LOGGED_IN_SESSIONS = {"user-1", "user-2"}

# Jinja2Templates loads .html files from this directory.
# Call templates.TemplateResponse(request, "file.html", context_dict) in routes.
templates = Jinja2Templates(directory="app/templates")


def is_logged_in(request: Request) -> bool:
    """Return True if the browser's session cookie belongs to a known user.

    Used both as a Python helper (imported by route modules) and as a Jinja2
    global so templates can call {{ is_logged_in(request) }} directly.
    """
    session = request.cookies.get(settings.session_cookie_name, "")
    return session in LOGGED_IN_SESSIONS


# Register is_logged_in as a global available in every template.
# This avoids having to pass `logged_in` in every route's context dict.
templates.env.globals["is_logged_in"] = is_logged_in


def make_client(session_id: str = Depends(get_session_id)) -> APIClient:
    """FastAPI dependency: return an APIClient wired to the current session.

    Declare `client: APIClient = Depends(make_client)` in any route parameter
    list and FastAPI will call this function and inject the result automatically.
    """
    return APIClient(session_id=session_id)
