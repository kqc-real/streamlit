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

    if "session_aborted" in st.session_state:
        st.toast("Deine Antworten und Punkte sind gespeichert.", icon="💾")
        del st.session_state["session_aborted"]

    # --- Login-Prozess für neue Teilnehmer (jetzt der einzige Weg) ---
    st.sidebar.header("Neuen Test starten")
    st.sidebar.info("Wähle ein Pseudonym, um eine neue Testrunde zu beginnen. Jede Runde ist einmalig.")

    scientists = load_scientists()
    used_pseudonyms = get_used_pseudonyms()
    
    available_scientists = [
        f"{s['name']} ({s['contribution']})" for s in scientists 
        if s['name'] not in used_pseudonyms
    ]

    # Stelle sicher, dass der Admin-Benutzer immer als "Alan C. Kay" auswählbar ist.
    admin_user = app_config.admin_user
    admin_display_name = ""
    if admin_user:
        # Alan C. Kay: Pionier der objektorientierten Programmierung und grafischen Benutzeroberflächen.
        admin_display_name = "Alan C. Kay (Pionier der OOP & GUIs)"
        # Entferne den Admin aus der Liste, falls er als normaler User vorhanden ist
        available_scientists = [s for s in available_scientists if not s.startswith(admin_user) and not s.startswith("Alan C. Kay")]
        # Füge den Admin-Eintrag ganz vorne hinzu
        available_scientists.insert(0, admin_display_name)

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
            st.rerun()

        # Spezielle Behandlung für den Admin-Login
        if selected_name_formatted == admin_display_name:
            user_name = admin_user
        else:
            user_name = selected_name_formatted.split(" (")[0]

        st.session_state.user_id = user_name
        st.session_state.user_id_hash = get_user_id_hash(user_name)
        # st.session_state.user_id_display = st.session_state.user_id_hash[:10]
        
        st.session_state.show_pseudonym_reminder = True
        
        initialize_session_state(questions)
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
