from __future__ import annotations

import re
from typing import Any
from markdown_it import MarkdownIt


def render_markdown_with_math(md: MarkdownIt, s: str) -> str:
    """Render markdown to HTML, normalizing KaTeX ($...$, $$...$$) only inside text tokens.

    This preserves math inside code fences/inline code by operating on markdown-it tokens.
    """
    if not s:
        return ""

    tokens = md.parse(s)
    for t in tokens:
        if t.type == "inline" and getattr(t, "children", None):
            for child in t.children:
                if child.type == "text":
                    txt = child.content
                    # $$...$$ -> \[ ... \]
                    txt = re.sub(r"\$\$(.*?)\$\$", lambda m: f"\\[{m.group(1)}\\]", txt, flags=re.S)
                    # $...$ -> \( ... \)
                    txt = re.sub(r"\$(.*?)\$", lambda m: f"\\({m.group(1)}\\)", txt)
                    child.content = txt

    return md.renderer.render(tokens, md.options, {})
