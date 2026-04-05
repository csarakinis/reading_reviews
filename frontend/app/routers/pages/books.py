from urllib.parse import quote as url_quote

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api_client import APIClient
from app.routers.pages.deps import parse_create_book_form, parse_update_book_form
from app.routers.pages.common import STATUS_LABELS, make_client, templates
from app.schemas import BookData

router = APIRouter()


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
    book: BookData = Depends(parse_create_book_form),
    client: APIClient = Depends(make_client),
):
    book_data = book.for_create()

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
    client: APIClient = Depends(make_client),
):
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    except httpx.HTTPError:
        return templates.TemplateResponse(request, "404.html", {}, status_code=503)

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
    client: APIClient = Depends(make_client),
):
    try:
        book = client.get_book(book_id)
    except httpx.HTTPStatusError:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

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
    book: BookData = Depends(parse_update_book_form),
    client: APIClient = Depends(make_client),
):
    book_data = book.for_update()

    try:
        client.update_book(book_id, book_data)
        return RedirectResponse(url=f"/books/{url_quote(book_id, safe='')}", status_code=303)
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
    client: APIClient = Depends(make_client),
):
    try:
        client.delete_book(book_id)
    except httpx.HTTPError:
        pass
    return RedirectResponse(url="/", status_code=303)
