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
        # No session state available (e.g. running outside Streamlit UI).
        # Do not attempt to read URL query parameters for the locale here;
        # that mechanism is unreliable in some deployment environments.
        return DEFAULT_LOCALE

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
    # Clear the cached locale data so changes to the JSON files are picked up
    # immediately in long-running Streamlit sessions.
    try:
        # Import here to avoid circular import at module load time.
        from . import _load_locale_data

        try:
            _load_locale_data.cache_clear()
        except Exception:
            # If the cache is not present or clearing fails, ignore silently.
            pass
    except Exception:
        pass
    return normalized


def t(key: str, default: Optional[str] = None) -> str:
    """Translate a key using the active locale stored in Streamlit session state."""

    return translate(key, locale=get_locale(), default=default)
