"""
Modul für wiederverwendbare UI-Komponenten.

Verantwortlichkeiten:
- Rendern der Sidebar.
- Anzeige von Bookmarks.
- Anzeige von Motivations-Feedback.
- Rendern von Diagrammen.
"""
import streamlit as st
import pandas as pd

from config import AppConfig
from logic import calculate_score, is_test_finished
from database import update_bookmarks


def render_sidebar(questions: list, app_config: AppConfig, is_admin: bool):
    """Rendert die komplette Sidebar der Anwendung."""
    st.sidebar.success(f"👋 **{st.session_state.user_id}**")

    # Zeige das aktuell ausgewählte Fragenset an
    selected_file = st.session_state.get("selected_questions_file")
    if selected_file:
        set_name = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
        st.sidebar.markdown(f"Fragenset: **{set_name}**")
        st.sidebar.divider()

    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    progress_pct = int((num_answered / len(questions)) * 100) if questions else 0

    st.sidebar.header("📋 Fortschritt")
    st.sidebar.progress(progress_pct, text=f"{progress_pct}%")

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    st.sidebar.metric("🎯 Punktestand", f"{current_score} / {max_score}")

    render_bookmarks(questions)
    render_skipped_questions(questions)

    # Füge einen "Zurück zum Review"-Button hinzu, wenn der Test beendet ist,
    # aber der Nutzer gerade eine einzelne Frage ansieht (z.B. nach Sprung von Bookmark).
    if is_test_finished(questions) and "jump_to_idx_active" in st.session_state and st.session_state.jump_to_idx_active:
        st.sidebar.divider()
        if st.sidebar.button("⬅️ Zurück zum Testreview", use_container_width=True):
            st.session_state.jump_to_idx_active = False # Deaktiviere den Review-Modus
            st.rerun()

    st.sidebar.divider()

    if is_admin:
        render_admin_switch(app_config)

    with st.sidebar.expander("⚠️ Session beenden"):
        st.warning(
            "Dein Punktestand wird gespeichert und der Test beendet. "
            "Für einen weiteren Versuch wähle ein neues Pseudonym."
        )

        if st.button("Session beenden", key="abort_session_btn", type="primary", use_container_width=True):
            # Speichere Bookmarks vor dem Abmelden direkt über die DB-Funktion
            bookmarked_q_nrs = [
                int(questions[i]['frage'].split('.')[0]) 
                for i in st.session_state.get("bookmarked_questions", [])
            ]
            if "session_id" in st.session_state:
                update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)

            # Speichere das Pseudonym für die Toast-Nachricht, bevor die Session gelöscht wird.
            aborted_user_id = st.session_state.get("user_id")

            # Lösche alle Session-Keys außer Admin-spezifischen und Fragenset-Auswahl
            for key in list(st.session_state.keys()):
                if not key.startswith("_admin") and key != "selected_questions_file":
                    del st.session_state[key]
            # Setze die Flags für die Toast-Nachricht nach dem Rerun
            st.session_state["session_aborted"] = True
            st.session_state["aborted_user_id"] = aborted_user_id
            st.rerun()

def render_admin_switch(app_config: AppConfig):
    """Rendert den Umschalter für das Admin-Panel in der Sidebar."""
    from auth import check_admin_key

    is_panel_active = st.session_state.get("show_admin_panel", False)

    if is_panel_active:
        st.sidebar.info("Du bist im Admin-Modus.")
        if st.sidebar.button("⬅️ Zurück zum Test", use_container_width=True):
            st.session_state.show_admin_panel = False
            st.rerun()
    else:
        # Wenn kein Admin-Key konfiguriert ist, erlaube direkten Zugang (für lokale Tests)
        if not app_config.admin_key:
            if st.sidebar.button("📊 Admin-Panel öffnen", use_container_width=True, type="primary"):
                st.session_state.show_admin_panel = True
                st.rerun()
        else:
            # Mit Admin-Key: Passwort-Eingabe erforderlich
            with st.sidebar.expander("🔐 Admin Panel"):
                entered_key = st.text_input("Admin-Key", type="password", key="admin_key_input_sidebar")
                if st.button("Panel aktivieren", key="admin_activate_sidebar_btn"):
                    if check_admin_key(entered_key, app_config):
                        st.session_state.show_admin_panel = True
                        st.rerun()
                    else:
                        st.error("Falscher Key.")


