"""
MC-Test Data Science
-------------------------------------------------
Lehrbeispiel für Multiple-Choice-Tests mit Streamlit.
Autor: kqc
"""

# Standardbibliotheken
import os
import csv
import time
import json
import random
import hashlib
from datetime import datetime
from typing import List, Dict


# Drittanbieter-Bibliotheken
import streamlit as st
import pandas as pd


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

# Force dark mode via theme config
st.markdown(
    """
    <style>
    body, .main, .block-container, .stApp {
        background-color: #181818 !important;
        color: #e0e0e0 !important;
    }
    .sidebar .sidebar-content {
        background-color: #222 !important;
        color: #e0e0e0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
STICKY_BAR_CSS = """
<style>
.top-progress-wrapper{
    position:fixed;
    top:0;left:0;width:100%;
    z-index:1000;
    background:rgba(0,0,0,0.05);
    backdrop-filter:blur(4px);
    padding:4px 12px;
}
.top-progress-bar{
    height:8px;
    border-radius:4px;
    background:#ddd;
    overflow:hidden;
}
.top-progress-fill{
    height:100%;
    background:linear-gradient(90deg,#4b9fff,#0073e6);
    transition:width .3s;
}
body{margin-top:60px;}
@media (prefers-reduced-motion: reduce){
    .top-progress-fill{transition:none}
}
</style>
"""


def get_rate_limit_seconds() -> int:
    """Liefert die minimale Wartezeit zwischen Antworten (Sekunden)."""
    try:
        val = st.secrets.get("MC_TEST_MIN_SECONDS_BETWEEN", None)
        if val is None:
            val = os.getenv("MC_TEST_MIN_SECONDS_BETWEEN", "0")
        return int(val)
    except Exception:
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
    css_parts = [
        ".sr-only{position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;}"
    ]
    if st.session_state.get("high_contrast"):
        css_parts.append(
            "body,.stApp{background:#000 !important;color:#fff !important;}h1,h2,h3,h4,h5,h6{color:#fff !important;}"
        )
    if st.session_state.get("large_text"):
        css_parts.append(
            "html,body,.stMarkdown p,.stRadio label,label,div{font-size:1.05rem !important;}"
        )
    if css_parts:
        st.markdown(f"<style>{''.join(css_parts)}</style>", unsafe_allow_html=True)


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
            file_exists_and_not_empty = (
                os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0
            )
            with open(LOGFILE, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                if not file_exists_and_not_empty:
                    writer.writeheader()
                writer.writerow(row)
            st.session_state[dup_key] = True
            if min_delta > 0:
                st.session_state["last_answer_ts"] = time.time()
            return
        except IOError as e:
            attempt += 1
            if attempt >= MAX_SAVE_RETRIES:
                st.error(f"Konnte Antwort nicht speichern (Versuche={attempt}): {e}")
            else:
                time.sleep(0.1 * attempt)


def display_question(frage_obj: dict, frage_idx: int, anzeige_nummer: int) -> None:
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
            if st.button("Nächste Frage!"):
                st.session_state[f"show_explanation_{frage_idx}"] = False
                st.rerun()


@st.cache_data
def calculate_leaderboard() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOGFILE)
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
        completed_df = agg_df[agg_df["Anzahl_Antworten"] >= FRAGEN_ANZAHL].copy()
        if completed_df.empty:
            return pd.DataFrame()
        leaderboard = completed_df.sort_values(by=["Punkte"], ascending=[False])
        leaderboard = leaderboard[["Pseudonym", "Punkte"]].head(5)
        leaderboard.reset_index(drop=True, inplace=True)
        leaderboard.insert(0, "Platz", leaderboard.index + 1)
        return leaderboard
    except Exception:
        return pd.DataFrame()


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
        prozent = aktueller_punktestand / len(fragen) if len(fragen) > 0 else 0
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
    user_is_admin = (
        not admin_user_cfg or st.session_state.get("user_id") == admin_user_cfg
    ) and st.session_state.get("admin_view", False)
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


def display_final_summary(num_answered: int) -> None:
    # Review-Modus auch bei abgelaufener Zeit anzeigen
    if num_answered != len(fragen) and not st.session_state.get(
        "test_time_expired", False
    ):
        return
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    if scoring_mode == "positive_only":
        aktueller_punktestand = sum([1 for p in st.session_state.beantwortet if p == 1])
    else:
        aktueller_punktestand = sum(
            [p for p in st.session_state.beantwortet if p is not None]
        )
    prozent = aktueller_punktestand / len(fragen) if len(fragen) > 0 else 0
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
                "**Noch Luft nach oben. Schau dir die Erklärungen zu den falschen Antworten nochmal an!** 🔍",
            )
    else:
        if aktueller_punktestand < 0:
            emoji = "🫠"
            quote = (
                f"**Endstand: {aktueller_punktestand} von {len(fragen)} Punkten.**  "
                "Das war... kreativ! 😅  "
                "Manchmal ist der Weg das Ziel. Schau dir die Erklärungen an und hol dir beim nächsten Mal den Highscore! 🚀"
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
                "**Ein paar Sachen sind noch offen. Schau dir die Erklärungen zu den falschen Antworten nochmal an!** 🔍",
            )
    st.success(
        f"### {emoji} Endstand: {int(prozent * 100)} % richtig"
    )
    if quote:
        st.markdown(quote)
    # Review-Modus Toggle
    st.divider()
    st.subheader("🧐 Review")
    # Nur einmal Review-Modus anzeigen
    show_review = st.checkbox("Alle Fragen des Tests anzeigen", key="review_mode")
    if show_review:
        filter_wrong = st.checkbox(
            "Nur falsch beantwortete Fragen anzeigen",
            value=True,
            key="review_only_wrong",
        )
        # Reset active_review_idx if filter changes
        if (
            "last_filter_wrong" not in st.session_state
            or st.session_state.last_filter_wrong != filter_wrong
        ):
            st.session_state.active_review_idx = 0
            st.session_state.last_filter_wrong = filter_wrong
        # Track which review index is open
        if "active_review_idx" not in st.session_state:
            st.session_state.active_review_idx = 0
        # Find all indices to show
        indices_to_show = []
        for i, frage in enumerate(fragen):
            user_val = st.session_state.get(f"frage_{i}")
            korrekt = frage["optionen"][frage["loesung"]]
            if filter_wrong:
                # Nur falsch beantwortete Fragen, aber keine unbeantworteten
                if user_val is None:
                    continue
                if user_val == korrekt:
                    continue
                indices_to_show.append(i)
            else:
                indices_to_show.append(i)
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
                # Zeige im Review-Modus die korrekte Fragennummer
                st.markdown(f"### Frage {idx + 1} von {FRAGEN_ANZAHL}")
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
                if st.button("Weiter", key=f"review_next_{idx}"):
                    # Move to next review index
                    if st.session_state.active_review_idx < len(indices_to_show) - 1:
                        st.session_state.active_review_idx += 1
                    else:
                        st.session_state.active_review_idx = 0
                    st.rerun()


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
                "Mit diesem Namen hast du den Test schon gemacht! Dein Ergebnis bleibt gespeichert – nochmal starten geht leider nicht. Aber du kannst alles nochmal anschauen und lernen. 🚀"
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
        import plotly.io as pio

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
