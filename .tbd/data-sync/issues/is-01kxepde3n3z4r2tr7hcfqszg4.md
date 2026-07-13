---
type: is
id: is-01kxepde3n3z4r2tr7hcfqszg4
title: Choose and enforce a main-branch ruleset
kind: task
status: open
priority: 1
version: 1
labels:
  - review-2026-07-13
dependencies: []
created_at: 2026-07-13T21:34:00.820Z
updated_at: 2026-07-13T21:34:00.820Z
---
Senior review SER-001. main currently has no branch protection or repository ruleset. Decide the solo-maintainer workflow: require the Docs quality / Validate repository check, whether to require a pull request and approvals, and which actors may bypass. Apply the selected ruleset after this review workflow is merged so the required check exists on main.
