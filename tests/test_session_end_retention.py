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

    deleted = {"called": False}

    def fake_delete_sets(uid):
        deleted["called"] = True

    # Replace the delete function in components so we can detect calls
    monkeypatch.setattr(components, "delete_sets_for_user", fake_delete_sets)

    # Call the helper
    components._apply_user_set_retention_policy(aborted_user)

    # When reserved, delete should NOT be called and a preserved flag is set
    assert components.st.session_state.get("_user_qset_preserved_notice") is True
    assert deleted["called"] is False


def test_delete_sets_for_non_reserved_pseudonym(monkeypatch):
    import components
    import database

    aborted_user = "normal_user"

    # Mock DB helper to report that the pseudonym is NOT reserved
    monkeypatch.setattr(database, "has_recovery_secret_for_pseudonym", lambda u: False)

    deleted = {"called": False, "user": None}

    def fake_delete_sets(uid):
        deleted["called"] = True
        deleted["user"] = uid

    monkeypatch.setattr(components, "delete_sets_for_user", fake_delete_sets)

    components._apply_user_set_retention_policy(aborted_user)

    # When not reserved, delete should be called and preserved flag absent
    assert components.st.session_state.get("_user_qset_preserved_notice") is not True
    assert deleted["called"] is True
    assert deleted["user"] == aborted_user
