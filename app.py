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
if _this_dir not in sys.path:
    # Ensure the module directory itself is importable (affects Streamlit Cloud paths).
    sys.path.insert(0, _this_dir)
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
    _render_history_table,
)
from admin_panel import render_admin_panel
from components import render_sidebar, render_admin_switch

try:
    from helpers import is_request_from_localhost
except (ImportError, AttributeError):
    def is_request_from_localhost() -> bool:
        return False


def main():
    """Hauptfunktion der Streamlit-Anwendung."""
    st.set_page_config(
        page_title="MC-Test AMALEA",
        page_icon="🎓",
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
    
    # --- Startup-Check: Warnung, wenn keine Konfiguration vorhanden ist ---
    env_file_exists = os.path.exists(os.path.join(_this_dir, '.env'))
    secrets_file_exists = os.path.exists(os.path.join(_this_dir, '.streamlit', 'secrets.toml'))
    
    if not env_file_exists and not secrets_file_exists:
        st.warning(
            "⚠️ **Keine Konfigurationsdatei gefunden!**\n\n"
            "Die App benötigt entweder eine `.env`-Datei oder `.streamlit/secrets.toml` "
            "für die Konfiguration (Admin-Zugang, URL für QR-Code, etc.).\n\n"
            "**Für lokale Installation:**\n"
            "1. Kopiere `.env.example` zu `.env`:\n"
            "   ```bash\n"
            "   cp .env.example .env\n"
            "   ```\n"
            "2. Starte die App neu.\n\n"
            "**Details:** Siehe [INSTALLATION_ANLEITUNG.md](INSTALLATION_ANLEITUNG.md)"
        )

    # Initialisiere die Datenbank und erstelle Tabellen, falls nicht vorhanden.
    init_database()

    # --- 1. Lade Konfiguration und Fragen (wird für Login benötigt) ---
    app_config = AppConfig()
    st.session_state["app_config"] = app_config
    
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
    # Lade Fortschritt, entscheide ob die finale Zusammenfassung gezeigt wird,
    # setze ein Flag so die Sidebar sich entsprechend verhalten kann, und
    # rendere dann die Sidebar und die entsprechende Hauptansicht.
    is_admin = is_admin_user(user_id, app_config)

    # Decide whether the final summary will be shown. This mirrors the
    # later rendering logic so we can inform the sidebar to hide per-question
    # UI immediately (no extra rerun needed).
    try:
        test_time_expired = st.session_state.get("test_time_expired", False)
        finished = is_test_finished(questions)
        last_answered_idx = st.session_state.get("last_answered_idx")
        explanation_open = False
        if last_answered_idx is not None:
            explanation_open = bool(st.session_state.get(f"show_explanation_{last_answered_idx}"))
        will_show_final_summary = (
            test_time_expired
            or st.session_state.get("test_manually_ended", False)
            or (finished and not explanation_open)
        )
        st.session_state["in_final_summary"] = will_show_final_summary
    except Exception:
        # Fail-safe: ensure flag absent if computation fails
        st.session_state.pop("in_final_summary", None)

    render_sidebar(questions, app_config, is_admin)

    # If the sidebar requested the history dialog (one-time), show it here so
    # it is available in Review/Final-summary views as well. This mirrors the
    # logic in `render_question_view` to keep UX consistent across modes.
    try:
        if st.session_state.pop('_open_history_requested', False):
            from database import get_user_test_history

            user_key = st.session_state.get('user_id_hash') or st.session_state.get('user_id')
            history_rows = []
            if user_key:
                try:
                    history_rows = get_user_test_history(user_key)
                except Exception:
                    history_rows = []

            filename_base = f"history_{(st.session_state.get('user_id') or 'user')}"

            dialog_fn = getattr(st, 'dialog', None)
            if callable(dialog_fn):

                @dialog_fn("Meine Sessions")
                def _history_dialog():
                    _render_history_table(history_rows, filename_base)

                _history_dialog()
            else:
                with st.container(border=True):
                    st.header("Meine Sessions")
                    _render_history_table(history_rows, filename_base)
    except Exception:
        # Non-critical: history rendering must not block main app flow
        pass

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
    # Im unsicheren Modus (kein admin_key) erlauben wir Admin-Zugang ohne User-Check
    is_local_request = is_request_from_localhost()

    if st.session_state.get("show_admin_panel") and not is_local_request:
        # Remote Zugriff darf das Admin-Panel nicht offen halten.
        st.session_state.show_admin_panel = False

    should_show_admin = (
        st.session_state.get("show_admin_panel", False)
        and (not app_config.admin_key or is_admin)
        and is_local_request
    )
    
    if should_show_admin:
        # Phase 2: Server-side Session Validation (nur wenn admin_key gesetzt)
        if app_config.admin_key:
            from session_manager import verify_admin_session
            admin_token = st.session_state.get("admin_session_token")
            user_id = st.session_state.get("user_id", "")
            
            if not verify_admin_session(admin_token, user_id):
                st.error("⚠️ Ungültige oder abgelaufene Admin-Session. Bitte erneut einloggen.")
                st.session_state.show_admin_panel = False
                if "admin_session_token" in st.session_state:
                    del st.session_state["admin_session_token"]
                st.rerun()
        
        render_admin_panel(app_config, questions)
    # Priorität 2: Test ist beendet (und keine Detailanzeige mehr offen)
    # Wenn das Review/Erklärungs-Overlay für die letzte beantwortete Frage
    # noch aktiv ist, soll zuerst die Bewertungs-/Erklärungsanzeige gezeigt
    # werden. Nur wenn kein Erklärungs-Overlay aktiv ist, zeigen wir die
    # finale Zusammenfassung automatisch.
    # If the test time expired, show the final summary immediately (override any open overlays)
    elif st.session_state.get("test_time_expired", False):
        render_final_summary(questions, app_config)
    elif st.session_state.get("test_manually_ended", False) or (is_test_finished(questions) and not (
        "last_answered_idx" in st.session_state
        and st.session_state.get(f"show_explanation_{st.session_state.last_answered_idx}")
    )):
        # Wenn der Test beendet ist und kein Erklärungsoverlay offen, zeige die Zusammenfassung.
        render_final_summary(questions, app_config)
    # Priorität 3: Eine spezifische Frage anzeigen (entweder die letzte Antwort oder die nächste offene)
    elif current_idx is not None:
        render_question_view(questions, current_idx, app_config)
    else:
        # Fallback, falls kein Zustand zutrifft (sollte selten passieren)
        st.rerun()


if __name__ == "__main__":
    main()
