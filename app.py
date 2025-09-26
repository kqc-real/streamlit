"""
Haupt-App-Datei für den MC-Test.

Diese Datei orchestriert den App-Ablauf, indem sie Funktionen aus den
modularen Komponenten aufruft. Sie enthält selbst kaum noch Logik.

Struktur:
1. Initialisierung und Konfiguration laden.
2. Benutzer-Authentifizierung und Session-Management.
3. Hauptansicht rendern (Start, Frage, Ende oder Admin-Panel).

Ausführung: streamlit run app.py
"""
import streamlit as st
import sys
import os

# --- Pfad-Setup für robuste Imports (Workaround für ältere Streamlit-Versionen) ---
# Dieser Block stellt sicher, dass die App als Skript ausgeführt werden kann,
# indem er das Projektverzeichnis zum Suchpfad hinzufügt.
_this_dir = os.path.dirname(__file__)
_parent_dir = os.path.abspath(os.path.join(_this_dir, '..'))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from config import AppConfig, load_questions, list_question_files
from auth import handle_user_session, is_admin_user
from logic import (
    get_current_question_index,
    is_test_finished,
    load_user_progress,
)
from main_view import (
    render_welcome_page,
    render_question_view,
    render_final_summary,
)
from admin_panel import render_admin_panel
from components import render_sidebar


def set_custom_theme():
    """Fügt benutzerdefiniertes CSS hinzu, um das Design anzupassen."""
    st.markdown(
        """
<style>
    /* Haupt-Layout und Hintergrund */
    .stApp {
        background-color: #0e1117;
    }
    /* Haupt-Textfarbe - nicht grell weiß */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #d1d1d1;
    }
    /* Überschriften in Akzentfarbe */
    .stApp h1, .stApp h2 {
        color: #4b9fff;
    }
    .stApp h3 {
        color: #a1cfff;
    }
    /* Zentriertes Layout für Mobile-First-Gefühl */
    .main .block-container {
        max-width: 730px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Container für Fragen */
    .st-emotion-cache-1r4qj8v {
        border: 1px solid #2a394f;
    }
    /* Spezielle Klasse für scrollbare KaTeX-Blöcke in Spalten */
    div[data-testid="column"]:has(div.scrollable-katex) {
        overflow-x: auto;
        white-space: nowrap;
        padding: 5px;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def main():
    """Hauptfunktion der Streamlit-Anwendung."""
    st.set_page_config(page_title="MC-Test AMALEA")
    set_custom_theme()

    # --- 1. Initialisierung & Konfiguration ---
    # Lade App-Konfiguration (Scoring-Modus etc.) und verfügbare Fragensets
    app_config = AppConfig()
    question_files = list_question_files()

    # Initialisiere `selected_questions_file` im Session State, falls nicht vorhanden
    if "selected_questions_file" not in st.session_state:
        st.session_state.selected_questions_file = (
            question_files[0] if question_files else None
        )

    # Lade die Fragen für das aktuell ausgewählte Set
    if st.session_state.selected_questions_file:
        questions = load_questions(st.session_state.selected_questions_file)
    else:
        questions = []
        st.error("Keine Fragensets (questions_*.json) gefunden.")
        st.stop()

    # --- 2. Benutzer-Authentifizierung & Session-Management ---
    # `handle_user_session` kümmert sich um Login, Session-Initialisierung
    # und das Laden von Fortschritt. Gibt `user_id` zurück oder None.
    user_id = handle_user_session(questions, app_config, question_files)

    if not user_id:
        # Wenn kein Nutzer angemeldet ist, zeige nur die Startseite.
        # Die Login-Logik befindet sich in `handle_user_session`.
        render_welcome_page(app_config)
        st.stop()

    # --- 3. Hauptansicht rendern ---
    # Ab hier ist ein Nutzer (oder Admin) angemeldet.

    # Lade den Fortschritt des Nutzers, falls vorhanden.
    # Dies geschieht nur einmal pro Session, um unnötige Lesezugriffe zu vermeiden.
    if not st.session_state.get("progress_loaded", False):
        load_user_progress(st.session_state.user_id_hash, questions)
        st.session_state.progress_loaded = True

    # Überprüfe, ob der angemeldete Nutzer Admin-Rechte hat.
    is_admin = is_admin_user(user_id, app_config)

    # Zeige die Sidebar mit Fortschritt, Bookmarks und Admin-Login an.
    render_sidebar(questions, app_config, is_admin)

    # Entscheide, welche Hauptansicht gezeigt wird.
    if st.session_state.get("show_admin_panel", False) and is_admin:
        # A) Admin-Panel anzeigen
        render_admin_panel(app_config, questions)

    elif is_test_finished(questions) or st.session_state.get("test_time_expired", False):
        # B) Test ist beendet -> Zeige die finale Zusammenfassung
        render_final_summary(questions, app_config)

    else:
        # C) Test läuft -> Zeige die aktuelle Frage
        current_idx = get_current_question_index()
        if current_idx is not None:
            render_question_view(questions, current_idx, app_config)
        else:
            # Sollte nicht passieren, aber als Fallback
            st.info("Alle Fragen beantwortet. Lade die Zusammenfassung...")
            st.rerun()


if __name__ == "__main__":
    main()