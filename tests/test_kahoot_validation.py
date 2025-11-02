import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_jobs import validate_kahoot_questions  # noqa: E402


def make_question(text, options, solution, **extra):
    data = {
        "frage": text,
        "optionen": options,
        "loesung": solution,
    }
    data.update(extra)
    return data


def test_validate_kahoot_questions_passes_for_valid_question():
    questions = [
        make_question(
            "Beispiel Frage?",
            ["Antwort A", "Antwort B", "Antwort C"],
            1,
        )
    ]

    errors, warnings = validate_kahoot_questions(questions)
    assert errors == []
    assert warnings == []


def test_validate_kahoot_questions_detects_length_and_options():
    long_question = "X" * 121
    questions = [
        make_question(long_question, ["A", "B"], 0),
        make_question("Ok", ["A", "B", "C", "D", "E"], 0),
    ]

    errors, _ = validate_kahoot_questions(questions)
    assert any("121" in err for err in errors)
    assert any("Höchstens" in err for err in errors)


def test_validate_kahoot_questions_detects_missing_solution():
    questions = [make_question("Frage", ["A", "B"], 5)]

    errors, _ = validate_kahoot_questions(questions)
    assert any("Lösungsindex" in err for err in errors)


def test_validate_kahoot_questions_warns_on_timer():
    questions = [make_question("Frage", ["A", "B"], 0, timer=7)]

    errors, warnings = validate_kahoot_questions(questions)
    assert errors == []
    assert any("Zeitlimit" in warn for warn in warnings)


def test_validate_kahoot_questions_global_limit():
    questions = [make_question("Frage", ["A", "B"], 0)] * 501

    errors, _ = validate_kahoot_questions(questions)
    assert any("500" in err for err in errors)
