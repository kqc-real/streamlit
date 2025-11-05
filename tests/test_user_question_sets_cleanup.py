import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on sys.path so top-level modules are importable when
# pytest runs from an isolated working directory.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import user_question_sets


def _make_payload_bytes():
    payload = {
        "questions": [
            {"frage": "1. Was ist 2+2?", "optionen": ["3", "4"], "loesung": 1}
        ],
        "meta": {"title": "temp test"},
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def test_cleanup_removes_stale_file(monkeypatch, tmp_path):
    # Force the module to use a temporary package dir so we don't touch repo files.
    monkeypatch.setattr(user_question_sets, "get_package_dir", lambda: str(tmp_path))

    payload = _make_payload_bytes()

    # Save a user question set
    info = user_question_sets.save_user_question_set("tester", payload, original_filename="upload.json")
    assert info.path.exists()

    # Overwrite the file to have an old uploaded_at timestamp (48 hours ago)
    with info.path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    old_ts = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    data.setdefault("meta", {})["uploaded_at"] = old_ts

    with info.path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    # Ensure the listing sees the item
    listed = user_question_sets.list_user_question_sets()
    assert any(i.path == info.path for i in listed)

    # Run cleanup with 24h threshold: should remove the file
    removed = user_question_sets.cleanup_stale_user_question_sets(hours=24)
    assert removed >= 1
    assert not info.path.exists()

    # After cleanup, listing should not include the file
    listed_after = user_question_sets.list_user_question_sets()
    assert all(i.path != info.path for i in listed_after)
