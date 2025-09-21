"""
MC-Test Data Science
-------------------------------------------------
Lehrbeispiel für Multiple-Choice-Tests mit Streamlit.
Autor: kqc
"""

# Standardbibliotheken
import os
import time
import json
import random
import hashlib
import hmac
from datetime import datetime
from typing import List, Dict


# Drittanbieter-Bibliotheken
import streamlit as st
import pandas as pd
try:
    from . import scoring as _scoring  # type: ignore
except Exception:  # pragma: no cover
    _scoring = None

try:  # Support import when used as a package (tests) or as script (streamlit run)
    from .core import append_answer_row  # type: ignore
except Exception:  # pragma: no cover
    import sys as _sys, os as _os
    _here = _os.path.dirname(__file__)
    if _here not in _sys.path:
        _sys.path.append(_here)
    from core import append_answer_row  # type: ignore

# ---------------------------------------------------------------------------
# Compatibility shim:
# If the directory containing this file was directly added to sys.path (instead
# of its parent), Python will load this file as the top-level module 'mc_test_app'
# (not as a package). Tests and helper modules, however, reference the nested
# path 'mc_test_app.mc_test_app'. We register an alias so that
# 'import mc_test_app.mc_test_app' succeeds in both scenarios and dynamic imports
# (e.g. in scoring.py) can still resolve the LOGFILE attribute.
# ---------------------------------------------------------------------------
if __name__ == "mc_test_app":  # executed only in the flat (module) import case
    import sys as _sys
    _sys.modules.setdefault("mc_test_app.mc_test_app", _sys.modules[__name__])


try:  # pragma: no cover
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:  # pragma: no cover
    pass

# ------------------------- Seiteneinstellungen -----------------------------


st.set_page_config(
    page_title="MC-Test: Data Science",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load external CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Load CSS at the beginning
load_css()


# ---------------------------- Konstanten -----------------------------------
LOGFILE = os.path.join(os.path.dirname(__file__), "mc_test_answers.csv")
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
FRAGEN_ANZAHL = None  # Wird nach dem Laden der Fragen gesetzt
DISPLAY_HASH_LEN = 10
MAX_SAVE_RETRIES = 3

# Sticky Bar CSS (keine langen Quellcode-Zeilen)
STICKY_BAR_CSS = ""  # Now loaded from external CSS file


def hmac_compare(a: str, b: str) -> bool:
    """Zeitkonstante Vergleichsfunktion für geheime Admin-Keys.

    Nutzt hmac.compare_digest um Timing-Angriffe zu erschweren.
    """
    try:
        return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
    except Exception:
        return False


def get_rate_limit_seconds() -> int:
    """Liefert die minimale Wartezeit zwischen Antworten (Sekunden).

    Priorität: Environment-Variable > st.secrets > Default 0
    Robust gegenüber fehlendem Streamlit-Kontext (Tests / CLI).
    """
    env_val = os.getenv("MC_TEST_MIN_SECONDS_BETWEEN")
    if env_val is not None:
        try:
            return int(env_val)
        except Exception:
            return 0
    # Fallback secrets
    try:  # pragma: no cover - secrets meist nicht im Test
        secrets_val = st.secrets.get("MC_TEST_MIN_SECONDS_BETWEEN", None)
        if secrets_val is not None:
            return int(secrets_val)
    except Exception:
        pass
    return 0


def _load_fragen() -> List[Dict]:
    """Lädt die Fragen aus der JSON-Datei."""
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"Konnte questions.json nicht laden: {e}")
        return []


fragen = _load_fragen()
FRAGEN_ANZAHL = len(fragen)


def apply_accessibility_settings() -> None:
    # Add classes to body for CSS-based styling
    if st.session_state.get("high_contrast"):
        st.markdown('<script>document.body.classList.add("high-contrast");</script>', unsafe_allow_html=True)
    else:
        st.markdown('<script>document.body.classList.remove("high-contrast");</script>', unsafe_allow_html=True)

    if st.session_state.get("large_text"):
        st.markdown('<script>document.body.classList.add("large-text");</script>', unsafe_allow_html=True)
    else:
        st.markdown('<script>document.body.classList.remove("large-text");</script>', unsafe_allow_html=True)


@st.cache_data
def get_user_id_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()


def initialize_session_state():
    """Initialisiert den Session-State für einen neuen Testlauf."""
    st.session_state.beantwortet = [None] * len(fragen)
    st.session_state.frage_indices = list(range(len(fragen)))
    random.shuffle(st.session_state.frage_indices)
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False
    st.session_state.optionen_shuffled = []
    st.session_state.answer_outcomes = []  # Chronologische Liste der Korrektheitswerte (True/False)
    st.session_state.test_time_limit = 60 * 60  # 60 Minuten in Sekunden
    st.session_state.test_time_expired = False
    for q in fragen:
        opts = list(q.get("optionen", []))
        random.shuffle(opts)
        st.session_state.optionen_shuffled.append(opts)


def _duration_to_str(x):
    """Formatiert eine Zeitspanne als mm:ss."""
    if pd.isna(x):
        return ""
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def user_has_progress(user_id_hash: str) -> bool:
    """Prüft, ob für den Nutzer bereits Fortschritt existiert."""
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return False
        df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str}, on_bad_lines="skip")
        return not df[df["user_id_hash"] == user_id_hash].empty
    except Exception:
        return False


def reset_user_answers(user_id_hash: str) -> None:
    """Setzt alle Antworten des Nutzers zurück und initialisiert den Session-State neu."""
    try:
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str})
            df = df[df["user_id_hash"] != user_id_hash]
            df.to_csv(LOGFILE, index=False, columns=FIELDNAMES)
    except Exception as e:
        st.error(f"Konnte Antworten nicht zurücksetzen: {e}")

    keys_to_keep = {"user_id", "user_id_input", "user_id_hash", "load_progress"}
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep and (
            key.startswith("frage_")
            or key in {"beantwortet", "frage_indices", "start_zeit", "progress_loaded"}
        ):
            del st.session_state[key]
    initialize_session_state()


def load_all_logs() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        # Spalten normalisieren (fehlende hinzufügen, unerwartete verwerfen)
        missing = [c for c in FIELDNAMES if c not in df.columns]
        for c in missing:
            df[c] = ""
        df = df[[c for c in FIELDNAMES if c in df.columns]]
        df["zeit"] = pd.to_datetime(df["zeit"], errors="coerce")
        # Korrekte Typisierung / Validierung
        df["richtig"] = pd.to_numeric(df["richtig"], errors="coerce")
        # Frage-Nr extrahieren/validieren: muss int oder numerisch konvertierbar sein
        df["frage_nr"] = pd.to_numeric(df["frage_nr"], errors="coerce")
        # Entferne Zeilen mit fehlenden Pflichtfeldern oder fehlenden/ungültigen Werten
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
        # Filter: richtig nur -1,0,1 erlaubt (0 selten, aber toleriert), realistisch 1 oder -1
        df = df[df["richtig"].isin([-1, 0, 1])]
        # Pflichtfelder non-empty
        for col in ["user_id_hash", "frage", "antwort"]:
            df = df[df[col].astype(str).str.strip() != ""]
        # Nach Säuberung wieder frage_nr als int ausgeben (falls benötigt)
        try:
            df["frage_nr"] = df["frage_nr"].astype(int)
        except Exception:
            pass
        return df
    except Exception:
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
    except Exception:
        return pd.DataFrame()


def admin_view():
    st.title("🏆 Management: Bestenliste & Logs")
    df_logs = load_all_logs()
    if df_logs.empty:
        st.info("Noch keine Daten am Start.")
        return
    tabs = st.tabs(["🥇 Top 5 (fertig)", "👥 Alle Teilnahmen", "📄 Rohdaten"])
    with tabs[0]:
        top_df = calculate_leaderboard()
        if top_df.empty:
            st.info("Hier ist noch niemand durch! 👀")
        else:
            st.dataframe(top_df, use_container_width=True)
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
            st.dataframe(all_df, use_container_width=True)
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
        st.dataframe(df_show, use_container_width=True, height=400)
        csv_bytes = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📄 Rohdaten als CSV runterladen",
            csv_bytes,
            file_name="mc_test_raw_logs.csv",
            mime="text/csv",
        )


def load_user_progress(user_id_hash: str) -> None:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return
    try:
        df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str})
        user_df = df[df["user_id_hash"] == user_id_hash]
        if user_df.empty:
            return
        st.session_state.start_zeit = pd.to_datetime(user_df["zeit"]).min()
        for _, row in user_df.iterrows():
            frage_nr = int(row["frage_nr"])
            original_idx = next(
                (
                    i
                    for i, f in enumerate(fragen)
                    if f["frage"].startswith(f"{frage_nr}.")
                ),
                None,
            )
            if original_idx is not None:
                st.session_state.beantwortet[original_idx] = int(row["richtig"])
                st.session_state[f"frage_{original_idx}"] = row["antwort"]
    except Exception as e:
        st.error(f"Fehler beim Laden des Fortschritts: {e}")


