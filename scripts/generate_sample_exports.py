import os
import sys
from datetime import datetime, timedelta

# Ensure repo root is on sys.path so local modules (config, pdf_export, etc.)
# can be imported when running this script directly.
sys.path.insert(0, os.getcwd())

import streamlit as st
import pandas as pd
from config import AppConfig
import pdf_export

# Minimal DummyQuestions like in the repro script
class DummyQuestions:
    def __init__(self, allowed_min=None, meta=None):
        self._allowed_min = allowed_min
        self.meta = meta or {}
    def get_test_duration_minutes(self, default):
        return self._allowed_min if self._allowed_min is not None else default
    def __len__(self):
        return 1
    def __iter__(self):
        yield {
            "frage": "1. Dummy",
            "optionen": ["A", "B"],
            "loesung": 0,
            "erklaerung": "Kurz",
            "gewichtung": 1,
            "thema": "Test",
            "kognitive_stufe": "wissen",
        }

# Prepare session state
try:
    st.session_state.clear()
except Exception:
    # when running outside Streamlit run, session_state may behave differently
    try:
        st.session_state.update({})
    except Exception:
        pass

st.session_state['selected_tempo'] = 'power'
now = datetime.utcnow()
st.session_state['test_start_time'] = now - timedelta(seconds=54)
st.session_state['test_end_time'] = now
st.session_state['user_id'] = 'tester'
st.session_state['selected_questions_file'] = 'questions_sample.json'

# App config and questions
app_cfg = AppConfig()
app_cfg.test_duration_minutes = 10
questions = DummyQuestions(allowed_min=10, meta={})

out_dir = os.path.join(os.getcwd(), 'artifacts')
os.makedirs(out_dir, exist_ok=True)

# Generate PDF (attempt). If the environment doesn't support WeasyPrint,
# fallback to writing the generated HTML to .html so you can inspect it.
pdf_path = os.path.join(out_dir, 'sample_report.pdf')
html_path = os.path.join(out_dir, 'sample_report.html')

try:
    pdf_bytes = pdf_export.generate_pdf_report(list(questions), app_cfg)
    # generate_pdf_report returns bytes (PDF) in normal runs; if it returns
    # HTML bytes, still write to file but with .html extension.
    try:
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        print('Wrote PDF to', pdf_path)
    except Exception:
        with open(html_path, 'wb') as f:
            f.write(pdf_bytes)
        print('Wrote HTML to', html_path)
except Exception as e:
    print('PDF generation failed — writing HTML fallback. Error:', e)
    try:
        # Try to get HTML body from the generator by monkeypatching PDF writer
        class FakeHTML:
            def __init__(self, string, base_url=None):
                self.string = string
            def write_pdf(self, optimize_images=True):
                return self.string.encode('utf-8')
        pdf_export.HTML = FakeHTML
        pdf_bytes = pdf_export.generate_pdf_report(list(questions), app_cfg)
        with open(html_path, 'wb') as f:
            f.write(pdf_bytes)
        print('Wrote HTML to', html_path)
    except Exception as e2:
        print('Fallback also failed:', e2)

# Build a sample history DataFrame and write CSV with tempo-adjusted allowed minutes
df = pd.DataFrame([
    {
        'user_pseudonym': 'tester',
        'total_score': 42,
        'last_test_time': datetime.utcnow().isoformat(),
        'duration_seconds': 54,
        'allowed_min': 10,
        'tempo': 'power',
    }
])

# Apply tempo-adjust logic (same as in components/main_view)
tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}

def display_allowed_from_row(r):
    base = r.get('allowed_min', None)
    if base is None:
        base = app_cfg.test_duration_minutes
    code = r.get('tempo') or st.session_state.get('selected_tempo') or 'normal'
    factor = tempo_factor_map.get(code, 1.0)
    try:
        disp = int(base * factor) if base is not None else None
        if disp is not None:
            disp = max(1, disp)
    except Exception:
        disp = base
    return f"{disp} min" if disp is not None else ''

allowed_header = pdf_export.translate_ui('pdf.meta.allowed', default='erlaubt')
tempo_header = pdf_export.translate_ui('sidebar.history_columns.tempo', default='Tempo')

try:
    df[allowed_header] = df.apply(display_allowed_from_row, axis=1)
    df[tempo_header] = df['tempo'].fillna('')
    csv_path = os.path.join(out_dir, 'sample_history.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print('Wrote CSV to', csv_path)
except Exception as e:
    print('Failed to write CSV:', e)

print('Done')
