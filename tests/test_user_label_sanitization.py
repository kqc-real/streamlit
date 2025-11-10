from user_question_sets import pretty_label_from_identifier_string


def test_sanitizes_raw_user_prefix_with_hash_and_ts():
    raw = "user::user fc35383db967e9ec1728f44b65a4e544fa40715e402e0f7797f6d217033f1e2b 1762778639"
    out = pretty_label_from_identifier_string(raw)
    assert out == "Ungenanntes Fragenset"


def test_sanitizes_raw_user_filename_variant():
    raw = "user::user_fc35383db967e9ec1728f44b65a4e544fa40715e402e0f7797f6d217033f1e2b_1762778639.json"
    out = pretty_label_from_identifier_string(raw)
    assert out == "Ungenanntes Fragenset"


def test_keeps_readable_identifier():
    raw = "user::my_special_set"
    out = pretty_label_from_identifier_string(raw)
    assert out == "my special set"
