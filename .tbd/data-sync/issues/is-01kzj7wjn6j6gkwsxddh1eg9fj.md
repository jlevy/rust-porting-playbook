---
type: is
id: is-01kzj7wjn6j6gkwsxddh1eg9fj
title: Refresh tbd integration to globally installed v0.4.2
kind: chore
status: closed
priority: 1
version: 5
labels:
  - tooling
dependencies:
  - type: blocks
    target: is-01kzj7wkjmbxrw5f7saykf39a7
parent_id: is-01kzj7w4t9d80a2bwamjm50bhc
child_order_hints:
  - is-01kzj7yga080v5pamcq2sdfvzp
created_at: 2026-08-09T03:08:29.733Z
updated_at: 2026-08-09T03:13:00.935Z
closed_at: 2026-08-09T03:13:00.935Z
close_reason: Upgraded the project integration to tbd v0.4.2, preserved the repository's hardened hook behavior, retained the refreshed proxy diagnostics, updated version-aware tests, and restored all 11 agent-hook tests.
---
Run the existing-project tbd upgrade, inspect generated changes, and validate refreshed Claude and Codex hooks without including unrelated user files.