def render_bookmarks(questions: list):
    """Rendert die Bookmark-Sektion in der Sidebar."""
    with st.sidebar.expander("🔖 Markierte Fragen", expanded=True):
        bookmarks = st.session_state.get("bookmarked_questions", [])
        if not bookmarks:
            st.caption("Keine Fragen markiert.")
            return

        # Sortiere die Bookmarks nach der Reihenfolge, in der sie im Test erscheinen
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_bookmarks = sorted(bookmarks, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        for q_idx in sorted_bookmarks:
            cols = st.columns([4, 1])

            with cols[0]:
                # Korrekte Ermittlung der laufenden Nummer der Frage im Testdurchlauf.
                # Wir verwenden die *initiale* Reihenfolge für eine stabile Nummerierung.
                session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
                display_question_number = session_local_idx + 1
                if st.button(f"Frage {display_question_number}", key=f"bm_jump_{q_idx}"):
                    # Setze den Sprung-Index. Die Haupt-App-Logik wird diesen als
                    # nächste anzuzeigende Frage verwenden.
                    st.session_state["jump_to_idx"] = q_idx
                    
                    # Setze ein Flag, das anzeigt, dass ein Sprung aktiv ist.
                    # Dies wird in der Hauptansicht verwendet, um den Testfluss anzupassen.
                    st.session_state.jump_to_idx_active = True

                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"bm_del_{q_idx}", help="Bookmark entfernen"):
                    st.session_state.bookmarked_questions.remove(q_idx)
                    bookmarked_q_nrs = [
                        int(questions[i]['frage'].split('.')[0]) 
                        for i in st.session_state.bookmarked_questions
                    ]
                    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)
                    st.rerun()

        if st.button("🗑️ Alle entfernen", key="bm_clear_all"):
            st.session_state.bookmarked_questions = []
            # Leere Liste an die DB-Funktion übergeben
            if "session_id" in st.session_state:
                update_bookmarks(st.session_state.session_id, [])
            st.rerun()


