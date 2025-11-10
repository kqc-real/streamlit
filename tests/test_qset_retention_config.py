import importlib


def setup_function(func):
    import components
    importlib.reload(components)


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
