from helpers.text import unwrap_markdown_document_fence


def test_unwrap_markdown_document_fence_removes_outer_markdown_wrapper():
    content = """```markdown
# Lernziele

## Anwendung

1. **bestimmen** passende Split-Kriterien.
```"""

    assert unwrap_markdown_document_fence(content) == (
        "# Lernziele\n\n"
        "## Anwendung\n\n"
        "1. **bestimmen** passende Split-Kriterien."
    )


def test_unwrap_markdown_document_fence_keeps_real_code_document():
    content = """```python
print("ok")
```"""

    assert unwrap_markdown_document_fence(content) == content


def test_unwrap_markdown_document_fence_keeps_inner_code_blocks():
    content = """```markdown
# Technische Lernziele

```python
print("ok")
```
```"""

    assert unwrap_markdown_document_fence(content) == (
        "# Technische Lernziele\n\n"
        "```python\n"
        'print("ok")\n'
        "```"
    )
