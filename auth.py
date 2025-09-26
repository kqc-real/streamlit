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

from config import AppConfig, load_scientists
from helpers import get_user_id_hash
from data_manager import get_used_pseudonyms


def initialize_session_state(questions: list):
    """Initialisiert den Session-State für einen neuen Testlauf."""
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


def handle_user_session(questions: list, app_config: AppConfig, question_files: list) -> str | None:
    """
    Verwaltet die User-Session. Zeigt Login an, wenn kein User angemeldet ist.
    Initialisiert die Session und gibt die `user_id` zurück.
    """
    if "user_id" in st.session_state:
        return st.session_state.user_id

    st.sidebar.header("Wer bist du?")

    login_type = st.radio(
        "Bist du ein neuer oder ein wiederkehrender Teilnehmer?",
        ["Neuer Teilnehmer", "Wiederkehrender Teilnehmer"],
        key="login_type",
        horizontal=True,
    )

    if "session_aborted" in st.session_state:
        st.toast("Deine Antworten und Punkte sind gespeichert.", icon="💾")
        del st.session_state["session_aborted"]

    if login_type == "Neuer Teilnehmer":
        scientists = load_scientists()
        used_pseudonyms = get_used_pseudonyms()
        
        available_scientists = [
            f"{s['name']} ({s['contribution']})" for s in scientists 
            if s['name'] not in used_pseudonyms
        ]

        if not available_scientists:
            st.sidebar.warning("Alle verfügbaren Pseudonyme sind bereits vergeben.")
            st.sidebar.info("Bitte kontaktiere den Autor der App, um die Liste zu erweitern.")
            return None

        selected_name_formatted = st.selectbox(
            "Wähle dein Pseudonym für diese Runde:",
            options=[""] + available_scientists,
            key="new_user_id_input",
            format_func=lambda x: "Bitte wählen..." if x == "" else x,
        )

        if st.sidebar.button("Test starten", key="start_new"):
            if not selected_name_formatted:
                st.sidebar.error("Bitte wähle ein Pseudonym aus.")
                return None

            user_name = selected_name_formatted.split(" (")[0]
            st.session_state.user_id = user_name
            st.session_state.user_id_hash = get_user_id_hash(user_name)
            st.session_state.user_id_display = st.session_state.user_id_hash[:10]
            
            st.info(f"Du hast das Pseudonym '{user_name}' gewählt. Bitte merke es dir gut, um deinen Test später fortsetzen zu können.")
            
            initialize_session_state(questions)
            st.rerun()

    else: # Wiederkehrender Teilnehmer
        used_pseudonyms = get_used_pseudonyms()
        if not used_pseudonyms:
            st.sidebar.info("Es gibt noch keine wiederkehrenden Teilnehmer.")
            return None

        entered_name = st.text_input(
            "Gib dein bisheriges Pseudonym ein:",
            key="returning_user_id_input",
        )

        if st.sidebar.button("Test fortsetzen", key="continue"):
            if not entered_name:
                st.sidebar.error("Bitte gib dein Pseudonym ein.")
                return None
            
            if entered_name not in used_pseudonyms:
                st.sidebar.error("Dieses Pseudonym wurde nicht gefunden. Überprüfe die Schreibweise oder registriere dich als neuer Teilnehmer.")
                return None

            st.session_state.user_id = entered_name
            st.session_state.user_id_hash = get_user_id_hash(entered_name)
            st.session_state.user_id_display = st.session_state.user_id_hash[:10]
            # Do not initialize, progress will be loaded in app.py
            st.rerun()

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
