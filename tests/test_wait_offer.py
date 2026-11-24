"""What the decision model is told WAIT means, and when a repeat is allowed.

Measured against the local model on a counter page ("Click the Add button 3
times"): after the first click the model answered WAIT 0.43 over CLICK 0.29,
twice, and the run stopped at one click. The only thing that had changed in the
request was one click in `recent_actions`; emptying it restored CLICK 0.81. The
label "Wait for the page to update." reads as the natural sequel to any click.
Reworded to name loading, WAIT fell to 0.02 on that page and kept 0.90 on a page
whose text says it is loading. The repeat rule had no exception for a goal that
asks for a count, which left CLICK, DONE and BLOCKED level at the second click.

These tests pin the words, because the words are the whole mechanism.
"""
from __future__ import annotations

import dataclasses

import pytest

from jev_ultrafast_mcp import policy
from jev_ultrafast_mcp.config import Config
from jev_ultrafast_mcp.observe import Element, Observation


def _sent(monkeypatch) -> dict:
    """The operation question `choose` would put to the model for a one-button page."""
    sent: dict = {}

    def _capture(_cfg, body):
        sent.update(body)
        raise policy.TurboUnavailable("captured")

    monkeypatch.setattr(policy, "_decide", _capture)
    observation = Observation(
        url="https://example.test/", title="Counter", text="count: 1", digest="d",
        elements=[Element(ref="e1", role="button", name="Add")],
        text_digest="t", page_key="k", scroll={"y": 0}, reachable=1, omitted=0,
        overlays=[], cross_frames=0, cross_frame_srcs=[],
    )
    cfg = dataclasses.replace(Config.from_env(), typesafe_key="test-key")
    history = [{"op": "click", "ref": "e1", "target": "Add", "ok": True}]
    with pytest.raises(policy.TurboUnavailable, match="captured"):
        policy.choose(cfg, observation, "Click the Add button 3 times", history)
    return sent["questions"]["operation"]


def test_wait_is_described_as_waiting_on_a_loading_page(monkeypatch):
    wait = _sent(monkeypatch)["criteria"]["WAIT"]
    assert "loading" in wait.lower(), wait
    assert "update" not in wait.lower(), (
        "every click is followed by the page updating; a WAIT described that way "
        "is chosen after any click")


def test_wait_stays_on_offer(monkeypatch):
    """Rewording, not removal: a page that says it is loading still needs WAIT."""
    assert "WAIT" in _sent(monkeypatch)["criteria"]


def test_the_repeat_rule_excepts_a_goal_that_asks_for_a_count(monkeypatch):
    rules = " ".join(_sent(monkeypatch)["instructions"]["rules"].split())
    assert "Unless the goal asks for a repeat count" in rules
    assert "is not progress" in rules, "the stall rule itself must stay"
    assert "A goal with a count is not finished until the page shows that count" in rules
