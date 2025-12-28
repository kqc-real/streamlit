import pytest

from helpers.navigation_model import compute_visibility


def base_state():
    return {
        "test_time_limit": 120,
        "initial_frage_indices": [0, 1, 2, 3],
        "skipped_questions": [],
        "bookmarked_questions": [],
        "jump_to_idx_active": False,
    }


@pytest.mark.parametrize(
    "answered", [False, True]
)
def test_normal_mode(answered):
    state = base_state()
    if answered:
        state["frage_0_beantwortet"] = 1
    vis = compute_visibility(state, frage_idx=0, remaining_time=90, remaining_questions=3)
    assert vis.mode == "Normal"
    assert vis.options_enabled == (not answered)
    assert vis.lock_in_enabled == (not answered)
    assert vis.skip_visible == (not answered)
    assert vis.next_nav_visible == answered


def test_panic_mode_always_allows_actions():
    state = base_state()
    state["frage_0_beantwortet"] = None
    vis = compute_visibility(state, frage_idx=0, remaining_time=5, remaining_questions=3)
    assert vis.mode == "Panic"
    assert vis.options_enabled
    assert vis.lock_in_enabled
    assert vis.skip_visible
    # Next nav still hidden until answered
    assert not vis.next_nav_visible


def test_skip_review_navigation():
    state = base_state()
    state.update(
        {
            "jump_to_idx_active": True,
            "skipped_questions": [0, 2, 3],
        }
    )
    vis = compute_visibility(state, frage_idx=0, remaining_time=60, remaining_questions=3)
    assert vis.mode == "SkipReview"
    assert vis.options_enabled
    assert vis.lock_in_enabled
    assert not vis.skip_visible  # skip hidden in skip-review unless panic
    assert vis.back_to_current_visible
    assert vis.next_skipped_visible  # there is a next (2)
    assert not vis.next_nav_visible  # generic nav hidden for unanswered skipped


def test_bookmark_review_navigation():
    state = base_state()
    state.update(
        {
            "jump_to_idx_active": True,
            "bookmarked_questions": [1, 2, 3],
            "jump_source": "bookmark",
        }
    )
    vis = compute_visibility(state, frage_idx=2, remaining_time=60, remaining_questions=3)
    assert vis.mode == "BookmarkReview"
    assert vis.options_enabled
    assert vis.lock_in_enabled
    assert vis.prev_bookmarked_visible
    assert vis.next_bookmarked_visible
    assert vis.back_to_current_bookmark_visible
    # Generic nav allowed in review mode
    assert vis.next_nav_visible


def test_skip_review_no_next_skipped_when_last():
    state = base_state()
    state.update(
        {
            "jump_to_idx_active": True,
            "skipped_questions": [0],
            "jump_source": "skip",
        }
    )
    vis = compute_visibility(state, frage_idx=0, remaining_time=60, remaining_questions=1)
    assert vis.mode == "SkipReview"
    assert not vis.next_skipped_visible
    assert vis.back_to_current_visible
