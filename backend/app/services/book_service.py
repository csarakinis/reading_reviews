import uuid

from sqlalchemy.orm import Session

from app.models.book import Book, ReadingStatus
from app.schemas.book import BookCreate, BookUpdate


def get_books(
    db: Session,
    user_id: str,
    status: ReadingStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Book], int]:
    query = db.query(Book).filter(Book.user_id == user_id)
    if status:
        query = query.filter(Book.status == status)
    total = query.count()
    books = query.order_by(Book.created_at.desc()).offset(skip).limit(limit).all()
    return books, total


def get_book(db: Session, book_id: str, user_id: str) -> Book | None:
    return db.query(Book).filter(Book.id == book_id, Book.user_id == user_id).first()


def create_book(db: Session, book_in: BookCreate, user_id: str) -> Book:
    book = Book(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **book_in.model_dump(),
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book: Book, book_in: BookUpdate) -> Book:
    update_data = book_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    db.delete(book)
    db.commit()
