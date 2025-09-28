"""
Modul für die Kernlogik des MC-Tests.

Verantwortlichkeiten:
- Punkteberechnung (Scoring).
- Fortschritts-Tracking (nächste Frage, Testende).
- Laden des Nutzerfortschritts aus den Log-Daten.
"""
import streamlit as st
from typing import Optional


def calculate_score(answered_scores: list, questions: list, scoring_mode: str) -> tuple[int, int]:
    """Berechnet den aktuellen und den maximal möglichen Punktestand."""
    current_score = sum(p for p in answered_scores if p is not None)
    max_score = sum(q.get("gewichtung", 1) for q in questions)
    return current_score, max_score


def get_current_question_index() -> Optional[int]:
    """
    Ermittelt den Index der nächsten unbeantworteten Frage in der zufälligen Reihenfolge.
    Gibt None zurück, wenn alle Fragen beantwortet sind.
    """
    indices = st.session_state.get("frage_indices", [])

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


def get_answer_for_question(frage_idx: int) -> str | None:
    """Holt die gegebene Antwort für eine Frage aus dem Session State."""
    return st.session_state.get(f"frage_{frage_idx}_antwort")


def set_question_as_answered(frage_idx: int, punkte: int, antwort: str):
    """Markiert eine Frage als beantwortet und speichert Punkte/Antwort."""
    st.session_state[f"frage_{frage_idx}_beantwortet"] = punkte
    st.session_state[f"frage_{frage_idx}_antwort"] = antwort
    st.session_state.answer_outcomes.append(punkte > 0)