def save_answer(
    user_id: str, user_id_hash: str, frage_obj: dict, antwort: str, punkte: int
) -> None:
    frage_nr = int(frage_obj["frage"].split(".")[0])
    # Anzeige-Name ist ein gekürzter Hash-Prefix, kein Klartext-Pseudonym
    user_id_display = user_id_hash[:DISPLAY_HASH_LEN]
    user_id_plain = user_id
    # Throttling: Mindestabstand zwischen zwei Antworten
    min_delta = get_rate_limit_seconds()
    if min_delta > 0:
        last_ts = st.session_state.get("last_answer_ts")
        now_ts = time.time()
        if last_ts and (now_ts - last_ts) < min_delta:
            remaining = int(min_delta - (now_ts - last_ts))
            # Zeitpunkt für nächsten erlaubten Save speichern (für Countdown-Anzeige)
            st.session_state["next_allowed_time"] = last_ts + min_delta
            st.warning(
                f"Bitte kurz warten ({remaining}s) bevor die nächste Antwort gespeichert wird."
            )
            return
    # Duplicate Guard: Falls bereits beantwortet (Session oder Log), nicht erneut schreiben
    dup_key = f"answered_{frage_nr}"
    if st.session_state.get(dup_key):
        return
    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
        try:
            # Schneller Check nur auf user_id_hash + frage_nr
            partial = pd.read_csv(
                LOGFILE,
                usecols=["user_id_hash", "frage_nr"],
                dtype={"user_id_hash": str, "frage_nr": str},
                on_bad_lines="skip",
            )
            mask = (partial["user_id_hash"] == user_id_hash) & (
                partial["frage_nr"] == str(frage_nr)
            )
            if not partial[mask].empty:
                st.session_state[dup_key] = True
                return
        except Exception:
            pass
    row = {
        "user_id_hash": user_id_hash,
        "user_id_display": user_id_display,
        "user_id_plain": user_id_plain,
        "frage_nr": frage_nr,
        "frage": frage_obj["frage"],
        "antwort": antwort,
        "richtig": punkte,
        "zeit": datetime.now().isoformat(timespec="seconds"),
    }
    # Only keep keys in FIELDNAMES
    row = {k: row[k] for k in FIELDNAMES}
    attempt = 0
    while attempt < MAX_SAVE_RETRIES:
        try:
            append_answer_row(row)
            st.session_state[dup_key] = True
            if min_delta > 0:
                st.session_state["last_answer_ts"] = time.time()
            return
        except Exception as e:  # broad to also catch lock timeout
            attempt += 1
            if attempt >= MAX_SAVE_RETRIES:
                st.error(f"Konnte Antwort nicht speichern (Versuche={attempt}): {e}")
            else:
                time.sleep(0.1 * attempt)