def render_skipped_questions(questions: list):
    """Rendert die Sektion für übersprungene Fragen in der Sidebar."""
    with st.sidebar.expander("↪️ Übersprungen", expanded=True):
        skipped = st.session_state.get("skipped_questions", [])
        if not skipped:
            st.caption("Keine Fragen übersprungen.")
            return

        # Sortiere die übersprungenen Fragen nach der Reihenfolge im Test
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_skipped = sorted(skipped, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        for q_idx in sorted_skipped:
            # Korrekte Ermittlung der laufenden Nummer der Frage im Testdurchlauf.
            session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
            display_question_number = session_local_idx + 1
            
            if st.button(f"Frage {display_question_number}", key=f"skip_jump_{q_idx}"):
                st.session_state["jump_to_idx"] = q_idx
                st.session_state.jump_to_idx_active = True
                st.rerun()

        st.divider()
        if st.button("Alle zurücksetzen", key="skip_clear_all", help="Setzt alle übersprungenen Fragen zurück, sodass sie nicht mehr in dieser Liste erscheinen."):
            # Um sie zurückzusetzen, müssen wir sie aus der 'skipped' Liste entfernen
            # und wieder an ihre ursprüngliche Position in 'frage_indices' bringen.
            # Einfachere Variante: Nur die Liste leeren. Die Fragen bleiben am Ende der Warteschlange.
            st.session_state.skipped_questions = []
            st.rerun()


def get_motivation_message(questions: list, app_config: AppConfig) -> str:
    """Gibt eine kontextabhängige, motivierende Feedback-Nachricht als HTML-String zurück."""
    scoring_mode = app_config.scoring_mode
    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        scoring_mode,
    )

    outcomes = st.session_state.get("answer_outcomes", [])
    num_answered = len(outcomes)
    if num_answered == 0 or not questions:
        return ""

    last_correct = outcomes[-1] if outcomes else None

    # Streak-Berechnung
    streak = 0
    for o in reversed(outcomes):
        if o:
            streak += 1
        else:
            break

    # Phase basierend auf Fortschritt
    progress_pct = int((num_answered / len(questions)) * 100)
    if progress_pct < 30: phase = "early"
    elif progress_pct < 60: phase = "mid"
    elif progress_pct < 90: phase = "late"
    elif progress_pct < 100: phase = "close"
    else: phase = "final"

    # Tier basierend auf Leistung
    ratio = current_score / max_score if max_score > 0 else 0
    if ratio >= 0.9: tier = "elite"
    elif ratio >= 0.75: tier = "high"
    elif ratio >= 0.55: tier = "mid"
    else: tier = "low"

    # Badges (einmalig rendern)
    badge_list = []
    if streak >= 3:
        icon = "🔥"
        if streak >= 10: icon = "⚡"
        if streak >= 20: icon = "🏅"
        badge_list.append(f"{icon} {streak}er Streak")
    
    for thr, name, keyflag in [
        (25, "🔓 25%", "_badge25"), (50, "🏁 50%", "_badge50"),
        (75, "🚀 75%", "_badge75"), (100, "🏆 100%", "_badge100"),
    ]:
        if progress_pct >= thr and not st.session_state.get(keyflag):
            badge_list.append(name)
            st.session_state[keyflag] = True

    if badge_list:
        badges_html = "".join(
            f"<span style='display:inline-block; background:#333; padding:2px 8px; margin-right:5px; border-radius:12px; font-size:0.8em;'>{b}</span>"
            for b in badge_list
        )
        st.markdown(badges_html, unsafe_allow_html=True)

    # Basis-Phrasen pro (phase, tier)
    base_phrases = {
        ("early", "low"): ["Langsam eingrooven – Muster erkennen.", "Fehler sind Daten – weiter so."],
        ("early", "mid"): ["Solider Start – Fokus halten.", "Guter Einstieg – nicht überpacen."],
        ("early", "high"): ["Starker Auftakt – Muster sichern.", "Sehr sauber bisher."],
        ("early", "elite"): ["Makelloser Start – Elite-Niveau.", "Perfekter Flow – behalten."],
        ("mid", "low"): ["Kurz justieren – Genauigkeit vor Tempo.", "Strategie schärfen – Erklärungen nutzen."],
        ("mid", "mid"): ["Stabil in der Mitte – weiter strukturieren.", "Basis sitzt – ausbauen."],
        ("mid", "high"): ["Sehr effizient – Qualität halten.", "Starker Kern – konsistent bleiben."],
        ("mid", "elite"): ["Nahezu fehlerfrei – weiter so.", "Elite-Quote – wach bleiben."],
        ("late", "low"): ["Jetzt stabilisieren – sauber lesen.", "Konzentration kurz resetten."],
        ("late", "mid"): ["Gut dabei – Fokus durchziehen.", "Letztes Drittel kontrolliert."],
        ("late", "high"): ["Starker Score – halten.", "Qualität bleibt hoch."],
        ("late", "elite"): ["Fast makellos – Konzentration!", "Elite-Level halten."],
        ("close", "low"): ["Kurz vor dem Ziel – ruhig atmen.", "Letzte Punkte einsammeln."],
        ("close", "mid"): ["Endspurt strukturiert.", "Nicht überhasten."],
        ("close", "high"): ["Sehr starker Lauf – sauber finishen.", "Score sichern – keine Hast."],
        ("close", "elite"): ["Perfektes Finish in Sicht.", "Elite bis zum Schluss."],
        ("final", "low"): ["Geschafft – Lernpunkte notieren.", "Reflexion lohnt sich."],
        ("final", "mid"): ["Solide Runde – sichern.", "Guter Abschluss."],
        ("final", "high"): ["Sehr stark – kurz reflektieren.", "Top-Ergebnis stabil."],
        ("final", "elite"): ["Exzellent – nahezu perfekt.", "Elite-Runde!"],
    }

    # Overlays abhängig von Streak / letzter Antwort
    overlay_phrases = []
    if last_correct:
        if streak in {2, 3}: overlay_phrases.append("Flow baut sich auf.")
        elif streak == 5: overlay_phrases.append("🔥 5er Serie!")
        elif streak == 10: overlay_phrases.append("⚡ 10er Serie – stark!")
        elif streak > 10 and streak % 5 == 0: overlay_phrases.append("Konstante Treffer – beeindruckend.")
    elif last_correct is False:
        if streak == 0: overlay_phrases.append("Reset: ruhig weiterlesen.")
        if ratio >= 0.75: overlay_phrases.append("Score weiter hoch – nicht kippen lassen.")
        else: overlay_phrases.append("Fehler = Signal. Muster prüfen.")

    # Auswahl kombinieren
    pool = list(base_phrases.get((phase, tier), []))
    pool.extend(overlay_phrases)
    if not pool:
        return ""

    # Wiederholung vermeiden
    last_phrase = st.session_state.get("_last_motivation_phrase")
    
    # Wähle eine Phrase, die nicht die letzte war
    import random
    possible_phrases = [p for p in pool if p != last_phrase]
    if not possible_phrases:
        possible_phrases = pool # Fallback, wenn nur eine Option da ist

    candidate = random.choice(possible_phrases)
    st.session_state._last_motivation_phrase = candidate

    # Anzeige
    message_html = ""
    if candidate:
        message_html = f"<div style='margin-top:8px; font-size:0.9em; opacity:0.8;'>💬 {candidate}</div>"
    return message_html

