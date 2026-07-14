---
type: is
id: is-01kxgt1nsss6p9657yvhvjhp6h
title: "R9: Markdown checker anchors tracked paths to cwd"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:15:58.648Z
updated_at: 2026-07-14T17:43:54.453Z
closed_at: 2026-07-14T17:43:54.453Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 third-round review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581145258. Discover the Git repository root independently of the caller cwd, resolve tracked Markdown there, retain explicit-path semantics, and add a nested-directory CLI regression test.
