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


