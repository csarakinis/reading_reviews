import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

MOCK_BOOKS = {
    "books": [
        {
            "id": "book-1",
            "user_id": "user-1",
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Fiction",
            "isbn": None,
            "total_pages": 300,
            "status": "reading",
            "rating": None,
            "review": None,
            "date_started": "2024-01-01",
            "date_completed": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ],
    "total": 1,
}

MOCK_USER = {
    "id": "user-1",
    "session_id": "test-session",
    "display_name": "Reader",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_STATS = {
    "total_books": 2,
    "by_status": {"reading": 1, "completed": 1},
    "average_rating": 4.0,
    "top_genres": [{"genre": "Fiction", "count": 2}],
    "books_completed_per_month": [{"year_month": "2024-01", "count": 1}],
}


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index_page(client):
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.get_books.return_value = MOCK_BOOKS
        instance.get_me.return_value = MOCK_USER
        response = client.get("/")
    assert response.status_code == 200
    assert b"Reading Reviews" in response.content
    assert b"Test Book" in response.content


def test_index_page_with_status_filter(client):
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.get_books.return_value = MOCK_BOOKS
        instance.get_me.return_value = MOCK_USER
        response = client.get("/?status_filter=reading")
    assert response.status_code == 200
    instance.get_books.assert_called_once_with(status="reading")


def test_add_book_form(client):
    response = client.get("/books/add")
    assert response.status_code == 200
    assert b"Add a Book" in response.content


def test_add_book_submit(client):
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.create_book.return_value = {**MOCK_BOOKS["books"][0]}
        response = client.post(
            "/books/add",
            data={"title": "New Book", "author": "New Author", "status": "want_to_read"},
            follow_redirects=False,
        )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_book_detail(client):
    book = MOCK_BOOKS["books"][0]
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.get_book.return_value = book
        response = client.get(f"/books/{book['id']}")
    assert response.status_code == 200
    assert b"Test Book" in response.content
    assert b"Test Author" in response.content


def test_stats_page(client):
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.get_stats.return_value = MOCK_STATS
        response = client.get("/stats")
    assert response.status_code == 200
    assert b"Reading Statistics" in response.content


def test_delete_book_redirects(client):
    with patch("app.routers.pages.APIClient") as MockClient:
        instance = MockClient.return_value
        instance.delete_book.return_value = None
        response = client.post("/books/book-1/delete", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
