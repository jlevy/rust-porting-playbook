---
type: is
id: is-01ksn5nxqjncq3ttkcve9g7zk6
title: Build reproducible lockfile-inventory extraction script
kind: task
status: open
priority: 1
version: 1
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:26.898Z
updated_at: 2026-05-27T16:53:26.898Z
---
Write a deterministic script that parses a pnpm v9 lockfile (importers + snapshots), attributes each lock entry to owner-root direct deps and groups, classifies the port action, and emits the package-inventory TSV, summary.json, and top-owners.json. Validate it reproduces the committed tbd@70d71fe numbers (454 entries / 32 direct / 420 transitive + action counts) before regenerating.
