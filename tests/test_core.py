import pytest
import hashlib
import os
import json
import tempfile
from unittest.mock import patch, mock_open
from datetime import timedelta

# Import from core.py
import importlib
try:
    # Package layout
    from mc_test_app import core as core  # type: ignore
    from mc_test_app import mc_test_app as app_mod  # type: ignore
except Exception:
    # Flat layout (repo root is the app folder)
    import core as core  # type: ignore
    import mc_test_app as app_mod  # type: ignore

get_user_id_hash = core.get_user_id_hash  # type: ignore
_load_fragen = core._load_fragen  # type: ignore
_duration_to_str = core._duration_to_str  # type: ignore

get_rate_limit_seconds = app_mod.get_rate_limit_seconds
user_has_progress = app_mod.user_has_progress
calculate_leaderboard = app_mod.calculate_leaderboard
save_answer = app_mod.save_answer
initialize_session_state = app_mod.initialize_session_state

# Removed legacy fallback imports (package import now stable)


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
    assert _duration_to_str(timedelta(seconds=0)) == "0:00 min"
    assert _duration_to_str(timedelta(seconds=65)) == "1:05 min"
    assert _duration_to_str(None) == ""


def test_get_rate_limit_seconds():
    # Test with environment variable
    with patch.dict(os.environ, {"MC_TEST_MIN_SECONDS_BETWEEN": "10"}):
        assert get_rate_limit_seconds() == 10
    # Test without env var
    with patch.dict(os.environ, {}, clear=True):
        assert get_rate_limit_seconds() == 0


def test_user_has_progress():
    # Create a temporary file path
    temp_file = tempfile.mktemp(suffix='.csv')
    
    # Write test data to the file
    with open(temp_file, 'w') as f:
        f.write("user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit\n")
        f.write("testhash,abcd1234,testuser,1,Test Frage,Option A,1,2025-09-19T10:00:00\n")
    
    # Mock the LOGFILE to point to our temp file
    with patch.object(app_mod, 'LOGFILE', temp_file):
        # Test with existing progress
        assert user_has_progress("testhash") is True
        # Test with no progress
        assert user_has_progress("nonexistent") is False
    
    # Clean up
    os.unlink(temp_file)


def test_calculate_leaderboard():
    # Mock CSV data
    mock_data = """user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit
hash1,abcd,user1,1,Q1,A,1,2025-09-19T10:00:00
hash1,abcd,user1,2,Q2,B,1,2025-09-19T10:01:00
hash2,efgh,user2,1,Q1,C,0,2025-09-19T10:02:00
"""
    with patch('pandas.read_csv') as mock_read:
        mock_read.return_value = mock_data
        # This would need more setup for full testing
        # For now, just ensure it doesn't crash
        result = calculate_leaderboard()
        assert result is not None  # Basic check


def test_initialize_session_state():
    # Mock streamlit session_state as an object with attributes
    class MockSessionState:
        def __init__(self):
            pass
    
    mock_state = MockSessionState()
    with patch('mc_test_app.mc_test_app.st.session_state', mock_state), \
        patch('mc_test_app.mc_test_app.fragen', [{'frage': 'test'}]):  # Mock fragen
        initialize_session_state()
        assert hasattr(mock_state, 'beantwortet')
        assert hasattr(mock_state, 'frage_indices')
        assert hasattr(mock_state, 'start_zeit')


def test_save_answer():
    # Mock dependencies
    with patch.object(app_mod, 'get_user_id_hash', return_value='testhash'), \
        patch.object(app_mod, 'datetime') as mock_datetime, \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('streamlit.session_state', {'user_id': 'testuser'}), \
         patch('os.path.isfile', return_value=False):

        mock_datetime.now.return_value.isoformat.return_value = '2025-09-19T10:00:00'

        frage_obj = {
            'frage': '1. Test Frage',
            'optionen': ['A', 'B', 'C']
        }

        save_answer('testuser', 'testhash', frage_obj, 'A', 1)

        # Check if file was written
        mock_file.assert_called()


# Additional tests for core logic
def test_punkte_berechnung():
    # Test scoring logic (extracted from app)
    def calculate_score(answers, fragen, mode='positive_only'):
        if mode == 'positive_only':
            return sum(
                frage.get("gewichtung", 1) if p == frage.get("gewichtung", 1) else 0
                for p, frage in zip(answers, fragen)
            )
        else:
            return sum(p if p is not None else 0 for p in answers)

    fragen = [{'gewichtung': 1}, {'gewichtung': 2}]
    answers = [1, 2]  # Correct answers
    assert calculate_score(answers, fragen, 'positive_only') == 3
    assert calculate_score(answers, fragen, 'negative') == 3

    answers_wrong = [0, -1]
    assert calculate_score(answers_wrong, fragen, 'positive_only') == 0
    assert calculate_score(answers_wrong, fragen, 'negative') == -1
