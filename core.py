"""
Kernfunktionen für MC-Test App (lehrbeispielhaft extrahiert)
"""
import hashlib
import json
import os
from typing import Dict, Any

import pandas as pd

# Robuster Import von FileLock mit Fallback (damit App auch ohne Abhängigkeit startet)
try:  # pragma: no cover - simpler import guard
    from filelock import FileLock  # type: ignore
except Exception:  # noqa: BLE001
    class _NoOpFileLock:
        def __init__(self, *_, **__):  # noqa: D401
            pass

        def __enter__(self):  # noqa: D401
            return self

        def __exit__(self, *exc_info):  # noqa: D401
            return False

    FileLock = _NoOpFileLock  # type: ignore


ANSWER_FIELDNAMES = [
    "user_id_hash",
    "user_id_display",
    "user_id_plain",
    "frage_nr",
    "frage",
    "antwort",
    "richtig",
    "zeit",
]


def get_answers_path() -> str:
    return os.path.join(os.path.dirname(__file__), "mc_test_answers.csv")


def append_answer_row(row: Dict[str, Any]) -> None:
    """Append a single answer row to the CSV with file locking.

    Creates the file with header if it does not yet exist.
    Silently ignores key errors by restricting to known columns.
    """
    path = get_answers_path()
    lock_path = path + ".lock"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Filter to expected columns only
    filtered = {k: row.get(k, "") for k in ANSWER_FIELDNAMES}
    lock = FileLock(lock_path, timeout=5)
    with lock:  # Raises if cannot acquire within timeout
        file_exists_and_not_empty = os.path.isfile(path) and os.path.getsize(path) > 0
        import csv  # local import keeps core import surface minimal

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ANSWER_FIELDNAMES)
            if not file_exists_and_not_empty:
                writer.writeheader()
            writer.writerow(filtered)

def get_user_id_hash(user_id: str) -> str:
    """Berechnet einen SHA256-Hash für das Pseudonym."""
    return hashlib.sha256(user_id.encode()).hexdigest()

def _load_fragen() -> list:
    """Lädt die Fragen aus der JSON-Datei im App-Verzeichnis."""
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _duration_to_str(x):
    """Formatiert eine Zeitspanne als mm:ss."""
    if x is None or pd.isna(x):
        return ''
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"
