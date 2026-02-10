import json
from datetime import datetime, timedelta, timezone

import database
import user_question_sets
from helpers.text import get_user_id_hash


def _make_payload_bytes():
    payload = {
        "questions": [
            {
                "frage": "1. Was ist 2+2?",
                "optionen": ["3", "4", "5"],
                "loesung": 1,
                "erklaerung": "Weil 2+2=4.",
                "gewichtung": 1,
                "thema": "Mathe",
                "konzept": "Addition",
            }
        ],
        "meta": {"title": "temp test", "language": "de"},
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def test_delete_sets_for_user_ids_accepts_hash(monkeypatch, tmp_path):
    monkeypatch.setattr(user_question_sets, "get_package_dir", lambda: str(tmp_path))

    payload = _make_payload_bytes()
    info_a = user_question_sets.save_user_question_set("alice", payload, original_filename="upload.json")
    info_b = user_question_sets.save_user_question_set("bob", payload, original_filename="upload.json")

    assert info_a.path.exists()
    assert info_b.path.exists()

    deleted = user_question_sets.delete_sets_for_user_ids([get_user_id_hash("alice")])
    assert deleted == 1
    assert not info_a.path.exists()
    assert info_b.path.exists()


def test_release_unreserved_pseudonyms_deletes_temp_sets(monkeypatch, tmp_path):
    # Use a temp DB
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)
    database.get_db_connection.clear()
    database.init_database()

    # Store temp user sets under temp package dir
    monkeypatch.setattr(user_question_sets, "get_package_dir", lambda: str(tmp_path))

    payload = _make_payload_bytes()
    info = user_question_sets.save_user_question_set("alice", payload, original_filename="upload.json")
    assert info.path.exists()

    user_pseudo = "alice"
    user_hash = get_user_id_hash(user_pseudo)
    database.add_user(user_hash, user_pseudo)

    session_id = database.start_test_session(user_hash, "qset_test")
    assert session_id is not None

    conn = database.get_db_connection()
    old_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    conn.execute("UPDATE test_sessions SET start_time = ? WHERE session_id = ?", (old_time, session_id))
    conn.commit()

    deleted_users = database.release_unreserved_pseudonyms()
    assert deleted_users >= 1
    assert not info.path.exists()

    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_hash,))
    assert cur.fetchone() is None
