import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.api_client import APIClient
from app.routers.pages.common import STATUS_LABELS, make_client, templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    status_filter: str | None = None,
    client: APIClient = Depends(make_client),
):
    try:
        books_data = client.get_books(status=status_filter)
        user = client.get_me()
    except httpx.HTTPError:
        books_data = {"books": [], "total": 0}
        user = {"display_name": "Reader"}

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "books": books_data["books"],
            "total": books_data["total"],
            "status_filter": status_filter,
            "status_labels": STATUS_LABELS,
            "user": user,
        },
    )
