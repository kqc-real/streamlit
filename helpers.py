"""
Modul für kleine, allgemeine Hilfsfunktionen.
"""
from __future__ import annotations

import hashlib
import ipaddress
import re
from html.parser import HTMLParser
from typing import Optional, Union
import html as _html


ACTIVE_SESSION_QUERY_PARAM = "active_session"


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
    """Whitelist-only HTML sanitizer to strip dangerous tags/attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._parts: list[str] = []
        self.modified: bool = False

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS:
            if attrs:
                # Strip attributes but keep the tag to avoid unsafe attrs
                self.modified = True
            self._parts.append(f"<{tag}>")
        else:
            # Escape disallowed start tags so they remain visible instead of being removed.
            # We intentionally do not include attributes when escaping to avoid leaking
            # potentially dangerous attribute content.
            self.modified = True
            self._parts.append(_html.escape(f"<{tag}>", quote=False))

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS and tag not in _VOID_HTML_TAGS:
            self._parts.append(f"</{tag}>")
        else:
            # Escape disallowed end tags so they remain visible in the output.
            self.modified = True
            self._parts.append(_html.escape(f"</{tag}>", quote=False))

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in SAFE_HTML_TAGS:
            if attrs:
                # Strip attributes on allowed tags
                self.modified = True
            if tag in _VOID_HTML_TAGS:
                self._parts.append(f"<{tag}>")
            else:
                self._parts.append(f"<{tag}></{tag}>")
        else:
            # Escape disallowed self-closing tags
            self.modified = True
            # Represent as escaped start tag to keep it visible
            self._parts.append(_html.escape(f"<{tag}>", quote=False))

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if data:
            self._parts.append(_html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:  # type: ignore[override]
        self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:  # type: ignore[override]
        self._parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:  # type: ignore[override]
        self.modified = True

    def handle_decl(self, decl: str) -> None:  # type: ignore[override]
        self.modified = True

    def handle_pi(self, data: str) -> None:  # type: ignore[override]
        self.modified = True

    def get_sanitized_html(self) -> str:
        return "".join(self._parts)


def sanitize_html(value: str) -> tuple[str, bool]:
    """Strip dangerous HTML tags/attributes while preserving a safe subset."""

    if not value:
        return "", False

    parser = _SafeHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return parser.get_sanitized_html(), parser.modified


def get_user_id_hash(user_id: str) -> str:
    """Erzeugt einen SHA256-Hash aus einer User-ID."""
    return hashlib.sha256(user_id.encode()).hexdigest()


def smart_quotes_de(text: str) -> str:
    """Wandelt gerade Anführungszeichen in deutsche typografische Zeichen um.

    Schützt Inhalte innerhalb von `<pre>` und `<code>`-Blöcken vor der
    Umwandlung, damit Quellcode nicht verändert wird.
    """
    if not text:
        return text

    # Quick reject if there are no quote-like characters (include common
    # typographic quote characters so we also handle inputs where LLMs
    # already produced curly quotes).
    quote_chars = set(["'", '"', '\u2018', '\u2019', '\u201A', '\u201C', '\u201D', '\u201E', '\u00BB', '\u00AB'])
    if not any((c in text) for c in quote_chars):
        return text

    # Split the HTML into code/pre segments and normal text segments so we
    # only convert quotes outside of code blocks.
    segments = re.split(r'(<pre[\s\S]*?</pre>|<code[\s\S]*?</code>)', text, flags=re.I)

    def _convert_segment(seg: str) -> str:
        # Preserve math blocks as before
        katex_pattern = re.compile(r'(\${1,2}.*?\${1,2})')
        parts = katex_pattern.split(seg)

        result_parts = []

        # Use a stack to track nested quote contexts. Each entry is a tuple
        # (type, origin_char) where `type` is 'double' or 'single' and
        # `origin_char` is the original ASCII quote character that opened
        # this context (either '"' or "'"). We keep the origin so that a
        # closing quote of the same ASCII char will close the matching
        # context even when we map single ASCII quotes to double German
        # quotes at top-level. This preserves nesting and implements the
        # rule: top-level single quotes become German double quotes
        # („...“), whereas single quotes inside an existing double quote
        # become German single quotes (‚...‘).
        quote_stack: list[tuple[str, str]] = []
        open_map = {'double': '„', 'single': '‚'}
        close_map = {'double': '“', 'single': '‘'}

        for i, part in enumerate(parts):
            if i % 2 == 0:
                processed_part = []
                # include common typographic single-quote characters so
                # the function also converts already-typographed single
                # quotes produced by LLMs or other sources.
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

                        # Non-apostrophe single-quote: decide by stack and origin
                        if quote_stack and quote_stack[-1][1] == ch:
                            # matching origin: close that context
                            entry_type, _ = quote_stack.pop()
                            processed_part.append(close_map.get(entry_type, '’'))
                        else:
                            # opening behavior: if we're inside an already-open
                            # German double quote (type 'double'), a single
                            # ASCII quote should open a nested single. If we're
                            # at top-level (no stack) or not inside a double,
                            # treat the ASCII single as starting a primary
                            # double quote (German style) to avoid producing
                            # German single quotes at top-level.
                            if quote_stack and quote_stack[-1][0] == 'double':
                                # nested single inside an existing double
                                quote_stack.append(('single', ch))
                                processed_part.append(open_map['single'])
                            else:
                                # top-level single -> map to German double
                                quote_stack.append(('double', ch))
                                processed_part.append(open_map['double'])
                    elif ch == '"':
                        # Double-quote handling: use origin matching with '"'
                        if quote_stack and quote_stack[-1][1] == '"':
                            entry_type, _ = quote_stack.pop()
                            processed_part.append(close_map.get(entry_type, '“'))
                        else:
                            # opening double (always type double)
                            quote_stack.append(('double', '"'))
                            processed_part.append(open_map['double'])
                    else:
                        processed_part.append(ch)
                result_parts.append("".join(processed_part))
            else:
                # Leave math parts untouched
                result_parts.append(part)

        return "".join(result_parts)

    out_parts = []
    for seg in segments:
        if not seg:
            continue
        # If this segment is a code/pre block, leave it unchanged
        if seg.lower().startswith('<pre') or seg.lower().startswith('<code'):
            out_parts.append(seg)
        else:
            out_parts.append(_convert_segment(seg))

    return "".join(out_parts)


def format_decimal_de(value: float, decimals: int = 1) -> str:
    """
    Formatiert eine Zahl mit deutscher Dezimalschreibweise.

    Beispiele:
        format_decimal_de(12.5) -> "12,5"
        format_decimal_de(3.1415, 2) -> "3,14"
    """
    decimals = max(0, int(decimals))
    formatted = f"{value:.{decimals}f}"
    return formatted.replace(".", ",")


def load_markdown_file(path: str) -> str | None:
    """
    Lädt den Inhalt einer Markdown-Datei. Gibt `None` zurück, wenn die Datei fehlt.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def format_datetime_de(ts, fmt: str = '%d.%m.%Y %H:%M:%S'):
    """
    Format a timestamp or a pandas Series of timestamps into a German
    localized string representation (Europe/Berlin). Handles ISO strings
    with offsets and naive timestamps by treating them as UTC.

    Returns a formatted string or a pandas Series of strings. On parse
    errors a placeholder '-' is returned for the offending values.
    """
    try:
        import pandas as _pd
        from datetime import timezone
        # Series handling
        if isinstance(ts, _pd.Series):
            s = _pd.to_datetime(ts, utc=True, errors='coerce')
            try:
                from zoneinfo import ZoneInfo
                berlin = ZoneInfo("Europe/Berlin")
                s = s.dt.tz_convert(berlin)
            except Exception:
                # If zoneinfo isn't available or conversion fails, keep UTC
                pass
            formatted = s.dt.strftime(fmt)
            # Replace NaT -> '-' for display
            return formatted.fillna("-")

        # Scalar handling
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
        # dt is a pandas Timestamp; use strftime
        return dt.strftime(fmt)
    except Exception:
        try:
            # Best-effort fallback
            return str(ts)
        except Exception:
            return '-'


