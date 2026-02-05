"""
Modul für Authentifizierung und Session-Management.

Verantwortlichkeiten:
- Anzeige des Login-Formulars.
- Initialisierung des `st.session_state` für einen neuen Testlauf.
- Überprüfung von Admin-Rechten.
"""
import streamlit as st
import random
import hmac
import json
from datetime import datetime
import sys

from config import AppConfig, load_scientists, QuestionSet
from i18n.context import t
from helpers.text import get_user_id_hash

def log_state(event: str):
    """Schreibt den aktuellen Session State zur Fehlersuche in eine Log-Datei."""
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"--- {event} at {datetime.now()} ---\n")
        state_copy = {}
        for k, v in st.session_state.items():
            try:
                json.dumps({k: v})
                state_copy[k] = v
            except (TypeError, OverflowError):
                state_copy[k] = f"NOT_SERIALIZABLE: {type(v)}"
        f.write(json.dumps(state_copy, indent=2, ensure_ascii=False) + "\n")

def initialize_session_state(question_set: QuestionSet, app_config: AppConfig | None = None):
    """Initialisiert den Session-State für einen neuen Testlauf."""
    streamlit_mod = sys.modules.get("streamlit", st)
    state = getattr(streamlit_mod, "session_state", st.session_state)

    def _state_set(key: str, value):
        try:
            state[key] = value
        except Exception:
            pass
        try:
            setattr(state, key, value)
        except Exception:
            pass
        try:
            state.__dict__[key] = value
        except Exception:
            pass
    # Lösche alte Test-spezifische Schlüssel, falls vorhanden
    # Dies ist wichtig, wenn ein Nutzer einen neuen Test startet, ohne die Session komplett zu beenden.
    try:
        existing_keys = list(state.keys())
    except Exception:
        try:
            existing_keys = list(getattr(state, "__dict__", {}).keys())
        except Exception:
            existing_keys = []

    for key in existing_keys:
        if key.startswith("frage_") or key in [
            "beantwortet", "frage_indices", "initial_frage_indices", "start_zeit",
            "progress_loaded", "optionen_shuffled", "answer_outcomes",
            "bookmarked_questions",
            "test_time_expired", "show_pseudonym_reminder",
            "login_attempts", "last_answered_idx", "resume_next_idx", "jump_to_idx_active"
        ]:
            del state[key]

    question_count = len(question_set)
    _state_set("beantwortet", [None] * question_count)
    frage_indices = list(range(question_count))
    
    sort_order = state.get("question_sort_order", "random")

    if sort_order == "random":
        random.shuffle(frage_indices)
    elif sort_order == "difficulty_asc":
        frage_indices.sort(key=lambda i: question_set[i].get("gewichtung", 2))
    elif sort_order == "difficulty_desc":
        frage_indices.sort(key=lambda i: question_set[i].get("gewichtung", 2), reverse=True)
    elif sort_order == "cognitive_stage":
        try:
            from pdf_export import BLOOM_STAGE_ORDER, _normalize_stage_label
            stage_map = {stage: i for i, stage in enumerate(BLOOM_STAGE_ORDER)}
            
            def get_stage_index(q_idx):
                q = question_set[q_idx]
                stage = _normalize_stage_label(q.get("kognitive_stufe"))
                return stage_map.get(stage, 99)

            frage_indices.sort(key=get_stage_index)
        except ImportError:
            # Fallback to random if pdf_export is not available
            random.shuffle(frage_indices)

    _state_set("frage_indices", frage_indices)
    _state_set("initial_frage_indices", list(frage_indices))  # Stabile Kopie für Nummerierung
    _state_set("start_zeit", None)
    _state_set("progress_loaded", False)
    _state_set("optionen_shuffled", [])
    _state_set("answer_outcomes", [])
    _state_set("skipped_questions", [])
    _state_set("bookmarked_questions", [])
    default_minutes = getattr(app_config, "test_duration_minutes", 60) if app_config else 60
    test_duration_minutes = question_set.get_test_duration_minutes(default_minutes)

    # Calculate exact total cooldown time for the question set (before tempo scaling)
    from pacing_helper import compute_total_cooldown_seconds
    from config import AppConfig
    app_cfg = AppConfig()
    per_weight_minutes = {}
    qmeta = getattr(question_set, 'meta', None)
    per_weight_raw = None
    if isinstance(qmeta, dict):
        per_weight_raw = qmeta.get('time_per_weight_minutes') or qmeta.get('time_per_weight')
    if isinstance(per_weight_raw, dict):
        for k, v in per_weight_raw.items():
            try:
                kk = int(k)
                per_weight_minutes[kk] = float(v)
            except Exception:
                continue
    if not per_weight_minutes:
        per_weight_minutes = {1: 0.5, 2: 0.75, 3: 1.0}
    
    total_cooldown_seconds = compute_total_cooldown_seconds(
        list(question_set), 
        per_weight_minutes,
        reading_cooldown_base_per_weight=app_cfg.reading_cooldown_base_per_weight,
        next_cooldown_extra_standard=app_cfg.next_cooldown_extra_standard,
        next_cooldown_extra_extended=app_cfg.next_cooldown_extra_extended
    )

    # Add cooldowns to base duration
    total_duration_minutes = test_duration_minutes + (total_cooldown_seconds / 60)

    # Apply tempo scaling to the entire duration (base + cooldowns)
    try:
        tempo = state.get('selected_tempo', 'normal')
        tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
        factor = float(tempo_factor_map.get(tempo, 1.0))
        test_duration_minutes = int(max(1, round(total_duration_minutes * factor)))
    except Exception:
        # Defensive fallback: keep the original duration if anything goes wrong
        pass

    _state_set("test_duration_minutes", test_duration_minutes)
    _state_set("test_time_limit", test_duration_minutes * 60)
    _state_set("test_time_expired", False)
    _state_set("question_set_meta", question_set.meta)
    # Track the active question set source so UI can detect set changes
    try:
        source_name = getattr(question_set, "source_filename", None) or state.get("selected_questions_file")
    except Exception:
        source_name = None
    _state_set("question_set_source", source_name)
    # Ensure pacing UI is hidden by default for a new session
    try:
        state["pacing_visible"] = False
    except Exception:
        pass

    questions = list(question_set)
    for q in questions:
        opts = list(q.get("optionen", []))
        random.shuffle(opts)
        try:
            state["optionen_shuffled"].append(opts)
        except Exception:
            # Fallback for attribute-only session_state objects
            try:
                state.optionen_shuffled.append(opts)
            except Exception:
                pass