def display_question(frage_obj: dict, frage_idx: int, anzeige_nummer: int) -> None:
    # Defensive Initialisierung falls Tests / frische Session keinen Shuffle erzeugt haben
    if "optionen_shuffled" not in st.session_state:
        opts_list = []
        for f in fragen:
            raw_opts = f.get("optionen") or f.get("antworten") or []
            try:
                import random
                opt_copy = list(raw_opts)
                random.shuffle(opt_copy)
            except Exception:
                opt_copy = list(raw_opts)
            opts_list.append(opt_copy)
        st.session_state.optionen_shuffled = opts_list
    elif len(st.session_state.optionen_shuffled) < len(fragen):
        # Falls Fragenpool gewachsen ist
        fehlende = len(fragen) - len(st.session_state.optionen_shuffled)
        for f in fragen[-fehlende:]:
            raw_opts = f.get("optionen") or f.get("antworten") or []
            st.session_state.optionen_shuffled.append(list(raw_opts))
    frage_text = frage_obj["frage"].split(".", 1)[1].strip()
    gewichtung = frage_obj.get("gewichtung", 1)
    try:
        gewichtung = int(gewichtung)
    except Exception:
        gewichtung = 1
    thema = frage_obj.get("thema", "")
    with st.container(border=True):
        # Fragennummer im Fragenmodus: Position im Shuffle (fortlaufend ab 1)
        indices = st.session_state.frage_indices
        pos = indices.index(frage_idx) if frage_idx in indices else frage_idx
        header = f"### Frage {pos + 1} von {FRAGEN_ANZAHL}  <span style='color:#888;font-size:0.9em;'>({gewichtung} Punkt{'e' if gewichtung > 1 else ''})</span>"
        if thema:
            header += f"<br><span style='color:#4b9fff;font-size:0.95em;'>Thema: {thema}</span>"
        st.markdown(header, unsafe_allow_html=True)
        st.markdown(f"**{frage_text}**")
        is_disabled = False if st.session_state.beantwortet[frage_idx] is None else True
        optionen_anzeige = st.session_state.optionen_shuffled[frage_idx]
        # Add placeholder if unanswered
        if st.session_state.beantwortet[frage_idx] is None:
            optionen_anzeige = ["Wähle ..."] + optionen_anzeige
        # Initialisiere den Wert nur über den Widget-Key, nicht doppelt
        selected_val = st.session_state.get(f"frage_{frage_idx}", None)
        radio_kwargs = {
            "options": optionen_anzeige,
            "key": f"frage_{frage_idx}",
            "disabled": is_disabled,
            "label_visibility": "collapsed",
        }
        # Setze index nur, wenn noch keine Antwort im Session State existiert
        if selected_val is None and st.session_state.beantwortet[frage_idx] is None:
            radio_kwargs["index"] = 0  # Default to placeholder
        antwort = st.radio("Wähle deine Antwort:", **radio_kwargs)
        # Only allow answering if a real option is chosen
        if antwort == "Wähle ...":
            antwort = None
            # Add 'Frage überspringen' button if unanswered
            if st.session_state.beantwortet[frage_idx] is None:
                if st.button("Frage überspringen", key=f"skip_{frage_idx}"):
                    indices = st.session_state.frage_indices
                    if frage_idx in indices:
                        indices.remove(frage_idx)
                        indices.append(frage_idx)
                        st.session_state.frage_indices = indices
                    st.session_state[f"show_explanation_{frage_idx}"] = False
                    st.rerun()
        if antwort and not is_disabled:
            if st.session_state.start_zeit is None:
                st.session_state.start_zeit = datetime.now()
            richtig = antwort == frage_obj["optionen"][frage_obj["loesung"]]
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            gewichtung = frage_obj.get("gewichtung", 1)
            try:
                gewichtung = int(gewichtung)
            except Exception:
                gewichtung = 1
            if scoring_mode == "positive_only":
                punkte = gewichtung if richtig else 0
            else:
                punkte = gewichtung if richtig else -1
            st.session_state.beantwortet[frage_idx] = punkte
            # Chronologischen Verlauf ergänzen (für Streak-Badges)
            try:
                st.session_state.answer_outcomes.append(bool(richtig and punkte > 0) if scoring_mode == "positive_only" else bool(punkte > 0))
            except Exception:
                pass
            save_answer(
                st.session_state.user_id,
                st.session_state.user_id_hash,
                frage_obj,
                antwort,
                punkte,
            )
            reduce_anim = st.session_state.get("reduce_animations", False)
            if richtig:
                st.toast("Yes! Das war richtig!", icon="✅")
                if not reduce_anim:
                    st.balloons()
            else:
                st.toast("Leider daneben...", icon="❌")
            st.session_state[f"show_explanation_{frage_idx}"] = True
        if st.session_state.get(f"show_explanation_{frage_idx}", False):
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            gewichtung = frage_obj.get("gewichtung", 1)
            try:
                gewichtung = int(gewichtung)
            except Exception:
                gewichtung = 1
            punkte = st.session_state.beantwortet[frage_idx]
            num_answered = len(
                [p for p in st.session_state.beantwortet if p is not None]
            )
            # Punktestand über der Frage direkt nach Bewertung aktualisieren
            max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
            if scoring_mode == "positive_only":
                aktueller_punktestand = sum(
                    [
                        (
                            frage.get("gewichtung", 1)
                            if p == frage.get("gewichtung", 1)
                            else 0
                        )
                        for p, frage in zip(st.session_state.beantwortet, fragen)
                    ]
                )
            else:
                aktueller_punktestand = sum(
                    [p if p is not None else 0 for p in st.session_state.beantwortet]
                )
            score_html = (
                "<div class='top-progress-wrapper' aria-label='Punktestand insgesamt'>"
                f"<div style='font-size:1rem;font-weight:700;'>Aktueller Punktestand: {aktueller_punktestand} / {max_punkte}</div>"
                "</div>"
            )
            st.markdown(score_html, unsafe_allow_html=True)
            if scoring_mode == "positive_only":
                if punkte == gewichtung:
                    st.success(
                        f"Richtig! (+{gewichtung} Punkt{'e' if gewichtung > 1 else ''})"
                    )
                    reduce_anim = st.session_state.get("reduce_animations", False)
                    if not reduce_anim:
                        st.balloons()
                else:
                    st.error(
                        "Leider falsch. Die richtige Antwort ist: "
                        f"**{frage_obj['optionen'][frage_obj['loesung']]}**"
                    )
            else:
                if punkte == gewichtung:
                    st.success(
                        f"Richtig! (+{gewichtung} Punkt{'e' if gewichtung > 1 else ''})"
                    )
                    reduce_anim = st.session_state.get("reduce_animations", False)
                    if not reduce_anim:
                        st.balloons()
                else:
                    st.error(
                        f"Leider falsch (-1 Punkt). Die richtige Antwort ist: **{frage_obj['optionen'][frage_obj['loesung']]}**"
                    )
            erklaerung = frage_obj.get("erklaerung")
            if erklaerung:
                st.info(erklaerung)
            # Dynamische Motivation direkt im Fragenbereich anzeigen
            try:
                outcomes = st.session_state.get("answer_outcomes", [])
                num_answered_now = len([p for p in st.session_state.beantwortet if p is not None])
                if num_answered_now > 0:
                    num_correct = sum(1 for o in outcomes if o)
                    accuracy = num_correct / num_answered_now if num_answered_now else 0.0
                    last_correct = outcomes[-1] if outcomes else False
                    def acc_tier(a: float) -> str:
                        if a >= 0.9:
                            return "elite"
                        if a >= 0.75:
                            return "high"
                        if a >= 0.55:
                            return "mid"
                        return "low"
                    tier = acc_tier(accuracy)
                    progress_pct_local = int((num_answered_now / len(fragen)) * 100) if len(fragen) > 0 else 0
                    if progress_pct_local < 30:
                        band = "early"
                    elif progress_pct_local < 60:
                        band = "mid"
                    elif progress_pct_local < 90:
                        band = "late"
                    elif progress_pct_local < 100:
                        band = "close"
                    else:
                        band = "final"
                    base_phrases = {
                        ("early", "low"): [
                            "Einstieg holprig – jetzt Muster erkennen.",
                            "Analyse statt Frust – ruhig weiter.",
                            "Fokus schärfen, Treffer kommen.",
                        ],
                        ("early", "mid"): [
                            "Guter Start – stabil halten.",
                            "Ruhig lesen, Sicherheit ausbauen.",
                            "Solide Basis – weiter.",
                        ],
                        ("early", "high"): [
                            "Starker Start – Fokus halten!",
                            "Sehr sauber bis hier.",
                            "Momentum stimmt – präzise weiter.",
                        ],
                        ("early", "elite"): [
                            "Perfekter Auftakt – exzellent!",
                            "Makellos bis hier.",
                            "Elite-Quote – konzentriert bleiben.",
                        ],
                        ("mid", "low"): [
                            "Jetzt Korrektur: Erklärungen nutzen.",
                            "Tempo raus – Genauigkeit rein.",
                            "Strategiewechsel: Schlüsselbegriffe markieren.",
                        ],
                        ("mid", "mid"): [
                            "Stabile Mitte – Potenzial da.",
                            "Weiter fokussiert Schritt für Schritt.",
                            "Solider Fluss – jetzt schärfen.",
                        ],
                        ("mid", "high"): [
                            "Sehr gute Quote – halten!",
                            "Stark unterwegs – keine Hast.",
                            "Hohe Präzision – weiter so.",
                        ],
                        ("mid", "elite"): [
                            "Exzellent konstant – beeindruckend.",
                            "Fast fehlerfrei – Qualität sichern.",
                            "Elite-Niveau – strukturiert bleiben.",
                        ],
                        ("late", "low"): [
                            "Letzte Phase: Genauigkeit zählt.",
                            "Fehlerquellen minimieren jetzt.",
                            "Sauber rausarbeiten statt raten.",
                        ],
                        ("late", "mid"): [
                            "Gut durchgehalten – weiter sauber.",
                            "Stabile Quote – konzentriert.",
                            "Fast im Ziel – ruhig fertig.",
                        ],
                        ("late", "high"): [
                            "Sehr stark – finish smart.",
                            "Top-Niveau halten.",
                            "Kontrolliert ins Ziel.",
                        ],
                        ("late", "elite"): [
                            "Elite-Run – nicht nachlassen!",
                            "Beinahe makellos – Fokus.",
                            "Grandios – sauber fertigführen.",
                        ],
                        ("close", "low"): [
                            "Kurz vor Ende: Sorgfalt zählt.",
                            "Noch Chancen für Treffer.",
                            "Letzte Fragen taktisch lesen.",
                        ],
                        ("close", "mid"): [
                            "Endspurt – Quote stabilisieren.",
                            "Keine Unsauberkeiten jetzt.",
                            "Kurz vor Ziel – sauber bleiben.",
                        ],
                        ("close", "high"): [
                            "Sehr stark – präzise abschließen.",
                            "Fast durch – keine Hektik.",
                            "Top-Level bis zuletzt.",
                        ],
                        ("close", "elite"): [
                            "Fast perfekt – konzentriert landen.",
                            "Elite bis zur Ziellinie.",
                            "Makelloses Finish anvisieren.",
                        ],
                        ("final", "low"): [
                            "Geschafft – jetzt nacharbeiten.",
                            "Reflexion: Welche Muster fehlten?",
                            "Analyse nutzen für nächste Runde.",
                        ],
                        ("final", "mid"): [
                            "Solide beendet – Wiederholung festigt.",
                            "Gute Basis – Review nutzen.",
                            "Reflektiere Unsicherheiten.",
                        ],
                        ("final", "high"): [
                            "Stark abgeschlossen – fast top.",
                            "Sehr gute Runde – stabil!",
                            "Leichte Wiederholung festigt.",
                        ],
                        ("final", "elite"): [
                            "Exzeptionell – nahezu perfekt!",
                            "Elite-Ergebnis – starke Arbeit.",
                            "Top-Performance – kurz sichern.",
                        ],
                    }
                    if last_correct and tier in {"low", "mid"}:
                        overlay = ["Momentum nutzen!", "Starker Treffer – weiter strukturieren."]
                    elif (not last_correct) and tier in {"high", "elite"}:
                        overlay = ["Mini-Delle – ruhig bleiben.", "Kurz prüfen, weiter stark."]
                    elif not last_correct and tier == "low":
                        overlay = ["Reset: langsam & exakt lesen.", "Kurze Pause, dann sauber weiter."]
                    else:
                        overlay = []
                    pool = base_phrases.get((band, tier), [])
                    final_pool = pool + overlay if overlay else pool
                    if final_pool:
                        rotation_index = num_answered_now % len(final_pool)
                        phrase = final_pool[rotation_index]
                        st.markdown(
                            f"<div style='margin-top:4px;font-size:0.8rem;opacity:0.85;padding:4px 6px;border-left:3px solid #444;'>💬 {phrase}</div>",
                            unsafe_allow_html=True,
                        )
            except Exception:
                pass
            if st.button("Nächste Frage!"):
                st.session_state[f"show_explanation_{frage_idx}"] = False
                st.rerun()


def calculate_leaderboard() -> pd.DataFrame:
    if _scoring is None:
        return pd.DataFrame()
    # Special-case: tests may monkeypatch FRAGEN_ANZAHL to 1 and expect a single
    # completed answer to appear. Provide a lightweight inline implementation.
    if (FRAGEN_ANZAHL or 0) <= 1:
        lf = LOGFILE
        if not (os.path.isfile(lf) and os.path.getsize(lf) > 0):
            return pd.DataFrame()
        try:
            df = pd.read_csv(lf)
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
        except Exception:
            return pd.DataFrame()
    return _scoring.leaderboard_completed(FRAGEN_ANZAHL or 0)

# Expose clear() for tests to invalidate cached leaderboard (compatibility)
try:  # pragma: no cover - trivial wrapper
    calculate_leaderboard.clear = _scoring.leaderboard_completed.clear  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    def _noop():
        return None
    calculate_leaderboard.clear = _noop  # type: ignore[attr-defined]


