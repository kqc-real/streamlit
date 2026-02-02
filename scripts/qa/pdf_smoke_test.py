from config import AppConfig
import pdf_export
from pdf_export import generate_pdf_report
import streamlit as st
from i18n.context import set_locale


def _make_question(idx: int, text: str, options, correct_idx: int):
    return {
        "frage": f"{idx}. {text}",
        "optionen": options,
        "loesung": correct_idx,
        "erklaerung": "Kurz",
        "gewichtung": 1,
        "thema": "Test",
        "kognitive_stufe": "wissen",
    }


# Prepare questions that cover all weights and cognitive stages so all tables render
questions = [
    # weight 1 -> easy -> Reproduktion
    {**_make_question(1, "Q1", ["A", "B"], 1), "gewichtung": 1, "kognitive_stufe": "Reproduktion"},
    # weight 2 -> medium -> Anwendung
    {**_make_question(2, "Q2", ["X", "Y"], 0), "gewichtung": 2, "kognitive_stufe": "Anwendung"},
    # weight 3 -> hard -> Analyse
    {**_make_question(3, "Q3", ["Yes", "No"], 0), "gewichtung": 3, "kognitive_stufe": "Analyse"},
    # add extra questions to create stage averages > 0 and multiple users average
    {**_make_question(4, "Q4", ["alpha", "beta"], 0), "gewichtung": 1, "kognitive_stufe": "Reproduktion"},
    {**_make_question(5, "Q5", ["uno", "dos"], 1), "gewichtung": 2, "kognitive_stufe": "Anwendung"},
]

# Setup minimal session state like tests
if not hasattr(st, 'session_state'):
    st.session_state = {}

st.session_state.clear()
for i, q in enumerate(questions):
    # mark question as answered and set the stored answer to the correct option
    st.session_state[f"frage_{i}_beantwortet"] = q.get("gewichtung", 1)
    st.session_state[f"frage_{i}_antwort"] = q["optionen"][q["loesung"]]

st.session_state["selected_questions_file"] = "questions_test.json"
st.session_state["user_id"] = "smoketester"

app_config = AppConfig()

# Monkeypatch average stats to ensure comparison tables are generated
avg_stats = {
    "avg_percent": 72.5,
    "avg_score": 29,
    "total_users": 3,
    "avg_difficulty": {"easy": 60.0, "medium": 65.0, "hard": 50.0},
}
pdf_export._calculate_average_stats = lambda q_file, qs: avg_stats

results = {}
for loc in ("en", "de", "fr", "es"):
    set_locale(loc)
    pdf_bytes = generate_pdf_report(questions, app_config)
    out_path = f'tmp_smoke_report_{loc}.pdf'
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)

    # Check that the localized stage names appear and that 'Schwierigkeit' etc. do not
    check_strings = [b'Schwierigkeit', b'Difficulty', b'Difficult', b'Dificultad']
    found_unwanted = {s.decode('utf-8'): (s in pdf_bytes) for s in check_strings}

    # Also check for localized stage labels (look for any of the stage values from i18n)
    stage_checks = {}
    # German localized forms
    stage_checks['Reproduktion'] = b'Reproduktion' in pdf_bytes
    stage_checks['Verständnis'] = b'Verst' in pdf_bytes or b'Verst' in pdf_bytes
    stage_checks['Anwendung'] = b'Anwendung' in pdf_bytes
    stage_checks['Analyse'] = b'Analyse' in pdf_bytes

    results[loc] = {
        'file': out_path,
        'size': len(pdf_bytes),
        'unwanted': found_unwanted,
        'stages_found': stage_checks,
    }

for loc, info in results.items():
    print('Locale:', loc)
    print(' PDF:', info['file'], 'size', info['size'])
    print(' Unwanted present:', info['unwanted'])
    print(' Stages found (partial checks):', info['stages_found'])
    print('---')
