"""
Modul für kleine, allgemeine Hilfsfunktionen.
"""
from __future__ import annotations

import hashlib
import ipaddress
import re
from typing import Optional, Union


def get_user_id_hash(user_id: str) -> str:
    """Erzeugt einen SHA256-Hash aus einer User-ID."""
    return hashlib.sha256(user_id.encode()).hexdigest()


def smart_quotes_de(text: str) -> str:
    """Wandelt gerade Anführungszeichen in deutsche typografische Zeichen um."""
    if not text or ('"' not in text and "'" not in text):
        return text

    katex_pattern = re.compile(r'(\${1,2}.*?\${1,2})')
    parts = katex_pattern.split(text)

    result_parts = []
    open_quote_expected = True

    for i, part in enumerate(parts):
        if i % 2 == 0:
            processed_part = []
            for char_idx, ch in enumerate(part):
                if ch == "'":
                    is_apostrophe = (
                        char_idx > 0
                        and part[char_idx - 1].isalpha()
                        and char_idx < len(part) - 1
                        and part[char_idx + 1].isalpha()
                    )
                    if is_apostrophe:
                        processed_part.append("’")
                    else:
                        processed_part.append("„" if open_quote_expected else "“")
                        open_quote_expected = not open_quote_expected
                elif ch == '"':
                    processed_part.append("„" if open_quote_expected else "“")
                    open_quote_expected = not open_quote_expected
                else:
                    processed_part.append(ch)
            result_parts.append("".join(processed_part))
        else:
            result_parts.append(part)

    return "".join(result_parts)


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
