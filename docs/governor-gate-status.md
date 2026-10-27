# Governor gate status: PR #1

Status: escalated to a human. The governor's automated cycles are used up.

- Contract `done-gate-main6`, base `main` at `d55479b`, proof command `/home/paulk/jev-ultrafast-mcp/.venv/bin/python -m pytest -q`.
- Cycle 1 (on `0ae3798`): REJECT. The stashed `cdp.py` change was in the review's diff, and this note said the gate had not run.
- Cycle 2 (on `ceb2247`): REJECT. The review's diff included untracked `.claude/` and `docs/TASKS.md`, and the handoff files held copied instruction text.
- Cycle 3 (on `78c4259`): REJECT, escalated. Blocking: an unrequested debug print in the `select` path in `browser.py`. The judge's shell also refused the proof command, so the suite result is unverified by the governor. The venv suite passed 412 of 412 on `9c9f0d5`.
- Non-blocking, from cycle 3: an unclosed test `httpx.Client`; a tautological `DONE_REFUSALS` count assertion; the fake session's history not mirroring the real one; refusals spending the shared `recovered` budget; no test for the refusal budget guard; a `wrangler` call per backup request.

Merge stays on hold. This PR is not called done.
