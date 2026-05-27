---
type: is
id: is-01ksn5nyyzqx1a7n3znk9zwcsh
title: Refresh qmd direct-dependency port plan
kind: task
status: open
priority: 1
version: 1
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:28.159Z
updated_at: 2026-05-27T16:53:28.159Z
---
Update research-qmd-dependency-port-plan.md to current v2.5.2 deps: added tree-sitter-{go,python,rust,typescript}, web-tree-sitter, better-sqlite3, zod (and 5 sqlite-vec optional platform pkgs). Map new deps to Rust: tree-sitter-* -> native tree-sitter Rust grammars (key insight: parsers are already Rust!), better-sqlite3 -> rusqlite, web-tree-sitter -> tree-sitter crate, zod -> validation approach. Update risk tiers + counts + metadata.
