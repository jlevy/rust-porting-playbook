---
title: "Research Appendix: tbd Lockfile Transitive Dependency Plan"
status: draft
date: 2026-05-27
source_repo: https://github.com/jlevy/tbd
source_commit: 395052437464a9e62ce209220dcc01096fa06f7e
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

This is automated and reproducible via
`docs/project/research/data/extract_lockfile_inventory.py`:

```sh
git clone https://github.com/jlevy/tbd.git attic/tbd
git -C attic/tbd checkout 395052437464a9e62ce209220dcc01096fa06f7e
uv --no-config run --locked \
  --script docs/project/research/data/extract_lockfile_inventory.py \
  attic/tbd/pnpm-lock.yaml tbd docs/project/research/data/tbd-lockfile
git diff --exit-code -- docs/project/research/data/tbd-lockfile-*
```

The adjacent `extract_lockfile_inventory.py.lock` pins the script’s PyYAML dependency.
The source commit pins the analyzed `pnpm-lock.yaml`; `attic/` is intentionally ignored
so third-party checkouts do not become part of this repository.

## Inventory Snapshot (as of 2026-05-27)

| Metric | Value |
| --- | --- |
| Lock entries (`snapshots`) | 397 |
| Unique package names in lock | 367 |
| Direct manifest entries | 31 |
| Direct manifest unique names | 30 |
| Transitive lock entries | 366 |
| Transitive unique names | 337 |
| Unreachable lock entries | 0 |

## Action Classification

| Action | Meaning | Count |
| --- | --- | --- |
| `covered-in-direct-plan` | Direct dependency; handled in D12 direct table | 31 |
| `replace-through-runtime-owner` | Transitive package owned only by runtime roots; replaced as part of runtime port | 34 |
| `removed-with-js-toolchain` | Transitive package owned only by TS/JS tooling roots; removed with tooling cutover | 311 |
| `split-runtime-and-tooling` | Shared by runtime and tooling roots; preserve runtime path while deleting tooling path | 21 |

> Note: `covered-in-direct-plan` (31) exceeds the 30 unique direct manifest names because
> a direct dependency appears at more than one version in the lockfile snapshots; each
> lock entry is counted separately here.

## Highest-Pressure Owner Roots (Transitive)

| Owner Root | Transitive Entries Owned |
| --- | --- |
| `@vitest/coverage-v8` | 116 |
| `typescript-eslint` | 108 |
| `tryscript` | 103 |
| `vitest` | 97 |
| `eslint-config-prettier` | 87 |
| `eslint` | 86 |
| `c8` | 75 |
| `tsdown` | 67 |
| `tsx` | 62 |
| `marked-terminal` | 44 |

Interpretation:
- Most transitive mass is tooling-owned (`removed-with-js-toolchain` is 311 of 397
  entries, ~78%) and should disappear as the Rust-native test/lint/release stack replaces
  the TS/JS stack.
- `@changesets/cli` (previously the third-largest owner at ~98 entries) was dropped
  upstream in favor of a simpler release flow, removing a large block of tooling-only
  transitive mass.
- Runtime-owned transitive entries are concentrated under markdown/output
  (`marked-terminal`, `gray-matter`) and schema/config paths and must be validated
  through runtime parity tests.

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
