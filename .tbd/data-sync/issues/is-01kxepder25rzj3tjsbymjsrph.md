---
type: is
id: is-01kxepder25rzj3tjsbymjsrph
title: Add executable validation for canonical documentation snippets
kind: task
status: open
priority: 2
version: 1
labels:
  - review-2026-07-13
dependencies: []
created_at: 2026-07-13T21:34:01.473Z
updated_at: 2026-07-13T21:34:01.473Z
---
Senior review SER-004. Repository-level tests now validate links, anchors, fences, the Python utility, shell scripts, JSON, and YAML loading, but the many illustrative Rust/YAML/shell snippets are not compiled or executed. Select canonical snippets, extract them into fixtures or mdBook-style tests, and gate their syntax/behavior without treating intentionally partial examples as programs.
