"""Leaderboard und Admin-Logik ausgelagert aus mc_test_app.py.

Diese Funktionen kapseln das Laden des Logs sowie die Berechnung der
Bestenlisten. Sie greifen – wenn verfügbar – auf das scoring-Modul zurück,
um die bereits vorhandene Logik wiederzuverwenden. Die Implementierung ist
so gestaltet, dass keine harten Zirkular-Abhängigkeiten entstehen.
"""
from __future__ import annotations
import os
from datetime import datetime
import pandas as pd
import streamlit as st


# Robust import for scoring module (absolute first, then relative, then local)
try:
    import mc_test_app.scoring as _scoring
except Exception:
    try:
        from . import scoring as _scoring  # type: ignore
    except Exception:
        try:
            import scoring as _scoring
        except Exception:
            _scoring = None  # type: ignore

# Standard-Logfile-Pfad (identisch zu mc_test_app.LOGFILE)
from ._paths import get_package_dir

LOGFILE = os.path.join(get_package_dir(), "mc_test_answers.csv")
FIELDNAMES = [
    "user_id_hash",
    "user_id_display",
    "user_id_plain",
    "frage_nr",
    "frage",
    "antwort",
    "richtig",
    "zeit",
    "questions_file",
]


def _duration_to_str(x):
    if pd.isna(x):
        return ""
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def _get_total_questions() -> int:
    """Lädt einmalig questions.json um die Gesamtzahl zu ermitteln.
    Fallback, falls FRAGEN_ANZAHL nicht aus Hauptmodul gelesen werden kann.
    """
    path = os.path.join(get_package_dir(), "questions.json")
    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return len(data)
    except Exception:  # pragma: no cover
        pass
    return 0


def _get_total_questions_prefer_main() -> int:
    # Immer die Fragenanzahl für das aktuell gewählte Fragenset bestimmen
    try:
        import streamlit as st
        sel = st.session_state.get("selected_questions_file", None)
        if sel:
            import os
            import json
            from ._paths import get_package_dir
            path = os.path.join(get_package_dir(), sel)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return len(data)
    except Exception:
        pass
    return _get_total_questions()


def load_all_logs() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        missing = [c for c in FIELDNAMES if c not in df.columns]
        for c in missing:
            df[c] = ""
        df = df[[c for c in FIELDNAMES if c in df.columns]]
        df["zeit"] = pd.to_datetime(df["zeit"], errors="coerce")
        df["richtig"] = pd.to_numeric(df["richtig"], errors="coerce")
        df["frage_nr"] = pd.to_numeric(df["frage_nr"], errors="coerce")
        df = df.dropna(
            subset=[
                "user_id_hash",
                "user_id_display",
                "frage_nr",
                "frage",
                "antwort",
                "richtig",
                "zeit",
            ]
        )
        df = df[df["richtig"].isin([-1, 0, 1])]
        for col in ["user_id_hash", "frage", "antwort"]:
            df = df[df[col].astype(str).str.strip() != ""]
        try:
            df["frage_nr"] = df["frage_nr"].astype(int)
        except Exception:
            pass
        return df
    except Exception:  # pragma: no cover
        return pd.DataFrame(columns=FIELDNAMES)


