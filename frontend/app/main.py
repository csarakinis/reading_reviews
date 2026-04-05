from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from app.config import settings
from app.routers import pages_router


class SessionCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        new_session_id = getattr(request.state, "new_session_id", None)
        if new_session_id:
            response.set_cookie(
                key=settings.session_cookie_name,
                value=new_session_id,
                httponly=True,
                samesite="lax",
                max_age=settings.session_cookie_max_age,
            )
        return response


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

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}
