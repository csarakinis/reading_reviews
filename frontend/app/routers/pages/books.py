# books.py — all CRUD routes for the Book resource.
#
# Each "edit" page follows the same pattern:
#   GET  /books/...  →  fetch data, render template
#   POST /books/...  →  validate + call backend, then EITHER redirect (success)
#                        OR re-render the same template with errors (failure)
#
# Redirects use status_code=303 (See Other) so the browser issues a GET for
# the next page. Without 303, hitting browser Back/Refresh would re-submit
# the form, which usually isn't what you want.
from urllib.parse import quote as url_quote

import httpx
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api_client import APIClient
from app.routers.pages.common import STATUS_LABELS, is_logged_in, make_client, templates

router = APIRouter()


@router.get("/books", response_class=HTMLResponse)
def book_list(
    request: Request,
    # Optional query parameter: /books?status_filter=reading shows only that status.
    status_filter: str | None = None,
    client: APIClient = Depends(make_client),
):
    # Guard: if the user hasn't selected a profile yet, send them to the login page.
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=303)

    try:
        books_data = client.get_books(status=status_filter)
        user = client.get_me()
    except httpx.HTTPError:
        # If the backend is unreachable, show an empty list rather than a crash page.
        books_data = {"books": [], "total": 0}
        user = {"display_name": "Reader"}

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "books": books_data["books"],
            "total": books_data["total"],
            "status_filter": status_filter,  # sent back so the template can highlight the active tab
            "status_labels": STATUS_LABELS,
            "user": user,
        },
    )


@router.get("/books/add", response_class=HTMLResponse)
def add_book_form(
    request: Request,
    client: APIClient = Depends(make_client),
):
    return templates.TemplateResponse(
        request,
        "add_book.html",
        {"status_labels": STATUS_LABELS, "errors": []},
    )


@router.post("/books/add")
def add_book_submit(
    request: Request,
    # Form(...) means the field is required — FastAPI returns 422 if it's missing.
    # Form(default="") means the field is optional; an empty string is fine.
    # The backend schema will coerce empty strings to None where appropriate.
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(default=""),
    isbn: str = Form(default=""),
    total_pages: str = Form(default=""),
    status: str = Form(default="want_to_read"),
    client: APIClient = Depends(make_client),
):
    book_data = {
        "title": title,
        "author": author,
        "genre": genre,
        "isbn": isbn,
        "total_pages": total_pages,
        "status": status,
    }
    try:
        client.create_book(book_data)
        # Success: redirect to the book list so the user sees their new book.
        return RedirectResponse(url="/books", status_code=303)
    except httpx.HTTPStatusError as e:
        # Failure (e.g. validation error from backend): re-render the form
        # with the original values pre-filled and an error message shown.
        return templates.TemplateResponse(
            request,
            "add_book.html",
            {
                "status_labels": STATUS_LABELS,
                "errors": [f"Failed to add book: {e.response.text}"],
                "form_data": book_data,  # keeps user's input so they don't retype everything
            },
            status_code=400,
        )


@router.get("/books/{book_id}", response_class=HTMLResponse)
def book_detail(
    book_id: str,
    request: Request,
    client: APIClient = Depends(make_client),
):
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        # 404 from the backend → show a not-found page.
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    except httpx.HTTPError:
        # Network / timeout error → also show a not-found page (503 would be more accurate,
        # but keeping it simple for now).
        return templates.TemplateResponse(request, "404.html", {}, status_code=503)

    return templates.TemplateResponse(
        request,
        "book_detail.html",
        {"book": book, "status_labels": STATUS_LABELS},
    )


@router.get("/books/{book_id}/edit", response_class=HTMLResponse)
def edit_book_form(
    book_id: str,
    request: Request,
    client: APIClient = Depends(make_client),
):
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

    return templates.TemplateResponse(
        request,
        "edit_book.html",
        {"book": book, "status_labels": STATUS_LABELS, "errors": []},
    )


@router.post("/books/{book_id}/edit")
def edit_book_submit(
    book_id: str,
    request: Request,
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
    client: APIClient = Depends(make_client),
):
    book_data = {
        "title": title,
        "author": author,
        "genre": genre,
        "isbn": isbn,
        "total_pages": total_pages,
        "status": status,
        "rating": rating,
        "review": review,
        "date_started": date_started,
        "date_completed": date_completed,
    }
    try:
        client.update_book(book_id, book_data)
        # url_quote ensures the book_id is safe for use in a URL path.
        return RedirectResponse(url=f"/books/{url_quote(book_id, safe='')}", status_code=303)
    except httpx.HTTPStatusError as e:
        # Inject book_id back into book_data so the template can build the form action URL.
        book_data["id"] = book_id
        return templates.TemplateResponse(
            request,
            "edit_book.html",
            {
                "book": book_data,
                "status_labels": STATUS_LABELS,
                "errors": [f"Failed to update book: {e.response.text}"],
            },
            status_code=400,
        )


@router.post("/books/{book_id}/delete")
def delete_book(
    book_id: str,
    client: APIClient = Depends(make_client),
):
    try:
        client.delete_book(book_id)
    except httpx.HTTPError:
        pass
    return RedirectResponse(url="/books", status_code=303)
