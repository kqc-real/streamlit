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
