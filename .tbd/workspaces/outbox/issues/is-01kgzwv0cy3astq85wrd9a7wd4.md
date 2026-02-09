---
close_reason: "Fixed: str.find() byte offset warning added"
closed_at: 2026-02-09T00:54:55.985Z
created_at: 2026-02-09T00:29:18.621Z
dependencies: []
id: is-01kgzwv0cy3astq85wrd9a7wd4
kind: bug
labels: []
parent_id: is-01kgzsz76j7ykszy5wc27rjqp8
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 3.5 Fix str.find() — note returns byte offset not char index
type: is
updated_at: 2026-02-09T00:55:59.730Z
version: 3
---
Python str.find() returns char index; Rust str::find() returns byte offset. Different for non-ASCII. Fix in: reference/python-to-rust-mapping-reference.md L203
