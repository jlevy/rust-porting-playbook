---
type: is
id: is-01ksn2j8s3er00ktz5rhtp6s9s
title: Update cargo-dist -> dist rename and version across docs
kind: task
status: closed
priority: 1
version: 2
labels:
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:01.411Z
updated_at: 2026-05-27T16:14:10.357Z
closed_at: 2026-05-27T16:14:10.356Z
close_reason: Updated 'latest stable' 0.30.4->0.31.0 (Feb 23 2026) in binary-distribution research, added release-history row and bumped pin example; clarified dist rename and v0.31+ in rust-project-setup and rust-cli-best-practices; dated the aarch64-pc-windows-msvc caveat. axodotdev/dist confirmed actively maintained (no shutdown).
---
cargo-dist was renamed to 'dist' and the latest stable is 0.31.0 (2026-02-23). Docs cite 'latest stable v0.30.4 (Feb 2026)' and 'v0.30+'.

Fix:
- docs/project/research/research-rust-cli-binary-distribution.md: update 'latest stable 0.30.4' (lines ~843,921,1243), refresh release-history table, note the dist rename, and re-verify time-sensitive claims: aarch64-pc-windows-msvc support (lines ~905,974,1089), cross-compilation issue #74 status (lines ~893,1247), GitLab support issue #1781.
- guidelines/rust-project-setup.md:449 ('v0.30+') and references/rust-cli-best-practices.md:688-689: clarify the dist rename and refresh version threshold.
Note: axodotdev/dist appears actively maintained (no shutdown found); confirm before writing.
