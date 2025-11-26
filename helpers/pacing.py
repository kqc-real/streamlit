"""Timing coach helpers for the MC test app.

Provides small, well-tested utilities to compute per-question ideal times,
assess pacing status and produce simple action recommendations.

These functions operate on seconds to avoid float surprises in UI code.
"""
from typing import List, Dict, Any
import math


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


def compute_ideal_times_by_total(questions: List[dict], total_allowed_seconds: int, min_seconds: int = 10) -> List[int]:
    """Distribute a total allowed time (in seconds) across questions proportionally by weight.

    - `questions` is a list of dicts with optional numeric `weight` (default 1).
    - `total_allowed_seconds` is the total budget for the whole test in seconds.
    - `min_seconds` enforces a per-question minimum (useful for tiny-weighted items).

    The algorithm:
    1. Compute raw proportional floats from weights.
    2. Enforce `min_seconds` floor on any question whose proportional share is smaller.
    3. If the floored/min-enforced sum exceeds the total, attempt to reduce other
       questions down toward their minima; if that's impossible (total < n*min_seconds)
       we return the current per-question minima (sum may exceed total).
    4. Otherwise, convert float allocations to integers while preserving the total by
       distributing remaining seconds according to fractional parts.
    """
    n = len(questions)
    if n == 0:
        return []

    weights = [float(q.get("weight", 1)) for q in questions]
    total_weight = sum(weights) if sum(weights) > 0 else float(n)

    # initial raw allocations (floats)
    raw = [total_allowed_seconds * (w / total_weight) for w in weights]

    # enforce minimum as float
    allocs = [r if r >= min_seconds else float(min_seconds) for r in raw]
    sum_allocs = sum(allocs)

    # If we've exceeded the budget after enforcing minima, try to reduce others
    if sum_allocs > total_allowed_seconds:
        reducible = sum((a - min_seconds) for a in allocs)
        needed_reduce = sum_allocs - total_allowed_seconds
        if reducible <= 0:
            # cannot reduce below minima; return integer mins (sum may exceed total)
            return [int(round(a)) for a in allocs]
        # reduce proportionally from those above min, but not below min
        for i in sorted(range(n), key=lambda i: allocs[i] - min_seconds, reverse=True):
            if needed_reduce <= 0:
                break
            can_reduce = allocs[i] - min_seconds
            take = min(can_reduce, needed_reduce)
            allocs[i] -= take
            needed_reduce -= take
        sum_allocs = sum(allocs)

    # At this point sum_allocs <= total_allowed_seconds (if reduction succeeded)
    # Convert to integer seconds while preserving total when possible.
    target = int(total_allowed_seconds)
    # If sum_allocs > target due to impossibility to reduce, just round and return
    if sum_allocs > target:
        return [int(round(a)) for a in allocs]

    floors = [int(math.floor(a)) for a in allocs]
    floor_sum = sum(floors)
    remainder = target - floor_sum

    # Distribute the remaining seconds by largest fractional part
    fracs = [allocs[i] - floors[i] for i in range(n)]
    order = sorted(range(n), key=lambda i: fracs[i], reverse=True)
    for i in order:
        if remainder <= 0:
            break
        floors[i] += 1
        remainder -= 1

    # Ensure minima are respected (edge cases)
    for i in range(n):
        if floors[i] < min_seconds:
            floors[i] = int(min_seconds)

    return floors
