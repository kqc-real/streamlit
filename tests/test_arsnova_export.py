import json
import sys
from pathlib import Path

import pytest  # type: ignore[import-not-found]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_jobs import generate_arsnova_json, validate_arsnova_questions  # noqa: E402


def _build_question(frage, optionen, loesung, gewichtung=1, thema="Mathe"):
    return {
        "frage": frage,
        "optionen": optionen,
        "loesung": loesung,
        "gewichtung": gewichtung,
        "thema": thema,
    }


def test_generate_arsnova_json_maps_core_fields(tmp_path, monkeypatch):
    questions = [
        _build_question(
            "1. Beispiel?",
            ["A", "B", "C"],
            1,
            gewichtung=2,
            thema="Test",
        ),
        _build_question("2. Noch eine?", ["Ja", "Nein"], 0, gewichtung=3, thema=""),
    ]

    data_bytes = generate_arsnova_json("questions_demo.json", questions)
    payload = json.loads(data_bytes.decode("utf-8"))

    assert payload["name"] == "demo"
    assert payload["state"] == "Inactive"
    assert payload["sessionConfig"]["theme"] == "Material"

    assert len(payload["questionList"]) == 2

    first = payload["questionList"][0]
    assert first["questionText"] == "Beispiel?"
    assert first["TYPE"] == "SingleChoiceQuestion"
    assert first["timer"] == 60
    assert first["requiredForToken"] is True
    assert first["difficulty"] == 6
    assert first["tags"] == ["Test"]
    assert first["multipleSelectionEnabled"] is False
    assert first["answerOptionList"][1]["isCorrect"] is True
    assert all(option["TYPE"] == "DefaultAnswerOption" for option in first["answerOptionList"])

    second = payload["questionList"][1]
    assert second["difficulty"] == 10
    # Ohne Thema erwarten wir ein leeres Array
    assert second["tags"] == []
    assert payload["sessionConfig"]["music"]["enabled"]["lobby"] is True


@pytest.mark.parametrize(
    "question",
    [
        {},
        {"frage": "", "optionen": ["A"], "loesung": 0},
        {"frage": "Fehlt Antwort", "optionen": [], "loesung": 0},
        {"frage": "Index off", "optionen": ["A"], "loesung": 5},
    ],
)
def test_generate_arsnova_json_validation_errors(question):
    with pytest.raises(ValueError):
        generate_arsnova_json("questions_invalid.json", [question])


def test_generate_arsnova_truncates_long_options():
    long_option = "X" * 80
    questions = [
        _build_question("Frage ohne Nummer", [long_option, "Kurz"], 0),
    ]

    data_bytes = generate_arsnova_json("questions_demo.json", questions)
    payload = json.loads(data_bytes.decode("utf-8"))

    exported_option = payload["questionList"][0]["answerOptionList"][0]["answerText"]
    assert len(exported_option) == 60
    assert exported_option == "X" * 60


def test_validate_arsnova_questions_reports_long_options():
    long_option = "A" * 70
    questions = [
        _build_question("Frage mit langer Option", ["Kurz", long_option], 0),
    ]

    warnings = validate_arsnova_questions(questions)
    assert warnings
    assert "überschreitet 60 Zeichen" in warnings[0]
