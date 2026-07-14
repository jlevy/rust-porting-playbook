---
type: is
id: is-01kxgrfbb8m7n5abg2hh96kww3
title: "R4: Codex hooks use cwd-relative paths"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T16:48:29.543Z
updated_at: 2026-07-14T17:43:54.400Z
closed_at: 2026-07-14T17:43:54.400Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3576126928. Make Codex hook commands resolve from the Git repository root so session and closing-reminder hooks work from nested working directories. Add an execution regression test.
