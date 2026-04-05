"""Server-rendered page routes split by feature."""

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
