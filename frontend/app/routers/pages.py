from typing import Any

import httpx
from fastapi import APIRouter, Cookie, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api_client import APIClient
from app.config import settings
from app.routers.deps import get_session_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

STATUS_LABELS = {
    "want_to_read": "Want to Read",
    "reading": "Currently Reading",
    "completed": "Completed",
    "abandoned": "Abandoned",
}


def _make_client(session_id: str) -> APIClient:
    return APIClient(session_id=session_id)


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    response: Response,
    status_filter: str | None = None,
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    try:
        books_data = client.get_books(status=status_filter)
        user = client.get_me()
    except httpx.HTTPError:
        books_data = {"books": [], "total": 0}
        user = {"display_name": "Reader"}

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "books": books_data["books"],
            "total": books_data["total"],
            "status_filter": status_filter,
            "status_labels": STATUS_LABELS,
            "user": user,
        },
    )


@router.get("/books/add", response_class=HTMLResponse)
def add_book_form(
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    return templates.TemplateResponse(
        request,
        "add_book.html",
        {"status_labels": STATUS_LABELS, "errors": []},
    )


@router.post("/books/add")
def add_book_submit(
    request: Request,
    response: Response,
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(default=""),
    isbn: str = Form(default=""),
    total_pages: str = Form(default=""),
    status: str = Form(default="want_to_read"),
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    book_data: dict[str, Any] = {
        "title": title,
        "author": author,
        "status": status,
    }
    if genre:
        book_data["genre"] = genre
    if isbn:
        book_data["isbn"] = isbn
    if total_pages.isdigit():
        book_data["total_pages"] = int(total_pages)

    try:
        client.create_book(book_data)
        return RedirectResponse(url="/", status_code=303)
    except httpx.HTTPStatusError as e:
        return templates.TemplateResponse(
            request,
            "add_book.html",
            {
                "status_labels": STATUS_LABELS,
                "errors": [f"Failed to add book: {e.response.text}"],
                "form_data": book_data,
            },
            status_code=400,
        )


@router.get("/books/{book_id}", response_class=HTMLResponse)
def book_detail(
    book_id: str,
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        return templates.TemplateResponse(
            request, "404.html", {}, status_code=404
        )
    except httpx.HTTPError:
        return templates.TemplateResponse(
            request, "404.html", {}, status_code=503
        )

    return templates.TemplateResponse(
        request,
        "book_detail.html",
        {
            "book": book,
            "status_labels": STATUS_LABELS,
        },
    )


@router.get("/books/{book_id}/edit", response_class=HTMLResponse)
def edit_book_form(
    book_id: str,
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        return templates.TemplateResponse(
            request, "404.html", {}, status_code=404
        )

    return templates.TemplateResponse(
        request,
        "edit_book.html",
        {
            "book": book,
            "status_labels": STATUS_LABELS,
            "errors": [],
        },
    )


@router.post("/books/{book_id}/edit")
def edit_book_submit(
    book_id: str,
    request: Request,
    response: Response,
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(default=""),
    isbn: str = Form(default=""),
    total_pages: str = Form(default=""),
    status: str = Form(default="want_to_read"),
    rating: str = Form(default=""),
    review: str = Form(default=""),
    date_started: str = Form(default=""),
    date_completed: str = Form(default=""),
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    book_data: dict[str, Any] = {
        "title": title,
        "author": author,
        "status": status,
        "genre": genre or None,
        "isbn": isbn or None,
        "review": review or None,
        "date_started": date_started or None,
        "date_completed": date_completed or None,
    }
    if total_pages.isdigit():
        book_data["total_pages"] = int(total_pages)
    if rating.isdigit() and 1 <= int(rating) <= 5:
        book_data["rating"] = int(rating)

    try:
        client.update_book(book_id, book_data)
        return RedirectResponse(url=f"/books/{book_id}", status_code=303)
    except httpx.HTTPStatusError as e:
        book = book_data
        book["id"] = book_id
        return templates.TemplateResponse(
            request,
            "edit_book.html",
            {
                "book": book,
                "status_labels": STATUS_LABELS,
                "errors": [f"Failed to update book: {e.response.text}"],
            },
            status_code=400,
        )


@router.post("/books/{book_id}/delete")
def delete_book(
    book_id: str,
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    try:
        client.delete_book(book_id)
    except httpx.HTTPError:
        pass
    return RedirectResponse(url="/", status_code=303)


@router.get("/stats", response_class=HTMLResponse)
def stats(
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    client = _make_client(session_id)
    try:
        stats_data = client.get_stats()
    except httpx.HTTPError:
        stats_data = {
            "total_books": 0,
            "by_status": {},
            "average_rating": None,
            "top_genres": [],
            "books_completed_per_month": [],
        }

    return templates.TemplateResponse(
        request,
        "stats.html",
        {
            "stats": stats_data,
            "status_labels": STATUS_LABELS,
        },
    )
