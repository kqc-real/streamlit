import streamlit as st

import database
import main_view as mv
from config import AppConfig, QuestionSet


def _questions() -> QuestionSet:
    return QuestionSet(
        questions=[
            {
                "question": "1. Erste",
                "optionen": ["Richtig", "Falsch"],
                "loesung": 0,
                "gewichtung": 1,
            },
            {
                "question": "2. Zweite",
                "optionen": ["A", "B"],
                "loesung": 0,
                "gewichtung": 1,
            },
        ],
        meta={"test_duration_minutes": 30},
        source_filename="questions_demo.json",
    )


def _fresh_db(monkeypatch, tmp_path):
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)
    database.init_database()
    return db_file


def test_restore_interrupted_session_reapplies_saved_answers(monkeypatch, tmp_path):
    _fresh_db(monkeypatch, tmp_path)
    st.session_state.clear()
    database.add_user("hash-ada", "Ada")
    session_id = database.start_test_session(
        "hash-ada",
        "questions_demo.json",
        tempo="normal",
        mode="practice",
    )
    assert session_id is not None
    database.save_answer(session_id, 1, "Richtig", 1, True, confidence="sure")
    database.update_bookmarks(session_id, [2])
    token = database.ensure_session_resume_token(session_id)
    assert token

    st.session_state.clear()
    st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] = f"{session_id}.{token}"
    monkeypatch.setattr(mv, "load_questions", lambda filename, silent=True: _questions())

    assert mv.restore_interrupted_session(AppConfig()) is True
    assert st.session_state["session_id"] == session_id
    assert st.session_state["user_id"] == "Ada"
    assert st.session_state["selected_mode"] == "practice"
    assert st.session_state["frage_0_antwort"] == "Richtig"
    assert st.session_state["frage_0_beantwortet"] == 1
    assert st.session_state.get("frage_1_beantwortet") is None
    assert st.session_state["bookmarked_questions"] == [1]
    assert st.session_state["test_started"] is True
    marker = st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM]
    assert marker.startswith(f"{session_id}.")


def test_restore_legacy_session_without_token(monkeypatch, tmp_path):
    _fresh_db(monkeypatch, tmp_path)
    st.session_state.clear()
    session_id = database.start_test_session("hash-ada", "questions_demo.json", mode="exam")
    assert session_id is not None
    conn = database.get_db_connection()
    conn.execute("UPDATE test_sessions SET resume_token = NULL WHERE session_id = ?", (session_id,))
    conn.commit()
    database.save_answer(session_id, 2, "A", 0, False)

    st.session_state.clear()
    st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
    monkeypatch.setattr(mv, "load_questions", lambda filename, silent=True: _questions())

    assert mv.restore_interrupted_session(AppConfig()) is True
    assert st.session_state["frage_1_antwort"] == "A"
    marker = str(st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM])
    assert marker.startswith(f"{session_id}.")
    assert len(marker) > len(str(session_id)) + 1


def test_restore_rejects_wrong_token(monkeypatch, tmp_path):
    _fresh_db(monkeypatch, tmp_path)
    st.session_state.clear()
    session_id = database.start_test_session("hash-ada", "questions_demo.json")
    assert session_id is not None
    st.session_state.clear()
    st.query_params[mv.ACTIVE_SESSION_QUERY_PARAM] = f"{session_id}.falsch"
    monkeypatch.setattr(mv, "load_questions", lambda filename, silent=True: _questions())

    assert mv.restore_interrupted_session(AppConfig()) is False
    assert "session_id" not in st.session_state
