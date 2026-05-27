---
title: "Research Appendix: tbd Lockfile Transitive Dependency Plan"
status: draft
date: 2026-03-04
source_repo: https://github.com/jlevy/tbd
source_commit: 70d71fe738763029f4b6a3cd6a14d3c7aa8a3061
source_lockfile: attic/tbd/pnpm-lock.yaml
---
# Research Appendix: tbd Lockfile Transitive Dependency Plan

## Scope

This appendix covers lockfile-level dependency planning for `tbd` beyond direct
manifest dependencies, using `attic/tbd/pnpm-lock.yaml`.

## Extraction Method

1. Read direct root dependencies from lockfile importers:
   - `.` `devDependencies`
   - `packages/tbd` `dependencies` and `devDependencies`
2. Traverse lock snapshot graph (`snapshots`) via `dependencies` and
   `optionalDependencies`.
3. Resolve alias-style lock edges where version strings are direct snapshot keys
   (for example `string-width-cjs -> string-width@4.2.3`).
4. Record one row per lock entry with owner roots and action classification.

## Inventory Snapshot (as of 2026-03-04)

| Metric | Value |
| --- | --- |
| Lock entries (`snapshots`) | 454 |
| Unique package names in lock | 419 |
| Direct manifest entries | 32 |
| Direct manifest unique names | 31 |
| Transitive lock entries | 420 |
| Transitive unique names | 388 |
| Unreachable lock entries | 0 |

## Action Classification

| Action | Meaning | Count |
| --- | --- | --- |
| `covered-in-direct-plan` | Direct dependency; handled in D12 direct table | 34 |
| `replace-through-runtime-owner` | Transitive package owned only by runtime roots; replaced as part of runtime port | 30 |
| `removed-with-js-toolchain` | Transitive package owned only by TS/JS tooling roots; removed with tooling cutover | 365 |
| `split-runtime-and-tooling` | Shared by runtime and tooling roots; preserve runtime path while deleting tooling path | 25 |

> Note: `covered-in-direct-plan` (34) exceeds the 32 direct manifest entries / 31 unique
> names because a few direct dependencies appear at more than one version in the lockfile
> snapshots; each lock entry is counted separately here.

## Highest-Pressure Owner Roots (Transitive)

| Owner Root | Transitive Entries Owned |
| --- | --- |
| `@vitest/coverage-v8` | 110 |
| `typescript-eslint` | 102 |
| `@changesets/cli` | 98 |
| `tryscript` | 95 |
| `vitest` | 92 |
| `eslint` | 84 |
| `eslint-config-prettier` | 84 |
| `c8` | 72 |
| `tsdown` | 63 |
| `marked-terminal` | 42 |

Interpretation:
- Most transitive mass is tooling-owned and should disappear as Rust-native
  test/lint/release stack replaces TS/JS stack.
- Runtime-owned transitive entries are concentrated under markdown/output and
  schema/config paths and must be validated through runtime parity tests.

## Rust Porting Use Rules

1. For every row marked `replace-through-runtime-owner`, ensure the owner direct
   dependency has an explicit Rust crate/pattern mapping in D12.
2. For every row marked `removed-with-js-toolchain`, verify removal in CI by
   deleting corresponding Node-based build/test/lint/release stages.
3. For every row marked `split-runtime-and-tooling`, add a targeted test proving
   runtime behavior remains after tooling removal.

## Full Lockfile Artifacts

- `docs/project/research/data/tbd-lockfile-package-inventory.tsv`
- `docs/project/research/data/tbd-lockfile-summary.json`
- `docs/project/research/data/tbd-lockfile-top-owners.json`
