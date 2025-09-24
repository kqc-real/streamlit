import os
from typing import List, Dict
from _paths import get_package_dir
import pandas as pd
import streamlit as st

# Shared constants (kept minimal to avoid circular import)
FIELDNAMES = [
    "user_id_hash",
    "user_id_display",
    "user_id_plain",
    "frage_nr",
    "frage",
    "antwort",
    "richtig",
    "zeit",
]

LOGFILE = os.path.join(get_package_dir(), "mc_test_answers.csv")  # default fallback


def max_score(fragen: List[Dict], scoring_mode: str) -> int:
    """Calculate theoretical maximum score.
    For negative mode it's sum of positive weights; same as positive_only.
    """
    return sum([int(frage.get("gewichtung", 1) or 1) for frage in fragen])


def current_score(beantwortet: List[int | None], fragen: List[Dict], scoring_mode: str) -> int:
    if scoring_mode == "positive_only":
        total = 0
        for p, frage in zip(beantwortet, fragen):
            gewicht = int(frage.get("gewichtung", 1) or 1)
            if p == gewicht:
                total += gewicht
        return total
    # Negative Modus: Punkte enthalten +gewichtung bei richtiger Antwort oder -gewichtung bei falscher Antwort.
    # beantwortet-Liste speichert bereits die tatsächlichen Punktwerte (+/- gewichtung) oder None.
    return sum([p if p is not None else 0 for p in beantwortet])


def percentage(beantwortet: List[int | None], fragen: List[Dict], scoring_mode: str) -> float:
    max_p = max_score(fragen, scoring_mode)
    if max_p <= 0:
        return 0.0
    return current_score(beantwortet, fragen, scoring_mode) / max_p


def summarize_result(beantwortet: List[int | None], fragen: List[Dict], scoring_mode: str) -> dict:
    max_p = max_score(fragen, scoring_mode)
    cur = current_score(beantwortet, fragen, scoring_mode)
    prozent = cur / max_p if max_p > 0 else 0.0
    return {"score": cur, "max": max_p, "percent": prozent}


def load_answers_dataframe() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    try:
        return pd.read_csv(LOGFILE, on_bad_lines="skip")
    except Exception:
        return pd.DataFrame(columns=FIELDNAMES)


def leaderboard_completed(fragen_anzahl: int) -> pd.DataFrame:
    # Defensive: treat non-positive threshold as 0 (no completions)
    if fragen_anzahl is None:
        fragen_anzahl = 0
    try:
        fragen_anzahl = int(fragen_anzahl)
    except Exception:
        fragen_anzahl = 0
    if fragen_anzahl <= 0:
        # Without a positive question count, no one can be considered complete
        return pd.DataFrame()
    # Allow dynamic override: if main app module defines LOGFILE (and tests monkeypatch it), use that.
    active_logfile = LOGFILE
    try:  # late import to avoid circular issues
        import mc_test_app.mc_test_app as app_mod  # type: ignore

        lf = getattr(app_mod, "LOGFILE", None)
        if isinstance(lf, str) and lf:
            active_logfile = lf
    except Exception:
        pass
    if not (os.path.isfile(active_logfile) and os.path.getsize(active_logfile) > 0):
        return pd.DataFrame()
    try:
        df = pd.read_csv(active_logfile)
        df["richtig"] = pd.to_numeric(df["richtig"], errors="coerce")
        df["zeit"] = pd.to_datetime(df["zeit"], errors="coerce")
        agg_df = (
            df.groupby("user_id_hash")
            .agg(
                Punkte=("richtig", "sum"),
                Anzahl_Antworten=("frage_nr", "count"),
                Pseudonym=("user_id_plain", "first"),
            )
            .reset_index()
        )
        if fragen_anzahl == 1:
            completed_df = agg_df.copy()
        else:
            completed_df = agg_df[agg_df["Anzahl_Antworten"] >= fragen_anzahl].copy()
        if completed_df.empty:
            return pd.DataFrame()
        leaderboard = completed_df.sort_values(by=["Punkte"], ascending=[False])
        leaderboard = leaderboard[["Pseudonym", "Punkte"]].head(5)
        leaderboard.reset_index(drop=True, inplace=True)
        leaderboard.insert(0, "Platz", leaderboard.index + 1)
        return leaderboard
    except Exception:
        return pd.DataFrame()

# Provide a no-op clear for compatibility with previous cached version
def _leaderboard_clear():
    """Compatibility method so tests can call .clear() regardless of caching implementation."""
    return None

leaderboard_completed.clear = _leaderboard_clear  # type: ignore[attr-defined]
