---
created_at: 2026-02-09T00:28:44.536Z
dependencies: []
id: is-01kgzwsz3sb4ggdg7h0nv8q8qa
kind: task
labels: []
parent_id: is-01kgzsz6t5wsggwaxv3tqv5jc1
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 2.3 Add Cow<str> to type mappings in porting rules
type: is
updated_at: 2026-02-09T00:28:44.536Z
version: 1
---
Essential for text-processing ports. Add row after L42 in guidelines/python-to-rust-porting-rules.md: str (sometimes modified) → Cow<'_, str>
