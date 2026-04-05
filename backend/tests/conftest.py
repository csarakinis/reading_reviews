import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

import app.database as db_module
from app.database import Base, get_db
from app.main import app

POSTGRES_IMAGE = "postgres:16-alpine"


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(POSTGRES_IMAGE) as postgres:
        yield postgres


@pytest.fixture(scope="session", autouse=True)
def patch_app_engine(postgres_container):
    """Redirect the module-level engine (used by lifespan create_all) to the
    testcontainer so no connection to the Docker Compose 'db' host is needed."""
    engine = create_engine(postgres_container.get_connection_url())
    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db(patch_app_engine):
    Base.metadata.create_all(bind=patch_app_engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=patch_app_engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=patch_app_engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
