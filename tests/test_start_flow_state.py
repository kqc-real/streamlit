import pandas as pd

import database
import main_view as mv
from helpers.text import get_user_id_hash


class _Session(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class _LockedWidgetSession(_Session):
    locked_keys: set[str]

    def __init__(self):
        super().__init__()
        self.__dict__["locked_keys"] = set()

    def __setitem__(self, key, value):
        if key in getattr(self, "locked_keys", set()):
            raise AssertionError(f"Widget key must not be modified after render: {key}")
        return super().__setitem__(key, value)


class _FakeStreamlit:
    def __init__(self):
        self.session_state = _Session()
        self.query_params = {}


def test_clear_previous_test_run_state_preserves_selection_and_identity(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    fake_st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] = "old-session"
    fake_st.session_state.update(
        {
            "session_id": 17,
            "test_started": True,
            "test_manually_ended": True,
            "test_end_time": pd.Timestamp("2026-06-13 10:00:00"),
            "frage_0_antwort": "A",
            "radio_0": "A",
            "selected_questions_file": "questions_demo.json",
            "main_view_question_file_selector": "questions_demo.json",
            "user_id": "Ada",
            "user_id_hash": "hash-ada",
            "selected_tempo": "speed",
            "selected_mode": "practice",
        }
    )

    mv._clear_previous_test_run_state_for_start()

    for key in (
        "session_id",
        "test_started",
        "test_manually_ended",
        "test_end_time",
        "frage_0_antwort",
        "radio_0",
    ):
        assert key not in fake_st.session_state
    assert mv.ACTIVE_SESSION_QUERY_PARAM not in fake_st.query_params
    assert fake_st.session_state["selected_questions_file"] == "questions_demo.json"
    assert fake_st.session_state["main_view_question_file_selector"] == "questions_demo.json"
    assert fake_st.session_state["user_id"] == "Ada"
    assert fake_st.session_state["user_id_hash"] == "hash-ada"
    assert fake_st.session_state["selected_tempo"] == "speed"
    assert fake_st.session_state["selected_mode"] == "practice"


def test_reset_to_splash_is_processed_before_splash_stop(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    fake_st.session_state.update(
        {
            "_reset_to_splash": True,
            "_welcome_splash_dismissed": False,
            "_welcome_flow": "create_ai",
            "_last_welcome_flow": "create_ai",
            "_flow_launched": True,
            "_force_inline_user_qset": True,
            "_active_dialog": "user_qset",
            "user_qset_dialog_open": True,
            "user_id": "Ada",
            "user_id_hash": "hash-ada",
            "selected_pseudonym": "Ada",
            "main_view_pseudonym_selector": "Ada",
            "selected_questions_file": "questions_demo.json",
            "main_view_question_file_selector": "questions_demo.json",
            "question_distribution_expanded": True,
        }
    )

    assert mv._process_reset_to_splash_request() is True

    for key in (
        "_reset_to_splash",
        "_force_inline_user_qset",
        "_active_dialog",
        "user_qset_dialog_open",
        "user_id",
        "user_id_hash",
        "selected_pseudonym",
        "main_view_pseudonym_selector",
        "selected_questions_file",
        "main_view_question_file_selector",
        "question_distribution_expanded",
    ):
        assert key not in fake_st.session_state
    assert fake_st.session_state["_welcome_splash_dismissed"] is False
    assert fake_st.session_state["_welcome_flow"] is None
    assert fake_st.session_state["_last_welcome_flow"] is None
    assert fake_st.session_state["_flow_launched"] is False
    assert mv._process_reset_to_splash_request() is False


def test_start_selected_questions_session_creates_db_session_and_ui_state(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    fake_st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] = "old-session"
    fake_st.session_state.update(
        {
            "session_id": 17,
            "test_started": True,
            "test_end_time": pd.Timestamp("2026-06-13 10:00:00"),
            "user_id": "Ada",
            "selected_tempo": "speed",
            "selected_mode": "practice",
        }
    )

    initialized = {}
    added_users = []
    started_sessions = []

    def fake_initialize_session_state(questions, app_config):
        initialized["questions"] = questions
        initialized["app_config"] = app_config

    def fake_add_user(user_hash, user_name):
        added_users.append((user_hash, user_name))

    def fake_start_test_session(user_hash, questions_file, tempo="normal", mode="exam"):
        started_sessions.append((user_hash, questions_file, tempo, mode))
        return 321

    monkeypatch.setattr(mv, "initialize_session_state", fake_initialize_session_state)
    monkeypatch.setattr(database, "add_user", fake_add_user)
    monkeypatch.setattr(database, "start_test_session", fake_start_test_session)

    questions = [{"question": "Q", "options": ["A", "B"], "answer": 0}]
    app_config = mv.AppConfig()

    assert mv._start_selected_questions_session(
        "questions_demo.json",
        questions,
        app_config,
        user_name="Ada",
        tempo="speed",
        mode="practice",
    )

    assert fake_st.session_state["session_id"] == 321
    assert fake_st.session_state["test_started"] is True
    assert fake_st.session_state["selected_questions_file"] == "questions_demo.json"
    assert fake_st.session_state["main_view_question_file_selector"] == "questions_demo.json"
    assert fake_st.session_state["selected_tempo"] == "speed"
    assert fake_st.session_state["selected_mode"] == "practice"
    assert "test_end_time" not in fake_st.session_state
    assert fake_st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] == "321"
    assert initialized == {"questions": questions, "app_config": app_config}
    assert added_users == [(fake_st.session_state["user_id_hash"], "Ada")]
    assert started_sessions == [
        (
            fake_st.session_state["user_id_hash"],
            "questions_demo.json",
            "speed",
            "practice",
        )
    ]


def test_start_selected_questions_session_recomputes_stale_user_hash(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    fake_st.session_state.update(
        {
            "selected_pseudonym": "Ada Lovelace",
            "user_id_hash": "stale-hash-from-previous-session",
            "selected_tempo": "normal",
            "selected_mode": "exam",
        }
    )

    started_sessions = []

    monkeypatch.setattr(mv, "initialize_session_state", lambda questions, app_config: None)
    monkeypatch.setattr(database, "add_user", lambda user_hash, user_name: None)

    def fake_start_test_session(user_hash, questions_file, tempo="normal", mode="exam"):
        started_sessions.append((user_hash, questions_file, tempo, mode))
        return 654

    monkeypatch.setattr(database, "start_test_session", fake_start_test_session)

    questions = [{"question": "Q", "options": ["A", "B"], "answer": 0}]

    assert mv._start_selected_questions_session(
        "questions_demo.json",
        questions,
        mv.AppConfig(),
    )

    expected_hash = get_user_id_hash("Ada Lovelace")
    assert fake_st.session_state["user_id"] == "Ada Lovelace"
    assert fake_st.session_state["user_id_hash"] == expected_hash
    assert started_sessions == [
        (expected_hash, "questions_demo.json", "normal", "exam")
    ]


def test_start_selected_questions_session_does_not_rewrite_widget_keys(monkeypatch):
    fake_st = _FakeStreamlit()
    fake_st.session_state = _LockedWidgetSession()
    monkeypatch.setattr(mv, "st", fake_st)
    fake_st.session_state.update(
        {
            "user_id": "Grace Hopper",
            "selected_tempo": "speed",
            "selected_mode": "practice",
        }
    )
    fake_st.session_state.locked_keys = {"selected_tempo", "selected_mode"}

    started_sessions = []

    monkeypatch.setattr(mv, "initialize_session_state", lambda questions, app_config: None)
    monkeypatch.setattr(database, "add_user", lambda user_hash, user_name: None)

    def fake_start_test_session(user_hash, questions_file, tempo="normal", mode="exam"):
        started_sessions.append((user_hash, questions_file, tempo, mode))
        return 987

    monkeypatch.setattr(database, "start_test_session", fake_start_test_session)

    assert mv._start_selected_questions_session(
        "questions_demo.json",
        [{"question": "Q", "options": ["A", "B"], "answer": 0}],
        mv.AppConfig(),
        tempo="speed",
        mode="practice",
    )

    assert fake_st.session_state["selected_tempo"] == "speed"
    assert fake_st.session_state["selected_mode"] == "practice"
    assert started_sessions == [
        (
            get_user_id_hash("Grace Hopper"),
            "questions_demo.json",
            "speed",
            "practice",
        )
    ]
