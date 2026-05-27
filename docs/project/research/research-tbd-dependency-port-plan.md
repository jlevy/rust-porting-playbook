---
title: "Research: tbd Dependency-by-Dependency Rust Port Plan"
status: draft
date: 2026-03-04
source_repo: https://github.com/jlevy/tbd
source_commit: 70d71fe738763029f4b6a3cd6a14d3c7aa8a3061
---
# Research: tbd Dependency-by-Dependency Rust Port Plan

## Scope

This document defines a detailed Rust-port plan for all direct dependencies used by
`tbd`, including runtime dependencies and development/tooling dependencies.

Input package files:
- `attic/tbd/package.json` (workspace root)
- `attic/tbd/packages/tbd/package.json` (CLI package)

Inventory snapshot (direct dependency entries):
- `packages/tbd` `dependencies`: 12
- `packages/tbd` `devDependencies`: 10
- workspace root `devDependencies`: 10
- total: 32 entries (31 unique names; `tsx` appears in both package scopes)

Validation notes (as of 2026-03-04):
- Dependency inventory extracted directly from the input package manifests.
- Candidate Rust crate targets verified for existence with `cargo search`.

## Supply-Chain Note

The **Risk** column below rates *porting difficulty*, not supply-chain risk. Treat
dependency selection as a supply-chain decision in both directions: audit the **source**
npm tree before trusting it as the parity oracle (`npm audit` / `pnpm audit signatures`,
review lifecycle scripts), and vet each proposed **target** crate (`cargo deny` /
`cargo audit`, 14-day cool-off for brand-new versions, read any `build.rs`/proc-macro,
`cargo-vet` for teams). See `tbd guidelines supply-chain-hardening`, §4.6 of
`references/rust-cli-best-practices.md`, and the Supply Chain Hardening guidebook
(<https://github.com/jlevy/supply-chain-hardening>).

## Runtime Dependency Plan (`packages/tbd`)

| JS Dependency | Current Role in `tbd` | Rust Target | Port Plan | Validation Gate | Risk |
| --- | --- | --- | --- | --- | --- |
| `atomically` | Crash-safe file writes for config/state/docs | `tempfile` + atomic rename pattern (`std::fs::rename`) | Build shared `atomic_write(path, bytes)` utility; use everywhere writes occur; ensure parent-dir policy mirrors current behavior | kill-process mid-write leaves old or full new file, never partial | medium |
| `commander` | CLI tree, options, help, grouped commands | `clap` v4 derive/builder | Define top-level parser and subcommands; preserve global flags and `--no-*` semantics; preserve help group layout | `--help` golden parity and option parsing parity | high |
| `github-slugger` | GitHub-style heading slug uniqueness | `github-slugger` crate (`cargo search`) or local equivalent | Implement slug state object with duplicate suffix behavior matching GitHub | snapshot tests over repeated headings and unicode headings | low |
| `gray-matter` | frontmatter extraction from markdown docs | `gray_matter` crate or `pulldown-cmark-frontmatter` | Add parser adapter that preserves body/frontmatter split and invalid-frontmatter behavior | parser golden tests from existing fixtures | medium |
| `marked` | markdown rendering for docs output | `pulldown-cmark` or `comrak` | Build markdown-to-terminal pipeline preserving headings/lists/code blocks | rendered help/docs golden tests | medium |
| `marked-terminal` | ANSI terminal formatting of markdown | `termimad` or custom renderer on `anstyle` | Start with custom minimal renderer for used markdown subset; evaluate `termimad` for coverage | CLI doc output parity tests in TTY/non-TTY modes | medium |
| `picocolors` | semantic color styling with env precedence | `anstream` + `anstyle` (or `owo-colors`) | Implement color policy helper for `--color`, `NO_COLOR`, `FORCE_COLOR`, TTY precedence | color mode test matrix (`always/never/auto`, env overrides) | high |
| `pretty-bytes` | human-readable byte counts | `bytesize` or `indicatif::HumanBytes` | central formatter wrapper for byte display consistency | output formatting tests for KB/MB/GB boundaries | low |
| `pretty-ms` | human-readable durations | `humantime` or custom formatter | central formatter wrapper for elapsed durations | output formatting tests for sec/min/hour boundaries | low |
| `ulid` | stable issue IDs | `ulid` crate | preserve generation and parsing format; ensure lexical ordering requirements | roundtrip and ordering tests | low |
| `yaml` | parse/stringify config and docs metadata | `serde_yaml_ng` (preferred) or `serde_norway` | create YAML utility module with deterministic key ordering and merge-conflict marker detection; avoid archived `serde_yaml` and advisory-flagged `serde_yml` (RUSTSEC-2025-0068) | config parser fixtures + deterministic write snapshots | high |
| `zod` | runtime schema validation + strong typing | `serde` + typed structs + custom validation (`validator` as needed) | convert schemas to Rust domain types; add explicit validation errors with context | schema-equivalence tests for valid/invalid samples | high |

## Test and Build Dependency Plan (`packages/tbd` devDependencies)

| JS Dependency | Current Role | Rust Target | Port Plan | Validation Gate |
| --- | --- | --- | --- | --- |
| `vitest` | unit/integration test runner | `cargo test` + `rstest` (optional) | migrate each test module to Rust test modules with fixture helpers | full test suite green |
| `tryscript` | markdown-driven CLI golden tests | `trycmd` (or `snapbox` + custom harness) | port `.tryscript.md` scenarios to `trycmd` cases; preserve wildcard/pattern semantics | golden diffs match expected behavior |
| `@vitest/coverage-v8` | Vitest V8 coverage provider | `cargo-llvm-cov` | remove JS coverage provider and wire Rust coverage collection in CI | coverage job green with Rust profiles |
| `c8` | JS coverage CLI and report generation | `cargo-llvm-cov` | replace coverage command chain with cargo-native workflow | coverage report generated in CI |
| `monocart-coverage-reports` | custom coverage report formatting | `cargo-llvm-cov` output formats + post-processing if needed | preserve required report artifacts consumed by CI/release checks | required CI coverage artifacts preserved |
| `tsdown` | package build/transpile | `cargo build --release` | remove JS build stage; replace with Cargo profile/build scripts as needed | release build artifact parity |
| `tsx` | local TS execution | `cargo run` | replace script entry points with cargo aliases/scripts | developer workflow docs updated |
| `publint` | npm package quality lint | `cargo package --allow-dirty` + audit checks | replace with crates.io package validation checks | package validation job green |
| `@types/node` | Node.js typing metadata for TS compile | N/A | removed during Rust migration | N/A |
| `@types/marked-terminal` | `marked-terminal` typing metadata | N/A | removed during Rust migration | N/A |

## Workspace Tooling Dependency Plan (`attic/tbd/package.json` devDependencies)

| JS Dependency | Current Role | Rust Workflow Equivalent | Port Plan |
| --- | --- | --- | --- |
| `typescript` | TS compilation/typechecking entrypoint | Rust compiler + strict lints | replace TS typecheck with `cargo check` and targeted compile-time guarantees |
| `typescript-eslint` | TS-aware lint rules | `clippy` | port safety/style checks to clippy rules and deny-lints |
| `eslint` | JS/TS lint runner | `clippy` | remove ESLint stages and enforce clippy in local+CI flows |
| `@eslint/js` | base ESLint rule presets | `clippy` + `rustfmt` conventions | map essential style/safety policies into Rust lint config |
| `eslint-config-prettier` | lint/format conflict mediation | `rustfmt` (single formatter) | remove JS formatter coordination and rely on rustfmt canonical style |
| `prettier` | source/doc formatting | `rustfmt` + markdown formatter policy | move code formatting to rustfmt; keep markdown formatting via existing doc tooling if still needed |
| `lefthook` | git hook orchestration | keep `lefthook` or switch to lightweight shell hooks | keep initially for continuity, then evaluate simplification |
| `@changesets/cli` | versioning/changelog release workflow | `release-plz` or `cargo-release` | choose one and codify release automation |
| `npm-check-updates` | dependency update checks | `cargo update` + `cargo-audit` + Dependabot | establish update cadence and security checks |
| `tsx` | script execution | `cargo run --bin <tool>` | remove as Rust utilities replace TS scripts |

## Migration Order (tbd)

1. Establish CLI skeleton and global option behavior (`clap`, color policy, help output).
2. Port core data model and validation (`serde` + validation layer).
3. Port YAML/markdown pipeline and deterministic serialization.
4. Port git/worktree/sync flows with atomic write and lock semantics.
5. Port tests (unit first, then golden CLI scenarios).
6. Replace release/tooling pipeline.

## Critical Spikes Required

1. Markdown rendering parity spike (`marked` + `marked-terminal` -> Rust terminal output).
2. Frontmatter parser behavior parity spike (`gray-matter` edge cases).
3. Golden test migration spike (`tryscript` -> `trycmd`).
4. Sync safety spike: atomic writes + lock fallback semantics.

## Completion Criteria

- Every runtime dependency above has an implemented Rust target or an approved in-house
  replacement.
- Every direct dependency entry from source manifests is represented in exactly one table
  row for its scope (runtime/dev/workspace).
- No `packages/tbd` direct JS runtime dependencies remain.
- Golden CLI behavior suite passes with Rust binary.
- Release pipeline is fully Rust-native (build/test/release).

## Lockfile-Level Transitive Coverage

Transitive lockfile coverage is maintained in:
- `docs/project/research/research-tbd-transitive-lockfile-appendix.md`
- `docs/project/research/data/tbd-lockfile-package-inventory.tsv`
- `docs/project/research/data/tbd-lockfile-summary.json`
- `docs/project/research/data/tbd-lockfile-top-owners.json`

Snapshot from `attic/tbd/pnpm-lock.yaml` (2026-03-04):
- lock entries: 454
- transitive entries: 420
- transitive unique package names: 388
- unmapped/unreachable lock entries: 0
