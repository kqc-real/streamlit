import json
import csv
import io

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


def test_missing_meta_title_falls_back_to_source_name():
    payload = [
        {
            "frage": "Frage 1",
            "optionen": ["A"],
            "loesung": 0,
            "thema": "Test",
            "gewichtung": 1,
        }
    ]
    b = json.dumps(payload).encode("utf-8")
    out = transform_to_anki_tsv(b, source_name="questions_Agiles_Projektmanagement.json")

    reader = csv.reader(io.StringIO(out), delimiter="\t")
    rows = list(reader)
    assert rows, "TSV should contain at least one row"
    first_row = rows[0]

    # Column order: Frage, Optionen, Antwort_Korrekt, Erklaerung_Basis,
    # Erklaerung_Erweitert, Glossar, Fragenset_Titel, ...
    assert first_row[6] == "Agiles Projektmanagement"


def test_matrix_backslashes_are_preserved():
    payload = {
        "meta": {"title": "Linear Algebra"},
        "questions": [
            {
                "frage": "$\\begin{pmatrix}1 & 2 \\ 3 & 4\\end{pmatrix}$",
                "optionen": ["$\\begin{pmatrix}4 & 5 \\ 6 & 7\\end{pmatrix}$"],
                "loesung": 0,
                "thema": "Matrix",
                "gewichtung": 2,
            }
        ],
    }
    b = json.dumps(payload).encode("utf-8")
    out = transform_to_anki_tsv(b)

    assert "\\\\" in out  # double backslash present for MathJax line breaks
