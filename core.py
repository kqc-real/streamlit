"""
Kernfunktionen für MC-Test App (lehrbeispielhaft extrahiert)
"""
import hashlib
import json
import os
import pandas as pd
from datetime import timedelta

def get_user_id_hash(user_id: str) -> str:
    """Berechnet einen SHA256-Hash für das Pseudonym."""
    return hashlib.sha256(user_id.encode()).hexdigest()

def _load_fragen() -> list:
    """Lädt die Fragen aus der JSON-Datei im App-Verzeichnis."""
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _duration_to_str(x):
    """Formatiert eine Zeitspanne als mm:ss."""
    if x is None or pd.isna(x):
        return ''
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"
