from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.routers.pages.common import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def landing(request: Request):
    """Welcome / home page. No API call needed — just renders the landing template."""
    return templates.TemplateResponse(request, "landing.html", {})
