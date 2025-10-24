"""
Modul für die Hauptansichten der Nutzer-Interaktion.

Verantwortlichkeiten:
- Rendern der Fragenansicht.
- Rendern der finalen Zusammenfassung.
"""
import os
import streamlit as st
import pandas as pd
import time
import re
import locale
import math

from config import (
    AppConfig,
    list_question_files,
    load_questions,
    get_question_counts,
    QuestionSet,
    get_package_dir,
    AppConfig,
)
from logic import (
    calculate_score,
    set_question_as_answered,
    get_answer_for_question,
    is_test_finished,
)
from helpers import (
    smart_quotes_de,
    get_user_id_hash,
    format_decimal_de,
    load_markdown_file,
    ACTIVE_SESSION_QUERY_PARAM,
)
from database import update_bookmarks
from components import render_question_distribution_chart
import logging


def _format_minutes_text(minutes: int) -> str:
    """Gibt eine sprachlich passende Darstellung für Minuten zurück."""
    value = max(1, minutes)
    return f"{value} min"


def _format_countdown_warning_de(remaining_seconds: int, neutral_window_seconds: int = 5) -> str | None:
    """
    Formatiert eine deutsche Countdown-Warnung gemäß der gewünschten Sprachregel.

    Rückgabe:
        - String mit Warntext (inkl. "Achtung, ..."), oder
        - None, falls keine Warnung angezeigt werden soll (z. B. > 5 min Restzeit).
    """
    if remaining_seconds <= 0:
        return None
    if remaining_seconds <= 60:
        return "⚠️ Achtung, nur noch wenige Sekunden!"
    if remaining_seconds > 5 * 60:
        return None

    minutes_floor = remaining_seconds // 60
    seconds = remaining_seconds % 60
    closest_minute = max(1, math.floor(remaining_seconds / 60 + 0.5))
    diff_to_closest = abs(remaining_seconds - closest_minute * 60)

    if diff_to_closest <= neutral_window_seconds:
        minutes_text = _format_minutes_text(closest_minute)
        if remaining_seconds < closest_minute * 60:
            return f"Achtung, nur noch knapp {minutes_text}!"
        if diff_to_closest == 0:
            return f"Achtung, nur noch genau {minutes_text}!"
        return f"Achtung, noch rund {minutes_text}!"

    if seconds <= 29:
        minutes_text = _format_minutes_text(max(1, minutes_floor))
        return f"⚠️ Achtung, noch gut {minutes_text}!"

    next_minute = minutes_floor + 1
    minutes_text = _format_minutes_text(next_minute)
    prefix = "nur noch" if remaining_seconds < next_minute * 60 else "noch"
    return f"⚠️ Achtung, {prefix} knapp {minutes_text}!"


def _steps_have_numbering(steps: list) -> bool:
    """Prüft, ob in einer Liste von Schritt‑Strings eine Nummerierung vorgegeben ist.

    Liefert True, sobald mindestens ein Eintrag eine führende Nummerierung wie "1. ", "1) " o.Ä. enthält.
    """
    if not steps or not isinstance(steps, list):
        return False
    numbered_count = 0
    for s in steps:
        if isinstance(s, str) and re.match(r"^\s*\d+[\.|\)]\s+", s):
            numbered_count += 1
    return numbered_count >= 1


def _strip_leading_numbering(text: str) -> str:
    """
    Entfernt führende Nummerierung wie "1. " oder "1) " aus einem Schritt-String.
    """
    if not isinstance(text, str):
        return text
    return re.sub(r'^\s*\d+[\.\)]\s+', '', text)


def _sync_questions_query_param(selected_file: str):
    """Synchronisiert die Query-Parameter mit der aktuellen Fragenset-Auswahl."""
    current_value = st.query_params.get("questions_file")
    if isinstance(current_value, list):
        current_value = current_value[0] if current_value else None
    if current_value == selected_file:
        return
    st.query_params["questions_file"] = selected_file


# --- queued rerun handler -------------------------------------------------
# Some environments or Streamlit builds may not expose experimental_rerun.
# To support callers that set a flag (st.session_state["_needs_rerun"] = True)
# we check the flag once at module import / first render and invoke the
# experimental rerun when available. This provides a reliable fallback
# for deployments where an immediate rerun cannot be executed in the
# same code path that updated session_state.
try:
    if st.session_state.pop("_needs_rerun", False):
        rerun_fn = getattr(st, "experimental_rerun", None)
        if callable(rerun_fn):
            try:
                rerun_fn()
            except Exception:
                logging.exception("queued experimental_rerun failed")
        else:
            logging.debug("queued rerun requested but experimental_rerun not available")
except Exception:
    # session_state may not be fully initialized during some import paths;
    # ignore and continue — the UI will render normally.
    pass


