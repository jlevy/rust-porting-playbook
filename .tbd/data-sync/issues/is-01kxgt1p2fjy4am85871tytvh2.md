---
type: is
id: is-01kxgt1p2fjy4am85871tytvh2
title: "R10: tbd prime hook skips repository root"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:15:58.926Z
updated_at: 2026-07-14T17:43:54.460Z
closed_at: 2026-07-14T17:43:54.460Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 third-round review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581145274. Change both tbd session hooks to the Git repository root before running local or pinned tbd prime, fail with a clear diagnostic outside a worktree, and add nested-directory regression coverage.