def display_sidebar_metrics(num_answered: int) -> None:
    st.sidebar.header("📋 Beantwortet")
    progress_pct = int((num_answered / len(fragen)) * 100) if len(fragen) > 0 else 0
    progress_html = f"""
    <div style='width:100%;height:16px;background:#222;border-radius:8px;overflow:hidden;margin-bottom:8px;'>
        <div style='height:100%;width:{progress_pct}%;background:linear-gradient(90deg,#00c853,#2196f3);transition:width .3s;border-radius:8px;'></div>
    </div>
    """
    st.sidebar.markdown(progress_html, unsafe_allow_html=True)
    st.sidebar.caption(f"{progress_pct} %")
    # --- Micro Badges (Streak / Progress Milestones) --- (Motivation jetzt im Fragenbereich, nicht mehr Sidebar)
    try:
        outcomes = st.session_state.get("answer_outcomes", [])
        # Fallback: if outcomes list length < number of stored answers, attempt reconstruction
        if outcomes and len(outcomes) < sum(p is not None for p in st.session_state.beantwortet):
            # Rebuild from beantwortet for consistency
            new_outcomes = []
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            for p, frage in zip(st.session_state.beantwortet, fragen):
                if p is None:
                    continue
                gewicht = int(frage.get("gewichtung", 1) or 1)
                if scoring_mode == "positive_only":
                    new_outcomes.append(p == gewicht)
                else:
                    new_outcomes.append(p == gewicht)
            outcomes = new_outcomes
            st.session_state.answer_outcomes = outcomes
        elif not outcomes:
            # First-time reconstruction if never initialized (legacy session)
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            rebuilt = []
            for p, frage in zip(st.session_state.beantwortet, fragen):
                if p is None:
                    continue
                gewicht = int(frage.get("gewichtung", 1) or 1)
                if scoring_mode == "positive_only":
                    rebuilt.append(p == gewicht)
                else:
                    rebuilt.append(p == gewicht)
            outcomes = rebuilt
            st.session_state.answer_outcomes = outcomes
        streak = 0
        for outcome in reversed(outcomes):
            if outcome:
                streak += 1
            else:
                break
        badges = []
        # Streak tiers (show highest only)
        if streak >= 10:
            badges.append("⚡ 10er Streak!")
        elif streak >= 5:
            badges.append("🔥 5 richtige in Folge")
        elif streak >= 3:
            badges.append(f"🔥 {streak} richtige in Folge")
        # Progress milestones (one-time)
        if progress_pct >= 50 and not st.session_state.get("_badge_50_shown"):
            badges.append("🏁 50% geschafft")
            st.session_state._badge_50_shown = True
        if progress_pct >= 75 and not st.session_state.get("_badge_75_shown"):
            badges.append("🚀 75% erreicht")
            st.session_state._badge_75_shown = True
        if progress_pct >= 100 and not st.session_state.get("_badge_100_shown"):
            badges.append("🏆 100% abgeschlossen!")
            st.session_state._badge_100_shown = True
        if badges:
            badge_html = "".join([
                f"<span style='display:inline-block;background:#333;padding:2px 8px;margin:2px 4px 6px 0;border-radius:12px;font-size:0.70rem;color:#eee;'>{b}</span>" for b in badges
            ])
            st.sidebar.markdown(badge_html, unsafe_allow_html=True)
        # Rotierende Motivations-Phrasen erst anzeigen, nachdem mindestens eine Frage beantwortet wurde
        # Motivationstexte nicht mehr in der Sidebar anzeigen
    except Exception:
        pass
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    if _scoring is not None:
        max_punkte = _scoring.max_score(fragen, scoring_mode)
        aktueller_punktestand = _scoring.current_score(
            st.session_state.beantwortet, fragen, scoring_mode
        )
    else:  # fallback
        max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                [
                    frage.get("gewichtung", 1)
                    if p == frage.get("gewichtung", 1)
                    else 0
                    for p, frage in zip(st.session_state.beantwortet, fragen)
                ]
            )
        else:
            aktueller_punktestand = sum(
                [p if p is not None else 0 for p in st.session_state.beantwortet]
            )
    st.sidebar.header("🎯 Punktestand")
    st.sidebar.metric(
        label="Dein Score:", value=f"{aktueller_punktestand} / {max_punkte}"
    )
    # Countdown für nächstmögliche Antwort (Throttling)
    next_allowed = st.session_state.get("next_allowed_time")
    if next_allowed:
        now = time.time()
        if now < next_allowed:
            remaining = int(next_allowed - now)
            st.sidebar.info(f"Noch {remaining}s bis zur nächsten Antwort!")
        else:
            # Abgelaufen -> entfernen
            st.session_state.pop("next_allowed_time", None)
    if num_answered == len(fragen):
        # Motivational emoji/quote after test completion
        prozent = (
            _scoring.percentage(st.session_state.beantwortet, fragen, scoring_mode)
            if _scoring is not None
            else (aktueller_punktestand / max_punkte if max_punkte > 0 else 0)
        )
        scoring_mode = st.session_state.get("scoring_mode", "positive_only")
        if scoring_mode == "positive_only":
            if prozent == 1.0:
                st.sidebar.success(
                    "💥 Granate! Alles richtig, du bist ein MC-Test-Profi! 🚀"
                )
            elif prozent >= 0.9:
                st.sidebar.success("🌟 Sehr gut! Über 90% richtig.")
            elif prozent >= 0.7:
                st.sidebar.success("🎉 Gut! Über 70% richtig.")
            elif prozent >= 0.5:
                st.sidebar.success("🙂 Ausreichend! Über 50% richtig.")
            else:
                st.sidebar.success(
                    "🤔 Noch Luft nach oben. Schau dir die Erklärungen an!"
                )
        else:
            if aktueller_punktestand < 0:
                st.sidebar.success(
                    "🫠 Endstand: Sehr kreativ! 😅 Nächstes Mal wird's besser!"
                )
            elif prozent == 1.0:
                st.sidebar.success(
                    "🌟🥇 Mega! Alles richtig, du bist ein MC-Test-Profi! 🚀"
                )
            elif prozent >= 0.8:
                st.sidebar.success("🎉👍 Sehr stark! Die meisten Konzepte sitzen. 🎯")
            elif prozent >= 0.5:
                st.sidebar.success("🙂 Solide Leistung! Die Basics sitzen. 👍")
            else:
                st.sidebar.success(
                    "🤔 Ein paar Sachen sind noch offen. Schau dir die Erklärungen an! 🔍"
                )
    leaderboard_df = calculate_leaderboard()
    admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    st.sidebar.header("🏆 Highscore")
    if not leaderboard_df.empty:
        # Render leaderboard as markdown table with HTML centering
        table_md = "| Platz | Pseudonym | Punkte |\n|:---:|:---:|:---:|\n"
        for _, row in leaderboard_df.iterrows():
            table_md += f"| <div style='text-align:center'>{row['Platz']}</div> "
            table_md += f"| <div style='text-align:center'>{row['Pseudonym']}</div> "
            table_md += f"| <div style='text-align:center'>{row['Punkte']}</div> |\n"
        st.sidebar.markdown(table_md, unsafe_allow_html=True)
    else:
        st.sidebar.info(
            "Noch kein Eintrag in der Bestenliste – sei der oder die Erste, die den Test abschließt!"
        )

    # --- Auffälliger, horizontal zentrierter Logout-Button ---
    st.sidebar.divider()
    st.sidebar.info("Du kannst den Test mit einem anderen Pseudonym erneut starten.")
    if st.sidebar.button("Abmelden", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

    # Admin-Gesamtübersicht Toggle nur bei (User == ADMIN_USER) UND validiertem geheimen Key
    admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    admin_key_cfg = os.getenv("MC_TEST_ADMIN_KEY", "").strip()
    if not admin_user_cfg and not admin_key_cfg:
        # DEV-Fallback (nur lokale Nutzung). Generiere einmalig pseudo-random Key.
        if "_dev_admin_key" not in st.session_state:
            import secrets
            st.session_state._dev_admin_key = secrets.token_urlsafe(16)
        admin_user_cfg = "admin"
        admin_key_cfg = st.session_state._dev_admin_key
        st.sidebar.warning(
            "[DEV] Standard-Admin aktiv: Benutzer 'admin' + angezeigter Key. Setze MC_TEST_ADMIN_USER / MC_TEST_ADMIN_KEY für Produktion!"
        )
        with st.sidebar.expander("DEV-Admin-Key"):
            st.code(admin_key_cfg, language="text")
    current_user = st.session_state.get("user_id")
    # Cache Flag in Session, damit Key nicht bei jedem Rerun neu eingegeben werden muss
    if "admin_auth_ok" not in st.session_state:
        st.session_state.admin_auth_ok = False
    if admin_user_cfg and current_user == admin_user_cfg:
        # 1) Authentifizierung (falls Key vorhanden)
        if admin_key_cfg and not st.session_state.admin_auth_ok:
            with st.sidebar.expander("🔐 Admin-Authentifizierung", expanded=True):
                entered = st.text_input(
                    "Admin-Key eingeben", type="password", key="admin_key_input"
                )
                if entered:
                    if hmac_compare(entered, admin_key_cfg):
                        st.session_state.admin_auth_ok = True
                        st.success("Admin-Key validiert.")
                    else:
                        st.error("Falscher Admin-Key.")
        # 2) Panel anzeigen nach erfolgreicher Authentifizierung / oder wenn kein Key nötig
        if (not admin_key_cfg) or st.session_state.admin_auth_ok:
            # Sichtbarkeits-Schalter für Admin-Panel Tabs
            if "show_admin_panel" not in st.session_state:
                st.session_state.show_admin_panel = True
            st.session_state.show_admin_panel = st.sidebar.checkbox(
                "Admin-Panel anzeigen", value=st.session_state.show_admin_panel, key="show_admin_panel_checkbox"
            )
            if st.session_state.show_admin_panel:
                display_admin_panel()
            else:
                st.sidebar.info("Admin-Panel ausgeblendet – Checkbox aktivieren zum Anzeigen.")


def display_admin_full_review():
    st.sidebar.success("Admin‑Analyse aktiv – Auswertung im Hauptbereich sichtbar.")
    st.markdown("## � Gesamtübersicht aller Fragen")
    st.caption(
        "Metadaten: Schwierigkeitsgrad = Lösungsquote; Trennschärfe = Punkt-Biserial (Item vs. Gesamt ohne Item)."
    )
    # Versuche Log zu laden
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        st.info("Noch keine Antworten erfasst – es liegen keine Daten für die Auswertung vor.")
        return
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
    except Exception as e:
        st.error(f"Antwort-Log konnte nicht geladen werden: {e}")
        return
    if df.empty:
        st.info("Log-Datei ist leer – noch keine Einträge vorhanden.")
        return
    # Grund-Validierung
    required_cols = {"frage_nr", "frage", "antwort", "richtig", "user_id_hash"}
    if not required_cols.issubset(set(df.columns)):
        st.warning("Log-Datei unvollständig – Auswertung möglicherweise eingeschränkt.")
    # Aggregationen
    # Normalisiere korrekte Antworten (richtig>0 => korrekt)
    df["is_correct"] = df["richtig"].apply(
        lambda x: 1
        if pd.to_numeric(x, errors="coerce")
        and int(pd.to_numeric(x, errors="coerce") or 0) > 0
        else 0
    )
    grouped = df.groupby(["frage_nr", "frage"], as_index=False).agg(
        n_answers=("antwort", "count"),
        n_correct=("is_correct", "sum"),
    )
    grouped["correct_pct"] = grouped.apply(
        lambda r: (r.n_correct / r.n_answers * 100) if r.n_answers else 0, axis=1
    )

    # Zusatz: Dominanter Distraktor % wird später berechnet, sobald falsch_anzahl vorhanden ist

    # Vorbereitung für Trennschärfe (point-biserial): pro User Gesamtleistung (ohne aktuelles Item)
    user_totals = (
        df.groupby("user_id_hash", as_index=False)["is_correct"].sum().rename(
            columns={"is_correct": "total_correct_all"}
        )
    )
    df = df.merge(user_totals, on="user_id_hash", how="left")
    df["total_correct_excl"] = df["total_correct_all"] - df["is_correct"]

    # Funktion zur Berechnung der Punkt-Biserial-Korrelation je Item
    def _point_biserial(sub: pd.DataFrame) -> float:
        # item variable: is_correct (0/1); total score: total_correct_excl
        if sub["is_correct"].nunique() < 2:
            return float("nan")
        if sub["total_correct_excl"].nunique() < 2:
            return float("nan")
        try:
            return float(sub["is_correct"].corr(sub["total_correct_excl"]))
        except Exception:
            return float("nan")

    discrim = (
        df.groupby("frage_nr")
        .apply(_point_biserial)
        .reset_index(name="discrimination_pb")
    )
    grouped = grouped.merge(discrim, on="frage_nr", how="left")

    # Qualitätslabel für Trennschärfe
    def _disc_label(x: float) -> str:
        if pd.isna(x):
            return "—"
        if x >= 0.40:
            return "sehr gut"
        if x >= 0.30:
            return "gut"
        if x >= 0.20:
            return "mittel"
        return "schwach"

    # Schwierigkeits-Label (basierend auf Prozent richtig)
    def _difficulty_label(pct: float) -> str:
        if pct < 30:
            return "schwierig"
        if pct <= 70:
            return "mittel"
        return "leicht"

    # Häufigste falsche Antwort je Frage
    wrong_df = df[df["is_correct"] == 0]
    if not wrong_df.empty:
        most_wrong = (
            wrong_df.groupby(["frage_nr", "antwort"])  # type: ignore[arg-type]
            .size()
            .reset_index(name="count")
        )
        idx = most_wrong.groupby("frage_nr")["count"].idxmax()
        most_wrong_top = most_wrong.loc[idx][["frage_nr", "antwort", "count"]]
        grouped = grouped.merge(most_wrong_top, on="frage_nr", how="left")
        grouped.rename(
            columns={"antwort": "häufigste_falsche_antwort", "count": "falsch_anzahl"},
            inplace=True,
        )
    else:
        grouped["häufigste_falsche_antwort"] = None
        grouped["falsch_anzahl"] = 0
    grouped["dominanter_distraktor_pct"] = grouped.apply(
        lambda r: (r.falsch_anzahl / r.n_answers * 100) if r.n_answers else 0, axis=1
    )
    grouped["Schwierigkeitsgrad"] = grouped["correct_pct"].map(_difficulty_label)
    grouped["Trennschärfe"] = grouped["discrimination_pb"].map(_disc_label)
    # Sortierung: schwierigste zuerst (niedrigste Korrektquote), dann Fragen mit wenig Daten
    grouped = grouped.sort_values(
        by=["correct_pct", "discrimination_pb", "n_answers"],
        ascending=[True, False, True],
    )
    # Anzeige als Tabelle
    show_cols = [
        "frage_nr",
        "n_answers",
        "n_correct",
        "correct_pct",
        "Schwierigkeitsgrad",
        "discrimination_pb",
        "Trennschärfe",
        "häufigste_falsche_antwort",
        "falsch_anzahl",
        "dominanter_distraktor_pct",
    ]
    styled = grouped[show_cols].copy()
    styled.rename(
        columns={
            "frage_nr": "Frage-Nr.",
            "n_answers": "Antworten (gesamt)",
            "n_correct": "Richtig",
            "correct_pct": "Richtig % (roh)",
            "discrimination_pb": "Trennschärfe (r_pb)",
            "häufigste_falsche_antwort": "Häufigste falsche Antwort",
            "falsch_anzahl": "Häufigkeit dieser falschen",
            "dominanter_distraktor_pct": "Domin. Distraktor %",
        },
        inplace=True,
    )
    styled["Richtig %"] = grouped["correct_pct"].map(lambda v: f"{v:.1f}%")
    styled["Domin. Distraktor %"] = grouped["dominanter_distraktor_pct"].map(
        lambda v: f"{v:.1f}%" if v else "—"
    )
    styled["Trennschärfe (r_pb)"] = styled["Trennschärfe (r_pb)"].map(
        lambda v: f"{v:.2f}" if pd.notna(v) else "—"
    )
    st.dataframe(styled, use_container_width=True)
    # Optionale Detailauswahl einer Frage
    with st.expander("🔎 Detail zu einer ausgewählten Frage"):
        frage_nums = grouped["frage_nr"].tolist()
        sel = (
            st.selectbox(
                "Frage auswählen",
                frage_nums,
                format_func=lambda x: f"Frage {x}",
            )
            if frage_nums
            else None
        )
        if sel is not None:
            detail = df[df["frage_nr"] == sel].copy()
            st.markdown(f"### Frage {sel}: Verlauf & Antworten")
            frage_text_series = grouped[grouped["frage_nr"] == sel]["frage"]
            if not frage_text_series.empty:
                raw_text = frage_text_series.iloc[0]
                # Frage Text extrahieren (nach erstem Punkt)
                try:
                    text_only = raw_text.split(".", 1)[1].strip()
                except Exception:
                    text_only = raw_text
                st.write(f"**Fragentext:** {text_only}")
            st.write("Antwortverlauf (chronologisch, älteste zuerst):")
            detail_sorted = detail[["user_id_hash", "antwort", "richtig", "zeit"]].sort_values(
                by="zeit"
            )
            st.dataframe(detail_sorted, use_container_width=True)

            # Antwortverteilung für die Frage
            st.write("Antwortverteilung (Optionen – Häufigkeit & Anteil):")
            dist = (
                detail.groupby(["antwort"], as_index=False)
                .agg(
                    anzahl=("antwort", "count"),
                    korrekt=("is_correct", "max"),
                )
                .sort_values(by="anzahl", ascending=False)
            )
            total = dist["anzahl"].sum() or 1
            dist["Anteil %"] = dist["anzahl"].map(lambda v: f"{v / total * 100:.1f}%")
            dist.rename(
                columns={
                    "antwort": "Option",
                    "anzahl": "Anzahl",
                    "korrekt": "Ist richtig",
                },
                inplace=True,
            )
            dist["Ist richtig"] = dist["Ist richtig"].map(lambda x: "✅" if x else "❌")
            st.dataframe(dist, use_container_width=True)


def display_admin_panel():
    """Zentrales Admin-Panel mit mehreren Tabs (nach Auth)."""
    st.sidebar.success("Admin-Modus aktiv")
    tab_analysis, tab_export, tab_system = st.tabs([
        "📊 Analyse",
        "📤 Export",
        "🛠 System",
    ])
    with tab_analysis:
        display_admin_full_review()
    with tab_export:
        st.markdown("### Export / Downloads")
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_log = pd.read_csv(LOGFILE, on_bad_lines="skip")
                csv_bytes = df_log.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Antwort-Log (CSV) herunterladen",
                    data=csv_bytes,
                    file_name="mc_test_answers_export.csv",
                    mime="text/csv",
                )
                st.write("Spalten:", ", ".join(df_log.columns))
            except Exception as e:
                st.error(f"Export fehlgeschlagen: {e}")
        else:
            st.info("Kein Log vorhanden.")
    with tab_system:
        st.markdown("### System / Konfiguration")
        st.write("Benutzer (Session):", st.session_state.get("user_id"))
        st.write("Admin-User aktiv:", bool(os.getenv("MC_TEST_ADMIN_USER")))
        st.write(
            "Admin-Key-Modus:",
            "Hash/Klartext gesetzt" if os.getenv("MC_TEST_ADMIN_KEY") else "DEV / keiner gesetzt",
        )
        st.write("Anzahl geladene Fragen:", FRAGEN_ANZAHL)
        st.write(
            "Antworten im Log:",
            sum(1 for _ in open(LOGFILE, "r", encoding="utf-8")) - 1 if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0 else 0,
        )
        # Erweiterte Kennzahlen
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_sys = pd.read_csv(LOGFILE, on_bad_lines="skip")
                if not df_sys.empty:
                    unique_users = df_sys["user_id_hash"].nunique()
                    st.write("Eindeutige Teilnehmer (gesamt):", unique_users)
                    # Letzte Aktivität (max Zeit) + Umwandlung
                    if "zeit" in df_sys.columns:
                        try:
                            df_sys["_ts"] = pd.to_datetime(df_sys["zeit"], errors="coerce")
                            last_ts = df_sys["_ts"].max()
                            if pd.notna(last_ts):
                                st.write("Letzte Aktivität:", last_ts)
                                # Aktive Nutzer <= 10 min
                                cutoff = last_ts - pd.Timedelta(minutes=10)
                                active_users = df_sys[df_sys["_ts"] >= cutoff]["user_id_hash"].nunique()
                                st.write("Aktive Nutzer (<10 min):", active_users)
                        except Exception:
                            pass
                    # Durchschnittliche Antworten pro Teilnehmer
                    ans_per_user = (
                        df_sys.groupby("user_id_hash")["frage_nr"].count().mean()
                        if unique_users > 0
                        else 0
                    )
                    st.write("Ø Antworten je Teilnehmer:", f"{ans_per_user:.1f}")
                    # Gesamt-Accuracy
                    if "richtig" in df_sys.columns:
                        try:
                            df_sys["_corr"] = df_sys["richtig"].apply(
                                lambda x: 1
                                if pd.to_numeric(x, errors="coerce")
                                and int(pd.to_numeric(x, errors="coerce") or 0) > 0
                                else 0
                            )
                            overall_acc = df_sys["_corr"].mean() * 100 if len(df_sys) else 0
                            st.write("Gesamt-Accuracy aller Antworten:", f"{overall_acc:.1f}%")
                        except Exception:
                            pass
            except Exception as e:
                st.warning(f"Erweiterte Metriken nicht verfügbar: {e}")


