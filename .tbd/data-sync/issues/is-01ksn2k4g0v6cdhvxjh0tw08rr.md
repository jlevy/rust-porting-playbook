---
type: is
id: is-01ksn2k4g0v6cdhvxjh0tw08rr
title: Reconcile performance-claim ranges across docs
kind: task
status: open
priority: 3
version: 1
labels:
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:29.792Z
updated_at: 2026-05-27T15:59:29.792Z
---
Speedup claims are inconsistent: 5-50x (guidelines/python-to-rust-cli-porting.md:487), 50-100x (playbooks/python-to-rust-porting-guide.md:560), 10-100x (port-checklist-initial-template.md:510), 10x with '50-100x typical' (port-checklist-initial-template.md:711), while the measured flowmark result is 20-40x (case-studies/flowmark/flowmark-port-metrics.md:29). Choose consistent, defensible guidance anchored to measured data and update all sites.
