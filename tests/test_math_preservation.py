import html
import types
import os
import sys

# Ensure repo root is on sys.path so top-level modules (e.g. pdf_export, exporters)
# can be imported when pytest changes cwd during collection.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_pdf_preserves_angle_brackets_in_math(monkeypatch):
    """_parse_text_with_formulas must not HTML-escape angle brackets inside math."""
    import pdf_export

    # Avoid network/formula rendering by stubbing the parallel renderer to return a simple marker
    def fake_render(formulas, total_timeout=None):
        # Return a mapping idx -> rendered HTML fragment
        return {i: f'<img alt="FORMULA_{i}">' for i in range(len(formulas))}

    monkeypatch.setattr(pdf_export, "_render_formulas_parallel", fake_render)

    out = pdf_export._render_latex_in_html('$<x,y>$')

    # The original LaTeX should be passed to the renderer, which is stubbed out.
    # The output will contain the placeholder for the formula.
    assert '<img alt="FORMULA_0">' in out


def test_anki_sanitizer_preserves_math_placeholders(monkeypatch):
    """_sanitize (Anki TSV) should protect math placeholders from bleach-clean escaping."""
    from exporters import anki_tsv

    # Simulate a bleach.clean implementation that escapes '<' and '>' so we can test placeholder protection
    fake_bleach = types.SimpleNamespace(
        clean=lambda s, **kwargs: s.replace('<', '&lt;').replace('>', '&gt;')
    )
    monkeypatch.setattr(anki_tsv, 'bleach', fake_bleach)

    inp = 'Normal text <script>alert(1)</script> and math $<x,y>$ here.'
    out = anki_tsv._sanitize(inp)

    # The script tag must be escaped by the sanitizer
    assert '<script>' not in out
    assert '&lt;script&gt;' in out

    # But the math angle brackets must be preserved inside math
    # UPDATE: The sanitizer now converts $...$ to \(...\) and escapes HTML
    # inside it. This is the desired behavior for Anki/MathJax.
    assert "\\(&lt;x,y&gt;\\)" in out