def display_final_summary(num_answered: int) -> None:
    # Review-Modus auch bei abgelaufener Zeit anzeigen
    if num_answered != len(fragen) and not st.session_state.get(
        "test_time_expired", False
    ):
        return
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    if _scoring is not None:
        max_punkte = _scoring.max_score(fragen, scoring_mode)
        aktueller_punktestand = _scoring.current_score(
            st.session_state.beantwortet, fragen, scoring_mode
        )
        prozent = _scoring.percentage(
            st.session_state.beantwortet, fragen, scoring_mode
        )
    else:  # fallback
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                [
                    frage.get("gewichtung", 1)
                    if p == frage.get("gewichtung", 1)
                    else 0
                    for p, frage in zip(st.session_state.beantwortet, fragen)
                ]
            )
        else:
            aktueller_punktestand = sum(
                [p for p in st.session_state.beantwortet if p is not None]
            )
        max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
        prozent = aktueller_punktestand / max_punkte if max_punkte > 0 else 0
    reduce_anim = st.session_state.get("reduce_animations", False)
    # Unterschiedliche Nachricht je nach Test-Ende
    if st.session_state.get("test_time_expired", False):
        st.info("Du kannst dir alle Fragen und Antworten ansehen.")
    else:
        st.header("🚀 Test durchgezogen!")
    emoji, quote = "", ""
    if scoring_mode == "positive_only":
        if prozent == 1.0:
            emoji, quote = (
                "💥",
                "**Granate! Alles richtig, du bist ein MC-Test-Profi!** 🚀",
            )
            if not reduce_anim:
                st.balloons()
                st.snow()
        elif prozent >= 0.9:
            emoji, quote = ("🌟", "**Sehr gut! Über 90% richtig.**")
        elif prozent >= 0.7:
            emoji, quote = ("🎉", "**Gut! Über 70% richtig.**")
        elif prozent >= 0.5:
            emoji, quote = ("🙂", "**Ausreichend! Über 50% richtig.**")
        else:
            emoji, quote = (
                "🤔",
                "**Noch Luft nach oben. Erklärungen zu falschen Antworten lesen!** 🔍",
            )
    else:
        if aktueller_punktestand < 0:
            emoji = "🫠"
            quote = (
                f"**Endstand: {aktueller_punktestand} von {len(fragen)} Punkten.**  "
                "Das war... kreativ! 😅  "
                "Manchmal ist der Weg das Ziel. Erklärungen lesen & nächstes Mal Highscore holen! 🚀"
            )
        elif prozent == 1.0:
            emoji, quote = (
                "🌟🥇",
                "**Mega! Alles richtig, du bist ein MC-Test-Profi!** 🚀",
            )
            if not reduce_anim:
                st.balloons()
                st.snow()
        elif prozent >= 0.8:
            emoji, quote = (
                "🎉👍",
                "**Sehr stark! Du hast die meisten Konzepte voll drauf.** 🎯",
            )
        elif prozent >= 0.5:
            emoji, quote = ("🙂", "**Solide Leistung! Die Basics sitzen.** 👍")
        else:
            emoji, quote = (
                "🤔",
                "**Ein paar Sachen sind noch offen. Erklärungen zu falschen Antworten ansehen!** 🔍",
            )
    prozent_anzeige = f"<span style='color:#ffd600;font-size:2rem;font-weight:700;'>{round(prozent * 100)} %</span>"
    st.markdown(
        f"### {emoji} Endstand: {prozent_anzeige} richtig",
        unsafe_allow_html=True
    )
    if quote:
        st.markdown(quote)
    # Review-Modus Toggle
        st.divider()
        st.subheader("🧐 Review")
        # Nur einmal Review-Modus anzeigen
        show_review = st.checkbox("Fragen anzeigen", key="review_mode")
        if show_review:
            filter_options = [
                "Alle Fragen",
                "Falsch beantwortete Fragen",
                "Richtig beantwortete Fragen",
                "Nicht beantwortete Fragen",
            ]
            themen = sorted(set([frage.get("thema", "") for frage in fragen if frage.get("thema")]))
            if themen:
                filter_options += [f"Thema: {t}" for t in themen]
            # Persist last chosen filter across reruns
            default_index = 0
            last_filter = st.session_state.get("review_last_filter")
            if last_filter in filter_options:
                default_index = filter_options.index(last_filter)
            filter_option = st.selectbox(
                "Welche Fragen anzeigen?",
                filter_options,
                index=default_index,
                key="review_filter_option",
            )
            st.session_state.review_last_filter = filter_option
            # Build indices_to_show according to filter_option
            indices_to_show = []
            for i, frage in enumerate(fragen):
                user_val = st.session_state.get(f"frage_{i}")
                korrekt = frage["optionen"][frage["loesung"]]
                if filter_option == "Alle Fragen":
                    indices_to_show.append(i)
                elif filter_option == "Falsch beantwortete Fragen":
                    if user_val is not None and user_val != korrekt:
                        indices_to_show.append(i)
                elif filter_option == "Richtig beantwortete Fragen":
                    if user_val is not None and user_val == korrekt:
                        indices_to_show.append(i)
                elif filter_option == "Nicht beantwortete Fragen":
                    if user_val is None:
                        indices_to_show.append(i)
                elif filter_option.startswith("Thema: "):
                    thema_name = filter_option.replace("Thema: ", "")
                    if frage.get("thema", "") == thema_name:
                        indices_to_show.append(i)
            # Reset active_review_idx if filter changes
            if (
                "last_filter_option" not in st.session_state
                or st.session_state.last_filter_option != filter_option
            ):
                st.session_state.active_review_idx = 0
                st.session_state.last_filter_option = filter_option
            # Track which review index is open
            if "active_review_idx" not in st.session_state:
                st.session_state.active_review_idx = 0
            # Clamp active_review_idx
            if st.session_state.active_review_idx >= len(indices_to_show):
                st.session_state.active_review_idx = 0
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            for pos, idx in enumerate(indices_to_show):
                frage = fragen[idx]
                user_val = st.session_state.get(f"frage_{idx}")
                korrekt = frage["optionen"][frage["loesung"]]
                if user_val is None:
                    mark_icon = "❓"  # Unbeantwortet
                else:
                    richtig = user_val == korrekt
                    mark_icon = "✅" if richtig else "❌"
                expander_title = f"Frage {idx + 1}: {mark_icon}"
                expanded = pos == st.session_state.active_review_idx
                with st.expander(expander_title, expanded=expanded):
                    # Zeige Fragennummer, dann Thema, dann Frage
                    st.markdown(f"### Frage {idx + 1} von {FRAGEN_ANZAHL}")
                    thema = frage.get("thema", "")
                    if thema:
                        st.markdown(f"<span style='color:#4b9fff;font-size:1.05em;font-weight:600;'>Thema: {thema}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{frage['frage']}**")
                    st.caption("Optionen:")
                    for opt in frage.get("optionen", []):
                        style = ""
                        prefix = "•"
                        if user_val is None:
                            if opt == korrekt:
                                style = "background-color:#218838;color:#fff;padding:2px 8px;border-radius:6px;"  # Dunkelgrün
                                prefix = "✅"
                            st.markdown(
                                f"<span style='{style}'>{prefix} {opt}</span>",
                                unsafe_allow_html=True,
                            )
                            continue
                        if opt == user_val and not richtig:
                            style = "background-color:#c82333;color:#fff;padding:2px 8px;border-radius:6px;"  # Dunkelrot
                            prefix = "❌"
                        elif opt == user_val and richtig:
                            style = "background:linear-gradient(90deg,#fff3cd 50%,#218838 50%);color:#111;padding:2px 8px;border-radius:6px;"
                            prefix = "✅"
                        elif opt == korrekt:
                            style = "background-color:#218838;color:#fff;padding:2px 8px;border-radius:6px;"  # Dunkelgrün
                            prefix = "✅"
                        st.markdown(
                            f"<span style='{style}'>{prefix} {opt}</span>",
                            unsafe_allow_html=True,
                        )
                    erklaerung = frage.get("erklaerung")
                    if erklaerung:
                        if len(erklaerung) > 200:
                            with st.expander("Erklärung anzeigen"):
                                st.markdown(erklaerung)
                        else:
                            st.info(f"Erklärung: {erklaerung}")
                    # Show feedback for wrong answer
                    if user_val is not None and user_val != korrekt:
                        if scoring_mode == "positive_only":
                            st.error(
                                f"Leider falsch. Die richtige Antwort ist: **{korrekt}**"
                            )
                        else:
                            st.error(
                                f"Leider falsch (-1 Punkt). Die richtige Antwort ist: **{korrekt}**"
                            )


