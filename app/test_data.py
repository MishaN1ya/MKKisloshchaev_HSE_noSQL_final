import random
from app.models import make_movie, make_user, make_review, GENRES

DIRECTORS = [
    "Кристофер Нолан", "Квентин Тарантино", "Мартин Скорсезе",
    "Стивен Спилберг", "Дэвид Финчер", "Ридли Скотт",
    "Денис Вильнёв", "Гай Ричи", "Вес Андерсон",
    "Андрей Тарковский", "Тим Бёртон", "Джеймс Кэмерон",
]

MOVIE_TITLES = [
    "Тёмный рассвет", "Последний рубеж", "Город теней", "Звёздный путь",
    "Ледяной шторм", "Огненный закат", "Тихая гавань", "Багровый пик",
    "Стальной кулак", "Золотой век", "Чёрная метка", "Белый шум",
    "Серебряный клинок", "Хрустальный замок", "Лунный свет",
    "Дневной дозор", "Ночной экспресс", "Призрачный гонщик",
    "Бриллиантовая рука", "Операция Ы", "Ирония судьбы",
    "Кавказская пленница", "Джентльмены удачи", "Двенадцать стульев",
    "Мастер и Маргарита", "Сталкер", "Солярис", "Зеркало",
    "Левиафан", "Нелюбовь", "Возвращение", "Остров",
    "Брат", "Питер FM", "Метро", "Экипаж", "Т-34",
    "Движение вверх", "Легенда №17", "Время первых",
    "Космический рейс", "Параллельные миры", "Обратный отсчёт",
    "Формула мечты", "Тайна перевала", "Ветер перемен",
    "Северное сияние", "Восточный ветер", "Западный фронт",
    "Южный крест", "Полярная звезда",
]

FIRST_NAMES = [
    "Александр", "Дмитрий", "Максим", "Иван", "Артём", "Никита", "Михаил",
    "Даниил", "Егор", "Андрей", "Кирилл", "Илья", "Алексей", "Роман",
    "Сергей", "Анна", "Мария", "Елена", "Ольга", "Наталья",
    "Екатерина", "Дарья", "Полина", "Алиса", "Виктория",
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Козлов", "Новиков", "Морозов",
    "Волков", "Соколов", "Лебедев", "Кузнецов", "Попов", "Васильев",
    "Зайцев", "Павлов", "Семёнов", "Голубев", "Виноградов", "Богданов",
    "Воробьёв", "Фёдоров",
]

SUBSCRIPTIONS = ["free", "standard", "premium"]

REVIEW_TEXTS = [
    "Отличный фильм, рекомендую!",
    "Средненько, ожидал большего.",
    "Шедевр! Смотрел на одном дыхании.",
    "Скучновато, но актёры хорошие.",
    "Не понравилось, слишком затянуто.",
    "Один из лучших фильмов года!",
    "Нормально, можно посмотреть один раз.",
    "Потрясающая режиссура и операторская работа.",
    "Сюжет предсказуемый, но снято красиво.",
    "Пересматриваю уже третий раз!",
    "Не мой жанр, но объективно неплохо.",
    "Финал разочаровал.",
    "Лучшее, что я видел за последнее время.",
    "Актёрская игра на высоте.",
    "Слабый сценарий портит всё впечатление.",
]


def generate_movies(n: int = 50) -> list[dict]:
    movies = []
    for i in range(1, n + 1):
        idx = (i - 1) % len(MOVIE_TITLES)
        suffix = f" {i // len(MOVIE_TITLES) + 1}" if i > len(MOVIE_TITLES) else ""
        title = MOVIE_TITLES[idx] + suffix
        movies.append(make_movie(
            movie_id=i,
            title=title,
            genre=random.choice(GENRES),
            year=random.randint(1990, 2025),
            director=random.choice(DIRECTORS),
            duration_min=random.randint(80, 180),
            rating=round(random.uniform(4.0, 9.5), 1),
        ))
    return movies


def generate_users(n: int = 1000) -> list[dict]:
    users = []
    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        username = f"{first.lower()}_{last.lower()}_{i}"
        email = f"{username}@cinema.ru"
        users.append(make_user(
            user_id=i,
            username=username,
            email=email,
            subscription=random.choice(SUBSCRIPTIONS),
        ))
    return users


def generate_reviews(users: list[dict], movies: list[dict],
                     avg_per_user: int = 5) -> list[dict]:
    reviews = []
    movie_ids = [m["movie_id"] for m in movies]
    for u in users:
        n_reviews = random.randint(1, avg_per_user + 3)
        chosen_movies = random.sample(movie_ids, min(n_reviews, len(movie_ids)))
        for mid in chosen_movies:
            reviews.append(make_review(
                user_id=u["user_id"],
                movie_id=mid,
                rating=random.randint(1, 10),
                text=random.choice(REVIEW_TEXTS),
            ))
    return reviews


def fill_database(db, n_users: int = 1000, n_movies: int = 50):
    print(f"Генерация {n_movies} фильмов...")
    movies = generate_movies(n_movies)

    print(f"Генерация {n_users} пользователей...")
    users = generate_users(n_users)

    print("Генерация отзывов...")
    reviews = generate_reviews(users, movies)

    print(f"Вставка {len(movies)} фильмов...")
    db.movies.insert_many(movies, ordered=False)

    print(f"Вставка {len(users)} пользователей...")
    db.users.insert_many(users, ordered=False)

    print(f"Вставка {len(reviews)} отзывов...")
    db.reviews.insert_many(reviews, ordered=False)

    print(f"\nГотово! Фильмов: {len(movies)}, Пользователей: {len(users)}, "
          f"Отзывов: {len(reviews)}")
