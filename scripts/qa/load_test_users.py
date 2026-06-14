#!/usr/bin/env python3
"""Small concurrency/load test for the MC-Test Streamlit app.

The test exercises the app's main persistence path without driving the
Streamlit widget protocol:

- create one user + test session per virtual user
- save multiple answers per session concurrently
- update heartbeats
- recompute the final session summary

By default, it uses a temporary SQLite database so local or production-like
statistics are not polluted. Use --live-db only when that is intentional.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Barrier
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("STREAMLIT_LOG_LEVEL", "error")
logging.getLogger("streamlit").setLevel(logging.ERROR)

import database  # noqa: E402
from config import load_questions  # noqa: E402
from helpers.text import get_user_id_hash  # noqa: E402


DEFAULT_QUESTION_FILE = "questions_AMALEA_2025.json"


@dataclass
class OperationTiming:
    name: str
    seconds: float


@dataclass
class VirtualUserResult:
    user_index: int
    session_id: int | None
    ok: bool
    error: str | None
    timings: list[OperationTiming]


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _summarize_timings(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {
            "count": 0,
            "mean_ms": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "max_ms": 0.0,
        }
    return {
        "count": len(values),
        "mean_ms": round(statistics.fmean(values) * 1000, 3),
        "p50_ms": round(_percentile(values, 0.50) * 1000, 3),
        "p95_ms": round(_percentile(values, 0.95) * 1000, 3),
        "p99_ms": round(_percentile(values, 0.99) * 1000, 3),
        "max_ms": round(max(values) * 1000, 3),
    }


def _time_call(timings: list[OperationTiming], name: str, func, *args, **kwargs):
    start = time.perf_counter()
    try:
        return func(*args, **kwargs)
    finally:
        timings.append(OperationTiming(name, time.perf_counter() - start))


def _virtual_user(
    user_index: int,
    *,
    barrier: Barrier,
    questions_file: str,
    answer_count: int,
    jitter_seconds: float,
) -> VirtualUserResult:
    timings: list[OperationTiming] = []
    session_id: int | None = None
    try:
        pseudonym = f"load_user_{user_index:03d}"
        user_id = get_user_id_hash(pseudonym)
        rng = random.Random(user_index)

        barrier.wait()

        _time_call(timings, "add_user", database.add_user, user_id, pseudonym)
        session_id = _time_call(
            timings,
            "start_test_session",
            database.start_test_session,
            user_id,
            questions_file,
            "normal",
            "exam",
        )
        if session_id is None:
            raise RuntimeError("start_test_session returned None")

        _time_call(
            timings,
            "heartbeat",
            database.upsert_user_heartbeat,
            user_id,
            session_id,
        )

        for question_nr in range(1, answer_count + 1):
            if jitter_seconds > 0:
                time.sleep(rng.uniform(0, jitter_seconds))
            is_correct = question_nr % 3 != 0
            points = 1 if is_correct else 0
            _time_call(
                timings,
                "save_answer",
                database.save_answer,
                session_id,
                question_nr,
                f"Option {question_nr % 4}",
                points,
                is_correct,
                "sure" if question_nr % 2 else "unsure",
            )

        _time_call(
            timings,
            "heartbeat",
            database.upsert_user_heartbeat,
            user_id,
            session_id,
        )
        summary_ok = _time_call(
            timings,
            "recompute_session_summary",
            database.recompute_session_summary,
            session_id,
        )
        if not summary_ok:
            raise RuntimeError("recompute_session_summary returned False")

        return VirtualUserResult(user_index, session_id, True, None, timings)
    except Exception as exc:
        return VirtualUserResult(user_index, session_id, False, repr(exc), timings)
    finally:
        try:
            database.get_db_connection.clear()
        except Exception:
            pass


def _measure_http(base_url: str, users: int, timeout_seconds: float) -> dict[str, Any]:
    def fetch(_: int) -> tuple[bool, float, int | None, str | None]:
        start = time.perf_counter()
        try:
            request = urllib.request.Request(
                base_url,
                headers={"User-Agent": "mc-test-load-test/1.0"},
            )
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                response.read(2048)
                return True, time.perf_counter() - start, response.status, None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return False, time.perf_counter() - start, None, repr(exc)

    with ThreadPoolExecutor(max_workers=users) as executor:
        results = list(executor.map(fetch, range(users)))

    latencies = [seconds for ok, seconds, _status, _error in results if ok]
    errors = [error for ok, _seconds, _status, error in results if not ok and error]
    statuses: dict[str, int] = {}
    for ok, _seconds, status, _error in results:
        if ok and status is not None:
            statuses[str(status)] = statuses.get(str(status), 0) + 1
    return {
        "url": base_url,
        "ok": len(latencies),
        "errors": len(errors),
        "statuses": statuses,
        "latency": _summarize_timings(latencies),
        "sample_errors": errors[:3],
    }


def _prepare_database(use_live_db: bool) -> tuple[str, tempfile.TemporaryDirectory[str] | None]:
    if use_live_db:
        database.get_db_connection.clear()
        database.init_database()
        return os.fspath(database.DATABASE_FILE), None

    tmp_dir = tempfile.TemporaryDirectory(prefix="mc-test-load-")
    db_file = Path(tmp_dir.name) / "mc_test_data.db"
    database.DATABASE_FILE = os.fspath(db_file)
    database.get_db_connection.clear()
    database.init_database()
    return os.fspath(db_file), tmp_dir


def _verify_counts() -> dict[str, int]:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    tables = ("users", "test_sessions", "answers", "test_session_summaries")
    counts: dict[str, int] = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        counts[table] = int(cursor.fetchone()["count"])
    return counts


def run_load_test(args: argparse.Namespace) -> dict[str, Any]:
    db_file, tmp_dir = _prepare_database(args.live_db)
    if not args.cold_cache:
        load_questions(args.questions_file, silent=True)
    started_at = time.perf_counter()
    barrier = Barrier(args.users)
    results: list[VirtualUserResult] = []

    try:
        with ThreadPoolExecutor(max_workers=args.users) as executor:
            futures = [
                executor.submit(
                    _virtual_user,
                    user_index,
                    barrier=barrier,
                    questions_file=args.questions_file,
                    answer_count=args.answers,
                    jitter_seconds=args.jitter,
                )
                for user_index in range(1, args.users + 1)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        total_seconds = time.perf_counter() - started_at
        timings_by_name: dict[str, list[float]] = {}
        for result in results:
            for timing in result.timings:
                timings_by_name.setdefault(timing.name, []).append(timing.seconds)

        counts = _verify_counts()
        failures = [result for result in results if not result.ok]
        payload: dict[str, Any] = {
            "config": {
                "users": args.users,
                "answers_per_user": args.answers,
                "questions_file": args.questions_file,
                "jitter_seconds": args.jitter,
                "db_file": db_file,
                "live_db": args.live_db,
                "warm_question_cache": not args.cold_cache,
            },
            "total_seconds": round(total_seconds, 3),
            "successful_users": len(results) - len(failures),
            "failed_users": len(failures),
            "database_counts": counts,
            "operation_latency": {
                name: _summarize_timings(values)
                for name, values in sorted(timings_by_name.items())
            },
            "sample_errors": [
                {"user": result.user_index, "error": result.error}
                for result in failures[:5]
            ],
        }

        expected_answers = args.users * args.answers
        payload["checks"] = {
            "users": counts.get("users") == args.users,
            "sessions": counts.get("test_sessions") == args.users,
            "answers": counts.get("answers") == expected_answers,
            "summaries": counts.get("test_session_summaries") == args.users,
            "no_failed_users": not failures,
        }

        if args.base_url and not args.skip_http:
            payload["http"] = _measure_http(args.base_url, args.users, args.http_timeout)

        return payload
    finally:
        try:
            database.get_db_connection.clear()
        except Exception:
            pass
        if tmp_dir is not None and not args.keep_temp_db:
            tmp_dir.cleanup()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a concurrent-user load test against the MC-Test persistence path.",
    )
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--answers", type=int, default=20)
    parser.add_argument("--questions-file", default=DEFAULT_QUESTION_FILE)
    parser.add_argument(
        "--jitter",
        type=float,
        default=0.01,
        help="Max random sleep between answers per virtual user.",
    )
    parser.add_argument(
        "--live-db",
        action="store_true",
        help="Use the configured app database instead of a temporary DB.",
    )
    parser.add_argument(
        "--keep-temp-db",
        action="store_true",
        help="Do not delete the temporary DB after the run.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8501/",
        help="Optional Streamlit URL for concurrent HTTP health checks.",
    )
    parser.add_argument("--skip-http", action="store_true")
    parser.add_argument("--http-timeout", type=float, default=5.0)
    parser.add_argument(
        "--cold-cache",
        action="store_true",
        help="Do not warm the selected question set before timing the load test.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON only.",
    )
    return parser


def _print_human_summary(payload: dict[str, Any]) -> None:
    config = payload["config"]
    print(
        f"Load test: {config['users']} users x "
        f"{config['answers_per_user']} answers "
        f"({config['questions_file']})"
    )
    print(f"DB: {config['db_file']} ({'live' if config['live_db'] else 'temp'})")
    print(
        f"Total: {payload['total_seconds']}s, "
        f"successful users: {payload['successful_users']}, "
        f"failed users: {payload['failed_users']}"
    )
    print(f"Counts: {payload['database_counts']}")
    print(f"Checks: {payload['checks']}")
    print("Operation latency:")
    for name, stats in payload["operation_latency"].items():
        print(
            f"  {name}: count={stats['count']} "
            f"p50={stats['p50_ms']}ms p95={stats['p95_ms']}ms "
            f"p99={stats['p99_ms']}ms max={stats['max_ms']}ms"
        )
    if payload.get("http"):
        http = payload["http"]
        print(
            f"HTTP {http['url']}: ok={http['ok']} errors={http['errors']} "
            f"statuses={http['statuses']} "
            f"p95={http['latency']['p95_ms']}ms"
        )
        if http.get("sample_errors"):
            print(f"HTTP sample errors: {http['sample_errors']}")
    if payload.get("sample_errors"):
        print(f"Sample user errors: {payload['sample_errors']}")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    payload = run_load_test(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human_summary(payload)
        print("\nJSON:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    checks_ok = all(payload.get("checks", {}).values())
    http_ok = payload.get("http", {}).get("errors", 0) == 0
    return 0 if checks_ok and http_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
