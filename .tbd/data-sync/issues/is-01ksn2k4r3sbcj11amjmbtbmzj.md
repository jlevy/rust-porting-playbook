---
type: is
id: is-01ksn2k4r3sbcj11amjmbtbmzj
title: Refresh stale Last-update date markers and set a dating policy
kind: chore
status: closed
priority: 3
version: 2
labels:
  - hygiene
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:30.051Z
updated_at: 2026-05-27T16:20:28.074Z
closed_at: 2026-05-27T16:20:28.074Z
close_reason: "Updated the three 'Last update' markers (porting-guide 2025-11-02, test-coverage-playbook + mapping-reference 2026-02-12) to 2026-05-27; all three were substantively edited this pass. Adopted convention: keep stamps only where they already exist and bump on substantive review (avoids stamp-rot from adding markers to all 19 docs)."
---
Explicit staleness markers are out of date: playbooks/python-to-rust-porting-guide.md:13 'Last update: 2025-11-02' and playbooks/python-to-rust-test-coverage-playbook.md:12 'Last update: 2026-02-12'. Decide on a consistent date-stamp/review-cadence convention (some docs have none) and refresh after this review pass.
