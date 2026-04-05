from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from app.config import settings
from app.routers import pages_router


# Middleware runs on every request, before and after the route handler.
# This one's job: if a route created a brand-new session ID (stored in
# request.state by get_session_id), write it as a cookie in the response.
#
# Why middleware instead of inside the route?
# FastAPI only merges background response headers into plain dict responses.
# When a route returns a TemplateResponse or RedirectResponse directly, any
# cookies set on the injected `response` parameter are silently discarded.
# Setting the cookie here, after the route runs, is the reliable fix.
class SessionCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)  # run the actual route handler
        new_session_id = getattr(request.state, "new_session_id", None)
        if new_session_id:
            response.set_cookie(
                key=settings.session_cookie_name,
                value=new_session_id,
                httponly=True,   # JavaScript cannot read this cookie
                samesite="lax",  # sent on normal navigation, blocked on cross-site POST
                max_age=settings.session_cookie_max_age,
            )
        return response


# lifespan is called once when the app starts and once when it stops.
# Add startup/shutdown logic here (e.g. connecting to a cache) when needed.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    description="Frontend for the Reading Reviews tracking application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(SessionCookieMiddleware)

# Serve files from app/static/ at the /static URL path.
# CSS, JS, and images go in that folder and are referenced in templates as /static/...
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register all the HTML page routes (defined in routers/pages/).
app.include_router(pages_router)


# A simple health-check endpoint used by Docker Compose to know the app is ready.
@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}
