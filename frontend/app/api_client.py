"""
api_client.py — thin HTTP wrapper for calling the backend API.

Every method maps one-to-one to a backend endpoint, forwards the browser's
session cookie, and raises httpx.HTTPStatusError on non-2xx responses (caught
in pages.py).

TODO: add retry logic or a timeout configuration if needed.
TODO: when the backend grows, add methods for search, export, etc.
"""
from typing import Any

import httpx

from app.config import settings

BACKEND_URL = settings.backend_url


class APIClient:
    """HTTP client for communicating with the backend API.

    Each public method maps one-to-one to a backend endpoint.
    The session cookie is forwarded with every request so the backend
    knows which user is making the call.
    """

    def __init__(self, session_id: str | None = None):
        self._session_id = session_id
        # Build the cookie jar once at construction time.
        self._cookies = {settings.session_cookie_name: session_id} if session_id else {}

    def _get_client(self) -> httpx.Client:
        # Creates a fresh httpx client for each request.
        # `with self._get_client() as client:` ensures the connection is
        # closed cleanly even if an exception occurs.
        return httpx.Client(
            base_url=BACKEND_URL,
            cookies=self._cookies,
            timeout=10.0,
        )

    def get_books(self, status: str | None = None) -> dict[str, Any]:
        # Optional ?status=... query param lets the backend filter by reading status.
        params = {}
        if status:
            params["status"] = status
        with self._get_client() as client:
            resp = client.get("/api/v1/books/", params=params)
            # raise_for_status() turns a 4xx/5xx response into an exception.
            # The calling route handler catches httpx.HTTPStatusError and shows an error page.
            resp.raise_for_status()
            return resp.json()

    def get_book(self, book_id: str) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.get(f"/api/v1/books/{book_id}")
            resp.raise_for_status()  # raises HTTPStatusError on 404, etc.
            return resp.json()

    def create_book(self, book_data: dict[str, Any]) -> dict[str, Any]:
        # json= serialises the dict to JSON and sets Content-Type: application/json.
        with self._get_client() as client:
            resp = client.post("/api/v1/books/", json=book_data)
            resp.raise_for_status()  # raises on 422 Unprocessable Entity if validation fails
            return resp.json()

    def update_book(self, book_id: str, book_data: dict[str, Any]) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.put(f"/api/v1/books/{book_id}", json=book_data)
            resp.raise_for_status()
            return resp.json()

    def delete_book(self, book_id: str) -> None:
        with self._get_client() as client:
            resp = client.delete(f"/api/v1/books/{book_id}")
            resp.raise_for_status()

    def get_stats(self) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.get("/api/v1/books/stats")
            resp.raise_for_status()
            return resp.json()
    
    def search_open_library(self, query: str) -> list[dict[str, Any]]:
        with self._get_client() as client:
            resp = client.get("/api/v1/books/search-ol", params={"q": query})
            resp.raise_for_status()
            return resp.json()

    def get_me(self) -> dict[str, Any]:
        """Return the profile for the currently logged-in user."""
        with self._get_client() as client:
            resp = client.get("/api/v1/users/me")
            resp.raise_for_status()
            return resp.json()

    def update_me(self, user_data: dict[str, Any]) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.put("/api/v1/users/me", json=user_data)
            resp.raise_for_status()
            return resp.json()

    def register_user(self, email: str, display_name: str = "Reader") -> dict[str, Any]:
        """Create a new account. Returns the user dict including the server-generated session_id."""
        with self._get_client() as client:
            resp = client.post("/api/v1/users/register", json={"email": email, "display_name": display_name})
            resp.raise_for_status()
            return resp.json()

    def login_user(self, email: str) -> dict[str, Any]:
        """Log in with an email. Returns the user dict including the session_id cookie value."""
        with self._get_client() as client:
            resp = client.post("/api/v1/users/login", json={"email": email})
            resp.raise_for_status()
            return resp.json()

    def logout(self) -> None:
        """Invalidate the current session in the database."""
        with self._get_client() as client:
            resp = client.post("/api/v1/users/logout")
            resp.raise_for_status()
