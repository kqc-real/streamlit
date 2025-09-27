"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
import streamlit as st
import pandas as pd

from config import AppConfig, load_questions, list_question_files
from data_manager import load_all_logs, reset_all_answers


def render_admin_panel(app_config: AppConfig, questions: list):
    """Rendert das komplette Admin-Dashboard mit Tabs."""
    st.title("🛠 Admin Dashboard")

    df_all_logs = load_all_logs()
    
    # Filtere Logs auf das aktuell ausgewählte Fragenset für Analyse, Export etc.
    q_file = st.session_state.get("selected_questions_file")
    df_filtered_logs = df_all_logs
    if q_file and "questions_file" in df_all_logs.columns:
        df_filtered_logs = df_all_logs[df_all_logs["questions_file"] == q_file].copy()

    tabs = st.tabs(["🏆 Leaderboard", "📊 Analyse", "📤 Export", "⚙️ System"])

    with tabs[0]:
        # Das Leaderboard soll alle Fragensets anzeigen, daher werden alle Logs übergeben.
        render_leaderboard_tab(df_all_logs)
    with tabs[1]:
        render_analysis_tab(df_filtered_logs, questions)
    with tabs[2]:
        render_export_tab(df_filtered_logs)
    with tabs[3]:
        render_system_tab(app_config, df_filtered_logs)


def render_leaderboard_tab(df_all: pd.DataFrame):
    """Rendert den Leaderboard-Tab."""
    st.header("Highscores nach Fragenset")
    if df_all.empty or "questions_file" not in df_all.columns:
        st.info("Noch keine Antworten aufgezeichnet.")
        return

    # Iteriere über jedes einzigartige Fragenset in den Logs
    for q_file in sorted(df_all["questions_file"].unique()):
        if not q_file:
            continue
        
        title = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
        st.subheader(f"Fragenset: {title}")

        df_set = df_all[df_all["questions_file"] == q_file].copy()
        
        if 'zeit' in df_set.columns:
            df_set['zeit'] = pd.to_datetime(df_set['zeit'], errors='coerce')

        scores = (
            df_set.groupby("user_id_hash")
            .agg(
                Pseudonym=("user_id_plain", "first"),
                Punkte=("richtig", "sum"),
                Datum=("zeit", "max"),
            )
            .sort_values("Punkte", ascending=False)
            .reset_index()
        )

        # Ersetze den Admin-Benutzernamen durch das Pseudonym "Alan C. Kay"
        # Lade die AppConfig, um den Admin-Benutzernamen zu erhalten
        app_config_for_admin_name = AppConfig()
        if app_config_for_admin_name.admin_user:
            admin_mask = scores["Pseudonym"].str.lower() == app_config_for_admin_name.admin_user.lower()
            scores.loc[admin_mask, "Pseudonym"] = "Alan C. Kay"

        # Lade die Fragen, um die maximale Punktzahl zu ermitteln
        questions_for_set = load_questions(q_file)
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions_for_set)
        scores["Max. Punkte"] = max_score_for_set

        scores["Datum"] = scores["Datum"].dt.strftime('%d.%m.%Y')

        icons = ["🥇", "🥈", "🥉"]
        for i in range(len(scores)):
            if i < len(icons):
                scores.loc[i, "Pseudonym"] = f"{icons[i]} {scores.loc[i, 'Pseudonym']}"
            else:
                scores.loc[i, "Pseudonym"] = f"{i + 1}. {scores.loc[i, 'Pseudonym']}"

        st.dataframe(scores[["Pseudonym", "Punkte", "Max. Punkte", "Datum"]], use_container_width=True, hide_index=True)
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

    # --- Globaler Reset ---
    st.subheader("Gefahrenzone")
    with st.expander("🔴 Alle Antworten unwiderruflich löschen"):
        st.warning(
            "**Achtung:** Diese Aktion löscht die gesamte `mc_test_answers.csv`-Datei. "
            "Alle Fortschritte aller Nutzer gehen verloren."
        )
        if st.checkbox("Ich bin mir der Konsequenzen bewusst."):
            if st.button("JETZT ALLE DATEN LÖSCHEN", type="primary"):
                if reset_all_answers():
                    st.success("Alle Antworten wurden gelöscht.")
                    # Session-State aller Nutzer invalidieren
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Löschen fehlgeschlagen. Überprüfe die Dateiberechtigungen.")