
"""
Neue, fokussierte Tests für die Kernlogik der MC-Test-App.

Diese Tests sind unabhängig von der Streamlit-UI und prüfen die
zentralen Funktionen wie das Laden von Fragen, die Verarbeitung von
Antworten und die Punkteberechnung.
"""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

# --- Mocking von Streamlit ---
# Erstelle ein Mock-Objekt für das `streamlit`-Modul, damit die App-Logik
# importiert werden kann, ohne dass Streamlit tatsächlich läuft.
import types

# Erstelle ein echtes Modul-Objekt statt einer einfachen Instanz, damit
# `import streamlit.components.v1` und ähnliche Subimports weiterhin
# funktionieren (das Modul verhält sich wie ein Paket).
mock_st = types.ModuleType("streamlit")
mock_st.error = MagicMock()
mock_st.warning = MagicMock()
mock_st.info = MagicMock()

# Simuliere st.cache_data als flexiblen Decorator-Fabrikator, der sowohl
# parameterlose Dekoratoren als auch dekoratoraufrufe mit Keyword-Argumenten
# unterstützt (z. B. @st.cache_data(ttl=3600)). Für Unit-Tests der Logik ist
# das tatsächliche Caching irrelevant.
def mock_cache_data(func=None, **kwargs):
    if callable(func):
        func.clear = lambda: None
        return func

    def decorator(f):
        f.clear = lambda: None
        return f

    return decorator

mock_st.cache_data = mock_cache_data

# Füge den Mock temporär zum sys.modules-Cache hinzu, damit die folgenden
# Imports `from streamlit import ...` diesen Mock anstelle des echten Moduls
# verwenden. Wichtig: Stelle sicher, dass wir den Original-Eintrag wieder
# herstellen, damit andere Testmodule (die z. B. `streamlit.components`
# importieren) nicht von unserem Mock beeinflusst werden.
sys.modules["streamlit"] = mock_st

# --- Echte Modul-Imports (nach dem Mocking) ---
# Jetzt können die Module der App sicher importiert werden.
import config
import logic


# --- Test-Setup ---

@pytest.fixture(autouse=True)
def mock_session_state():
    """
    Diese Fixture ersetzt `st.session_state` durch einen robusten Mock, der
    sich wie ein Dictionary verhält, aber auch Attributzugriffe erlaubt.
    """
    # Ein echtes Dictionary dient als zentraler Speicher.
    _state = {}

    # Ein MagicMock wird für die Simulation verwendet.
    mock_ss = MagicMock()

    # Leite die get/set-Methoden auf das Dictionary um.
    mock_ss.get.side_effect = lambda key, default=None: _state.get(key, default)
    mock_ss.__setitem__.side_effect = lambda key, value: _state.__setitem__(key, value)
    mock_ss.__getitem__.side_effect = lambda key: _state.__getitem__(key)

    # Wichtig: `st.session_state` im gemockten Modul ersetzen.
    mock_st.session_state = mock_ss

    # Initialisiere Werte, die von der App als existierend erwartet werden.
    mock_st.session_state["answer_outcomes"] = []


@pytest.fixture
def test_questions():
    """Stellt eine Beispielliste von Fragen für die Tests bereit."""
    return [
        {
            "frage": "1. Was ist 1+1?",
            "optionen": ["1", "2", "3"],
            "loesung": 1,
            "gewichtung": 1,
        },
        {
            "frage": "2. Was ist die Hauptstadt von Deutschland?",
            "optionen": ["Berlin", "München", "Hamburg"],
            "loesung": 0,
            "gewichtung": 2,
        },
    ]


