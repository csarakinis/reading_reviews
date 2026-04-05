from dataclasses import dataclass


@dataclass
class BookData:
    title: str
    author: str
    genre: str = ""
    isbn: str = ""
    total_pages: str = ""
    status: str = "want_to_read"
    rating: str = ""
    review: str = ""
    date_started: str = ""
    date_completed: str = ""

    def for_create(self) -> dict[str, str]:
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "isbn": self.isbn,
            "total_pages": self.total_pages,
            "status": self.status,
        }

    def for_update(self) -> dict[str, str]:
        return {
            **self.for_create(),
            "rating": self.rating,
            "review": self.review,
            "date_started": self.date_started,
            "date_completed": self.date_completed,
        }
