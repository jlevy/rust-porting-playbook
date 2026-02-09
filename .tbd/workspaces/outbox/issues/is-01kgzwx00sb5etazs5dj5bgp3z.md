---
created_at: 2026-02-09T00:30:23.768Z
dependencies: []
id: is-01kgzwx00sb5etazs5dj5bgp3z
kind: task
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 5.8 Add std::process::ExitCode guidance
type: is
updated_at: 2026-02-09T00:30:23.768Z
version: 1
---
ExitCode (1.61+) is cleaner than process::exit(), allows destructors to run. Fix in: guidelines/rust-cli-app-patterns.md
