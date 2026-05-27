---
type: is
id: is-01ksn5nynb81ymh0ngzs50czyc
title: Regenerate qmd lockfile data + transitive appendix from current HEAD
kind: task
status: open
priority: 1
version: 1
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:27.851Z
updated_at: 2026-05-27T16:53:27.851Z
---
qmd moved 40610c3 -> 443760f (v2.5.2). Regenerate data/qmd-lockfile-* and research-qmd-transitive-lockfile-appendix.md. Note: original used bun.lock; switch basis to pnpm-lock.yaml for consistency with tbd + reproducibility, and document the change. Update counts, owner table, alias notes, metadata.
