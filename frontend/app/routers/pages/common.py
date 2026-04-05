# common.py — objects shared by every page router module.
#
# Import from here to avoid repeating the same setup in home.py, books.py, etc.
from fastapi import Depends
from fastapi.templating import Jinja2Templates

from app.api_client import APIClient
from app.routers.deps import get_session_id

# Maps backend enum values to human-readable strings for the UI.
# Templates receive this dict and display e.g. STATUS_LABELS[book.status].
STATUS_LABELS = {
    "want_to_read": "Want to Read",
    "reading": "Currently Reading",
    "completed": "Completed",
    "abandoned": "Abandoned",
}

# Jinja2Templates loads .html files from this directory.
# Call templates.TemplateResponse(request, "file.html", context_dict) in routes.
templates = Jinja2Templates(directory="app/templates")


def make_client(session_id: str = Depends(get_session_id)) -> APIClient:
    """FastAPI dependency: return an APIClient wired to the current session.

    Declare `client: APIClient = Depends(make_client)` in any route parameter
    list and FastAPI will call this function and inject the result automatically.
    """
    return APIClient(session_id=session_id)
