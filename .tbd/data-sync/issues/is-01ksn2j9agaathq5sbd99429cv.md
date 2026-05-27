---
type: is
id: is-01ksn2j9agaathq5sbd99429cv
title: Update GitHub Actions versions and fix cross-file inconsistencies
kind: task
status: closed
priority: 2
version: 2
labels:
  - currency
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:01.968Z
updated_at: 2026-05-27T16:15:46.590Z
closed_at: 2026-05-27T16:15:46.589Z
close_reason: Bumped setup-python@v5->v6 and setup-uv@v4->v7 in mapping-reference and test-coverage-playbook; all prescriptive CI examples now consistent (checkout@v6, rust-cache@v2, setup-uv@v7). upload/download-artifact@v4 is the current major so unchanged. Case-study/migration-plan CI YAML left as historical record.
---
Action pins drifted and disagree across files. Current: actions/checkout v6, actions/setup-python v6, astral-sh/setup-uv v7.5, upload/download-artifact v6/v7.

Fix:
- setup-uv: '@v4' -> '@v7' in references/python-to-rust-mapping-reference.md:956 and playbooks/python-to-rust-test-coverage-playbook.md:524 (other docs already @v7).
- setup-python: '@v5' (mapping-reference:955) and '@v4' (migration-plan:553, research docs) -> '@v6'.
- checkout: '@v5' in mapping-reference:955 -> '@v6'.
- upload-artifact/download-artifact: reconcile '@v4' (pypi-dist, migration-plan) vs '@v6'/'@v7' noted for ruff.
Keep the existing SHA-pinning recommendation. Case-study CI YAML may stay historical but note where it diverges.