def _render_welcome_splash():
    """Zeigt beim ersten Aufruf der Startseite einen Willkommen-Splash an."""
    if st.session_state.get("_welcome_splash_dismissed", False):
        return

    splash_path = os.path.join(get_package_dir(), "docs", "welcome_splash.md")
    splash_content = load_markdown_file(splash_path)
    if not splash_content:
        # Wenn keine Inhalte vorliegen, den Splash überspringen, um Blockaden zu vermeiden.
        st.session_state._welcome_splash_dismissed = True
        return

    st.markdown(
        """
        <style>
        [data-testid="stDialogContent"] .splash-scroll {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        .splash-fallback {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    dialog_func = getattr(st, "dialog", None)
    if callable(dialog_func):

        @dialog_func("🎓 MC-Test App")
        def _welcome_dialog():
            st.markdown('<div class="splash-scroll">', unsafe_allow_html=True)
            st.markdown(splash_content)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("🚀 Los geht’s", type="primary", width="stretch"):
                st.session_state._welcome_splash_dismissed = True
                st.rerun()

        _welcome_dialog()
    else:
        st.markdown('<div class="splash-fallback">', unsafe_allow_html=True)
        st.markdown(splash_content)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 Los geht’s", type="primary", width="stretch"):
            st.session_state._welcome_splash_dismissed = True
            st.rerun()

        st.stop()


def render_welcome_page(app_config: AppConfig):
    """Zeigt die Startseite für nicht eingeloggte Nutzer."""

    # --- Fragenset-Vorauswahl (Session-State + Query-Parameter) ---
    available_question_files = list_question_files()

    if not available_question_files:
        st.error("Keine Fragensets (z.B. `questions_Data_Science.json`) gefunden.")
        st.info("Stelle sicher, dass gültige, nicht-leere JSON-Dateien mit Fragen im Projektverzeichnis liegen.")
        return

    query_params = st.query_params
    previous_session_marker = query_params.get(ACTIVE_SESSION_QUERY_PARAM)
    if previous_session_marker and "session_id" not in st.session_state:
        st.warning(
            "⚠️ Deine letzte Sitzung ist abgelaufen. Bitte Seite neu laden oder einen neuen Test starten."
        )
        query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)
        st.session_state["_welcome_splash_dismissed"] = True

    requested_file = query_params.get("questions_file")
    if isinstance(requested_file, list):
        requested_file = requested_file[0] if requested_file else None

    if requested_file and requested_file in available_question_files:
        st.session_state.selected_questions_file = requested_file
    elif (
        "selected_questions_file" not in st.session_state
        or st.session_state.selected_questions_file not in available_question_files
    ):
        st.session_state.selected_questions_file = available_question_files[0]

    selected_file = st.session_state.get("selected_questions_file")
    if not selected_file:
        st.error("Konnte kein gültiges Fragenset bestimmen.")
        return

    _sync_questions_query_param(selected_file)
    _render_welcome_splash()

    # --- Dynamischer Titel und Willkommensnachricht ---
    # Der Titel wird aus dem ausgewählten Dateinamen generiert, der im Session State liegt.
    dynamic_title = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    st.markdown(f"""
        <div style='text-align: center; padding: 0 0 10px 0;'>
            <h1 style='color:#4b9fff; font-size: clamp(2.5rem, 5vw, 2.1rem);'>MC-Test</h1>
            <h1 style='font-size: clamp(1.8rem, 7vw, 2.8rem); margin-top: -1.0rem;'>{dynamic_title}</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- Auswahl des Fragensets (mit Filterung) ---
    # Nutze die optimierte Funktion, um die Anzahl der Fragen zu bekommen.
    question_counts = get_question_counts()
    valid_question_files = sorted(question_counts.keys())

    if not valid_question_files:
        st.error("Keine Fragensets (z.B. `questions_Data_Science.json`) gefunden.")
        st.info("Stelle sicher, dass gültige, nicht-leere JSON-Dateien mit Fragen im Projektverzeichnis liegen.")
        return

    # Lade Metadaten (z.B. empfohlene Testdauer) für alle Sets vorab.
    question_set_cache: dict[str, "QuestionSet"] = {}
    question_durations: dict[str, int] = {}
    default_duration = app_config.test_duration_minutes
    for filename in valid_question_files:
        question_set = load_questions(filename, silent=True)
        question_set_cache[filename] = question_set
        question_durations[filename] = question_set.get_test_duration_minutes(default_duration)

    # Erstelle eine benutzerfreundlichere Anzeige für die Dateinamen
    def format_filename(filename):
        name = filename.replace("questions_", "").replace(".json", "").replace("_", " ")
        num_questions = question_counts.get(filename)
        return f"{name} ({num_questions} Fragen)" if num_questions else name

    st.markdown(
        "<h3 style='text-align: center; margin-top: 1.5rem;'>Wähle dein Fragenset</h3>",
        unsafe_allow_html=True,
    )

    current_selection = st.session_state.get("selected_questions_file", valid_question_files[0])
    selected_choice = st.selectbox(
        "Wähle ein Fragenset:",
        options=valid_question_files,
        index=valid_question_files.index(current_selection) if current_selection in valid_question_files else 0,
        format_func=format_filename,
        key="main_view_question_file_selector",
        label_visibility="collapsed"
    )

    if selected_choice != st.session_state.get("selected_questions_file"):
        st.session_state.selected_questions_file = selected_choice
        _sync_questions_query_param(selected_choice)
        st.rerun()
        return
    selected_file = st.session_state.get("selected_questions_file")

    selected_question_set = question_set_cache.get(selected_file)
    if selected_question_set:
        duration = question_durations.get(selected_file)
        difficulty_profile = selected_question_set.meta.get("difficulty_profile", {})
        difficulty_parts: list[str] = []
        difficulty_labels = {
            "leicht": "leicht",
            "mittel": "mittel",
            "schwer": "schwer",
        }
        for key, label in difficulty_labels.items():
            count = difficulty_profile.get(key)
            if count:
                difficulty_parts.append(f"- {count} × {label}")
        info_suffix = f" · Schwierigkeitsmix:\n{chr(10).join(difficulty_parts)}" if difficulty_parts else ""
        if duration:
            st.caption(f"⏱️ Empfohlene Testzeit: {duration} min{info_suffix}")
        elif difficulty_parts:
            st.caption(f"Schwierigkeitsmix:\n{chr(10).join(difficulty_parts)}")

    if selected_question_set is not None:
        questions = selected_question_set
    else:
        questions = load_questions(selected_file)

    # --- Diagramm zur Verteilung der Fragen ---
    with st.expander("⚖️ Fragen nach Thema und Schwierigkeit", expanded=False):
        if questions:
            render_question_distribution_chart(list(questions))
        else:
            st.warning("⚠️ Das ausgewählte Fragenset ist leer oder konnte nicht geladen werden.")

    # --- Öffentliches Leaderboard ---
    if app_config.show_top5_public:
        # Berechne die maximale Punktzahl für das ausgewählte Set
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions)
        leaderboard_title = f"🏆 Aktuelle Top 10 (max. {max_score_for_set} Punkte)"
        with st.expander(leaderboard_title, expanded=False):
            from database import get_all_logs_for_leaderboard
            
            leaderboard_data = get_all_logs_for_leaderboard(selected_file)

            if not leaderboard_data:
                st.info("Noch keine Ergebnisse für dieses Fragenset")
            else:
                scores = pd.DataFrame(leaderboard_data)
                scores = scores[~((scores["total_score"] == 0) & (scores["duration_seconds"] == 0))]
                # Blende Durchläufe ohne erzielte Punkte aus dem öffentlichen Leaderboard aus
                scores = scores[scores["total_score"] > 0]
                # Filtere Sessions unter 3 min heraus, um überstürzte Abgaben zu vermeiden.
                # NEU: Mindestdauer ist 20% der empfohlenen Testzeit, aber mind. 60s
                recommended_duration_minutes = question_durations.get(selected_file, app_config.test_duration_minutes)
                min_duration_seconds = max(60, int(recommended_duration_minutes * 60 * 0.20))
                
                scores = scores[scores["duration_seconds"] >= min_duration_seconds]
                scores = scores.reset_index(drop=True)
                if scores.empty:
                    st.info("Noch keine Ergebnisse für dieses Fragenset")
                else:
                    # Prozentzahl berechnen und als neue Spalte einfügen
                    max_score = max_score_for_set if max_score_for_set > 0 else 1
                    # Nutze den originalen Spaltennamen für die Berechnung
                    if 'total_score' in scores.columns:
                        scores['percent'] = scores['total_score'].apply(lambda x: f"{round((x / max_score) * 100)} %")
                    else:
                        scores['percent'] = "-"

                    # Formatiere die Dauer als Kombination aus Minuten und Sekunden
                    def format_duration(seconds):
                        mins, secs = divmod(seconds, 60)
                        parts = []
                        if mins:
                            parts.append(f"{int(mins)} min")
                        if secs or not parts:
                            parts.append(f"{int(secs)} s")
                        return " ".join(parts)
                    scores['duration_seconds'] = scores['duration_seconds'].apply(format_duration)

                    # Formatiere das Datum
                    scores["last_test_time"] = pd.to_datetime(scores["last_test_time"]).dt.strftime('%d.%m.%y')

                    # Spalten für Anzeige umbenennen
                    scores.rename(columns={
                        'user_pseudonym': '👤 Pseudonym',
                        'percent': '🏅 %',
                        'last_test_time': '📅 Datum',
                        'duration_seconds': '⏱️ Dauer',
                    }, inplace=True)

                    # Dekoriere die Top 3 mit Icons und nummeriere den Rest
                    icons = ["🥇", "🥈", "🥉"]
                    for i in range(len(scores)):
                        if i < len(icons):
                            scores.loc[i, "👤 Pseudonym"] = f"{icons[i]} {scores.loc[i, '👤 Pseudonym']}"
                        else:
                            scores.loc[i, "👤 Pseudonym"] = f"{i + 1}. {scores.loc[i, '👤 Pseudonym']}"

                    st.dataframe(
                        scores[["👤 Pseudonym", "🏅 %", "⏱️ Dauer", "📅 Datum"]],
                        width="stretch",
                        hide_index=True,
                    )


    # --- Login-Formular im Hauptbereich ---
    from auth import initialize_session_state, is_admin_user
    from config import load_scientists
    from database import get_used_pseudonyms

    st.markdown("<h3 style='text-align: center; margin-top: 1.5rem;'>Wähle dein Pseudonym</h3>", unsafe_allow_html=True)

    scientists = load_scientists()
    used_pseudonyms = get_used_pseudonyms()

    # Erstelle eine Liste der verfügbaren Wissenschaftler-Objekte
    available_scientists_obj = [s for s in scientists if s['name'] not in used_pseudonyms]

    # Stelle sicher, dass der Admin-Benutzer immer auswählbar ist,
    # auch wenn er bereits einen Test gemacht hat.
    admin_user = app_config.admin_user
    if admin_user:
        admin_scientist = next((s for s in scientists if s['name'] == admin_user), None)
        # Füge den Admin hinzu, falls er nicht bereits in der verfügbaren Liste ist
        if admin_scientist and admin_scientist not in available_scientists_obj:
            available_scientists_obj.append(admin_scientist)

    # Sortiere die Objekte alphabetisch nach dem Namen
    # Wichtig: Die Sortierung muss nach dem Hinzufügen des Admins erfolgen.
    available_scientists_obj.sort(key=lambda s: locale.strxfrm(s['name']))

    # Erstelle die Optionen für das Selectbox (nur die Namen).
    options = [s['name'] for s in available_scientists_obj]
    # Erstelle eine Map von allen Wissenschaftlern für die Formatierungsfunktion.
    # Diese muss *alle* Wissenschaftler enthalten, nicht nur die verfügbaren,
    # damit die Formatierung immer funktioniert.
    scientist_map = {s['name']: s['contribution'] for s in scientists}

    def format_scientist(name):
        contribution = scientist_map.get(name, "")
        return f"{name} ({contribution})" if contribution else name

    # Prüfe, ob überhaupt Optionen verfügbar sind, bevor das selectbox gerendert wird.
    if not options:
        st.warning("⚠️ Alle verfügbaren Pseudonyme sind bereits in Verwendung. Bitte kontaktiere den Admin.")
        selected_name_from_user = None
    else:
        selected_name_from_user = st.selectbox(
            "Wähle dein Pseudonym für diese Runde:",
            options=options,
            index=0,  # Wählt das erste Element als Standard aus
            format_func=format_scientist,
            label_visibility="collapsed" # Optional: Blendet das Label aus, falls gewünscht
        )

    _, col2, _ = st.columns([2, 1.5, 2])
    with col2:
        # Deaktiviere den Button, wenn keine Auswahl möglich ist.
        if st.button(
            "Test starten",
            type="primary",
            width="stretch",
            disabled=(not selected_name_from_user),
        ):
            from database import add_user, start_test_session
            user_name = selected_name_from_user
            user_id_hash = get_user_id_hash(user_name)

            add_user(user_id_hash, user_name)
            session_id = start_test_session(user_id_hash, st.session_state.selected_questions_file)

            if session_id:
                st.session_state.user_id = user_name
                st.session_state.user_id_hash = user_id_hash
                st.session_state.session_id = session_id
                st.session_state.show_pseudonym_reminder = True
                query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                initialize_session_state(questions, app_config)
                st.rerun()
            else:
                st.error("Datenbankfehler: Konnte keine neue Test-Session starten.")

