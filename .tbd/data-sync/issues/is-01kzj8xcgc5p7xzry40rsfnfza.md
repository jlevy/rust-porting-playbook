---
type: is
id: is-01kzj8xcgc5p7xzry40rsfnfza
title: Validate CI on current stable Python 3.14
kind: task
status: closed
priority: 2
version: 2
labels:
  - dependencies
  - ci
dependencies: []
parent_id: is-01kzj7wkb4gjdszdand45x12ff
created_at: 2026-08-09T03:26:24.780Z
updated_at: 2026-08-09T03:59:50.822Z
closed_at: 2026-08-09T03:59:50.822Z
close_reason: Applied all eligible reviewed pins, recorded the owner-approved exact tbd exception, hardened checksum-verified gh extraction, and passed the full suite on Python 3.14.6; uv 0.12 remains separately deferred as rpp-1gar.
---
Advance the docs-quality workflow from Python 3.13 to the current stable 3.14 line, which is well outside the cool-off, and run the full suite locally under Python 3.14 before delivery.
