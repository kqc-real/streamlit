"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
import streamlit as st
import pandas as pd

from config import AppConfig, load_questions, list_question_files
from database import get_all_answer_logs, get_all_feedback, get_all_logs_for_leaderboard, delete_user_results_for_qset, DATABASE_FILE


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

    tabs = st.tabs(["🏆 Leaderboard", "📊 Analyse", "📢 Feedback", "📤 Export", "⚙️ System", "🔒 Audit-Log"])

    with tabs[0]:
        # Das Leaderboard soll alle Fragensets anzeigen, daher werden alle Logs übergeben
        render_leaderboard_tab(df_all_logs, app_config)
    with tabs[1]:
        render_analysis_tab(df_filtered_logs, questions)
    with tabs[2]:
        render_feedback_tab() # Diese Funktion holt sich ihre Daten jetzt selbst
    with tabs[3]:
        render_export_tab(df_filtered_logs, app_config)
    with tabs[4]:
        render_system_tab(app_config, df_filtered_logs)
    with tabs[5]:
        render_audit_log_tab()


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
        st.subheader(f"{title} (max. {max_score_for_set} Punkte)")

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
            'duration_seconds': 'Dauer'
        }, inplace=True)

        # Formatiere die Dauer von Sekunden in MM:SS
        def format_duration(seconds):
            mins, secs = divmod(seconds, 60)
            return f"{int(mins):02d}:{int(secs):02d}"
        scores['Dauer'] = scores['Dauer'].apply(format_duration)

        # Konvertiere die 'Datum'-Spalte in ein Datetime-Objekt, bevor sie formatiert wird.
        scores["Datum"] = pd.to_datetime(scores["Datum"])

        scores["Datum"] = scores["Datum"].dt.strftime('%d.%m.%y')
        
        icons = ["🥇", "🥈", "🥉"]
        for i in range(len(scores)):
            if i < len(icons):
                scores.loc[i, "Pseudonym"] = f"{icons[i]} {scores.loc[i, 'Pseudonym']}"
            else:
                scores.loc[i, "Pseudonym"] = f"{i + 1}. {scores.loc[i, 'Pseudonym']}"

        st.dataframe(scores[["Pseudonym", "Punkte", "Dauer", "Datum"]], use_container_width=True, hide_index=True)

        # --- Funktion zum Zurücksetzen von Benutzerergebnissen ---
        with st.expander("Benutzerergebnisse für dieses Set zurücksetzen"):
            user_to_reset = st.selectbox(
                "Wähle einen Benutzer:",
                options=[p for p in scores["Pseudonym"]],
                format_func=lambda x: x.split(" ", 1)[-1], # Zeige nur den Namen ohne Rang/Icon
                key=f"reset_user_select_{q_file}"
            )
            
            if user_to_reset:
                user_name_plain = user_to_reset.split(" ", 1)[-1]
                st.warning(f"**Achtung:** Alle Ergebnisse von **{user_name_plain}** für das Fragenset **{title}** werden unwiderruflich gelöscht.")
                
                # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
                from auth import check_admin_key
                reauth_key = st.text_input(
                    "Admin-Key zur Bestätigung:",
                    type="password",
                    key=f"delete_reauth_{q_file}",
                    help="Zur Sicherheit muss der Admin-Key erneut eingegeben werden."
                )
                
                if st.checkbox("Ja, ich bin sicher.", key=f"reset_confirm_{q_file}"):
                    if st.button("Ergebnisse jetzt löschen", type="primary", key=f"reset_btn_{q_file}"):
                        # Prüfe Admin-Key (wenn gesetzt, sonst direkter Zugriff für lokale Tests)
                        if not app_config.admin_key or check_admin_key(reauth_key, app_config):
                            if delete_user_results_for_qset(user_name_plain, q_file):
                                # --- 🔒 PHASE 3: Audit-Logging ---
                                from audit_log import log_admin_action
                                admin_user = st.session_state.get("user_id", "Unknown")
                                log_admin_action(
                                    admin_user, 
                                    "DELETE_USER_RESULTS",
                                    f"Deleted results: user={user_name_plain}, qset={q_file}",
                                    success=True
                                )
                                st.success(f"✅ Die Ergebnisse von {user_name_plain} wurden zurückgesetzt.")
                                st.rerun()
                            else:
                                st.error("❌ Fehler beim Zurücksetzen der Ergebnisse.")
                        else:
                            st.error("🔒 Falscher Admin-Key. Löschung abgebrochen.")
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
                    # Setze NaN auf 0.0 für konsistente numerische Verarbeitung
                    correlations[frage_nr] = 0.0 if pd.isna(corr) else float(corr)
            else:
                correlations[frage_nr] = 0.0  # 0.0 statt None für konsistente Typisierung

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
            "Richtig (%)": round(difficulty, 1),  # Numerischer Wert für korrektes Sortieren
        }
        if show_correlation:
            trennschaerfe = correlations.get(frage_nr)
            # Numerischer Wert statt String für korrektes Sortieren
            row["Trennschärfe (r_it)"] = round(trennschaerfe, 2) if pd.notna(trennschaerfe) else 0.0
        
        analysis_data.append(row)

    if not analysis_data:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    analysis_df = pd.DataFrame(analysis_data)
    
    # Sortiere den DataFrame nach der Frage-Nummer, um eine konsistente Anzeige zu gewährleisten.
    analysis_df = analysis_df.sort_values(by="Frage-Nr.").reset_index(drop=True)
    
    # Stelle sicher, dass numerische Spalten korrekt typisiert sind für Sortierung
    analysis_df["Frage-Nr."] = pd.to_numeric(analysis_df["Frage-Nr."], errors='coerce').fillna(0).astype(int)
    analysis_df["Antworten"] = pd.to_numeric(analysis_df["Antworten"], errors='coerce').fillna(0).astype(int)
    analysis_df["Richtig (%)"] = pd.to_numeric(analysis_df["Richtig (%)"], errors='coerce').fillna(0.0)
    if show_correlation and "Trennschärfe (r_it)" in analysis_df.columns:
        # Robuste Konvertierung: coerce wandelt ungültige Werte in NaN, dann fillna(0.0)
        analysis_df["Trennschärfe (r_it)"] = pd.to_numeric(
            analysis_df["Trennschärfe (r_it)"], errors='coerce'
        ).fillna(0.0)
    
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