def _show_welcome_container(app_config: AppConfig):
    """Zeigt die Welcome-Message in einem hervorgehobenen Container."""
    # Testzeit berechnen (in min)
    test_time_minutes = int(st.session_state.test_time_limit / 60)
    
    if app_config.scoring_mode == "positive_only":
        scoring_text = (
            "Für eine richtige Antwort erhältst du Punkte gmäß der Gewichtung, "
            "für eine falsche 0 Punkte."
        )
    else:
        scoring_text = "Richtig: +Gewichtung, falsch: -Gewichtung."
    
    # Großer, zentraler Container mit klarer Aufforderung
    st.markdown("<br>" * 3, unsafe_allow_html=True)  # Abstand nach oben
    
    with st.container(border=True):
        st.markdown(f"""
        ### ⏱️ Testzeit
        Du hast **{test_time_minutes} min** für den Test.  
        Der Countdown startet, sobald du auf »Test beginnen« klickst und aktualisiert sich mit jeder Frage.
        
        ### ✅ 1 richtige Option
        Wähle mit Bedacht, du hast keine zweite Chance pro Frage.
        
        ### 🎯 Punktelogik
        {scoring_text}
        """)
        
        st.info(
            "💡 **Tipp:** In der Sidebar ( **»** oben links) findest du deinen Fortschritt, "
            "Punktestand und die markierten und übersprungenen Fragen."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Test beginnen", type="primary", width="stretch"):
            st.session_state.test_started = True
            # Starte den Countdown sofort
            st.session_state.start_zeit = pd.Timestamp.now()
            st.rerun()

def render_question_view(questions: QuestionSet, frage_idx: int, app_config: AppConfig):
    """Rendert die Ansicht für eine einzelne Frage."""
    if st.session_state.get("show_pseudonym_reminder", False):
        st.success(
            f"**Willkommen, {st.session_state.user_id}!** "
            "Bitte merke dir dein Pseudonym gut, um den Test später fortsetzen zu können."
        )
        del st.session_state.show_pseudonym_reminder

    # Zähler für verbleibende Fragen (früh berechnen für Dialog-Check)
    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    
    # Zeige Welcome-Dialog vor dem ersten Test-Start
    # Problem: st.dialog lässt sich nicht unterdrücken wenn User X klickt
    # Lösung: Container statt Dialog für garantierte Sichtbarkeit
    if num_answered == 0 and not st.session_state.get("test_started", False):
        _show_welcome_container(app_config)
        st.stop()  # Stoppe Ausführung komplett, bis Test gestartet

    # --- Sicherheitscheck und Re-Initialisierung ---
    # Dieser Block fängt den Zustand ab, in dem ein neues Fragenset ausgewählt wurde,
    # aber der session_state (insb. optionen_shuffled) noch vom alten Set stammt.
    if len(st.session_state.get("optionen_shuffled", [])) != len(questions):
        from auth import initialize_session_state
        st.warning("⚠️ Erkenne Wechsel des Fragensets, initialisiere Test neu...")
        initialize_session_state(questions, app_config)
        time.sleep(1) # Kurze Pause, damit der Nutzer die Nachricht sieht
        st.rerun()
        return # Verhindert die weitere Ausführung mit inkonsistenten Daten

    frage_obj = questions[frage_idx]

    # Ermittle die laufende Nummer der Frage im aktuellen Testdurchlauf
    initial_indices = st.session_state.get("initial_frage_indices", [])
    session_local_idx = initial_indices.index(frage_idx) if frage_idx in initial_indices else -1
    display_question_number = session_local_idx + 1

    # Extrahiere den reinen Fragentext ohne die ursprüngliche Nummer
    original_frage_text = frage_obj["frage"].split('. ', 1)[-1]
    frage_text = smart_quotes_de(f"{display_question_number}. {original_frage_text}")
    thema = frage_obj.get("thema", "")
    gewichtung = frage_obj.get("gewichtung", 1)

    # Zähler für verbleibende Fragen
    remaining = len(questions) - num_answered

    with st.container(border=True):

        # --- Countdown-Timer ---
        if st.session_state.start_zeit and not is_test_finished(questions):
            elapsed_time = (pd.Timestamp.now() - st.session_state.start_zeit).total_seconds()
            remaining_time = int(st.session_state.test_time_limit - elapsed_time)

            col1, col2 = st.columns(2)
            with col1:
                if remaining_time > 0:
                    minutes, seconds = divmod(remaining_time, 60)
                    st.metric("⏳ Verbleibende Zeit", f"{minutes:02d}:{seconds:02d}")
                    warning_text = _format_countdown_warning_de(remaining_time)
                    if warning_text:
                        st.warning(warning_text)
                else:
                    st.session_state.test_time_expired = True
                    st.error("⏰ Zeit ist um!")
                    st.rerun()
            with col2:
                pass  # Platzhalter für Layout

        # Logik für die Fortschrittsanzeige
        if num_answered == 0:
            st.markdown(f"### {len(questions)} Fragen insgesamt")
        elif remaining == 0:
            # Dieser Fall tritt nur nach der letzten Antwort auf, bevor die Zusammenfassung kommt.
            # Hier ist keine Anzeige mehr nötig.
            pass
        elif remaining == 1 and not is_test_finished(questions):
            st.markdown("### Letzte Frage")
        else:
            st.markdown(f"### Noch {remaining} Frage{'n' if remaining > 1 else ''}")

        if thema:
            st.caption(f"Thema: {thema}")
        st.markdown(
            f"**{frage_text}** <span style='color:#888; font-size:0.9em;'>(Gewicht: {gewichtung})</span>",
            unsafe_allow_html=True,
        )

        # --- Optionen und Antwort-Logik ---
        is_answered = st.session_state.get(f"frage_{frage_idx}_beantwortet") is not None
        optionen = st.session_state.optionen_shuffled[frage_idx]
        
        # Widget-Key und gespeicherte Antwort holen
        widget_key = f"radio_{frage_idx}"
        gespeicherte_antwort = get_answer_for_question(frage_idx)

        # Wir verwenden st.radio, um die Auswahl zu steuern.
        # Die `format_func` wird verwendet, um KaTeX-Formeln korrekt darzustellen.
        selected_index = st.radio(
            "Wähle deine Antwort:",
            options=range(len(optionen)),
            key=widget_key,
            index=optionen.index(gespeicherte_antwort) if gespeicherte_antwort in optionen else None,
            disabled=is_answered,
            label_visibility="collapsed",
            format_func=lambda x: smart_quotes_de(optionen[x]),
        )

        antwort = optionen[selected_index] if selected_index is not None else None

        # --- Logik zur Anpassung des Testflusses nach einem Sprung ---
        # Wenn wir zu einer unbeantworteten Frage springen, passen wir die Reihenfolge
        # der Fragen an, damit der Test von hier aus nahtlos weitergeht.
        # Das Flag wird danach zurückgesetzt.
        if not is_answered and st.session_state.get("jump_to_idx_active"):
            handle_jump_to_unanswered_question(frage_idx)

        # --- Buttons: Antworten, Überspringen und Merken ---
        if not is_answered:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                # Bookmark-Toggle
                is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
                new_bookmark_state = st.toggle("🔖 Merken", value=is_bookmarked, key=f"bm_toggle_{frage_idx}")
                if new_bookmark_state != is_bookmarked:
                    handle_bookmark_toggle(frage_idx, new_bookmark_state, questions)
                    st.rerun() # Rerun, um den Zustand sofort zu reflektieren
            with col2:
                # Überspringen-Button
                if st.button("↪️ Überspringen", key=f"skip_{frage_idx}", width="stretch"):
                    # Verschiebe die aktuelle Frage ans Ende der Liste
                    frage_indices = st.session_state.get("frage_indices", [])
                    if frage_idx in frage_indices:
                        frage_indices.remove(frage_idx)
                        frage_indices.append(frage_idx)
                        st.session_state.frage_indices = frage_indices
                        # Füge die Frage zur Liste der übersprungenen hinzu (falls noch nicht vorhanden)
                        if "skipped_questions" not in st.session_state:
                            st.session_state.skipped_questions = []
                        if frage_idx not in st.session_state.skipped_questions:
                            st.session_state.skipped_questions.append(frage_idx)
                        st.toast("Frage übersprungen. Sie wird später erneut gestellt.")
                        st.rerun()
            with col3:
                # Antworten-Button (nur aktiv, wenn eine Option gewählt wurde)
                if st.button(
                    "Antworten",
                    key=f"submit_{frage_idx}",
                    type="primary",
                    width="stretch",
                    disabled=(antwort is None),
                ):
                    # Die Logik für das Antworten wird hierhin verschoben, questions wird übergeben
                    handle_answer_submission(frage_idx, antwort, frage_obj, app_config, questions)
        
        else:
            # --- Logik für den Fall, dass zu einer bereits beantworteten Frage gesprungen wird ---
            # Wenn die Frage beantwortet ist UND wir gerade von einem Bookmark hierher gesprungen sind,
            # oder von einer übersprungenen Frage, braucht der Nutzer eine Möglichkeit, zum Test zurückzukehren.
            is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
            is_skipped = frage_idx in st.session_state.get("skipped_questions", [])
            
            if st.session_state.get("jump_to_idx_active") and (is_bookmarked or is_skipped):
                st.info("Diese Frage wurde bereits beantwortet.")
                _, col2, _ = st.columns([1, 1, 1])
                with col2:
                    if st.button(
                        "Test fortsetzen",
                        key=f"resume_from_answered_bm_{frage_idx}",
                        type="primary",
                        width="stretch",
                    ):
                        # Setze das Sprung-Flag zurück, damit die App zur nächsten unbeantworteten Frage geht.
                        st.session_state.jump_to_idx_active = False
                        # Lösche den last_answered_idx, damit die App nicht hier hängen bleibt.
                        if "last_answered_idx" in st.session_state:
                            del st.session_state.last_answered_idx
                        st.rerun()

    # --- Motivation anzeigen (AUSSERHALB des Fragen-Containers) ---
    # Zeige die Motivation nur für die Frage, die gerade beantwortet wurde
    # Die Bedingung: last_answered_idx == frage_idx (nicht is_answered!)
    # Weil nach dem Rerun zur nächsten Frage gesprungen wird, aber last_answered_idx
    # zeigt auf die gerade beantwortete Frage
    if (st.session_state.get("last_answered_idx") == frage_idx and
        "last_motivation_message" in st.session_state and 
        st.session_state.last_motivation_message):
        st.markdown(st.session_state.last_motivation_message, unsafe_allow_html=True)
    
    # --- Erklärung anzeigen ---
    if st.session_state.get(f"show_explanation_{frage_idx}", False):
        render_explanation(frage_obj, app_config, questions)


def handle_jump_to_unanswered_question(frage_idx: int):
    """Passt die Reihenfolge der Fragen an, wenn zu einer unbeantworteten Frage gesprungen wird."""
    frage_indices = st.session_state.get("frage_indices", [])
    if frage_idx in frage_indices:
        # Entferne die angesprungene Frage von ihrer alten Position
        frage_indices.remove(frage_idx)
        # Füge sie an der aktuellen Position (vorne) wieder ein
        frage_indices.insert(0, frage_idx)
        st.session_state.frage_indices = frage_indices
    # Setze das Flag zurück, da der Sprung nun verarbeitet wurde.
    st.session_state.jump_to_idx_active = False


def handle_bookmark_toggle(frage_idx: int, new_state: bool, questions: list):
    """Verarbeitet das Umschalten eines Bookmarks."""
    is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
    if new_state and not is_bookmarked:
        st.session_state.bookmarked_questions.append(frage_idx)
    elif not new_state and is_bookmarked:
        st.session_state.bookmarked_questions.remove(frage_idx)
    
    # Extrahiere die echten Fragennummern für die DB
    bookmarked_q_nrs = [int(questions[i]['frage'].split('.')[0]) for i in st.session_state.bookmarked_questions]
    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)


