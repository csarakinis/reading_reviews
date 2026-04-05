from dataclasses import asdict, dataclass
from typing import ClassVar

@dataclass(slots=True)
class BookData:
    CREATE_FIELDS: ClassVar[tuple[str, ...]] = (
        "title",
        "author",
        "genre",
        "isbn",
        "total_pages",
        "status",
    )
    UPDATE_ONLY_FIELDS: ClassVar[tuple[str, ...]] = (
        "rating",
        "review",
        "date_started",
        "date_completed",
    )

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
        return self._pick_fields(self.CREATE_FIELDS)

    def for_update(self) -> dict[str, str]:
        payload = self.for_create()
        payload.update(self._pick_fields(self.UPDATE_ONLY_FIELDS))
        return payload

    def _pick_fields(self, keys: tuple[str, ...]) -> dict[str, str]:
        raw = asdict(self)
        return {key: raw[key] for key in keys}
