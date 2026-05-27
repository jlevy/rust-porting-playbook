---
type: is
id: is-01ksn5ny9s5rkjtdzkbsnermh6
title: Refresh tbd direct-dependency port plan
kind: task
status: open
priority: 1
version: 1
labels:
  - pr-10
dependencies: []
parent_id: is-01ksn5hrb4gvxrpm4948d2j676
created_at: 2026-05-27T16:53:27.480Z
updated_at: 2026-05-27T16:53:27.480Z
---
Update research-tbd-dependency-port-plan.md to current direct deps: runtime now atomically, commander, github-slugger, gray-matter, marked, marked-terminal, picocolors, pretty-bytes, pretty-ms, ulid, yaml, zod; root devDeps restructured (eslint stack + npm-check-updates + prettier); @changesets/cli dropped. Add Rust targets for new deps (marked->comrak/pulldown-cmark, zod->validation, ulid->ulid crate, pretty-bytes->humansize). Update counts + metadata.
