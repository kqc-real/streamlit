import json
import csv
import io
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

    # Ensure options list rendered as a scoped ordered list (CSV quoting may escape quotes)
    first_row = next(csv.reader(io.StringIO(tsv), delimiter="\t"))
    assert '<ol class="answer-options" type="A">' in first_row[1] and "<li>" in first_row[1]

    # Ensure code fence dollar signs remain inside <pre>/<code> (not converted).
    assert "print('$x$')" in tsv


def test_transform_renders_markdown_stress_features_for_anki():
    payload = {
        "meta": {"title": "Markdown Stress"},
        "questions": [
            {
                "question": (
                    "1. ## Formatierungs-Mix\n"
                    "Welche Aussage passt zu **Fett**, *Kursiv* und `Code`?\n\n"
                    "> Hinweis im Fragenstamm\n\n"
                    "| Element | Bedeutung |\n"
                    "|---|---|\n"
                    "| `X` | Feature-Matrix |"
                ),
                "options": [
                    (
                        "### Option mit Tabelle\n"
                        "| Aspekt | Aussage |\n"
                        "|---|---|\n"
                        "| Struktur | bleibt Tabelle |"
                    ),
                    (
                        "```python\n"
                        "print('$x$')\n"
                        "```\n"
                        "Der Codeblock bleibt getrennt vom Fließtext."
                    ),
                    "<strong>HTML:</strong><br>H<sub>2</sub>O und x<sup>2</sup>",
                    "Link [Beispiel](https://example.com/a) und Bild ![Alt](https://example.com/i.svg)",
                ],
                "answer": 0,
                "explanation": "Math außerhalb von Code wird $x$ und **Markdown** bleibt HTML.",
                "mini_glossary": [
                    {"term": "Markdown-Link", "definition": "Syntax der Form `[Text](URL)`."},
                    {"term": "Markdown-Tabelle", "definition": "| A | B |\n|---|---|\n| 1 | 2 |"},
                ],
                "topic": "Markdown",
                "concept": "Stress",
                "cognitive_level": "Anwendung",
                "weight": 1,
            }
        ],
    }

    tsv = transform_to_anki_tsv(json.dumps(payload).encode("utf-8"), source_name="questions_Markdown_Stress.json")
    row = next(csv.reader(io.StringIO(tsv), delimiter="\t"))
    html = "\n".join(row[:6])

    assert "<h2>Formatierungs-Mix</h2>" in html
    assert "<strong>Fett</strong>" in html
    assert "<em>Kursiv</em>" in html
    assert "<blockquote>" in html
    assert "<table>" in html
    assert "<th>Element</th>" in html
    assert "<td>bleibt Tabelle</td>" in html
    assert "print('$x$')" in html
    assert "<p>Der Codeblock bleibt getrennt vom Fließtext.</p>" in html
    assert "print('\\(x\\)')" not in html
    assert "<br>" in html
    assert "<sub>2</sub>" in html
    assert "<sup>2</sup>" in html
    assert '<a href="https://example.com/a">Beispiel</a>' in html
    assert '<img src="https://example.com/i.svg" alt="Alt">' in html
    assert "„https://example.com" not in html
    assert "\\(x\\)" in html
    assert "<dl>" in html
    assert "<dt>Markdown-Tabelle</dt>" in html
    assert "<td>2</td>" in html
    assert "| Element |" not in html


def test_transform_keeps_multiblock_question_paragraphs_intact():
    payload = {
        "meta": {"title": "Multiblock"},
        "questions": [
            {
                "question": "1. Prüfe diese Struktur:\n\n1. Daten lesen\n2. Modell trainieren\n\nFertig.",
                "options": ["OK"],
                "answer": 0,
                "explanation": "Kurz",
            }
        ],
    }

    tsv = transform_to_anki_tsv(json.dumps(payload).encode("utf-8"))
    row = next(csv.reader(io.StringIO(tsv), delimiter="\t"))

    assert "<p>Prüfe diese Struktur:</p>" in row[0]
    assert "<ol>" in row[0]
    assert "<li>Daten lesen</li>" in row[0]
    assert row[0].endswith("<p>Fertig.</p>")


def test_transform_scopes_answer_option_markers_around_nested_lists():
    payload = {
        "meta": {"title": "Markdown Stress"},
        "questions": [
            {
                "question": "Prüfe diese Struktur:\n\n1. Daten lesen\n2. Modell trainieren",
                "options": [
                    (
                        "> Ablauf\n"
                        "> Die Reihenfolge ist ein einfacher ML-Ablauf.\n\n"
                        "- Lesen\n"
                        "- Trainieren\n"
                        "- Bewerten"
                    ),
                    (
                        "> Startpunkt\n"
                        "> Die Reihenfolge startet mit der Bewertung.\n\n"
                        "- Bewerten\n"
                        "- Lesen\n"
                        "- Trainieren"
                    ),
                ],
                "answer": 0,
                "explanation": "Kurz",
            }
        ],
    }

    tsv = transform_to_anki_tsv(json.dumps(payload).encode("utf-8"))
    row = next(csv.reader(io.StringIO(tsv), delimiter="\t"))

    assert row[1].startswith('<ol class="answer-options" type="A">')
    assert "<blockquote>" in row[1]
    assert "<ul>" in row[1]
    assert "<li>Lesen</li>" in row[1]


def test_apkg_css_scopes_answer_option_markers_to_outer_list():
    from export_jobs import _ANKI_CARD_CSS

    assert ".options > ol.answer-options > li::before" in _ANKI_CARD_CSS
    assert ".options ol li::before" not in _ANKI_CARD_CSS
