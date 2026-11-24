"""A counter: the same click keeps producing new text, so it is not a stall.

Only a repeat of the SAME (op, ref) whose text moved again is held out of the
stall streak. A text change from a different ref still counts towards it, which
is what stops a model wandering between text-only buttons.
"""

from __future__ import annotations

from jev_ultrafast_mcp import browser, policy
from jev_ultrafast_mcp.observe import Element
from tests.test_repeat_stop import CLICK, OTHER, _run, _stuck

THIRD = {"op": "click", "ref": "e4"}


def _count(op: dict, n: int, start: int = 1) -> list[tuple[dict, str, str]]:
    return [(op, "d0", f"t{i}") for i in range(start, start + n)]


def test_same_ref_whose_text_keeps_changing_continues_past_the_limit():
    payloads = _run(_count(CLICK, 8))
    assert _stuck(payloads) == [False] * 8
    assert all(p["page_changed"] is False for p in payloads)  # still elements-only


def test_a_different_ref_changing_text_does_not_reset_the_streak():
    # counting on one button earns nothing for the next: two more targets and it stops
    script = _count(CLICK, 3) + [(OTHER, "d0", "t9"), (THIRD, "d0", "t10")]
    assert _stuck(_run(script)) == [False, False, False, False, True]


def test_identical_state_repeat_after_counting_stops_at_once():
    payloads = _run(_count(CLICK, 4) + [(CLICK, "d0", "t4")])
    assert _stuck(payloads) == [False] * 4 + [True]
    assert "already took effect" in payloads[-1]["stuck"]


def test_text_only_repeats_are_capped():
    # a dead button under a ticking clock: 1 first click + the cap + 2 to finish the streak
    n = 1 + browser.TEXT_REPEAT_LIMIT + 2
    payloads = _run(_count(CLICK, n))
    assert _stuck(payloads) == [False] * (n - 1) + [True]
    assert "3 consecutive" in payloads[-1]["stuck"]


def test_reset_progress_forgets_the_held_repeats():
    session = browser.Session("t", cfg=None, cdp=None)
    session._text_repeats = 5
    session.reset_progress()
    assert session._text_repeats == 0


def _session_after(script) -> browser.Session:
    session = browser.Session("t", cfg=None, cdp=None)
    _run(script, session)
    return session


def test_counting_names_the_ref_only_while_its_text_keeps_moving_and_under_the_cap():
    assert _session_after(_count(CLICK, 1)).counting is None  # one click proves nothing
    assert _session_after(_count(CLICK, 3)).counting == ("click", "e33")
    assert _session_after(_count(CLICK, 3) + [(OTHER, "d0", "t9")]).counting is None
    assert _session_after(_count(CLICK, 2 + browser.TEXT_REPEAT_LIMIT)).counting is None
    # a click that flips its own element (the hover-menu loop) is not counting
    assert _session_after([(CLICK, "d1", "t1"), (CLICK, "d2", "t2")]).counting is None


def test_a_counting_ref_is_not_withdrawn_but_any_other_retried_ref_is():
    add, other = Element(ref="e33", role="button", name="Add"), Element(ref="e3", role="button", name="Reset")
    history = [{"op": "click", "ref": "e33", "ok": True}] * 3

    assert policy.withdraw_stalled({"CLICK": [add, other]}, history)["CLICK"] == [other]
    assert policy.withdraw_stalled({"CLICK": [add, other]}, history, keep=("click", "e33"))["CLICK"] == [add, other]
    assert policy.withdraw_stalled({"CLICK": [add, other]}, history, keep=("click", "e3"))["CLICK"] == [other]