def handle_user_session(questions: list, app_config: AppConfig) -> str | None:
    """
    Überprüft, ob ein Benutzer in der Session angemeldet ist.
    Gibt die user_id zurück, wenn ja, sonst None.
    Die UI-Logik für den Login befindet sich in `main_view.render_welcome_page`.
    """
    # log_state("Enter handle_user_session")
    # Prefer showing any post-session toast first (e.g. when a test was
    # just ended). This must run even if `user_id` is still present in
    # the session (some flows keep the login state). Previously this
    # check happened after the early-return and the toast could be
    # skipped when `user_id` existed.
    if "session_aborted" in st.session_state:
        user_name = st.session_state.get("aborted_user_id", "Unbekannt")
        score = st.session_state.get("aborted_user_score", 0)
        made_it_to_leaderboard = st.session_state.get("aborted_user_on_leaderboard", False)

        if made_it_to_leaderboard:
            # store a structured toast so it can be localized later when
            # the welcome screen renders (the UI locale may change).
            toast_struct = {
                "key": "messages.session_saved.leaderboard",
                "params": {"user": user_name, "score": score},
            }
            # show an immediate transient toast in the current runtime
            try:
                st.toast(t(toast_struct["key"]).format(**toast_struct["params"]), icon="🏆", duration=20)
            except Exception:
                pass
            # Ensure a persistent copy that the welcome page can render
            # inside its dialog so mobile users don't miss it.
            try:
                # persist the structured message (not the formatted string)
                st.session_state['post_session_toast'] = toast_struct
            except Exception:
                pass
        elif st.session_state.get("aborted_user_mode", "exam") == "exam":
            duration = st.session_state.get("aborted_user_duration", 0)
            recommended_duration_seconds = st.session_state.get("aborted_user_recommended_duration", 180)

            # Definiere die Schwellenwerte
            MIN_SCORE_FOR_LEADERBOARD = 1
            # Mindestdauer ist 20% der empfohlenen Testzeit, aber mind. 60s
            MIN_DURATION_FOR_LEADERBOARD = max(60, int(recommended_duration_seconds * 0.20))

            # Decide which reason key to use (resolve at render time)
            if score < MIN_SCORE_FOR_LEADERBOARD:
                reason_key = "messages.session_saved.reason_zero_score"
                reason_params = {}
            elif duration < MIN_DURATION_FOR_LEADERBOARD:
                # min_duration_display is the rounded minute threshold shown to users
                min_duration_display = max(1, round(MIN_DURATION_FOR_LEADERBOARD / 60))
                # recommended_minutes is the tempo-adjusted full recommended test time in minutes
                recommended_minutes = max(1, round(recommended_duration_seconds / 60)) if recommended_duration_seconds is not None else min_duration_display
                reason_key = "messages.session_saved.reason_too_short"
                reason_params = {"min_duration": min_duration_display, "recommended_minutes": recommended_minutes}
            else:
                reason_key = "messages.session_saved.reason_not_top10"
                reason_params = {}

            toast_struct = {
                "key": "messages.session_saved.saved_not_on_leaderboard",
                "params": {"user": user_name, "reason_key": reason_key, "reason_params": reason_params},
            }
            try:
                # show immediate localized transient toast when possible
                reason_text = t(reason_key).format(**reason_params) if reason_key else ""
                st.toast(t(toast_struct["key"]).format(user=user_name, reason=reason_text), icon="🏆", duration=20)
            except Exception:
                pass

        del st.session_state["session_aborted"]
        if "aborted_user_id" in st.session_state:
            del st.session_state["aborted_user_id"]
        if "aborted_user_mode" in st.session_state:
            del st.session_state["aborted_user_mode"]

    if "user_id" in st.session_state:
        # log_state(f"User '{st.session_state.user_id}' found in session_state")
        return st.session_state.user_id

    # log_state("Exit handle_user_session without login")
    return None


def is_admin_user(user_id: str, app_config: AppConfig) -> bool:
    """Prüft, ob der aktuelle Nutzer ein Admin ist."""
    return user_id.casefold() == app_config.admin_user.casefold()


def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    """
    Prüft den eingegebenen Admin-Key.
    Nutzt `hmac.compare_digest` für einen zeitkonstanten Vergleich.
    """
    if not provided_key or not app_config.admin_key:
        return False
    return hmac.compare_digest(provided_key.encode(), app_config.admin_key.encode())
