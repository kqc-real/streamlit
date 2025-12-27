"""
Lightweight navigation/visibility model used in tests to validate button states
across modes (normal, panic, skip review, bookmark review). This mirrors the
conditions in `main_view.py` without invoking Streamlit widgets.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Visibility:
    mode: str
    options_enabled: bool
    lock_in_enabled: bool
    skip_visible: bool
    skip_enabled: bool
    next_nav_visible: bool
    back_to_current_visible: bool
    next_skipped_visible: bool
    prev_bookmarked_visible: bool
    next_bookmarked_visible: bool
    back_to_current_bookmark_visible: bool


def _panic_active(session_state: dict, remaining_time: int, remaining_questions: int, threshold: int) -> bool:
    has_limit = bool(session_state.get("test_time_limit", 0))
    if not has_limit or remaining_time is None:
        return False
    return remaining_time < remaining_questions * threshold


def _next_skipped(skipped: list[int], current_idx: int) -> Optional[int]:
    if current_idx not in skipped:
        return None
    pos = skipped.index(current_idx)
    if pos + 1 < len(skipped):
        return skipped[pos + 1]
    return None


def _bookmark_neighbors(initial_indices: list[int], bookmarks: list[int], current_idx: int) -> tuple[Optional[int], Optional[int]]:
    if current_idx not in bookmarks:
        return None, None
    # Use sorted by initial order for deterministic navigation
    sorted_bm = sorted(bookmarks, key=lambda i: initial_indices.index(i) if i in initial_indices else i)
    pos = sorted_bm.index(current_idx)
    prev_bm = sorted_bm[pos - 1] if pos > 0 else None
    next_bm = sorted_bm[pos + 1] if pos + 1 < len(sorted_bm) else None
    return prev_bm, next_bm


def compute_visibility(
    session_state: dict,
    frage_idx: int,
    remaining_time: int,
    remaining_questions: int,
    panic_threshold: int = 15,
) -> Visibility:
    answered = session_state.get(f"frage_{frage_idx}_beantwortet") is not None
    skipped = session_state.get("skipped_questions", [])
    bookmarks = session_state.get("bookmarked_questions", [])
    jump_active = bool(session_state.get("jump_to_idx_active"))
    panic_mode = _panic_active(session_state, remaining_time, remaining_questions, panic_threshold)

    is_skipped = frage_idx in skipped
    is_bookmarked = frage_idx in bookmarks

    # Mode selection
    if jump_active and is_skipped:
        mode = "SkipReview"
    elif jump_active and is_bookmarked:
        mode = "BookmarkReview"
    elif panic_mode:
        mode = "Panic"
    else:
        mode = "Normal"

    # Options/Lock In
    options_enabled = not answered or panic_mode
    lock_in_enabled = options_enabled

    # Skip visibility
    skip_visible = panic_mode or ((not answered) and not (is_skipped and jump_active))
    skip_enabled = not answered or panic_mode

    # Next navigation (generic)
    is_current_skipped_unanswered = is_skipped and jump_active and not answered
    next_nav_visible = not is_current_skipped_unanswered and (answered or jump_active)

    # Skip review navigation
    next_skipped = _next_skipped(skipped, frage_idx) if jump_active and is_skipped else None
    back_to_current_visible = jump_active and is_skipped
    next_skipped_visible = next_skipped is not None

    # Bookmark navigation
    prev_bm, next_bm = _bookmark_neighbors(session_state.get("initial_frage_indices", []), bookmarks, frage_idx)
    prev_bookmarked_visible = jump_active and is_bookmarked and prev_bm is not None
    next_bookmarked_visible = jump_active and is_bookmarked and next_bm is not None
    back_to_current_bookmark_visible = jump_active and is_bookmarked

    return Visibility(
        mode=mode,
        options_enabled=options_enabled,
        lock_in_enabled=lock_in_enabled,
        skip_visible=skip_visible,
        skip_enabled=skip_enabled,
        next_nav_visible=next_nav_visible,
        back_to_current_visible=back_to_current_visible,
        next_skipped_visible=next_skipped_visible,
        prev_bookmarked_visible=prev_bookmarked_visible,
        next_bookmarked_visible=next_bookmarked_visible,
        back_to_current_bookmark_visible=back_to_current_bookmark_visible,
    )
