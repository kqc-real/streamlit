#!/usr/bin/env python3
"""Repro script to exercise render_final_summary early-finish path."""
import datetime
import traceback

import streamlit as st

from main_view import render_final_summary
import main_view


class DummyQuestions:
    def __init__(self, allowed_min=None):
        self._allowed_min = allowed_min

    def get_test_duration_minutes(self, default):
        return self._allowed_min if self._allowed_min is not None else default

    def __len__(self):
        return 0


class DummyConfig:
    def __init__(self, test_duration_minutes=10, scoring_mode='default'):
        self.test_duration_minutes = test_duration_minutes
        self.scoring_mode = scoring_mode


def main():
    # Clear any previous state
    st.session_state.clear()

    # Simulate a very short test: 30 seconds duration
    now = datetime.datetime.now()
    st.session_state['test_start_time'] = now - datetime.timedelta(seconds=30)
    st.session_state['test_end_time'] = now
    st.session_state['selected_tempo'] = 'power'
    st.session_state['test_manually_ended'] = True
    st.session_state['test_time_expired'] = False

    questions = DummyQuestions(allowed_min=10)
    app_config = DummyConfig(test_duration_minutes=10)

    # Monkeypatch calculate_score to avoid heavy dependencies
    main_view.calculate_score = lambda answered, qs, mode: (0, 1)

    try:
        render_final_summary(questions, app_config)
        print("render_final_summary completed without exception")
    except Exception:
        print("Exception during render_final_summary:")
        traceback.print_exc()


if __name__ == '__main__':
    main()
