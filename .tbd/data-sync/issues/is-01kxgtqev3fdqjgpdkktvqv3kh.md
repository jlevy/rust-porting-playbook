---
type: is
id: is-01kxgtqev3fdqjgpdkktvqv3kh
title: "R11: Codex hook bootstrap depends on git cwd"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T17:27:52.418Z
updated_at: 2026-07-14T17:43:54.724Z
closed_at: 2026-07-14T17:43:54.722Z
close_reason: "Rejected after source validation: Codex 0.135.0 launches hooks at request.cwd and serializes the same cwd without exposing a hooks.json source path, so the claimed independently recoverable outside-repository state is not part of the hook contract. Evidence was posted on PR #16 and the thread was resolved."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3581207704. Validate the claimed outside-worktree failure against Codex 0.135.0 hook execution semantics and either implement a portable fix or reject the finding with exact source evidence.
