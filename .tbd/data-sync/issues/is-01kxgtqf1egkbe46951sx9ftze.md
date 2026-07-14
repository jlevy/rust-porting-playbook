---
type: is
id: is-01kxgtqf1egkbe46951sx9ftze
title: "R12: Closing reminder root discovery depends on cwd"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:27:52.621Z
updated_at: 2026-07-14T17:43:54.467Z
closed_at: 2026-07-14T17:43:54.467Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581207713. Anchor both Claude and Codex closing-reminder hooks to the worktree containing their script, and cover invocation from outside the repository.
