"""Text and formatting utilities extracted from the legacy `helpers.py`.
"""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from typing import Optional, Union
import html as _html

SAFE_HTML_TAGS = {
    "b",
    "strong",
    "i",
    "em",
    "u",
    "sup",
    "sub",
    "code",
    "pre",
    "br",
    "p",
    "ul",
    "ol",
    "li",
}

_VOID_HTML_TAGS = {"br"}


class _SafeHTMLSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._parts: list[str] = []
        self.modified: bool = False

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS:
            if attrs:
                self.modified = True
            self._parts.append(f"<{tag}>")
        else:
            self.modified = True
            self._parts.append(_html.escape(f"<{tag}>", quote=False))

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS and tag not in _VOID_HTML_TAGS:
            self._parts.append(f"</{tag}>")
        else:
            self.modified = True
            self._parts.append(_html.escape(f"</{tag}>", quote=False))

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS:
            if attrs:
                self.modified = True
            if tag in _VOID_HTML_TAGS:
                self._parts.append(f"<{tag}>")
            else:
                self._parts.append(f"<{tag}></{tag}>")
        else:
            self.modified = True
            self._parts.append(_html.escape(f"<{tag}>", quote=False))

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if data:
            self._parts.append(_html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.modified = True

    def handle_decl(self, decl: str) -> None:
        self.modified = True

    def handle_pi(self, data: str) -> None:
        self.modified = True

    def get_sanitized_html(self) -> str:
        return "".join(self._parts)


def sanitize_html(value: str) -> tuple[str, bool]:
    if not value:
        return "", False
    parser = _SafeHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return parser.get_sanitized_html(), parser.modified


def get_user_id_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()


def smart_quotes_de(text: str) -> str:
    if not text:
        return text

    quote_chars = set(["'", '"', '\u2018', '\u2019', '\u201A', '\u201C', '\u201D', '\u201E', '\u00BB', '\u00AB'])
    if not any((c in text) for c in quote_chars):
        return text

    segments = re.split(r'(<pre[\s\S]*?</pre>|<code[\s\S]*?</code>)', text, flags=re.I)

    def _convert_segment(seg: str) -> str:
        katex_pattern = re.compile(r'(\${1,2}.*?\${1,2})')
        parts = katex_pattern.split(seg)
        result_parts = []
        quote_stack: list[tuple[str, str]] = []
        open_map = {'double': '„', 'single': '‚'}
        close_map = {'double': '“', 'single': '‘'}

        for i, part in enumerate(parts):
            if i % 2 == 0:
                processed_part = []
                single_quote_chars = {"'", "\u2018", "\u2019", "\u201A"}
                for char_idx, ch in enumerate(part):
                    if ch in single_quote_chars:
                        is_apostrophe = (
                            char_idx > 0
                            and part[char_idx - 1].isalpha()
                            and char_idx < len(part) - 1
                            and part[char_idx + 1].isalpha()
                        )
                        if is_apostrophe:
                            processed_part.append("’")
                            continue
                        if quote_stack and quote_stack[-1][1] == ch:
                            entry_type, _ = quote_stack.pop()
                            processed_part.append(close_map.get(entry_type, '’'))
                        else:
                            if quote_stack and quote_stack[-1][0] == 'double':
                                quote_stack.append(('single', ch))
                                processed_part.append(open_map['single'])
                            else:
                                quote_stack.append(('double', ch))
                                processed_part.append(open_map['double'])
                    elif ch == '"':
                        if quote_stack and quote_stack[-1][1] == '"':
                            entry_type, _ = quote_stack.pop()
                            processed_part.append(close_map.get(entry_type, '“'))
                        else:
                            quote_stack.append(('double', '"'))
                            processed_part.append(open_map['double'])
                    else:
                        processed_part.append(ch)
                result_parts.append("".join(processed_part))
            else:
                result_parts.append(part)

        return "".join(result_parts)

    out_parts = []
    for seg in segments:
        if not seg:
            continue
        if seg.lower().startswith('<pre') or seg.lower().startswith('<code'):
            out_parts.append(seg)
        else:
            out_parts.append(_convert_segment(seg))

    return "".join(out_parts)


def normalize_detailed_explanation(value) -> dict | None:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        parsed = None
        try:
            import json as _json
            if s.startswith('{') or s.startswith('['):
                try:
                    parsed = _json.loads(s)
                except Exception:
                    parsed = None
        except Exception:
            parsed = None
        if parsed is None and (s.startswith('{') or s.startswith('[')):
            try:
                import ast
                parsed = ast.literal_eval(s)
            except Exception:
                parsed = None
        if parsed is None:
            try:
                m = re.match(r"^\s*(\{.*?\})\s*[:\-–—]\s*(.*)$", s, flags=re.S)
            except Exception:
                m = None
            if m:
                head, tail = m.group(1), m.group(2).strip()
                try:
                    import json as _json
                    try:
                        parsed_head = _json.loads(head)
                    except Exception:
                        parsed_head = None
                except Exception:
                    parsed_head = None
                if parsed_head is None:
                    try:
                        import ast
                        parsed_head = ast.literal_eval(head)
                    except Exception:
                        parsed_head = None
                if isinstance(parsed_head, dict):
                    if not parsed_head.get('content'):
                        parsed_head['content'] = tail or parsed_head.get('content')
                    parsed = parsed_head
        if isinstance(parsed, (dict, list)):
            value = parsed
        else:
            return {"title": "", "content": s, "steps": None}

    if isinstance(value, dict):
        title = value.get("title") or value.get("titel") or value.get("heading") or ""
        content = value.get("content") or value.get("inhalt") or value.get("text") or None
        steps_candidate = value.get("steps") or value.get("schritte") or value.get("list") or None
        steps = None
        if isinstance(steps_candidate, list):
            cleaned = [str(s).strip() for s in steps_candidate if s is not None and str(s).strip()]
            steps = cleaned if cleaned else None
        elif isinstance(steps_candidate, str):
            parts = [p.strip() for p in re.split(r"\r?\n", steps_candidate) if p.strip()]
            steps = parts if parts else None
        if content is None:
            for k, v in value.items():
                if k.lower() in {"title", "titel", "steps", "schritte", "list"}:
                    continue
                if isinstance(v, str) and v.strip():
                    content = v.strip()
                    break
        try:
            import json as _json
        except Exception:
            _json = None
        if title is None:
            title = ""
        elif not isinstance(title, str):
            try:
                title = _json.dumps(title, ensure_ascii=False) if _json else str(title)
            except Exception:
                title = str(title)
        else:
            title = title.strip()
        if content is None:
            content = None
        elif not isinstance(content, str):
            try:
                content = _json.dumps(content, ensure_ascii=False) if _json else str(content)
            except Exception:
                content = str(content)
        else:
            content = content.strip() or None
        if not title and not content and not steps:
            return None
        return {"title": title, "content": content, "steps": steps}

    try:
        s = str(value).strip()
        return {"title": "", "content": s, "steps": None} if s else None
    except Exception:
        return None


def format_decimal_de(value: float, decimals: int = 1) -> str:
    decimals = max(0, int(decimals))
    formatted = f"{value:.{decimals}f}"
    return formatted.replace(".", ",")


def load_markdown_file(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def format_datetime_de(ts, fmt: str = '%d.%m.%Y %H:%M:%S'):
    try:
        import pandas as _pd
        from datetime import timezone
        if isinstance(ts, _pd.Series):
            s = _pd.to_datetime(ts, utc=True, errors='coerce')
            try:
                from zoneinfo import ZoneInfo
                berlin = ZoneInfo("Europe/Berlin")
                s = s.dt.tz_convert(berlin)
            except Exception:
                pass
            formatted = s.dt.strftime(fmt)
            return formatted.fillna("-")
        dt = None
        try:
            dt = _pd.to_datetime(ts, utc=True, errors='coerce')
        except Exception:
            return '-'
        if _pd.isna(dt):
            return '-'
        try:
            from zoneinfo import ZoneInfo
            berlin = ZoneInfo("Europe/Berlin")
            dt = dt.tz_convert(berlin)
        except Exception:
            pass
        return dt.strftime(fmt)
    except Exception:
        try:
            return str(ts)
        except Exception:
            return '-'
