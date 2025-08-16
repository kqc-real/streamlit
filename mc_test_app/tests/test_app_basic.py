import json
import csv
from pathlib import Path


import os
import pandas as pd
from mc_test_utils import save_answer

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


def test_save_answer_creates_or_appends(tmp_path):
    logfile = tmp_path / "mc_test_answers.csv"
    orig_logfile = os.environ.get('LOGFILE')
    os.environ['LOGFILE'] = str(logfile)
    frage_obj = {
        "frage": "999. Testfrage?",
        "optionen": ["A", "B"],
        "loesung": 0,
    }
    save_answer("userX", "hashX", frage_obj, "A", 1)
    df = pd.read_csv(logfile)
    assert df.shape[0] == 1
    assert df.iloc[0]["frage_nr"] == 999
    save_answer("userX", "hashX", frage_obj, "A", 1)
    df2 = pd.read_csv(logfile)
    assert df2.shape[0] == 1, "Keine zweite Zeile bei Duplicate erwartet"
    if orig_logfile:
        os.environ['LOGFILE'] = orig_logfile
