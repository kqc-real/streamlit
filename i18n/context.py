"""Streamlit-aware helpers for managing the active locale and translations."""
from __future__ import annotations

from typing import Any, MutableMapping, Optional

import streamlit as st

from . import DEFAULT_LOCALE, available_locales, normalize_locale, translate

LOCALE_SESSION_KEY = "active_locale"

__all__ = ["LOCALE_SESSION_KEY", "get_locale", "set_locale", "t"]


def _get_state() -> Optional[MutableMapping[str, Any]]:
    # In some test environments `streamlit` is mocked and may not expose
    # `session_state` at import time. Use getattr to avoid raising
    # AttributeError/RuntimeError and return None when unavailable.
    return getattr(st, "session_state", None)


def get_locale() -> str:
    """Return the normalized locale stored in the session state (or default)."""

    state = _get_state()
    if state is None:
        # No session state available (e.g. running outside Streamlit UI). Try
        # to honour a URL query parameter if present, otherwise fall back to
        # the default locale. Use `st.query_params` instead of the
        # experimental API to avoid conflicts with other parts of the app.
        try:
            params = getattr(st, "query_params", {}) or {}
            for key in ("lang", "locale", "l"):
                values = params.get(key)
                if values:
                    normalized_qp = normalize_locale(values[0])
                    if normalized_qp in set(available_locales()):
                        return normalized_qp
        except Exception:
            pass
        return DEFAULT_LOCALE

    # Prefer an explicit query parameter so the locale can be fixed via the
    # URL (e.g. `?lang=de`). This is useful when the client cannot persist
    # the choice to localStorage.
    try:
        params = getattr(st, "query_params", {}) or {}
        for key in ("lang", "locale", "l"):
            values = params.get(key)
            if values:
                normalized_qp = normalize_locale(values[0])
                if normalized_qp in set(available_locales()):
                    try:
                        state[LOCALE_SESSION_KEY] = normalized_qp
                    except Exception:
                        pass
                    return normalized_qp
    except Exception:
        # Accessing `st.query_params` may raise in some environments; ignore
        # errors and fall back to the session-based behavior.
        pass

    stored = state.get(LOCALE_SESSION_KEY)
    normalized = normalize_locale(stored)
    locales = set(available_locales())
    if normalized in locales:
        if state.get(LOCALE_SESSION_KEY) != normalized:
            try:
                state[LOCALE_SESSION_KEY] = normalized
            except Exception:
                pass
        return normalized

    try:
        state[LOCALE_SESSION_KEY] = DEFAULT_LOCALE
    except Exception:
        pass
    return DEFAULT_LOCALE


def set_locale(locale: str) -> str:
    """Activate a new locale for the current session."""

    state = _get_state()
    normalized = normalize_locale(locale)
    if state is not None:
        try:
            state[LOCALE_SESSION_KEY] = normalized
        except Exception:
            pass
    return normalized


def t(key: str, default: Optional[str] = None) -> str:
    """Translate a key using the active locale stored in Streamlit session state."""

    return translate(key, locale=get_locale(), default=default)
