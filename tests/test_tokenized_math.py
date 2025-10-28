import json

from examples.transform_to_anki import transform_to_anki_tsv


def test_code_fence_math_preserved():
    # A question where an option contains a code fence and inline code with $...$
    payload = {
        "meta": {"title": "TokenTest"},
        "questions": [
            {
                "frage": "Code fence test",
                "optionen": [
                    "```\nprint('$x$')\n```",
                    "Normal $y$"
                ],
                "loesung": 1,
                "erklaerung": "Erkl.",
                "extended_explanation": "Ext",
                "thema": "Test",
                "gewichtung": 1
            }
        ]
    }

    json_bytes = json.dumps(payload).encode('utf-8')
    out = transform_to_anki_tsv(json_bytes)

    # The first option should contain a code block with the literal $x$ (not converted to \(x\))
    assert "$x$" in out
    # The second option should have math converted to \(...\)
    assert "\\(y\\)" in out
