"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
import streamlit as st
import pandas as pd

from config import AppConfig, load_questions, list_question_files
from database import get_all_answer_logs, get_all_feedback, get_all_logs_for_leaderboard, DATABASE_FILE


def render_admin_panel(app_config: AppConfig, questions: list):
    """Rendert das komplette Admin-Dashboard mit Tabs."""
    st.title("🛠 Admin Dashboard")

    # Lade die Daten direkt aus der Datenbank
    logs = get_all_answer_logs()
    if not logs:
        df_all_logs = pd.DataFrame()
    else:
        df_all_logs = pd.DataFrame(logs)
    
    # Filtere Logs auf das aktuell ausgewählte Fragenset für Analyse, Export etc.
    q_file = st.session_state.get("selected_questions_file")
    df_filtered_logs = df_all_logs
    if q_file and "questions_file" in df_all_logs.columns:
        df_filtered_logs = df_all_logs[df_all_logs["questions_file"] == q_file].copy()

    tabs = st.tabs(["🏆 Leaderboard", "📊 Analyse", "📢 Feedback", "📤 Export", "⚙️ System"])

    with tabs[0]:
        # Das Leaderboard soll alle Fragensets anzeigen, daher werden alle Logs übergeben
        render_leaderboard_tab(df_all_logs, app_config)
    with tabs[1]:
        render_analysis_tab(df_filtered_logs, questions)
    with tabs[2]:
        render_feedback_tab() # Diese Funktion holt sich ihre Daten jetzt selbst
    with tabs[3]:
        render_export_tab(df_filtered_logs)
    with tabs[4]:
        render_system_tab(app_config, df_filtered_logs)


def render_leaderboard_tab(df_all: pd.DataFrame, app_config: AppConfig):
    """Rendert den Leaderboard-Tab."""
    st.header("🏆 Highscores nach Fragenset")

    # Hole alle einzigartigen Fragensets aus den Logs
    all_question_files = sorted(df_all["questions_file"].unique()) if not df_all.empty and "questions_file" in df_all.columns else []

    if not all_question_files:
        st.info("Noch keine Antworten aufgezeichnet.")
        return

    # Iteriere über jedes einzigartige Fragenset in den Logs
    for q_file in all_question_files:
        if not q_file:
            continue
        
        # Lade die Fragen, um die maximale Punktzahl zu ermitteln
        questions_for_set = load_questions(q_file)
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions_for_set)
        
        title = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
        st.subheader(f"Fragenset: {title} (max. {max_score_for_set} Punkte)")

        # Nutze die optimierte DB-Funktion
        leaderboard_data = get_all_logs_for_leaderboard(q_file)
        if not leaderboard_data:
            st.info("Für dieses Set liegen keine Ergebnisse vor.")
            st.divider()
            continue

        scores = pd.DataFrame(leaderboard_data)
        scores.rename(columns={
            'user_pseudonym': 'Pseudonym',
            'total_score': 'Punkte',
            'last_test_time': 'Datum',
            'duration_minutes': 'Dauer (min)'
        }, inplace=True)

        # Konvertiere die 'Datum'-Spalte in ein Datetime-Objekt, bevor sie formatiert wird.
        scores["Datum"] = pd.to_datetime(scores["Datum"])

        scores["Datum"] = scores["Datum"].dt.strftime('%d.%m.%y')
        
        icons = ["🥇", "🥈", "🥉"]
        for i in range(len(scores)):
            if i < len(icons):
                scores.loc[i, "Pseudonym"] = f"{icons[i]} {scores.loc[i, 'Pseudonym']}"
            else:
                scores.loc[i, "Pseudonym"] = f"{i + 1}. {scores.loc[i, 'Pseudonym']}"

        st.dataframe(scores[["Pseudonym", "Punkte", "Dauer (min)", "Datum"]], use_container_width=True, hide_index=True)
        st.divider()


