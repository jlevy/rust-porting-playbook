---
type: is
id: is-01ksn2k502a1ndasf4jqxw9etc
title: Refresh Rust toolchain currency notes (latest stable 1.95; verify since-version claims)
kind: task
status: open
priority: 3
version: 1
labels:
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:30.306Z
updated_at: 2026-05-27T15:59:30.306Z
---
MSRV 1.85 / Edition 2024 floor is correct and should stay. But 'latest stable' context and several 'stable since Rust X' notes should be verified against current stable 1.95.0.

Action:
- Where docs reference 'latest stable', mention 1.95 era (e.g. guidelines/python-to-rust-porting-guide.md:22).
- Spot-check 'stable since' claims in references/python-to-rust-mapping-reference.md (fs::exists 1.81, std::path::absolute 1.79, File::create_new 1.77, file.lock 1.89, set_times 1.75) — these look right; confirm.
- Verify aarch64-pc-windows-msvc 'Tier 1 since 1.91' claim in research-rust-cli-binary-distribution.md.
