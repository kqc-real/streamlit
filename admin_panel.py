"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
import streamlit as st
import pandas as pd

from config import AppConfig
from data_manager import load_all_logs, reset_all_answers


def render_admin_panel(app_config: AppConfig, questions: list):
    """Rendert das komplette Admin-Dashboard mit Tabs."""
    st.title("🛠 Admin Dashboard")

    df_logs = load_all_logs()
    # Filtere Logs auf das aktuell ausgewählte Fragenset
    q_file = st.session_state.get("selected_questions_file")
    if q_file and "questions_file" in df_logs.columns:
        df_logs = df_logs[df_logs["questions_file"] == q_file].copy()

    tabs = st.tabs(["🏆 Leaderboard", "📊 Analyse", "📤 Export", "⚙️ System"])

    with tabs[0]:
        render_leaderboard_tab(df_logs)
    with tabs[1]:
        render_analysis_tab(df_logs, questions)
    with tabs[2]:
        render_export_tab(df_logs)
    with tabs[3]:
        render_system_tab(app_config, df_logs)


def render_leaderboard_tab(df: pd.DataFrame):
    """Rendert den Leaderboard-Tab."""
    st.header("Highscore - Alle Teilnahmen")
    if df.empty:
        st.info("Noch keine Antworten aufgezeichnet.")
        return

    # Berechne den Score pro Nutzer
    scores = (
        df.groupby("user_id_hash")
        .agg(
            Pseudonym=("user_id_plain", "first"),
            Punkte=("richtig", "sum"),
            Antworten=("frage_nr", "nunique"),
        )
        .sort_values("Punkte", ascending=False)
        .reset_index()
    )

    st.dataframe(scores[["Pseudonym", "Punkte", "Antworten"]], use_container_width=True)


def render_analysis_tab(df: pd.DataFrame, questions: list):
    """Rendert den Item-Analyse-Tab."""
    st.header("Item-Analyse")
    if df.empty:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    # Berechne Statistiken pro Frage
    analysis_data = []
    for i, frage in enumerate(questions):
        frage_nr = int(frage["frage"].split(".", 1)[0])
        frage_df = df[df["frage_nr"] == frage_nr]
        if frage_df.empty:
            continue

        total_answers = len(frage_df)
        correct_answers = frage_df[frage_df["richtig"] > 0].shape[0]
        difficulty = (correct_answers / total_answers) * 100 if total_answers > 0 else 0

        analysis_data.append({
            "Frage-Nr.": frage_nr,
            "Frage": frage["frage"].split(".", 1)[1].strip(),
            "Antworten": total_answers,
            "Richtig (%)": f"{difficulty:.1f}",
        })

    if not analysis_data:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    analysis_df = pd.DataFrame(analysis_data)
    st.dataframe(analysis_df, use_container_width=True)

    with st.expander("Glossar der Metriken"):
        st.markdown("""
        - **Antworten**: Gesamtzahl der abgegebenen Antworten für diese Frage.
        - **Richtig (%)**: Prozentsatz der korrekten Antworten (Schwierigkeitsindex `p`).
        - **Trennschärfe `r_it`** (nicht implementiert): Korrelation zwischen der Beantwortung dieser Frage und dem Gesamtergebnis im Test. Ein hoher Wert bedeutet, dass die Frage gut zwischen starken und schwachen Teilnehmern unterscheidet.
        """)


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