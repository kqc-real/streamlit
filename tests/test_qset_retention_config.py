import importlib

_MISSING = object()
_previous_locale = _MISSING


def setup_function(func):
    import components
    import streamlit as st

    global _previous_locale
    importlib.reload(components)
    try:
        _previous_locale = st.session_state.get("active_locale", _MISSING)
        st.session_state["active_locale"] = "de"
    except Exception:
        _previous_locale = _MISSING


def teardown_function(func):
    import streamlit as st

    try:
        if _previous_locale is _MISSING:
            st.session_state.pop("active_locale", None)
        else:
            st.session_state["active_locale"] = _previous_locale
    except Exception:
        pass


def test_retention_caption_uses_configured_reserved_days(monkeypatch):
    import components
    from config import AppConfig
    import database

    app_config = AppConfig()
    app_config.user_qset_reserved_retention_days = 7

    # Mock DB helper to report reserved pseudonym
    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: True)

    caption = components.get_user_qset_retention_caption(True, "reserved_user", app_config)
    assert "7 Tage" in caption


def test_retention_caption_non_reserved_uses_cleanup_hours(monkeypatch):
    import components
    from config import AppConfig
    import database

    app_config = AppConfig()
    app_config.user_qset_cleanup_hours = 12

    # Mock DB helper to report not reserved
    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: False)

    caption = components.get_user_qset_retention_caption(True, "normal_user", app_config)
    assert "12 Stunden" in caption