def handle_answer_submission(frage_idx: int, antwort: str, frage_obj: dict, app_config: AppConfig, questions: list):
    """Verarbeitet die Abgabe einer Antwort."""
    # --- Rate Limiting ---
    last_answer_time = st.session_state.get("last_answer_time", 0)
    current_time = time.time()
    if app_config.min_seconds_between_answers > 0 and current_time - last_answer_time < app_config.min_seconds_between_answers:
        st.warning(f"⚠️ Bitte warte kurz, bevor du die nächste Antwort abgibst (Limit: {app_config.min_seconds_between_answers}s).")
        return
    
    st.session_state.last_answer_time = current_time

    if st.session_state.start_zeit is None:
        st.session_state.start_zeit = pd.Timestamp.now()

    richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
    ist_richtig = antwort == richtige_antwort_text
    gewichtung = frage_obj.get("gewichtung", 1)
    
    if ist_richtig:
        punkte = gewichtung
        st.toast("Richtig!", icon="✅")
    else:
        punkte = -gewichtung if app_config.scoring_mode == "negative" else 0
        st.toast("Leider falsch.", icon="❌")

    set_question_as_answered(frage_idx, punkte, antwort)
    
    # Generiere eine neue Motivationsnachricht NACH set_question_as_answered,
    # damit questions_remaining korrekt berechnet wird (inkl. der gerade beantworteten Frage)
    from components import get_motivation_message
    st.session_state.last_motivation_message = get_motivation_message(questions, app_config)

    # Entferne die Frage aus der Liste der übersprungenen, falls sie dort war
    if "skipped_questions" in st.session_state and frage_idx in st.session_state.skipped_questions:
        st.session_state.skipped_questions.remove(frage_idx)


    # Extrahiere die Frage-Nummer aus dem Fragetext
    try:
        frage_nr_str = frage_obj.get("frage", "").split(".", 1)[0]
        frage_nr = int(frage_nr_str)
    except (ValueError, IndexError):
        st.error("Fehler: Die Frage-Nummer konnte nicht extrahiert werden.")
        return

    # Speichere die Antwort in der neuen Datenbank-Struktur
    from database import save_answer as db_save_answer
    db_save_answer(
        session_id=st.session_state.session_id,
        question_nr=frage_nr,
        answer_text=antwort,
        points=punkte,
        is_correct=(punkte > 0)
    )

    # Setze das Sprung-Flag zurück, da der Nutzer nun aktiv eine Aktion ausgeführt hat.
    # Dies verhindert, dass die Erklärung nach der Antwort fälschlicherweise blockiert wird.
    st.session_state.jump_to_idx_active = False

    st.session_state[f"show_explanation_{frage_idx}"] = True
    st.session_state.last_answered_idx = frage_idx
    st.rerun()


