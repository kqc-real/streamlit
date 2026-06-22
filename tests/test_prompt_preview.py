from components import _build_prompt_preview_html


def test_prompt_preview_renders_markdown_as_read_only_html():
    html = _build_prompt_preview_html("# Prompt Title\n\n```json\n{\"ok\": true}\n```")

    assert 'class="mc-prompt-preview"' in html
    assert "user-select: none" in html
    assert "-webkit-touch-callout: none" in html
    assert 'oncopy="return false"' in html
    assert "<h1>Prompt Title</h1>" in html
    assert "{&quot;ok&quot;: true}" in html
    assert "height: clamp(260px, 52vh, 520px);" in html
    assert "overflow-y: auto;" in html
    assert ".mc-prompt-preview h1" in html
    assert "font-size: 1.28rem;" in html
    assert ".mc-prompt-preview p" in html
    assert ".mc-prompt-preview pre code" in html


def test_prompt_preview_sanitizes_unsafe_html():
    html = _build_prompt_preview_html("# Title\n\n<script>alert('x')</script>")

    assert "<script" not in html
    assert "mc-prompt-preview" in html