# ---------------------------------------------------------------------------
# Request/Client Helpers
# ---------------------------------------------------------------------------

def _get_current_request():
    """Liefert das aktuelle Streamlit Request-Objekt oder None."""
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import (
            get_script_run_ctx,
        )
    except Exception:
        return None

    ctx = get_script_run_ctx(suppress_warning=True)
    if ctx is None:
        return None

    # Einige Streamlit-Versionen speichern das Request-Objekt direkt im Kontext.
    request = getattr(ctx, "request", None)
    if request is not None:
        return request

    session_id = getattr(ctx, "session_id", None)
    if not session_id:
        return None

    # Zugriff über Runtime → SessionManager → SessionInfo → Client.
    try:
        from streamlit.runtime.runtime import Runtime
    except Exception:
        return None

    try:
        runtime = Runtime.instance()
    except Exception:
        return None

    session_mgr = getattr(runtime, "_session_mgr", None)
    if session_mgr is None:
        return None

    try:
        session_info = session_mgr.get_session_info(session_id)
    except Exception:
        session_info = None

    if not session_info:
        return None

    client = getattr(session_info, "client", None)
    request = getattr(client, "request", None)
    if request is not None:
        return request

    session = getattr(session_info, "session", None)
    if session is not None:
        # Einige Implementierungen hinterlegen den Client am Session-Objekt.
        proxy = getattr(session, "_client", None)
        if proxy is not None:
            proxied_request = getattr(proxy, "request", None)
            if proxied_request is not None:
                return proxied_request

    return None


