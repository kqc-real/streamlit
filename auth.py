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

from config import AppConfig, load_scientists
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

def initialize_session_state(questions: list, app_config: AppConfig | None = None):
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

    st.session_state.beantwortet = [None] * len(questions)
    frage_indices = list(range(len(questions)))
    random.shuffle(frage_indices)
    st.session_state.frage_indices = frage_indices
    st.session_state.initial_frage_indices = list(frage_indices)  # Stabile Kopie für Nummerierung
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False
    st.session_state.optionen_shuffled = []
    st.session_state.answer_outcomes = []
    st.session_state.skipped_questions = []
    st.session_state.bookmarked_questions = []
    test_duration_minutes = 60
    if app_config is not None:
        try:
            parsed_minutes = int(getattr(app_config, "test_duration_minutes", test_duration_minutes))
            if parsed_minutes > 0:
                test_duration_minutes = parsed_minutes
        except (TypeError, ValueError):
            pass

    st.session_state.test_time_limit = test_duration_minutes * 60
    st.session_state.test_time_expired = False

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
        user_name = st.session_state.get("aborted_user_id", "Dein")
        toast_message = f"Dein Ergebnis für »{user_name}« wurde im Leaderboard gespeichert."
        st.toast(toast_message, icon="🏆")
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