def calculate_leaderboard_all(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    try:
        tmp = df.copy()
        tmp["richtig"] = pd.to_numeric(tmp["richtig"], errors="coerce")
        tmp["zeit"] = pd.to_datetime(tmp["zeit"], errors="coerce")
        agg_df = (
            tmp.groupby("user_id_hash")
            .agg(
                Punkte=("richtig", "sum"),
                Antworten=("frage_nr", "count"),
                Start=("zeit", "min"),
                Ende=("zeit", "max"),
                Pseudonym=("user_id_plain", "first"),
            )
            .reset_index(drop=True)
        )
        agg_df["Dauer"] = agg_df["Ende"] - agg_df["Start"]
        agg_df = agg_df.sort_values(by=["Punkte", "Dauer"], ascending=[False, True])
        agg_df["Zeit"] = agg_df["Dauer"].apply(_duration_to_str)
        return agg_df[["Pseudonym", "Punkte", "Antworten", "Zeit", "Start", "Ende"]]
    except Exception:  # pragma: no cover
        return pd.DataFrame()


def calculate_leaderboard() -> pd.DataFrame:
    """Kompatible Wrapper-Funktion für die Top-5-Leaderboard Anzeige.

    Berücksichtigt den Spezialfall weniger Fragen analog zur Original-Implementierung.
    """
    total_q = _get_total_questions_prefer_main()
    if _scoring is None:
        return pd.DataFrame()
    if total_q <= 1:  # Spezialfall leichte Inline-Auswertung
        lf = LOGFILE
        if not (os.path.isfile(lf) and os.path.getsize(lf) > 0):
            return pd.DataFrame()
        try:
            # Load logs via helper so missing columns are normalized
            df = load_all_logs()
            # Filter by selected question-file/pool when present
            sel = None
            try:
                sel = st.session_state.get("selected_questions_file")
            except Exception:
                sel = None
            if "questions_file" in df.columns and sel:
                df = df[df.get("questions_file") == sel]
            if df.empty:
                return pd.DataFrame()
            df["richtig"] = pd.to_numeric(df["richtig"], errors="coerce")
            agg = (
                df.groupby("user_id_hash")
                .agg(Punkte=("richtig", "sum"), Pseudonym=("user_id_plain", "first"))
                .reset_index(drop=True)
            )
            agg = agg.sort_values(by=["Punkte"], ascending=[False]).head(5)
            agg.insert(0, "Platz", range(1, len(agg) + 1))
            return agg[["Platz", "Pseudonym", "Punkte"]]
        except Exception:  # pragma: no cover
            return pd.DataFrame()
    return _scoring.leaderboard_completed(total_q)  # type: ignore

# clear Cache Proxy (optional – falls scoring dies unterstützt)
try:  # pragma: no cover
    calculate_leaderboard.clear = _scoring.leaderboard_completed.clear  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    def _noop():
        return None
    calculate_leaderboard.clear = _noop  # type: ignore[attr-defined]


def admin_view():
    """Originale Admin-Leaderboard-Ansicht (Tabs) extrahiert."""
    st.title("🏆 Management: Bestenliste & Logs")
    df_logs = load_all_logs()
    # Apply selected question-file/pool filter so admin views are pool-specific
    try:
        sel = st.session_state.get("selected_questions_file")
    except Exception:
        sel = None
    if "questions_file" in df_logs.columns and sel:
        df_logs = df_logs[df_logs.get("questions_file") == sel]
    if df_logs.empty:
        st.info("Noch keine Daten am Start.")
        return
    tabs = st.tabs(["🥇 Top 5 (fertig)", "👥 Alle Teilnahmen", "📄 Rohdaten"])
    with tabs[0]:
        top_df = calculate_leaderboard()
        if top_df.empty:
            import pandas as _pd
            placeholder = _pd.DataFrame([
                {"Platz": "", "Pseudonym": "", "Punkte": ""}
            ])
            st.dataframe(placeholder, width='stretch', hide_index=True)
        else:
            # Rang-Icons ergänzen
            icons = {1: "🥇", 2: "🥈", 3: "🥉"}
            df_show = top_df.copy()
            if "Platz" in df_show.columns:
                df_show.insert(0, "Rang", df_show["Platz"].map(icons).fillna(df_show["Platz"].astype(str)))
            st.dataframe(df_show[[c for c in ["Rang", "Platz", "Pseudonym", "Punkte"] if c in df_show.columns]], width='stretch', hide_index=True)
            if "questions_file" not in top_df.columns:
                try:
                    top_df["questions_file"] = st.session_state.get("selected_questions_file", "")
                except Exception:
                    top_df["questions_file"] = ""
            csv_bytes = top_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "🥇 Top 5 als CSV runterladen",
                csv_bytes,
                file_name="leaderboard_top5.csv",
                mime="text/csv",
            )
    with tabs[1]:
        all_df = calculate_leaderboard_all(df_logs)
        if all_df.empty:
            st.info("Noch keine Einträge. Mach du den Anfang!")
        else:
            st.dataframe(all_df, width='stretch', hide_index=True)
            if "questions_file" not in all_df.columns:
                try:
                    all_df["questions_file"] = st.session_state.get("selected_questions_file", "")
                except Exception:
                    all_df["questions_file"] = ""
            csv_bytes = all_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "👥 Alle Teilnahmen als CSV runterladen",
                csv_bytes,
                file_name="leaderboard_all.csv",
                mime="text/csv",
            )
    with tabs[2]:
        show_cols = [
            "user_id_plain",
            "user_id_display",
            "user_id_hash",
            "frage_nr",
            "antwort",
            "richtig",
            "zeit",
        ]
        df_show = df_logs.copy()
        missing = [c for c in show_cols if c not in df_show.columns]
        for c in missing:
            df_show[c] = ""
        df_show = df_show[show_cols].sort_values("zeit", ascending=True)
        st.dataframe(df_show, width='stretch', height=400, hide_index=True)
        if "questions_file" not in df_logs.columns:
            try:
                df_logs["questions_file"] = st.session_state.get("selected_questions_file", "")
            except Exception:
                df_logs["questions_file"] = ""
        csv_bytes = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📄 Rohdaten als CSV runterladen",
            csv_bytes,
            file_name="mc_test_raw_logs.csv",
            mime="text/csv",
        )
