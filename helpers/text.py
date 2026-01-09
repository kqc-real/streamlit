"""Text and formatting utilities extracted from the legacy `helpers.py`.
"""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from typing import Optional, Union
import html as _html

# Reusable date/time format presets (numeric, locale-adjusted in format_datetime_locale)
FMT_DATETIME_SECONDS = "%d.%m.%Y %H:%M:%S"
FMT_DATETIME = "%d.%m.%Y %H:%M"
FMT_DATETIME_SHORT_YEAR = "%d.%m.%y %H:%M"
FMT_DATE = "%d.%m.%Y"
FMT_DATE_SHORT = "%d.%m.%y"
_DECIMAL_COMMA_LOCALES = {"de", "fr", "es", "it"}

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


def format_decimal_locale(value: float, decimals: int = 1, locale: str | None = None) -> str:
    """Format a decimal number with locale-aware separators."""
    try:
        decimals = max(0, int(decimals))
    except Exception:
        decimals = 1

    try:
        from i18n import normalize_locale
        from i18n.context import get_locale as _get_locale

        locale_code = normalize_locale(locale or _get_locale())
    except Exception:
        locale_code = "en"

    try:
        from babel.numbers import format_decimal as _babel_decimal

        pattern = f"#.{ '0' * decimals}" if decimals else "#"
        return _babel_decimal(value, format=pattern, locale=locale_code)
    except Exception:
        pass

    try:
        formatted = f"{value:.{decimals}f}"
    except Exception:
        formatted = str(value)

    if locale_code in _DECIMAL_COMMA_LOCALES:
        return formatted.replace(".", ",")
    return formatted


def format_decimal_de(value: float, decimals: int = 1) -> str:
    return format_decimal_locale(value, decimals=decimals, locale="de")


def load_markdown_file(path: str) -> str | None:
    try:
        raw = None
        with open(path, "rb") as f:
            raw = f.read()
        if raw is None:
            return None

        # Prefer UTF-8, but tolerate common variants/legacy encodings so
        # Learning Objectives Markdown files created on different systems
        # still load in the app.
        for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        # Last resort: return a best-effort UTF-8 decode to avoid failing UI.
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return None


