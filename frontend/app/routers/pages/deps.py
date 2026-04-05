from fastapi import Form

from app.schemas import BookData


def parse_create_book_form(
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(default=""),
    isbn: str = Form(default=""),
    total_pages: str = Form(default=""),
    status: str = Form(default="want_to_read"),
) -> BookData:
    return BookData(
        title=title,
        author=author,
        genre=genre,
        isbn=isbn,
        total_pages=total_pages,
        status=status,
    )


def parse_update_book_form(
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
) -> BookData:
    return BookData(
        title=title,
        author=author,
        genre=genre,
        isbn=isbn,
        total_pages=total_pages,
        status=status,
        rating=rating,
        review=review,
        date_started=date_started,
        date_completed=date_completed,
    )