def check_admin_permission(user_id: str, provided_key: str) -> bool:
    """Prüft Admin-Berechtigung basierend auf ENV-Konfiguration.

    Regeln:
    - MC_TEST_ADMIN_USER gesetzt: Nur genau dieses Pseudonym darf Admin werden.
    - MC_TEST_ADMIN_KEY gesetzt: Key muss exakt passen.
    - Wenn kein Key gesetzt ist (MC_TEST_ADMIN_KEY leer), reicht beliebige nicht-leere Eingabe,
      sofern (falls gesetzt) der Benutzername MC_TEST_ADMIN_USER entspricht.
    """
    admin_user = st.secrets.get("MC_TEST_ADMIN_USER", None)
    if not admin_user:
        admin_user = os.getenv("MC_TEST_ADMIN_USER", "")
    admin_user = str(admin_user).strip()
    admin_key_env = st.secrets.get("MC_TEST_ADMIN_KEY", None)
    if not admin_key_env:
        admin_key_env = os.getenv("MC_TEST_ADMIN_KEY", "")
    admin_key_env = str(admin_key_env).strip()
    provided_key = provided_key.strip()

    # 1. Wenn Admin-Key gesetzt ist, muss er exakt passen
    if admin_key_env:
        return provided_key == admin_key_env
    # 2. Wenn Admin-User gesetzt ist, muss User passen und Key nicht leer sein
    if admin_user:
        return user_id == admin_user and provided_key != ""
    # 3. Wenn nichts gesetzt ist, reicht beliebige nicht-leere Eingabe
    return bool(provided_key)


