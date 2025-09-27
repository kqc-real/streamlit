"""
Modul für die Hauptansichten der Nutzer-Interaktion.

Verantwortlichkeiten:
- Rendern der Fragenansicht.
- Rendern der finalen Zusammenfassung.
"""
import streamlit as st
import pandas as pd
import time

from config import AppConfig, list_question_files, load_questions
from logic import (
    calculate_score,
    set_question_as_answered,
    get_answer_for_question,
    is_test_finished,
)
from helpers import smart_quotes_de, format_explanation_text, get_user_id_hash
from data_manager import save_answer, update_bookmarks_for_user, load_all_logs
from components import show_motivation, render_question_distribution_chart


def render_welcome_page(app_config: AppConfig):
    """Zeigt die Startseite für nicht eingeloggte Nutzer."""

    # --- Auswahl des Fragensets ---
    question_files = list_question_files()
    if not question_files:
        st.error("Keine Fragensets (z.B. `questions_Data_Science.json`) gefunden.")
        return

    current_selection = st.session_state.get("selected_questions_file", question_files[0])
    
    # Erstelle eine benutzerfreundlichere Anzeige für die Dateinamen
    def format_filename(filename):
        name = filename.replace("questions_", "").replace(".json", "").replace("_", " ")
        try:
            # Lade die Fragen, um die Anzahl zu ermitteln.
            num_questions = len(load_questions(filename))
            return f"{name} ({num_questions} Fragen)"
        except Exception:
            return f"{name} (Fehler)"

    selected_file = st.selectbox(
        "Wähle ein Fragenset:",
        options=question_files,
        index=question_files.index(current_selection) if current_selection in question_files else 0,
        format_func=format_filename,
        key="main_view_question_file_selector"
    )

    if selected_file != st.session_state.get("selected_questions_file"):
        st.session_state.selected_questions_file = selected_file
        st.rerun()

    # --- Dynamischer Titel und Willkommensnachricht ---
    # Der Titel wird aus dem ausgewählten Dateinamen generiert.
    dynamic_title = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    st.markdown(f"""
        <div style='text-align: center; padding: 0 0 10px 0;'>
            <h2 style='color:#4b9fff; font-size: clamp(1.5rem, 5vw, 2.1rem); margin-bottom: 0.5rem;'>Multiple-Choice-Test</h2>
            <h1 style='font-size: clamp(1.8rem, 7vw, 2.8rem); margin-top: 0; line-height: 1.2;'>{dynamic_title}</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- Diagramm zur Verteilung der Fragen ---
    with st.expander("Verteilung der Fragen im Set anzeigen", expanded=True):
        questions = load_questions(selected_file)
        if questions:
            render_question_distribution_chart(questions)
        else:
            st.warning("Das ausgewählte Fragenset ist leer oder konnte nicht geladen werden.")

    # --- Öffentliches Leaderboard ---
    if app_config.show_top5_public:
        with st.expander("🏆 Aktuelle Top 10", expanded=False):
            df_logs = load_all_logs()
            
            # Filtere Logs auf das aktuell ausgewählte Fragenset
            if not df_logs.empty and "questions_file" in df_logs.columns:
                df_logs = df_logs[df_logs["questions_file"] == selected_file].copy()

            if df_logs.empty:
                st.info("Noch keine Ergebnisse für dieses Fragenset vorhanden.")
            else:
                # Stelle sicher, dass die 'zeit'-Spalte ein Datumsformat hat
                if 'zeit' in df_logs.columns:
                    df_logs['zeit'] = pd.to_datetime(df_logs['zeit'], errors='coerce')

                scores = (
                    df_logs.groupby("user_id_hash")
                    .agg(
                        Pseudonym=("user_id_plain", "first"),
                        Punkte=("richtig", "sum"),
                        Datum=("zeit", "max"),
                    )
                    .sort_values("Punkte", ascending=False)
                    .head(10)
                    .reset_index()  # Verhindert, dass der Hash als Index angezeigt wird
                )

                # Ersetze den Admin-Benutzernamen durch das Pseudonym "Alan C. Kay"
                if app_config.admin_user:
                    admin_mask = scores["Pseudonym"].str.lower() == app_config.admin_user.lower()
                    scores.loc[admin_mask, "Pseudonym"] = "Alan C. Kay"

                # Berechne die maximale Punktzahl für dieses Set
                questions_for_max_score = load_questions(selected_file)
                max_score_for_set = sum(q.get("gewichtung", 1) for q in questions_for_max_score)
                scores["Max. Punkte"] = max_score_for_set

                # Formatiere das Datum
                scores["Datum"] = scores["Datum"].dt.strftime('%d.%m.%Y')

                # Dekoriere die Top 3 mit Icons und nummeriere den Rest
                icons = ["🥇", "🥈", "🥉"]
                for i in range(len(scores)):
                    if i < len(icons):
                        scores.loc[i, "Pseudonym"] = f"{icons[i]} {scores.loc[i, 'Pseudonym']}"
                    else:
                        scores.loc[i, "Pseudonym"] = f"{i + 1}. {scores.loc[i, 'Pseudonym']}"

                st.dataframe(scores[["Pseudonym", "Punkte", "Max. Punkte", "Datum"]], use_container_width=True, hide_index=True)

    st.divider()

    # --- Login-Formular im Hauptbereich ---
    from auth import initialize_session_state, is_admin_user
    from config import load_scientists
    from data_manager import get_used_pseudonyms

    st.markdown("<h3 style='text-align: center;'>Neuen Test starten</h3>", unsafe_allow_html=True)

    scientists = load_scientists()
    used_pseudonyms = get_used_pseudonyms()
    
    available_scientists = [
        f"{s['name']} ({s['contribution']})" for s in scientists 
        if s['name'] not in used_pseudonyms
    ]

    # Admin-Login-Option hinzufügen
    admin_user = app_config.admin_user
    admin_display_name = ""
    if admin_user:
        admin_display_name = "Alan C. Kay (Pionier der OOP & GUIs)"
        available_scientists = [s for s in available_scientists if not s.startswith(admin_user) and not s.startswith("Alan C. Kay")]
        available_scientists.insert(0, admin_display_name)

    selected_name_formatted = st.selectbox(
        "Wähle dein Pseudonym für diese Runde:",
        options=available_scientists,
        placeholder="Bitte wählen...",
        index=None,
    )

    # Zentriere den Button mit Spalten
    _, col2, _ = st.columns([2, 1.5, 2])
    with col2:
        if st.button("Test starten", type="primary", use_container_width=True):
            if not selected_name_formatted:
                st.error("Bitte wähle ein Pseudonym aus.")
            else:
                user_name = admin_user if selected_name_formatted == admin_display_name else selected_name_formatted.split(" (")[0]
                st.session_state.user_id = user_name
                st.session_state.user_id_hash = get_user_id_hash(user_name)
                st.session_state.show_pseudonym_reminder = True
                initialize_session_state(questions)
                st.rerun()

def render_question_view(questions: list, frage_idx: int, app_config: AppConfig):
    """Rendert die Ansicht für eine einzelne Frage."""
    if st.session_state.get("show_pseudonym_reminder", False):
        st.success(f"**Willkommen, {st.session_state.user_id}!** Bitte merke dir dein Pseudonym gut, um den Test später fortsetzen zu können.")
        del st.session_state.show_pseudonym_reminder

    frage_obj = questions[frage_idx]
    frage_text = smart_quotes_de(frage_obj["frage"])
    thema = frage_obj.get("thema", "")
    gewichtung = frage_obj.get("gewichtung", 1)

    with st.container(border=True):
        # --- Countdown-Timer ---
        if st.session_state.start_zeit and not is_test_finished(questions):
            elapsed_time = (pd.Timestamp.now() - st.session_state.start_zeit).total_seconds()
            remaining = int(st.session_state.test_time_limit - elapsed_time)
            
            col1, col2 = st.columns(2)
            with col1:
                if remaining > 0:
                    minutes, seconds = divmod(remaining, 60)
                    st.metric("⏳ Verbleibende Zeit", f"{minutes:02d}:{seconds:02d}")
                    if remaining <= 5 * 60 and remaining > 0:
                        st.warning(f"Achtung, nur noch {minutes} Minuten!")
                else:
                    st.session_state.test_time_expired = True
                    st.error("⏰ Zeit ist um!")
                    st.rerun()
            with col2:
                pass # Platzhalter für Layout

        # Zähler für verbleibende Fragen
        num_answered = sum(
            1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
        )
        remaining = len(questions) - num_answered
        
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


        # Zeige Willkommensnachricht und Scoring-Info nur bei der ersten Frage
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

        if thema:
            st.caption(f"Thema: {thema}")
        st.markdown(
            f"**{frage_text}** <span style='color:#888; font-size:0.9em;'>(Gewicht: {gewichtung})</span>",
            unsafe_allow_html=True,
        )

        # --- Resume-Logik nach Sprung von Bookmark ---
        resume_target_idx = st.session_state.get("resume_next_idx")
        if resume_target_idx is not None:
            # Wenn wir auf einer gebookmarkten Frage sind (und nicht dort, wo wir sein sollten)
            if resume_target_idx != frage_idx and st.session_state.get("jump_to_idx_active"):
                st.warning("Du bist im Review-Modus einer markierten Frage.")
                if st.button("Test fortsetzen", key=f"resume_btn_{frage_idx}"):
                    st.session_state.jump_to_idx = resume_target_idx
                    # Resume-Status zurücksetzen
                    del st.session_state.resume_next_idx
                    # Setze den Aktiv-Status explizit auf False, anstatt ihn zu löschen.
                    st.session_state.jump_to_idx_active = False
                    st.rerun()
            # Wenn wir am Fortsetzungspunkt angekommen sind, Status zurücksetzen
            elif resume_target_idx == frage_idx:
                del st.session_state.resume_next_idx
                # Setze den Aktiv-Status explizit auf False, anstatt ihn zu löschen.
                st.session_state.jump_to_idx_active = False

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
            format_func=lambda x: optionen[x],
        )

        antwort = optionen[selected_index] if selected_index is not None else None

        # --- Bookmark-Logik ---
        is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
        if st.toggle("🔖 Merken", value=is_bookmarked, key=f"bm_toggle_{frage_idx}"):
            if not is_bookmarked:
                st.session_state.bookmarked_questions.append(frage_idx)
                update_bookmarks_for_user(st.session_state.user_id_hash, st.session_state.bookmarked_questions, questions)
        else:
            if is_bookmarked:
                st.session_state.bookmarked_questions.remove(frage_idx)
                update_bookmarks_for_user(st.session_state.user_id_hash, st.session_state.bookmarked_questions, questions)

        # --- Antwort auswerten ---
        if antwort and not is_answered:
            if st.button("Antworten", key=f"submit_{frage_idx}"):
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
                save_answer(
                    st.session_state.user_id_hash,
                    st.session_state.user_id,
                    frage_obj,
                    antwort,
                    punkte,
                    is_bookmarked,
                    st.session_state.selected_questions_file
                )
                st.session_state[f"show_explanation_{frage_idx}"] = True
                st.rerun()

        # --- Erklärung anzeigen ---
        if st.session_state.get(f"show_explanation_{frage_idx}", False):
            render_explanation(frage_obj, app_config, questions)

def render_explanation(frage_obj: dict, app_config: AppConfig, questions: list):
    """Rendert den Feedback- und Erklärungsblock nach einer Antwort."""
    st.divider() 
    
    # Feedback (richtig/falsch)
    richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
    gegebene_antwort = get_answer_for_question(questions.index(frage_obj))
    ist_richtig = gegebene_antwort == richtige_antwort_text

    if ist_richtig:
        # Zeige die Ballons bei jeder richtigen Antwort
        if "celebrated_questions" not in st.session_state:
            st.session_state.celebrated_questions = []
        st.balloons()
        st.markdown(f"Richtig! Die Antwort war: **{richtige_antwort_text}**")
    else:
        st.markdown(f"Leider falsch. Deine Antwort war: {gegebene_antwort}. Richtig ist: **{richtige_antwort_text}**")

    # Erklärungstext
    erklaerung = frage_obj.get("erklaerung")
    if erklaerung:
        with st.container(border=True):
            st.markdown("<span style='font-weight:600; color:#4b9fff;'>Erklärung:</span>", unsafe_allow_html=True)
            # Prüfe, ob die Erklärung ein strukturiertes Objekt ist
            if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                st.markdown(f"**{erklaerung['titel']}**")
                # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                # und bei Bedarf scrollbar zu sein.
                for i, schritt in enumerate(erklaerung['schritte']):
                    cols = st.columns([1, 19])
                    with cols[0]:
                        st.markdown(f"{i+1}.")
                    with cols[1]:
                        st.markdown(f"<div class='scrollable-katex'>{schritt}</div>", unsafe_allow_html=True)
            else:
                # Fallback für einfache String-Erklärungen
                st.markdown(str(erklaerung))

    show_motivation(questions, app_config)

    if st.button("Nächste Frage", key=f"next_q_{questions.index(frage_obj)}"):
        st.session_state[f"show_explanation_{questions.index(frage_obj)}"] = False
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

    if prozent >= 100:
        st.balloons()
        st.snow()
        st.success("Exzellent! Du bist ein wahrer Meister.")
    elif prozent >= 70:
        st.success("Sehr gut gemacht!")
    elif prozent >= 50:
        st.info("Gut gemacht, die Grundlagen sitzen.")
    else:
        st.warning("Da ist noch Luft nach oben. Nutze den Review-Modus zum Lernen!")

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


def render_review_mode(questions: list):
    """Rendert den interaktiven Review-Modus am Ende des Tests."""
    st.subheader("🧐 Review deiner Antworten")

    filter_option = st.selectbox(
        "Filtere die Fragen:",
        ["Alle", "Nur falsch beantwortete", "Nur richtig beantwortete", "Nur markierte"],
    )

    for i, frage in enumerate(questions):
        # Variablen vorab definieren, damit sie im Filter verfügbar sind
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage["optionen"][frage["loesung"]]
        ist_richtig = gegebene_antwort == richtige_antwort_text

        # Filterlogik
        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        is_bookmarked = i in st.session_state.get("bookmarked_questions", [])

        if filter_option == "Nur falsch beantwortete" and (punkte is None or punkte > 0):
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
        with st.expander(f"{icon} Frage {i+1}: {title_text}"):
            st.markdown(f"**{smart_quotes_de(frage['frage'])}**")
            st.markdown(f"Deine Antwort: {gegebene_antwort}")
            if not ist_richtig:
                st.markdown(f"Richtige Antwort: {richtige_antwort_text}")

            erklaerung = frage.get("erklaerung")
            if erklaerung:
                with st.container(border=True):
                    st.markdown("<span style='font-weight:600; color:#4b9fff;'>Erklärung:</span>", unsafe_allow_html=True)
                    if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                        st.markdown(f"**{erklaerung['titel']}**")
                        # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                        # und bei Bedarf scrollbar zu sein.
                        for i, schritt in enumerate(erklaerung['schritte']):
                            cols = st.columns([1, 19])
                            with cols[0]:
                                st.markdown(f"{i+1}.")
                            with cols[1]:
                                st.markdown(f"<div class='scrollable-katex'>{schritt}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(str(erklaerung))