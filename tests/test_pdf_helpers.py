import types
from types import SimpleNamespace

import pytest

import pdf_export


def test_get_options_variants():
    # dict -> ordered list
    q = {'optionen': {'B': 'two', 'A': 'one'}}
    assert pdf_export._get_options(q) == ['one', 'two']

    # list remains list
    q = {'options': ['a', 'b']}
    assert pdf_export._get_options(q) == ['a', 'b']

    # string becomes single-item list
    q = {'answers': 'only'}
    assert pdf_export._get_options(q) == ['only']

    # None or missing -> empty list
    q = {}
    assert pdf_export._get_options(q) == []


def test_resolve_correct_answer_index_and_letter_and_string():
    # numeric index in loesung
    q = {'options': ['x', 'y', 'z'], 'loesung': 1}
    assert pdf_export._resolve_correct_answer(q) == 'y'

    # letter mapping
    q = {'options': ['first', 'second', 'third'], 'loesung': 'C'}
    assert pdf_export._resolve_correct_answer(q) == 'third'

    # exact string match
    q = {'options': ['opt A', 'opt B'], 'loesung': 'opt B'}
    assert pdf_export._resolve_correct_answer(q) == 'opt B'

    # english answer key
    q = {'options': ['aa', 'bb'], 'answer': 'aa'}
    assert pdf_export._resolve_correct_answer(q) == 'aa'


def test_generate_pdf_report_applies_normalization(monkeypatch, tmp_path):
    # Prepare a question with German schema variants
    questions = [
        {
            'frage': 'Was ist Scrum?',
            'optionen': {'A': 'Framework', 'B': 'Prozess'},
            'loesung': 'A',
            'konzept': 'Scrum-Definition'
        }
    ]

    # Patch heavy external dependencies in pdf_export
    class DummyHTML:
        def __init__(self, string=None):
            self.string = string

        def write_pdf(self, **kwargs):
            # Accept kwargs like optimize_images to mimic real API
            return b'%PDF-TEST%'

    # Accept arbitrary kwargs like `base_url` used by caller
    monkeypatch.setattr(pdf_export, 'HTML', lambda string=None, **kwargs: DummyHTML(string))
    # The pdf_export function imports `get_all_logs_for_leaderboard` from
    # the `database` module at runtime inside the function. Provide a
    # lightweight dummy module so that import inside `generate_pdf_report`
    # succeeds and returns an empty leaderboard.
    import sys
    # Provide used database entrypoints; returning None for connection
    # causes `_calculate_average_stats` to return early.
    dummy_db = SimpleNamespace(
        get_all_logs_for_leaderboard=lambda q_file: [],
        get_db_connection=lambda: None,
    )
    monkeypatch.setitem(sys.modules, 'database', dummy_db)
    monkeypatch.setattr(pdf_export, 'get_answer_for_question', lambda i: None)
    monkeypatch.setattr(pdf_export, 'calculate_score', lambda answered, qs, mode: (0, 1))

    # Ensure a minimal session_state exists
    try:
        pdf_export.st.session_state = {}
    except Exception:
        pdf_export.st.session_state = {}

    # Minimal AppConfig substitute
    app_config = SimpleNamespace(scoring_mode='default')

    # Capture the HTML passed to the DummyHTML so we can inspect it
    container = {}

    def factory(string=None, **kwargs):
        inst = DummyHTML(string)
        container['inst'] = inst
        return inst

    monkeypatch.setattr(pdf_export, 'HTML', factory)

    # Call the generator (should produce PDF bytes)
    res = pdf_export.generate_pdf_report(questions, app_config)
    assert isinstance(res, (bytes, bytearray))

    # Inspect the produced HTML to ensure concept and options are present
    html = container['inst'].string if 'inst' in container else ''
    assert 'Scrum-Definition' in html
    assert 'Framework' in html and 'Prozess' in html