@pytest.fixture
def mock_question_file(tmp_path, test_questions):
    """
    Erstellt eine temporäre `questions_test.json`-Datei und gibt den Pfad zurück.
    `tmp_path` ist eine eingebaute pytest-Fixture für temporäre Verzeichnisse.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    questions_path = data_dir / "questions_test.json"
    questions_path.write_text(json.dumps(test_questions), encoding="utf-8")
    return questions_path.name # Gib nur den Dateinamen zurück


# --- Testfälle ---

def test_load_questions_successfully(mock_question_file, test_questions, tmp_path):
    """
    Testet, ob `config.load_questions` eine JSON-Datei korrekt liest und parst.
    """
    # Arrange: Patch `get_package_dir`, damit es auf unser temporäres Verzeichnis (tmp_path) zeigt.
    # Die Fixture `mock_question_file` hat die Testdatei unter `tmp_path/data/` erstellt.
    # `get_package_dir` muss also auf `tmp_path` zeigen.
    with patch.object(config, "get_package_dir", return_value=str(tmp_path)):
        # Act: Lade die Fragen aus der temporären Datei.
        loaded_questions = config.load_questions(mock_question_file)

        # Assert: Die `load_questions`-Funktion nummeriert die Fragen neu.
        # Wir müssen die Original-Testdaten ebenfalls neu nummerieren, um sie vergleichen zu können.
        expected_questions = []
        for i, q in enumerate(test_questions):
            new_q = q.copy()
            base_txt = q.get('question') or q.get('frage', '')
            new_text = f"{i + 1}. {base_txt.split('.', 1)[-1].strip()}"
            # Keep both canonical English and legacy German keys for compatibility
            new_q["question"] = new_text
            new_q["frage"] = new_text
            new_q["question"] = new_text
            expected_questions.append(new_q)

        # Compare the canonical English 'question' field (loader guarantees this)
        loaded_trimmed = []
        for q in loaded_questions.questions:
            loaded_trimmed.append({
                "question": q.get("question"),
                "optionen": q.get("optionen"),
                "loesung": q.get("loesung"),
                "gewichtung": q.get("gewichtung"),
            })
        # For compatibility we ensured expected_questions contains a canonical 'question' key
        expected_trimmed = []
        for q in expected_questions:
            expected_trimmed.append({
                "question": q.get("question"),
                "optionen": q.get("optionen"),
                "loesung": q.get("loesung"),
                "gewichtung": q.get("gewichtung"),
            })

        assert loaded_trimmed == expected_trimmed


def test_load_questions_with_meta(tmp_path, test_questions):
    """
    Stellt sicher, dass Metadaten (inkl. Testdauer) korrekt verarbeitet werden.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    payload = {
        "meta": {
            "title": "Meta Testset",
            "test_duration_minutes": 42,
            "time_per_weight_minutes": {"1": 1.0, "2": 2.0, "3": 3.0},
        },
        "questions": test_questions,
    }
    questions_path = data_dir / "questions_meta.json"
    questions_path.write_text(json.dumps(payload), encoding="utf-8")

    with patch.object(config, "get_package_dir", return_value=str(tmp_path)):
        question_set = config.load_questions(questions_path.name)

    assert question_set.meta["title"] == "Meta Testset"
    assert question_set.get_test_duration_minutes(default_minutes=30) == 40


@pytest.mark.parametrize(
    "scoring_mode, answered_scores, expected_current, expected_maximum",
    [
        # Testfall 1: Modus "positive_only"
        ("positive_only", [1, 0], 1, 3),
        # Testfall 2: Modus "negative"
        ("negative", [1, -2], -1, 3),
        # Testfall 3: Keine Antworten gegeben
        ("positive_only", [None, None], 0, 3),
        # Testfall 4: Alle richtig
        ("positive_only", [1, 2], 3, 3),
    ],
)
def test_scoring_logic(
    scoring_mode, answered_scores, expected_current, expected_maximum, test_questions
):
    """
    Testet die Punkteberechnung aus logic.py mit verschiedenen Szenarien.
    Verwendet pytest.mark.parametrize, um mehrere Fälle abzudecken.
    """
    # Act
    current, maximum = logic.calculate_score(answered_scores, test_questions, scoring_mode)

    # Assert
    assert current == expected_current
    assert maximum == expected_maximum


def test_load_questions_file_not_found():
    """
    Testet das Verhalten von `load_questions`, wenn die Datei nicht existiert.
    Der Fehler sollte abgefangen und eine leere Liste zurückgegeben werden.
    """
    mock_st.error.reset_mock()
    # Act: Versuche, eine nicht existierende Datei zu laden.
    loaded_questions = config.load_questions("non_existent_file.json")
    # Assert: Es sollte eine leere Liste zurückkommen und st.error aufgerufen werden.
    assert len(loaded_questions) == 0
    mock_st.error.assert_called_once()


def test_test_flow_and_completion(test_questions):
    """
    Simuliert einen kompletten Testdurchlauf:
    1. Prüft den Startzustand.
    2. Beantwortet alle Fragen.
    3. Prüft den Endzustand.
    """
    # --- 1. Initialzustand ---
    # Arrange: Initialisiere den Session State für einen Testlauf.
    # Die Fixture `mock_session_state` hat `answer_outcomes` bereits initialisiert.
    mock_st.session_state["frage_indices"] = list(range(len(test_questions)))
    for i in range(len(test_questions)):
        mock_st.session_state[f"frage_{i}_beantwortet"] = None

    # Act & Assert: Zu Beginn ist der Test nicht beendet und die erste Frage ist dran.
    assert not logic.is_test_finished(test_questions)
    assert logic.get_current_question_index() == 0

    # --- 2. Alle Fragen beantworten ---
    # Act: Simuliere das Beantworten beider Fragen.
    logic.set_question_as_answered(frage_idx=0, punkte=1, antwort="2")
    logic.set_question_as_answered(frage_idx=1, punkte=0, antwort="München")

    # Assert: Die `beantwortet`-Flags im Session State müssen gesetzt sein.
    assert mock_st.session_state["frage_0_beantwortet"] == 1
    assert mock_st.session_state["frage_1_beantwortet"] == 0

    # --- 3. Endzustand ---
    # Act & Assert: Nach Beantwortung aller Fragen ist der Test beendet.
    assert logic.is_test_finished(test_questions)
    # `get_current_question_index` sollte `None` zurückgeben, da keine Fragen mehr offen sind.
    assert logic.get_current_question_index() is None
