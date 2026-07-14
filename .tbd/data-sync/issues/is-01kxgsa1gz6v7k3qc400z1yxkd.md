---
type: is
id: is-01kxgsa1gz6v7k3qc400z1yxkd
title: "R5: Claude hooks use cwd-relative paths"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:03:04.222Z
updated_at: 2026-07-14T17:43:54.423Z
closed_at: 2026-07-14T17:43:54.423Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 follow-up review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581052624. Resolve Claude SessionStart and PreCompact scripts from CLAUDE_PROJECT_DIR and add nested-directory regression coverage.
