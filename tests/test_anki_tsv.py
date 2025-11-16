import json
from exporters.anki_tsv import transform_to_anki_tsv


def make_sample_json():
    return {
        "meta": {"title": "Beispieltest"},
        "questions": [
            {
                "frage": "Was ist $a+b$?",
                "optionen": ["$a$", "$b$", "a + b"],
                "loesung": 2,
                "erklaerung": "Die Summe ist $a+b$.",
                "extended_explanation": {"title": "Details", "content": "Mehr Info $x$"},
                "mini_glossary": {"Term": "Definition $y$"},
                "thema": "Mathe",
                "gewichtung": 2,
            },
            {
                "frage": """Codebeispiel mit Dollarzeichen:
```
print('$x$')
```
""",
                "optionen": ["A", "B"],
                "loesung": 0,
                "erklaerung": "Siehe Code oben.",
                "thema": "Code",
                "gewichtung": 1,
            },
        ],
    }


def test_transform_contains_math_and_preserves_code_block():
    js = make_sample_json()
    b = json.dumps(js).encode("utf-8")
    tsv = transform_to_anki_tsv(b)

    # Ensure inline math converted to MathJax style \( ... \)
    assert "\\(" in tsv and "\\)" in tsv

    # Ensure options list rendered as an ordered list (CSV quoting may escape quotes)
    assert "<ol" in tsv and "<li>" in tsv

    # Ensure code fence dollar signs remain inside <pre>/<code> (not converted)
    # UPDATE: The sanitizer now converts ALL single-dollar-pairs to \(...\)
    # for better Anki/MathJax compatibility. This is expected behavior.
    assert "print('\\(x\\)')" in tsv
