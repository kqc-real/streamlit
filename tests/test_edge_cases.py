import sys
import os
import importlib
import pandas as pd
import streamlit as st

TEST_DIR = os.path.dirname(__file__)
PKG_ROOT = os.path.dirname(TEST_DIR)
REPO_ROOT = os.path.dirname(PKG_ROOT)
for p in (PKG_ROOT, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    app_mod = importlib.import_module("mc_test_app.mc_test_app")  # package layout
    core = importlib.import_module("mc_test_app.core")
except Exception:
    # Flat layout
    app_mod = importlib.import_module("mc_test_app")
    core = importlib.import_module("core")


def test_leaderboard_empty(tmp_path, monkeypatch):
    """calculate_leaderboard() sollte bei leerer / fehlender Datei leer sein."""
    # Patch Pfad der Logdatei auf temporäre Datei ohne Inhalt
    empty_path = tmp_path / "mc_test_answers.csv"
    monkeypatch.setattr(app_mod, "LOGFILE", str(empty_path))
    # Cache leeren, sonst kann altes Ergebnis zurückkommen
    try:
        app_mod.calculate_leaderboard.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    df = app_mod.calculate_leaderboard()
    assert df.empty


def test_leaderboard_minimal_completion(tmp_path, monkeypatch):
    """Ein Nutzer mit genau FRAGEN_ANZAHL beantworteten Fragen erscheint im Leaderboard."""
    answers_path = tmp_path / "mc_test_answers.csv"
    # Wir reduzieren künstlich die Anzahl Fragen auf 1 für schnellen Test
    original_count = getattr(app_mod, "FRAGEN_ANZAHL", None)
    monkeypatch.setattr(app_mod, "FRAGEN_ANZAHL", 1)
    monkeypatch.setattr(app_mod, "LOGFILE", str(answers_path))
    # Schreibe eine einzelne vollständige Antwortzeile
    answers_path.write_text(
        "user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit\n"
        "h1,h1,user1,1,1. Test?,A,1,2025-09-20T10:00:00\n",
        encoding="utf-8",
    )
    try:
        app_mod.calculate_leaderboard.clear()  # Cache invalidieren
    except Exception:
        pass
    df = app_mod.calculate_leaderboard()
    assert not df.empty
    assert list(df.columns) == ["Platz", "Pseudonym", "Punkte"]
    assert df.iloc[0]["Punkte"] == 1
    # Restore original value to avoid side-effects for other tests
    if original_count is not None:
        monkeypatch.setattr(app_mod, "FRAGEN_ANZAHL", original_count)


def test_duplicate_answer_prevention(tmp_path, monkeypatch):
    """save_answer schreibt eine Frage nur einmal (Duplicate Guard)."""
    # Patch core Speicherpfad, damit append_answer_row dort schreibt
    answers_path = tmp_path / "mc_test_answers.csv"

    def fake_get_answers_path():
        return str(answers_path)

    monkeypatch.setattr(core, "get_answers_path", fake_get_answers_path)
    monkeypatch.setattr(app_mod, "LOGFILE", str(answers_path))

    # Session State vorbereiten
    st.session_state.clear()
    st.session_state.user_id = "tester"
    st.session_state.user_id_hash = "hash_tester"
    st.session_state.beantwortet = [None]
    st.session_state.frage_indices = [0]
    st.session_state.optionen_shuffled = [["A", "B"]]

    frage_obj = {"frage": "1. Test?", "optionen": ["A", "B"], "loesung": 0, "gewichtung": 1}

    # Erster Save
    app_mod.save_answer("tester", "hash_tester", frage_obj, "A", 1)
    # Zweiter (doppelter) Save Versuch
    app_mod.save_answer("tester", "hash_tester", frage_obj, "A", 1)

    # Datei einlesen und prüfen, dass nur eine Datenzeile existiert
    df = pd.read_csv(answers_path)
    assert len(df) == 1
    assert df.iloc[0]["antwort"] == "A"


def test_duplicate_answer_via_csv_existing(tmp_path, monkeypatch):
    """Duplicate Guard greift auch, wenn bereits Zeile im CSV steht (simulate reload)."""
    answers_path = tmp_path / "mc_test_answers.csv"

    # Vorab vorhandene Antwort schreiben (simuliert früheren Lauf)
    answers_path.write_text(
        "user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit\n"
        "hash_tester,hash_test,tester,1,1. Test?,A,1,2025-09-20T10:00:00\n",
        encoding="utf-8",
    )

    def fake_get_answers_path():
        return str(answers_path)

    monkeypatch.setattr(core, "get_answers_path", fake_get_answers_path)
    monkeypatch.setattr(app_mod, "LOGFILE", str(answers_path))

    st.session_state.clear()
    st.session_state.user_id = "tester"
    st.session_state.user_id_hash = "hash_tester"
    st.session_state.beantwortet = [None]
    st.session_state.frage_indices = [0]
    st.session_state.optionen_shuffled = [["A", "B"]]

    frage_obj = {"frage": "1. Test?", "optionen": ["A", "B"], "loesung": 0, "gewichtung": 1}

    # Save Versuch — sollte wegen CSV-Duplikat keine neue Zeile hinzufügen
    app_mod.save_answer("tester", "hash_tester", frage_obj, "A", 1)

    df = pd.read_csv(answers_path)
    # Weiterhin nur eine Zeile
    assert len(df) == 1
    assert df.iloc[0]["antwort"] == "A"
