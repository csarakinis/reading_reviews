import pytest


SAMPLE_BOOK = {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Classic",
    "status": "want_to_read",
    "total_pages": 180,
}


def test_list_books_empty(client):
    response = client.get("/api/v1/books/")
    assert response.status_code == 200
    data = response.json()
    assert data["books"] == []
    assert data["total"] == 0


def test_add_book(client):
    response = client.post("/api/v1/books/", json=SAMPLE_BOOK)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == SAMPLE_BOOK["title"]
    assert data["author"] == SAMPLE_BOOK["author"]
    assert data["status"] == "want_to_read"
    assert "id" in data
    assert "user_id" in data


def test_get_book(client):
    create_resp = client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


def test_get_book_not_found(client):
    response = client.get("/api/v1/books/nonexistent-id")
    assert response.status_code == 404


def test_update_book_status(client):
    create_resp = client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/books/{book_id}",
        json={"status": "reading", "date_started": "2024-01-15"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reading"
    assert data["date_started"] == "2024-01-15"


def test_update_book_with_review(client):
    create_resp = client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/books/{book_id}",
        json={"status": "completed", "rating": 5, "review": "Excellent book!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["review"] == "Excellent book!"


def test_rating_validation(client):
    response = client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "rating": 6},
    )
    assert response.status_code == 422


def test_delete_book(client):
    create_resp = client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/books/{book_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/books/{book_id}")
    assert get_resp.status_code == 404


def test_filter_books_by_status(client):
    client.post("/api/v1/books/", json={**SAMPLE_BOOK, "status": "want_to_read"})
    client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "title": "Book Two", "status": "reading"},
    )

    response = client.get("/api/v1/books/?status=want_to_read")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["books"][0]["status"] == "want_to_read"


def test_get_stats_empty(client):
    response = client.get("/api/v1/books/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 0
    assert data["by_status"] == {}
    assert data["average_rating"] is None


def test_get_stats_with_books(client):
    client.post("/api/v1/books/", json={**SAMPLE_BOOK, "status": "completed", "rating": 4})
    client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "title": "Book Two", "status": "reading"},
    )

    response = client.get("/api/v1/books/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 2
    assert "completed" in data["by_status"]
    assert "reading" in data["by_status"]
    assert data["average_rating"] == 4.0


def test_books_isolated_by_session(client):
    """Books added in one browser session must not appear in another."""
    client.post("/api/v1/books/", json=SAMPLE_BOOK)

    # Simulate a fresh browser by clearing the session cookie.
    # get_current_user will auto-create a new user with no books.
    client.cookies.clear()

    response = client.get("/api/v1/books/")
    assert response.json()["total"] == 0
