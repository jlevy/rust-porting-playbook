---
type: is
id: is-01ksn2j92bywfz6aarqp7nqtqb
title: Refresh maturin and PyPI distribution tooling versions in research docs
kind: task
status: open
priority: 2
version: 1
labels:
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:01.707Z
updated_at: 2026-05-27T15:59:01.707Z
---
Research docs cite maturin v1.11.5 and PyO3/maturin-action@v1.50.0 as surveyed/recommended pins; current maturin is 1.13.3 (May 2026). The maturin>=1.9,<2.0 build-system bound is still fine.

Fix in docs/project/research/research-rust-cli-binary-distribution.md and research-rust-cli-pypi-distribution.md:
- Update maturin version references and maturin-action pin to current.
- Review aging runner/target claims: macos-13 for x86_64 (pypi-dist ~561), macosx_10_12 minimum target (~237) — confirm current maturin defaults.
- Re-verify 'rooster' is still used by ruff/uv for version bumping (~177).
