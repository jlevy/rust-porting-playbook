---
created_at: 2026-02-09T00:30:22.853Z
dependencies: []
id: is-01kgzwwz46h5wdkprbr1gm03qv
kind: task
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 5.6 Add SIGPIPE handling guidance for CLI tools
type: is
updated_at: 2026-02-09T00:30:22.853Z
version: 1
---
Rust CLIs panic on broken pipe without SIGPIPE handling. Add to: guidelines/rust-cli-app-patterns.md, guidelines/python-to-rust-cli-porting.md
