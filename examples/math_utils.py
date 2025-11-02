from __future__ import annotations

import re
from typing import Any
from markdown_it import MarkdownIt
from markdown_it.token import Token

try:
    # pykatex is optional for environments that don't need server-side rendering.
    from pykatex import render as pykatex_render
except Exception:  # pragma: no cover - tests run without pykatex installed in some CI
    pykatex_render = None


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
        seg = re.sub(r'\\\[(.+?)\\\]', lambda m: pykatex_render(m.group(1), display_mode=True), seg, flags=re.S)
        # Then inline math
        seg = re.sub(r'\\\((.+?)\\\)', lambda m: pykatex_render(m.group(1), display_mode=False), seg, flags=re.S)
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



