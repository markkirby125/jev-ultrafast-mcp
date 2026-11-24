"""`Session.act` stop signals: the stall streak (elements only) and the no-effect repeat (elements + text).

A click that only rewrites a paragraph ("clicked item 33") leaves the element digest alone. Counting text
as progress let a model wander between buttons forever; ignoring it cost a third click. The repeat rule
stops on the second identical action whose first run worked and whose second run changed nothing.
"""

from __future__ import annotations

from jev_ultrafast_mcp import browser
from jev_ultrafast_mcp.observe import Element, Observation


def _obs(digest: str, text_digest: str, previous: Observation | None) -> Observation:
    return Observation(
        url="https://example.test/",
        title="Example",
        text="Example page",
        elements=[Element(ref="e1", role="button", name="Save")],
        digest=digest,
        text_digest=text_digest,
        page_key="k",
        scroll={"y": 0},
        reachable=1,
        omitted=0,
        overlays=[],
        cross_frames=0,
        cross_frame_srcs=[],
        previous=previous,
    )


def _run(script: list[tuple[dict, str, str]], session: browser.Session | None = None) -> list[dict]:
    """Act each op in turn; the page then reads (digest, text_digest). Returns the payloads."""
    session = session or browser.Session("t", cfg=None, cdp=None)
    session.last = _obs("d0", "t0", None)
    state = {}

    def run_op(raw_op, *, dry_run, strict=True):
        return browser.Step(op=raw_op["op"], ok=True, ref=raw_op.get("ref"))

    def observe(**_):
        session.last = _obs(state["digest"], state["text"], session.last)
        return session.last

    session._run_op = run_op
    session.observe = observe
    payloads = []
    for op, digest, text in script:
        state.update(digest=digest, text=text)
        payloads.append(session.act([op]))
    return payloads


CLICK = {"op": "click", "ref": "e33"}
OTHER = {"op": "click", "ref": "e3"}


def _stuck(payloads: list[dict]) -> list[bool]:
    return [bool(p.get("stuck")) for p in payloads]


def test_repeat_of_a_click_that_worked_stops_on_the_second_click():
    # click 1 prints "clicked item 33" (text only); click 2 changes nothing at all
    assert _stuck(_run([(CLICK, "d0", "t1"), (CLICK, "d0", "t1")])) == [False, True]


def test_repeat_after_an_element_change_stops_on_the_second_click():
    # click 1 renames the button; click 2 changes nothing
    assert _stuck(_run([(CLICK, "d1", "t1"), (CLICK, "d1", "t1")])) == [False, True]


def test_repeated_click_that_keeps_changing_text_is_not_a_no_effect_repeat():
    # a counter: every click moves the text, so neither the repeat rule nor the streak stops it
    payloads = _run([(CLICK, "d0", "t1"), (CLICK, "d0", "t2"), (CLICK, "d0", "t3")])
    assert _stuck(payloads) == [False, False, False]


def test_dead_click_still_gets_the_old_limit():
    # the click never did anything: a slow render keeps its three chances
    assert _stuck(_run([(CLICK, "d0", "t0")] * 3)) == [False, False, True]


def test_wandering_between_text_only_buttons_stops_at_the_old_limit():
    # text changes are not progress for the streak, so wandering cannot outrun NO_CHANGE_LIMIT
    assert _stuck(_run([(CLICK, "d0", "t1"), (OTHER, "d0", "t2"), (CLICK, "d0", "t1")])) == [False, False, True]


def test_a_different_ref_with_no_effect_is_not_a_repeat():
    assert _stuck(_run([(CLICK, "d0", "t1"), (OTHER, "d0", "t1")])) == [False, False]


def test_refless_ops_are_never_a_repeat():
    # scroll at the bottom of a page: the model gets to pick something else
    scroll = {"op": "scroll", "dir": "down"}
    assert _stuck(_run([(scroll, "d0", "t1"), (scroll, "d0", "t1")])) == [False, False]


def test_page_changed_stays_elements_only_and_reset_forgets_the_repeat():
    session = browser.Session("t", cfg=None, cdp=None)
    session._no_change_streak, session._worked = 2, ("click", "e33")
    session.reset_progress()
    assert (session._no_change_streak, session._worked) == (0, None)
    assert _run([(CLICK, "d0", "t1")])[0]["page_changed"] is False
