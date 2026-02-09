---
created_at: 2026-02-09T00:29:18.167Z
dependencies: []
id: is-01kgzwtzyrg92z2r14eg3s35me
kind: bug
labels: []
parent_id: is-01kgzsz76j7ykszy5wc27rjqp8
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 3.4 Fix frozenset note — misleading immutability claim
type: is
updated_at: 2026-02-09T00:29:18.167Z
version: 1
---
Says HashSet (immutable by default) but Rust HashSet is mutable with let mut. Fix in: reference/python-to-rust-mapping-reference.md L33
