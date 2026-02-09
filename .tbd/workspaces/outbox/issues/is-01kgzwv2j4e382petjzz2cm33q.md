---
close_reason: "Fixed: TypedDict serde coupling corrected"
closed_at: 2026-02-09T00:55:01.839Z
created_at: 2026-02-09T00:29:20.835Z
dependencies: []
id: is-01kgzwv2j4e382petjzz2cm33q
kind: bug
labels: []
parent_id: is-01kgzsz76j7ykszy5wc27rjqp8
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 3.10 Fix TypedDict serde coupling and Protocol nominal note
type: is
updated_at: 2026-02-09T01:18:11.750Z
version: 5
---
TypedDict shouldn't require serde; Protocol is structural in Python but nominal in Rust. Fix in: reference/python-to-rust-mapping-reference.md L48-49