def render_question_distribution_chart(questions: list):
    """Rendert ein gestapeltes Balkendiagramm der Fragenverteilung."""
    import plotly.graph_objects as go

    df_fragen = pd.DataFrame(questions)
    if df_fragen.empty:
        st.info("Keine Fragen zum Anzeigen vorhanden.")
        return

    # Standardwerte für fehlende Spalten setzen
    if "gewichtung" not in df_fragen.columns:
        df_fragen["gewichtung"] = 1
    if "thema" not in df_fragen.columns:
        df_fragen["thema"] = "Allgemein"

    def gewicht_to_schwierigkeit(gewicht):
        try:
            g = int(gewicht)
            if g >= 3:
                return "Schwer"
            elif g == 2:
                return "Mittel"
            else:
                return "Leicht"
        except (ValueError, TypeError):
            return "Leicht"

    df_fragen["Schwierigkeit"] = df_fragen["gewichtung"].apply(gewicht_to_schwierigkeit)

    pivot = df_fragen.pivot_table(
        index="thema", columns="Schwierigkeit", values="frage", aggfunc="count", fill_value=0
    )

    # Plotly-Diagramm erstellen
    fig = go.Figure()
    colors = {"Leicht": "#00c853", "Mittel": "#4b9fff", "Schwer": "#ffb300"}
    
    for difficulty in ["Leicht", "Mittel", "Schwer"]:
        if difficulty in pivot.columns:
            fig.add_trace(
                go.Bar(x=pivot.index, y=pivot[difficulty], name=difficulty, marker_color=colors[difficulty])
            )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Thema",
        yaxis_title="Anzahl der Fragen",
        legend_title="Schwierigkeit",
    )
    st.plotly_chart(fig, use_container_width=True) # plotly_chart does not support `width` yet, keeping `use_container_width`
