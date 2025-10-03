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
from dotenv import load_dotenv
import locale
import os

# --- Pfad-Setup für robuste Imports (Workaround für ältere Streamlit-Versionen) ---
# Dieser Block stellt sicher, dass die App als Skript ausgeführt werden kann,
# indem er das Projektverzeichnis zum Suchpfad hinzufügt.
_this_dir = os.path.dirname(__file__)
_parent_dir = os.path.abspath(os.path.join(_this_dir, '..'))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from config import AppConfig, load_questions, list_question_files
from database import init_database
from auth import handle_user_session, is_admin_user
from logic import (
    get_current_question_index,
    is_test_finished,
)
from main_view import (
    render_question_view,
    render_final_summary,
    render_welcome_page,
)
from admin_panel import render_admin_panel
from components import render_sidebar, render_admin_switch


def main():
    """Hauptfunktion der Streamlit-Anwendung."""
    st.set_page_config(
        page_title="MC-Test AMALEA",
        layout="centered",
        # Legt den initialen Zustand der Sidebar fest.
        initial_sidebar_state="expanded"  # "collapsed" oder "expanded"
    )

    # Setze das Locale, um eine korrekte alphabetische Sortierung von Namen
    # mit Akzenten und Umlauten zu gewährleisten (z.B. 'Erwin' bei 'E').
    # Wir probieren eine Liste von Locales durch, um die Portabilität zu erhöhen.
    # 'de_DE.UTF-8' ist ideal, aber nicht überall verfügbar (z.B. in manchen Docker-Images).
    # 'C.UTF-8' ist ein guter, moderner Fallback in POSIX-Systemen.
    possible_locales = [
        'de_DE.UTF-8',  # Linux/macOS
        'de-DE.UTF-8',  # Alternative Schreibweise
        'German_Germany.1252',  # Windows
        'de_DE',
        'de',
        'C.UTF-8',  # Moderner POSIX-Standard, guter Fallback
        'en_US.UTF-8'  # Häufig verfügbarer Fallback
    ]
    for loc in possible_locales:
        try:
            locale.setlocale(locale.LC_COLLATE, loc)
            break  # Erfolgreich, Schleife verlassen
        except locale.Error:
            continue  # Nächstes Locale probieren
    else:  # Wird ausgeführt, wenn die Schleife nie durch 'break' verlassen wurde
        st.warning("Kein passendes Locale für korrekte Sortierung gefunden. Umlaute werden evtl. falsch sortiert.")

    # Lade Umgebungsvariablen aus der .env-Datei (für lokale Entwicklung)
    load_dotenv()

    # Initialisiere die Datenbank und erstelle Tabellen, falls nicht vorhanden.
    init_database()

    # --- 1. Lade Konfiguration und Fragen (wird für Login benötigt) ---
    app_config = AppConfig()
    
    # Initialisiere das Fragenset, falls noch nicht geschehen.
    if "selected_questions_file" not in st.session_state:
        question_files = list_question_files()
        st.session_state.selected_questions_file = question_files[0] if question_files else None

    if st.session_state.get("selected_questions_file"):
        questions = load_questions(st.session_state.get("selected_questions_file"))
    else:
        st.error("Keine Fragensets (questions_*.json) gefunden.")
        st.stop()

    # --- 2. Authentifizierung: Zeigt Login-Seite oder gibt user_id zurück ---
    user_id = handle_user_session(questions, app_config)

    if not user_id:
        # handle_user_session rendert die Login-Seite, hier abbrechen.
        render_welcome_page(app_config)
        st.stop()

    # --- 3. Hauptanwendung für eingeloggte Benutzer ---
    # Lade Fortschritt, zeige Sidebar und die entsprechende Hauptansicht
    is_admin = is_admin_user(user_id, app_config)
    render_sidebar(questions, app_config, is_admin)

    # --- 4. Zeitstempel für Test-Dauer setzen ---
    # Setze Startzeit beim ersten Aufruf (wenn erste Frage geladen wird)
    if "test_start_time" not in st.session_state:
        from datetime import datetime
        st.session_state.test_start_time = datetime.now()
    
    # Setze Endzeit, wenn Test abgeschlossen ist
    if is_test_finished(questions) and "test_end_time" not in st.session_state:
        from datetime import datetime
        st.session_state.test_end_time = datetime.now()

    # --- 5. Logik zur Bestimmung der anzuzeigenden Frage ---
    current_idx = None
    if "jump_to_idx" in st.session_state:
        # Priorität 1: Sprung von einem Bookmark
        current_idx = st.session_state.jump_to_idx
        del st.session_state.jump_to_idx
    elif "last_answered_idx" in st.session_state and st.session_state.get(f"show_explanation_{st.session_state.last_answered_idx}"):
        # Priorität 2: Bleibe auf der letzten Frage, um die Erklärung anzuzeigen
        current_idx = st.session_state.last_answered_idx
        # Lösche den Marker, damit beim Klick auf "Nächste Frage" normal weitergemacht wird.
        if not st.session_state.get(f"show_explanation_{current_idx}"):
             del st.session_state.last_answered_idx
    else:
        # Priorität 3: Finde die nächste unbeantwortete Frage
        current_idx = get_current_question_index()

    # --- 5. Rendere die passende Hauptansicht basierend auf der Priorität ---
    
    # Priorität 1: Admin-Panel anzeigen
    if st.session_state.get("show_admin_panel", False) and is_admin:
        render_admin_panel(app_config, questions)
    # Priorität 2: Eine spezifische Frage anzeigen (entweder die nächste oder ein Sprungziel)
    elif current_idx is not None:
        render_question_view(questions, current_idx, app_config)
    # Priorität 3: Test ist beendet (und es gibt kein Sprungziel)
    elif is_test_finished(questions) or st.session_state.get("test_time_expired", False):
        # Wenn der Test beendet ist, zeige immer die Zusammenfassung.
        # Die Logik für den Review-Modus ist in render_final_summary enthalten.
        render_final_summary(questions, app_config)
    else:
        # Fallback, falls kein Zustand zutrifft (sollte selten passieren)
        st.rerun()


if __name__ == "__main__":
    main()