def render_export_tab(df: pd.DataFrame, app_config: AppConfig = None):
    """Rendert den Export-Tab."""
    st.header("Datenexport")
    if df.empty:
        st.info("Keine Daten zum Exportieren vorhanden.")
        return

    # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung vor Export (optional) ---
    # Hinweis: Export ist lesend und weniger kritisch, aber kann sensible Daten enthalten
    st.info("💡 Der Export enthält alle Antwortdaten inklusive Nutzerpseudonymen und Zeitstempel.")
    
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

    # --- Erweiterte Dashboard-Statistiken ---
    st.subheader("📊 Dashboard-Statistiken")
    
    from database import get_dashboard_statistics
    stats = get_dashboard_statistics()
    
    if stats and stats['total_tests'] > 0:
        # Oberste Zeile: Hauptmetriken
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Abgeschlossene Tests", stats['total_tests'])
        with col2:
            st.metric("Eindeutige Teilnehmer", stats['unique_users'])
        with col3:
            st.metric("Gemeldete Probleme", stats['total_feedback'])
        with col4:
            # Formatiere Dauer in MM:SS
            mins, secs = divmod(stats['avg_duration'], 60)
            duration_str = f"{int(mins):02d}:{int(secs):02d} min"
            st.metric("Ø Testdauer", duration_str)
        
        st.divider()
        
        # Zweite Zeile: Abschlussquote
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Abschlussquote",
                f"{stats['completion_rate']}%",
                help="Prozentsatz der Tests, die vollständig beendet wurden"
            )
        
        # Durchschnittliche Punktzahlen pro Fragenset
        if stats['avg_scores_by_qset']:
            st.divider()
            st.subheader("📈 Durchschnittliche Leistung pro Fragenset")
            
            # Bereite Daten für Chart vor
            import plotly.graph_objects as go
            
            qsets = []
            avg_scores = []
            test_counts = []
            
            for qfile, data in sorted(stats['avg_scores_by_qset'].items()):
                # Extrahiere schönen Namen aus Dateiname
                qset_name = qfile.replace("questions_", "").replace(".json", "").replace("_", " ")
                qsets.append(qset_name)
                avg_scores.append(data['avg_score'])
                test_counts.append(data['test_count'])
            
            # Erstelle Bar-Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=qsets,
                    y=avg_scores,
                    text=[f"{score:.1f} Pkt<br>({count} Tests)" for score, count in zip(avg_scores, test_counts)],
                    textposition='auto',
                    marker_color='#1f77b4',
                    hovertemplate='<b>%{x}</b><br>Durchschnitt: %{y:.2f} Punkte<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="Durchschnittliche Punktzahl nach Fragenset",
                xaxis_title="Fragenset",
                yaxis_title="Durchschnittliche Punktzahl",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine abgeschlossenen Tests vorhanden. Statistiken werden nach den ersten Tests angezeigt.")

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
        
        # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
        from auth import check_admin_key
        reauth_key_global = st.text_input(
            "Admin-Key zur Bestätigung:",
            type="password",
            key="global_delete_reauth",
            help="Zur Sicherheit muss der Admin-Key erneut eingegeben werden."
        )
        
        if st.checkbox("Ich bin mir der Konsequenzen bewusst und möchte alle Daten löschen.", key="global_delete_confirm"):
            if st.button("JETZT ALLE TESTDATEN LÖSCHEN", type="primary", key="global_delete_btn"):
                # Prüfe Admin-Key (wenn gesetzt, sonst direkter Zugriff für lokale Tests)
                if not app_config.admin_key or check_admin_key(reauth_key_global, app_config):
                    from database import reset_all_test_data
                    if reset_all_test_data():
                        # --- 🔒 PHASE 3: Audit-Logging ---
                        from audit_log import log_admin_action
                        admin_user = st.session_state.get("user_id", "Unknown")
                        log_admin_action(
                            admin_user,
                            "GLOBAL_DELETE_ALL_DATA",
                            "All test data deleted (CRITICAL ACTION)",
                            success=True
                        )
                        st.success("✅ Alle Testdaten wurden zurückgesetzt.")
                        # Session-State aller Nutzer invalidieren (gute Praxis)
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("❌ Löschen fehlgeschlagen. Überprüfe die Server-Logs.")
                else:
                    st.error("🔒 Falscher Admin-Key. Globales Löschen abgebrochen.")


