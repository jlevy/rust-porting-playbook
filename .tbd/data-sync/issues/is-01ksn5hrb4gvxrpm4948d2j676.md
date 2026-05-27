---
type: is
id: is-01ksn5hrb4gvxrpm4948d2j676
title: "Refresh PR #10 tbd/qmd dependency data to current upstream state"
kind: epic
status: open
priority: 1
version: 7
labels:
  - review
  - pr-10
dependencies: []
child_order_hints:
  - is-01ksn5nxqjncq3ttkcve9g7zk6
  - is-01ksn5ny0qdz1a0rjw8ezdkn1g
  - is-01ksn5ny9s5rkjtdzkbsnermh6
  - is-01ksn5nynb81ymh0ngzs50czyc
  - is-01ksn5nyyzqx1a7n3znk9zwcsh
  - is-01ksn5nz8j4by1v38qp37jbnfm
created_at: 2026-05-27T16:51:10.308Z
updated_at: 2026-05-27T16:53:28.466Z
---
PR #10 (TypeScript-to-Rust porting path) includes tbd and qmd as exemplar dependency port plans, derived from upstream snapshots: tbd@70d71fe and qmd@40610c3 (both ~2026-03-04). Both projects have since been updated significantly. Re-derive the dependency inventories, lockfile appendices, and data files from current HEAD and update the spec plans accordingly. Branch: claude/typescript-migration-plan-EBkrU.
