---
created_at: 2026-02-09T00:28:21.282Z
dependencies: []
id: is-01kgzws8d3q4j1wqkvpfwp7evk
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 1.6 Fix swapped version constraint mappings
type: is
updated_at: 2026-02-09T00:28:21.282Z
version: 1
---
~=1.4→~1.4 is WRONG (should be caret 1.4). ==1.4.*→1.4 is WRONG (should be ~1.4). The two rows are swapped. Fix in: reference/python-to-rust-mapping-reference.md L339-340
