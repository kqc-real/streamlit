#!/usr/bin/env python3
"""
Run end-to-end verification for tempos: normal, speed, power.
This script simulates a finished session for each tempo, calls the PDF
generation helper and writes a CSV row showing tempo and tempo-adjusted
allowed minutes. It also prints quick DB checks and the debug log tail.

Run from repo root: `python scripts/verify_tempo_end_to_end.py`
"""
import os
import sys
from datetime import datetime, timedelta
import sqlite3
import json

sys.path.insert(0, os.getcwd())

import streamlit as st
import pandas as pd
from config import AppConfig
import pdf_export

OUT_DIR = os.path.join(os.getcwd(), 'artifacts', 'tempo_verification')
os.makedirs(OUT_DIR, exist_ok=True)

TEMPOS = ['normal', 'speed', 'power']


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


def make_session_state_for_tempo(code: str, allowed_min: int = 10):
    # Reset session_state safely when running outside streamlit server
    try:
        st.session_state.clear()
    except Exception:
        try:
            st.session_state.update({})
        except Exception:
            pass

    now = datetime.utcnow()
    st.session_state['selected_tempo'] = code
    st.session_state['test_start_time'] = now - timedelta(seconds=54)
    st.session_state['test_end_time'] = now
    st.session_state['user_id'] = f'tester_{code}'
    st.session_state['selected_questions_file'] = f'questions_sample_{code}.json'


def display_allowed_from_row(r, app_cfg):
    tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
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


def run_for_tempo(code: str):
    print('---', code)
    make_session_state_for_tempo(code)

    app_cfg = AppConfig()
    app_cfg.test_duration_minutes = 10

    questions = DummyQuestions(allowed_min=10, meta={})

    # Generate PDF (or HTML fallback)
    out_pdf = os.path.join(OUT_DIR, f'report_{code}.pdf')
    out_html = os.path.join(OUT_DIR, f'report_{code}.html')
    try:
        pdf_bytes = pdf_export.generate_pdf_report(list(questions), app_cfg)
        # write bytes; if not a PDF, extension may be .html but we'll still write
        try:
            with open(out_pdf, 'wb') as f:
                f.write(pdf_bytes)
            print('Wrote PDF to', out_pdf)
        except Exception:
            with open(out_html, 'wb') as f:
                f.write(pdf_bytes)
            print('Wrote HTML to', out_html)
    except Exception as e:
        print('PDF generation failed — trying HTML fallback. Error:', e)
        try:
            class FakeHTML:
                def __init__(self, string, base_url=None):
                    self.string = string

                def write_pdf(self, optimize_images=True):
                    return self.string.encode('utf-8')

            pdf_export.HTML = FakeHTML
            pdf_bytes = pdf_export.generate_pdf_report(list(questions), app_cfg)
            with open(out_html, 'wb') as f:
                f.write(pdf_bytes)
            print('Wrote HTML to', out_html)
        except Exception as e2:
            print('Fallback also failed:', e2)

    # CSV row
    df = pd.DataFrame([
        {
            'user_pseudonym': f'tester_{code}',
            'total_score': 42,
            'last_test_time': datetime.utcnow().isoformat(),
            'duration_seconds': 54,
            'allowed_min': 10,
            'tempo': code,
        }
    ])

    allowed_header = pdf_export.translate_ui('pdf.meta.allowed', default='erlaubt')
    tempo_header = pdf_export.translate_ui('sidebar.history_columns.tempo', default='Tempo')
    try:
        df[allowed_header] = df.apply(lambda r: display_allowed_from_row(r, app_cfg), axis=1)
        df[tempo_header] = df['tempo'].fillna('')
        csv_path = os.path.join(OUT_DIR, f'history_{code}.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print('Wrote CSV to', csv_path)
    except Exception as e:
        print('Failed to write CSV:', e)

    # Quick DB check: see if any snapshot with this user exists and report tempo/effective_allowed
    db_path = os.path.join(os.getcwd(), 'db', 'mc_test_data.db')
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT session_id, tempo, allowed_min, effective_allowed FROM test_session_summaries WHERE user_pseudonym LIKE ? ORDER BY start_time DESC LIMIT 5", (f'tester_{code}%',))
            rows = cur.fetchall()
            if rows:
                print('DB snapshots (sample):')
                for r in rows:
                    print('  ', r)
            else:
                print('No matching snapshots for tester in DB (this run simulates but may not insert snapshots).')
            conn.close()
        except Exception as e:
            print('DB check failed:', e)
    else:
        print('DB not found at', db_path)


def tail_debug_log(n=40):
    log_path = os.path.join(os.getcwd(), 'var', 'tempo_debug.log')
    if not os.path.exists(log_path):
        print('No debug log at', log_path)
        return
    try:
        with open(log_path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = 1024
            data = b''
            while size > 0 and len(data.splitlines()) <= n:
                size = max(0, size - block)
                f.seek(size)
                data = f.read()
        print('\n--- tempo_debug.log tail ---')
        print(data.decode('utf-8', errors='replace').splitlines()[-n:])
    except Exception as e:
        print('Failed to read debug log:', e)


def main():
    print('Writing artifacts to', OUT_DIR)
    for t in TEMPOS:
        run_for_tempo(t)

    tail_debug_log()


if __name__ == '__main__':
    main()
