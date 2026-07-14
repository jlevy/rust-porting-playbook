---
type: is
id: is-01kxgsa2ebtk8xk2ptxpwdaajy
title: "R8: Preserve npm global tbd discovery"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:03:05.162Z
updated_at: 2026-07-14T17:43:54.444Z
closed_at: 2026-07-14T17:43:54.444Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 follow-up review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581052651. Restore npm global prefix discovery while retaining exact 0.4.0 version enforcement and pinned fallback behavior. Add regression tests.
