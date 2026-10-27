# Governor gate status: PR #1

Governor gate status: not run.

- The governor's proof command (`pytest -q` on its PATH) resolves to `/usr/bin/python3`, which lacks the package. One test fails for that reason (411 passed, 1 failed).
- Two contracts that used the venv interpreter were rejected at the governor's security gate, because that binary is not on its allowlist.
- The venv's suite passes on this branch at 9c9f0d5: 412 passed.
- An allowlist request is filed: https://github.com/markkirby125/kirby-governor-mcp/issues/2
- Merge is on hold until `verify_adversarial_diff` has run on a fresh contract. This PR is not called done.
