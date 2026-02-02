import streamlit as st
from main_view import render_final_summary
from config import AppConfig
from datetime import datetime, timedelta

# Minimal dummy QuestionSet with required API
class DummyQuestions:
    def __init__(self, allowed_min=None, meta=None):
        self._allowed_min = allowed_min
        self.meta = meta or {}
    def get_test_duration_minutes(self, default):
        return self._allowed_min if self._allowed_min is not None else default
    def __len__(self):
        # Minimal length implementation so render_final_summary can
        # iterate/measure the number of questions without raising.
        return 1
    def __iter__(self):
        # Provide a minimal iterable of one placeholder question so
        # code that iterates over `questions` won't fail. Include the
        # typical fields used by rendering/score logic.
        yield {
            "frage": "1. Dummy",
            "optionen": ["A", "B"],
            "loesung": 0,
            "erklaerung": "Kurz",
            "gewichtung": 1,
            "thema": "Test",
            "kognitive_stufe": "wissen",
        }

# Monkeypatch streamlit display functions to print to stdout so we can
# observe messages when running outside `streamlit run`.
try:
    st._orig_info = getattr(st, 'info', None)
    st._orig_header = getattr(st, 'header', None)
except Exception:
    st._orig_info = None
    st._orig_header = None

def _print_info(msg):
    print("INFO:", msg)

def _print_header(msg):
    print("HEADER:", msg)

st.info = _print_info
st.header = _print_header

# Prepare session state: select 'power' tempo and a short test (54s)
st.session_state.clear()
st.session_state['selected_tempo'] = 'power'
now = datetime.utcnow()
st.session_state['test_start_time'] = now - timedelta(seconds=54)
st.session_state['test_end_time'] = now
# ensure flags
st.session_state['test_manually_ended'] = False
st.session_state['test_time_expired'] = False

# Create dummy app config and question set with base allowed 10 minutes
app_cfg = AppConfig()
app_cfg.test_duration_minutes = 10
questions = DummyQuestions(allowed_min=10, meta={})

print("Running render_final_summary with selected_tempo=power and allowed_min=10")
try:
    render_final_summary(questions, app_cfg)
    print("render_final_summary executed")
except Exception as e:
    print("render_final_summary raised:", e)

# Restore originals (best-effort)
if st._orig_info is not None:
    st.info = st._orig_info
if st._orig_header is not None:
    st.header = st._orig_header
