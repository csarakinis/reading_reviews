"""
database.py — SQLAlchemy engine, session factory, and declarative base.

All ORM models inherit from `Base`.  `get_db()` is a FastAPI dependency that
yields a database session for each request and closes it afterwards.

To add a new table: create a model in app/models/, import it in
app/models/__init__.py, then re-run the app (create_all handles migration
during development; use Alembic for production migrations).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that provides a database session per request.

    Using `yield` turns this into a context manager: the code before `yield`
    runs at the start of the request, the session is given to the route, then
    the code after `yield` (in the finally block) runs after the route returns
    — whether or not an exception was raised. This guarantees the connection is
    always returned to the pool.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
