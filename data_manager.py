"""
Modul für das Datenmanagement.

Verantwortlichkeiten:
- Lesen und Schreiben der `mc_test_answers.csv`.
- Kapselt alle CSV-Operationen, um Race Conditions zu minimieren und
  die Logik zu zentralisieren.
"""
import os
import csv
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import streamlit as st

from mc_test_app.config import get_package_dir

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
    "markiert",
    "questions_file",
]


def ensure_logfile_exists():
    """Stellt sicher, dass die Log-Datei mit Header existiert."""
    if not os.path.isfile(LOGFILE) or os.path.getsize(LOGFILE) == 0:
        with open(LOGFILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def append_answer_row(row: Dict[str, Any]):
    """Hängt eine einzelne Antwortzeile an die CSV-Datei an."""
    ensure_logfile_exists()
    filtered_row = {k: row.get(k, "") for k in FIELDNAMES}
    with open(LOGFILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(filtered_row)


@st.cache_data(ttl=30)  # Cache für 30 Sekunden, um DB-Hits zu reduzieren
def load_all_logs() -> pd.DataFrame:
    """Lädt alle Antworten aus der CSV-Datei in einen DataFrame."""
    ensure_logfile_exists()
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        # Stelle sicher, dass alle erwarteten Spalten existieren
        for col in FIELDNAMES:
            if col not in df.columns:
                df[col] = None
        return df[FIELDNAMES]  # Korrekte Spaltenreihenfolge
    except (IOError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=FIELDNAMES)


def save_all_logs(df: pd.DataFrame):
    """Speichert den kompletten DataFrame zurück in die CSV-Datei."""
    try:
        df.to_csv(LOGFILE, index=False, columns=FIELDNAMES)
        # Cache leeren, damit der nächste Ladevorgang die neuen Daten holt
        load_all_logs.clear()
    except IOError as e:
        st.error(f"Speichern der Antworten fehlgeschlagen: {e}")


def save_answer(
    user_id_hash: str,
    user_id_plain: str,
    frage_obj: dict,
    antwort: str,
    punkte: int,
    is_bookmarked: bool,
    questions_file: str,
):
    """Speichert eine einzelne Antwort sicher."""
    frage_nr_str = frage_obj.get("frage", "").split(".", 1)[0]
    try:
        frage_nr = int(frage_nr_str)
    except (ValueError, IndexError):
        st.error(f"Konnte Frage-Nummer nicht aus '{frage_nr_str}' extrahieren.")
        return

    row = {
        "user_id_hash": user_id_hash,
        "user_id_display": user_id_hash[:10],
        "user_id_plain": user_id_plain,
        "frage_nr": frage_nr,
        "frage": frage_obj["frage"],
        "antwort": antwort,
        "richtig": punkte,
        "zeit": datetime.now().isoformat(timespec="seconds"),
        "markiert": is_bookmarked,
        "questions_file": questions_file,
    }
    append_answer_row(row)
    # Cache leeren, damit Admin-Panel und Leaderboard aktuell sind
    load_all_logs.clear()


def reset_all_answers():
    """Löscht den Inhalt der Log-Datei und schreibt nur den Header."""
    try:
        with open(LOGFILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        load_all_logs.clear()
        return True
    except IOError:
        return False


def update_bookmarks_for_user(user_id_hash: str, bookmarked_indices: list, questions: list):
    """Aktualisiert den Bookmark-Status für einen Nutzer in der CSV."""
    df = load_all_logs()
    if df.empty:
        return

    bookmarked_question_nrs = {
        int(questions[i]["frage"].split(".", 1)[0]) for i in bookmarked_indices
    }

    user_mask = df["user_id_hash"] == user_id_hash
    df.loc[user_mask, "markiert"] = df.loc[user_mask, "frage_nr"].isin(
        bookmarked_question_nrs
    )

    # Füge Platzhalter für unbeantwortete, aber gebookmarkte Fragen hinzu
    existing_nrs = set(df.loc[user_mask, "frage_nr"].dropna().astype(int))
    new_rows = []
    for idx in bookmarked_indices:
        frage_nr = int(questions[idx]["frage"].split(".", 1)[0])
        if frage_nr not in existing_nrs:
            new_rows.append({
                "user_id_hash": user_id_hash,
                "user_id_display": user_id_hash[:10],
                "user_id_plain": st.session_state.get("user_id", ""),
                "frage_nr": frage_nr,
                "frage": questions[idx]["frage"],
                "antwort": "__bookmark__",
                "richtig": 0,
                "zeit": datetime.now().isoformat(timespec="seconds"),
                "markiert": True,
                "questions_file": st.session_state.get("selected_questions_file", ""),
            })

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    # Entferne alte Platzhalter, die nicht mehr gebookmarkt sind
    placeholder_mask = user_mask & (df["antwort"] == "__bookmark__")
    unbookmarked_placeholder_mask = placeholder_mask & ~df["frage_nr"].isin(
        bookmarked_question_nrs
    )
    df = df[~unbookmarked_placeholder_mask]

    save_all_logs(df)