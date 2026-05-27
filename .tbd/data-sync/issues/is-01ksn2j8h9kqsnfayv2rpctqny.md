---
type: is
id: is-01ksn2j8h9kqsnfayv2rpctqny
title: Refresh and reconcile Rust crate version pins in prescriptive docs
kind: task
status: open
priority: 1
version: 1
labels:
  - currency
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:01.161Z
updated_at: 2026-05-27T15:59:01.161Z
---
Prescriptive docs pin crate minimum versions that have drifted and disagree across files. Current (2026-05-27): regex 1.12.3, clap 4.6.1, indicatif 0.18.4, thiserror 2.x.

Fix:
- regex: bump '1.10' to '1.12' in references/rust-cli-best-practices.md:125 and guidelines/rust-project-setup.md:60; mapping reference already says '1.12+'. Make consistent.
- clap/clap_complete: examples pin '4.5' (rust-cli-best-practices.md:68,128,162,579; rust-project-setup.md:63; port-checklist-initial-template.md:257) and clap_complete '4' (guidelines/python-to-rust-cli-porting.md:255). Decide floor policy and bump to '4.6' for currency + consistency.
- tempfile: mapping reference disagrees with itself — 3.26 (line 360) vs 3.10 (line 1057) vs '3.x' (line 293). Unify (current 3.x line is fine; pick one).
- fs-err: '3.x' (line 244) vs '3.1' (line 365). Unify.
- thiserror notation: '2.0' vs '2' across rust-project-setup.md:61 and port-checklist-initial-template.md:259. Standardize.
Acceptance: grep shows one consistent pin per crate, each at or above latest minor as of May 2026.
