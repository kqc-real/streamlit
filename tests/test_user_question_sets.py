"""
Tests für die Verwaltung von temporären User-Fragensets (Wizard-Backend).
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import user_question_sets

@pytest.fixture
def mock_package_dir(tmp_path):
    """Simuliert das App-Verzeichnis im temporären Test-Ordner."""
    with patch("user_question_sets.get_package_dir", return_value=str(tmp_path)):
        yield tmp_path

def test_save_user_question_set_stores_metadata(mock_package_dir):
    """
    Prüft, ob beim Speichern eines User-Sets die Metadaten (insb. original_filename)
    korrekt gesetzt werden. Dies ist wichtig für die Wizard-Schritt-Erkennung.
    """
    # Mock für das QuestionSet-Objekt, das intern gebaut wird
    mock_qs = MagicMock()
    mock_qs.questions = [{"question": "Test?", "answers": ["A"], "correct": 0}]
    mock_qs.meta = {"title": "Test Set"}
    
    # Wir patchen _load_question_set_from_payload, um das Parsing zu überspringen
    with patch("user_question_sets._load_question_set_from_payload", return_value=mock_qs):
        
        user_id = "test_user"
        payload = b'{"meta":{}, "questions":[]}' # Dummy payload
        filename = "postproduction.json"
        
        # Act
        info = user_question_sets.save_user_question_set(user_id, payload, filename)
        
        # Assert 1: Metadaten im Objekt aktualisiert
        assert mock_qs.meta["uploaded_by"] == user_id
        assert mock_qs.meta["temporary"] is True
        assert mock_qs.meta["original_filename"] == filename
        
        # Assert 2: Datei wurde physisch geschrieben
        assert info.path.exists()
        
        # Assert 3: Gespeicherte JSON-Datei enthält die Metadaten
        content = json.loads(info.path.read_text(encoding="utf-8"))
        assert content["meta"]["original_filename"] == filename
        assert content["meta"]["uploaded_by"] == user_id

def test_is_owner_of_user_qset(mock_package_dir):
    """
    Prüft die Logik für den Besitz von temporären Sets (wichtig für Edit/Delete-Rechte).
    """
    # Setup: Mock Info-Objekt, das von get_user_question_set zurückgegeben wird
    mock_info = MagicMock()
    mock_info.uploaded_by = "owner_user"
    mock_info.uploaded_by_hash = "hash_123"
    
    with patch("user_question_sets.get_user_question_set", return_value=mock_info):
        # Fall 1: Match über User-ID (Pseudonym)
        assert user_question_sets.is_owner_of_user_qset("user::test.json", "owner_user", "other_hash") is True
        
        # Fall 2: Match über User-Hash
        assert user_question_sets.is_owner_of_user_qset("user::test.json", "other_user", "hash_123") is True
        
        # Fall 3: Kein Match
        assert user_question_sets.is_owner_of_user_qset("user::test.json", "other_user", "other_hash") is False

    # Fall 4: Set nicht gefunden
    with patch("user_question_sets.get_user_question_set", return_value=None):
        assert user_question_sets.is_owner_of_user_qset("user::test.json", "owner", "hash") is False