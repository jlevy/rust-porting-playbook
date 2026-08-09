---
type: is
id: is-01kzj891m17cz6znhrag3t3wfx
title: Protect agent configuration and reject hidden instruction text
kind: task
status: closed
priority: 1
version: 3
labels:
  - supply-chain
  - github
dependencies: []
parent_id: is-01kzj7wjwrv2swn2r4ebapcqgk
created_at: 2026-08-09T03:15:18.272Z
updated_at: 2026-08-09T03:59:50.561Z
closed_at: 2026-08-09T03:59:50.561Z
close_reason: Implemented the reviewed install/load/open-time policy, explicit cache disable, CODEOWNERS and all-text Unicode gate, pre-open bootstrap, wheel-only execution, and deterministic 14-day lock-artifact check; targeted and full Python 3.14 validation pass.
---
Add CODEOWNERS coverage for agent/editor autostart, policy, executable validation, workflow, and lockfile paths. Scan every tracked text file, including automation configuration and Markdown fences, for zero-width and bidirectional control characters so invisible prompt injection cannot land unnoticed.
