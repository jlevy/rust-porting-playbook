---
type: is
id: is-01kzj9aqjj644cbrnq7k1nzwk2
title: Enforce wheel-only execution and lockfile cool-off
kind: task
status: closed
priority: 1
version: 4
labels:
  - supply-chain
  - python
dependencies: []
parent_id: is-01kzj7wjwrv2swn2r4ebapcqgk
created_at: 2026-08-09T03:33:42.097Z
updated_at: 2026-08-09T03:59:50.574Z
closed_at: 2026-08-09T03:59:50.574Z
close_reason: Implemented the reviewed install/load/open-time policy, explicit cache disable, CODEOWNERS and all-text Unicode gate, pre-open bootstrap, wheel-only execution, and deterministic 14-day lock-artifact check; targeted and full Python 3.14 validation pass.
---
Set UV_NO_BUILD=1 in CI and the repository-owned uv subprocess so validation cannot execute an sdist build backend. Add a deterministic checker that rejects registry artifacts in PEP 723 lockfiles until every locked artifact is at least 14 days old; do not inject a rolling resolver setting into an already-frozen lock.

## Notes

Testing showed UV_EXCLUDE_NEWER='14 days' changes resolver inputs and makes uv --locked reject the existing lock. The implementation separates resolution policy from frozen-lock validation: artifact timestamps enforce age; UV_NO_BUILD enforces wheel-only execution. The repository subprocess also clears an ambient UV_EXCLUDE_NEWER so a caller's shell cannot perturb the frozen run.
