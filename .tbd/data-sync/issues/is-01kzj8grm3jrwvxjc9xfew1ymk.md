---
type: is
id: is-01kzj8grm3jrwvxjc9xfew1ymk
title: Upgrade pinned GitHub CLI bootstrap to 2.96.0
kind: task
status: closed
priority: 1
version: 3
labels:
  - dependencies
  - security
dependencies: []
parent_id: is-01kzj7wkb4gjdszdand45x12ff
created_at: 2026-08-09T03:19:31.202Z
updated_at: 2026-08-09T03:59:50.798Z
closed_at: 2026-08-09T03:59:50.797Z
close_reason: Applied all eligible reviewed pins, recorded the owner-approved exact tbd exception, hardened checksum-verified gh extraction, and passed the full suite on Python 3.14.6; uv 0.12 remains separately deferred as rpp-1gar.
---
Upgrade the checksum-verified GitHub CLI fallback from 2.92.0 to eligible 2.96.0, which fixes GHSA-8cg3-r6g9-fpg2. Keep both bootstrap scripts identical, verify every supported asset checksum, and extract only inside a fresh private temporary directory.
