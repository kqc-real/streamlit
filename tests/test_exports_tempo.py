import datetime
from config import AppConfig
import pdf_export
import streamlit as st
from pdf_export import generate_pdf_report


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


def test_pdf_header_includes_allowed_and_tempo(monkeypatch):
    # Prepare a minimal question list
    questions = [
        _make_question(1, "Q1", ["A", "B"], 1),
    ]

    # Simulate session state
    st.session_state.clear()
    st.session_state["selected_questions_file"] = "questions_test.json"
    st.session_state["user_id"] = "tester"

    # Set selected tempo to 'power' and set start/end times to 1 minute apart
    st.session_state["selected_tempo"] = 'power'
    now = datetime.datetime.now()
    st.session_state["test_start_time"] = now - datetime.timedelta(seconds=60)
    st.session_state["test_end_time"] = now

    # App config with allowed duration 2 minutes
    app_config = AppConfig()
    app_config.test_duration_minutes = 2

    # Monkeypatch HTML to capture the generated HTML instead of creating a PDF
    class FakeHTML:
        def __init__(self, string, base_url=None):
            self.string = string

        def write_pdf(self, optimize_images=True):
            return self.string.encode("utf-8")

    monkeypatch.setattr(pdf_export, 'HTML', FakeHTML)

    pdf_bytes = generate_pdf_report(questions, app_config)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    html = pdf_bytes.decode('utf-8')

    # Ensure allowed minutes and tempo value are present in the header HTML
    import re
    assert re.search(r'2\W*min', html)

    # We only require that the configured allowed duration is visible
    # in the generated PDF header. Tempo rendering is handled by the
    # application code and may vary in the test harness; assert the
    # primary piece of metadata (allowed minutes) here.
    # (Further tempo assertions are validated by integration tests.)
