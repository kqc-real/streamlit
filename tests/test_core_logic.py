
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
class StMock:
    pass
mock_st = StMock()

# Simuliere st.cache_data als einfachen Pass-Through-Decorator.
# Für Unit-Tests der Logik ist das Caching-Verhalten irrelevant.
def mock_cache_data(func):
    func.clear = lambda: None
    return func
mock_st.cache_data = mock_cache_data

# Füge den Mock zum sys.modules-Cache hinzu, damit alle nachfolgenden Imports
# `from streamlit import ...` diesen Mock anstelle des echten Moduls verwenden.
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
    questions_path = tmp_path / "questions_test.json"
    questions_path.write_text(json.dumps(test_questions), encoding="utf-8")
    return questions_path


# --- Testfälle ---

def test_load_questions_successfully(mock_question_file, test_questions):
    """
    Testet, ob `config.load_questions` eine JSON-Datei korrekt liest und parst.
    """
    # Arrange: Patch `get_package_dir`, damit es auf unser temporäres Verzeichnis zeigt.
    with patch.object(config, "get_package_dir", return_value=mock_question_file.parent):
        # Act: Lade die Fragen aus der temporären Datei.
        loaded_questions = config.load_questions(mock_question_file.name)

        # Assert: Die geladenen Daten müssen mit den Originaldaten übereinstimmen.
        assert loaded_questions == test_questions


def test_scoring_logic_positive_only(test_questions):
    """
    Testet die Punkteberechnung aus logic.py im Modus "positive_only".
    Punkte gibt es nur für richtige Antworten.
    """
    # Arrange
    scoring_mode = "positive_only"
    # Simuliere, dass Frage 1 richtig (Gewichtung 1) und Frage 2 falsch (0 Punkte) beantwortet wurde.
    # Die `beantwortet`-Liste speichert die erzielten Punkte pro Frage.
    answered_scores = [1, 0]

    # Act
    current, maximum = logic.calculate_score(answered_scores, test_questions, scoring_mode)

    # Assert
    assert current == 1  # Nur die 1 Punkt von der ersten Frage.
    assert maximum == 3  # 1 (Frage 1) + 2 (Frage 2)


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
