"""Anki TSV Exporter

Erzeugt eine UTF-8 kodierte TSV-String-Repräsentation aus dem internen
Fragenset-JSON. Baut auf `examples.math_utils.render_markdown_with_math`
und sanitized die resultierende HTML-Ausgabe mit `bleach`.

Die Funktion ist intentionally pure (keine Streamlit-Abhängigkeit) so dass
Unit-Tests sie einfach nutzen können. Streamlit-Wrapper kann die Funktion
mit `@st.cache_data` umgeben.
"""
from __future__ import annotations

import json
import io
import csv
from typing import Any, Iterable, Optional
from pathlib import Path
import re

from markdown_it import MarkdownIt
from examples.math_utils import render_markdown_with_math
import logging

try:
    import bleach
except Exception:  # pragma: no cover - bleach optional in some environments
    bleach = None


logger = logging.getLogger(__name__)


DEFAULT_ALLOWED_TAGS = [
    "p",
    "div",
    "span",
    "ol",
    "ul",
    "li",
    "strong",
    "em",
    "a",
    "img",
    "code",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "dl",
    "dt",
    "dd",
]

DEFAULT_ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "div": ["class"],
    "span": ["class"],
}


def _fallback_title_from_source(source_name: Optional[str]) -> str:
    if not source_name:
        return ""

    stem = Path(source_name).stem
    if stem.startswith("questions_"):
        stem = stem[len("questions_"):]

    stem = stem.replace("_", " ").strip()
    return stem


def _sanitize(html: str) -> str:
    if not html:
        return ""
    if bleach is None:
        # If bleach not installed, return input (best-effort). Caller should
        # ensure the environment includes bleach for production.
        return html
    cleaned = bleach.clean(
        html,
        tags=DEFAULT_ALLOWED_TAGS,
        attributes=DEFAULT_ALLOWED_ATTRS,
        strip=True,
    )
    if cleaned != html:
        # Log sanitized differences for later review (truncate to keep logs readable).
        original_snippet = html if len(html) <= 400 else html[:400] + "…"
        cleaned_snippet = cleaned if len(cleaned) <= 400 else cleaned[:400] + "…"
        logger.warning(
            "Anki TSV sanitizer stripped content",
            extra={
                "anki_sanitize_original": original_snippet,
                "anki_sanitize_cleaned": cleaned_snippet,
            },
        )
    return _restore_math_backslash_breaks(cleaned)


_SINGLE_MATH_BREAK = re.compile(r"(?<!\\)\\(?=\s)")


def _restore_math_backslash_breaks(html: str) -> str:
    if not html or "\\" not in html:
        return html
    # Ensure MathJax receives double backslashes for line breaks in matrices.
    return _SINGLE_MATH_BREAK.sub(r"\\\\", html)


def _map_schwierigkeit(value: Any) -> str:
    try:
        v = int(value)
    except Exception:
        return "mittel"
    return {1: "leicht", 2: "mittel", 3: "schwer"}.get(v, "mittel")


def _strip_wrapping_paragraph(html: str) -> str:
    if not html:
        return ""
    stripped = html.strip()
    if stripped.startswith("<p>") and stripped.endswith("</p>"):
        return stripped[3:-4]
    return stripped


def _render_extended_explanation(md: MarkdownIt, value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, dict):
        return _render_extended_dict(md, value)
    return _sanitize(render_markdown_with_math(md, str(value)).strip())


def _render_extended_dict(md: MarkdownIt, data: dict[str, Any]) -> str:
    parts: list[str] = []

    title_html = _render_extended_title(md, data.get("title") or data.get("titel"))
    if title_html:
        parts.append(title_html)

    steps_html = _render_extended_steps(md, data.get("schritte"))
    if steps_html:
        parts.append(steps_html)

    content_html = _render_extended_content(md, data.get("content"))
    if content_html:
        parts.append(content_html)

    if not parts:
        fallback = _sanitize(render_markdown_with_math(md, str(data)).strip())
        if fallback:
            parts.append(fallback)

    return _sanitize("".join(parts))


def _render_extended_title(md: MarkdownIt, title: Any) -> str:
    if not title:
        return ""
    title_html = render_markdown_with_math(md, str(title)).strip()
    title_html = _strip_wrapping_paragraph(title_html)
    title_html = _sanitize(title_html)
    return f"<h3>{title_html}</h3>" if title_html else ""


