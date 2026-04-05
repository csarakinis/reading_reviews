import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.api_client import APIClient
from app.routers.pages.common import STATUS_LABELS, make_client, templates

router = APIRouter()


@router.get("/stats", response_class=HTMLResponse)
def stats(
    request: Request,
    client: APIClient = Depends(make_client),
):
    try:
        stats_data = client.get_stats()
    except httpx.HTTPError:
        # Provide zero-value fallback shapes so the template never crashes on
        # a missing key, even if the backend is temporarily unavailable.
        stats_data = {
            "total_books": 0,
            "by_status": {},
            "average_rating": None,
            "top_genres": [],
            "books_completed_per_month": [],
        }

    return templates.TemplateResponse(
        request,
        "stats.html",
        {
            "stats": stats_data,
            "status_labels": STATUS_LABELS,
        },
    )
