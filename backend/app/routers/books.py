from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import ReadingStatus
from app.models.user import User
from app.schemas.book import BookCreate, BookListResponse, BookResponse, BookUpdate
from app.services.book_service import create_book, delete_book, get_book, get_books, update_book
from app.transformations.reading_stats import compute_reading_stats
from app.routers.deps import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


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
