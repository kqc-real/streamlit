from config import AppConfig
from pdf_export import generate_pdf_report
import streamlit as st


def _make_question(idx: int, text: str, options, correct_idx: int):
    return {
        "frage": f"{idx}. {text}",
        "optionen": options,
        "loesung": correct_idx,
        "erklaerung": "Kurz",
        "gewichtung": 1,
        "thema": "Test",
        "kognitive_stufe": "wissen",
    }


def test_generate_pdf_all_answered(tmp_path, monkeypatch):
    # Prepare questions
    questions = [
        _make_question(1, "Q1", ["A", "B"], 1),
        _make_question(2, "Q2", ["X", "Y"], 0),
        _make_question(3, "Q3", ["Yes", "No"], 0),
    ]

    # Simulate session state: all answered
    st.session_state.clear()
    for i, q in enumerate(questions):
        st.session_state[f"frage_{i}_beantwortet"] = q.get("gewichtung", 1)
        # store the answer text as used by pdf_export
        st.session_state[f"frage_{i}_antwort"] = q["optionen"][q["loesung"]]

    st.session_state["selected_questions_file"] = "questions_test.json"
    st.session_state["user_id"] = "tester"
    st.session_state["test_start_time"] = None

    app_config = AppConfig()

    pdf_bytes = generate_pdf_report(questions, app_config)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


def test_generate_pdf_with_unanswered_and_bookmarks(tmp_path):
    questions = [
        _make_question(1, "Alpha", ["1", "2"], 0),
        _make_question(2, "Beta", ["a", "b"], 1),
    ]

    st.session_state.clear()
    # First answered, second unanswered
    st.session_state["frage_0_beantwortet"] = questions[0].get("gewichtung", 1)
    st.session_state["frage_0_antwort"] = questions[0]["optionen"][0]
    # second remains unanswered: no keys set

    st.session_state["bookmarked_questions"] = [1]
    st.session_state["test_manually_ended"] = True
    st.session_state["selected_questions_file"] = "questions_test2.json"
    st.session_state["user_id"] = "tester2"

    app_config = AppConfig()

    pdf_bytes = generate_pdf_report(questions, app_config)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes[:4] == b"%PDF"
    # Ensure the PDF is not empty and contains at least one page
    assert len(pdf_bytes) > 800
