"""Timing coach helpers for the MC test app.

Provides small, well-tested utilities to compute per-question ideal times,
assess pacing status and produce simple action recommendations.

These functions operate on seconds to avoid float surprises in UI code.
"""
from typing import List, Dict, Any


def compute_ideal_times(questions: List[dict], time_per_weight: Dict[str, float]) -> List[int]:
    """Return list of ideal times in seconds for each question.

    time_per_weight maps weight as string ("1","2","3") to minutes.
    """
    res: List[int] = []
    for q in questions:
        w = q.get("weight", 1)
        minutes = time_per_weight.get(str(w), time_per_weight.get("1", 0.5))
        seconds = int(round(minutes * 60))
        # enforce a small minimum to avoid zero/very small values
        if seconds < 10:
            seconds = 10
        res.append(seconds)
    return res


def expected_cumulative(ideal_times: List[int], index: int) -> int:
    """Return cumulative expected seconds up to and including index."""
    if index < 0:
        return 0
    return sum(ideal_times[: index + 1])


def pacing_delta(elapsed_seconds: int, ideal_times: List[int], current_index: int) -> int:
    """Return elapsed - expected_cumulative (positive => behind schedule)."""
    expected = expected_cumulative(ideal_times, current_index)
    return int(elapsed_seconds - expected)


def pacing_status(
    elapsed_seconds: int,
    ideal_times: List[int],
    current_index: int,
    ahead_fraction: float = 0.05,
    min_ahead_seconds: int = 5,
    green_threshold: float = 0.10,
    yellow_threshold: float = 0.30,
) -> str:
    """Return one of 'ahead', 'green', 'yellow', 'red' based on relative delta.

    - 'ahead' is returned when the user is sufficiently ahead of schedule
      (negative delta) beyond an absolute or relative margin.
    - 'green' is the default on-track state.
    - 'yellow'/'red' indicate increasing levels of being behind schedule.

    Parameters:
    - ahead_fraction: relative fraction of expected time to qualify as ahead
    - min_ahead_seconds: absolute minimum seconds to qualify as ahead
    - green_threshold / yellow_threshold: relative fractions for color bounds
    """
    expected = expected_cumulative(ideal_times, current_index)
    if expected <= 0:
        return "green"
    delta = pacing_delta(elapsed_seconds, ideal_times, current_index)
    # relative fraction (can be negative when ahead)
    pct = delta / float(expected)

    # Determine absolute ahead threshold in seconds
    ahead_threshold_seconds = max(int(min_ahead_seconds), int(round(ahead_fraction * expected)))
    if delta < 0 and abs(delta) >= ahead_threshold_seconds:
        return "ahead"

    # If within green threshold (including slight negative deltas), treat as green
    if pct <= green_threshold:
        return "green"

    # Only positive pct from here on indicates behind schedule
    if pct <= yellow_threshold:
        return "yellow"
    return "red"


def recommend_action(elapsed_seconds: int, ideal_times: List[int], current_index: int,
                     total_allowed_seconds: int, remaining_buffer_seconds: int = 0) -> Dict[str, Any]:
    """Return a small recommendation dict describing suggested action.

    Fields: action (on_track|speedup|skip), message, required_speedup (ratio),
    suggested_reduction_pct (per remaining question) when applicable.
    """
    n = len(ideal_times)
    if n == 0:
        return {"action": "on_track", "message": "No questions."}
    # remaining expected time excluding current question
    remaining_expected = sum(ideal_times[current_index + 1:])
    remaining_questions = max(1, n - (current_index + 1))
    # total allowed includes buffer
    allowed = total_allowed_seconds + remaining_buffer_seconds
    projected_finish = elapsed_seconds + remaining_expected
    if projected_finish <= allowed:
        return {"action": "on_track", "message": "On track."}
    # compute how much faster we must be
    required_speedup = projected_finish / float(allowed)
    # suggested per-question reduction percentage
    suggested_reduction_pct = max(0.0, (required_speedup - 1.0) / remaining_questions * 100.0)
    # if required_speedup is large, recommend skipping
    if required_speedup > 1.2:
        msg = (
            "Significant delay: consider quickly answering or skipping the hardest "
            "remaining questions and return later."
        )
        return {
            "action": "skip",
            "message": msg,
            "required_speedup": required_speedup,
            "suggested_reduction_pct": suggested_reduction_pct,
        }
    msg = (
        f"Behind schedule. Try to reduce time per remaining question by about "
        f"{int(round(suggested_reduction_pct))}%.")
    return {
        "action": "speedup",
        "message": msg,
        "required_speedup": required_speedup,
        "suggested_reduction_pct": suggested_reduction_pct,
    }
