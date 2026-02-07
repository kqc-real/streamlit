import types
import importlib

import user_question_sets


def make_info(uploaded_by=None, uploaded_by_hash=None):
    return types.SimpleNamespace(
        uploaded_by=uploaded_by,
        uploaded_by_hash=uploaded_by_hash,
    )


def test_is_owner_by_pseudonym(monkeypatch):
    monkeypatch.setattr(user_question_sets, 'get_user_question_set', lambda ident: make_info(uploaded_by='alice', uploaded_by_hash='h1'))
    assert user_question_sets.is_owner_of_user_qset('user::foo.json', 'alice', 'hX') is True


def test_is_owner_by_hash(monkeypatch):
    monkeypatch.setattr(user_question_sets, 'get_user_question_set', lambda ident: make_info(uploaded_by=None, uploaded_by_hash='h1'))
    assert user_question_sets.is_owner_of_user_qset('user::foo.json', None, 'h1') is True


def test_is_not_owner(monkeypatch):
    monkeypatch.setattr(user_question_sets, 'get_user_question_set', lambda ident: make_info(uploaded_by='bob', uploaded_by_hash='h2'))
    assert user_question_sets.is_owner_of_user_qset('user::foo.json', 'alice', 'h1') is False
