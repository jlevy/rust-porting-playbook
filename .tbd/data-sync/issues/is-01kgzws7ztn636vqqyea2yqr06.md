---
close_reason: "Fixed: assert mapping split into debug_assert (invariants) and assert!/Result (validation)"
closed_at: 2026-02-09T00:54:17.959Z
created_at: 2026-02-09T00:28:20.858Z
dependencies: []
id: is-01kgzws7ztn636vqqyea2yqr06
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 1.5 Fix assert→debug_assert dangerous default
type: is
updated_at: 2026-02-09T01:18:11.580Z
version: 5
---
debug_assert! stripped in release builds. Fix in: guidelines/python-to-rust-porting-rules.md L69, reference/python-to-rust-mapping-reference.md L148. Split into invariant vs validation rows.
