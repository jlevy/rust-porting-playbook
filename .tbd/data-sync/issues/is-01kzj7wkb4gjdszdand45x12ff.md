---
type: is
id: is-01kzj7wkb4gjdszdand45x12ff
title: Audit and apply eligible dependency and tool upgrades
kind: task
status: closed
priority: 1
version: 9
labels:
  - dependencies
  - supply-chain
dependencies:
  - type: blocks
    target: is-01kzj7wkjmbxrw5f7saykf39a7
parent_id: is-01kzj7w4t9d80a2bwamjm50bhc
child_order_hints:
  - is-01kzj8grm3jrwvxjc9xfew1ymk
  - is-01kzj8grme0p4e7bynhe9w45j3
  - is-01kzj8grn7s2x4jyetnkxcadmw
  - is-01kzj8gxj8ksqnqzqkhxv3kkx3
  - is-01kzj8xcgc5p7xzry40rsfnfza
created_at: 2026-08-09T03:08:30.435Z
updated_at: 2026-08-09T03:59:51.649Z
closed_at: 2026-08-09T03:59:51.648Z
close_reason: Completed dependency/tool inventory and source/release review, applied every eligible useful upgrade, recorded the tbd exception, and deferred uv 0.12 to rpp-1gar until its cool-off expires.
---
Inventory all pinned dependencies, GitHub Actions, external source commits, and tool versions. Verify release dates and changes, upgrade only versions outside the 14-day cool-off with concrete maintenance or security value, review diffs, and regenerate locked artifacts deterministically.