def render_analysis_tab(df: pd.DataFrame, questions: list):
    """Rendert den Item-Analyse-Tab."""
    st.header("Item-Analyse")
    if df.empty:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    # --- Erweiterte Analyse (Trennschärfe) nur bei >1 Teilnehmer ---
    show_correlation = df['user_id_hash'].nunique() >= 2
    correlations = {}
    if show_correlation:
        # --- Berechnung der Trennschärfe (r_it) ---
        user_scores = df.groupby('user_id_hash')['richtig'].sum()
        df['correct'] = (df['richtig'] > 0).astype(int)
        pivot_df = df.pivot_table(index='user_id_hash', columns='frage_nr', values='correct')

        for frage_nr in pivot_df.columns:
            valid_users = pivot_df[frage_nr].dropna().index
            if len(valid_users) > 1:
                item_responses = pivot_df.loc[valid_users, frage_nr]
                total_scores = user_scores.loc[valid_users]

                # Prüfe auf Standardabweichung von Null, um Division-by-Zero-Warnung zu vermeiden
                if item_responses.std() == 0 or total_scores.std() == 0:
                    correlations[frage_nr] = 0.0
                else:
                    # Berechne die Korrelation nur, wenn die Daten variieren
                    corr = item_responses.corr(total_scores)
                    correlations[frage_nr] = corr
            else:
                correlations[frage_nr] = None

    # --- Statistiken pro Frage sammeln ---
    analysis_data = []
    for i, frage in enumerate(questions):
        frage_nr = int(frage["frage"].split(".", 1)[0])
        frage_df = df[df["frage_nr"] == frage_nr]
        if frage_df.empty:
            continue

        total_answers = len(frage_df)
        correct_answers = frage_df[frage_df["richtig"] > 0].shape[0]
        difficulty = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
        
        row = {
            "Frage-Nr.": frage_nr,
            "Frage": frage["frage"].split(".", 1)[1].strip(),
            "Antworten": total_answers,
            "Richtig (%)": f"{difficulty:.1f}",
        }
        if show_correlation:
            trennschaerfe = correlations.get(frage_nr)
            row["Trennschärfe (r_it)"] = f"{trennschaerfe:.2f}" if pd.notna(trennschaerfe) else "0.00"
        
        analysis_data.append(row)

    if not analysis_data:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    analysis_df = pd.DataFrame(analysis_data)
    
    # Sortiere den DataFrame nach der Frage-Nummer, um eine konsistente Anzeige zu gewährleisten.
    analysis_df = analysis_df.sort_values(by="Frage-Nr.").reset_index(drop=True)
    
    st.dataframe(analysis_df, use_container_width=True, hide_index=True)

    with st.expander("Glossar der Metriken"):
        st.markdown("""
        - **Antworten**: Gesamtzahl der abgegebenen Antworten für diese Frage.
        - **Richtig (%)**: Prozentsatz der korrekten Antworten (Schwierigkeitsindex `p`). Ein Wert nahe 100% bedeutet eine leichte Frage, ein Wert nahe 0% eine schwere Frage.
        """)
        if show_correlation:
            st.markdown("""
            - **Trennschärfe (r_it)**: Korrelation zwischen der korrekten Beantwortung dieser Frage und dem Gesamtergebnis im Test.
                - `r_it > 0.3`: Die Frage trennt gut zwischen starken und schwachen Teilnehmern.
                - `0.1 < r_it < 0.3`: Die Frage trennt noch akzeptabel.
                - `r_it < 0.1`: Die Frage trennt schlecht. Möglicherweise ist sie missverständlich, zu einfach/schwer oder hat einen Fehler in der Antwort.
            """)
        else:
            st.info("Für die Berechnung der Trennschärfe sind mindestens 2 Teilnehmer erforderlich.")

    # --- Distraktor-Analyse ---
    st.divider()
    st.header("Detail-Analyse: Distraktoren")

    question_titles = [q["frage"] for q in questions]
    selected_question_title = st.selectbox(
        "Wähle eine Frage für die Detail-Analyse:",
        options=question_titles,
        index=0
    )

    if selected_question_title:
        selected_question = next((q for q in questions if q["frage"] == selected_question_title), None)
        if selected_question:
            frage_nr = int(selected_question["frage"].split(".", 1)[0])
            frage_df = df[df["frage_nr"] == frage_nr]

            if frage_df.empty:
                st.info("Für diese Frage liegen noch keine Antworten vor.")
            else:
                answer_counts = frage_df["antwort"].value_counts().reset_index()
                answer_counts.columns = ["Antwort", "Anzahl"]

                all_options = pd.DataFrame({"Antwort": selected_question["optionen"]})
                merged_df = pd.merge(all_options, answer_counts, on="Antwort", how="left").fillna(0)
                merged_df["Anzahl"] = merged_df["Anzahl"].astype(int)

                correct_answer = selected_question["optionen"][selected_question["loesung"]]
                merged_df["Korrekt"] = merged_df["Antwort"].apply(lambda x: "✅" if x == correct_answer else "")

                st.write("Antwortverteilung:")
                st.dataframe(merged_df[["Antwort", "Anzahl", "Korrekt"]].sort_values("Anzahl", ascending=False), use_container_width=True)

                if st.checkbox("Zeige als Balkendiagramm", key=f"distractor_chart_{frage_nr}"):
                    import plotly.express as px
                    fig = px.bar(
                        merged_df,
                        x="Anzahl",
                        y="Antwort",
                        orientation='h',
                        title="Antwortverteilung",
                        color="Korrekt",
                        color_discrete_map={"": "grey", "✅": "green"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

def render_feedback_tab():
    """Rendert den Feedback-Tab."""
    st.header("Gemeldete Probleme")
    
    feedback_data = get_all_feedback()
    if not feedback_data:
        st.info("Bisher wurden keine Probleme gemeldet.")
        return

    df_all_feedback = pd.DataFrame(feedback_data)
    df_all_feedback.rename(columns={
        'timestamp': 'Gemeldet am',
        'question_nr': 'Frage-Nr.',
        'feedback_type': 'Problem-Typ',
        'questions_file': 'Fragenset',
        'user_pseudonym': 'Gemeldet von'
    }, inplace=True)

    # Ersetze den technischen Standardwert durch einen verständlicheren Text für die Anzeige.
    df_all_feedback['Problem-Typ'] = df_all_feedback['Problem-Typ'].replace(
        'Unbekannt', 'Veraltet (ohne Typ)'
    )

    # --- Filter für das Feedback ---
    st.write("Filtere die Meldungen:")
    
    # Erstelle eine Hilfsfunktion und ein Mapping für saubere Namen
    def format_q_filename(filename):
        return filename.replace("questions_", "").replace(".json", "").replace("_", " ")

    unique_files = sorted(df_all_feedback['Fragenset'].unique())
    file_display_map = {format_q_filename(f): f for f in unique_files}
    
    col1, col2 = st.columns(2)
    with col1:
        display_name = st.selectbox("Fragenset:", options=["Alle"] + list(file_display_map.keys()), key="feedback_qfile_filter")
        selected_q_file = file_display_map.get(display_name) if display_name != "Alle" else "Alle"
    with col2:
        selected_f_type = st.selectbox("Problem-Typ:", options=["Alle"] + sorted(df_all_feedback['Problem-Typ'].unique()), key="feedback_type_filter")

    df_feedback = df_all_feedback.copy()
    if selected_q_file != "Alle":
        df_feedback = df_feedback[df_feedback['Fragenset'] == selected_q_file]
    if selected_f_type != "Alle":
        df_feedback = df_feedback[df_feedback['Problem-Typ'] == selected_f_type]

    # --- Gefahrenzone: Alle sichtbaren Feedbacks löschen ---
    if not df_feedback.empty:
        with st.expander("🔴 Gefahrenzone: Mehrere Meldungen löschen"):
            st.warning(
                f"**Achtung:** Diese Aktion löscht die **{len(df_feedback)}** aktuell sichtbaren Feedback-Meldungen unwiderruflich."
            )
            if st.checkbox("Ich bin mir der Konsequenzen bewusst.", key="confirm_delete_all_feedback"):
                if st.button(f"Ja, {len(df_feedback)} Meldungen endgültig löschen", type="primary"):
                    from database import delete_multiple_feedback
                    ids_to_delete = df_feedback['feedback_id'].tolist()
                    if delete_multiple_feedback(ids_to_delete):
                        st.success(f"{len(ids_to_delete)} Feedback-Meldungen wurden gelöscht.")
                        st.rerun()
                    else:
                        st.error("Fehler beim Löschen der Meldungen.")
    st.divider()

    # Lade alle Fragen, um den Fragentext zuzuordnen
    all_questions = {}
    unique_files = df_feedback['Fragenset'].unique()
    for q_file in unique_files:
        questions = load_questions(q_file, silent=True)
        for q in questions:
            q_nr = int(q['frage'].split('.', 1)[0])
            all_questions[(q_file, q_nr)] = q['frage'].split('.', 1)[1].strip()

    df_feedback['Frage'] = df_feedback.apply(lambda row: all_questions.get((row['Fragenset'], row['Frage-Nr.']), "Frage nicht gefunden"), axis=1)
    df_feedback['Gemeldet am'] = pd.to_datetime(df_feedback['Gemeldet am']).dt.strftime('%d.%m.%Y %H:%M')

    # Ersetze das starre Dataframe durch eine interaktive Liste mit Buttons
    for _, row in df_feedback.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Frage {row['Frage-Nr.']}:** {row['Frage']}")
                st.caption(f"**Typ:** {row['Problem-Typ']} | **Set:** {format_q_filename(row['Fragenset'])} | **Von:** {row['Gemeldet von']} | {row['Gemeldet am']}")
            
            with col2:
                # Button, um direkt zur Frage zu springen
                if st.button("Zur Frage", key=f"jump_feedback_{row.name}", use_container_width=True):
                    # Finde den Index der Frage im entsprechenden Fragenset
                    q_file_to_load = row['Fragenset']
                    questions_to_load = load_questions(q_file_to_load, silent=True)
                    target_idx = next((i for i, q in enumerate(questions_to_load) if int(q['frage'].split('.', 1)[0]) == row['Frage-Nr.']), None)

                    if target_idx is not None:
                        st.session_state.selected_questions_file = q_file_to_load
                        st.session_state.jump_to_idx = target_idx
                        st.session_state.jump_to_idx_active = True
                        st.session_state.show_admin_panel = False
                        st.rerun()
                    else:
                        st.error("Frage konnte im Set nicht gefunden werden.")
                
                # Popover für die Löschbestätigung
                with st.popover("Löschen", use_container_width=True):
                    st.warning("Soll dieses Feedback wirklich gelöscht werden?")
                    if st.button("Ja, endgültig löschen", key=f"del_feedback_{row['feedback_id']}", type="primary", use_container_width=True):
                        from database import delete_feedback
                        if delete_feedback(row['feedback_id']):
                            st.toast("Feedback gelöscht.")
                            st.rerun()
                        else:
                            st.error("Fehler beim Löschen.")


def render_export_tab(df: pd.DataFrame):
    """Rendert den Export-Tab."""
    st.header("Datenexport")
    if df.empty:
        st.info("Keine Daten zum Exportieren vorhanden.")
        return

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Antwort-Log herunterladen (CSV)",
        data=csv_data,
        file_name="mc_test_answers.csv",
        mime="text/csv",
    )


def render_system_tab(app_config: AppConfig, df: pd.DataFrame):
    """Rendert den System-Tab für Konfiguration und Statistiken."""
    st.header("Systemeinstellungen und Metriken")

    # --- Scoring-Modus ---
    st.subheader("Scoring-Modus")
    new_mode = st.radio(
        "Wie sollen falsche Antworten bewertet werden?",
        options=["positive_only", "negative"],
        index=0 if app_config.scoring_mode == "positive_only" else 1,
        format_func=lambda v: "Nur Pluspunkte (falsch = 0)"
        if v == "positive_only"
        else "Plus-Minus-Punkte (falsch = -Gewichtung)",
        horizontal=True,
    )
    if new_mode != app_config.scoring_mode:
        app_config.scoring_mode = new_mode
        app_config.save()
        st.success("Scoring-Modus gespeichert. Wird bei der nächsten Antwort aktiv.")
        st.rerun()

    st.divider()

    # --- System-Metriken ---
    st.subheader("Metriken")
    if not df.empty:
        total_answers = len(df)
        unique_users = df["user_id_hash"].nunique()
        st.metric("Gesamtzahl der Antworten", total_answers)
        st.metric("Eindeutige Teilnehmer", unique_users)
    else:
        st.info("Noch keine Metriken verfügbar.")

    st.divider()

    # --- Datenbank-Management ---
    st.subheader("Datenbank-Management")
    st.info("Lade einen kompletten SQL-Dump der Datenbank herunter. Diese Textdatei enthält die Struktur (Schema) und alle Inhalte und kann in jedem Texteditor oder SQLite-Tool geöffnet werden.")
    
    # Importiere die Funktion hier, um zyklische Importe zu vermeiden
    from database import get_database_dump
    
    db_dump_data = get_database_dump()
    st.download_button(
        label="Datenbank-Dump herunterladen (.sql)",
        data=db_dump_data,
        file_name="mc_test_dump.sql",
        mime="application/sql"
    )
    st.divider()

    # --- Globaler Reset ---
    st.subheader("Gefahrenzone")
    with st.expander("🔴 Alle Testdaten unwiderruflich löschen"):
        st.warning(
            "**Achtung:** Diese Aktion löscht alle aufgezeichneten Antworten, Sessions und Benutzer "
            "(außer dem Admin-Account) aus der Datenbank."
        )
        if st.checkbox("Ich bin mir der Konsequenzen bewusst und möchte alle Daten löschen."):
            if st.button("JETZT ALLE TESTDATEN LÖSCHEN", type="primary"):
                from database import reset_all_test_data
                if reset_all_test_data():
                    st.success("Alle Testdaten wurden zurückgesetzt.")
                    # Session-State aller Nutzer invalidieren (gute Praxis)
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Löschen fehlgeschlagen. Überprüfe die Server-Logs.")