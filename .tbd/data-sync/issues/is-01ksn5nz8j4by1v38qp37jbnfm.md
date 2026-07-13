---
type: is
id: is-01ksn5nz8j4by1v38qp37jbnfm
title: Update spec plans for current tbd/qmd facts and metadata
kind: task
status: closed
priority: 2
version: 2
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:28.466Z
updated_at: 2026-05-27T17:02:45.862Z
closed_at: 2026-05-27T17:02:45.862Z
close_reason: "Updated qmd spec plan: comparison figures (tbd 87%/420->85%/366; qmd 76%/431->72%/353; node-llama-cpp 226->129 with pnpm-basis caveat; mcp-sdk 90->91), risk table, direct-entry count 16->22, audited commit 40610c3->443760f, bun.lock->pnpm-lock references, added tree-sitter note. TS parent + knip plans cite the appendices generically (no hard numbers) — no change needed."
---
Propagate refreshed facts into plan-2026-03-04-qmd-ai-application-porting-path.md (transitive-mass figures e.g. node-llama-cpp share, dep counts), the parent TS porting-path plan, and the knip plan where they cite tbd/qmd numbers. Update any cited source commits/dates and the 'why qmd is harder' quantitative comparison.
