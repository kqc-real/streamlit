"""Lernmodus: Antwort, Sofortfeedback, nächste Frage, Auswertung."""

import time

import streamlit as st

import database
import logic
import main_view as mv
from config import AppConfig, QuestionSet
from i18n.context import t as translate_ui


class _Slot:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return iter(())


class _LearningUi:
    """Zeichnet Feedback und Auswertung auf, ohne eine Streamlit-Sitzung zu starten."""

    def __init__(self, session_state, pressed_buttons: set[str] | None = None):
        self.session_state = session_state
        self.pressed_buttons = pressed_buttons if pressed_buttons is not None else set()
        self.markdown_calls: list[str] = []
        self.success_calls: list[str] = []
        self.error_calls: list[str] = []
        self.button_labels: list[str] = []

    def markdown(self, text="", **kwargs):
        self.markdown_calls.append(str(text))

    def success(self, text="", **kwargs):
        self.success_calls.append(str(text))

    def error(self, text="", **kwargs):
        self.error_calls.append(str(text))

    def button(self, label, key=None, **kwargs):
        self.button_labels.append(str(label))
        return key in self.pressed_buttons

    def columns(self, spec, **kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [_Slot() for _ in range(count)]

    def toggle(self, label, value=False, key=None, **kwargs):
        return value

    def checkbox(self, *args, **kwargs):
        return False

    def form_submit_button(self, *args, **kwargs):
        return False

    def container(self, *args, **kwargs):
        return _Slot()

    def form(self, *args, **kwargs):
        return _Slot()

    def popover(self, *args, **kwargs):
        return _Slot()

    def expander(self, *args, **kwargs):
        return _Slot()

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            return _Slot()

        return _call


def _questions() -> QuestionSet:
    return QuestionSet(
        questions=[
            {
                "question": "1. Erste Frage",
                "optionen": ["Alpha", "Beta"],
                "loesung": 0,
                "erklaerung": "Alpha ist richtig.",
                "gewichtung": 1,
            },
            {
                "question": "2. Zweite Frage",
                "optionen": ["Ja", "Nein"],
                "loesung": 0,
                "erklaerung": "Ja ist richtig.",
                "gewichtung": 2,
            },
        ],
        meta={"test_duration_minutes": 30},
        source_filename="questions_learn.json",
    )


def _fresh_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_FILE", str(tmp_path / "mc_test_data.db"))
    database.init_database()


def _shows_summary(questions) -> bool:
    """Gleiche Bedingung wie in app.py: Auswertung erst nach dem Feedback."""
    if st.session_state.get("test_time_expired", False) or st.session_state.get("test_manually_ended", False):
        return True
    last = st.session_state.get("last_answered_idx")
    explanation_open = last is not None and bool(st.session_state.get(f"show_explanation_{last}"))
    return logic.is_test_finished(questions) and not explanation_open


def _answer(questions, app_config, frage_idx: int, answer: str, confidence: str) -> None:
    mv.handle_answer_submission(
        frage_idx,
        answer,
        questions[frage_idx],
        app_config,
        questions,
        confidence=confidence,
    )


def _advance(ui: _LearningUi, questions, frage_idx: int, remaining: int) -> None:
    shown_key = f"frage_{frage_idx}_explanation_shown_time_monotonic"
    st.session_state[shown_key] = time.monotonic() - 10_000
    ui.pressed_buttons.add(f"next_q_{frage_idx}")
    mv.render_next_question_button(questions, frage_idx, remaining_time=0, remaining_questions=remaining)
    ui.pressed_buttons.clear()


def test_practice_mode_runs_from_answers_to_summary(monkeypatch, tmp_path):
    _fresh_db(monkeypatch, tmp_path)
    st.session_state.clear()
    questions = _questions()
    app_config = AppConfig()
    database.add_user("hash-learn", "Lernperson")
    session_id = database.start_test_session(
        "hash-learn",
        "questions_learn.json",
        tempo="normal",
        mode="practice",
    )
    assert session_id is not None

    st.session_state.clear()
    st.session_state["selected_tempo"] = "normal"
    st.session_state["selected_mode"] = "practice"
    st.session_state["user_id"] = "Lernperson"
    st.session_state["user_id_hash"] = "hash-learn"
    st.session_state["selected_questions_file"] = "questions_learn.json"
    st.session_state["session_id"] = session_id
    mv.initialize_session_state(questions, app_config)
    st.session_state["selected_mode"] = "practice"
    st.session_state["session_id"] = session_id
    st.session_state["test_started"] = True

    assert logic.get_current_question_index() == 0
    assert not _shows_summary(questions)

    _answer(questions, app_config, 0, "Alpha", "sure")

    assert st.session_state["frage_0_antwort"] == "Alpha"
    assert st.session_state["frage_0_beantwortet"] == 1
    assert st.session_state["show_explanation_0"] is True
    assert st.session_state["last_answered_idx"] == 0
    assert not _shows_summary(questions)

    ui = _LearningUi(st.session_state)
    monkeypatch.setattr(mv, "st", ui)
    mv.render_explanation(questions[0], app_config, questions, remaining_time=0, remaining_questions=1)
    correct_label = translate_ui("test_view.explanation_correct", default="Richtig! ✅")
    assert any(correct_label in text for text in ui.success_calls)
    assert any("Alpha" in text for text in ui.markdown_calls)
    assert not ui.error_calls

    _advance(ui, questions, 0, remaining=1)
    assert st.session_state.get("show_explanation_0") is False
    assert logic.get_current_question_index() == 1
    assert not _shows_summary(questions)

    monkeypatch.setattr(mv, "st", st)
    _answer(questions, app_config, 1, "Nein", "unsure")
    assert st.session_state["frage_1_antwort"] == "Nein"
    assert st.session_state["frage_1_beantwortet"] == 0
    assert st.session_state["show_explanation_1"] is True
    assert logic.is_test_finished(questions)
    assert not _shows_summary(questions)

    ui.error_calls.clear()
    ui.markdown_calls.clear()
    ui.success_calls.clear()
    monkeypatch.setattr(mv, "st", ui)
    mv.render_explanation(questions[1], app_config, questions, remaining_time=0, remaining_questions=0)
    wrong_label = translate_ui("test_view.explanation_wrong", default="Leider falsch. ❌")
    assert any(wrong_label in text for text in ui.error_calls)
    assert any("Nein" in text for text in ui.markdown_calls)
    assert any("Ja" in text for text in ui.markdown_calls)

    _advance(ui, questions, 1, remaining=0)
    assert st.session_state.get("show_explanation_1") is False
    assert _shows_summary(questions)
    summary_button = translate_ui("test_view.next_button_summary", default="Zur Testauswertung 🏁")
    assert any(summary_button in label for label in ui.button_labels)

    monkeypatch.setattr("config.load_questions", lambda filename, silent=True: questions)
    mv.render_final_summary(questions, app_config)

    rendered = "\n".join(ui.markdown_calls)
    score_line = translate_ui("summary.score_display", default="{current} / {max} Punkte").format(current=1, max=3)
    assert score_line in rendered
    assert "(33 %)" in rendered
    assert st.session_state.get("in_final_summary") is True

    conn = database.get_db_connection()
    row = conn.execute(
        "SELECT total_points, correct_count, percent FROM test_session_summaries WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    assert row is not None
    assert int(row["total_points"]) == 1
    assert int(row["correct_count"]) == 1
    assert int(round(float(row["percent"]))) == 33

    saved = database.get_answers_for_session(session_id)
    by_nr = {int(item["question_nr"]): item for item in saved}
    assert by_nr[1]["answer_text"] == "Alpha"
    assert int(by_nr[1]["is_correct"]) == 1
    assert by_nr[1]["confidence"] == "sure"
    assert by_nr[2]["answer_text"] == "Nein"
    assert int(by_nr[2]["is_correct"]) == 0
    assert by_nr[2]["confidence"] == "unsure"
