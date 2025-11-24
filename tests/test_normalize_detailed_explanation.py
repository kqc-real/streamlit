import pytest

from helpers import normalize_detailed_explanation


def test_none_and_empty():
    assert normalize_detailed_explanation(None) is None
    assert normalize_detailed_explanation("") is None


def test_string_becomes_content():
    res = normalize_detailed_explanation("This is an extended explanation.")
    assert isinstance(res, dict)
    assert res["title"] == ""
    assert res["content"] == "This is an extended explanation."
    assert res["steps"] is None


def test_dict_with_german_keys():
    src = {"titel": "Schritt-für-Schritt", "inhalt": "Erklärungstext", "schritte": ["Erster Schritt", "Zweiter Schritt"]}
    res = normalize_detailed_explanation(src)
    assert res["title"] == "Schritt-für-Schritt"
    assert res["content"] == "Erklärungstext"
    assert res["steps"] == ["Erster Schritt", "Zweiter Schritt"]


def test_steps_string_splits():
    src = {"title": "T", "steps": "1. Erstens\n2. Zweitens\n"}
    res = normalize_detailed_explanation(src)
    assert res["title"] == "T"
    assert res["steps"] == ["1. Erstens", "2. Zweitens"]


def test_empty_dict_returns_none():
    assert normalize_detailed_explanation({}) is None
