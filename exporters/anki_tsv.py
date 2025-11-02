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
from typing import Any

from markdown_it import MarkdownIt
from examples.math_utils import render_markdown_with_math

try:
    import bleach
except Exception:  # pragma: no cover - bleach optional in some environments
    bleach = None


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


def _sanitize(html: str) -> str:
    if not html:
        return ""
    if bleach is None:
        # If bleach not installed, return input (best-effort). Caller should
        # ensure the environment includes bleach for production.
        return html
    return bleach.clean(html, tags=DEFAULT_ALLOWED_TAGS, attributes=DEFAULT_ALLOWED_ATTRS, strip=True)


def _map_schwierigkeit(value: Any) -> str:
    try:
        v = int(value)
    except Exception:
        return "mittel"
    return {1: "leicht", 2: "mittel", 3: "schwer"}.get(v, "mittel")


def transform_to_anki_tsv(json_bytes: bytes) -> str:
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
    title = meta.get("title", "")

    for q in data.get("questions", []):
        # Frage
        frage_html = render_markdown_with_math(md, q.get("frage", ""))
        frage_html = frage_html.strip()
        # Strip outer <p> for single-paragraph legacy compatibility
        if frage_html.startswith("<p>") and frage_html.endswith("</p>"):
            frage_field = frage_html[3:-4]
        else:
            frage_field = frage_html

        # Optionen
        options = q.get("optionen", []) or []
        options_html = "<ol type=\"A\">" + "".join(
            f"<li>{_sanitize(render_markdown_with_math(md, opt).strip())}</li>" for opt in options
        ) + "</ol>"

        # Richtige Antwort
        loesung_idx = q.get("loesung", 0)
        correct_text = ""
        try:
            if options:
                correct_text = _sanitize(render_markdown_with_math(md, options[int(loesung_idx)]).strip())
        except Exception:
            correct_text = ""

        # Erklärungen
        erklaerung = _sanitize(render_markdown_with_math(md, q.get("erklaerung", "")))
        extended = _sanitize(render_markdown_with_math(md, str(q.get("extended_explanation", ""))))

        # Glossar (mini_glossary) -> dl
        gloss_html = ""
        mg = q.get("mini_glossary") or {}
        if isinstance(mg, dict) and mg:
            parts = ["<dl>"]
            for term, definition in mg.items():
                parts.append(f"<dt>{_sanitize(str(term))}</dt>")
                parts.append(f"<dd>{_sanitize(render_markdown_with_math(md, str(definition)))}</dd>")
            parts.append("</dl>")
            gloss_html = "".join(parts)

        thema = q.get("thema", "")
        schwierigkeit = _map_schwierigkeit(q.get("gewichtung", ""))

        # Tags: meta.title + thema + gewichtung
        tags_parts = [str(title).replace(" ", "_") if title else "", str(thema).replace(" ", "_") if thema else "", f"Gewichtung_{q.get('gewichtung', '')}"]
        tags = " ".join([p for p in tags_parts if p]).strip()

        row = [
            _sanitize(frage_field),
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

        writer.writerow(row)

    return out.getvalue()
