
"""
MC-Test App für Data Analytics & Big Data
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
    page_title="MC-Test: Data Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- Konstanten -----------------------------------
LOGFILE = os.path.join(os.path.dirname(__file__), "mc_test_answers.csv")
FIELDNAMES = [
    'user_id_hash', 'user_id_display', 'frage_nr', 'frage',
    'antwort', 'richtig', 'zeit'
]
FRAGEN_ANZAHL = 50  # Fallback (wird durch echte Anzahl überschrieben)
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
        return int(os.getenv("MC_TEST_MIN_SECONDS_BETWEEN", "0"))
    except ValueError:
        return 0


def _load_fragen() -> List[Dict]:
    """Lädt die Fragen aus der JSON-Datei."""
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"Konnte questions.json nicht laden: {e}")
        return []


fragen = _load_fragen()
FRAGEN_ANZAHL = len(fragen) or FRAGEN_ANZAHL


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
    for q in fragen:
        opts = list(q.get('optionen', []))
        random.shuffle(opts)
        st.session_state.optionen_shuffled.append(opts)


def _duration_to_str(x):
    """Formatiert eine Zeitspanne als mm:ss."""
    if pd.isna(x):
        return ''
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def user_has_progress(user_id_hash: str) -> bool:
    """Prüft, ob für den Nutzer bereits Fortschritt existiert."""
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return False
        df = pd.read_csv(
            LOGFILE,
            dtype={'user_id_hash': str},
            on_bad_lines='skip'
        )
        return not df[df['user_id_hash'] == user_id_hash].empty
    except Exception:
        return False


def reset_user_answers(user_id_hash: str) -> None:
    """Setzt alle Antworten des Nutzers zurück und initialisiert den Session-State neu."""
    try:
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            df = pd.read_csv(LOGFILE, dtype={'user_id_hash': str})
            df = df[df['user_id_hash'] != user_id_hash]
            df.to_csv(LOGFILE, index=False, columns=FIELDNAMES)
    except Exception as e:
        st.error(f"Konnte Antworten nicht zurücksetzen: {e}")

    keys_to_keep = {'user_id', 'user_id_input', 'user_id_hash', 'load_progress'}
    for key in list(st.session_state.keys()):
        if (
            key not in keys_to_keep and (
                key.startswith('frage_') or key in {
                    'beantwortet', 'frage_indices', 'start_zeit', 'progress_loaded'
                }
            )
        ):
            del st.session_state[key]
    initialize_session_state()


def load_all_logs() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines='skip')
        # Spalten normalisieren (fehlende hinzufügen, unerwartete verwerfen)
        missing = [c for c in FIELDNAMES if c not in df.columns]
        for c in missing:
            df[c] = ''
        df = df[[c for c in FIELDNAMES if c in df.columns]]
        df['zeit'] = pd.to_datetime(df['zeit'], errors='coerce')
        # Korrekte Typisierung / Validierung
        df['richtig'] = pd.to_numeric(df['richtig'], errors='coerce')
        # Frage-Nr extrahieren/validieren: muss int oder numerisch konvertierbar sein
        df['frage_nr'] = pd.to_numeric(df['frage_nr'], errors='coerce')
        # Entferne Zeilen mit fehlenden Pflichtfeldern oder fehlenden/ungültigen Werten
        df = df.dropna(subset=['user_id_hash', 'user_id_display', 'frage_nr', 'frage', 'antwort', 'richtig', 'zeit'])
        # Filter: richtig nur -1,0,1 erlaubt (0 selten, aber toleriert), realistisch 1 oder -1
        df = df[df['richtig'].isin([-1, 0, 1])]
        # Pflichtfelder non-empty
        for col in ['user_id_hash', 'frage', 'antwort']:
            df = df[df[col].astype(str).str.strip() != '']
        # Nach Säuberung wieder frage_nr als int ausgeben (falls benötigt)
        try:
            df['frage_nr'] = df['frage_nr'].astype(int)
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
    except Exception:
        return pd.DataFrame()


def admin_view():
    st.title("🔐 Admin: Leaderboard & Logs")
    df_logs = load_all_logs()
    if df_logs.empty:
        st.info("Keine Daten vorhanden.")
        return
    tabs = st.tabs(["Top 5 (abgeschlossen)", "Alle Teilnahmen", "Rohdaten"])
    with tabs[0]:
        top_df = calculate_leaderboard()
        if top_df.empty:
            st.info("Noch keine abgeschlossenen Tests.")
        else:
            st.dataframe(top_df, use_container_width=True)
            csv_bytes = top_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "CSV herunterladen (Top 5)", csv_bytes,
                file_name="leaderboard_top5.csv",
                mime="text/csv",
            )
    with tabs[1]:
        all_df = calculate_leaderboard_all(df_logs)
        if all_df.empty:
            st.info("Keine Einträge.")
        else:
            st.dataframe(all_df, use_container_width=True)
            csv_bytes = all_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "CSV herunterladen (Alle)", csv_bytes,
                file_name="leaderboard_all.csv",
                mime="text/csv",
            )
    with tabs[2]:
        show_cols = [
            'user_id_display', 'user_id_hash', 'frage_nr',
            'antwort', 'richtig', 'zeit',
        ]
        df_show = df_logs.copy()
        missing = [c for c in show_cols if c not in df_show.columns]
        for c in missing:
            df_show[c] = ''
        df_show = df_show[show_cols].sort_values('zeit', ascending=True)
        st.dataframe(df_show, use_container_width=True, height=400)
        csv_bytes = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            "CSV herunterladen (Rohdaten)", csv_bytes,
            file_name="mc_test_raw_logs.csv",
            mime="text/csv",
        )


def load_user_progress(user_id_hash: str) -> None:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return
    try:
        df = pd.read_csv(LOGFILE, dtype={'user_id_hash': str})
        user_df = df[df['user_id_hash'] == user_id_hash]
        if user_df.empty:
            return
        st.session_state.start_zeit = pd.to_datetime(user_df['zeit']).min()
        for _, row in user_df.iterrows():
            frage_nr = int(row['frage_nr'])
            original_idx = next(
                (i for i, f in enumerate(fragen) if f['frage'].startswith(f"{frage_nr}.")),
                None,
            )
            if original_idx is not None:
                st.session_state.beantwortet[original_idx] = int(row['richtig'])
                st.session_state[f"frage_{original_idx}"] = row['antwort']
    except Exception as e:
        st.error(f"Fehler beim Laden des Fortschritts: {e}")


def save_answer(user_id: str, user_id_hash: str, frage_obj: dict, antwort: str, punkte: int) -> None:
    frage_nr = int(frage_obj['frage'].split('.')[0])
    # Anzeige-Name ist ein gekürzter Hash-Prefix, kein Klartext-Pseudonym
    user_id_display = user_id_hash[:DISPLAY_HASH_LEN]
    # Throttling: Mindestabstand zwischen zwei Antworten
    min_delta = get_rate_limit_seconds()
    if min_delta > 0:
        last_ts = st.session_state.get('last_answer_ts')
        now_ts = time.time()
        if last_ts and (now_ts - last_ts) < min_delta:
            remaining = int(min_delta - (now_ts - last_ts))
            # Zeitpunkt für nächsten erlaubten Save speichern (für Countdown-Anzeige)
            st.session_state['next_allowed_time'] = last_ts + min_delta
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
                usecols=['user_id_hash', 'frage_nr'],
                dtype={'user_id_hash': str, 'frage_nr': str},
                on_bad_lines='skip'
            )
            mask = (
                (partial['user_id_hash'] == user_id_hash) &
                (partial['frage_nr'] == str(frage_nr))
            )
            if not partial[mask].empty:
                st.session_state[dup_key] = True
                return
        except Exception:
            pass
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
            st.session_state[dup_key] = True
            if min_delta > 0:
                st.session_state['last_answer_ts'] = time.time()
            return
        except IOError as e:
            attempt += 1
            if attempt >= MAX_SAVE_RETRIES:
                st.error(f"Konnte Antwort nicht speichern (Versuche={attempt}): {e}")
            else:
                time.sleep(0.1 * attempt)


def display_question(frage_obj: dict, frage_idx: int, anzeige_nummer: int) -> None:
    frage_text = frage_obj['frage'].split('.', 1)[1].strip()
    with st.container(border=True):
        st.markdown(f"### Frage {anzeige_nummer} von {len(fragen)}")
        st.markdown(f"**{frage_text}**")
        is_disabled = st.session_state.beantwortet[frage_idx] is not None
        try:
            gespeicherte_antwort = st.session_state.get(f"frage_{frage_idx}")
            optionen_anzeige = st.session_state.optionen_shuffled[frage_idx]
            antwort_index = (
                optionen_anzeige.index(gespeicherte_antwort)
                if gespeicherte_antwort else None
            )
        except (ValueError, TypeError):
            antwort_index = None
            optionen_anzeige = st.session_state.optionen_shuffled[frage_idx]
        antwort = st.radio(
            "Antwort auswählen:",
            options=optionen_anzeige,
            key=f"frage_{frage_idx}",
            index=antwort_index,
            disabled=is_disabled,
            label_visibility="collapsed",
        )
        if antwort and not is_disabled:
            if st.session_state.start_zeit is None:
                st.session_state.start_zeit = datetime.now()
            # Korrektheitsprüfung gegen ursprüngliche richtige Option
            richtig = (antwort == frage_obj["optionen"][frage_obj["loesung"]])
            punkte = 1 if richtig else -1
            st.session_state.beantwortet[frage_idx] = punkte
            save_answer(
                st.session_state.user_id,
                st.session_state.user_id_hash,
                frage_obj,
                antwort,
                punkte,
            )
            reduce_anim = st.session_state.get('reduce_animations', False)
            if richtig:
                st.toast("Richtig! ✅", icon="✅")
                if not reduce_anim:
                    st.balloons()
            else:
                st.toast("Leider falsch. ❌", icon="❌")
            time.sleep(1.5)
            st.rerun()
        if is_disabled:
            if st.session_state.beantwortet[frage_idx] == 1:
                st.success("Ihre Antwort ist richtig! (+1 Punkt)")
            else:
                st.error(
                    "Ihre Antwort war leider falsch (-1 Punkt). Die korrekte Antwort "
                    f"lautet: **{frage_obj['optionen'][frage_obj['loesung']]}**"
                )


@st.cache_data
def calculate_leaderboard() -> pd.DataFrame:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOGFILE)
        df['richtig'] = pd.to_numeric(df['richtig'], errors='coerce')
        df['zeit'] = pd.to_datetime(df['zeit'], errors='coerce')
        agg_df = df.groupby('user_id_hash').agg(
            Punkte=('richtig', 'sum'),
            Anzahl_Antworten=('frage_nr', 'count'),
            Startzeit=('zeit', 'min'),
            Endzeit=('zeit', 'max'),
            Anzeige_Name=('user_id_display', 'first')
        ).reset_index()
        completed_df = agg_df[agg_df['Anzahl_Antworten'] >= FRAGEN_ANZAHL].copy()
        if completed_df.empty:
            return pd.DataFrame()
        completed_df['Dauer'] = completed_df['Endzeit'] - completed_df['Startzeit']
        leaderboard = completed_df.sort_values(
            by=['Punkte', 'Dauer'], ascending=[False, True]
        )
        leaderboard['Zeit'] = leaderboard['Dauer'].apply(_duration_to_str)
        leaderboard = leaderboard[['Anzeige_Name', 'Punkte', 'Zeit']].head(5)
        leaderboard.rename(columns={'Anzeige_Name': 'Name'}, inplace=True)
        leaderboard.reset_index(drop=True, inplace=True)
        leaderboard.index += 1
        return leaderboard
    except Exception:
        return pd.DataFrame()


def display_sidebar_metrics(num_answered: int) -> None:
    st.sidebar.header("📊 Fortschritt & Score")
    st.sidebar.progress(num_answered / len(fragen))
    aktueller_punktestand = sum(
        [p for p in st.session_state.beantwortet if p is not None]
    )
    st.sidebar.metric(
        "Aktueller Punktestand",
        f"{aktueller_punktestand} / {len(fragen)}",
    )
    if st.session_state.start_zeit and num_answered < len(fragen):
        elapsed_time = datetime.now() - st.session_state.start_zeit
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        st.sidebar.metric("⏳ Bisherige Zeit", f"{minutes:02d}:{seconds:02d}")
    # Countdown für nächstmögliche Antwort (Throttling)
    next_allowed = st.session_state.get('next_allowed_time')
    if next_allowed:
        now = time.time()
        if now < next_allowed:
            remaining = int(next_allowed - now)
            st.sidebar.info(f"Wartezeit bis nächste Antwort: {remaining}s")
        else:
            # Abgelaufen -> entfernen
            st.session_state.pop('next_allowed_time', None)
    if num_answered == len(fragen):
        st.sidebar.success("✅ Test abgeschlossen!")
    leaderboard_df = calculate_leaderboard()
    admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    user_is_admin = (
        (not admin_user_cfg or st.session_state.get('user_id') == admin_user_cfg)
        and st.session_state.get('admin_view', False)
    )
    if not leaderboard_df.empty:
        st.sidebar.header("🏆 Bestenliste")
        st.sidebar.dataframe(leaderboard_df)
    elif user_is_admin:
        st.sidebar.info("Noch keine abgeschlossenen Tests.")
    st.sidebar.divider()
    # Persistente Einstellung für Filter nur unbeantwortete Fragen.
    # Explizit value setzen & Rückgabewert speichern, damit ein Rerun nach Antwort
    # (st.rerun) den Zustand nicht zurücksetzt.
    # Default: Nur unbeantwortete Fragen anzeigen (beim ersten Laden)
    if 'only_unanswered' not in st.session_state:
        st.session_state['only_unanswered'] = True
    st.session_state['only_unanswered'] = st.sidebar.checkbox(
        "Nur unbeantwortete Fragen anzeigen",
        value=st.session_state['only_unanswered'],
    )


def display_final_summary(num_answered: int) -> None:
    if num_answered != len(fragen):
        return
    st.header("🎉 Test abgeschlossen!")
    aktueller_punktestand = sum(
        [p for p in st.session_state.beantwortet if p is not None]
    )
    prozent = aktueller_punktestand / len(fragen) if len(fragen) > 0 else 0
    emoji, quote = "", ""
    reduce_anim = st.session_state.get('reduce_animations', False)
    if prozent == 1.0:
        emoji, quote = (
            "🌟🥇",
            "**Perfekt! Hervorragende Leistung! Alle Fragen richtig beantwortet.**",
        )
        if not reduce_anim:
            st.balloons()
            st.snow()
    elif prozent >= 0.8:
        emoji, quote = (
            "🎉👍",
            "**Sehr stark! Sie haben ein exzellentes Verständnis der Konzepte.**",
        )
    elif prozent >= 0.5:
        emoji, quote = (
            "🙂",
            "**Gut gemacht! Eine solide Grundlage ist vorhanden.**",
        )
    else:
        emoji, quote = (
            "🤔",
            "**Einige Konzepte sitzen schon. Schauen Sie sich die Erklärungen zu den falschen "
            "Antworten noch einmal an.**",
        )
    st.success(
        f"### {emoji} Endstand: {aktueller_punktestand} von {len(fragen)} Punkten"
    )
    st.markdown(quote)
    # Review-Modus Toggle
    st.divider()
    st.subheader("🔍 Review-Modus")
    show_review = st.checkbox(
        "Alle Fragen & Antworten anzeigen (Review)", value=False, key="review_mode"
    )
    if show_review:
        for idx, frage in enumerate(fragen):
            user_val = st.session_state.get(f"frage_{idx}")
            korrekt = frage["optionen"][frage["loesung"]]
            richtig = (user_val == korrekt)
            with st.expander(f"Frage {idx + 1}: {'✅' if richtig else '❌'}"):
                st.markdown(f"**{frage['frage']}**")
                if user_val is not None:
                    st.write(f"Ihre Antwort: {user_val}")
                else:
                    st.write("Ihre Antwort: —")
                if not richtig:
                    st.write(f"Korrekte Antwort: {korrekt}")
                # Optional kurze Liste aller Optionen bei Bedarf
                st.caption("Optionen:")
                for opt in frage.get('optionen', []):
                    prefix = "➡️" if opt == user_val else ("✅" if opt == korrekt else "•")
                    st.write(f"{prefix} {opt}")


def check_admin_permission(user_id: str, provided_key: str) -> bool:
    """Prüft Admin-Berechtigung basierend auf ENV-Konfiguration.

    Regeln:
    - MC_TEST_ADMIN_USER gesetzt: Nur genau dieses Pseudonym darf Admin werden.
    - MC_TEST_ADMIN_KEY gesetzt: Key muss exakt passen.
    - Wenn kein Key gesetzt ist (MC_TEST_ADMIN_KEY leer), reicht beliebige nicht-leere Eingabe,
      sofern (falls gesetzt) der Benutzername MC_TEST_ADMIN_USER entspricht.
    """
    admin_user = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    admin_key_env = os.getenv("MC_TEST_ADMIN_KEY", "")
    if admin_user and user_id != admin_user:
        return False
    if admin_key_env:
        return provided_key == admin_key_env
    # Kein Key konfiguriert -> jede nicht-leere Eingabe akzeptieren
    return provided_key != ""


def handle_user_session():
    # 1. Nutzerkennung
    st.sidebar.header("👤 Nutzerkennung")
    if 'user_id' not in st.session_state:
        def start_mc_test():
            user_id_input = st.session_state.get('user_id_input', '').strip()
            if not user_id_input:
                st.sidebar.error("Bitte ein Pseudonym eingeben.")
            else:
                st.session_state.user_id = user_id_input
                st.session_state['mc_test_started'] = True

        st.sidebar.text_input(
            "Pseudonym eingeben (frei wählbar)",
            key='user_id_input',
            on_change=start_mc_test
        )
        if not st.session_state.get('mc_test_started'):
            st.stop()
    st.sidebar.success(f"Angemeldet als: **{st.session_state.user_id}**")
    current_hash = (
        st.session_state.get('user_id_hash') or
        get_user_id_hash(st.session_state.user_id)
    )
    has_progress = user_has_progress(current_hash)
    st.session_state['load_progress'] = has_progress

    # Ensure session state is initialized before sidebar metrics
    if 'beantwortet' not in st.session_state or 'frage_indices' not in st.session_state:
        initialize_session_state()

    # 2. Fortschritt & Score direkt nach Nutzerkennung
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    display_sidebar_metrics(num_answered)

    # 3. Admin Sektion
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Admin")
    admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    user_allowed = (not admin_user_cfg) or (st.session_state.user_id == admin_user_cfg)
    if not user_allowed:
        st.sidebar.caption(
            f"Admin nur für Benutzer: {admin_user_cfg}" if admin_user_cfg else ""
        )
    if user_allowed:
        admin_key_input = st.sidebar.text_input(
            "Admin-Key", type="password", key="admin_key_input"
        )
        if not st.session_state.get('admin_view'):
            if st.sidebar.button("Admin aktivieren"):
                if check_admin_permission(st.session_state.user_id, admin_key_input):
                    st.session_state['admin_view'] = True
                    st.rerun()
                else:
                    st.sidebar.error("Admin-Berechtigung fehlgeschlagen")
        else:
            if st.sidebar.button("Admin verlassen"):
                st.session_state['admin_view'] = False
                st.rerun()
    return st.session_state.user_id


def main():
    st.title("📝 MC-Test: Data Analytics & Big Data")
    user_id = handle_user_session()

    # Sticky Progress Bar (oben)
    if 'beantwortet' in st.session_state:
        answered = len([p for p in st.session_state.beantwortet if p is not None])
        pct = (answered / len(fragen)) if fragen else 0
        if 'sticky_bar_css' not in st.session_state:
            st.markdown(STICKY_BAR_CSS, unsafe_allow_html=True)
            st.session_state['sticky_bar_css'] = True
        progress_html = (
            "<div class='top-progress-wrapper' aria-label='Fortschritt insgesamt'>"
            f"<div style='font-size:0.8rem;font-weight:600;'>Fortschritt: {answered} / "
            f"{len(fragen)} ({int(pct*100)}%)</div>"
            "<div class='top-progress-bar'>"
            f"<div class='top-progress-fill' style='width:{pct*100}%;'></div>"
            "</div></div>"
        )
        st.markdown(progress_html, unsafe_allow_html=True)

    if st.session_state.get('admin_view', False):
        admin_view()
        st.stop()

    if 'user_id_hash' not in st.session_state:
        st.session_state.user_id_hash = get_user_id_hash(user_id)
    if 'frage_indices' not in st.session_state:
        initialize_session_state()
        if (
            st.session_state.get('load_progress', False) and
            user_has_progress(st.session_state.user_id_hash)
        ):
            load_user_progress(st.session_state.user_id_hash)

    st.info("Wähle die beste Antwort. Einmal beantwortete Fragen sind final. Viel Erfolg!")

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    st.markdown(
        f"<p class='sr-only'>Fortschritt: {num_answered} von {len(fragen)} Fragen beantwortet.</p>",
        unsafe_allow_html=True,
    )

    if num_answered == len(fragen):
        display_final_summary(num_answered)
    else:
        only_unanswered = st.session_state.get('only_unanswered', False)
        indices = st.session_state.frage_indices
        if only_unanswered:
            indices = [i for i in indices if st.session_state.beantwortet[i] is None]
        for i, q_idx in enumerate(indices):
            display_question(fragen[q_idx], q_idx, i + 1)
    # Fortschritt & Score wird nur im Sidebar-Abschnitt angezeigt



if __name__ == "__main__":
    main()
