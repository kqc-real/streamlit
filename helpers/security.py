"""Request and security related helpers extracted from legacy `helpers.py`.
"""
from __future__ import annotations

import ipaddress
from typing import Optional, Union


def _get_current_request():
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import (
            get_script_run_ctx,
        )
    except Exception:
        return None

    ctx = get_script_run_ctx(suppress_warning=True)
    if ctx is None:
        return None

    request = getattr(ctx, "request", None)
    if request is not None:
        return request

    session_id = getattr(ctx, "session_id", None)
    if not session_id:
        return None

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
        proxy = getattr(session, "_client", None)
        if proxy is not None:
            proxied_request = getattr(proxy, "request", None)
            if proxied_request is not None:
                return proxied_request

    return None


# Constant used across the app to indicate the active session query parameter
ACTIVE_SESSION_QUERY_PARAM = "active_session"


def _normalize_ip(raw_ip: Union[str, None]) -> Optional[str]:
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
    try:
        from streamlit import config as st_config
        return st_config.get_option("server.address")
    except Exception:
        return None


def get_request_host() -> Optional[str]:
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
    server_address = _get_server_address()
    if server_address in (None, "", "localhost", "127.0.0.1", "::1"):
        return True
    return False
