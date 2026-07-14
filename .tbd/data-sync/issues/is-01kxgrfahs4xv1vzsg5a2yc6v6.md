---
type: is
id: is-01kxgrfahs4xv1vzsg5a2yc6v6
title: "R1: CI skips lockfile golden check"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T16:48:28.728Z
updated_at: 2026-07-14T17:43:54.371Z
closed_at: 2026-07-14T17:43:54.370Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3576126920. Add a reproducible CI check that regenerates the committed tbd and qmd lockfile inventory artifacts from the exact pinned upstream lockfiles and fails on drift. Correct CONTRIBUTING.md validation guidance and add tests.
