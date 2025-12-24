import importlib
import importlib.util
import sys
import pathlib
import streamlit as st
from unittest.mock import patch

# Prefer package imports; fall back to loading by path when import fails.
try:
    config = importlib.import_module("config")
    auth = importlib.import_module("auth")
    database = importlib.import_module("database")
except Exception:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    # Ensure repo root is on sys.path so package imports (helpers, etc.) work
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # config
    cfg_path = str(repo_root / "config.py")
    spec = importlib.util.spec_from_file_location("config", cfg_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"config.py not found at {cfg_path}")
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)

    # auth
    auth_path = str(repo_root / "auth.py")
    spec = importlib.util.spec_from_file_location("auth", auth_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"auth.py not found at {auth_path}")
    auth = importlib.util.module_from_spec(spec)
    sys.modules["auth"] = auth
    spec.loader.exec_module(auth)

    # database
    db_path = str(repo_root / "database.py")
    spec = importlib.util.spec_from_file_location("database", db_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"database.py not found at {db_path}")
    database = importlib.util.module_from_spec(spec)
    sys.modules["database"] = database
    spec.loader.exec_module(database)

QuestionSet = config.QuestionSet
initialize_session_state = auth.initialize_session_state
create_tables = database.create_tables
get_db_connection = database.get_db_connection
start_test_session = database.start_test_session


def make_question_set(minutes: int = 60, count: int = 5) -> QuestionSet:
    questions = [{} for _ in range(count)]
    meta = {"test_duration_minutes": minutes}
    return QuestionSet(questions=questions, meta=meta)


def test_initialize_session_state_applies_tempo():
    # Mock compute_total_cooldown_seconds to return 0 so we verify pure tempo scaling of the base duration
    with patch('pacing_helper.compute_total_cooldown_seconds', return_value=0):
        # Normal tempo
        st.session_state.clear()
        st.session_state['selected_tempo'] = 'normal'
        qs = make_question_set(minutes=60, count=3)
        initialize_session_state(qs, app_config=None)
        assert st.session_state.test_duration_minutes == 60
        assert st.session_state.test_time_limit == 60 * 60

        # Speed (1/2)
        st.session_state.clear()
        st.session_state['selected_tempo'] = 'speed'
        qs = make_question_set(minutes=60, count=3)
        initialize_session_state(qs, app_config=None)
        assert st.session_state.test_duration_minutes == 30
        assert st.session_state.test_time_limit == 30 * 60

        # Power (1/4)
        st.session_state.clear()
        st.session_state['selected_tempo'] = 'power'
        qs = make_question_set(minutes=60, count=3)
        initialize_session_state(qs, app_config=None)
        assert st.session_state.test_duration_minutes == 15
        assert st.session_state.test_time_limit == 15 * 60


def test_start_test_session_persists_tempo():
    # Ensure tables exist
    create_tables()
    # Start a session with a specific tempo
    session_id = start_test_session('test_user_tempo', 'questions_dummy', tempo='power')
    assert session_id is not None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT tempo FROM test_sessions WHERE session_id = ?", (session_id,))
    row = cur.fetchone()
    assert row is not None
    assert row['tempo'] == 'power'
