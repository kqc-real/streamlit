import sqlite3
import pathlib
import importlib
import sys
from config import QuestionSet
import streamlit as st

# load modules via package import when running tests
import database
import config


def make_qset(num_questions=2):
    questions = [{"gewichtung": 1} for _ in range(num_questions)]
    return QuestionSet(questions=questions, meta={})


def test_recompute_session_summary_uses_best_per_question(monkeypatch, tmp_path):
    # Ensure a clean DB in tmp_path and point DATABASE_FILE there
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)

    # Create tables
    database.init_database()

    # Prepare a simple QuestionSet via monkeypatching load_questions
    def fake_load_questions(qfile, silent=False):
        return make_qset(num_questions=2)

    monkeypatch.setattr(config, "load_questions", fake_load_questions)

    # Start a session
    session_id = database.start_test_session("user_1", "qset_test")
    assert session_id is not None

    # Insert multiple answers for the same question (duplicates / updates)
    # Question 1: two correct attempts (1 + 1 -> should count as 1)
    database.save_answer(session_id, 1, "A", 1, True)
    database.save_answer(session_id, 1, "A (again)", 1, True)

    # Question 2: first wrong (0), then corrected (1) -> best should be 1
    database.save_answer(session_id, 2, "B", 0, False)
    database.save_answer(session_id, 2, "B (fixed)", 1, True)

    # Recompute summary
    ok = database.recompute_session_summary(session_id)
    assert ok

    # Read back the summary
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT total_points, max_points, correct_count, percent FROM test_session_summaries WHERE session_id = ?", (session_id,))
    row = cur.fetchone()
    assert row is not None

    total_points = int(row['total_points']) if row['total_points'] is not None else 0
    correct_count = int(row['correct_count']) if row['correct_count'] is not None else 0
    percent = float(row['percent']) if row['percent'] is not None else 0.0

    # Expect best per question: 1 + 1 = 2
    assert total_points == 2
    # Both questions have at least one correct attempt
    assert correct_count == 2
    # Since we monkeypatched questions to have 2 * weight(1) => max_points == 2 -> percent == 100
    assert int(round(percent)) == 100
