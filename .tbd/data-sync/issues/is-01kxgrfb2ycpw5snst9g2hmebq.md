---
type: is
id: is-01kxgrfb2ycpw5snst9g2hmebq
title: "R3: Codex starts tbd before gh"
kind: bug
status: closed
priority: 2
version: 2
labels:
  - pr-review
  - pull-request-16
dependencies: []
parent_id: is-01kxgrezbkn8x79ndqghz4khhy
created_at: 2026-07-14T16:48:29.277Z
updated_at: 2026-07-14T17:43:54.394Z
closed_at: 2026-07-14T17:43:54.394Z
close_reason: "Fixed on PR #16; regression coverage and the full repository validation suite pass, all review threads are resolved, and both required checks are green."
---
PR #16 review thread https://github.com/jlevy/rust-porting-playbook/pull/16#discussion_r3576126925. Ensure the Codex SessionStart hook provisions gh before running tbd prime, matching the repository setting use_gh_cli: true. Add structural regression coverage.
