"""
Modul für die Hauptansichten der Nutzer-Interaktion.

Verantwortlichkeiten:
- Rendern der Fragenansicht.
- Rendern der finalen Zusammenfassung.
"""
import streamlit as st
import pandas as pd
import time
import locale

from config import AppConfig, list_question_files, load_questions, get_question_counts
from logic import (
    calculate_score,
    set_question_as_answered,
    get_answer_for_question,
    is_test_finished,
)
from helpers import smart_quotes_de, get_user_id_hash
from database import update_bookmarks
from components import render_question_distribution_chart


def render_welcome_page(app_config: AppConfig):
    """Zeigt die Startseite für nicht eingeloggte Nutzer."""

    # --- Dynamischer Titel und Willkommensnachricht ---
    # Der Titel wird aus dem ausgewählten Dateinamen generiert, der im Session State liegt.
    # Falls noch kein Set ausgewählt wurde, wird das erste verfügbare als Default genommen.
    if "selected_questions_file" not in st.session_state:
        all_files = list_question_files()
        if all_files:
            st.session_state.selected_questions_file = all_files[0]
        else:
            st.error("Keine Fragensets (z.B. `questions_Data_Science.json`) gefunden.")
            st.info("Stelle sicher, dass gültige, nicht-leere JSON-Dateien mit Fragen im Projektverzeichnis liegen.")
            return

    selected_file = st.session_state.get("selected_questions_file")
    dynamic_title = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    st.markdown(f"""
        <div style='text-align: center; padding: 0 0 10px 0;'>
            <h2 style='color:#4b9fff; font-size: clamp(1.5rem, 5vw, 2.1rem);'>MC-Tests zu IU-Kursen</h2>
            <h2 style='color:#4b9fff; font-size: clamp(1.0rem, 2vw, 1.5rem); margin-top: -1.5rem;'>App & Fragen KI generiert</h2>
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

    # Erstelle eine benutzerfreundlichere Anzeige für die Dateinamen
    def format_filename(filename):
        name = filename.replace("questions_", "").replace(".json", "").replace("_", " ")
        num_questions = question_counts.get(filename)
        return f"{name} ({num_questions} Fragen)" if num_questions else f"{name} (Fehler)"

    current_selection = st.session_state.get("selected_questions_file", valid_question_files[0])
    selected_file = st.selectbox(
        "Wähle ein Fragenset:",
        options=valid_question_files,
        index=valid_question_files.index(current_selection) if current_selection in valid_question_files else 0,
        format_func=format_filename,
        key="main_view_question_file_selector",
        label_visibility="collapsed"
    )

    if selected_file != st.session_state.get("selected_questions_file"):
        st.session_state.selected_questions_file = selected_file
        st.rerun()
    # --- Diagramm zur Verteilung der Fragen ---
    with st.expander("Verteilung nach Thema und Schwierigkeit", expanded=True):
        questions = load_questions(selected_file)
        if questions:
            render_question_distribution_chart(questions)
        else:
            st.warning("Das ausgewählte Fragenset ist leer oder konnte nicht geladen werden.")

    # --- Öffentliches Leaderboard ---
    if app_config.show_top5_public:
        # Berechne die maximale Punktzahl für das ausgewählte Set
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions)
        leaderboard_title = f"🏆 Aktuelle Top 10 (max. {max_score_for_set} Punkte)"
        with st.expander(leaderboard_title, expanded=False):
            from database import get_all_logs_for_leaderboard
            
            leaderboard_data = get_all_logs_for_leaderboard(selected_file)

            if not leaderboard_data:
                st.info("Noch keine Ergebnisse für dieses Fragenset vorhanden.")
            else:
                scores = pd.DataFrame(leaderboard_data)
                scores.rename(columns={
                    'user_pseudonym': 'Pseudonym',
                    'total_score': 'Punkte',
                    'last_test_time': 'Datum',
                    'duration_seconds': 'Dauer',
                }, inplace=True)

                # Formatiere die Dauer von Sekunden in MM:SS
                def format_duration(seconds):
                    mins, secs = divmod(seconds, 60)
                    return f"{int(mins):02d}:{int(secs):02d}"
                scores['Dauer'] = scores['Dauer'].apply(format_duration)

                # Formatiere das Datum
                scores["Datum"] = pd.to_datetime(scores["Datum"]).dt.strftime('%d.%m.%y')

                # Dekoriere die Top 3 mit Icons und nummeriere den Rest
                icons = ["🥇", "🥈", "🥉"]
                for i in range(len(scores)):
                    if i < len(icons):
                        scores.loc[i, "Pseudonym"] = f"{icons[i]} {scores.loc[i, 'Pseudonym']}"
                    else:
                        scores.loc[i, "Pseudonym"] = f"{i + 1}. {scores.loc[i, 'Pseudonym']}"

                st.dataframe(scores[["Pseudonym", "Punkte", "Dauer", "Datum"]], use_container_width=True, hide_index=True)


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
        st.warning("Alle verfügbaren Pseudonyme sind bereits in Verwendung. Bitte kontaktiere den Admin.")
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
        if st.button("Test starten", type="primary", use_container_width=True, disabled=(not selected_name_from_user)):
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
                initialize_session_state(questions)
                st.rerun()
            else:
                st.error("Datenbankfehler: Konnte keine neue Test-Session starten.")

def render_question_view(questions: list, frage_idx: int, app_config: AppConfig):
    """Rendert die Ansicht für eine einzelne Frage."""
    if st.session_state.get("show_pseudonym_reminder", False):
        st.success(f"**Willkommen, {st.session_state.user_id}!** Bitte merke dir dein Pseudonym gut, um den Test später fortsetzen zu können.")
        del st.session_state.show_pseudonym_reminder

    # --- Sicherheitscheck und Re-Initialisierung ---
    # Dieser Block fängt den Zustand ab, in dem ein neues Fragenset ausgewählt wurde,
    # aber der session_state (insb. optionen_shuffled) noch vom alten Set stammt.
    if len(st.session_state.get("optionen_shuffled", [])) != len(questions):
        from auth import initialize_session_state
        st.warning("Erkenne Wechsel des Fragensets, initialisiere Test neu...")
        initialize_session_state(questions)
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

    # Zähler für verbleibende Fragen (früh berechnen für alle Logik)
    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    remaining = len(questions) - num_answered

    with st.container(border=True):
        # Zeige Willkommensnachricht GANZ OBEN (wichtig für Mobile UX!)
        if num_answered == 0:
            st.title("Los geht's!")
            if app_config.scoring_mode == "positive_only":
                scoring_text = (
                    "Für eine richtige Antwort erhältst du die volle Gewichtung (z. B. 2 Punkte), "
                    "falsche Antworten geben 0 Punkte."
                )
            else:
                scoring_text = "Richtig: +Gewichtung, falsch: -Gewichtung."
            
            info_html = (
                "<div style='padding:10px 14px; background:#1f1f1f80; border-radius: 8px; margin-bottom: 1rem;'>"
                "<span style=\"display:inline-block;background:#2d3f5a;color:#fff;padding:2px 8px;"
                "border-radius:12px;font-size:0.75rem;font-weight:600;letter-spacing:.5px;\">✅ 1 richtige Option</span> "
                "Wähle mit Bedacht, du hast keine zweite Chance pro Frage.<br><br>"
                "<span style=\"display:inline-block;background:#2d3f5a;color:#fff;padding:2px 8px;"
                "border-radius:12px;font-size:0.75rem;font-weight:600;letter-spacing:.5px;\">🎯 Punktelogik</span> "
                f"{scoring_text}"
                "</div>"
            )
            st.markdown(info_html, unsafe_allow_html=True)

        # --- Countdown-Timer ---
        if st.session_state.start_zeit and not is_test_finished(questions):
            elapsed_time = (pd.Timestamp.now() - st.session_state.start_zeit).total_seconds()
            remaining_time = int(st.session_state.test_time_limit - elapsed_time)
            
            col1, col2 = st.columns(2)
            with col1:
                if remaining_time > 0:
                    minutes, seconds = divmod(remaining_time, 60)
                    st.metric("⏳ Verbleibende Zeit", f"{minutes:02d}:{seconds:02d}")
                    if remaining_time <= 5 * 60 and remaining_time > 0:
                        st.warning(f"Achtung, nur noch {minutes} Minuten!")
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
                if st.button("↪️ Überspringen", key=f"skip_{frage_idx}", use_container_width=True):
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
                if st.button("Antworten", key=f"submit_{frage_idx}", type="primary", use_container_width=True, disabled=(antwort is None)):
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
                    if st.button("Test fortsetzen", key=f"resume_from_answered_bm_{frage_idx}", type="primary", use_container_width=True):
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
        st.warning(f"Bitte warte kurz, bevor du die nächste Antwort abgibst (Limit: {app_config.min_seconds_between_answers}s).")
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
        st.markdown(f"<span style='color:#28a745; font-weight:bold;'>Richtig:</span> {formatted_richtige_antwort}", unsafe_allow_html=True)

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
                for i, schritt in enumerate(erklaerung['schritte']):
                    cols = st.columns([1, 19])
                    with cols[0]:
                        st.markdown(f"{i+1}.")
                    with cols[1]:
                        st.markdown(f"<div class='scrollable-katex'>{smart_quotes_de(schritt)}</div>", unsafe_allow_html=True)
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
                if st.button("🧠 Zeige detaillierte Erklärung", key=f"btn_extended_{frage_idx}", use_container_width=True):
                    st.session_state[show_extended_key] = True
                    st.rerun()
        
        if st.session_state.get(show_extended_key, False):
            with st.expander("Detaillierte Erklärung", expanded=True):
                if isinstance(extended_explanation, dict):
                    st.markdown(f"**{smart_quotes_de(extended_explanation.get('title', ''))}**")
                    st.markdown(smart_quotes_de(extended_explanation.get('content', '')))
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
        st.success("✔️ Danke, dein Feedback wurde übermittelt.")
    else:
        # Zentriere den Popover-Button in der mittleren Spalte für ein konsistentes Layout
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            with st.popover("Problem mit dieser Frage melden", use_container_width=True):
                st.markdown("**Welche Probleme sind dir aufgefallen?**")

                # --- Custom CSS für den roten Button ---
                # Wir definieren eine CSS-Klasse für den aktiven Button und wenden sie an.
                # Der Key des Buttons wird als Teil des CSS-Selektors verwendet.
                button_key = f"btn_submit_feedback_{frage_idx}"
                st.markdown(f"""
                <style>
                    /* Ziel: Der Streamlit-Button, wenn er nicht deaktiviert ist */
                    div[data-testid="stButton"] > button[kind="primary"]:not(:disabled) {{
                        background-color: #d32f2f; /* Ein kräftiges Rot */
                        color: white;
                        border-color: #d32f2f;
                    }}
                    div[data-testid="stButton"] > button[kind="primary"]:not(:disabled):hover {{
                        background-color: #b71c1c; /* Ein dunkleres Rot beim Hover */
                        border-color: #b71c1c;
                    }}
                </style>
                """, unsafe_allow_html=True)
                
                # Verwende Checkboxen statt Multiselect für eine bessere UX
                selected_feedback_types = []
                for option in feedback_options:
                    # Der Key muss eindeutig pro Frage und Option sein
                    if st.checkbox(option, key=f"cb_feedback_{frage_idx}_{option}"):
                        selected_feedback_types.append(option)
                
                # Der Senden-Button ist direkt im Popover und wird aktiv, wenn eine Auswahl getroffen wurde.
                st.button(
                    "Feedback senden", key=button_key,
                    on_click=_handle_feedback_submission, args=(frage_idx, frage_obj, selected_feedback_types),
                    disabled=not selected_feedback_types, use_container_width=True,
                    type="primary" if selected_feedback_types else "secondary"
                )

    # Zeige den "Nächste Frage"-Button nur an, wenn der Nutzer nicht gerade
    # im Sprung-Modus eine bereits beantwortete Frage reviewt.
    if not st.session_state.get("jump_to_idx_active"):
        render_next_question_button(questions, questions.index(frage_obj))


def render_next_question_button(questions: list, frage_idx: int):
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
        if st.button(button_text, key=f"next_q_{frage_idx}", type="primary", use_container_width=True):
            # Setze das Flag zurück, um die Erklärung bei der nächsten Anzeige nicht mehr zu zeigen.
            st.session_state[f"show_explanation_{frage_idx}"] = False
            st.rerun()


def render_final_summary(questions: list, app_config: AppConfig):
    """Zeigt die finale Zusammenfassung und den Review-Modus an."""
    st.header("🚀 Test abgeschlossen!")

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    st.metric("Dein Endergebnis", f"{current_score} / {max_score} Punkte", f"{prozent:.1f}%")

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
            "🏆 Perfekt! 100% – Makellose Runde!",
            "⚡ Fehlerlos! Absolute Elite-Leistung.",
            "💎 Makellos! Alle Fragen richtig.",
            "🌟 100%! Du bist ein wahrer Meister.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 90:  # Exzellent (90-99%)
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
    elif prozent >= 50:  # Ausreichend (50-59%)
        messages = [
            "⚠️ Ausreichend. Deutlicher Nachholbedarf.",
            "📖 Knapp bestanden. Erklärungen nutzen!",
            "🎯 50-59%. Themen gezielt wiederholen.",
            "🔄 Schwankend. Review zeigt Schwächen auf.",
        ]
        st.warning(random.choice(messages))
    elif prozent >= 40:  # Mangelhaft (40-49%)
        messages = [
            "⛔ Mangelhaft. Grundlagen fehlen noch.",
            "📕 Unter 50%. Intensive Wiederholung nötig.",
            "🚨 Lücken groß. Review-Modus ist Pflicht.",
            "🔴 Viele Fehler. Stoff nochmal durcharbeiten.",
        ]
        st.warning(random.choice(messages))
    else:  # Ungenügend (<40%)
        messages = [
            "❌ Ungenügend. Stoff von Grund auf lernen.",
            "📚 Unter 40%. Systematisch neu starten.",
            "🆘 Große Wissenslücken. Hilfe holen!",
            "⚠️ Sehr schwach. Review zeigt alle Fehler.",
        ]
        st.error(random.choice(messages))

    # --- Performance-Analyse pro Thema ---
    st.subheader("Deine Leistung nach Themen")

    topic_performance = {}
    for i, frage in enumerate(questions):
        thema = frage.get("thema", "Allgemein")
        if thema not in topic_performance:
            topic_performance[thema] = {"erreicht": 0, "maximal": 0}

        max_punkte = frage.get("gewichtung", 1)
        topic_performance[thema]["maximal"] += max_punkte

        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        if punkte is not None:
            # Nur positive Punkte für die Leistungsanalyse zählen, um negative Scores zu vermeiden.
            erreichte_punkte = max(0, punkte)
            topic_performance[thema]["erreicht"] += erreichte_punkte

    # DataFrame für die Visualisierung erstellen
    performance_data = []
    for thema, scores in topic_performance.items():
        if scores["maximal"] > 0:
            prozent = (scores["erreicht"] / scores["maximal"]) * 100
            performance_data.append({"Thema": thema, "Leistung (%)": prozent})

    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        df_performance = df_performance.set_index("Thema")
        st.bar_chart(df_performance, color="#4b9fff")
    else:
        st.info("Keine Daten für eine themenspezifische Analyse verfügbar.")


    st.divider()
    render_review_mode(questions)
    
    # --- PDF-Export (am Ende, nach Review) ---
    st.divider()
    st.subheader("📄 PDF-Export")
    
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
    
    # Dynamische Zeitschätzung mit Probe-Rendering
    if has_math and first_formula:
        # Zeige Info über Formel-Benchmark
        with st.expander("⏱️ Zeitschätzung", expanded=True):
            st.info(
                f"📊 Dieses Fragenset enthält **{formula_count} Formeln** "
                f"in {anzahl_fragen} Fragen.\n\n"
                "Für eine genaue Zeitschätzung wird eine Probe-Formel gerendert..."
            )
            
            # Benchmark mit Probe-Formel
            import time
            import random
            from pdf_export import _render_latex_to_image
            
            benchmark_placeholder = st.empty()
            benchmark_placeholder.text("🔄 Rendere Probe-Formel...")
            
            # Verwende eine eindeutige Test-Formel mit Zufallskomponente
            # um Cache-Treffer zu vermeiden
            random_num = random.randint(1000, 9999)
            # Wähle Test-Formel basierend auf Komplexität der echten Formeln
            if any('\\begin{' in first_formula for first_formula in [first_formula]):
                # Komplexe Matrix/Array-Formel für Tests mit Matrizen
                test_latex = f"\\begin{{pmatrix}}{random_num}&1\\\\2&3\\end{{pmatrix}}"
                is_block = True
            elif len(first_formula.strip('$')) > 30:
                # Mittlere Komplexität für längere Formeln
                test_latex = f"\\sum_{{i=1}}^{{{random_num}}} x_i^2 + \\alpha"
                is_block = False
            else:
                # Einfache Formel für kurze Formeln
                test_latex = f"x_{{{random_num}}} + y = z"
                is_block = False
            
            start_time = time.time()
            try:
                _render_latex_to_image(test_latex, is_block)
                render_time = time.time() - start_time
                
                # Fallback: Wenn Zeit zu klein (wahrscheinlich Cache), verwende Minimum
                if render_time < 0.1:
                    render_time = 1.5  # Realistischer Durchschnittswert
                
                # Berechne geschätzte Gesamtdauer
                total_seconds = formula_count * render_time
                total_minutes = total_seconds / 60
                
                # Formatiere Zeitangabe
                if total_minutes < 1:
                    time_str = f"{int(total_seconds)} Sekunden"
                elif total_minutes < 2:
                    time_str = f"ca. 1 Minute"
                else:
                    time_str = f"ca. {int(total_minutes)} Minuten"
                
                benchmark_placeholder.success(
                    f"✅ Probe-Rendering: {render_time:.2f}s\n\n"
                    f"**Geschätzte Gesamtdauer:** {time_str}\n"
                    f"({formula_count} Formeln × {render_time:.2f}s)"
                )
            except Exception as e:
                benchmark_placeholder.warning(
                    f"⚠️ Probe-Rendering fehlgeschlagen: {e}\n\n"
                    f"Schätzung basiert auf Durchschnittswert: "
                    f"ca. {max(1, formula_count // 20)} Minuten"
                )
    
    # Button zum Generieren
    if st.button("📥 PDF jetzt generieren", type="primary", use_container_width=True):
        from pdf_export import generate_pdf_report
        
        # Fortschrittsanzeige passend zum Inhalt
        spinner_text = (
            f"⏳ Formeln werden konvertiert... Bitte warten ({anzahl_fragen} Fragen)"
            if has_math
            else f"⏳ PDF wird erstellt... ({anzahl_fragen} Fragen)"
        )
        with st.spinner(spinner_text):
            try:
                # Generiere die PDF-Daten im Speicher
                pdf_bytes = generate_pdf_report(questions, app_config)
                
                user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")
                q_file_clean = q_file_name.replace("questions_", "").replace(".json", "")
                
                st.success("✅ PDF erfolgreich erstellt!")
                
                # Download-Button
                st.download_button(
                    label="💾 PDF herunterladen",
                    data=pdf_bytes,
                    file_name=f"ergebnisse_{q_file_clean}_{user_name_file}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Fehler beim Erstellen des PDFs: {str(e)}")
                st.info("Versuche es bitte erneut oder kontaktiere den Support.")


def render_review_mode(questions: list):
    """Rendert den interaktiven Review-Modus am Ende des Tests."""
    st.subheader("🧐 Review deiner Antworten")
    
    # Die `initial_frage_indices` werden für die korrekte Nummerierung im Review-Modus benötigt.
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    filter_option = st.radio(
        "Filtere die Fragen:",
        ["Alle", "Nur falsch beantwortete", "Nur richtig beantwortete", "Nur markierte"],
    )

    for i, frage in enumerate(questions):
        # Variablen vorab definieren, damit sie im Filter verfügbar sind
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage["optionen"][frage["loesung"]]
        ist_richtig = gegebene_antwort == richtige_antwort_text

        # Formatiere die Antworten, um Markdown (wie `...`) in HTML umzuwandeln
        formatted_gegebene_antwort = smart_quotes_de(str(gegebene_antwort)) if gegebene_antwort is not None else "*(nicht beantwortet)*"
        formatted_richtige_antwort = smart_quotes_de(str(richtige_antwort_text))

        # Filterlogik
        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        is_bookmarked = i in st.session_state.get("bookmarked_questions", [])

        if filter_option == "Nur falsch beantwortete" and ist_richtig:
            continue
        if filter_option == "Nur richtig beantwortete" and not ist_richtig:
            continue
        if filter_option == "Nur markierte" and not is_bookmarked:
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

        with st.expander(f"{icon} Frage {display_question_number}: {title_text}"):
            st.markdown(f"**{smart_quotes_de(frage['frage'])}**")
            
            st.markdown(f"**Deine Antwort:** {formatted_gegebene_antwort}")
            if not ist_richtig:
                st.markdown(f"**Richtig:** {formatted_richtige_antwort}")


            erklaerung = frage.get("erklaerung")
            if erklaerung:
                with st.container(border=True):
                    st.markdown("<span style='font-weight:600; color:#4b9fff;'>Erklärung:</span>", unsafe_allow_html=True)
                    if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                        st.markdown(f"**{smart_quotes_de(erklaerung['titel'])}**")
                        # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                        # und bei Bedarf scrollbar zu sein.
                        for i, schritt in enumerate(erklaerung['schritte']):
                            cols = st.columns([1, 19])
                            with cols[0]:
                                st.markdown(f"{i+1}.")
                            with cols[1]:
                                st.markdown(f"<div class='scrollable-katex'>{smart_quotes_de(schritt)}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(smart_quotes_de(str(erklaerung)))