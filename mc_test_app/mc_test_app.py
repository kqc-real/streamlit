import os
import csv
import time
import hashlib
import random
import json
from datetime import datetime

import streamlit as st
import pandas as pd

# Optional: .env laden, falls vorhanden (macht python-dotenv-Abhängigkeit sinnvoll)
try:  # pragma: no cover - trivial import
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:  # pragma: no cover
    pass

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="MC-Test: Data Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- KONSTANTEN & FRAGENKATALOG ---
LOGFILE = os.path.join(os.path.dirname(__file__), "mc_test_answers.csv")
FIELDNAMES = [
    'user_id_hash', 'user_id_display', 'frage_nr', 'frage',
    'antwort', 'richtig', 'zeit'
]
FRAGEN_ANZAHL = 50
DISPLAY_HASH_LEN = 10  # Länge des Hash-Prefix für Anzeige (Pseudonymisierung)


def _load_fragen():
    """Lädt Fragen aus externer JSON-Datei (questions.json)."""
    questions_path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(questions_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("questions.json muss eine Liste enthalten")
        return data
    except Exception as e:
        st.error(f"Konnte questions.json nicht laden: {e}")
        return []


fragen = _load_fragen()
FRAGEN_ANZAHL = len(fragen) or FRAGEN_ANZAHL


@st.cache_data
def get_user_id_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()


def initialize_session_state():
    st.session_state.beantwortet = [None] * len(fragen)
    st.session_state.frage_indices = list(range(len(fragen)))
    random.shuffle(st.session_state.frage_indices)
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False


def _duration_to_str(x):
    if pd.isna(x):
        return ''
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def user_has_progress(user_id_hash: str) -> bool:
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return False
        df = pd.read_csv(LOGFILE, dtype={'user_id_hash': str})
        return not df[df['user_id_hash'] == user_id_hash].empty
    except Exception:
        return False


def reset_user_answers(user_id_hash: str) -> None:
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
        df = pd.read_csv(LOGFILE)
        df['zeit'] = pd.to_datetime(df['zeit'], errors='coerce')
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
    row = {
        'user_id_hash': user_id_hash,
        'user_id_display': user_id_display,
        'frage_nr': frage_nr,
        'frage': frage_obj['frage'],
        'antwort': antwort,
        'richtig': punkte,
        'zeit': datetime.now().isoformat(timespec='seconds'),
    }
    try:
        file_exists_and_not_empty = (
            os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0
        )
        with open(LOGFILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            if not file_exists_and_not_empty:
                writer.writeheader()
            writer.writerow(row)
    except IOError as e:
        st.error(f"Konnte Antwort nicht speichern: {e}")


def display_question(frage_obj: dict, frage_idx: int, anzeige_nummer: int) -> None:
    frage_text = frage_obj['frage'].split('.', 1)[1].strip()
    with st.container(border=True):
        st.markdown(f"### Frage {anzeige_nummer}")
        st.markdown(f"**{frage_text}**")
        is_disabled = st.session_state.beantwortet[frage_idx] is not None
        try:
            gespeicherte_antwort = st.session_state.get(f"frage_{frage_idx}")
            antwort_index = (
                frage_obj["optionen"].index(gespeicherte_antwort)
                if gespeicherte_antwort else None
            )
        except (ValueError, TypeError):
            antwort_index = None
        antwort = st.radio(
            "Antwort auswählen:",
            options=frage_obj["optionen"],
            key=f"frage_{frage_idx}",
            index=antwort_index,
            disabled=is_disabled,
            label_visibility="collapsed",
        )
        if antwort and not is_disabled:
            if st.session_state.start_zeit is None:
                st.session_state.start_zeit = datetime.now()
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
            if richtig:
                st.toast("Richtig! 🚀", icon="✅")
                st.balloons()
            else:
                st.toast("Leider falsch.", icon="❌")
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
    if num_answered == len(fragen):
        st.sidebar.success("✅ Test abgeschlossen!")
    st.sidebar.header("🏆 Bestenliste")
    leaderboard_df = calculate_leaderboard()
    if leaderboard_df.empty:
        st.sidebar.info("Noch keine abgeschlossenen Tests.")
    else:
        st.sidebar.dataframe(leaderboard_df)
    st.sidebar.divider()
    if 'only_unanswered' not in st.session_state:
        st.session_state['only_unanswered'] = False
    st.sidebar.checkbox(
        "Nur unbeantwortete Fragen anzeigen",
        key="only_unanswered",
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
    if prozent == 1.0:
        emoji, quote = (
            "🌟🥇",
            "**Perfekt! Hervorragende Leistung! Alle Fragen richtig beantwortet.**",
        )
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


def handle_user_session():
    st.sidebar.header("👤 Nutzerkennung")
    if 'user_id' in st.session_state:
        st.sidebar.success(
            f"Angemeldet als: **{st.session_state.user_id}**"
        )
        current_hash = (
            st.session_state.get('user_id_hash') or
            get_user_id_hash(st.session_state.user_id)
        )
        has_progress = user_has_progress(current_hash)
        if has_progress:
            if 'load_progress' not in st.session_state:
                st.session_state['load_progress'] = True
            st.sidebar.checkbox(
                "Fortschritt laden (falls vorhanden)",
                key="load_progress",
            )
        else:
            st.session_state['load_progress'] = False
        st.sidebar.divider()
        st.sidebar.subheader("🔐 Admin")
        admin_key_env = os.getenv("MC_TEST_ADMIN_KEY", "")
        hint = "(ENV nicht gesetzt)" if not admin_key_env else ""
        st.sidebar.caption(f"Admin-Key {hint}")
        admin_key_input = st.sidebar.text_input(
            "Admin-Schlüssel", type="password", key="admin_key_input"
        )
        is_admin = (
            (bool(admin_key_env) and admin_key_input == admin_key_env) or
            (not admin_key_env and admin_key_input != "")
        )
        if 'admin_view' not in st.session_state:
            st.session_state['admin_view'] = False
        st.sidebar.checkbox(
            "Admin-Ansicht anzeigen", key="admin_view",
            disabled=not is_admin,
            help=(
                "Bitte gültigen Admin-Schlüssel eingeben."
                if not is_admin else None
            ),
        )
        if st.sidebar.button("Antworten dieses Nutzers zurücksetzen"):
            reset_user_answers(current_hash)
            st.sidebar.success(
                "Antworten zurückgesetzt. Neuer Durchlauf gestartet."
            )
            st.rerun()
        if st.sidebar.button("Ausloggen & Nutzer wechseln"):
            current_input = st.session_state.get('user_id_input', '')
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.user_id_input = current_input
            st.rerun()
        return st.session_state.user_id
    user_input = st.sidebar.text_input(
        "Bitte gib ein Pseudonym ein:", key="user_id_input"
    )
    if st.sidebar.button("Test starten / Nutzer wechseln"):
        if user_input:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['user_id'] = user_input.strip()
            st.session_state['load_progress'] = True
            st.rerun()
        else:
            st.sidebar.error("Bitte gib zuerst ein Pseudonym ein.")
    st.warning(
        "Bitte gib im Seitenmenü ein Pseudonym ein und starte den Test."
    )
    st.stop()


def main():
    st.title("📝 MC-Test: Data Analytics & Big Data")
    user_id = handle_user_session()
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
    st.info(
        "**Hinweis:** Wähle die beste Antwort. Einmal beantwortete Fragen sind "
        "final. Viel Erfolg!"
    )
    num_answered = len(
        [p for p in st.session_state.beantwortet if p is not None]
    )
    if num_answered == len(fragen):
        display_final_summary(num_answered)
    else:
        quiz_container = st.container()
        only_unanswered = st.session_state.get('only_unanswered', False)
        indices = st.session_state.frage_indices
        if only_unanswered:
            indices = [
                idx for idx in indices
                if st.session_state.beantwortet[idx] is None
            ]
        with quiz_container:
            for i, q_idx in enumerate(indices):
                display_question(fragen[q_idx], q_idx, i + 1)
    display_sidebar_metrics(num_answered)


if __name__ == "__main__":
    main()
