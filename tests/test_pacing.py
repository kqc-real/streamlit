import importlib.util
import sys

# Import the helpers/pacing.py module by path to avoid name conflicts with an existing
# top-level `helpers.py` module in the project.
spec = importlib.util.spec_from_file_location("helpers.pacing", "/Users/kqc/streamlit/helpers/pacing.py")
pacing = importlib.util.module_from_spec(spec)
sys.modules["helpers.pacing"] = pacing
spec.loader.exec_module(pacing)


def make_questions(weights):
    return [{"weight": w} for w in weights]


def test_compute_ideal_times_defaults():
    qs = make_questions([1, 2, 3])
    times = pacing.compute_ideal_times(qs, {"1": 0.5, "2": 0.75, "3": 1.0})
    assert times == [30, 45, 60]


def test_expected_and_delta_and_status_on_track():
    qs = make_questions([1, 1, 1])
    times = pacing.compute_ideal_times(qs, {"1": 0.5})
    # after first question expected = 30
    elapsed = 30
    status = pacing.pacing_status(elapsed, times, 0)
    assert status == "green"
    delta = pacing.pacing_delta(elapsed, times, 0)
    assert delta == 0


def test_status_yellow_and_recommend_speedup():
    qs = make_questions([2, 2, 2])
    times = pacing.compute_ideal_times(qs, {"2": 0.75})
    # expected after first = 45, make elapsed 70 -> behind
    elapsed = 70
    status = pacing.pacing_status(elapsed, times, 0)
    # 70s elapsed vs expected 45s -> sizeable delay -> red
    assert status == "red"
    rec = pacing.recommend_action(elapsed, times, 0, total_allowed_seconds=3 * 45)
    assert rec["action"] in {"speedup", "skip"}


def test_recommend_on_track_when_enough_time():
    qs = make_questions([1, 1, 1, 1])
    times = pacing.compute_ideal_times(qs, {"1": 0.5})
    elapsed = 20
    total_allowed = sum(times) + 60  # generous buffer
    rec = pacing.recommend_action(elapsed, times, 0, total_allowed_seconds=total_allowed)
    assert rec["action"] == "on_track"


def test_status_ahead_when_well_ahead():
    qs = make_questions([1, 1, 1])
    times = pacing.compute_ideal_times(qs, {"1": 0.5})
    # expected after first = 30s; use elapsed = 5s -> well ahead
    elapsed = 5
    status = pacing.pacing_status(elapsed, times, 0)
    assert status == "ahead"
