import os
import sys
import re

# Ensure project root is importable when running pytest from repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import load_questions, AppConfig
import pdf_export


def test_pdf_extended_explanation_no_python_repr():
    # Load a real question (loader applies aliases/normalization)
    # Use an available mathematics dataset that contains explanations
    qset = load_questions('questions_Mathematik_I.json', silent=True)
    # pick any question that has at least a short explanation or extended_explanation
    source_q = None
    for qq in qset:
        if 'erklaerung' in qq or 'extended_explanation' in qq:
            source_q = dict(qq)
            break
    assert source_q is not None

    # Create the problematic stringified-python-dict + trailing text form
    bad = "{'title': 'Titel', 'steps': 'Schritte', 'content': 'Inhalt'}: Berechnung einer symmetrischen Differenz"
    source_q['extended_explanation'] = bad

    # Monkeypatch the HTML writer to capture returned HTML instead of writing a PDF
    class DummyHTML:
        def __init__(self, string=None, base_url=None):
            self._string = string
            self.base_url = base_url

        def write_pdf(self, *a, **kw):
            return self._string

    origHTML = pdf_export.HTML
    pdf_export.HTML = DummyHTML
    try:
        app = AppConfig()
        html = pdf_export.generate_pdf_report([source_q], app)
    finally:
        pdf_export.HTML = origHTML

    # Assert that no Python-style dict repr is present in the generated HTML
    assert re.search(r"\{\'title\':", html) is None
    # And ensure at least some explanation text is present (fallback should show short explanation)
    assert ('Erklärung' in html) or ('Detaillierte Erklärung' in html) or ('Titel' in html)
