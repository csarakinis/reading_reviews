"""Server-rendered page routes split by feature.

Each sub-module owns one area of the UI and exposes a single `router` object.
They are all merged here into one combined router that main.py registers.

Order matters: login is registered first so /login takes precedence over any
wildcard routes that might be added later.
"""

from fastapi import APIRouter

from app.routers.pages.books import router as books_router
from app.routers.pages.home import router as home_router
from app.routers.pages.login import router as login_router
from app.routers.pages.stats import router as stats_router

router = APIRouter()
router.include_router(login_router)
router.include_router(home_router)
router.include_router(books_router)
router.include_router(stats_router)

__all__ = ["router"]
