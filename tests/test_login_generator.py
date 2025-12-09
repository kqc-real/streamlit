import string

import admin_panel


def test_generate_secret_respects_length_and_charset():
    secret = admin_panel._generate_secret(24)
    assert len(secret) == 24
    allowed = set(string.ascii_letters + string.digits)
    assert set(secret) <= allowed


def test_available_pseudonyms_filters_used_and_sorts(monkeypatch):
    fake_scientists = [
        {"name": "curie", "contribution": "Radioactivity"},
        {"name": "Ada", "contribution": "Computing"},
        {"name": "Bohr", "contribution": "Quantum"},
        {"name": 123},  # invalid entry should be ignored
    ]

    monkeypatch.setattr(admin_panel, "load_scientists", lambda: fake_scientists)
    monkeypatch.setattr(admin_panel, "get_used_pseudonyms", lambda: ["curie"])

    result = admin_panel._available_pseudonyms()
    assert [p["name"] for p in result] == ["Ada", "Bohr"]
    assert result[0]["contribution"] == "Computing"
    assert result[1]["contribution"] == "Quantum"


def test_used_pseudonyms_deduplicates_and_sorts(monkeypatch):
    monkeypatch.setattr(admin_panel, "get_used_pseudonyms", lambda: ["bob", "Alice", "bob", " "])

    result = admin_panel._used_pseudonyms()
    assert result == ["Alice", "bob"]  # casefold-sorted, deduped, trimmed


def test_reserved_pseudonyms_filters_by_recovery(monkeypatch):
    monkeypatch.setattr(admin_panel, "get_used_pseudonyms", lambda: ["Alice", "bob", "Eve"])

    def fake_has_recovery(name):
        return name.lower() in {"bob", "eve"}

    monkeypatch.setattr(admin_panel, "has_recovery_secret_for_pseudonym", fake_has_recovery)

    result = admin_panel._reserved_pseudonyms()
    assert result == ["bob", "Eve"]
