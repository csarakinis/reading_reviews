from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.routers.pages.common import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login_submit():
    # POC: session is created automatically on first request.
    # Replace this handler with real authentication when ready.
    return RedirectResponse(url="/", status_code=303)