def test_generate_pdf_report_renders_block_markdown_in_questions_and_options(monkeypatch):
    correct_option = (
        "### Korrekt\n"
        "- **Fett** nutzt zwei Sternchen.\n"
        "- *Kursiv* nutzt ein Sternchen.\n"
        "- Inline-Code nutzt `Backticks`."
    )
    table_option = (
        "| Bewertung | Aussage |\n"
        "|---|---|\n"
        "| korrekt | Tabellenzeilen und `Inline-Code` sollen erhalten bleiben. |"
    )
    questions = [
        {
            "question": (
                "1. ## Formatierungs-Mix\n"
                "Welche Antwort beschreibt korrekt, wie **Fett**, *Kursiv* und `Inline-Code` getrennt werden?\n\n"
                "&gt; Prüfe, ob alle drei Inline-Formate erhalten bleiben."
            ),
            "optionen": [correct_option, table_option],
            "loesung": 0,
            "erklaerung": "Kurz",
            "gewichtung": 1,
            "thema": "Markdown-Grundlagen",
            "concept": "Inline-Formatierung",
            "kognitive_stufe": "Reproduktion",
        }
    ]

    class DummyHTML:
        def __init__(self, string=None):
            self.string = string

        def write_pdf(self, **kwargs):
            return b"%PDF-TEST%"

    container = {}

    def factory(string=None, **kwargs):
        inst = DummyHTML(string)
        container["inst"] = inst
        return inst

    import sys

    dummy_db = SimpleNamespace(
        get_all_logs_for_leaderboard=lambda q_file: [],
        get_db_connection=lambda: None,
    )
    monkeypatch.setitem(sys.modules, "database", dummy_db)
    monkeypatch.setattr(pdf_export, "HTML", factory)
    monkeypatch.setattr(pdf_export, "get_answer_for_question", lambda i: None)
    monkeypatch.setattr(pdf_export, "calculate_score", lambda answered, qs, mode: (0, 1))

    try:
        pdf_export.st.session_state = {}
    except Exception:
        pdf_export.st.session_state = {}
    pdf_export.st.session_state["selected_questions_file"] = "questions_Markdown_Stress.json"

    result = pdf_export.generate_pdf_report(questions, SimpleNamespace(scoring_mode="default"))
    assert result == b"%PDF-TEST%"

    html = container["inst"].string
    assert "<h2>Formatierungs-Mix</h2>" in html
    assert "<blockquote>" in html
    assert "&gt; Prüfe" not in html
    assert "<h3>Korrekt</h3>" in html
    assert "<li><strong>Fett</strong> nutzt zwei Sternchen.</li>" in html
    assert "<table>" in html
    assert "<th>Bewertung</th>" in html
    assert "| Bewertung |" not in html
    assert "### Korrekt" not in html
    assert "ul.options &gt; li" not in html
    assert "ul.options > li" in html


def test_build_glossary_html_renders_block_markdown_definitions():
    glossary = {
        "Markdown-Tabellen": {
            "Tabelle": (
                "| Element | Erwartung |\n"
                "|---|---|\n"
                "| Tabelle | wird als HTML-Tabelle gerendert |\n"
            ),
            "Code-Fence": "```python\nprint('ok')\n```",
        }
    }

    html = pdf_export._build_glossary_html(glossary)

    assert "<table>" in html
    assert "<th>Element</th>" in html
    assert "<td>wird als HTML-Tabelle gerendert</td>" in html
    assert "<pre><code" in html
    assert "| Element |" not in html
    assert "```python" not in html


def test_generate_musterloesung_pdf_renders_block_markdown_options(monkeypatch):
    questions = [
        {
            "question": (
                "1. ## Formatierungs-Mix\n"
                "Welche Option erhaelt Block-Markdown?"
            ),
            "options": [
                (
                    "### Markdown-Konventionen\n"
                    "- **Fett** nutzt zwei Sternchen.\n"
                    "- `Inline-Code` nutzt Backticks."
                ),
                (
                    "| Feld | Status |\n"
                    "|---|---|\n"
                    "| Tabelle | bleibt Tabelle |"
                ),
            ],
            "answer": 0,
            "explanation": "Kurz",
            "weight": 1,
            "topic": "Markdown",
            "concept": "Block-Markdown",
            "cognitive_level": "Reproduktion",
            "mini_glossary": [
                {"term": "Tabelle", "definition": "| A | B |\n|---|---|\n| 1 | 2 |"}
            ],
        }
    ]

    class DummyHTML:
        def __init__(self, string=None):
            self.string = string

        def write_pdf(self, **kwargs):
            return b"%PDF-TEST%"

    container = {}

    def factory(string=None, **kwargs):
        inst = DummyHTML(string)
        container["inst"] = inst
        return inst

    import config

    monkeypatch.setattr(config, "load_questions", lambda *args, **kwargs: None)
    monkeypatch.setattr(pdf_export, "HTML", factory)

    result = pdf_export.generate_musterloesung_pdf(
        "questions_Markdown_Stress.json",
        questions,
        SimpleNamespace(scoring_mode="default"),
    )

    assert result == b"%PDF-TEST%"
    html = container["inst"].string
    assert "<h2>Formatierungs-Mix</h2>" in html
    assert '<div class="option-content"><h3>Markdown-Konventionen</h3>' in html
    assert "<li><strong>Fett</strong> nutzt zwei Sternchen.</li>" in html
    assert "<table>" in html
    assert "<td>bleibt Tabelle</td>" in html
    assert '<span class="option-marker">\u2714</span>' in html
    assert "### Markdown-Konventionen" not in html
    assert "| Feld | Status |" not in html
