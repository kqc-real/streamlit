import pytest
import hashlib
import os
import json
from mc_test_app.core import get_user_id_hash, _load_fragen, _duration_to_str

def test_get_user_id_hash():
    user_id = "testuser"
    hash_val = get_user_id_hash(user_id)
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64
    # Hash should be deterministic
    assert hash_val == hashlib.sha256(user_id.encode()).hexdigest()

def test_load_fragen():
    fragen = _load_fragen()
    assert isinstance(fragen, list)
    if fragen:
        assert isinstance(fragen[0], dict)
        assert "frage" in fragen[0]
        assert "optionen" in fragen[0]
        assert "loesung" in fragen[0]

def test_duration_to_str():
    from datetime import timedelta
    assert _duration_to_str(timedelta(seconds=0)) == "0:00 min"
    assert _duration_to_str(timedelta(seconds=65)) == "1:05 min"
    assert _duration_to_str(None) == ""
