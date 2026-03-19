from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27020"
DB_NAME = "online_cinema"


def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_db():
    client = get_client()
    return client[DB_NAME]


def insert_movie(db, movie: dict):
    return db.movies.insert_one(movie)


def find_movie(db, movie_id: int):
    return db.movies.find_one({"movie_id": movie_id}, {"_id": 0})


def find_movies(db, query: dict = None, limit: int = 20):
    return list(db.movies.find(query or {}, {"_id": 0}).limit(limit))


def update_movie(db, movie_id: int, fields: dict):
    return db.movies.update_one({"movie_id": movie_id}, {"$set": fields})


def delete_movie(db, movie_id: int):
    return db.movies.delete_one({"movie_id": movie_id})


def insert_user(db, user: dict):
    return db.users.insert_one(user)


def find_user(db, user_id: int):
    return db.users.find_one({"user_id": user_id}, {"_id": 0})


def find_users(db, query: dict = None, limit: int = 20):
    return list(db.users.find(query or {}, {"_id": 0}).limit(limit))


def update_user(db, user_id: int, fields: dict):
    return db.users.update_one({"user_id": user_id}, {"$set": fields})


def delete_user(db, user_id: int):
    return db.users.delete_one({"user_id": user_id})


def insert_review(db, review: dict):
    return db.reviews.insert_one(review)


def find_reviews_by_user(db, user_id: int):
    return list(db.reviews.find({"user_id": user_id}, {"_id": 0}))


def find_reviews_by_movie(db, movie_id: int):
    return list(db.reviews.find({"movie_id": movie_id}, {"_id": 0}))


def update_review(db, user_id: int, movie_id: int, fields: dict):
    return db.reviews.update_one(
        {"user_id": user_id, "movie_id": movie_id},
        {"$set": fields},
    )


def delete_review(db, user_id: int, movie_id: int):
    return db.reviews.delete_one({"user_id": user_id, "movie_id": movie_id})


def get_shard_distribution(db):
    result = {}
    for coll_name in ["movies", "users", "reviews"]:
        stats = db.command("collStats", coll_name)
        result[coll_name] = {
            "count": stats.get("count", 0),
            "size_bytes": stats.get("size", 0),
            "shards": stats.get("shards", {}),
        }
    return result
