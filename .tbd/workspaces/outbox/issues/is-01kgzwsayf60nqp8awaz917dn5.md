---
created_at: 2026-02-09T00:28:23.886Z
dependencies: []
id: is-01kgzwsayf60nqp8awaz917dn5
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 1.12 Fix main() error handling contradiction
type: is
updated_at: 2026-02-09T00:28:23.886Z
version: 1
---
main() returns color_eyre::Result<()> but also manually catches errors with if let Err(e) and process::exit(1). Pick one pattern. Fix in: guidelines/rust-cli-app-patterns.md L169-183
