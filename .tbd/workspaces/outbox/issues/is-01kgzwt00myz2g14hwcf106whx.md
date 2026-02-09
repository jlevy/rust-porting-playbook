---
created_at: 2026-02-09T00:28:45.459Z
dependencies: []
id: is-01kgzwt00myz2g14hwcf106whx
kind: task
labels: []
parent_id: is-01kgzsz6t5wsggwaxv3tqv5jc1
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 2.5 Add match command.as_str() pattern
type: is
updated_at: 2026-02-09T00:28:45.459Z
version: 1
---
match command { 'quit' => } won't compile if command is String. Fix in: reference/python-to-rust-mapping-reference.md L93
