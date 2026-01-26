import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import user_question_sets


def test_smart_quotes_inside_strings_are_ok(tmp_path):
    payload = {
        "meta": {"title": "Test"},
        "questions": [
            {
                "question": "1. Im Kontext des „IoT-Trilemmas“ müssen Kompromisse eingegangen werden.",
                "options": ["A", "B"],
                "answer": 0,
            }
        ],
    }
    path = tmp_path / "q.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    question_set = user_question_sets.validate_user_question_file(path)
    assert len(question_set.questions) == 1
    assert "„IoT-Trilemmas“" in question_set.questions[0]["question"]


def test_smart_quotes_as_delimiters_are_normalized(tmp_path):
    raw = (
        "{“meta”:{“title”:“Test”},"
        "“questions”:[{“question”:“Hallo”,“options”:[“A”,“B”],“answer”:0}]}"
    )
    path = tmp_path / "smart.json"
    path.write_text(raw, encoding="utf-8")

    question_set = user_question_sets.validate_user_question_file(path)
    assert len(question_set.questions) == 1
