import types

import main_view as mv
from config import AppConfig


class _FakeCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def markdown(self, *args, **kwargs):
        return None


class _Session(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value
        return value


class _FakeStreamlit:
    def __init__(self):
        self.session_state = _Session()
        self.markdown_calls = []
        self.html_calls = []
        self.expander_labels = []
        self.button_calls = []
        self.radio_calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # UI primitives
    def columns(self, sizes):
        return [self for _ in sizes]

    def container(self, *args, **kwargs):
        return _FakeCtx()

    def expander(self, label, *args, **kwargs):
        self.expander_labels.append(label)
        return _FakeCtx()

    def markdown(self, text, **kwargs):
        self.markdown_calls.append(text)

    def html(self, text, **kwargs):
        self.html_calls.append((text, kwargs))

    def toggle(self, label, value=False, key=None):
        return value

    def button(self, *args, **kwargs):
        self.button_calls.append((args, kwargs))
        return False

    def radio(self, label, options, **kwargs):
        self.radio_calls.append((label, options, kwargs))
        return 0

    def popover(self, *args, **kwargs):
        return _FakeCtx()

    def form(self, *args, **kwargs):
        return _FakeCtx()

    def form_submit_button(self, *args, **kwargs):
        return False

    def checkbox(self, *args, **kwargs):
        return False

    # Feedback/UI helpers
    def success(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def balloons(self, *args, **kwargs):
        pass

    def snow(self, *args, **kwargs):
        pass

    def rerun(self):
        # No-op for tests; we avoid infinite reruns by pre-setting state flags.
        pass

    def stop(self):
        # Simulate Streamlit stop without raising.
        pass

    def caption(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def metric(self, *args, **kwargs):
        pass

    def container_border(self, *args, **kwargs):
        return _FakeCtx()

    def subheader(self, *args, **kwargs):
        pass

    def header(self, *args, **kwargs):
        pass


def test_render_explanation_renders_extended_and_glossary(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)

    # Simplify translations/lookups to deterministic fallbacks.
    monkeypatch.setattr(mv, "_test_view_text", lambda key, default=None: default or key)
    monkeypatch.setattr(mv, "_summary_text", lambda key, default=None: default or key)
    monkeypatch.setattr(mv, "translate_ui", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "smart_quotes_de", lambda s: s)
    monkeypatch.setattr(mv, "_strip_leading_numbering", lambda x: x)
    monkeypatch.setattr(mv, "_steps_have_numbering", lambda steps: False)

    # Ensure an answer is present so the explanation view can render normally.
    monkeypatch.setattr(mv, "get_answer_for_question", lambda idx: "falsch")

    # Build a question with all optional display elements.
    question = {
        "question": "1. Welcher Zusammenhang beschreibt das ökonomische Prinzip korrekt?",
        "optionen": ["Richtig", "Falsch"],
        "loesung": 0,
        "erklaerung": "Kurzbegründung",
        "extended_explanation": {
            "titel": "Varianten des ökonomischen Prinzips",
            "schritte": [
                "Das ökonomische Prinzip basiert auf knappen Ressourcen.",
                "Minimalprinzip: Ziel fest, Mittel minimieren.",
                "Maximalprinzip: Mittel fest, Output maximieren.",
            ],
        },
        "mini_glossary": {"Ressource": "Einsatzfaktor, der knapp ist"},
    }
    questions = [question]

    # Pre-set the extended explanation to be visible to avoid relying on a rerun.
    fake_st.session_state[f"show_extended_0"] = True
    fake_st.session_state["bookmarked_questions"] = []

    # Minimal app_config placeholder
    app_config = types.SimpleNamespace(scoring_mode="positive")

    mv.render_explanation(question, app_config, questions, remaining_time=0, remaining_questions=0)

    # Extended explanation expander should render
    assert any("Detaillierte Erklärung" in label for label in fake_st.expander_labels)
    # Steps from the extended explanation should be emitted
    assert any("Minimalprinzip" in text for text in fake_st.markdown_calls)
    # Mini-glossary content should render after the explanation
    assert any("Ressource" in text for text in fake_st.markdown_calls)


def test_page_reload_guard_injects_beforeunload_and_can_disable(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)

    mv._set_page_reload_guard(True)
    mv._set_page_reload_guard(False)

    assert len(fake_st.html_calls) == 2
    active_html, active_kwargs = fake_st.html_calls[0]
    disabled_html, disabled_kwargs = fake_st.html_calls[1]

    assert active_kwargs["unsafe_allow_javascript"] is True
    assert disabled_kwargs["unsafe_allow_javascript"] is True
    assert "beforeunload" in active_html
    assert "overscroll-behavior-y: contain" in active_html
    assert "dataset.mcTestReloadGuardActive" in active_html
    assert "input[role=\"combobox\"]" in active_html
    assert "inputmode\", \"none\"" in active_html
    assert "dataset.mcTestKeyboardGuard" in active_html
    assert "MutationObserver" in active_html
    assert "const active = true;" in active_html
    assert "const active = false;" in disabled_html


def test_render_question_view_smoke(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)

    # Patch helpers that are UI-only or external.
    monkeypatch.setattr(mv, "_process_queued_rerun", lambda: None)
    monkeypatch.setattr(mv, "_inject_main_container_padding", lambda: None)
    monkeypatch.setattr(mv, "translate_ui", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "_test_view_text", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "_summary_text", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "smart_quotes_de", lambda s: s)
    monkeypatch.setattr(mv, "_normalize_stage_label", lambda x: x)
    for helper_name in ("_sidebar_text", "_welcome_text", "_dialog_text"):
        if hasattr(mv, helper_name):
            monkeypatch.setattr(mv, helper_name, lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "get_db_connection", lambda: None)
    monkeypatch.setattr(mv, "_show_welcome_container", lambda cfg: None)
    monkeypatch.setattr(mv, "initialize_session_state", lambda questions, cfg: None)
    for helper_name in (
        "_dismiss_user_qset_dialog_and_rerun",
        "_dismiss_user_qset_dialog_from_test",
        "handle_bookmark_toggle",
        "_render_history_table",
        "close_user_qset_dialog",
        "is_test_finished",
    ):
        if hasattr(mv, helper_name):
            monkeypatch.setattr(mv, helper_name, lambda *args, **kwargs: None)
    monkeypatch.setattr(mv, "is_test_finished", lambda qs: False)

    # Prepare session state to bypass welcome stop and to provide shuffled options.
    fake_st.session_state.update(
        {
            "test_started": True,
            "optionen_shuffled": [["Richtig", "Falsch"]],
            "frage_0_beantwortet": None,
            "answered_indices": [],
            "skipped_questions": [],
            "initial_frage_indices": [0],
            "start_zeit": None,
            "test_time_limit": 0,
        }
    )

    question = {
        "question": "1. Welcher Zusammenhang beschreibt das ökonomische Prinzip korrekt?",
        "optionen": ["Richtig", "Falsch"],
        "loesung": 0,
        "erklaerung": "Kurzbegründung",
        "extended_explanation": None,
        "mini_glossary": None,
        "gewichtung": 2,
    }
    questions = [question]
    app_config = AppConfig()

    mv.render_question_view(questions, 0, app_config)

    # Ensure question header was rendered (markdown called with question text)
    assert any("ökonomische Prinzip" in text for text in fake_st.markdown_calls)
    # Radio selection invoked once for options
    assert fake_st.radio_calls


def test_prepare_markdown_for_streamlit_converts_escaped_blockquotes():
    rendered = mv._prepare_markdown_for_streamlit(
        "Einleitung\n\n&gt; Prüfe, ob die geladene JSON-Variante als Quote erscheint."
    )

    assert "<blockquote>" in rendered
    assert "Prüfe, ob die geladene JSON-Variante als Quote erscheint." in rendered
    assert "&gt; Prüfe" not in rendered


def test_answer_option_selected_marker_does_not_reuse_letter_circle(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    monkeypatch.setattr(mv, "_test_view_text", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "smart_quotes_de", lambda s: s)

    mv._render_markdown_answer_options(["A falsch", "D richtig"], selected_index=1)

    rendered = "\n".join(fake_st.markdown_calls)
    assert ".mc-answer-option-label span" not in rendered
    assert ".mc-answer-option-label .mc-answer-option-letter" in rendered
    assert "<span class='mc-answer-option-letter'>B</span>" in rendered
    assert "<span class='mc-answer-option-selected-text'>(ausgewählt)</span>" in rendered


def test_render_question_view_keeps_block_markdown_in_question_and_options(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)

    monkeypatch.setattr(mv, "_process_queued_rerun", lambda: None)
    monkeypatch.setattr(mv, "_inject_main_container_padding", lambda: None)
    monkeypatch.setattr(mv, "translate_ui", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "_test_view_text", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "_summary_text", lambda key, default=None, **_: default or key)
    monkeypatch.setattr(mv, "smart_quotes_de", lambda s: s)
    monkeypatch.setattr(mv, "_normalize_stage_label", lambda x: x)
    monkeypatch.setattr(mv, "get_db_connection", lambda: None)
    monkeypatch.setattr(mv, "_show_welcome_container", lambda cfg: None)
    monkeypatch.setattr(mv, "initialize_session_state", lambda questions, cfg: None)
    monkeypatch.setattr(mv, "is_test_finished", lambda qs: False)
    for helper_name in (
        "_dismiss_user_qset_dialog_and_rerun",
        "_dismiss_user_qset_dialog_from_test",
        "handle_bookmark_toggle",
        "_render_history_table",
        "close_user_qset_dialog",
    ):
        if hasattr(mv, helper_name):
            monkeypatch.setattr(mv, helper_name, lambda *args, **kwargs: None)

    markdown_option = (
        "### Korrekt\n"
        "- **Fett** nutzt zwei Sternchen.\n"
        "- *Kursiv* nutzt ein Sternchen.\n"
        "- Inline-Code nutzt `Backticks`."
    )
    html_option = "<em>Korrekt:</em><br><code>code</code>, <sub>sub</sub> und <sup>sup</sup> prüfen sichere HTML-Tags."

    fake_st.session_state.update(
        {
            "test_started": True,
            "optionen_shuffled": [[markdown_option, html_option]],
            "frage_0_beantwortet": None,
            "answered_indices": [],
            "skipped_questions": [],
            "initial_frage_indices": [0],
            "start_zeit": None,
            "test_time_limit": 0,
        }
    )

    question = {
        "question": "1. ## Formatierungs-Mix\n\n> Prüfe, ob alle drei Inline-Formate erhalten bleiben.",
        "optionen": [markdown_option, html_option],
        "loesung": 0,
        "erklaerung": "Kurzbegründung",
        "extended_explanation": None,
        "mini_glossary": None,
        "gewichtung": 1,
    }

    mv.render_question_view([question], 0, AppConfig())

    assert any(text == "## Formatierungs-Mix" for text in fake_st.markdown_calls)
    assert any("<blockquote>" in text and "Prüfe, ob alle drei Inline-Formate erhalten bleiben." in text for text in fake_st.markdown_calls)
    assert any("### Korrekt\n- **Fett** nutzt zwei Sternchen." in text for text in fake_st.markdown_calls)
    assert any("<em>Korrekt:</em><br><code>code</code>" in text for text in fake_st.markdown_calls)
    assert fake_st.radio_calls
    assert fake_st.radio_calls[0][2]["format_func"](0) == "A"
    assert fake_st.radio_calls[0][2]["format_func"](1) == "B"
