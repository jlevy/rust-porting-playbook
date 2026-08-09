---
type: is
id: is-01kzj7yga080v5pamcq2sdfvzp
title: Preserve hardened agent-hook behavior after the tbd v0.4.2 refresh
kind: bug
status: closed
priority: 1
version: 3
labels:
  - tooling
  - regression
dependencies: []
parent_id: is-01kzj7wjn6j6gkwsxddh1eg9fj
created_at: 2026-08-09T03:09:32.863Z
updated_at: 2026-08-09T03:13:00.920Z
closed_at: 2026-08-09T03:13:00.919Z
close_reason: Upgraded the project integration to tbd v0.4.2, preserved the repository's hardened hook behavior, retained the refreshed proxy diagnostics, updated version-aware tests, and restored all 11 agent-hook tests.
---
The v0.4.2 setup refresh replaces repository-specific hook anchoring, global CLI discovery, safe fallback, best-effort GitHub CLI provisioning, and push-detection behavior. The baseline suite now has 15 failures and 8 errors in tests/test_agent_hooks.py. Reconcile the refreshed integration with these required behaviors and restore the full suite.
