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

    assert payload["exportVersion"] == 1
    assert payload["exportedAt"].endswith("Z")
    assert "questionList" not in payload
    assert "sessionConfig" not in payload

    quiz = payload["quiz"]
    assert quiz["name"] == "demo"
    assert quiz["defaultTimer"] == 30
    assert quiz["timerScaleByDifficulty"] is False
    assert quiz["nicknameTheme"] == "NOBEL_LAUREATES"
    assert quiz["readingPhaseEnabled"] is True
    assert len(quiz["questions"]) == 2

    first = quiz["questions"][0]
    assert first["text"] == "Beispiel?"
    assert first["type"] == "SINGLE_CHOICE"
    assert first["timer"] == 45
    assert first["difficulty"] == "MEDIUM"
    assert first["order"] == 0
    assert first["skipReadingPhase"] is False
    assert first["enabled"] is True
    assert "shortTextEvaluationMode" not in first
    assert first["answers"][1] == {"text": "B", "isCorrect": True}

    second = quiz["questions"][1]
    assert second["difficulty"] == "HARD"
    assert second["timer"] == 60


def test_generate_arsnova_json_uses_meta_for_quiz_and_timers(tmp_path, monkeypatch):
    questions = [
        _build_question("1. Meta-Frage?", ["A", "B", "C"], 0, weight=3),
    ]
    source = tmp_path / "questions_meta.json"
    source.write_text(
        json.dumps(
            {
                "meta": {
                    "title": "Machine Learning: Kapitel 3",
                    "target_audience": "Studierende",
                    "question_count": 1,
                    "difficulty_profile": {"easy": 0, "medium": 0, "hard": 1},
                    "language": "de",
                    "time_per_weight_minutes": {"1": 0.5, "2": 0.75, "3": 1.0},
                    "test_duration_minutes": 30,
                },
                "questions": questions,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(export_jobs, "_resolve_json_source", lambda _selected_file: source)

    payload = json.loads(generate_arsnova_json("questions_meta.json").decode("utf-8"))
    quiz = payload["quiz"]

    assert quiz["name"] == "Machine Learning: Kapitel 3"
    assert quiz["defaultTimer"] == 30
    assert quiz["questions"][0]["timer"] == 60
    assert quiz["questions"][0]["difficulty"] == "HARD"
    assert quiz["description"].startswith("## MC-Test-Import: Machine Learning: Kapitel 3\n\n- Zielgruppe: Studierende")
    assert "- Sprache: Deutsch (de)" in quiz["description"]
    assert "- Schwierigkeitsprofil: 0 leicht, 0 mittel, 1 schwer" in quiz["description"]


def test_generate_arsnova_description_includes_structure_metadata():
    questions = [
        _build_question("1. Topic A?", ["A", "B", "C"], 0, topic="Datenaufbereitung", concept="Skalierung"),
        _build_question("2. Topic B?", ["A", "B", "C"], 0, topic="Datenaufbereitung", concept="Skalierung"),
        _build_question("3. Topic C?", ["A", "B", "C"], 0, topic="Modelle", concept="Regularisierung"),
    ]
    questions[0]["cognitive_level"] = "Reproduktion"
    questions[1]["cognitive_level"] = "Anwendung"
    questions[2]["cognitive_level"] = "Anwendung"

    payload = json.loads(generate_arsnova_json("questions_demo.json", questions).decode("utf-8"))
    description = payload["quiz"]["description"]

    assert "## Kognitive Stufen" in description
    assert "- Reproduktion: 1 Frage" in description
    assert "- Anwendung: 2 Fragen" in description
    assert "## Topics" in description
    assert "- Datenaufbereitung: 2 Fragen" in description
    assert "- Modelle: 1 Frage" in description
    assert "## Concepts" in description
    assert "- Skalierung: 2 Fragen" in description
    assert "- Regularisierung: 1 Frage" in description
    assert "MC-Test-Erklärungen sind" in description


def test_generate_arsnova_description_includes_mini_glossary():
    question = _build_question(
        "1. Was ist Regularisierung?",
        ["Strafterm gegen Überanpassung", "Zufälliges Raten", "Datenbankabfrage"],
        0,
        topic="Lineare Modelle",
    )
    question["mini_glossary"] = [
        {"term": "Regularisierung", "definition": "Begrenzt Modellkomplexität, um Overfitting zu reduzieren."},
        {"term": "Overfitting", "definition": "Ein Modell passt Trainingsdaten zu stark an und generalisiert schlecht."},
    ]

    payload = json.loads(generate_arsnova_json("questions_demo.json", [question]).decode("utf-8"))
    description = payload["quiz"]["description"]

    assert "## Topics" in description
    assert "- Lineare Modelle: 1 Frage" in description
    assert "## Concepts" in description
    assert "- Beispiel: 1 Frage" in description
    assert "## Mini-Glossar" in description
    assert "### Lineare Modelle" in description
    assert "- **Regularisierung**: Begrenzt Modellkomplexität, um Overfitting zu reduzieren." in description
    assert "- **Overfitting**: Ein Modell passt Trainingsdaten zu stark an und generalisiert schlecht." in description
    assert len(description) <= export_jobs.ARSNOVA_EU_MAX_DESCRIPTION_LENGTH


def test_generate_arsnova_description_truncates_large_mini_glossary():
    question = _build_question("1. Große Glossarfrage?", ["A", "B", "C"], 0)
    question["mini_glossary"] = {
        f"Begriff {idx:03d}": "Definition " + ("X" * 120)
        for idx in range(120)
    }

    payload = json.loads(generate_arsnova_json("questions_demo.json", [question]).decode("utf-8"))
    description = payload["quiz"]["description"]

    assert "## Topics" in description
    assert "- Mathe: 1 Frage" in description
    assert "## Concepts" in description
    assert "## Mini-Glossar" in description
    assert "weitere Glossarbegriffe" in description or "weitere)." in description
    assert len(description) <= export_jobs.ARSNOVA_EU_MAX_DESCRIPTION_LENGTH


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


def test_generate_arsnova_rejects_long_options():
    long_option = "X" * (export_jobs.ARSNOVA_EU_MAX_ANSWER_LENGTH + 1)
    questions = [
        _build_question("Frage ohne Nummer", [long_option, "Kurz"], 0),
    ]

    with pytest.raises(ValueError, match="überschreitet"):
        generate_arsnova_json("questions_demo.json", questions)


def test_generate_arsnova_preserves_markdown_and_code_tokens():
    questions = [
        _build_question(
            "1. Beispiel mit Code:\n\n```python\nprint('x')\n```\n\nWelche Funktionsfamilie?",
            ["make_* Funktionen", "`fetch_*` Funktionen", "load_* Funktionen"],
            0,
        ),
    ]

    payload = json.loads(generate_arsnova_json("questions_demo.json", questions).decode("utf-8"))
    exported_question = payload["quiz"]["questions"][0]

    assert "```python\nprint('x')\n```" in exported_question["text"]
    assert exported_question["answers"][0]["text"] == "`make_*` Funktionen"
    assert exported_question["answers"][1]["text"] == "`fetch_*` Funktionen"
    assert exported_question["answers"][2]["text"] == "`load_*` Funktionen"


def test_generate_arsnova_json_preserves_markdown_tables_for_arsnova_renderer():
    questions = [
        _build_question(
            "1. Welche Aussage passt?\n\n| Element | Bedeutung |\n|---|---|\n| `X` | Feature-Matrix |\n| `y` | Zielvariable |",
            [
                "| Aspekt | Aussage |\n|---|---|\n| Struktur | Tabellen bleiben lesbar. |",
                "| Aspekt | Aussage |\n|---|---|\n| Umwandlung | Tabellen bleiben Pipe-Text. |",
            ],
            0,
        ),
    ]

    payload = json.loads(generate_arsnova_json("questions_demo.json", questions).decode("utf-8"))
    exported_question = payload["quiz"]["questions"][0]

    assert "| Element | Bedeutung |" in exported_question["text"]
    assert "|---|---|" in exported_question["text"]
    assert "| `X` | Feature-Matrix |" in exported_question["text"]
    assert "| `y` | Zielvariable |" in exported_question["text"]

    correct_answer = exported_question["answers"][0]["text"]
    assert "| Aspekt | Aussage |" in correct_answer
    assert "|---|---|" in correct_answer
    assert "| Struktur | Tabellen bleiben lesbar. |" in correct_answer


def test_generate_arsnova_json_converts_safe_html_to_markdown_text():
    questions = [
        _build_question(
            "<strong>Wichtig:</strong><br>H<sub>2</sub>O und x<sup>2</sup>",
            [
                "<em>Korrekt:</em><br><code>code</code> bleibt als Inline-Code lesbar.",
                "<strong>Falsch:</strong><br>HTML soll roh bleiben.",
            ],
            0,
        ),
    ]

    payload = json.loads(generate_arsnova_json("questions_demo.json", questions).decode("utf-8"))
    exported_question = payload["quiz"]["questions"][0]

    assert exported_question["text"] == "**Wichtig:**\nH_2O und x^2"
    assert exported_question["answers"][0]["text"] == "*Korrekt:*\n`code` bleibt als Inline-Code lesbar."
    assert "<strong>" not in exported_question["text"]
    assert "<code>" not in exported_question["answers"][0]["text"]


def test_validate_arsnova_questions_reports_long_options():
    long_option = "A" * (export_jobs.ARSNOVA_EU_MAX_ANSWER_LENGTH + 1)
    questions = [
        _build_question("Frage mit langer Option", ["Kurz", long_option], 0),
    ]

    warnings = validate_arsnova_questions(questions)
    assert warnings
    assert f"überschreitet {export_jobs.ARSNOVA_EU_MAX_ANSWER_LENGTH} Zeichen" in warnings[0]
