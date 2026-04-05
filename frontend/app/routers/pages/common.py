from fastapi import Depends
from fastapi.templating import Jinja2Templates

from app.api_client import APIClient
from app.routers.deps import get_session_id

# Shared labels used by templates and filters.
STATUS_LABELS = {
    "want_to_read": "Want to Read",
    "reading": "Currently Reading",
    "completed": "Completed",
    "abandoned": "Abandoned",
}

templates = Jinja2Templates(directory="app/templates")


def make_client(session_id: str = Depends(get_session_id)) -> APIClient:
    return APIClient(session_id=session_id)
