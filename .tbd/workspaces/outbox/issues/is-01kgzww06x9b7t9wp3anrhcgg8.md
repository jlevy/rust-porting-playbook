---
created_at: 2026-02-09T00:29:51.196Z
dependencies: []
id: is-01kgzww06x9b7t9wp3anrhcgg8
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 4.8 Add concurrency/logging dependency mappings to porting rules
type: is
updated_at: 2026-02-09T00:29:51.196Z
version: 1
---
Add logging→tracing/log, asyncio→tokio, threading→std::thread/rayon, subprocess→std::process::Command. Fix in: guidelines/python-to-rust-porting-rules.md after L147
