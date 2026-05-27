---
type: is
id: is-01ksn5ny0qdz1a0rjw8ezdkn1g
title: Regenerate tbd lockfile data + transitive appendix from current HEAD
kind: task
status: closed
priority: 1
version: 2
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:27.191Z
updated_at: 2026-05-27T16:59:07.559Z
closed_at: 2026-05-27T16:59:07.559Z
close_reason: "Regenerated tbd-lockfile-{tsv,summary,top-owners} and the transitive appendix from current HEAD 39505243: 397 lock entries / 31 direct / 366 transitive; actions 311/34/31/21; top owner now @vitest/coverage-v8 (116); @changesets/cli gone. Updated source_commit/date and noted the script + the changesets drop."
---
tbd moved 70d71fe -> 39505243 (dropped @changesets/cli per PR #134, eslint moved to root). Regenerate data/tbd-lockfile-{package-inventory.tsv,summary.json,top-owners.json} and research-tbd-transitive-lockfile-appendix.md (counts, owner table, action counts, source_commit/date).
