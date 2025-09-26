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
from helpers import smart_quotes_de, format_explanation_text
from data_manager import save_answer, update_bookmarks_for_user, load_all_logs
from components import show_motivation, render_question_distribution_chart


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
        st.markdown(f"### Noch {remaining} Frage{'n' if remaining != 1 else ''}")

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
                if st.button("Test fortsetzen", key=f"resume_btn_{frage_idx}"):
                    st.session_state.jump_to_idx = resume_target_idx
                    # Resume-Status zurücksetzen
                    del st.session_state.resume_next_idx
                    if "jump_to_idx_active" in st.session_state:
                        del st.session_state.jump_to_idx_active
                    st.rerun()
            # Wenn wir am Fortsetzungspunkt angekommen sind, Status zurücksetzen
            elif resume_target_idx == frage_idx:
                del st.session_state.resume_next_idx
                if "jump_to_idx_active" in st.session_state:
                    del st.session_state.jump_to_idx_active

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