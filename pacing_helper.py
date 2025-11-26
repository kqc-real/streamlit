"""Compatibility shim for the pacing helpers.

This module provides the same functions as `helpers/pacing.py` but is
importable as a top-level module to avoid conflicts with an existing
`helpers.py` module in the project.
"""
from typing import List, Dict, Any


def compute_ideal_times(questions: List[dict], time_per_weight: Dict[str, float]) -> List[int]:
    res: List[int] = []
    for q in questions:
        w = q.get("weight", q.get("gewichtung", 1))
        minutes = time_per_weight.get(str(w), time_per_weight.get("1", 0.5))
        seconds = int(round(minutes * 60))
        if seconds < 10:
            seconds = 10
        res.append(seconds)
    return res


def expected_cumulative(ideal_times: List[int], index: int) -> int:
    if index < 0:
        return 0
    return sum(ideal_times[: index + 1])


def pacing_delta(elapsed_seconds: int, ideal_times: List[int], current_index: int) -> int:
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
    expected = expected_cumulative(ideal_times, current_index)
    if expected <= 0:
        return "green"
    delta = pacing_delta(elapsed_seconds, ideal_times, current_index)
    pct = delta / float(expected)

    ahead_threshold_seconds = max(int(min_ahead_seconds), int(round(ahead_fraction * expected)))
    if delta < 0 and abs(delta) >= ahead_threshold_seconds:
        return "ahead"

    if pct <= green_threshold:
        return "green"
    if pct <= yellow_threshold:
        return "yellow"
    return "red"


def recommend_action(elapsed_seconds: int, ideal_times: List[int], current_index: int,
                     total_allowed_seconds: int, remaining_buffer_seconds: int = 0) -> Dict[str, Any]:
    n = len(ideal_times)
    if n == 0:
        return {"action": "on_track", "message": "No questions."}
    remaining_expected = sum(ideal_times[current_index + 1:])
    remaining_questions = max(1, n - (current_index + 1))
    allowed = total_allowed_seconds + remaining_buffer_seconds
    projected_finish = elapsed_seconds + remaining_expected
    if projected_finish <= allowed:
        return {"action": "on_track", "message": "On track."}
    required_speedup = projected_finish / float(allowed)
    suggested_reduction_pct = max(0.0, (required_speedup - 1.0) / remaining_questions * 100.0)
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
        f"{int(round(suggested_reduction_pct))}%."
    )
    return {
        "action": "speedup",
        "message": msg,
        "required_speedup": required_speedup,
        "suggested_reduction_pct": suggested_reduction_pct,
    }
