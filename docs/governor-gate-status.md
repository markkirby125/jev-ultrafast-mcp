# Governor gate status: PR #1

Status: gate ran, verdict REJECT (cycle 1 of 3).

- Contract `done-gate-main6`, base `main` at `d55479b`, proof command `/home/paulk/jev-ultrafast-mcp/.venv/bin/python -m pytest -q`. The security gate accepted the venv interpreter after the governor's allowlist was extended.
- The outside judge (reasonix) returned REJECT on `0ae3798`. The judge reported that pytest did not return within its shell budget, so its evidence doesn't include the suite result. The venv suite passed 412 of 412 on `9c9f0d5`.
- Blocking, first: a `stderr=PIPE` change in `cdp.py` that is never drained, which can hang Chrome. That file is parked and out of this PR; it was stashed before this review.
- Blocking, second: this note itself said the gate had not run. It now has, and it rejected.
- Non-blocking: per-request `wrangler auth token` calls, refusals spending the `recovered` budget, an extra `error` key in `recent_actions`, a backup-test stub that doesn't prove the model sees the refusal, an unclosed test `httpx.Client`.

Merge stays on hold until a cycle 2 verdict is PASS. This PR is not called done.
