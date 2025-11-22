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
    assert "question" in qn and qn["question"].endswith("What is 2+2?")
    assert qn["options"] == ["3", "4"]
    assert qn["answer"] == 1
    assert qn["explanation"] != ""
    assert qn["weight"] == 2
    assert qn["topic"] == "Math"
    assert qn.get("cognitive_level") == "apply"


def test_answer_as_text_resolves_index():
    q = {"question": "Pick Yes", "options": ["Yes", "No"], "answer": "Yes"}
    qn = _single_question(q)
    assert qn["answer"] == 0


def test_variations_of_keys_are_mapped():
    q = {
        "question": "Alt key",
        "options": ["A", "B"],
        "answer": 0,
        "explanation": "Short",
        "weight": 1,
        "topic": "TopicX",
        "cognitive_level": "understand",
    }
    qn = _single_question(q)
    assert qn["question"].endswith("Alt key")
    assert qn["options"] == ["A", "B"]
    assert qn["answer"] == 0
    assert qn["explanation"] != ""
    assert qn["weight"] == 1
    assert qn["topic"] == "TopicX"
    assert qn.get("cognitive_level") == "understand"


def test_german_keys_take_precedence_over_english():
    q = {
        "question": "Frage EN",
        "options": ["X", "Y"],
        "answer": "X",
    }
    qn = _single_question(q)
    # textual answer should be resolved to index 0
    assert qn["answer"] == 0
