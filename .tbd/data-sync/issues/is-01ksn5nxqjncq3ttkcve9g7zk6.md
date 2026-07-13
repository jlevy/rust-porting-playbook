---
type: is
id: is-01ksn5nxqjncq3ttkcve9g7zk6
title: Build reproducible lockfile-inventory extraction script
kind: task
status: closed
priority: 1
version: 2
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:26.898Z
updated_at: 2026-05-27T16:59:07.306Z
closed_at: 2026-05-27T16:59:07.306Z
close_reason: "Wrote docs/project/research/data/extract_lockfile_inventory.py (pnpm v9 lockfile -> TSV+summary+top-owners). Validated against tbd@70d71fe: reproduced 454/32/420 entries and exact action counts (365/34/30/25); alias-edge resolution brings missing_edges to 0. Committed for reproducibility."
---
Write a deterministic script that parses a pnpm v9 lockfile (importers + snapshots), attributes each lock entry to owner-root direct deps and groups, classifies the port action, and emits the package-inventory TSV, summary.json, and top-owners.json. Validate it reproduces the committed tbd@70d71fe numbers (454 entries / 32 direct / 420 transitive + action counts) before regenerating.
