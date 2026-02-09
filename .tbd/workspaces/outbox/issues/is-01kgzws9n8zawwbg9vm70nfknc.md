---
created_at: 2026-02-09T00:28:22.568Z
dependencies: []
id: is-01kgzws9n8zawwbg9vm70nfknc
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 1.9 Add dict→HashMap insertion-order warning
type: is
updated_at: 2026-02-09T00:28:22.568Z
version: 1
---
Python dict preserves insertion order since 3.7; HashMap does not. Add IndexMap guidance. Fix in: guidelines/python-to-rust-porting-rules.md L49, reference/python-to-rust-mapping-reference.md L31
