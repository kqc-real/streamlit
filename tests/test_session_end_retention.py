import importlib


def setup_function(func):
    # Ensure fresh module state for each test
    import components
    importlib.reload(components)
    # streamlit in the test environment may not expose a real session_state
    if not hasattr(components.st, "session_state"):
        components.st.session_state = {}
    else:
        try:
            components.st.session_state.clear()
        except Exception:
            components.st.session_state = {}


def test_preserve_sets_for_reserved_pseudonym(monkeypatch):
    import components
    import database

    aborted_user = "reserved_user"

    # Mock DB helper to report that the pseudonym is reserved
    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: True)

    # Call the helper
    components._apply_user_set_retention_policy(aborted_user)

    # When reserved, a preserved flag is set
    assert components.st.session_state.get("_user_qset_preserved_notice") is True


def test_keep_sets_for_non_reserved_pseudonym(monkeypatch):
    import components
    import database

    aborted_user = "normal_user"

    # Mock DB helper to report that the pseudonym is NOT reserved
    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: False)

    components._apply_user_set_retention_policy(aborted_user)

    # When not reserved, sets are kept; preserved flag stays unset
    assert components.st.session_state.get("_user_qset_preserved_notice") is not True
