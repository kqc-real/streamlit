# Quick diagnostic script to compute export filename stems using the same
# slugification logic as implemented in main_view.py.

import re
from config import QuestionSet, USER_QUESTION_PREFIX


def compute_export_file_stem(export_selected_file, export_questions=None, question_set_cache=None, user_info_map=None):
    raw_label = None

    # Try question_set_cache meta
    try:
        if question_set_cache and isinstance(question_set_cache, dict):
            qs_obj = question_set_cache.get(export_selected_file)
            if qs_obj and getattr(qs_obj, 'meta', None):
                raw_label = qs_obj.meta.get('thema') or qs_obj.meta.get('title')
    except Exception:
        raw_label = raw_label

    # Try user-upload info
    try:
        if not raw_label and isinstance(export_selected_file, str) and export_selected_file.startswith(USER_QUESTION_PREFIX):
            if user_info_map and export_selected_file in user_info_map:
                info = user_info_map[export_selected_file]
            else:
                info = None

            if info:
                try:
                    raw_label = getattr(info, 'question_set', None) and info.question_set.meta.get('thema')
                    if not raw_label:
                        # Fallback to friendly label or filename
                        raw_label = getattr(info, 'friendly_label', None) or getattr(info, 'filename', None)
                except Exception:
                    raw_label = getattr(info, 'filename', None) or None
    except Exception:
        raw_label = raw_label

    # First question thema
    try:
        if not raw_label and isinstance(export_questions, (list, tuple)) and len(export_questions) > 0:
            first_q = export_questions[0]
            if isinstance(first_q, dict):
                raw_label = first_q.get('thema')
    except Exception:
        raw_label = raw_label

    # Fallback to filename
    if not raw_label:
        raw_label = str(export_selected_file).replace(USER_QUESTION_PREFIX, "").replace("questions_", "").replace("::", "_").replace(".json", "")

    # Slugify
    stem = re.sub(r"[^\w\s-]", "", str(raw_label) or "export")
    stem = stem.strip().replace(" ", "_")
    stem = re.sub(r"_+", "_", stem)
    stem = stem[:80] or "export"
    return stem


# Sample scenarios
if __name__ == '__main__':
    # 1) Core set with meta.thema
    qs1 = QuestionSet(questions=[{"frage": "1. Was ist ..."}], meta={"thema": "Lineare Algebra", "title": "LA"}, source_filename='questions_lineare_algebra.json')
    question_set_cache = {'questions_lineare_algebra.json': qs1}
    s1 = compute_export_file_stem('questions_lineare_algebra.json', export_questions=list(qs1), question_set_cache=question_set_cache, user_info_map=None)
    print('Scenario 1 (meta.thema):', s1)

    # 2) User uploaded set with info holding meta.thema
    user_id = 'user::pasted_abcdef.json'
    qs2 = QuestionSet(questions=[{"frage": "1. ..."}], meta={"title": "Meine Fragen", "thema": "Statistik"}, source_filename='pasted_abcdef.json')
    class Info:
        def __init__(self, question_set, filename, friendly_label=None):
            self.question_set = question_set
            self.filename = filename
            self.friendly_label = friendly_label
            self.identifier = user_id

    info2 = Info(qs2, 'pasted_abcdef.json', friendly_label='Meine Sammlung')
    user_info_map = {user_id: info2}
    s2 = compute_export_file_stem(user_id, export_questions=list(qs2), question_set_cache=None, user_info_map=user_info_map)
    print('Scenario 2 (user meta.thema):', s2)

    # 3) No meta but first question has thema
    export_questions3 = [{'frage': '1. ...', 'thema': 'Analysis'}]
    s3 = compute_export_file_stem('questions_custom.json', export_questions=export_questions3, question_set_cache=None, user_info_map=None)
    print('Scenario 3 (first question thema):', s3)

    # 4) Fallback to filename
    s4 = compute_export_file_stem('questions_Fußball.json', export_questions=None, question_set_cache=None, user_info_map=None)
    print('Scenario 4 (fallback filename):', s4)