def format_datetime_locale(ts, fmt: str = FMT_DATETIME_SECONDS, locale: str | None = None):
    """Format timestamps according to the active UI locale.

    - Accepts pandas Series, pandas/py datetime, ISO strings, or epoch numbers.
    - Tries to use Babel (if installed) for locale-aware month/day names.
    - Falls back to per-locale strftime patterns so we still localize ordering.
    """
    try:
        import pandas as _pd
    except Exception:
        _pd = None

    try:
        from i18n import normalize_locale
        from i18n.context import get_locale as _get_locale
        locale_code = normalize_locale(locale or _get_locale())
    except Exception:
        locale_code = "en"

    _STYLE_ALIASES = {
        FMT_DATETIME_SECONDS: "datetime_seconds",
        FMT_DATETIME: "datetime",
        FMT_DATETIME_SHORT_YEAR: "datetime_short_year",
        FMT_DATE: "date",
        FMT_DATE_SHORT: "date_short",
    }
    _STYLE_FORMATS = {
        "datetime_seconds": {
            "de": "%d.%m.%Y %H:%M:%S",
            "fr": "%d/%m/%Y %H:%M:%S",
            "es": "%d/%m/%Y %H:%M:%S",
            "it": "%d/%m/%Y %H:%M:%S",
            "zh": "%Y-%m-%d %H:%M:%S",
            "en": "%Y-%m-%d %H:%M:%S",
        },
        "datetime": {
            "de": "%d.%m.%Y %H:%M",
            "fr": "%d/%m/%Y %H:%M",
            "es": "%d/%m/%Y %H:%M",
            "it": "%d/%m/%Y %H:%M",
            "zh": "%Y-%m-%d %H:%M",
            "en": "%Y-%m-%d %H:%M",
        },
        "datetime_short_year": {
            "de": "%d.%m.%y %H:%M",
            "fr": "%d/%m/%y %H:%M",
            "es": "%d/%m/%y %H:%M",
            "it": "%d/%m/%y %H:%M",
            "zh": "%y-%m-%d %H:%M",
            "en": "%y-%m-%d %H:%M",
        },
        "date": {
            "de": "%d.%m.%Y",
            "fr": "%d/%m/%Y",
            "es": "%d/%m/%Y",
            "it": "%d/%m/%Y",
            "zh": "%Y-%m-%d",
            "en": "%Y-%m-%d",
        },
        "date_short": {
            "de": "%d.%m.%y",
            "fr": "%d/%m/%y",
            "es": "%d/%m/%y",
            "it": "%d/%m/%y",
            "zh": "%y-%m-%d",
            "en": "%y-%m-%d",
        },
    }
    style = _STYLE_ALIASES.get(fmt)
    if fmt is None:
        style = "datetime_seconds"
    fmt_to_use = None
    if style:
        fmt_to_use = _STYLE_FORMATS.get(style, {}).get(locale_code) or _STYLE_FORMATS.get(style, {}).get("en")
    if not fmt_to_use:
        fmt_to_use = fmt or "%Y-%m-%d %H:%M:%S"

    def _resolve_tz_info():
        try:
            from zoneinfo import ZoneInfo

            return ZoneInfo("Europe/Berlin")
        except Exception:
            return None

    berlin_tz = _resolve_tz_info()

    _DAYFIRST_LOCALES = {"de", "fr", "es", "it"}
    dayfirst_flag = locale_code in _DAYFIRST_LOCALES

    def _looks_dayfirst_string(val: Any) -> bool:
        try:
            s = str(val)
        except Exception:
            return False
        return bool(re.search(r"\d{1,2}\.\d{1,2}\.\d{2,4}", s))

    def _looks_iso_ymd_string(val: Any) -> bool:
        try:
            s = str(val)
        except Exception:
            return False
        # Matches 2024-12-31T23:59:59+0100 or +01:00 (with optional milliseconds/Z)
        return bool(
            re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$", s)
        )

    def _format_series(series_obj):
        if _pd is None:
            return series_obj
        try:
            # If the series seems to contain day-first dotted dates, force dayfirst=True to avoid warnings.
            series_dayfirst = dayfirst_flag
            try:
                if not series_dayfirst and _pd.api.types.is_object_dtype(series_obj):
                    sample = series_obj.dropna().astype(str).head(5)
                    if any(_looks_dayfirst_string(v) for v in sample):
                        series_dayfirst = True
                    if any(_looks_iso_ymd_string(v) for v in sample):
                        series_dayfirst = False
            except Exception:
                pass
            if _pd.api.types.is_numeric_dtype(series_obj):
                # Heuristic: values above 1e12 are likely milliseconds
                try:
                    max_val = series_obj.max()
                    unit = "ms" if max_val and abs(max_val) > 1_000_000_000_000 else "s"
                except Exception:
                    unit = "s"
                s = _pd.to_datetime(series_obj, unit=unit, utc=True, errors="coerce")
            else:
                s = _pd.to_datetime(series_obj, utc=True, errors="coerce", dayfirst=series_dayfirst)
            if berlin_tz is not None:
                try:
                    s = s.dt.tz_convert(berlin_tz)
                except Exception:
                    pass
            formatted = s.dt.strftime(fmt_to_use)
            return formatted.fillna("-")
        except Exception:
            return series_obj

    def _coerce_scalar(value):
        if _pd is None:
            return None
        try:
            if isinstance(value, _pd.Timestamp):
                return value
            if isinstance(value, (int, float)):
                unit = "s"
                if abs(value) > 1_000_000_000_000:
                    unit = "ms"
                return _pd.to_datetime(value, unit=unit, utc=True, errors="coerce")
            force_dayfirst = dayfirst_flag or _looks_dayfirst_string(value)
            if _looks_iso_ymd_string(value):
                force_dayfirst = False
            return _pd.to_datetime(value, utc=True, errors="coerce", dayfirst=force_dayfirst)
        except Exception:
            return None

    def _apply_tz(dt_obj):
        if berlin_tz is None or dt_obj is None:
            return dt_obj
        try:
            if getattr(dt_obj, "tzinfo", None) is None:
                return dt_obj.replace(tzinfo=berlin_tz)
            return dt_obj.astimezone(berlin_tz)
        except Exception:
            return dt_obj

    # Series support
    if _pd is not None and isinstance(ts, _pd.Series):
        return _format_series(ts)

    # Scalar support
    dt = _coerce_scalar(ts)
    if dt is None:
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(str(ts))
        except Exception:
            try:
                return str(ts)
            except Exception:
                return "-"

    if _pd is not None and _pd.isna(dt):
        return "-"

    try:
        dt = _apply_tz(dt)
    except Exception:
        pass

    # Prefer explicit format strings; only use Babel when no format was requested.
    if fmt is None:
        try:
            from babel.dates import format_datetime as _babel_format

            babel_style = "medium"
            if style in ("date", "date_short"):
                babel_style = "medium"
            elif style in ("datetime", "datetime_short_year"):
                babel_style = "medium"
            elif style == "datetime_seconds":
                babel_style = "long"
            return _babel_format(dt, format=babel_style, locale=locale_code)
        except Exception:
            pass

    try:
        return dt.strftime(fmt_to_use)
    except Exception:
        try:
            return str(ts)
        except Exception:
            return "-"


# Backwards compatibility for existing imports
format_datetime_de = format_datetime_locale
