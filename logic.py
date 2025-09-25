"""
Modul für die Kernlogik des MC-Tests.

Verantwortlichkeiten:
- Punkteberechnung (Scoring).
- Fortschritts-Tracking (nächste Frage, Testende).
- Laden des Nutzerfortschritts aus den Log-Daten.
"""
import streamlit as st
import pandas as pd

from mc_test_app.data_manager import load_all_logs


def calculate_score(answered_mask: list, questions: list, scoring_mode: str) -> tuple[int, int]:
    """Berechnet den aktuellen und den maximal möglichen Punktestand."""
    current_score = 0
    max_score = 0
    for i, frage in enumerate(questions):
        gewichtung = frage.get("gewichtung", 1)
        max_score += gewichtung
        if answered_mask[i] is not None:
            punkte = answered_mask[i]
            current_score += punkte
    return current_score, max_score


def get_current_question_index() -> int | None:
    """
    Ermittelt den Index der nächsten anzuzeigenden Frage basierend auf der
    Logik: Erklärungsmodus > Sprungziel > nächste unbeantwortete Frage.
    """
    indices = st.session_state.get("frage_indices", [])

    # 1. Priorität: Eine Frage ist im Erklärungsmodus
    for idx in indices:
        if st.session_state.get(f"show_explanation_{idx}", False):
            return idx

    # 2. Priorität: Ein Sprungziel (z.B. von Bookmark) wurde gesetzt
    if "jump_to_idx" in st.session_state:
        idx = st.session_state.jump_to_idx
        del st.session_state["jump_to_idx"]
        return idx

    # 3. Priorität: Nächste unbeantwortete Frage in der geshuffelten Reihenfolge
    for idx in indices:
        if st.session_state.get(f"frage_{idx}_beantwortet") is None:
            return idx

    return None  # Alle Fragen beantwortet


def is_test_finished(questions: list) -> bool:
    """Prüft, ob alle Fragen beantwortet wurden."""
    num_questions = len(questions)
    num_answered = sum(
        1 for i in range(num_questions) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    return num_answered == num_questions


def load_user_progress(user_id_hash: str, questions: list):
    """Lädt den Fortschritt eines Nutzers aus den Log-Daten in den Session State."""
    df = load_all_logs()
    if df.empty:
        return

    # Filtere nach Nutzer und aktuellem Fragenset
    q_file = st.session_state.get("selected_questions_file")
    user_df = df[
        (df["user_id_hash"] == user_id_hash) & (df["questions_file"] == q_file)
    ]
    if user_df.empty:
        return

    # Finde den originalen Index für jede Frage-Nummer
    frage_nr_to_idx = {
        int(q["frage"].split(".", 1)[0]): i for i, q in enumerate(questions)
    }

    reconstructed_outcomes = []
    bookmarked = []

    for _, row in user_df.sort_values("zeit").iterrows():
        frage_nr = int(row["frage_nr"])
        original_idx = frage_nr_to_idx.get(frage_nr)

        if original_idx is None:
            continue

        # Lade Bookmarks
        if row.get("markiert"):
            if original_idx not in bookmarked:
                bookmarked.append(original_idx)

        # Lade Antworten (ignoriere reine Bookmark-Platzhalter)
        if row["antwort"] != "__bookmark__":
            punkte = int(row["richtig"])
            st.session_state[f"frage_{original_idx}_beantwortet"] = punkte
            st.session_state[f"frage_{original_idx}_antwort"] = row["antwort"]
            reconstructed_outcomes.append(punkte > 0)

    st.session_state.answer_outcomes = reconstructed_outcomes
    st.session_state.bookmarked_questions = sorted(bookmarked)


def get_answer_for_question(frage_idx: int) -> str | None:
    """Holt die gegebene Antwort für eine Frage aus dem Session State."""
    return st.session_state.get(f"frage_{frage_idx}_antwort")


def set_question_as_answered(frage_idx: int, punkte: int, antwort: str):
    """Markiert eine Frage als beantwortet und speichert Punkte/Antwort."""
    st.session_state[f"frage_{frage_idx}_beantwortet"] = punkte
    st.session_state[f"frage_{frage_idx}_antwort"] = antwort
    st.session_state.answer_outcomes.append(punkte > 0)