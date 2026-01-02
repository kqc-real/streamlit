import json
import sys
from pathlib import Path

import pytest  # type: ignore[import-not-found]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_jobs import generate_arsnova_json, validate_arsnova_questions  # noqa: E402
import export_jobs


def _build_question(question, options, answer, weight=1, topic="Mathe", concept="Beispiel"):
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "weight": weight,
        "topic": topic,
        "concept": concept,
    }


def test_generate_arsnova_json_maps_core_fields(tmp_path, monkeypatch):
    questions = [
        _build_question(
            "1. Beispiel?",
            ["A", "B", "C"],
            1,
            weight=2,
            topic="Test",
        ),
        _build_question("2. Noch eine?", ["Ja", "Nein"], 0, weight=3, topic="", concept="Noch ein Beispiel"),
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
    assert first["tags"] == ["Test", "Konzept: Beispiel"]
    assert first["multipleSelectionEnabled"] is False
    assert first["answerOptionList"][1]["isCorrect"] is True
    assert all(option["TYPE"] == "DefaultAnswerOption" for option in first["answerOptionList"])

    second = payload["questionList"][1]
    assert second["difficulty"] == 10
    # Mit Concept, aber ohne Thema erwarten wir das Concept-Tag
    assert second["tags"] == ["Konzept: Noch ein Beispiel"]
    assert payload["sessionConfig"]["music"]["enabled"]["lobby"] is True


@pytest.mark.parametrize(
    "question",
    [
        {},
        {"question": "", "options": ["A"], "answer": 0},
        {"question": "Fehlt Antwort", "options": [], "answer": 0},
        {"question": "Index off", "options": ["A"], "answer": 5},
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
    expected_len = min(len(long_option), export_jobs.ARSNOVA_MAX_OPTION_LENGTH)
    assert len(exported_option) == expected_len
    assert exported_option == "X" * expected_len


def test_validate_arsnova_questions_reports_long_options():
    long_option = "A" * 70
    questions = [
        _build_question("Frage mit langer Option", ["Kurz", long_option], 0),
    ]

    warnings = validate_arsnova_questions(questions)
    if len(long_option) > export_jobs.ARSNOVA_MAX_OPTION_LENGTH:
        assert warnings
        assert f"überschreitet {export_jobs.ARSNOVA_MAX_OPTION_LENGTH} Zeichen" in warnings[0]
    else:
        assert not warnings
