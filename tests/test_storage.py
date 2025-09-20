import os
import threading
import time
import pandas as pd

try:
    import mc_test_app.core as core  # type: ignore
except Exception:  # Flat layout
    import core  # type: ignore


def test_append_single_row(tmp_path, monkeypatch):
    answers_path = tmp_path / "mc_test_answers.csv"
    monkeypatch.setenv("PYTHONHASHSEED", "0")

    def fake_get_answers_path():
        return str(answers_path)

    # Patch function dynamically
    core.get_answers_path = fake_get_answers_path  # type: ignore
    import sys
    if 'mc_test_app.core' in sys.modules:
        sys.modules['mc_test_app.core'].get_answers_path = fake_get_answers_path  # type: ignore

    row = {
        "user_id_hash": "h1",
        "user_id_display": "h1",
        "user_id_plain": "user1",
        "frage_nr": 1,
        "frage": "1. Test?",
        "antwort": "A",
        "richtig": 1,
        "zeit": "2025-09-20T10:00:00",
    }
    core.append_answer_row(row)  # type: ignore
    assert answers_path.exists()
    df = pd.read_csv(answers_path)
    assert len(df) == 1
    assert list(df.columns) == core.ANSWER_FIELDNAMES  # type: ignore


def test_concurrent_appends(tmp_path, monkeypatch):
    answers_path = tmp_path / "mc_test_answers.csv"

    def fake_get_answers_path():
        return str(answers_path)

    core.get_answers_path = fake_get_answers_path  # type: ignore
    import sys
    if 'mc_test_app.core' in sys.modules:
        sys.modules['mc_test_app.core'].get_answers_path = fake_get_answers_path  # type: ignore


    rows = []
    for i in range(10):
        rows.append(
            {
                "user_id_hash": f"h{i}",
                "user_id_display": f"h{i}",
                "user_id_plain": f"user{i}",
                "frage_nr": 1,
                "frage": "1. Test?",
                "antwort": "A",
                "richtig": 1,
                "zeit": f"2025-09-20T10:00:{i:02d}",
            }
        )

    threads = []
    for r in rows:
        t = threading.Thread(target=core.append_answer_row, args=(r,))  # type: ignore
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    df = pd.read_csv(answers_path)
    assert len(df) == 10
    assert set(df["user_id_hash"]) == {f"h{i}" for i in range(10)}
