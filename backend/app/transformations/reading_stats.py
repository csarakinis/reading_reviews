from typing import Any

import polars as pl

from app.models.book import Book, ReadingStatus


def compute_reading_stats(books: list[Book]) -> dict[str, Any]:
    """Use Polars to compute reading statistics from a list of books."""
    if not books:
        return {
            "total_books": 0,
            "by_status": {},
            "average_rating": None,
            "top_genres": [],
            "books_completed_per_month": [],
        }

    data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "genre": b.genre or "Unknown",
            "status": b.status.value,
            "rating": b.rating,
            "date_completed": b.date_completed,
        }
        for b in books
    ]

    df = pl.DataFrame(data)

    total_books = len(df)

    by_status = (
        df.group_by("status")
        .agg(pl.len().alias("count"))
        .to_dicts()
    )
    by_status_dict = {row["status"]: row["count"] for row in by_status}

    rated_df = df.filter(pl.col("rating").is_not_null())
    average_rating = float(rated_df["rating"].mean()) if len(rated_df) > 0 else None

    top_genres = (
        df.filter(pl.col("genre") != "Unknown")
        .group_by("genre")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
        .head(5)
        .to_dicts()
    )

    completed_df = df.filter(
        (pl.col("status") == ReadingStatus.COMPLETED.value)
        & pl.col("date_completed").is_not_null()
    )

    books_per_month = []
    if len(completed_df) > 0:
        completed_with_date = completed_df.with_columns(
            pl.col("date_completed").cast(pl.Utf8).str.slice(0, 7).alias("year_month")
        )
        books_per_month = (
            completed_with_date.group_by("year_month")
            .agg(pl.len().alias("count"))
            .sort("year_month")
            .to_dicts()
        )

    return {
        "total_books": total_books,
        "by_status": by_status_dict,
        "average_rating": round(average_rating, 2) if average_rating is not None else None,
        "top_genres": top_genres,
        "books_completed_per_month": books_per_month,
    }
