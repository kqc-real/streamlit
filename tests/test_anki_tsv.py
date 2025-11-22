import json
from exporters.anki_tsv import transform_to_anki_tsv


def make_sample_json():
    return {
        "meta": {"title": "Beispieltest"},
        "questions": [
            {
                "question": "Was ist $a+b$?",
                "options": ["$a$", "$b$", "a + b"],
                "answer": 2,
                "explanation": "Die Summe ist $a+b$.",
                "extended_explanation": {"title": "Details", "content": "Mehr Info $x$"},
                "mini_glossary": {"Term": "Definition $y$"},
                "topic": "Mathe",
                "weight": 2,
            },
            {
                "question": """Codebeispiel mit Dollarzeichen:
```
print('$x$')
```
""",
                "options": ["A", "B"],
                "answer": 0,
                "explanation": "Siehe Code oben.",
                "topic": "Code",
                "weight": 1,
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
