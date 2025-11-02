import json
from exporters.anki_tsv import transform_to_anki_tsv


def test_dollar_in_normal_text_is_preserved():
    # A single $ without a closing delimiter should not be treated as math
    payload = {
        "meta": {"title": "EdgeCases"},
        "questions": [
            {"frage": "Preis: $5", "optionen": ["OK"], "loesung": 0, "thema": "Money", "gewichtung": 1}
        ],
    }
    b = json.dumps(payload).encode("utf-8")
    out = transform_to_anki_tsv(b)

    # The literal $5 should be present (not converted to math delimiters)
    assert "$5" in out


def test_ambiguous_nested_delimiters_keep_display_math_and_inner_dollar():
    # Example: $$ a $ b $$ should be treated as display math with inner single $ preserved
    payload = {
        "meta": {"title": "EdgeCases"},
        "questions": [
            {"frage": "$$a $ b$$", "optionen": ["X"], "loesung": 0, "thema": "Math", "gewichtung": 2}
        ],
    }
    b = json.dumps(payload).encode("utf-8")
    out = transform_to_anki_tsv(b)

    # The display math should be converted to \[ ... \] and the inner single $ should remain inside
    assert "\\[" in out and "\\]" in out
    assert "$ b" in out
