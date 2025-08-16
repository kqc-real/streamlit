import json
import csv
from pathlib import Path

import importlib.util

# We only test pure helper behaviors (no Streamlit runtime UI rendering).

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "questions.json"


def test_questions_file_exists_and_valid():
    assert QUESTIONS_FILE.exists(), "questions.json fehlt"
    data = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) > 0, "questions.json muss nicht-leere Liste sein"
    first = data[0]
    assert {"frage", "optionen", "loesung"}.issubset(first.keys())
    assert isinstance(first["optionen"], list) and len(first["optionen"]) >= 2
    assert isinstance(first["loesung"], int)


def test_save_answer_creates_or_appends(tmp_path, monkeypatch):
    """Patch LOGFILE to temp and verify row append semantics."""
    # Import module
    module_path = BASE_DIR / "mc_test_app.py"
    spec = importlib.util.spec_from_file_location("mc_test_app_module", module_path)
    app = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec and spec.loader
    spec.loader.exec_module(app)  # type: ignore
    # Patch logfile path
    temp_log = tmp_path / "answers.csv"
    monkeypatch.setattr(app, "LOGFILE", str(temp_log))
    # Minimal fake state for save_answer
    
    class DummySession(dict):
        pass
    # No streamlit monkeypatching or stubs; use real streamlit
    frage_obj = {
        "frage": "999. Testfrage?",
        "optionen": ["A", "B"],
        "loesung": 0,
    }
    # First write
    app.save_answer("userX", "hashX", frage_obj, "A", 1)
    assert temp_log.exists(), "Logfile sollte erzeugt werden"
    rows = list(csv.DictReader(open(temp_log, newline="", encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["frage_nr"] == "999"
    # Duplicate guard: second call should not append
    app.save_answer("userX", "hashX", frage_obj, "A", 1)
    rows2 = list(csv.DictReader(open(temp_log, newline="", encoding="utf-8")))
    assert len(rows2) == 1, "Keine zweite Zeile bei Duplicate erwartet"