def _render_extended_steps(md: MarkdownIt, steps: Any) -> str:
    if not isinstance(steps, Iterable):
        return ""
    items: list[str] = []
    for step in steps:
        rendered_step = _sanitize(render_markdown_with_math(md, str(step)).strip())
        if rendered_step:
            items.append(f"<li>{rendered_step}</li>")
    if not items:
        return ""
    return "<ol>" + "".join(items) + "</ol>"


def _render_extended_content(md: MarkdownIt, content: Any) -> str:
    if not isinstance(content, str) or not content.strip():
        return ""
    return _sanitize(render_markdown_with_math(md, content).strip())


def _render_options(md: MarkdownIt, options: list[Any]) -> str:
    if not options:
        return "<ol type=\"A\"></ol>"
    items = [
        f"<li>{_sanitize(render_markdown_with_math(md, opt).strip())}</li>"
        for opt in options
    ]
    return "<ol type=\"A\">" + "".join(items) + "</ol>"


def _render_correct_answer(md: MarkdownIt, options: list[Any], index: Any) -> str:
    if not options:
        return ""
    try:
        idx = int(index)
    except Exception:
        return ""
    if idx < 0 or idx >= len(options):
        return ""
    return _sanitize(render_markdown_with_math(md, options[idx]).strip())


def _render_glossary(md: MarkdownIt, glossary: Any) -> str:
    if not isinstance(glossary, dict) or not glossary:
        return ""
    parts = ["<dl>"]
    for term, definition in glossary.items():
        parts.append(f"<dt>{_sanitize(str(term))}</dt>")
        parts.append(f"<dd>{_sanitize(render_markdown_with_math(md, str(definition)).strip())}</dd>")
    parts.append("</dl>")
    return "".join(parts)


def _build_tags(title: Any, thema: Any, gewichtung: Any) -> str:
    parts: list[str] = []
    if title:
        parts.append(str(title).replace(" ", "_"))
    if thema:
        parts.append(str(thema).replace(" ", "_"))
    if gewichtung not in (None, ""):
        parts.append(f"Gewichtung_{gewichtung}")
    return " ".join(p for p in parts if p).strip()


def _build_row(md: MarkdownIt, question: dict[str, Any], title: str) -> list[str]:
    frage_html = render_markdown_with_math(md, question.get("frage", "")).strip()
    frage_field = _sanitize(_strip_wrapping_paragraph(frage_html))

    options = question.get("optionen", []) or []
    options_html = _render_options(md, options)

    correct_text = _render_correct_answer(md, options, question.get("loesung", 0))

    erklaerung = _sanitize(render_markdown_with_math(md, question.get("erklaerung", "")).strip())
    extended = _render_extended_explanation(md, question.get("extended_explanation"))

    gloss_html = _render_glossary(md, question.get("mini_glossary"))

    thema = question.get("thema", "")
    schwierigkeit = _map_schwierigkeit(question.get("gewichtung", ""))
    tags = _build_tags(title, thema, question.get("gewichtung", ""))

    return [
        frage_field,
        options_html,
        correct_text,
        erklaerung,
        extended,
        gloss_html,
        title,
        thema,
        schwierigkeit,
        tags,
    ]


def transform_to_anki_tsv(json_bytes: bytes, *, source_name: str | None = None) -> str:
    """Transform JSON bytes (app format) to a TSV string for Anki import.

    Contract: see `README_EXPORT_ANKI.md`.
    """
    data = json.loads(json_bytes.decode("utf-8"))
    # Support legacy files that contain a top-level list of questions
    # instead of an object with a `questions` key.
    if isinstance(data, list):
        data = {"meta": {}, "questions": data}
    md = MarkdownIt()
    out = io.StringIO()
    writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    meta = data.get("meta", {}) or {}
    raw_title = meta.get("title") or meta.get("name") or ""
    if isinstance(raw_title, str):
        title = raw_title.strip()
    elif raw_title is None:
        title = ""
    else:
        title = str(raw_title).strip()

    # If the title is missing or the generic 'pasted' placeholder, prefer
    # the question-set 'thema' or the first question's 'thema' so exported
    # filenames and the Anki "Fragenset" field are user-friendly.
    if not title or title == "pasted":
        tema = meta.get("thema")
        if not tema:
            try:
                q0 = data.get("questions", [])[0]
                if isinstance(q0, dict):
                    tema = q0.get("thema")
            except Exception:
                tema = None
        if tema:
            title = str(tema).strip()

    if not title:
        title = _fallback_title_from_source(source_name)

    if not title:
        title = "MC-Test Deck"

    for q in data.get("questions", []):
        writer.writerow(_build_row(md, q, title))

    return out.getvalue()
