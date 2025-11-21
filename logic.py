"""
Modul für die Kernlogik des MC-Tests.

Verantwortlichkeiten:
- Punkteberechnung (Scoring).
- Fortschritts-Tracking (nächste Frage, Testende).
- Laden des Nutzerfortschritts aus den Log-Daten.
"""
import importlib


def _st_module():
    try:
        return importlib.import_module("streamlit")
    except Exception:
        return None
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
    st = _st_module()
    state = getattr(st, "session_state", None) if st is not None else None
    # (debug prints removed)
    if state is None:
        return None

    indices = state.get("frage_indices", [])

    # 3. Priorität: Nächste unbeantwortete Frage in der (geshuffelten) Reihenfolge
    for idx in indices:
        if state.get(f"frage_{idx}_beantwortet") is None:
            return idx

    return None  # Alle Fragen beantwortet


def is_test_finished(questions: list) -> bool:
    """Prüft, ob alle Fragen beantwortet wurden."""
    num_questions = len(questions)
    st = _st_module()
    state = getattr(st, "session_state", {}) if st is not None else {}
    num_answered = sum(
        1 for i in range(num_questions) if state.get(f"frage_{i}_beantwortet") is not None
    )
    return num_answered == num_questions


def get_answer_for_question(frage_idx: int) -> str | None:
    """Holt die gegebene Antwort für eine Frage aus dem Session State."""
    st = _st_module()
    state = getattr(st, "session_state", {}) if st is not None else {}
    return state.get(f"frage_{frage_idx}_antwort")


def set_question_as_answered(frage_idx: int, punkte: int, antwort: str):
    """Markiert eine Frage als beantwortet und speichert Punkte/Antwort."""
    st = _st_module()
    state = getattr(st, "session_state", {}) if st is not None else {}
    # Support both the real Streamlit session_state object and simple dict mocks
    try:
        state[f"frage_{frage_idx}_beantwortet"] = punkte
        state[f"frage_{frage_idx}_antwort"] = antwort
    except Exception:
        # If the session_state isn't dict-like, try setting attributes
        try:
            setattr(state, f"frage_{frage_idx}_beantwortet", punkte)
            setattr(state, f"frage_{frage_idx}_antwort", antwort)
        except Exception:
            pass

    # Ensure answer_outcomes exists and append the boolean outcome
    try:
        # dict-like
        state.setdefault("answer_outcomes", []).append(punkte > 0)
    except Exception:
        try:
            # attribute-style
            ao = getattr(state, "answer_outcomes", None)
            if ao is None:
                setattr(state, "answer_outcomes", [punkte > 0])
            else:
                ao.append(punkte > 0)
        except Exception:
            pass