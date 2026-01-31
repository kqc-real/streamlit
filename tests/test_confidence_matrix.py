import database
import main_view
from helpers.text import get_user_id_hash


def _init_tmp_db(monkeypatch, tmp_path):
    db_file = str(tmp_path / "mc_test_data.db")
    monkeypatch.setattr(database, "DATABASE_FILE", db_file)
    try:
        database.get_db_connection.clear()
    except Exception:
        pass
    database.init_database()


def test_get_confidence_counts_for_questionset_excludes_author(monkeypatch, tmp_path):
    _init_tmp_db(monkeypatch, tmp_path)

    # Create two sessions for the same question set
    sid_author = database.start_test_session("author_hash", "qset_confidence")
    sid_user = database.start_test_session("user_hash", "qset_confidence")
    assert sid_author is not None
    assert sid_user is not None

    # Author answers
    database.save_answer(sid_author, 1, "A", 1, True, confidence="sure")
    database.save_answer(sid_author, 2, "B", 0, False, confidence="sure")

    # Other user answers
    database.save_answer(sid_user, 1, "C", 0, False, confidence="unsure")
    database.save_answer(sid_user, 2, "D", 1, True, confidence="unsure")

    counts = database.get_confidence_counts_for_questionset("qset_confidence")
    assert counts[1] == {
        "sure_correct": 1,
        "sure_wrong": 0,
        "unsure_correct": 0,
        "unsure_wrong": 1,
    }
    assert counts[2] == {
        "sure_correct": 0,
        "sure_wrong": 1,
        "unsure_correct": 1,
        "unsure_wrong": 0,
    }

    counts_excl = database.get_confidence_counts_for_questionset(
        "qset_confidence",
        exclude_user_id="author_hash",
    )
    assert counts_excl[1] == {
        "sure_correct": 0,
        "sure_wrong": 0,
        "unsure_correct": 0,
        "unsure_wrong": 1,
    }
    assert counts_excl[2] == {
        "sure_correct": 0,
        "sure_wrong": 0,
        "unsure_correct": 1,
        "unsure_wrong": 0,
    }


def test_resolve_author_hash_from_meta():
    meta = {"uploaded_by_hash": "hash123", "uploaded_by": "Alice"}
    assert main_view._resolve_author_hash_from_meta(meta) == "hash123"

    meta = {"uploaded_by": "Alice"}
    assert main_view._resolve_author_hash_from_meta(meta) == get_user_id_hash("Alice")

    assert main_view._resolve_author_hash_from_meta({}) is None
    assert main_view._resolve_author_hash_from_meta(None) is None


def test_should_show_confidence_matrix():
    fn = main_view._should_show_confidence_matrix

    assert fn(True, False, False, "qset", []) is True
    assert fn(False, False, False, "qset", []) is False
    assert fn(False, True, True, "qset", []) is True
    assert fn(False, True, False, "qset", ["qset"]) is True
    assert fn(False, True, False, "qset", []) is False
    assert fn(False, True, False, None, ["qset"]) is False
