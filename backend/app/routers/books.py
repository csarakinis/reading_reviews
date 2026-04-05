"""
routers/books.py — REST endpoints for the reading list.

Pattern for every endpoint:
  1. Depend on get_current_user so every action is scoped to the caller.
  2. Call the matching service function (database layer).
  3. Return a Pydantic schema (automatic JSON serialisation).

Existing endpoints
------------------
GET    /api/v1/books/         list books, optional ?status= filter
POST   /api/v1/books/         add a book
GET    /api/v1/books/stats    Polars-computed reading statistics
GET    /api/v1/books/{id}     get one book
PUT    /api/v1/books/{id}     update a book (status, rating, review …)
DELETE /api/v1/books/{id}     remove a book

TODO: add GET /api/v1/books/search?q= for title/author search.
TODO: add GET /api/v1/books/export for CSV download using Polars.
"""
import httpx

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book, ReadingStatus
from app.models.user import User
from app.schemas.book import BookCreate, BookListResponse, BookResponse, BookUpdate, OLSearchResult
from app.services.book_service import create_book, delete_book, get_book, get_books, update_book
from app.transformations.reading_stats import compute_reading_stats
from app.routers.deps import get_current_user

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search-ol", response_model=list[OLSearchResult])
def search_open_library(
    q: str = Query(..., min_length=3, max_length=100),
    current_user: User = Depends(get_current_user),
):
    """Search Open Library API for books matching the query string."""
        
    OL_SEARCH_URL = "https://openlibrary.org/search.json"
    OL_HEADERS = {"User-Agent": "ReadingReviews (your@email.com)"}

    # Inside the endpoint:
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                OL_SEARCH_URL,
                params={
                    "q": q,
                    "fields": "title,author_name,cover_i,isbn,number_of_pages_median",
                    "limit": "10",
                },
                headers=OL_HEADERS,
            )
            resp.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for doc in resp.json().get("docs", []):
        cover_i = doc.get("cover_i")
        isbn_list = doc.get("isbn", [])
        author_list = doc.get("author_name", [])
        results.append(OLSearchResult(
            title=doc.get("title", "Unknown"),
            author=author_list[0] if author_list else "Unknown",
            isbn=isbn_list[0] if isbn_list else None,
            total_pages=doc.get("number_of_pages_median"),
            cover_url=f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else None,
        ))
    return results


@router.get("/", response_model=BookListResponse)
def list_books(
    status: ReadingStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    books, total = get_books(db, user_id=current_user.id, status=status, skip=skip, limit=limit)
    return BookListResponse(books=books, total=total)


@router.post("/", response_model=BookResponse, status_code=201)
def add_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_book(db, book_in, user_id=current_user.id)


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    books, _ = get_books(db, user_id=current_user.id, limit=10000)
    return compute_reading_stats(books)


@router.get("/{book_id}", response_model=BookResponse)
def get_single_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = get_book(db, book_id=book_id, user_id=current_user.id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_single_book(
    book_id: str,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = get_book(db, book_id=book_id, user_id=current_user.id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return update_book(db, book, book_in)


@router.delete("/{book_id}", status_code=204)
def delete_single_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = get_book(db, book_id=book_id, user_id=current_user.id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    delete_book(db, book)
