import pandas as pd

import main_view as mv


class _Session(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class _FakeStreamlit:
    def __init__(self, with_fragment: bool = True):
        self.session_state = _Session()
        self.with_fragment = with_fragment
        self.fragment_calls = []
        self.fragment_runs = 0
        self.metric_calls = []
        self.warning_calls = []
        self.error_calls = []
        self.iframe_calls = []
        self.rerun_called = False

    def fragment(self, *args, **kwargs):
        if not self.with_fragment:
            raise AttributeError("fragment")
        self.fragment_calls.append((args, kwargs))

        def _decorator(func):
            def _wrapped(*wrapped_args, **wrapped_kwargs):
                self.fragment_runs += 1
                return func(*wrapped_args, **wrapped_kwargs)

            return _wrapped

        return _decorator

    def metric(self, *args, **kwargs):
        self.metric_calls.append((args, kwargs))

    def warning(self, *args, **kwargs):
        self.warning_calls.append((args, kwargs))

    def error(self, *args, **kwargs):
        self.error_calls.append((args, kwargs))

    def iframe(self, *args, **kwargs):
        self.iframe_calls.append((args, kwargs))

    def rerun(self):
        self.rerun_called = True


def test_compute_countdown_remaining_seconds():
    now = pd.Timestamp("2026-06-13 10:00:00")
    start = now - pd.Timedelta(seconds=75)

    assert mv._compute_countdown_remaining_seconds(start, 120, now=now) == 45


def test_countdown_warning_uses_elapsed_full_minutes(monkeypatch):
    monkeypatch.setattr(
        mv,
        "translate_ui",
        lambda _key, default=None: default or "",
    )

    assert mv._format_countdown_warning(135) == "⚠️ Warning, only 2 min left!"
    assert mv._format_countdown_warning(119) == "⚠️ Warning, only 1 min left!"
    assert mv._format_countdown_warning(60) == "⚠️ Attention, only a few seconds left!"


def test_countdown_start_time_prefers_existing_start_zeit(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    start = pd.Timestamp("2026-06-13 10:00:00")
    fake_st.session_state.start_zeit = start

    resolved = mv._ensure_countdown_start_time(now=start + pd.Timedelta(minutes=2))

    assert resolved == start
    assert fake_st.session_state.start_zeit == start
    assert fake_st.session_state.test_start_time == start.to_pydatetime()
    assert fake_st.session_state.test_started is True


def test_countdown_start_time_recovers_from_test_start_time_without_reset(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    start = pd.Timestamp("2026-06-13 10:00:00")
    fake_st.session_state.test_start_time = start.to_pydatetime()

    resolved = mv._ensure_countdown_start_time(now=start + pd.Timedelta(minutes=2))

    assert resolved == start
    assert fake_st.session_state.start_zeit == start
    assert fake_st.session_state.test_started is True


def test_countdown_start_time_initializes_only_when_no_start_exists(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    start = pd.Timestamp("2026-06-13 10:00:00")

    resolved = mv._ensure_countdown_start_time(now=start)

    assert resolved == start
    assert fake_st.session_state.start_zeit == start
    assert fake_st.session_state.test_start_time == start.to_pydatetime()
    assert fake_st.session_state.test_started is True


def test_set_countdown_start_time_sets_both_time_anchors(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)
    start = pd.Timestamp("2026-06-13 10:00:00")
    fake_st.session_state.test_end_time = start.to_pydatetime()

    resolved = mv._set_countdown_start_time(start)

    assert resolved == start
    assert fake_st.session_state.start_zeit == start
    assert fake_st.session_state.test_start_time == start.to_pydatetime()
    assert fake_st.session_state.test_time_expired is False
    assert "test_end_time" not in fake_st.session_state


def test_countdown_renders_client_side_timer(monkeypatch):
    fake_st = _FakeStreamlit(with_fragment=True)
    rendered_html = []
    monkeypatch.setattr(mv, "st", fake_st)
    monkeypatch.setattr(mv, "_test_view_text", lambda _key, default=None: default or "")
    monkeypatch.setattr(mv, "translate_ui", lambda _key, default=None: default or "")
    monkeypatch.setattr(mv, "_render_countdown_component_html", rendered_html.append)

    remaining = mv._render_countdown_timer_auto_refresh(pd.Timestamp.now(), 120)

    assert remaining > 0
    assert rendered_html
    assert "window.setInterval" in rendered_html[0]
    assert "initialRemainingSeconds" in rendered_html[0]
    assert "mc-countdown-warning" in rendered_html[0]
    assert "mc-countdown-panic" in rendered_html[0]
    assert "panicActive" in rendered_html[0]
    assert "formatWarning" in rendered_html[0]
    assert "totalSeconds > 600" in rendered_html[0]
    assert "Math.floor(totalSeconds / 60)" in rendered_html[0]
    assert "Math.ceil(totalSeconds / 60)" not in rendered_html[0]
    assert "background: transparent" in rendered_html[0]
    assert "--mc-countdown-panel-bg" not in rendered_html[0]
    assert "body.mc-light" in rendered_html[0]
    assert not fake_st.fragment_calls
    assert not fake_st.metric_calls
    assert not fake_st.warning_calls


def test_countdown_embeds_live_panic_mode_threshold():
    html = mv._build_countdown_timer_html(
        label="⏳ Time Left",
        remaining_seconds=44,
        expired_text="Time up",
        warning_seconds_text="Almost done",
        warning_minutes_template="Only {minutes_text} left",
        panic_text="Panic mode live",
        panic_threshold_seconds=15,
        remaining_questions=3,
    )

    assert "Panic mode live" in html
    assert "const panicThresholdSeconds = 15;" in html
    assert "const panicRemainingQuestions = 3;" in html
    assert "totalSeconds < panicRemainingQuestions * panicThresholdSeconds" in html
    assert "panicEl.style.display = \"block\"" in html
    assert "background:" not in html.split(".mc-countdown-panic", 1)[1].split("}", 1)[0]


def test_pacing_status_renders_client_side_component():
    html = mv._build_pacing_status_html(
        elapsed_seconds=30,
        ideal_times=[60, 120, 60],
        current_index=0,
        total_allowed_seconds=240,
        status_text_map={
            "ahead": "Ahead of schedule",
            "green": "On track",
            "yellow": "Slightly behind schedule",
            "red": "Behind schedule",
        },
    )

    assert "window.setInterval" in html
    assert "function pacingStatus" in html
    assert "Ahead of schedule" in html
    assert "mc-pacer-bar" in html
    assert "mc-pacer-status" in html


def test_timer_and_pacer_embed_with_st_iframe(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(mv, "st", fake_st)

    mv._render_countdown_component_html("<p>Timer</p>")
    mv._render_pacing_component_html("<p>Pacer</p>")

    assert fake_st.iframe_calls == [
        (("<p>Timer</p>",), {"height": 124}),
        (("<p>Pacer</p>",), {"height": 62}),
    ]


def test_expired_countdown_sets_session_state_and_reruns(monkeypatch):
    fake_st = _FakeStreamlit(with_fragment=False)
    monkeypatch.setattr(mv, "st", fake_st)
    monkeypatch.setattr(mv, "_test_view_text", lambda _key, default=None: default or "")
    now = pd.Timestamp("2026-06-13 10:00:00")
    start = now - pd.Timedelta(seconds=10)

    remaining = mv._render_countdown_timer(start, 5, now=now)

    assert remaining <= 0
    assert fake_st.session_state["test_time_expired"] is True
    assert fake_st.session_state["test_end_time"] == now.to_pydatetime()
    assert fake_st.error_calls
    assert fake_st.rerun_called is True
