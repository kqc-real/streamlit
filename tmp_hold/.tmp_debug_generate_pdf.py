import datetime
import streamlit as st
from config import AppConfig
import pdf_export
from pdf_export import generate_pdf_report

# Prepare questions
questions = [
    {"frage":"1. Q1","optionen":["A","B"],"loesung":1,"erklaerung":"Kurz","gewichtung":1,"thema":"Test","kognitive_stufe":"wissen"}
]

# session state
try:
    st.session_state.clear()
except Exception:
    st.session_state = {}

st.session_state['selected_questions_file'] = 'questions_test.json'
st.session_state['user_id'] = 'tester'
st.session_state['selected_tempo'] = 'power'
now = datetime.datetime.now()
st.session_state['test_start_time'] = now - datetime.timedelta(seconds=60)
st.session_state['test_end_time'] = now

app_config = AppConfig()
app_config.test_duration_minutes = 2

class FakeHTML:
    def __init__(self, string, base_url=None):
        self.string = string
    def write_pdf(self, optimize_images=True):
        return self.string.encode('utf-8')

pdf_export.HTML = FakeHTML
pdf_bytes = generate_pdf_report(questions, app_config)
html = pdf_bytes.decode('utf-8')
print(html)
