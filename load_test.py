import os
import time
import random
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymongo import MongoClient
from app.models import make_user, make_review, GENRES

MONGO_URI = "mongodb://localhost:27020"
DB_NAME = "online_cinema"
RESULTS_DIR = "results"


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def op_insert_user(db, uid: int):
    doc = make_user(uid, f"loadtest_user_{uid}", f"lt_{uid}@test.ru", "free")
    db.users.insert_one(doc)


def op_read_user(db, uid: int):
    db.users.find_one({"user_id": uid})


def op_read_movies_by_genre(db):
    genre = random.choice(GENRES)
    list(db.movies.find({"genre": genre}).limit(10))


def op_update_user(db, uid: int):
    sub = random.choice(["free", "standard", "premium"])
    db.users.update_one({"user_id": uid}, {"$set": {"subscription": sub}})


def op_insert_review(db, uid: int):
    doc = make_review(uid, random.randint(1, 50), random.randint(1, 10), "load test review")
    db.reviews.insert_one(doc)


def benchmark(name: str, func, n_operations: int, n_threads: int = 10):
    latencies = []

    def worker(i):
        db = get_db()
        start = time.perf_counter()
        func(db, i)
        elapsed = time.perf_counter() - start
        return elapsed

    total_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = {pool.submit(worker, i): i for i in range(1, n_operations + 1)}
        for f in as_completed(futures):
            try:
                latencies.append(f.result())
            except Exception as e:
                latencies.append(None)

    total_time = time.perf_counter() - total_start
    valid = [l for l in latencies if l is not None]
    errors = len(latencies) - len(valid)

    result = {
        "name": name,
        "operations": n_operations,
        "threads": n_threads,
        "total_time_s": round(total_time, 3),
        "throughput_ops": round(n_operations / total_time, 1),
        "avg_latency_ms": round(statistics.mean(valid) * 1000, 2) if valid else 0,
        "p50_latency_ms": round(statistics.median(valid) * 1000, 2) if valid else 0,
        "p95_latency_ms": round(sorted(valid)[int(len(valid) * 0.95)] * 1000, 2) if valid else 0,
        "p99_latency_ms": round(sorted(valid)[int(len(valid) * 0.99)] * 1000, 2) if valid else 0,
        "max_latency_ms": round(max(valid) * 1000, 2) if valid else 0,
        "errors": errors,
    }

    print(f"\n[{name}]")
    for k, v in result.items():
        if k != "name":
            print(f"  {k}: {v}")

    return result, valid


def benchmark_read_no_id(name: str, func, n_operations: int, n_threads: int = 10):
    latencies = []

    def worker(_):
        db = get_db()
        start = time.perf_counter()
        func(db)
        elapsed = time.perf_counter() - start
        return elapsed

    total_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = {pool.submit(worker, i): i for i in range(n_operations)}
        for f in as_completed(futures):
            try:
                latencies.append(f.result())
            except Exception:
                latencies.append(None)

    total_time = time.perf_counter() - total_start
    valid = [l for l in latencies if l is not None]
    errors = len(latencies) - len(valid)

    result = {
        "name": name,
        "operations": n_operations,
        "threads": n_threads,
        "total_time_s": round(total_time, 3),
        "throughput_ops": round(n_operations / total_time, 1),
        "avg_latency_ms": round(statistics.mean(valid) * 1000, 2) if valid else 0,
        "p50_latency_ms": round(statistics.median(valid) * 1000, 2) if valid else 0,
        "p95_latency_ms": round(sorted(valid)[int(len(valid) * 0.95)] * 1000, 2) if valid else 0,
        "p99_latency_ms": round(sorted(valid)[int(len(valid) * 0.99)] * 1000, 2) if valid else 0,
        "max_latency_ms": round(max(valid) * 1000, 2) if valid else 0,
        "errors": errors,
    }

    print(f"\n[{name}]")
    for k, v in result.items():
        if k != "name":
            print(f"  {k}: {v}")

    return result, valid


def plot_results(all_results: list[dict], all_latencies: dict):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    names = [r["name"] for r in all_results]
    throughputs = [r["throughput_ops"] for r in all_results]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, throughputs, color=["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"])
    ax.set_ylabel("Операций / сек")
    ax.set_title("Пропускная способность (throughput)")
    for bar, val in zip(bars, throughputs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"{val}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/throughput.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(names))
    width = 0.18
    metrics = ["avg_latency_ms", "p50_latency_ms", "p95_latency_ms", "p99_latency_ms"]
    labels = ["AVG", "P50", "P95", "P99"]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

    for i, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
        vals = [r[metric] for r in all_results]
        offset = (i - 1.5) * width
        ax.bar([xi + offset for xi in x], vals, width, label=label, color=color)

    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylabel("Задержка (мс)")
    ax.set_title("Задержка по перцентилям")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/latency_percentiles.png", dpi=150)
    plt.close()

    fig, axes = plt.subplots(1, len(all_latencies), figsize=(5 * len(all_latencies), 4))
    if len(all_latencies) == 1:
        axes = [axes]
    for ax, (name, lats) in zip(axes, all_latencies.items()):
        lats_ms = [l * 1000 for l in lats]
        ax.hist(lats_ms, bins=50, color="#2196F3", alpha=0.7, edgecolor="black")
        ax.set_xlabel("Задержка (мс)")
        ax.set_ylabel("Количество")
        ax.set_title(name)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/latency_distribution.png", dpi=150)
    plt.close()

    print(f"\nГрафики сохранены в {RESULTS_DIR}/")


def run_load_test(n_ops: int = 500, n_threads: int = 10):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_results = []
    all_latencies = {}

    db = get_db()
    db.users.delete_many({"email": {"$regex": r"^lt_"}})

    print(f"=" * 60)
    print(f"НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
    print(f"Операций: {n_ops}, Потоков: {n_threads}")
    print(f"=" * 60)

    # Тест 1: INSERT users
    offset = 100_000
    r, lats = benchmark("INSERT users", lambda db, i: op_insert_user(db, offset + i), n_ops, n_threads)
    all_results.append(r)
    all_latencies[r["name"]] = lats

    # Тест 2: READ user by ID
    r, lats = benchmark("READ user by ID",
                        lambda db, i: op_read_user(db, random.randint(1, 1000)), n_ops, n_threads)
    all_results.append(r)
    all_latencies[r["name"]] = lats

    # Тест 3: READ movies by genre
    r, lats = benchmark_read_no_id("READ movies by genre", op_read_movies_by_genre, n_ops, n_threads)
    all_results.append(r)
    all_latencies[r["name"]] = lats

    # Тест 4: UPDATE user subscription
    r, lats = benchmark("UPDATE user",
                        lambda db, i: op_update_user(db, random.randint(1, 1000)), n_ops, n_threads)
    all_results.append(r)
    all_latencies[r["name"]] = lats

    # Тест 5: INSERT reviews
    r, lats = benchmark("INSERT reviews",
                        lambda db, i: op_insert_review(db, random.randint(1, 1000)), n_ops, n_threads)
    all_results.append(r)
    all_latencies[r["name"]] = lats

    with open(f"{RESULTS_DIR}/results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    plot_results(all_results, all_latencies)

    db.users.delete_many({"email": {"$regex": r"^lt_"}})

    return all_results


if __name__ == "__main__":
    run_load_test(n_ops=500, n_threads=10)
