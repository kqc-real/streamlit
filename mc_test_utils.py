"""Testable utility functions from mc_test_app.py (no Streamlit dependency)."""
import os
import csv
import json
import random
import hashlib
from datetime import datetime
from typing import List, Dict
import pandas as pd

LOGFILE = os.path.join(os.path.dirname(__file__), "mc_test_answers.csv")
FIELDNAMES = [
    'user_id_hash', 'user_id_display', 'frage_nr', 'frage',
    'antwort', 'richtig', 'zeit'
]
DISPLAY_HASH_LEN = 10
MAX_SAVE_RETRIES = 3


def get_user_id_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()


def _load_fragen() -> List[Dict]:
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

fragen = _load_fragen()
FRAGEN_ANZAHL = len(fragen) or 50


def reset_user_answers(user_id_hash: str) -> None:
    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
        df = pd.read_csv(LOGFILE, dtype={'user_id_hash': str})
        df = df[df['user_id_hash'] != user_id_hash]
        df.to_csv(LOGFILE, index=False, columns=FIELDNAMES)


def user_has_progress(user_id_hash: str) -> bool:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return False
    df = pd.read_csv(LOGFILE, dtype={'user_id_hash': str}, on_bad_lines='skip')
    return not df[df['user_id_hash'] == user_id_hash].empty


def save_answer(user_id: str, user_id_hash: str, frage_obj: dict, antwort: str, punkte: int) -> None:
    frage_nr = int(frage_obj['frage'].split('.')[0])
    user_id_display = user_id_hash[:DISPLAY_HASH_LEN]
    row = {
        'user_id_hash': user_id_hash,
        'user_id_display': user_id_display,
        'frage_nr': frage_nr,
        'frage': frage_obj['frage'],
        'antwort': antwort,
        'richtig': punkte,
        'zeit': datetime.now().isoformat(timespec='seconds'),
    }
    attempt = 0
    while attempt < MAX_SAVE_RETRIES:
        try:
            file_exists_and_not_empty = (
                os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0
            )
            with open(LOGFILE, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                if not file_exists_and_not_empty:
                    writer.writeheader()
                writer.writerow(row)
            return
        except IOError:
            attempt += 1
            if attempt >= MAX_SAVE_RETRIES:
                raise
            else:
                import time
                time.sleep(0.1 * attempt)


def load_all_logs() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    df = pd.read_csv(LOGFILE, on_bad_lines='skip')
    missing = [c for c in FIELDNAMES if c not in df.columns]
    for c in missing:
        df[c] = ''
    df = df[[c for c in FIELDNAMES if c in df.columns]]
    df['zeit'] = pd.to_datetime(df['zeit'], errors='coerce')
    df['richtig'] = pd.to_numeric(df['richtig'], errors='coerce')
    df['frage_nr'] = pd.to_numeric(df['frage_nr'], errors='coerce')
    df = df.dropna(subset=['user_id_hash', 'user_id_display', 'frage_nr', 'frage', 'antwort', 'richtig', 'zeit'])
    df = df[df['richtig'].isin([-1, 0, 1])]
    for col in ['user_id_hash', 'frage', 'antwort']:
        df = df[df[col].astype(str).str.strip() != '']
    try:
        df['frage_nr'] = df['frage_nr'].astype(int)
    except Exception:
        pass
    return df


def _duration_to_str(x):
    if pd.isna(x):
        return ''
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def calculate_leaderboard_all(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp['richtig'] = pd.to_numeric(tmp['richtig'], errors='coerce')
    tmp['zeit'] = pd.to_datetime(tmp['zeit'], errors='coerce')
    agg_df = tmp.groupby('user_id_hash').agg(
        Punkte=('richtig', 'sum'),
        Antworten=('frage_nr', 'count'),
        Start=('zeit', 'min'),
        Ende=('zeit', 'max'),
        Name=('user_id_display', 'first'),
    ).reset_index(drop=True)
    agg_df['Dauer'] = agg_df['Ende'] - agg_df['Start']
    agg_df = agg_df.sort_values(by=['Punkte', 'Dauer'], ascending=[False, True])
    agg_df['Zeit'] = agg_df['Dauer'].apply(_duration_to_str)
    return agg_df[['Name', 'Punkte', 'Antworten', 'Zeit', 'Start', 'Ende']]
