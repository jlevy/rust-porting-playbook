---
type: is
id: is-01kxgrfatn5r65z3yg3b56jhhv
title: "R2: Stale global tbd bypasses repository pin"
kind: bug
status: closed
priority: 1
version: 3
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T16:48:29.012Z
updated_at: 2026-07-14T17:43:54.387Z
closed_at: 2026-07-14T17:43:54.387Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3576126923. Ensure both Claude and Codex session hooks use the local tbd binary only when it matches required version 0.4.0; otherwise use the pinned zero-install fallback with lifecycle scripts disabled. Add regression tests.
