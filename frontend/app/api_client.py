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
    """HTTP client for communicating with the backend API."""

    def __init__(self, session_id: str | None = None):
        self._session_id = session_id
        self._cookies = {settings.session_cookie_name: session_id} if session_id else {}

    def _get_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=BACKEND_URL,
            cookies=self._cookies,
            timeout=10.0,
        )

    def get_books(self, status: str | None = None) -> dict[str, Any]:
        params = {}
        if status:
            params["status"] = status
        with self._get_client() as client:
            resp = client.get("/api/v1/books/", params=params)
            resp.raise_for_status()
            return resp.json()

    def get_book(self, book_id: str) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.get(f"/api/v1/books/{book_id}")
            resp.raise_for_status()
            return resp.json()

    def create_book(self, book_data: dict[str, Any]) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.post("/api/v1/books/", json=book_data)
            resp.raise_for_status()
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

    def get_me(self) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.get("/api/v1/users/me")
            resp.raise_for_status()
            return resp.json()

    def update_me(self, user_data: dict[str, Any]) -> dict[str, Any]:
        with self._get_client() as client:
            resp = client.put("/api/v1/users/me", json=user_data)
            resp.raise_for_status()
            return resp.json()
