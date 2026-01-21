import importlib
import pathlib
import sys
import streamlit as st
import database
import config


def test_save_answer_upserts(monkeypatch, tmp_path):
    # Use a fresh DB in the tmp path
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)

    database.init_database()

    # Start a session
    session_id = database.start_test_session("user_upsert", "qset_upsert")
    assert session_id is not None

    # Insert a first answer
    database.save_answer(session_id, 1, "A", 0, False)

    # Insert a second answer for the same question (should upsert)
    database.save_answer(session_id, 1, "A fixed", 1, True)

    # Check that only one row exists for that (session_id, question_nr)
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c, SUM(points) AS s, MAX(is_correct) AS any_correct FROM answers WHERE session_id = ? AND question_nr = ?", (session_id, 1))
    row = cur.fetchone()
    assert row is not None
    assert int(row['c']) == 1
    assert int(row['s']) == 1
    assert int(row['any_correct']) == 1


def test_create_tables_dedupes_existing_duplicates(monkeypatch, tmp_path):
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)
    # Clear any cached DB connection so the monkeypatched DATABASE_FILE is used
    try:
        database.get_db_connection.clear()
    except Exception:
        pass

    # Create a minimal DB schema WITHOUT the unique index to simulate an
    # older DB that contains duplicates.
    conn = database.get_db_connection()
    cur = conn.cursor()
    with conn:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_nr INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                points INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Insert duplicate answers for the same session/question
        cur.execute("INSERT INTO answers (session_id, question_nr, answer_text, points, is_correct, timestamp) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (1, 1, 'A', 1, 1))
        cur.execute("INSERT INTO answers (session_id, question_nr, answer_text, points, is_correct, timestamp) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (1, 1, 'A second', 1, 1))

    # Run create_tables which contains the dedupe step and will create the unique index
    database.create_tables()

    # Now there should be only one row left for that (session_id, question_nr)
    cur.execute("SELECT COUNT(*) AS c FROM answers WHERE session_id = ? AND question_nr = ?", (1, 1))
    row = cur.fetchone()
    assert row is not None
    assert int(row['c']) == 1
