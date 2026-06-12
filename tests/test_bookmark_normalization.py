from components import _normalize_bookmarked_questions


def test_normalize_bookmarked_questions_removes_duplicates_and_invalid_indices():
    raw_bookmarks = [5, "5", 2, -1, "x", 99, 2, None, 0]

    assert _normalize_bookmarked_questions(raw_bookmarks, question_count=6) == [5, 2, 0]