def _normalize_ip(raw_ip: Union[str, None]) -> Optional[str]:
    """Reinigt IP-Strings und validiert sie mit ipaddress."""
    if not raw_ip:
        return None

    candidate = raw_ip.strip()
    if not candidate:
        return None

    if candidate.startswith("::ffff:"):
        candidate = candidate.split("::ffff:")[-1]

    if "%" in candidate:
        candidate = candidate.split("%", 1)[0]

    try:
        ipaddress.ip_address(candidate)
        return candidate
    except ValueError:
        return None


def get_client_ip() -> Optional[str]:
    """Bestimmt die IP-Adresse des aktuellen Clients."""
    request = _get_current_request()
    if request is None:
        return None

    headers = getattr(request, "headers", None)
    if headers:
        forwarded = headers.get("X-Forwarded-For")
        if forwarded:
            candidate = forwarded.split(",")[0].strip()
            normalized = _normalize_ip(candidate)
            if normalized:
                return normalized

    remote_ip = getattr(request, "remote_ip", None)
    normalized_remote = _normalize_ip(remote_ip)
    if normalized_remote:
        return normalized_remote

    return None


def _get_server_address() -> Optional[str]:
    """Liest die konfigurierte Serveradresse aus Streamlit-Konfiguration."""
    try:
        from streamlit import config as st_config

        return st_config.get_option("server.address")
    except Exception:
        return None


def get_request_host() -> Optional[str]:
    """Gibt den Host-Header der aktuellen Anfrage zurück."""
    request = _get_current_request()
    if request is None:
        return None

    headers = getattr(request, "headers", None)
    if headers:
        host_header = headers.get("Host")
        if host_header:
            return host_header

    host_attr = getattr(request, "host", None)
    if host_attr:
        return str(host_attr)

    return None


def is_request_from_localhost() -> bool:
    """Prüft, ob die aktuelle Anfrage von localhost stammt."""
    client_ip = get_client_ip()
    if client_ip:
        try:
            if ipaddress.ip_address(client_ip).is_loopback:
                return True
        except ValueError:
            pass

    host = get_request_host()
    if host:
        hostname = host.split(":", 1)[0].strip().lower()
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return True

    # Fallback auf Server-Konfiguration: Standardmäßig bindet Streamlit lokal.
    server_address = _get_server_address()

    if server_address in (None, "", "localhost", "127.0.0.1", "::1"):
        return True

    return False
