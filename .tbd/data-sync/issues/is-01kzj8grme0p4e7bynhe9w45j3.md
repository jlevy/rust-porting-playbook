---
type: is
id: is-01kzj8grme0p4e7bynhe9w45j3
title: Upgrade eligible CI action and uv pins
kind: task
status: closed
priority: 1
version: 2
labels:
  - dependencies
  - ci
  - supply-chain
dependencies: []
parent_id: is-01kzj7wkb4gjdszdand45x12ff
created_at: 2026-08-09T03:19:31.212Z
updated_at: 2026-08-09T03:59:50.807Z
closed_at: 2026-08-09T03:59:50.807Z
close_reason: Applied all eligible reviewed pins, recorded the owner-approved exact tbd exception, hardened checksum-verified gh extraction, and passed the full suite on Python 3.14.6; uv 0.12 remains separately deferred as rpp-1gar.
---
Upgrade only releases published on or before the 2026-07-25 cool-off cutoff, review release/source diffs, preserve immutable SHA pins, and remove PR cache writes.