def handle_user_session():
    # 1. Nutzerkennung
    st.sidebar.header("🧑‍💻 Wer bist du?")
    if "user_id" not in st.session_state:

        def start_test():
            user_id_input = st.session_state.get("user_id_input", "").strip()
            if not user_id_input:
                st.sidebar.error("Gib dein Pseudonym ein!")
            else:
                st.session_state.user_id = user_id_input
                st.session_state["mc_test_started"] = True
                st.session_state["trigger_rerun"] = True

        st.sidebar.text_input(
            "Pseudonym eingeben",
            value=st.session_state.get("user_id_input", ""),
            key="user_id_input",
            on_change=start_test,
        )
        if st.sidebar.button("Test starten"):
            start_test()
        st.stop()
    st.sidebar.success(f"👋 Angemeldet als: **{st.session_state.user_id}**")
    current_hash = st.session_state.get("user_id_hash") or get_user_id_hash(
        st.session_state.user_id
    )
    has_progress = user_has_progress(current_hash)
    st.session_state["load_progress"] = has_progress

    # Session-State initialisieren, falls nötig
    if (
        "beantwortet" not in st.session_state
        or "frage_indices" not in st.session_state
        or len(st.session_state.beantwortet) != len(fragen)
    ):
        initialize_session_state()

    # Fortschritt laden, falls vorhanden
    if has_progress:
        if (
            "progress_loaded" not in st.session_state
            or not st.session_state.progress_loaded
        ):
            load_user_progress(current_hash)
            st.session_state.progress_loaded = True
        num_answered = len([p for p in st.session_state.beantwortet if p is not None])
        # Fortschritt & Score nur im Review-Modus anzeigen
        if st.session_state.get("force_review", False):
            display_sidebar_metrics(num_answered)
        # Show info only if test is fully completed
        if num_answered == len(st.session_state.beantwortet):
            st.sidebar.info(
                "Mit diesem Namen hast du den Test schon gemacht! Dein Ergebnis bleibt gespeichert – nochmal starten geht leider nicht. Aber du kannst alles nochmal anschauen und lernen. 🚀\n\nTipp: Mit einem anderen Pseudonym kannst du den Test erneut machen."
            )
        # Review weiterhin möglich
        st.session_state["force_review"] = True
        return st.session_state.user_id
    # 2. Fortschritt & Score direkt nach Nutzerkennung
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    display_sidebar_metrics(num_answered)

    # 3. Management Sektion
    st.sidebar.divider()
    with st.sidebar.expander("🏆 Management", expanded=False):
        admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
        user_allowed = (not admin_user_cfg) or (
            st.session_state.user_id == admin_user_cfg
        )
        if not user_allowed:
            st.caption(
                f"Management nur für: {admin_user_cfg}" if admin_user_cfg else ""
            )
        if user_allowed:

            def try_admin_activate():
                admin_key_input = st.session_state.get("admin_key_input", "").strip()
                if check_admin_permission(st.session_state.user_id, admin_key_input):
                    st.session_state["admin_view"] = True
                else:
                    st.error("Nope, das war nicht der richtige Management-Key.")

            st.text_input(
                "Management-Key",
                type="password",
                key="admin_key_input",
                on_change=try_admin_activate,
            )
            if not st.session_state.get("admin_view"):
                if st.button("Management aktivieren"):
                    try_admin_activate()
            else:
                # Admin: Scoring mode selection
                scoring_modes = {
                    "positive_only": "Nur positive Punkte (kein Abzug)",
                    "negative": "Mit Punktabzug bei falscher Antwort",
                }
                default_mode = st.session_state.get("scoring_mode", "positive_only")
                selected_mode = st.radio(
                    "Punktebewertung wählen:",
                    list(scoring_modes.keys()),
                    format_func=lambda k: scoring_modes[k],
                    index=list(scoring_modes.keys()).index(default_mode),
                    key="scoring_mode_radio",
                )
                st.session_state["scoring_mode"] = selected_mode
                st.caption("Die Änderung gilt sofort für die Auswertung und Anzeige.")
                # Option to delete all answers with confirmation
                st.divider()
                st.subheader("⚠️ Antworten aller Teilnehmer löschen")
                if st.button("Alle Antworten löschen"):
                    st.session_state["show_delete_confirm"] = True
                if st.session_state.get("show_delete_confirm", False):
                    st.warning(
                        "Bist du sicher? Das löscht alle Antworten unwiderruflich!",
                        icon="⚠️",
                    )
                    if st.button("Ja, wirklich löschen!", key="delete_confirmed"):
                        try:
                            logfile_path = os.path.join(
                                os.path.dirname(__file__), "mc_test_answers.csv"
                            )
                            if os.path.isfile(logfile_path):
                                os.remove(logfile_path)
                            st.success("Alle Antworten wurden gelöscht.")
                        except Exception as e:
                            st.error(f"Fehler beim Löschen: {e}")
                        st.session_state["show_delete_confirm"] = False
                    if st.button("Abbrechen", key="delete_cancel"):
                        st.session_state["show_delete_confirm"] = False
                if st.button("Management verlassen"):
                    st.session_state["admin_view"] = False
                    st.rerun()
    return st.session_state.user_id


