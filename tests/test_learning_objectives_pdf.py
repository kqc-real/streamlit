import sys
from types import SimpleNamespace

import main_view


def _capture_learning_objectives_html(monkeypatch):
    captured = {}

    class DummyHTML:
        def __init__(self, string=None, base_url=None, **kwargs):
            captured["html"] = string or ""
            captured["base_url"] = base_url
            captured["init_kwargs"] = kwargs

        def write_pdf(self, **kwargs):
            captured["write_kwargs"] = kwargs
            return b"%PDF-TEST%"

    monkeypatch.setitem(sys.modules, "weasyprint", SimpleNamespace(HTML=DummyHTML))
    return captured


def test_learning_objectives_pdf_unwraps_outer_markdown_fence(monkeypatch, tmp_path):
    captured = _capture_learning_objectives_html(monkeypatch)
    content = """```markdown
# Overarching Learning Objectives: Decision Trees

## Split Criteria

- Learners can compare Gini impurity and entropy.
```"""

    pdf_bytes, error = main_view._learning_objectives_pdf(content, tmp_path)

    assert error is None
    assert pdf_bytes == b"%PDF-TEST%"
    html = captured["html"]
    assert "<h1" in html
    assert "Overarching Learning Objectives: Decision Trees" in html
    assert "<h2" in html
    assert "Split Criteria" in html
    assert "<pre><code" not in html
    assert "```markdown" not in html


def test_learning_objectives_pdf_keeps_real_code_blocks_readable(monkeypatch, tmp_path):
    captured = _capture_learning_objectives_html(monkeypatch)
    content = """# Technische Lernziele

```python
print("ok")
```
"""

    pdf_bytes, error = main_view._learning_objectives_pdf(content, tmp_path)

    assert error is None
    assert pdf_bytes == b"%PDF-TEST%"
    html = captured["html"]
    assert '<pre><code class="language-python">print(&quot;ok&quot;)' in html
    assert "pre code {" in html
    assert "background: transparent;" in html
    assert "color: inherit;" in html
    assert "white-space: pre-wrap;" in html
