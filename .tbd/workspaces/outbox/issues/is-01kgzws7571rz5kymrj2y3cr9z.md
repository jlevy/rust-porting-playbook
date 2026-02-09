---
created_at: 2026-02-09T00:28:20.006Z
dependencies: []
id: is-01kgzws7571rz5kymrj2y3cr9z
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 1.3 Fix non-compiling build.rs code in porting guide
type: is
updated_at: 2026-02-09T00:28:20.006Z
version: 1
---
4 compile errors: CARGO_PKG_METADATA_* doesn't exist, env! 2nd arg is error msg not default, concat! can't accept const vars, or_else type mismatch. Fix in: reference/python-to-rust-porting-guide.md L54-71 and L76-100, guidelines/rust-cli-app-patterns.md L319-324
