---
type: is
id: is-01kzj891ckc5hgbw8v87en1zed
title: Prevent pull-request workflows from saving reusable dependency caches
kind: bug
status: closed
priority: 1
version: 3
labels:
  - supply-chain
  - github-actions
dependencies: []
parent_id: is-01kzj7wjwrv2swn2r4ebapcqgk
created_at: 2026-08-09T03:15:18.034Z
updated_at: 2026-08-09T03:59:50.547Z
closed_at: 2026-08-09T03:59:50.547Z
close_reason: Implemented the reviewed install/load/open-time policy, explicit cache disable, CODEOWNERS and all-text Unicode gate, pre-open bootstrap, wheel-only execution, and deterministic 14-day lock-artifact check; targeted and full Python 3.14 validation pass.
---
setup-uv v9 defaults enable-cache to auto on GitHub-hosted runners, so omitting the input still permits pull-request cache writes. Set enable-cache: false explicitly, keep the workflow read-only, and regression-test the invariant.
