---
type: is
id: is-01kxepdeap9z0n5y09b10td6ma
title: Decide immutable pinning policy for published workflow examples
kind: task
status: open
priority: 2
version: 1
labels:
  - review-2026-07-13
dependencies: []
created_at: 2026-07-13T21:34:01.045Z
updated_at: 2026-07-13T21:34:01.045Z
---
Senior review SER-002. The repository's own CI is pinned to full action SHAs, but educational copy-paste snippets use floating major tags for readability. Decide whether every published workflow example must use immutable SHAs and how those dozens of pins will be maintained, or explicitly document the examples as templates that consumers must pin.
