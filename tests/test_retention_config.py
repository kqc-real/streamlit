import importlib


def setup_function(func):
    import components
    importlib.reload(components)
    # Ensure session_state exists for test environment
    if not hasattr(components.st, "session_state"):
        components.st.session_state = {}
    else:
        try:
            components.st.session_state.clear()
        except Exception:
            components.st.session_state = {}


def test_caption_uses_cleanup_hours_from_config(monkeypatch):
    import components
    from config import AppConfig

    cfg = AppConfig()
    cfg.user_qset_cleanup_hours = 48
    # No pseudonym provided -> caption should reference hours
    caption = components.get_user_qset_retention_caption(True, None, cfg)
    assert "48 Stunden" in caption


def test_caption_uses_reserved_days_from_config_when_reserved(monkeypatch):
    import components
    from config import AppConfig

    cfg = AppConfig()
    cfg.user_qset_reserved_retention_days = 7

    # Mock DB helper to return True for reserved pseudonym
    import database

    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: True)

    caption = components.get_user_qset_retention_caption(True, "reserved_user", cfg)
    assert "7 Tage" in caption


def test_caption_falls_back_to_hours_if_db_check_fails(monkeypatch):
    import components
    from config import AppConfig

    cfg = AppConfig()
    cfg.user_qset_cleanup_hours = 12

    # Mock DB helper to raise exception
    import database

    def bad_helper(u):
        raise RuntimeError("db error")

    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", bad_helper)

    caption = components.get_user_qset_retention_caption(True, "some_user", cfg)
    assert "12 Stunden" in caption
