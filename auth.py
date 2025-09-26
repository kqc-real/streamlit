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
from data_manager import get_used_pseudonyms

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

def initialize_session_state(questions: list):
    """Initialisiert den Session-State für einen neuen Testlauf."""
    log_state("Initializing new session state")
    # Lösche alte Test-spezifische Schlüssel, falls vorhanden
    for key in list(st.session_state.keys()):
        if key.startswith("frage_") or key in [
            "beantwortet", "frage_indices", "start_zeit", "progress_loaded", 
            "optionen_shuffled", "answer_outcomes", "bookmarked_questions", 
            "test_time_expired", "show_pseudonym_reminder", "login_attempts"
        ]:
            del st.session_state[key]

    st.session_state.beantwortet = [None] * len(questions)
    st.session_state.frage_indices = list(range(len(questions)))
    random.shuffle(st.session_state.frage_indices)
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False
    st.session_state.optionen_shuffled = []
    st.session_state.answer_outcomes = []
    st.session_state.bookmarked_questions = []
    st.session_state.test_time_limit = 60 * 60  # 60 Minuten in Sekunden
    st.session_state.test_time_expired = False

    for q in questions:
        opts = list(q.get("optionen", []))
        random.shuffle(opts)
        st.session_state.optionen_shuffled.append(opts)


def handle_user_session(questions: list, app_config: AppConfig) -> str | None:
    """
    Rendert die Login-Seite, wenn kein Benutzer eingeloggt ist.
    Gibt die user_id zurück, wenn der Login erfolgreich war.
    """
    log_state("Enter handle_user_session")
    if "user_id" in st.session_state:
        log_state(f"User '{st.session_state.user_id}' found in session_state")
        return st.session_state.user_id

    st.title("Willkommen zum MC-Test")
    st.write("Bitte melde dich an, um zu beginnen.")

    login_type = st.radio(
        "Login-Typ",
        ["Neuer Teilnehmer", "Wiederkehrender Teilnehmer"],
        key="login_type",
        horizontal=True,
        label_visibility="collapsed"
    )

    if login_type == "Neuer Teilnehmer":
        scientists = load_scientists()
        used_pseudonyms = get_used_pseudonyms()
        
        available_scientists = [
            f"{s['name']} ({s['contribution']})" for s in scientists 
            if s['name'] not in used_pseudonyms
        ]

        if not available_scientists:
            st.warning("Alle verfügbaren Pseudonyme sind bereits vergeben.")
            st.info("Bitte kontaktiere den Autor der App, um die Liste zu erweitern.")
            return None

        selected_name_formatted = st.selectbox(
            "Wähle dein Pseudonym für diese Runde:",
            options=[""] + available_scientists,
            key="new_user_id_input",
            format_func=lambda x: "Bitte wählen..." if x == "" else x,
        )

        if st.button("Test starten", key="start_new"):
            if not selected_name_formatted:
                st.error("Bitte wähle ein Pseudonym aus.")
            else:
                user_name = selected_name_formatted.split(" (")[0]
                st.session_state.user_id = user_name
                st.session_state.user_id_hash = get_user_id_hash(user_name)
                st.session_state.user_id_display = st.session_state.user_id_hash[:10]
                st.session_state.show_pseudonym_reminder = True
                initialize_session_state(questions)
                log_state("New user login -> RERUN")
                st.rerun()

    else: # Wiederkehrender Teilnehmer
        used_pseudonyms = get_used_pseudonyms()
        if not used_pseudonyms:
            st.info("Es gibt noch keine wiederkehrenden Teilnehmer.")
            return None

        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        
        MAX_LOGIN_ATTEMPTS = 5
        is_locked = st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS

        entered_name = st.text_input(
            "Gib dein bisheriges Pseudonym ein (genaue Schreibweise beachten):",
            key="returning_user_id_input",
            disabled=is_locked,
        )

        if st.button("Test fortsetzen", key="continue", disabled=is_locked):
            clean_entered_name = entered_name.strip()
            if not clean_entered_name:
                st.error("Bitte gib dein Pseudonym ein.")
            
            elif clean_entered_name not in used_pseudonyms:
                st.session_state.login_attempts += 1
                remaining_attempts = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                log_state(f"Wrong pseudonym: '{clean_entered_name}'")
                if remaining_attempts > 0:
                    st.error(f"Pseudonym nicht gefunden. Achte auf die genaue Schreibweise. Du hast noch {remaining_attempts} Versuche.")
                else:
                    st.error("Zu viele Fehlversuche. Der Login ist gesperrt.")
            else:
                st.session_state.login_attempts = 0
                st.session_state.user_id = clean_entered_name
                st.session_state.user_id_hash = get_user_id_hash(clean_entered_name)
                st.session_state.user_id_display = st.session_state.user_id_hash[:10]
                initialize_session_state(questions)
                log_state(f"Returning user login: '{clean_entered_name}' -> RERUN")
                st.rerun()
            
        if is_locked:
            st.error("Zu viele Fehlversuche. Der Login ist gesperrt.")

    log_state("Exit handle_user_session without login")
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


def handle_admin_login(app_config: AppConfig):
    """Zeigt das Admin-Login-Formular in der Sidebar an."""
    with st.sidebar.expander("🔐 Admin Login", expanded=False):
        if not app_config.admin_key:
            st.caption("Kein Admin-Key konfiguriert.")
            return

        entered_key = st.text_input("Admin-Key", type="password", key="admin_key_input")
        if st.button("Aktivieren", key="admin_activate_btn"):
            if check_admin_key(entered_key, app_config):
                st.session_state["show_admin_panel"] = True
                st.rerun()
            else:
                st.error("Falscher Key.")