def _handle_feedback_submission(frage_idx: int, frage_obj: dict, feedback_types: list[str]):
    """Kapselt die Logik zum Senden von Feedback, um Reruns zu steuern."""
    from database import add_feedback
    frage_nr = int(frage_obj.get("frage", "0").split(".", 1)[0])
    session_id = st.session_state.get("session_id")
    if session_id and frage_nr > 0 and feedback_types:
        add_feedback(session_id, frage_nr, feedback_types)
        st.session_state[f"feedback_reported_{frage_idx}"] = True
        st.toast("Feedback gesendet!")


def render_explanation(frage_obj: dict, app_config: AppConfig, questions: list):
    """Rendert den Feedback- und Erklärungsblock nach einer Antwort."""
    
    # Ermittle den Index der aktuellen Frage. Dies wird an mehreren Stellen benötigt.
    frage_idx = questions.index(frage_obj)

    # Feedback (richtig/falsch)
    richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
    gegebene_antwort = get_answer_for_question(frage_idx)
    ist_richtig = gegebene_antwort == richtige_antwort_text

    # Formatiere die Antworten, um Markdown (wie `...`) in HTML umzuwandeln
    formatted_gegebene_antwort = smart_quotes_de(str(gegebene_antwort)) if gegebene_antwort else ""
    formatted_richtige_antwort = smart_quotes_de(str(richtige_antwort_text))

    if ist_richtig:
        # Gimmick: Gestaffelte Belohnung für schwierige Fragen.
        if "celebrated_questions" not in st.session_state:
            st.session_state.celebrated_questions = []
        
        if frage_idx not in st.session_state.celebrated_questions:
            gewichtung = frage_obj.get("gewichtung", 1)
            if gewichtung >= 3: st.balloons()
            elif gewichtung == 2: st.snow()
            st.session_state.celebrated_questions.append(frage_idx)

        st.success("Richtig! ✅")
    else:
        st.error("Leider falsch. ❌")
        st.markdown(f"<span style='color:#15803d; font-weight:bold;'>Richtig:</span> {formatted_richtige_antwort}", unsafe_allow_html=True)

    # Markieren und Feedback-Button gemeinsam platzieren
    action_cols = st.columns([1.2, 2, 1])
    with action_cols[0]:
        bookmark_key = f"bm_toggle_{frage_idx}"
        is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
        new_bookmark_state = st.toggle("🔖 Merken", value=is_bookmarked, key=bookmark_key)
        if new_bookmark_state != is_bookmarked:
            handle_bookmark_toggle(frage_idx, new_bookmark_state, questions)
            st.rerun()

    # Erklärungstext
    erklaerung = frage_obj.get("erklaerung")
    if erklaerung:
        with st.container(border=True):
            st.markdown("<span style='font-weight:600; color:#4b9fff;'>Erklärung:</span>", unsafe_allow_html=True)
            # Prüfe, ob die Erklärung ein strukturiertes Objekt ist
            if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                st.markdown(f"**{smart_quotes_de(erklaerung['titel'])}**")
                # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                # und bei Bedarf scrollbar zu sein.
                steps = erklaerung.get('schritte') or []
                numbered = _steps_have_numbering(steps)
                for i, schritt in enumerate(steps):
                    cols = st.columns([1, 19])
                    with cols[0]:
                        # Zeige nur dann Indexzahlen, wenn die Originalschritte nummeriert sind
                        if numbered:
                            st.markdown(f"{i+1}.")
                        else:
                            st.markdown("•")
                    with cols[1]:
                        # Wenn die Schritte bereits nummeriert sind, entferne die Nummerierung
                        display_step = _strip_leading_numbering(schritt) if numbered else schritt
                        st.markdown(f"<div class='scrollable-katex'>{smart_quotes_de(display_step)}</div>", unsafe_allow_html=True)
            else:
                # Fallback für einfache String-Erklärungen
                st.markdown(smart_quotes_de(str(erklaerung)))

    # --- Optionale, detaillierte Erklärung ---
    extended_explanation = frage_obj.get("extended_explanation")
    if extended_explanation:
        show_extended_key = f"show_extended_{frage_idx}"

        # Zeige den Button nur an, wenn die Erklärung noch nicht sichtbar ist.
        if not st.session_state.get(show_extended_key, False):
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                if st.button(
                    "🧠 Zeige detaillierte Erklärung",
                    key=f"btn_extended_{frage_idx}",
                    width="stretch",
                ):
                    st.session_state[show_extended_key] = True
                    st.rerun()
        
        if st.session_state.get(show_extended_key, False):
            with st.expander("Detaillierte Erklärung", expanded=True):
                if isinstance(extended_explanation, dict):
                    title = extended_explanation.get("title") or extended_explanation.get("titel") or ""
                    if title:
                        st.markdown(f"**{smart_quotes_de(title)}**")

                    content = extended_explanation.get("content")
                    steps = extended_explanation.get("schritte")

                    if isinstance(steps, list) and steps:
                        numbered = _steps_have_numbering(steps)
                        for idx, step in enumerate(steps, start=1):
                            if numbered:
                                # Remove leading numbering from the source step to
                                # avoid showing e.g. "1. 1. Do X".
                                item = _strip_leading_numbering(step)
                                st.markdown(f"{idx}. {smart_quotes_de(item)}")
                            else:
                                st.markdown(f"- {smart_quotes_de(step)}")
                    elif isinstance(content, str) and content.strip():
                        st.markdown(smart_quotes_de(content))
                    else:
                        st.markdown(smart_quotes_de(str(extended_explanation)))
                else:
                    st.markdown(smart_quotes_de(str(extended_explanation)))

    # --- Feedback-Mechanismus ---
    feedback_options = [
        "Inhaltlicher Fehler",
        "Tippfehler/Grammatik",
        "Frage unklar formuliert",
        "Antwortoptionen unpassend",
        "Erklärung falsch/unverständlich",
        "Technisches Problem (z.B. Anzeige)",
        "Sonstiges"
    ]
    feedback_key = f"feedback_reported_{frage_idx}"

    if st.session_state.get(feedback_key, False):
        with action_cols[1]:
            st.success("✔️ Danke, dein Feedback wurde übermittelt.")
    else:
        # Action-Buttons teilen sich die Spaltengruppe
        with action_cols[1]:
            with st.popover("Problem mit dieser Frage melden", width="stretch"):
                st.markdown("**Welche Probleme sind dir aufgefallen?**")
                
                # NEU: Formular verwenden, um Checkbox-Klicks zu bündeln
                with st.form(key=f"feedback_form_{frage_idx}"):
                    # Speichere den Zustand der Checkboxen in einem temporären Dictionary
                    selections = {
                        option: st.checkbox(option, key=f"cb_feedback_{frage_idx}_{option}")
                        for option in feedback_options
                    }
                    
                    # Der Senden-Button für das Formular
                    submitted = st.form_submit_button(
                        "Feedback senden",
                        type="primary",
                        use_container_width=True
                    )
                    
                    if submitted:
                        selected_types = [option for option, checked in selections.items() if checked]
                        if selected_types:
                            _handle_feedback_submission(frage_idx, frage_obj, selected_types)
                            st.rerun() # Erzwinge einen Rerun, um den "Danke"-Text anzuzeigen

    # Zeige den "Nächste Frage"-Button nur an, wenn der Nutzer nicht gerade
    # im Sprung-Modus eine bereits beantwortete Frage reviewt.
    if not st.session_state.get("jump_to_idx_active"):
        render_next_question_button(questions, questions.index(frage_obj))


