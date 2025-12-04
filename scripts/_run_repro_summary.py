#!/usr/bin/env python3
"""Run `render_final_summary` in isolation with a shimmed Streamlit session_state.

This helps reproduce the early-finish message and verify tempo handling.
"""
import sys
import os
import types
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Minimal streamlit shim
st = types.ModuleType('streamlit')

class _State(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    def __setattr__(self, name, value):
        self[name] = value

st.session_state = _State()
sys.modules['streamlit'] = st

from main_view import render_final_summary
from config import AppConfig

class DummyQuestions:
    def __init__(self, allowed_min=None, meta=None):
        self._allowed_min = allowed_min
        self.meta = meta or {}
    def get_test_duration_minutes(self, default):
        return self._allowed_min if self._allowed_min is not None else default
    def __len__(self):
        return 1
    def __iter__(self):
        yield {"frage":"1","optionen":["A","B"],"loesung":0}

def main():
    # prepare session state
    now = datetime.utcnow()
    st.session_state.clear()
    st.session_state['selected_tempo'] = 'power'
    st.session_state['test_start_time'] = now - timedelta(seconds=50)
    st.session_state['test_end_time'] = now
    st.session_state['test_manually_ended'] = False
    st.session_state['test_time_expired'] = False

    app_cfg = AppConfig()
    app_cfg.test_duration_minutes = 10

    # Monkeypatch simple st.info/header to print
    def _info(msg):
        print("INFO:", msg)
    def _header(msg):
        print("HEADER:", msg)
    st.info = _info
    st.header = _header
    # Minimal markdown/write helpers used by render_final_summary
    st.markdown = lambda s, **kw: print("MD:", s)
    st.subheader = lambda s, **kw: print("SUB:", s)
    st.write = lambda s, **kw: print("WRITE:", s)
    st.success = lambda s, **kw: print("SUCCESS:", s)
    st.divider = lambda **kw: None

    class _DummyCol:
        def markdown(self, *a, **kw):
            pass
        def write(self, *a, **kw):
            pass

    st.columns = lambda n: [_DummyCol() for _ in range(n)]

    class _Expander:
        def __init__(self, *a, **kw):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    st.expander = lambda *a, **kw: _Expander()
    st.radio = lambda label, options=None, index=0, **kw: (options[index] if options else None)

    questions = DummyQuestions(allowed_min=10)
    render_final_summary(questions, app_cfg)

if __name__ == '__main__':
    main()