def render_audit_log_tab():
    """Rendert den Audit-Log-Tab mit Filterung und Export."""
    from audit_log import (
        get_audit_log, 
        export_audit_log_csv, 
        get_audit_statistics,
        cleanup_old_audit_logs
    )
    
    st.header("🔒 Audit-Log")
    st.caption("Protokollierung aller Admin-Aktionen für Sicherheit und Compliance")
    
    # --- Statistiken ---
    stats = get_audit_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gesamt-Einträge", stats["total"])
    with col2:
        st.metric("Erfolgreich", stats["successful"], 
                 delta=None if stats["total"] == 0 
                 else f"{stats['successful']/stats['total']*100:.1f}%")
    with col3:
        st.metric("Fehlgeschlagen", stats["failed"],
                 delta=None if stats["total"] == 0
                 else f"{stats['failed']/stats['total']*100:.1f}%")
    
    st.divider()
    
    # --- Filter ---
    st.subheader("Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("Anzahl Einträge", 
                               min_value=10, max_value=1000, value=100, step=10)
    
    with col2:
        # User-Filter (aus Statistik)
        user_options = ["Alle"] + [u["user_id"] for u in stats["top_users"]]
        selected_user = st.selectbox("Benutzer", user_options)
        user_filter = None if selected_user == "Alle" else selected_user
    
    with col3:
        # Action-Filter
        action_options = ["Alle"] + [a["action"] for a in stats["actions"]]
        selected_action = st.selectbox("Aktion", action_options)
        action_filter = None if selected_action == "Alle" else selected_action
    
    # Success-Filter
    success_options = {"Alle": None, "Nur Erfolgreiche": True, "Nur Fehlgeschlagene": False}
    selected_success = st.radio("Status", list(success_options.keys()), horizontal=True)
    success_filter = success_options[selected_success]
    
    st.divider()
    
    # --- Audit-Log abrufen ---
    logs = get_audit_log(
        limit=limit,
        user_id=user_filter,
        action=action_filter,
        success_only=success_filter
    )
    
    if not logs:
        st.info("📭 Keine Audit-Log-Einträge gefunden.")
        return
    
    # --- Tabelle anzeigen ---
    st.subheader(f"Audit-Log ({len(logs)} Einträge)")
    
    import pandas as pd
    df = pd.DataFrame(logs)
    
    # Formatiere Spalten
    df = df[["timestamp", "user_id", "action", "success", "details"]]
    df.columns = ["Zeitstempel", "Benutzer", "Aktion", "Erfolg", "Details"]
    
    # Success als ✅/❌
    df["Erfolg"] = df["Erfolg"].apply(lambda x: "✅" if x else "❌")
    
    # Formatiere Timestamp
    df["Zeitstempel"] = pd.to_datetime(df["Zeitstempel"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Zeige Tabelle
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # --- Export & Cleanup ---
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV-Export
        csv_data = export_audit_log_csv()
        st.download_button(
            "📥 Export als CSV",
            data=csv_data,
            file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Cleanup alte Logs
        with st.expander("🗑️ Alte Logs löschen (DSGVO)"):
            days = st.number_input("Logs älter als (Tage)", 
                                  min_value=30, max_value=365, value=90, step=30)
            if st.button("Jetzt löschen", type="secondary"):
                deleted_count = cleanup_old_audit_logs(days)
                st.success(f"✅ {deleted_count} alte Einträge gelöscht.")
                st.rerun()
    
    # --- Info-Box ---
    with st.expander("ℹ️ Über Audit-Logging"):
        st.markdown("""
        ### Was wird protokolliert?
        
        **Erfasste Events:**
        - 🔐 Admin-Login (erfolgreich/fehlgeschlagen)
        - 🗑️ Benutzer-Ergebnisse löschen
        - ⚠️ Globale Daten-Löschung
        - 📥 CSV-Export
        - 🚫 Login-Blockierungen (Rate-Limiting)
        
        **Gespeicherte Informationen:**
        - Zeitstempel (ISO 8601)
        - Benutzer-ID (Pseudonym)
        - Aktionstyp
        - Erfolgs-Status
        - Details (z.B. gelöschter User)
        - IP-Adresse (wenn verfügbar)
        
        ### Warum Audit-Logging?
        
        - ✅ **Sicherheit:** Nachvollziehbarkeit bei Incidents
        - ✅ **Compliance:** DSGVO-Audit-Trail
        - ✅ **Forensik:** Analyse von Zugriffen
        - ✅ **Transparenz:** Admin-Aktivitäten dokumentiert
        
        ### Datenschutz
        
        **Retention:** Logs werden nach 90 Tagen automatisch gelöscht.  
        **Zugriff:** Nur Admin-Benutzer können Logs einsehen.  
        **Export:** CSV-Export für externe Archivierung möglich.
        """)
