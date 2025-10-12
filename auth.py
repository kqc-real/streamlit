"""
Modul für Authentifizierung und Session-Management.

Verantwortlichkeiten:
- Anzeige des Login-Formulars.
- Initialisierung des `st.session_state` für einen neuen Testlauf.
- Überprüfung von Admin-Rechten.
"""
import streamlit as st
import random
import hmac
import json
from datetime import datetime

from config import AppConfig, load_scientists, QuestionSet
from helpers import get_user_id_hash

def log_state(event: str):
    """Schreibt den aktuellen Session State zur Fehlersuche in eine Log-Datei."""
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"--- {event} at {datetime.now()} ---\n")
        state_copy = {}
        for k, v in st.session_state.items():
            try:
                json.dumps({k: v})
                state_copy[k] = v
            except (TypeError, OverflowError):
                state_copy[k] = f"NOT_SERIALIZABLE: {type(v)}"
        f.write(json.dumps(state_copy, indent=2, ensure_ascii=False) + "\n")

def initialize_session_state(question_set: QuestionSet, app_config: AppConfig | None = None):
    """Initialisiert den Session-State für einen neuen Testlauf."""
    # Lösche alte Test-spezifische Schlüssel, falls vorhanden
    # Dies ist wichtig, wenn ein Nutzer einen neuen Test startet, ohne die Session komplett zu beenden.
    for key in list(st.session_state.keys()):
        if key.startswith("frage_") or key in [
            "beantwortet", "frage_indices", "initial_frage_indices", "start_zeit",
            "progress_loaded", "optionen_shuffled", "answer_outcomes",
            "bookmarked_questions",
            "test_time_expired", "show_pseudonym_reminder",
            "login_attempts", "last_answered_idx", "resume_next_idx", "jump_to_idx_active"
        ]:
            del st.session_state[key]

    question_count = len(question_set)
    st.session_state.beantwortet = [None] * question_count
    frage_indices = list(range(question_count))
    random.shuffle(frage_indices)
    st.session_state.frage_indices = frage_indices
    st.session_state.initial_frage_indices = list(frage_indices)  # Stabile Kopie für Nummerierung
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False
    st.session_state.optionen_shuffled = []
    st.session_state.answer_outcomes = []
    st.session_state.skipped_questions = []
    st.session_state.bookmarked_questions = []
    default_minutes = getattr(app_config, "test_duration_minutes", 60) if app_config else 60
    test_duration_minutes = question_set.get_test_duration_minutes(default_minutes)
    st.session_state.test_duration_minutes = test_duration_minutes
    st.session_state.test_time_limit = test_duration_minutes * 60
    st.session_state.test_time_expired = False
    st.session_state.question_set_meta = question_set.meta

    questions = list(question_set)
    for q in questions:
        opts = list(q.get("optionen", []))
        random.shuffle(opts)
        st.session_state.optionen_shuffled.append(opts)


def handle_user_session(questions: list, app_config: AppConfig) -> str | None:
    """
    Überprüft, ob ein Benutzer in der Session angemeldet ist.
    Gibt die user_id zurück, wenn ja, sonst None.
    Die UI-Logik für den Login befindet sich in `main_view.render_welcome_page`.
    """
    # log_state("Enter handle_user_session")
    if "user_id" in st.session_state:
        # log_state(f"User '{st.session_state.user_id}' found in session_state")
        return st.session_state.user_id
    
    if "session_aborted" in st.session_state:
        user_name = st.session_state.get("aborted_user_id", "Unbekannt")
        score = st.session_state.get("aborted_user_score", 0)
        made_it_to_leaderboard = st.session_state.get("aborted_user_on_leaderboard", False)

        if made_it_to_leaderboard:
            toast_message = f"🎉 Glückwunsch, {user_name}! Du hast es mit {score} Punkten ins Leaderboard geschafft!"
        else:
            duration = st.session_state.get("aborted_user_duration", 0)
            recommended_duration_seconds = st.session_state.get("aborted_user_recommended_duration", 180)

            # Definiere die Schwellenwerte
            MIN_SCORE_FOR_LEADERBOARD = 1
            # NEU: Mindestdauer ist 20% der empfohlenen Testzeit, aber mind. 60s
            MIN_DURATION_FOR_LEADERBOARD = max(60, int(recommended_duration_seconds * 0.20))

            # Prüfe die spezifischen Gründe
            if score < MIN_SCORE_FOR_LEADERBOARD:
                reason = f"da Ergebnisse mit 0 Punkten nicht gezählt werden."
            elif duration < MIN_DURATION_FOR_LEADERBOARD:
                min_duration_display = max(1, round(MIN_DURATION_FOR_LEADERBOARD / 60))
                reason = f"da die Testzeit zu kurz war (weniger als {min_duration_display} min)."
            else:
                reason = f"da die Punktzahl nicht für die Top 10 ausreichte."
            
            toast_message = f"Dein Ergebnis für »{user_name}« ist gespeichert, taucht aber nicht im Leaderboard auf, {reason}"

        st.toast(toast_message, icon="🏆", duration=10)
        del st.session_state["session_aborted"]
        if "aborted_user_id" in st.session_state:
            del st.session_state["aborted_user_id"]

    # log_state("Exit handle_user_session without login")
    return None


def is_admin_user(user_id: str, app_config: AppConfig) -> bool:
    """Prüft, ob der aktuelle Nutzer ein Admin ist."""
    return user_id.casefold() == app_config.admin_user.casefold()


def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    """
    Prüft den eingegebenen Admin-Key.
    Nutzt `hmac.compare_digest` für einen zeitkonstanten Vergleich.
    """
    if not provided_key or not app_config.admin_key:
        return False
    return hmac.compare_digest(provided_key.encode(), app_config.admin_key.encode())
