from __future__ import annotations

import re
from markdown_it import MarkdownIt

try:
    # pykatex is optional for environments that don't need server-side rendering.
    from pykatex import render as pykatex_render
except Exception:  # pragma: no cover - tests run without pykatex installed in some CI
    pykatex_render = None


def _convert_math_tokens(content: str) -> str:
    if not content or '$' not in content:
        return content

    # Replace display math first: $$...$$ -> \[...\]
    content = re.sub(
        r'\$\$(.+?)\$\$',
        lambda m: f"\\[{m.group(1)}\\]",
        content,
        flags=re.DOTALL,
    )

    # Replace inline math: $...$ -> \(...\) while ignoring $$...$$ blocks
    content = re.sub(
        r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',
        lambda m: f"\\({m.group(1)}\\)",
        content,
        flags=re.DOTALL,
    )

    # Escape remaining dollar signs (currency etc.)
    content = re.sub(r'(?<!\\)\$', r'\\$', content)

    return content


def _apply_math_conversions(tokens: list) -> None:
    for token in tokens:
        if token.type == 'inline' and token.children:
            for child in token.children:
                if child.type == 'text':
                    child.content = _convert_math_tokens(child.content)
        elif token.type == 'text':
            token.content = _convert_math_tokens(token.content)


def render_markdown_with_math(md: MarkdownIt, s: str) -> str:
    r"""
    Render markdown string to HTML, converting math expressions.
    - $$...$$ -> \[... \] (display)
    - $...$ -> \(...\) (inline)
    This is done only on text tokens, to avoid converting math in code blocks.
    """
    if not s:
        return ""

    # Protect math regions by replacing them with safe placeholders
    # before feeding the text to Markdown-It. This prevents the Markdown
    # emphasis parser from splitting math (e.g. underscores inside math
    # being interpreted as emphasis). After rendering we restore the
    # converted math (replace $...$ -> \(...\) / \[...\]).
    # Match common math delimiters in the raw source ($$, $, \[ \], \( \)).
    math_pattern = __import__('re').compile(r'(\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\))', __import__('re').DOTALL)
    placeholders: dict[str, str] = {}

    def _repl(m):
        key = f"MATHPLACEHOLDER{len(placeholders)}"
        # Convert $...$ to \(...\) / \[...\] so downstream rendering
        # (and optional KaTeX) receives normalized delimiters.
        placeholders[key] = _convert_math_tokens(m.group(0))
        return key

    protected = math_pattern.sub(_repl, s)
    # Parse and render with Markdown-It while math is hidden behind
    # inert placeholders.
    tokens = md.parse(protected)
    html = md.renderer.render(tokens, md.options, {})

    # Restore math placeholders with the converted math content.
    for key, math_html in placeholders.items():
        html = html.replace(key, math_html)

    # Some Markdown engines may have (incorrectly) injected inline HTML
    # tags inside restored math delimiters (e.g. `<em>` from underscore
    # processing). Strip any HTML tags that ended up inside math
    # delimiters to ensure math engines receive clean LaTeX source.
    def _strip_tags_in_math(match: re.Match) -> str:
        inner = match.group(1)
        # Remove any HTML tags inside the math content
        clean_inner = re.sub(r"<[^>]+>", "", inner)
        return f"\\({clean_inner}\\)"

    # Inline math: \(...\)
    html = re.sub(r"\\\\\((.*?)\\\\\)", _strip_tags_in_math, html, flags=re.S)

    def _strip_tags_in_display(match: re.Match) -> str:
        inner = match.group(1)
        clean_inner = re.sub(r"<[^>]+>", "", inner)
        return f"\\[{clean_inner}\\]"

    # Display math: \[...\]
    html = re.sub(r"\\\\\[(.*?)\\\\\]", _strip_tags_in_display, html, flags=re.S)

    return html


def _render_math_html_outside_code(html: str) -> str:
    r"""Render KaTeX expressions in HTML, but skip content inside <pre> or <code> blocks.

    This function finds \(...\) (inline) and \[...\] (display) math in the HTML
    and replaces them with the HTML produced by pykatex. It uses a simple split on
    <pre> and <code> blocks so that code snippets are left untouched.
    """
    if not pykatex_render:
        return html

    # Split into segments that are either code/pre blocks or other HTML.
    parts = re.split(r'(<pre[\s\S]*?</pre>|<code[\s\S]*?</code>)', html, flags=re.I)

    def _replace_math_in_segment(seg: str) -> str:
        # Replace display math first
        seg = re.sub(r'\\\\[(.+?)\\]', lambda m: pykatex_render(m.group(1), display_mode=True), seg, flags=re.S)
        # Then inline math
        seg = re.sub(r'\\\\(.+?)\\\)', lambda m: pykatex_render(m.group(1), display_mode=False), seg, flags=re.S)
        return seg

    out_parts = []
    for p in parts:
        if not p:
            continue
        if p.lower().startswith('<pre') or p.lower().startswith('<code'):
            out_parts.append(p)
        else:
            out_parts.append(_replace_math_in_segment(p))

    return ''.join(out_parts)
