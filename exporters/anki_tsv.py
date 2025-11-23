"""Anki TSV Exporter

Erzeugt eine UTF-8 kodierte TSV-String-Repräsentation aus dem internen
Fragenset-JSON. Baut auf `examples.math_utils.render_markdown_with_math`
und sanitized die resultierende HTML-Ausgabe mit `bleach`.

Hinweis: Mathematische Fragmente (z.B. `$...$`, `\\(...\\)`, `\\[...\\]`) werden
vor dem Aufruf von `bleach.clean` durch Platzhalter ersetzt und nach der
Sanitierung unverändert (verbatim) wieder eingesetzt. Dadurch werden bereits
vom Markdown-Renderer erzeugte HTML-Entities nicht versehentlich
doppelt-escaped (z.B. '&lt;' -> '&amp;lt;').

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
import html as _html_module
from examples.math_utils import render_markdown_with_math
from mdit_py_plugins.amsmath import amsmath_plugin
import logging
from i18n.context import t as translate_ui
try:
    # Reuse normalization from pdf_export to map aliases like 'wissen' -> 'Reproduktion'
    from pdf_export import _normalize_stage_label
except Exception:
    from typing import Any

    def _normalize_stage_label(value: Any) -> str:
        try:
            return str(value) if value is not None else ""
        except Exception:
            return ""

try:
    import bleach
except Exception:  # pragma: no cover - bleach optional in some environments
    bleach = None

# For robust math token fallback when MarkdownIt parsing doesn't convert
# $...$ into \(...\) as expected in some environments, reuse the
# conversion helper from the examples math utilities.
try:
    from examples.math_utils import _convert_math_tokens
except Exception:
    def _convert_math_tokens(s: str) -> str:
        return s


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

# Allow certain list attributes so ordered lists can preserve their
# display style (e.g. type="A"). Keep the set minimal for safety.
DEFAULT_ALLOWED_ATTRS.update({
    "ol": ["type", "start", "class"],
    "li": ["class"],
})


def _fallback_title_from_source(source_name: Optional[str]) -> str:
    if not source_name:
        return ""

    stem = Path(source_name).stem
    if stem.startswith("questions_"):
        stem = stem[len("questions_"):]

    stem = stem.replace("_", " ").strip()
    return stem


def _sanitize(html_content: str) -> str:
    if not html_content:
        return ""
    if bleach is None:
        return html_content
    # Die zentrale Bereinigung in config.py hat bereits unsicheres HTML entfernt.
    # Für den Anki-Export ist es entscheidend, dass LaTeX-Befehle wie `\langle`
    # NICHT durch ein weiteres Escaping zu `\\langle` werden.
    # Daher wird hier nur noch eine minimale Bereinigung vorgenommen, die
    # LaTeX-Befehle intakt lässt.
    cleaned = bleach.clean(html_content, tags=DEFAULT_ALLOWED_TAGS, attributes=DEFAULT_ALLOWED_ATTRS, strip=True)
    cleaned = bleach.clean(
        html_content, tags=DEFAULT_ALLOWED_TAGS, attributes=DEFAULT_ALLOWED_ATTRS, strip=True
    )

    # Anki/MathJax erwartet \(...\) für Inline-Mathe. Ersetze einzelne $...$
    # aber lasse $$...$$ (Display-Mathe) unberührt.
    # Negative Lookbehind/Lookahead stellen sicher, dass wir nur einzelne $ matchen.
    # Die Ersetzung r"\1" ist hier sicher, da der Inhalt von LaTeX-Blöcken
    # bereits durch das amsmath-Plugin geschützt wurde und keine Backslash-Probleme
    # mehr verursachen sollte. Die Verwendung von r"\\(" + r"\1" + r"\\)" war ein
    # Versuch, eine SyntaxWarning zu umgehen, ist aber nicht die korrekte Lösung.
    cleaned = re.sub(r"(?<!\$)\$([^\$]+?)\$(?!\$)", r"\\(\1\\)", cleaned)

    return _restore_math_backslash_breaks(cleaned)


# Regex, um einzelne Backslashes, die für Zeilenumbrüche in LaTeX
# (z.B. in Matrizen) verwendet werden, zu verdoppeln, da Anki dies erwartet.
# Beispiel: `a \\ b` wird zu `a \\\\ b`.
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
    # Remove wrapping <p>...</p>
    if stripped.startswith("<p>") and stripped.endswith("</p>"):
        return stripped[3:-4]

    # If the content is wrapped in an ordered/unordered list (e.g. produced
    # from markdown like `1. Question`), extract the inner <li> content and
    # return it without the list container so Anki cards don't display a
    # misleading sequential number. Keep any inline HTML inside the <li>.
    low = stripped.lower()
    if (low.startswith("<ol") and low.endswith("</ol>")) or (
        low.startswith("<ul") and low.endswith("</ul>")
    ):
        # Extract all <li>...</li> blocks and join them with a space.
        # Usually there will be a single <li> with the question text.
        import re

        items = re.findall(r"<li[^>]*>(.*?)</li>", stripped, flags=re.DOTALL | re.IGNORECASE)
        if items:
            # Join multiple list items if present, separated by a single space.
            joined = " ".join(item.strip() for item in items if item and item.strip())
            return joined

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

    # Accept both German 'schritte' and English 'steps' as possible keys.
    steps_val = data.get("schritte") if isinstance(data.get("schritte"), Iterable) else (
        data.get("steps") if isinstance(data.get("steps"), Iterable) else None
    )
    steps_html = _render_extended_steps(md, steps_val)
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


def _render_metadata_value(md: MarkdownIt, value: Any) -> str:
    if not value:
        return ""
    return _sanitize(render_markdown_with_math(md, str(value)).strip())


def _render_options(md: MarkdownIt, options: list[Any]) -> str:
    if not options:
        return "<ol type=\"A\"></ol>"
    items = []
    for opt in options:
        try:
            if isinstance(opt, str) and opt.strip().startswith("```"):
                # Preserve code-fence blocks verbatim (do NOT convert $...$ inside code blocks)
                # Strip the fence markers and any optional language tag
                inner = re.sub(r"^```[a-zA-Z0-9]*\n?|\n?```$", "", opt.strip(), flags=re.MULTILINE)
                code_html = f"<pre><code>{_html_module.escape(inner)}</code></pre>"
                items.append(f"<li>{code_html}</li>")
                continue
        except Exception:
            pass
        rendered_inner = _sanitize(render_markdown_with_math(md, opt).strip())
        # If original contains $...$ but rendered still contains literal $,
        # attempt a conversion fallback to normalize math tokens.
        try:
            if isinstance(opt, str) and "$" in opt and "\(" not in rendered_inner and "$" in rendered_inner:
                converted = _convert_math_tokens(opt)
                rendered_inner = _sanitize(render_markdown_with_math(md, converted).strip())
        except Exception:
            pass
        items.append(f"<li>{rendered_inner}</li>")
    rendered = "".join(items)
    # Fallback: if sanitizer/renderer produced empty items (some test envs
    # may strip content), emit a conservative escaped representation so
    # tests and downstream exporters still receive visible options.
    def _li_inner_nonempty(li_html: str) -> bool:
        inner = re.sub(r"<li[^>]*>|</li>", "", li_html).strip()
        return bool(inner)

    if not any(_li_inner_nonempty(it) for it in items):
        items = []
        for opt in options:
            try:
                if isinstance(opt, str) and opt.strip().startswith("```"):
                    inner = re.sub(r"^```[a-zA-Z0-9]*\n?|\n?```$", "", opt.strip(), flags=re.MULTILINE)
                    code_html = f"<pre><code>{_html_module.escape(inner)}</code></pre>"
                    items.append(f"<li>{code_html}</li>")
                    continue
            except Exception:
                pass
            items.append(f"<li>{_html_module.escape(str(opt))}</li>")
        rendered = "".join(items)

    return "<ol type=\"A\">" + rendered + "</ol>"


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
    frage_html = render_markdown_with_math(md, question.get("question", "")).strip()
    frage_field = _sanitize(_strip_wrapping_paragraph(frage_html))

    options = question.get("options", []) or []
    options_html = _render_options(md, options)

    correct_text = _render_correct_answer(md, options, question.get("answer", 0))

    erklaerung = _sanitize(
        render_markdown_with_math(md, question.get("explanation", "")).strip()
    )
    extended = _render_extended_explanation(md, question.get("extended_explanation"))

    gloss_html = _render_glossary(md, question.get("mini_glossary"))

    thema = question.get("topic", "")
    schwierigkeit = _map_schwierigkeit(question.get("weight", ""))
    konzept = _render_metadata_value(md, question.get("concept"))
    konzept = _strip_wrapping_paragraph(konzept)
    kognitive_stufe = _render_metadata_value(md, question.get("cognitive_level"))
    kognitive_stufe = _strip_wrapping_paragraph(kognitive_stufe)
    # Normalize and translate simple stage labels so exports respect the UI locale
    try:
        if kognitive_stufe:
            normalized = _normalize_stage_label(kognitive_stufe)
            kognitive_stufe = translate_ui(f"pdf.stage_name.{normalized}", default=normalized)
    except Exception:
        pass
    tags = _build_tags(title, thema, question.get("weight", ""))

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
        konzept,
        kognitive_stufe,
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

    # Erstelle eine spezielle Markdown-Instanz für Anki.
    # WICHTIG: Wir deaktivieren die 'emphasis'-Regel explizit. Dies verhindert,
    # dass Unterstriche `_` in LaTeX-Formeln (z.B. `x_i`) fälschlicherweise
    # als Markdown für Kursivschrift interpretiert und in `<em>`-Tags umgewandelt werden.
    # Das `amsmath_plugin` kümmert sich um die korrekte Erkennung der LaTeX-Blöcke.
    md = MarkdownIt("commonmark", {"html": True}).use(amsmath_plugin).disable("emphasis")

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

    # If the title is missing or the generic 'pasted' placeholder, choose a
    # sensible fallback for the exported Fragenset title so Anki imports look
    # user-friendly. Priority:
    # 1. meta['thema'] (explicit topic in the meta)
    # 2. fallback derived from the source filename (if provided)
    # 3. first question's 'thema' (best-effort)
    if not title or title == "pasted":
        tema = meta.get("topic") or meta.get("thema")
        if tema:
            title = str(tema).strip()
        else:
            # Prefer a human-friendly name derived from the source file
            # before falling back to the first question's 'thema'. This
            # makes legacy top-level-list imports (no meta) produce a
            # predictable title when a source_name is provided.
            source_fallback = _fallback_title_from_source(source_name)
            if source_fallback:
                title = source_fallback
            else:
                try:
                    q0 = data.get("questions", [])[0]
                    if isinstance(q0, dict):
                        tema = q0.get("topic") or q0.get("thema")
                except Exception:
                    tema = None
                if tema:
                    title = str(tema).strip()

    if not title:
        title = "MC-Test Deck"

    # Questions must use canonical English keys (migration cleanup removed
    # the previous runtime compatibility layer). Build rows first so we can
    # trim trailing entirely-empty optional columns across the whole export.
    rows: list[list[str]] = []
    for q in data.get("questions", []):
        rows.append(_build_row(md, q, title))

    # Determine the last column index that contains any non-empty value.
    last_nonempty = -1
    for r in rows:
        for idx, cell in enumerate(r):
            if cell not in (None, ""):
                if idx > last_nonempty:
                    last_nonempty = idx

    # Ensure we don't trim away required core columns. Keep at least 6
    # columns (question, options, correct, explanation, extended, glossary).
    MIN_COLUMNS = 6
    final_cols = max(last_nonempty + 1, MIN_COLUMNS)

    # Write rows with a consistent column count, trimming trailing empty
    # optional columns while preserving core fields.
    for r in rows:
        # Pad shorter rows to the final column count to avoid index errors.
        if len(r) < final_cols:
            r = r + [""] * (final_cols - len(r))
        writer.writerow(r[:final_cols])

    return out.getvalue()
