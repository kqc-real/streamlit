from config import _build_question_set


def _single_question(qdict):
    qs = _build_question_set({"questions": [qdict]}, "testfile.json", silent=True)
    assert len(qs) == 1
    return qs[0]


def test_english_keys_map_to_german():
    q = {
        "question": "What is 2+2?",
        "options": ["3", "4"],
        "answer": 1,
        "explanation": "Because arithmetic.",
        "weight": 2,
        "topic": "Math",
        "cognitive_level": "apply",
    }
    qn = _single_question(q)
    assert "frage" in qn and qn["frage"].endswith("What is 2+2?")
    assert qn["optionen"] == ["3", "4"]
    assert qn["loesung"] == 1
    assert qn["erklaerung"] != ""
    assert qn["gewichtung"] == 2
    assert qn["thema"] == "Math"
    assert qn.get("kognitive_stufe") == "apply"


def test_answer_as_text_resolves_index():
    q = {"question": "Pick Yes", "options": ["Yes", "No"], "answer": "Yes"}
    qn = _single_question(q)
    assert qn["loesung"] == 0


def test_variations_of_keys_are_mapped():
    q = {
        "text": "Alt key",
        "choices": ["A", "B"],
        "solution": 0,
        "explain": "Short",
        "points": 1,
        "theme": "TopicX",
        "level": "understand",
    }
    qn = _single_question(q)
    assert qn["frage"].endswith("Alt key")
    assert qn["optionen"] == ["A", "B"]
    assert qn["loesung"] == 0
    assert qn["erklaerung"] != ""
    assert qn["gewichtung"] == 1
    assert qn["thema"] == "TopicX"
    assert qn.get("kognitive_stufe") == "understand"


def test_german_keys_take_precedence_over_english():
    q = {
        "frage": "Frage DE",
        "optionen": ["X", "Y"],
        "loesung": 1,
        "answer": "X",
    }
    qn = _single_question(q)
    # loesung should remain 1 (German key present), not overwritten by English 'answer'
    assert qn["loesung"] == 1
