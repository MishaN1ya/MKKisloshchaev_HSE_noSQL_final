from datetime import datetime


GENRES = [
    "Боевик", "Комедия", "Драма", "Ужасы", "Фантастика",
    "Триллер", "Мелодрама", "Детектив", "Анимация", "Документальный",
]


def make_movie(movie_id: int, title: str, genre: str, year: int,
               director: str, duration_min: int, rating: float) -> dict:
    return {
        "movie_id": movie_id,
        "title": title,
        "genre": genre,
        "year": year,
        "director": director,
        "duration_min": duration_min,
        "rating": rating,
    }


def make_user(user_id: int, username: str, email: str,
              subscription: str, registered_at: str | None = None) -> dict:
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "subscription": subscription,
        "registered_at": registered_at or datetime.utcnow().isoformat(),
    }


def make_review(user_id: int, movie_id: int, rating: int,
                text: str, created_at: str | None = None) -> dict:
    return {
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": rating,
        "text": text,
        "created_at": created_at or datetime.utcnow().isoformat(),
    }
