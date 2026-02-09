---
close_reason: "Fixed: match command.as_str() pattern added with explanation"
closed_at: 2026-02-09T00:54:37.907Z
created_at: 2026-02-09T00:28:45.459Z
dependencies: []
id: is-01kgzwt00myz2g14hwcf106whx
kind: task
labels: []
parent_id: is-01kgzsz6t5wsggwaxv3tqv5jc1
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 2.5 Add match command.as_str() pattern
type: is
updated_at: 2026-02-09T00:55:59.693Z
version: 3
---
match command { 'quit' => } won't compile if command is String. Fix in: reference/python-to-rust-mapping-reference.md L93
