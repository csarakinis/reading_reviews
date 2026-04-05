# login.py — stub login page.
#
# Currently this is just a placeholder. The session (and user row in the
# database) are already created automatically on the first request via
# get_session_id() + get_current_user(). To add real authentication:
#   1. Collect credentials in login.html (username + password, or OAuth).
#   2. Verify them in login_submit().
#   3. Store the authenticated user's ID in the session.
#   4. Guard protected routes by checking the session in get_session_id().
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
    # 303 See Other tells the browser to follow the redirect with a GET request.
    return RedirectResponse(url="/", status_code=303)
