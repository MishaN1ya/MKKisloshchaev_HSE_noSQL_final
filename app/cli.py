import json
from app.database import (
    get_db,
    insert_movie, find_movie, find_movies, update_movie, delete_movie,
    insert_user, find_user, find_users, update_user, delete_user,
    insert_review, find_reviews_by_user, find_reviews_by_movie,
    update_review, delete_review, get_shard_distribution,
)
from app.models import make_movie, make_user, make_review
from app.test_data import fill_database


def print_json(data):
    if isinstance(data, list):
        for item in data:
            item.pop("_id", None)
            print(json.dumps(item, ensure_ascii=False, indent=2, default=str))
            print("-" * 40)
        print(f"Найдено записей: {len(data)}")
    elif isinstance(data, dict):
        data.pop("_id", None)
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        print(data)


def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число.")


def menu_movies(db):
    while True:
        print("\n--- Фильмы ---")
        print("1. Добавить фильм")
        print("2. Найти фильм по ID")
        print("3. Список фильмов")
        print("4. Обновить фильм")
        print("5. Удалить фильм")
        print("0. Назад")

        choice = input("Выбор: ").strip()
        if choice == "1":
            mid = input_int("movie_id: ")
            title = input("Название: ").strip()
            genre = input("Жанр: ").strip()
            year = input_int("Год: ")
            director = input("Режиссёр: ").strip()
            duration = input_int("Длительность (мин): ")
            rating = float(input("Рейтинг (0-10): "))
            doc = make_movie(mid, title, genre, year, director, duration, rating)
            insert_movie(db, doc)
            print("Фильм добавлен.")
        elif choice == "2":
            mid = input_int("movie_id: ")
            result = find_movie(db, mid)
            print_json(result) if result else print("Не найден.")
        elif choice == "3":
            genre = input("Фильтр по жанру (Enter — все): ").strip()
            query = {"genre": genre} if genre else {}
            print_json(find_movies(db, query))
        elif choice == "4":
            mid = input_int("movie_id: ")
            field = input("Поле для обновления: ").strip()
            value = input("Новое значение: ").strip()
            if field in ("year", "duration_min"):
                value = int(value)
            elif field == "rating":
                value = float(value)
            res = update_movie(db, mid, {field: value})
            print(f"Обновлено: {res.modified_count}")
        elif choice == "5":
            mid = input_int("movie_id: ")
            res = delete_movie(db, mid)
            print(f"Удалено: {res.deleted_count}")
        elif choice == "0":
            break


def menu_users(db):
    while True:
        print("\n--- Пользователи ---")
        print("1. Добавить пользователя")
        print("2. Найти пользователя по ID")
        print("3. Список пользователей")
        print("4. Обновить пользователя")
        print("5. Удалить пользователя")
        print("0. Назад")

        choice = input("Выбор: ").strip()
        if choice == "1":
            uid = input_int("user_id: ")
            username = input("Имя пользователя: ").strip()
            email = input("Email: ").strip()
            sub = input("Подписка (free/standard/premium): ").strip()
            doc = make_user(uid, username, email, sub)
            insert_user(db, doc)
            print("Пользователь добавлен.")
        elif choice == "2":
            uid = input_int("user_id: ")
            result = find_user(db, uid)
            print_json(result) if result else print("Не найден.")
        elif choice == "3":
            sub = input("Фильтр по подписке (Enter — все): ").strip()
            query = {"subscription": sub} if sub else {}
            print_json(find_users(db, query))
        elif choice == "4":
            uid = input_int("user_id: ")
            field = input("Поле для обновления: ").strip()
            value = input("Новое значение: ").strip()
            res = update_user(db, uid, {field: value})
            print(f"Обновлено: {res.modified_count}")
        elif choice == "5":
            uid = input_int("user_id: ")
            res = delete_user(db, uid)
            print(f"Удалено: {res.deleted_count}")
        elif choice == "0":
            break


def menu_reviews(db):
    while True:
        print("\n--- Отзывы ---")
        print("1. Добавить отзыв")
        print("2. Отзывы пользователя")
        print("3. Отзывы на фильм")
        print("4. Обновить оценку")
        print("5. Удалить отзыв")
        print("0. Назад")

        choice = input("Выбор: ").strip()
        if choice == "1":
            uid = input_int("user_id: ")
            mid = input_int("movie_id: ")
            rating = input_int("Оценка (1-10): ")
            text = input("Текст отзыва: ").strip()
            doc = make_review(uid, mid, rating, text)
            insert_review(db, doc)
            print("Отзыв добавлен.")
        elif choice == "2":
            uid = input_int("user_id: ")
            print_json(find_reviews_by_user(db, uid))
        elif choice == "3":
            mid = input_int("movie_id: ")
            print_json(find_reviews_by_movie(db, mid))
        elif choice == "4":
            uid = input_int("user_id: ")
            mid = input_int("movie_id: ")
            rating = input_int("Новая оценка (1-10): ")
            res = update_review(db, uid, mid, {"rating": rating})
            print(f"Обновлено: {res.modified_count}")
        elif choice == "5":
            uid = input_int("user_id: ")
            mid = input_int("movie_id: ")
            res = delete_review(db, uid, mid)
            print(f"Удалено: {res.deleted_count}")
        elif choice == "0":
            break


def main():
    db = get_db()

    while True:
        print("\n========== Онлайн-Кинотеатр ==========")
        print("1. Фильмы")
        print("2. Пользователи")
        print("3. Отзывы")
        print("4. Заполнить БД тестовыми данными")
        print("5. Статистика шардинга")
        print("0. Выход")

        choice = input("Выбор: ").strip()
        if choice == "1":
            menu_movies(db)
        elif choice == "2":
            menu_users(db)
        elif choice == "3":
            menu_reviews(db)
        elif choice == "4":
            n = input_int("Количество пользователей (по умолч. 1000): ") or 1000
            fill_database(db, n_users=n)
        elif choice == "5":
            dist = get_shard_distribution(db)
            print_json(dist)
        elif choice == "0":
            print("Выход.")
            break


if __name__ == "__main__":
    main()
