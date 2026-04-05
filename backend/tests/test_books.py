import pytest


SAMPLE_BOOK = {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Classic",
    "status": "want_to_read",
    "total_pages": 180,
}


def test_books_require_auth(client):
    response = client.get("/api/v1/books/")
    assert response.status_code == 401


def test_list_books_empty(auth_client):
    response = auth_client.get("/api/v1/books/")
    assert response.status_code == 200
    data = response.json()
    assert data["books"] == []
    assert data["total"] == 0


def test_add_book(auth_client):
    response = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == SAMPLE_BOOK["title"]
    assert data["author"] == SAMPLE_BOOK["author"]
    assert data["status"] == "want_to_read"
    assert "id" in data
    assert "user_id" in data


def test_get_book(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = auth_client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


def test_get_book_not_found(auth_client):
    response = auth_client.get("/api/v1/books/nonexistent-id")
    assert response.status_code == 404


def test_update_book_status(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = auth_client.put(
        f"/api/v1/books/{book_id}",
        json={"status": "reading", "date_started": "2024-01-15"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reading"
    assert data["date_started"] == "2024-01-15"


def test_update_book_with_review(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = auth_client.put(
        f"/api/v1/books/{book_id}",
        json={"status": "completed", "rating": 5, "review": "Excellent book!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["review"] == "Excellent book!"


def test_rating_validation(auth_client):
    response = auth_client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "rating": 6},
    )
    assert response.status_code == 422


def test_create_book_accepts_optional_empty_strings(auth_client):
    response = auth_client.post(
        "/api/v1/books/",
        json={
            "title": "With Optional Fields",
            "author": "Reader",
            "genre": "",
            "isbn": "",
            "total_pages": "",
            "status": "want_to_read",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["genre"] is None
    assert data["isbn"] is None
    assert data["total_pages"] is None


def test_update_book_accepts_string_numbers_and_empty_optionals(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = auth_client.put(
        f"/api/v1/books/{book_id}",
        json={
            "total_pages": "250",
            "rating": "4",
            "review": "",
            "date_started": "2024-01-01",
            "date_completed": "",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_pages"] == 250
    assert data["rating"] == 4
    assert data["review"] is None
    assert data["date_started"] == "2024-01-01"
    assert data["date_completed"] is None


def test_update_book_rejects_completion_before_start(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    response = auth_client.put(
        f"/api/v1/books/{book_id}",
        json={
            "date_started": "2024-02-01",
            "date_completed": "2024-01-01",
        },
    )
    assert response.status_code == 422


def test_delete_book(auth_client):
    create_resp = auth_client.post("/api/v1/books/", json=SAMPLE_BOOK)
    book_id = create_resp.json()["id"]

    delete_resp = auth_client.delete(f"/api/v1/books/{book_id}")
    assert delete_resp.status_code == 204

    get_resp = auth_client.get(f"/api/v1/books/{book_id}")
    assert get_resp.status_code == 404


def test_filter_books_by_status(auth_client):
    auth_client.post("/api/v1/books/", json={**SAMPLE_BOOK, "status": "want_to_read"})
    auth_client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "title": "Book Two", "status": "reading"},
    )

    response = auth_client.get("/api/v1/books/?status=want_to_read")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["books"][0]["status"] == "want_to_read"



def test_get_stats_empty(auth_client):
    response = auth_client.get("/api/v1/books/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 0
    assert data["by_status"] == {}
    assert data["average_rating"] is None


def test_get_stats_with_books(auth_client):
    auth_client.post("/api/v1/books/", json={**SAMPLE_BOOK, "status": "completed", "rating": 4})
    auth_client.post(
        "/api/v1/books/",
        json={**SAMPLE_BOOK, "title": "Book Two", "status": "reading"},
    )

    response = auth_client.get("/api/v1/books/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 2
    assert "completed" in data["by_status"]
    assert "reading" in data["by_status"]
    assert data["average_rating"] == 4.0


def test_books_isolated_by_user(client):
    """Books added by one user must not appear when logged in as another user."""
    # Register user A and add a book.
    resp_a = client.post(
        "/api/v1/users/register",
        json={"email": "user_a@example.com", "display_name": "User A"},
    )
    client.cookies.set("reading_session", resp_a.json()["session_id"])
    client.post("/api/v1/books/", json=SAMPLE_BOOK)

    # Register user B with a fresh session — should see zero books.
    resp_b = client.post(
        "/api/v1/users/register",
        json={"email": "user_b@example.com", "display_name": "User B"},
    )
    client.cookies.set("reading_session", resp_b.json()["session_id"])

    response = client.get("/api/v1/books/")
    assert response.status_code == 200
    assert response.json()["total"] == 0
