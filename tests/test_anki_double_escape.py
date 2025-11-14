import types
import sys
import os

# Ensure repo root available for imports during pytest collection
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_anki_sanitizer_does_not_double_escape(monkeypatch):
    """The Anki TSV sanitizer must not turn existing HTML entities
    inside math into doubly-escaped sequences like '&amp;lt;'.
    """
    from exporters import anki_tsv

    # Simulate bleach.clean that naively escapes angle brackets so the
    # sanitizer's placeholder logic is exercised.
    fake_bleach = types.SimpleNamespace(
        clean=lambda s, **kwargs: s.replace('<', '&lt;').replace('>', '&gt;')
    )
    monkeypatch.setattr(anki_tsv, 'bleach', fake_bleach)

    inp = 'Normal text <script>alert(1)</script> and math $<x,y>$ here.'
    out = anki_tsv._sanitize(inp)

    # script tags must be escaped
    assert '<script>' not in out
    assert '&lt;script&gt;' in out

    # math angle brackets must be present (raw or entity) but must NOT
    # appear double-escaped as '&amp;lt;' which indicates the math
    # fragment was escaped a second time.
    assert ('$<x,y>$' in out) or ('<x,y>' in out) or ('&lt;x,y&gt;' in out)
    assert '&amp;lt;' not in out
