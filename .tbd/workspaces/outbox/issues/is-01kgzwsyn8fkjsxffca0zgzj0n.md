---
close_reason: "Fixed: once_cell replaced with std::sync::LazyLock everywhere"
closed_at: 2026-02-09T00:54:36.673Z
created_at: 2026-02-09T00:28:44.071Z
dependencies: []
id: is-01kgzwsyn8fkjsxffca0zgzj0n
kind: task
labels: []
parent_id: is-01kgzsz6t5wsggwaxv3tqv5jc1
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 2.2 Replace once_cell with std::sync::LazyLock everywhere
type: is
updated_at: 2026-02-09T00:55:59.672Z
version: 3
---
Target is Rust 1.85+, LazyLock stable since 1.80. Fix in: reference/python-to-rust-mapping-reference.md L295+L420, reference/python-to-rust-porting-guide.md (search), guidelines/rust-general-rules.md L111