def render_next_question_button(questions: QuestionSet, frage_idx: int):
    """
    Rendert den "Nächste Frage"-Button am Ende des Erklärungsblocks.
    Bei der letzten Frage wird der Button als "Zur Testauswertung" angezeigt.
    """
    # Prüfe, ob dies die letzte Frage ist
    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    is_last_question = (num_answered == len(questions))
    
    button_text = "Zur Testauswertung" if is_last_question else "Nächste Frage"
    
    _, col2, _ = st.columns([2, 1.5, 2])
    with col2:
        if st.button(button_text, key=f"next_q_{frage_idx}", type="primary", width="stretch"):
            # Setze das Flag zurück, um die Erklärung bei der nächsten Anzeige nicht mehr zu zeigen.
            st.session_state[f"show_explanation_{frage_idx}"] = False
            st.rerun()


def render_final_summary(questions: QuestionSet, app_config: AppConfig):
    """Zeigt die finale Zusammenfassung und den Review-Modus an."""
    import time
    # Wenn die Testzeit abgelaufen ist, zeigen wir einen anderen Titel an.
    if st.session_state.get("test_time_expired", False):
        st.header("⏰ Zeit abgelaufen!")
        st.info("Die Testzeit ist abgelaufen — Ergebnisse werden automatisch angezeigt.")
    else:
        st.header("🚀 Test abgeschlossen!")

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    st.metric(
        "Dein Endergebnis",
        f"{current_score} / {max_score} Punkte",
        f"{format_decimal_de(prozent, 1)} %"
    )

    # Animation nur einmal beim ersten Laden der Ergebnisseite zeigen
    if "celebration_shown" not in st.session_state:
        st.session_state.celebration_shown = True
        if prozent >= 100:
            st.balloons()
            st.snow()
    
    # Feingranulare, abwechslungsreiche Feedback-Messages (8 Tiers)
    import random
    
    if prozent == 100:  # Perfekt (100%)
        messages = [
            "🏆 Perfekt! 100 % – Makellose Runde!",
            "⚡ Fehlerlos! Absolute Elite-Leistung.",
            "💎 Makellos! Alle Fragen richtig.",
            "🌟 100 %! Du bist ein wahrer Meister.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 90:  # Exzellent (90-99 %)
        messages = [
            "🏅 Exzellent! Fast perfekte Quote.",
            "✨ Hervorragend! Sehr starke Leistung.",
            "🚀 Elite-Niveau! Beeindruckend konsistent.",
            "🎯 Top-Ergebnis! Kaum Fehler.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 80:  # Sehr gut (80-89%)
        messages = [
            "✅ Sehr gut! Solide Top-Performance.",
            "💪 Stark! Nur wenige Fehler.",
            "👍 Überzeugende Leistung! Weiter so.",
            "🎉 Sehr sauber! Qualität stimmt.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 70:  # Gut (70-79%)
        messages = [
            "📈 Gut gemacht! Stabile Quote.",
            "✨ Ordentlich! Grundlagen sitzen.",
            "💼 Solide Leistung! Noch Potenzial.",
            "🔧 Gutes Ergebnis! Kleine Lücken schließbar.",
        ]
        st.info(random.choice(messages))
    elif prozent >= 60:  # Befriedigend (60-69%)
        messages = [
            "📚 Befriedigend. Basis vorhanden, Vertiefung lohnt.",
            "🌱 Okay. Kernthemen nochmal durchgehen.",
            "🔍 Durchschnitt. Review-Modus hilft dir weiter.",
            "💡 Mittelfeld. Mit Übung wird's besser.",
        ]
        st.info(random.choice(messages))
    elif prozent >= 50:  # Ausreichend (50-59 %)
        messages = [
            "⚠️ Ausreichend. Deutlicher Nachholbedarf.",
            "📖 Knapp bestanden. Erklärungen nutzen!",
            "🎯 50-59 %. Themen gezielt wiederholen.",
            "🔄 Schwankend. Review zeigt Schwächen auf.",
        ]
        st.warning(random.choice(messages))
    elif prozent >= 40:  # Mangelhaft (40-49%)
        messages = [
            "⛔ Mangelhaft. Grundlagen fehlen noch.",
            "📕 Unter 50 %. Intensive Wiederholung nötig.",
            "🚨 Lücken groß. Review-Modus ist Pflicht.",
            "🔴 Viele Fehler. Stoff nochmal durcharbeiten.",
        ]
        st.warning(random.choice(messages))
    else:  # Ungenügend (<40%)
        messages = [
            "❌ Ungenügend. Stoff von Grund auf lernen.",
            "📚 Unter 40 %. Systematisch neu starten.",
            "🆘 Große Wissenslücken. Hilfe holen!",
            "⚠️ Sehr schwach. Review zeigt alle Fehler.",
        ]
        st.error(random.choice(messages))

    # --- Performance-Analyse pro Thema ---
    st.subheader("Deine Leistung nach Themen")

    # Aggregiere Punkte pro Thema und zähle beantwortete vs. Gesamtfragen.
    topic_performance = {}
    for i, frage in enumerate(questions):
        thema = frage.get("thema", "Allgemein")
        if thema not in topic_performance:
            topic_performance[thema] = {"erreicht": 0, "maximal": 0, "answered_count": 0, "question_count": 0, "correct": 0, "wrong": 0}

        max_punkte = frage.get("gewichtung", 1)
        topic_performance[thema]["maximal"] += max_punkte
        topic_performance[thema]["question_count"] += 1

        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        if punkte is not None:
            # Nur positive Punkte für die Leistungsanalyse zählen, um negative Scores zu vermeiden.
            erreichte_punkte = max(0, punkte)
            topic_performance[thema]["erreicht"] += erreichte_punkte
            topic_performance[thema]["answered_count"] += 1
            # Zähle korrekte vs. falsche Antworten (korrekt = positiv erzielte Punkte)
            try:
                if punkte > 0:
                    topic_performance[thema]["correct"] += 1
                else:
                    topic_performance[thema]["wrong"] += 1
            except Exception:
                # Defensive: falls punkte kein Zahlentyp ist
                pass

    # DataFrame für die Visualisierung erstellen.
    # Zeige nur Themen, zu denen mindestens eine Frage beantwortet wurde,
    # und kennzeichne die Themen mit (beantwortet/gesamt), damit 100 % bei
    # sehr wenigen Fragen nicht irreführend wirkt.
    performance_data = []
    for thema, scores in topic_performance.items():
        answered = scores.get('answered_count', 0)
        total_q = scores.get('question_count', 0)
        if scores["maximal"] > 0 and answered > 0:
            prozent = (scores["erreicht"] / scores["maximal"]) * 100
            performance_data.append({
                "Thema": thema,
                "Answered": answered,
                "Total": total_q,
                "Leistung (%)": prozent,
            })

    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        # Create a human-friendly label but keep Thema separate for hover
        df_performance["Label"] = df_performance.apply(lambda r: f"{r['Thema']} ({int(r['Answered'])}/{int(r['Total'])})", axis=1)

        # Use Plotly for better label/hover control so the (answered/total) is always visible
        try:
            import plotly.graph_objects as go

            # Prepare customdata: Thema, Answered, Total, correct, wrong, pct
            customdata = []
            for _, row in df_performance.iterrows():
                thema = row['Thema']
                answered = int(row['Answered'])
                total = int(row['Total'])
                # Retrieve correct/wrong counts from topic_performance
                perf = topic_performance.get(thema, {})
                correct = int(perf.get('correct', 0))
                wrong = int(perf.get('wrong', 0))
                pct = float(row['Leistung (%)'])
                customdata.append([thema, answered, total, correct, wrong, pct])

            # Short label inside/outside the bar
            df_performance['display_text'] = df_performance.apply(
                lambda r: f"{int(r['Leistung (%)'])} % ({int(r['Answered'])}/{int(r['Total'])})", axis=1
            )

            fig = go.Figure()
            # Determine color per bar: green >=75, orange >=50, red <50
            def color_for_pct(pct: float) -> str:
                try:
                    if pct >= 75:
                        return '#15803d'  # dark green
                    if pct >= 50:
                        return '#b45309'  # darker amber
                    return '#b91c1c'      # darker red
                except Exception:
                    return '#4b9fff'

            colors = [color_for_pct(float(r)) for r in df_performance['Leistung (%)']]

            fig.add_trace(
                go.Bar(
                    x=df_performance['Label'],
                    y=df_performance['Leistung (%)'],
                    text=df_performance['display_text'],
                    textposition='inside',
                    marker_color=colors,
                    customdata=customdata,
                    hovertemplate=(
                        '<b>Thema</b>: %{customdata[0]}<br>'
                        '<b>Leistung</b>: %{customdata[5]:.1f} %<br>'
                        '<b>Richtig / Gesamt</b>: %{customdata[3]} / %{customdata[2]}<br>'
                        '<b>Falsch</b>: %{customdata[4]}<br>'
                        '<b>Beantwortet</b>: %{customdata[1]} / %{customdata[2]}<extra></extra>'
                    ),
                )
            )

            # Compute y-axis top to leave room for labels
            max_pct = float(df_performance['Leistung (%)'].max() if not df_performance.empty else 100)
            y_top = max(105.0, max_pct * 1.12)

            fig.update_layout(
                xaxis_tickangle=-30,
                xaxis_title='Thema (beantwortet/gesamt)',
                yaxis_title='Leistung (%)',
                margin=dict(t=40, b=140, l=40, r=10),
                height=400,
                yaxis=dict(range=[0, y_top]),
            )

            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            # Fallback to the simple chart if Plotly is unavailable
            df_simple = df_performance.set_index("Label")[['Leistung (%)']]
            st.bar_chart(df_simple, color="#15803d")

        # Kleine Legende und Erklärung
        with st.expander("Über diese Auswertung (kurze Erklärung)", expanded=False):
            st.markdown(
                "- Die Balken zeigen den Anteil der erreichten Punkte pro Thema (in %).\n"
                "- In Klammern hinter dem Thema steht: (beantwortete Fragen / Gesamtfragen).\n"
                "- Wenn nur sehr wenige Fragen für ein Thema beantwortet wurden, sind die Prozentwerte statistisch wenig aussagekräftig."
            )

        # (Hinweis zu kleinen Stichproben wurde entfernt — die Erklärung im Expander genügt.)
    else:
        st.info("Keine Daten für eine themenspezifische Analyse verfügbar. Beantworte mindestens eine Frage, um themenspezifische Ergebnisse zu sehen.")


    st.divider()
    render_review_mode(questions, app_config)
    # --- PDF-Export (am Ende, nach Review) ---
    # Warnung über die Dauer
    q_file_name = st.session_state.get("selected_questions_file", "")
    anzahl_fragen = len(questions)
    # Dank Parallelverarbeitung und Caching: ca. 3-5 Sekunden pro Frage
    # Prüfe ob Formeln vorhanden sind und extrahiere erste Formel
    def extract_formulas(questions):
        """Extrahiert erste gefundene Formel und zählt Gesamt-Formeln."""
        import re
        formula_pattern = r'\$\$.*?\$\$|\$.*?\$'
        
        first_formula = None
        total_count = 0
        
        for q in questions:
            # Prüfe Frage-Text
            matches = re.findall(formula_pattern, q.get("frage", ""))
            if matches and not first_formula:
                first_formula = matches[0]
            total_count += len(matches)
            
            # Prüfe Optionen
            for opt in q.get("optionen", []):
                matches = re.findall(formula_pattern, opt)
                if matches and not first_formula:
                    first_formula = matches[0]
                total_count += len(matches)
            
            # Prüfe Erklärung
            matches = re.findall(formula_pattern, q.get("erklaerung", ""))
            if matches and not first_formula:
                first_formula = matches[0]
            total_count += len(matches)
        
        return first_formula, total_count
    
    first_formula, formula_count = extract_formulas(questions)
    has_math = formula_count > 0
    
    user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")




def render_review_mode(questions: QuestionSet, app_config=None):
    if app_config is None:
        app_config = st.session_state.get("app_config")
    from pdf_export import (
        generate_musterloesung_pdf,
        generate_mini_glossary_pdf,
        generate_pdf_report,
    )

    # Dateinamen und User-Info
    selected_file = st.session_state.get(
        "selected_questions_file", "questions_export.json"
    )
    user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")

    st.subheader("🧐 Review deiner Antworten")
    
    # Die `initial_frage_indices` werden für die korrekte Nummerierung im Review-Modus benötigt.
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    filter_option = st.radio(
        "Filtere die Fragen:",
        ["Alle", "Nur falsch beantwortete", "Nur richtig beantwortete", "Nur markierte", "Nur unbeantwortete"],
        index=3  # Standard: "Nur markierte"
    )

    # Hole app_config aus Session oder global, falls vorhanden
    app_config = globals().get("app_config")
    try:
        # Falls in Session State gespeichert (z.B. von main/app.py), bevorzuge diesen
        if "app_config" in st.session_state:
            app_config = st.session_state["app_config"]
    except Exception:
        pass

    for i, frage in enumerate(questions):
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage["optionen"][frage["loesung"]]
        ist_richtig = gegebene_antwort == richtige_antwort_text
        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        is_bookmarked = i in st.session_state.get("bookmarked_questions", [])

        if filter_option == "Nur falsch beantwortete":
            # Zeige nur beantwortete UND falsch beantwortete Fragen
            if ist_richtig or punkte is None:
                continue
        if filter_option == "Nur richtig beantwortete" and not ist_richtig:
            continue
        if filter_option == "Nur markierte" and not is_bookmarked:
            continue
        if filter_option == "Nur unbeantwortete" and punkte is not None:
            continue

        icon = "❓"
        if punkte is not None:
            icon = "✅" if ist_richtig else "❌"
        if is_bookmarked:
            icon += " 🔖"

        # Titel für den Expander erstellen und intelligent kürzen
        try:
            title_text = frage['frage'].split('.', 1)[1].strip()
            if len(title_text) > 50:
                title_text = title_text[:50].rsplit(' ', 1)[0] + "..."
        except IndexError:
            title_text = frage['frage'][:50] + "..."

        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1

        # Review-UI (z.B. Expander für jede Frage, Anzeige der Antworten etc.)
        with st.expander(f"{icon} Frage {display_question_number}: {title_text}"):
            st.markdown(f"**Frage:** {frage['frage']}")
            # Immer zuerst die gegebene Antwort (falsch oder richtig), dann die richtige darunter
            if gegebene_antwort is not None:
                if ist_richtig:
                    st.markdown(f"<span style='color:#15803d; font-weight:bold;'>Deine Antwort:</span> <span style='color:#15803d;'>{gegebene_antwort}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#b91c1c; font-weight:bold;'>Deine Antwort:</span> <span style='color:#b91c1c;'>{gegebene_antwort}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#b91c1c; font-weight:bold;'>Deine Antwort:</span> <span style='color:#b91c1c;'>(nicht beantwortet)</span>", unsafe_allow_html=True)
            # Richtige Antwort immer darunter, auch wenn sie schon oben steht
            st.markdown(f"<span style='color:#15803d; font-weight:bold;'>Richtige Antwort:</span> <span style='color:#15803d;'>{richtige_antwort_text}</span>", unsafe_allow_html=True)
            if frage.get("erklaerung"):
                st.markdown(f"**Erklärung:** {frage['erklaerung']}")

    # --- Exportbereich (work in progress) ---
    st.markdown("---")
    st.subheader("📦 Export")
    with st.expander("Exportiere deine Testergebnisse & Lernmaterialien"):

        # Anki
        def handle_anki_export():
            try:
                from export_jobs import generate_anki_apkg
            except ImportError:
                st.info("Dieses Export-Feature steht demnächst zur Verfügung.")
                return
            try:
                apkg_bytes = generate_anki_apkg(selected_file, list(questions))
                st.download_button(
                    label="💾 Anki-Kartenset herunterladen",
                    data=apkg_bytes,
                    file_name=f"anki_export_{selected_file.replace('questions_', '').replace('.json', '')}.apkg",
                    mime="application/octet-stream",
                    key=anki_dl_key
                )
            except Exception as e:
                st.error(f"Fehler beim Erzeugen des Anki-Exports: {e}")
        with st.expander("📦 Anki-Lernkarten (empfohlen für Wiederholung)"):
            st.markdown("Exportiere alle Fragen als Anki-Kartenset für effizientes Lernen mit Spaced Repetition. Importiere die Datei direkt in die Anki-App.")
            st.caption("Format: .apkg  |  [Anki Import-Anleitung (Intro)](https://docs.ankiweb.net/importing/intro.html)  |  [Textdateien importieren](https://docs.ankiweb.net/importing/text-files.html)")
            anki_btn_key = f"download_anki_review_{selected_file}"
            anki_dl_key = f"dl_anki_direct_{selected_file}"
            if st.button("Download starten", key=anki_btn_key):
                handle_anki_export()

        # Kahoot
        def handle_kahoot_export():
            try:
                from export_jobs import generate_kahoot_xlsx
            except ImportError:
                st.info("Dieses Export-Feature steht demnächst zur Verfügung.")
                return
            try:
                xlsx_bytes = generate_kahoot_xlsx(selected_file, list(questions))
                st.download_button(
                    label="💾 Kahoot-Quiz herunterladen",
                    data=xlsx_bytes,
                    file_name=f"kahoot_export_{selected_file.replace('questions_', '').replace('.json', '')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=kahoot_dl_key
                )
            except Exception as e:
                st.error(f"Fehler beim Erzeugen des Kahoot-Exports: {e}")
        with st.expander("📦 Kahoot-Quiz (für Live-Quizze)"):
            st.markdown("Erstelle ein Kahoot-Quiz aus deinen Fragen. Perfekt für Gruppen- oder Unterrichtssituationen.")
            st.caption("Format: .xlsx  |  [Kahoot Import-Anleitung](https://support.kahoot.com/hc/en-us/articles/115002303908)")
            kahoot_btn_key = f"download_kahoot_review_{selected_file}"
            kahoot_dl_key = f"dl_kahoot_direct_{selected_file}"
            if st.button("Download starten", key=kahoot_btn_key):
                handle_kahoot_export()

        # arsnova.click
        def handle_arsnova_export():
            try:
                from export_jobs import generate_arsnova_json
            except ImportError:
                st.info("Dieses Export-Feature steht demnächst zur Verfügung.")
                return
            try:
                json_bytes = generate_arsnova_json(selected_file, list(questions))
                st.download_button(
                    label="💾 arsnova.click-Quiz herunterladen",
                    data=json_bytes,
                    file_name=f"arsnova_export_{selected_file.replace('questions_', '').replace('.json', '')}.json",
                    mime="application/json",
                    key=arsnova_dl_key
                )
            except Exception as e:
                st.error(f"Fehler beim Erzeugen des arsnova.click-Exports: {e}")
        with st.expander("📦 arsnova.click-Quiz (für Hochschul-Feedback)"):
            st.markdown("Exportiere deine Fragen für arsnova.click – ein Audience-Response-System für Hochschulen. Ideal für Feedback und Live-Abstimmungen.")
            st.caption("Format: .json  |  [arsnova.click Infos](https://github.com/thm-projects/arsnova.click-v2)")
            arsnova_btn_key = f"download_arsnova_review_{selected_file}"
            arsnova_dl_key = f"dl_arsnova_direct_{selected_file}"
            if st.button("Download starten", key=arsnova_btn_key):
                handle_arsnova_export()

        # Musterlösung
        with st.expander("📄 Musterlösung (PDF mit allen richtigen Antworten)"):
            st.markdown("Erhalte eine vollständige Musterlösung mit allen korrekten Antworten und Erklärungen. Ideal zum Nacharbeiten und Lernen.")
            muster_download_name = (
                f"musterloesung_"
                f"{selected_file.replace('questions_', '').replace('.json', '')}"
                f"_{user_name_file}.pdf"
            )
            musterloesung_btn_key = f"download_musterloesung_review_{selected_file}"
            musterloesung_dl_key = f"dl_musterloesung_direct_{selected_file}"
            if st.button("Download starten", key=musterloesung_btn_key):
                with st.spinner("Musterlösung wird erstellt..."):
                    try:
                        pdf_bytes = generate_musterloesung_pdf(
                            selected_file, list(questions), app_config
                        )
                        st.download_button(
                            label="💾 Musterlösung herunterladen",
                            data=pdf_bytes,
                            file_name=muster_download_name,
                            mime="application/pdf",
                            key=musterloesung_dl_key
                        )
                    except Exception as e:
                        st.error(f"Fehler beim Erzeugen der Musterlösung: {e}")

        # Mini-Glossar
        with st.expander("📄 Mini-Glossar (PDF mit allen Fachbegriffen)"):
            st.markdown("Erstelle ein kompaktes Glossar aller im Test vorkommenden Begriffe und Definitionen. Praktisch zum schnellen Nachschlagen.")
            glossary_download_name = (
                f"mini_glossar_"
                f"{selected_file.replace('questions_', '').replace('.json', '')}.pdf"
            )
            glossar_btn_key = f"download_glossar_review_{selected_file}"
            glossar_dl_key = f"dl_glossar_direct_{selected_file}"
            if st.button("Download starten", key=glossar_btn_key):
                with st.spinner("Glossar wird erstellt..."):
                    try:
                        pdf_bytes = generate_mini_glossary_pdf(
                            selected_file, list(questions)
                        )
                        st.download_button(
                            label="💾 Mini-Glossar herunterladen",
                            data=pdf_bytes,
                            file_name=glossary_download_name,
                            mime="application/pdf",
                            key=glossar_dl_key
                        )
                    except Exception as e:
                        st.error(f"Fehler beim Erzeugen des Mini-Glossars: {e}")

        # Testbericht
        with st.expander("📄 Testbericht (PDF mit deinem Ergebnis)"):
            st.markdown("Lade einen ausführlichen Testbericht mit deinem Punktestand, Antwortübersicht und Zeitstatistiken herunter. Perfekt zur Dokumentation deines Fortschritts.")
            report_download_name = (
                f"testbericht_"
                f"{selected_file.replace('questions_', '').replace('.json', '')}"
                f"_{user_name_file}.pdf"
            )
            testbericht_btn_key = f"download_testbericht_review_{selected_file}"
            testbericht_dl_key = f"dl_testbericht_direct_{selected_file}"
            if st.button("Download starten", key=testbericht_btn_key):
                with st.spinner("Testbericht wird erstellt..."):
                    try:
                        if app_config is None:
                            raise Exception("app_config nicht gefunden – Testbericht-Export nicht möglich.")
                        pdf_bytes = generate_pdf_report(
                            list(questions), app_config
                        )
                        st.download_button(
                            label="💾 Testbericht herunterladen",
                            data=pdf_bytes,
                            file_name=report_download_name,
                            mime="application/pdf",
                            key=testbericht_dl_key
                        )
                    except Exception as e:
                        st.error(f"Fehler beim Erzeugen des Testberichts: {e}")
