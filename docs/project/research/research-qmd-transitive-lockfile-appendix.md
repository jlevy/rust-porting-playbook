---
title: "Research Appendix: qmd Lockfile Transitive Dependency Plan"
status: draft
date: 2026-03-04
source_repo: https://github.com/tobi/qmd
source_commit: 40610c3aa65d9d399ebb188a7e4930f6628ae51c
source_lockfile: attic/qmd/bun.lock
---
# Research Appendix: qmd Lockfile Transitive Dependency Plan

## Scope

This appendix covers lockfile-level dependency planning for `qmd` beyond direct
manifest dependencies, using `attic/qmd/bun.lock`.

## Extraction Method

1. Read direct root dependencies from lockfile workspace `""`:
   - `dependencies`, `optionalDependencies`, `devDependencies`, `peerDependencies`
2. Traverse bun package graph through `dependencies`, `optionalDependencies`, and
   `peerDependencies` fields for each lock entry.
3. Normalize Bun alias forms to propagate ownership:
   - same `name@version` aliases
   - slash-key parent inheritance (for example `cliui/string-width/...`)
   - reverse dependency inheritance for entries with sparse metadata
4. Record one row per lock entry with owner roots and action classification.

## Inventory Snapshot (as of 2026-03-04)

| Metric | Value |
| --- | --- |
| Lock entries (`packages`) | 447 |
| Unique package names in lock | 403 |
| Direct manifest entries | 16 |
| Direct manifest unique names | 16 |
| Transitive lock entries | 431 |
| Transitive unique names | 388 |
| Unreachable lock entries | 0 |

## Action Classification

| Action | Meaning | Count |
| --- | --- | --- |
| `covered-in-direct-plan` | Direct dependency; handled in D13 direct table | 16 |
| `replace-through-runtime-owner` | Transitive package owned only by runtime/optional roots; replaced as part of runtime port | 328 |
| `removed-with-js-toolchain` | Transitive package owned only by dev/peer roots; removed with tooling cutover | 100 |
| `split-runtime-and-tooling` | Shared by runtime and dev roots; preserve runtime path while deleting tooling path | 3 |

## Highest-Pressure Owner Roots (Transitive)

| Owner Root | Transitive Entries Owned |
| --- | --- |
| `node-llama-cpp` | 226 |
| `vitest` | 103 |
| `@modelcontextprotocol/sdk` | 90 |
| `better-sqlite3` | 37 |
| `tsx` | 30 |
| `fast-glob` | 16 |

Interpretation:
- The transitive graph is dominated by LLM runtime (`node-llama-cpp`) and MCP
  server stack, so those spikes remain the highest leverage for risk reduction.
- Tooling-only transitive entries are smaller than runtime-owned entries in qmd,
  so runtime parity testing is the critical path.

## Lockfile Alias Note

Direct optional dependency alias mismatch observed:
- Manifest name: `sqlite-vec-win32-x64`
- Lock key: `sqlite-vec-windows-x64`

This is explicitly normalized in inventory extraction and should be preserved in
porting documentation to avoid false missing-dependency checks.

## Rust Porting Use Rules

1. For every row marked `replace-through-runtime-owner`, ensure the owner direct
   dependency has a concrete Rust mapping and integration test in D13.
2. For every row marked `removed-with-js-toolchain`, remove the owning TS/Node
   workflow and verify no runtime command path still references it.
3. For every row marked `split-runtime-and-tooling`, add targeted tests to guard
   runtime behavior while pruning tooling dependencies.

## Full Lockfile Artifacts

- `docs/project/research/data/qmd-lockfile-package-inventory.tsv`
- `docs/project/research/data/qmd-lockfile-summary.json`
- `docs/project/research/data/qmd-lockfile-top-owners.json`