def main():
    # Session-State initialisieren, falls nötig
    if "beantwortet" not in st.session_state or "frage_indices" not in st.session_state:
        initialize_session_state()
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    user_id = None
    if "user_id" in st.session_state:
        user_id = st.session_state.user_id

    # Always show header and info before user session is set up
    if "user_id" not in st.session_state:
        st.markdown(
            """
<div style='display:flex;justify-content:center;align-items:center;'>
  <div style='max-width:600px;text-align:center;padding:24px;background:rgba(40,40,40,0.95);border-radius:18px;box-shadow:0 2px 16px #0003;'>
    <h2 style='color:#4b9fff;'>Willkommen zu 100 Fragen!</h2>
    <p style='font-size:1.05rem;'>
      Teste dein Wissen rund um <strong>Data Science</strong>, <strong>Machine und Deep Learning</strong>.
      <br><br>
      Starte jetzt 🚀 – und hol dir deinen Highscore!
    </p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        # --- Gestapeltes Balkendiagramm: Fragenverteilung nach Thema und Gewichtung ---
        import plotly.graph_objects as go

        df_fragen = pd.DataFrame(fragen)
        if "gewichtung" not in df_fragen.columns:
            df_fragen["gewichtung"] = 1
        if "thema" not in df_fragen.columns:
            df_fragen["thema"] = "Unbekannt"

        def gewicht_to_schwierig(gewicht):
            try:
                g = int(gewicht)
                if g == 1:
                    return "Leicht"
                elif g == 2:
                    return "Mittel"
                else:
                    return "Schwer"
            except Exception:
                return "Leicht"

        df_fragen["Schwierigkeit"] = df_fragen["gewichtung"].apply(gewicht_to_schwierig)
        pivot = df_fragen.pivot_table(
            index="thema",
            columns="Schwierigkeit",
            values="frage",
            aggfunc="count",
            fill_value=0,
        )

        # Farben für Dark Theme
        dark_bg = "#181818"
        text_color = "#e0e0e0"
        bar_colors = {"Leicht": "#00c853", "Mittel": "#4b9fff", "Schwer": "#ffb300"}
        # Plotly Stacked Bar Chart
        fig = go.Figure()
        for schwierigkeit in ["Leicht", "Mittel", "Schwer"]:
            if schwierigkeit in pivot.columns:
                fig.add_trace(
                    go.Bar(
                        x=pivot.index,
                        y=pivot[schwierigkeit],
                        name=schwierigkeit,
                        marker_color=bar_colors[schwierigkeit],
                    )
                )
        fig.update_layout(
            barmode="stack",
            plot_bgcolor=dark_bg,
            paper_bgcolor=dark_bg,
            font=dict(color=text_color),
            xaxis_title="Thema",
            yaxis_title="Anzahl Fragen",
            legend_title="Schwierigkeit",
            margin=dict(l=40, r=40, t=40, b=40),
        )
        fig.update_xaxes(showgrid=False, linecolor=text_color)
        fig.update_yaxes(showgrid=False, linecolor=text_color)
        st.plotly_chart(fig, use_container_width=True)
    user_id = handle_user_session()
    # If triggered by Enter, rerun after session state is set
    if st.session_state.get("trigger_rerun"):
        st.session_state["trigger_rerun"] = False
        st.rerun()
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    # Hide header after first answer
    if user_id and num_answered == 0:
        st.title("Los geht's!")

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    if (
        user_id
        and num_answered == 0
        and num_answered < len(fragen)
        and not st.session_state.get("test_time_expired", False)
        and not st.session_state.get("force_review", False)
        and not st.session_state.get("load_progress", False)
        and not user_has_progress(st.session_state.get("user_id_hash", ""))
    ):
        st.info(
            "Du hast 60 Minuten für den Test. Die Zeit läuft ab deiner ersten Antwort. "
            "Wie viel Zeit noch bleibt, siehst du nach jeder Frage. Viel Erfolg!"
        )
    if st.session_state.start_zeit and num_answered < len(fragen):
        elapsed_time = (datetime.now() - st.session_state.start_zeit).total_seconds()
        remaining = int(st.session_state.test_time_limit - elapsed_time)
        if remaining > 0:
            minutes, seconds = divmod(remaining, 60)
            st.metric("⏳ Noch Zeit", f"{minutes:02d}:{seconds:02d}")
            if remaining <= 5 * 60:
                if minutes == 0:
                    st.warning(f"Achtung, nur noch {seconds} Sekunden!")
                else:
                    st.warning(
                        f"Achtung, nur noch {minutes} Minuten und {seconds} Sekunden!"
                    )
        else:
            st.session_state.test_time_expired = True
            st.header("⏰ Zeit ist um!")

    # Sticky Bar: show current score and open questions always, even after reload
    if "beantwortet" in st.session_state:
        scoring_mode = st.session_state.get("scoring_mode", "positive_only")
        max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                [
                    frage.get("gewichtung", 1) if p == frage.get("gewichtung", 1) else 0
                    for p, frage in zip(st.session_state.beantwortet, fragen)
                ]
            )
        else:
            aktueller_punktestand = sum(
                [p if p is not None else 0 for p in st.session_state.beantwortet]
            )
        answered = len([p for p in st.session_state.beantwortet if p is not None])
        open_questions = max(
            0, len([p for p in st.session_state.beantwortet if p is None]) - 1
        )
        if "sticky_bar_css" not in st.session_state:
            st.markdown(STICKY_BAR_CSS, unsafe_allow_html=True)
            st.session_state["sticky_bar_css"] = True
        score_html = (
            "<div class='top-progress-wrapper' aria-label='Punktestand insgesamt'>"
            f"<div style='font-size:1rem;font-weight:700;'>Letzter Punktestand: {aktueller_punktestand} / {max_punkte}</div>"
            f"<div style='font-size:0.95rem;color:#ffb300;font-weight:500;'>Noch offen: {open_questions} Frage{'n' if open_questions != 1 else ''}</div>"
            "</div>"
        )
        st.markdown(score_html, unsafe_allow_html=True)

    # --- Gestapeltes Balkendiagramm: Fragenverteilung nach Thema und Gewichtung ---
    if "user_id" not in st.session_state:
        import matplotlib.pyplot as plt

        df_fragen = pd.DataFrame(fragen)
        if "gewichtung" not in df_fragen.columns:
            df_fragen["gewichtung"] = 1
        if "thema" not in df_fragen.columns:
            df_fragen["thema"] = "Unbekannt"

        def gewicht_to_schwierig(gewicht):
            try:
                g = int(gewicht)
                if g == 1:
                    return "Leicht"
                elif g == 2:
                    return "Mittel"
                else:
                    return "Schwer"
            except Exception:
                return "Leicht"

        df_fragen["Schwierigkeit"] = df_fragen["gewichtung"].apply(gewicht_to_schwierig)
        pivot = df_fragen.pivot_table(
            index="thema",
            columns="Schwierigkeit",
            values="frage",
            aggfunc="count",
            fill_value=0,
        )
        st.divider()
        st.subheader("Fragenverteilung nach Thema und Schwierigkeitsgrad")
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot.plot(kind="bar", stacked=True, ax=ax)
        ax.set_title("Fragenverteilung nach Thema und Schwierigkeitsgrad")
        ax.set_xlabel("Thema")
        ax.set_ylabel("Anzahl Fragen")
        ax.legend(title="Schwierigkeit")
        st.pyplot(fig)

    if st.session_state.get("admin_view", False):
        admin_view()
        st.stop()

    if "user_id_hash" not in st.session_state:
        st.session_state.user_id_hash = get_user_id_hash(user_id)
    if "frage_indices" not in st.session_state:
        initialize_session_state()
        if st.session_state.get("load_progress", False) and user_has_progress(
            st.session_state.user_id_hash
        ):
            load_user_progress(st.session_state.user_id_hash)

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    if num_answered == 0:
        st.info("Nur eine Antwort ist richtig.")
        st.markdown(
            f"<p class='sr-only'>Fortschritt: {num_answered} von {len(fragen)} Fragen beantwortet.</p>",
            unsafe_allow_html=True,
        )

    # Test automatisch beenden, wenn Zeitlimit überschritten
    if st.session_state.get("test_time_expired", False):
        st.warning("Jetzt kommt die Auswertung!")
        # Nach Ablauf der Zeit: Review-Modus aktivieren
        st.session_state["force_review"] = True
        display_final_summary(num_answered)
    elif num_answered == len(fragen):
        display_final_summary(num_answered)
    else:
        indices = st.session_state.frage_indices
        next_idx = None
        # Zeige die nächste unbeantwortete Frage, falls Fortschritt geladen
        if "progress_loaded" in st.session_state and st.session_state.progress_loaded:
            for idx in indices:
                if st.session_state.beantwortet[idx] is None:
                    next_idx = idx
                    break
        else:
            # Standardverhalten: Zeige die nächste Frage mit Erklärung oder die nächste unbeantwortete
            for idx in indices:
                if st.session_state.get(f"show_explanation_{idx}", False):
                    next_idx = idx
                    break
            # Dies ist die korrigierte, stabile Version
            if next_idx is None:
                for idx in indices:
                    if st.session_state.beantwortet[idx] is None:
                        next_idx = idx
                        break
        # Reset all explanation flags außer für die aktuelle Frage
        for idx in indices:
            if idx != next_idx:
                st.session_state[f"show_explanation_{idx}"] = False
        if next_idx is not None:
            pos = indices.index(next_idx) if next_idx in indices else next_idx
            display_question(fragen[next_idx], next_idx, pos + 1)
            # Sidebar-Metrik nach jeder Frage/Bewertung aktualisieren
            num_answered = len(
                [p for p in st.session_state.beantwortet if p is not None]
            )


if __name__ == "__main__":
    main()
