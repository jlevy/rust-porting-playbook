---
type: is
id: is-01kxepdehgjtw0dq457acdjxa6
title: Approve and apply a Flowmark repository-wide formatting baseline
kind: task
status: open
priority: 3
version: 1
labels:
  - review-2026-07-13
dependencies: []
created_at: 2026-07-13T21:34:01.263Z
updated_at: 2026-07-13T21:34:01.263Z
---
Senior review SER-003. flowmark 0.3.1 --auto --check reports 39 of 54 tracked Markdown files would change. Apply the baseline in a dedicated mechanical PR (not mixed with substantive review fixes), review smart-quote and layout changes, then add an enforceable formatter check with a pinned installation.
