---
title: "Research: qmd Dependency-by-Dependency Rust Port Plan"
status: draft
date: 2026-03-04
source_repo: https://github.com/tobi/qmd
source_commit: 40610c3aa65d9d399ebb188a7e4930f6628ae51c
---
# Research: qmd Dependency-by-Dependency Rust Port Plan

## Scope

This document defines a detailed Rust-port plan for all direct dependencies used by
`qmd`, including runtime, optional, peer, and development dependencies.

Input package file:
- `attic/qmd/package.json`

Inventory snapshot (direct dependency entries):
- `dependencies`: 8
- `optionalDependencies`: 4
- `peerDependencies`: 1
- `devDependencies`: 3
- total: 16 entries (16 unique names)

Validation notes (as of 2026-03-04):
- Dependency inventory extracted directly from the input package manifest.
- Candidate Rust crate targets verified for existence with `cargo search`.

## Runtime Dependency Plan (`dependencies`)

| JS Dependency | Current Role in `qmd` | Rust Target | Port Plan | Validation Gate | Risk |
| --- | --- | --- | --- | --- | --- |
| `@modelcontextprotocol/sdk` | MCP server (stdio + streamable HTTP), tools/resources contracts | `rmcp` (Rust MCP SDK) | Build MCP layer using `rmcp`; preserve tool/resource surface and instructions behavior; mirror stdio and HTTP transport options | MCP integration tests with same tool/resource contracts | high |
| `better-sqlite3` | primary SQLite runtime API on Node | `rusqlite` | Port DB abstraction to `rusqlite`; preserve prepared statements, transaction semantics, and schema behavior | DB unit tests + migration/integrity tests | high |
| `sqlite-vec` | vector extension loading/search in SQLite | `sqlite-vec` crate + `rusqlite` extension loading | implement extension probe/load path; preserve graceful degradation when vec unavailable | vector/no-vector test matrix, fallback behavior parity | high |
| `fast-glob` | file discovery for indexing and retrieval | `globset`/`wax` + `walkdir`/`ignore` | implement deterministic file walker matching current glob behavior and exclude patterns | corpus discovery parity tests |
| `picomatch` | pattern matching for filters/rules | `globset` or `regex` (case-specific) | identify each picomatch use and replace with explicit matcher wrappers | matcher unit tests from current fixtures | medium |
| `node-llama-cpp` | local embedding/generation/reranking and session management | Rust llama.cpp binding (`llama_cpp`, `llama-cpp-2`) or external llama.cpp server client | run spike to choose binding vs subprocess service; preserve embedding/rerank/query-expansion APIs and timeout/abort behavior | LLM smoke tests + latency/quality benchmarks | very high |
| `yaml` | collection config and serialization | `serde_yml` (preferred) or `yaml_serde` | typed config structs + deterministic emit rules where needed; avoid deprecated `serde_yaml` | config roundtrip and invalid-config tests | medium |
| `zod` | runtime input/schema validation | `serde` + custom validators (`validator` if needed) | replace zod schemas with explicit typed request/response/input validation | invalid input/error message tests | high |

## Optional Dependency Plan (`optionalDependencies`)

| JS Dependency | Current Role | Rust Target | Port Plan | Validation Gate |
| --- | --- | --- | --- | --- |
| `sqlite-vec-darwin-arm64` | platform-specific vec binary | Rust build/release artifacts per target | package extension with release bundles or documented runtime prerequisite | install/run checks on macOS arm64 |
| `sqlite-vec-darwin-x64` | platform-specific vec binary | same as above | same as above | install/run checks on macOS x64 |
| `sqlite-vec-linux-x64` | platform-specific vec binary | same as above | same as above | install/run checks on linux x64 |
| `sqlite-vec-win32-x64` | platform-specific vec binary | same as above | same as above | install/run checks on windows x64 |

## Peer and Dev Dependency Plan

| JS Dependency | Current Role | Rust Workflow Equivalent | Port Plan |
| --- | --- | --- | --- |
| `typescript` | peer dependency for TS ecosystem compatibility signal | N/A in Rust binary | remove peer dependency in Rust package context |
| `vitest` | test runner | `cargo test` + targeted integration tests | port test suite and fixtures |
| `tsx` | local script execution | `cargo run` | replace script workflow in docs |
| `@types/better-sqlite3` | TS typing support | N/A | eliminated by Rust types |

## qmd-Specific Dependency Risk Areas

1. **LLM runtime parity (`node-llama-cpp`)**:
   embedding behavior, batching, rerank semantics, model lifecycle, timeout/cancellation.
2. **SQLite extension portability (`sqlite-vec`)**:
   dynamic loading constraints differ by OS/build.
3. **Dual transport MCP support**:
   stdio and HTTP transport behavior must remain compatible.
4. **Node/Bun compatibility layer in current code**:
   Rust target should collapse runtime branching while preserving behavior.

## Migration Order (qmd)

1. Port storage/indexing core (`rusqlite`, schema, search basics).
2. Port glob/pattern discovery and indexing pipeline.
3. Port CLI parsing/output behavior and command routing.
4. Port MCP server layer and tool/resource contracts.
5. Port LLM subsystem and verify embedding/rerank/query-expansion parity.
6. Port tests and release pipeline.

## Required Spikes

1. LLM backend decision spike: direct Rust llama binding vs external inference process.
2. sqlite-vec packaging spike across macOS/Linux/Windows targets.
3. MCP transport parity spike (stdio + streamable HTTP).
4. Pattern/glob parity spike against current corpus fixtures.

## Completion Criteria

- Every dependency listed above has an implemented Rust replacement strategy.
- Every direct dependency entry from `attic/qmd/package.json` is represented in exactly
  one table row for its scope (runtime/optional/peer/dev).
- LLM, sqlite-vec, and MCP high-risk paths have passing integration tests.
- Cross-platform install and runtime story is documented and validated.
- No remaining JS runtime dependencies are required for the Rust CLI binary.

## Lockfile-Level Transitive Coverage

Transitive lockfile coverage is maintained in:
- `docs/project/research/research-qmd-transitive-lockfile-appendix.md`
- `docs/project/research/data/qmd-lockfile-package-inventory.tsv`
- `docs/project/research/data/qmd-lockfile-summary.json`
- `docs/project/research/data/qmd-lockfile-top-owners.json`

Snapshot from `attic/qmd/bun.lock` (2026-03-04):
- lock entries: 447
- transitive entries: 431
- transitive unique package names: 388
- unmapped/unreachable lock entries: 0
- direct-name alias note: `sqlite-vec-win32-x64` (manifest) resolves to
  `sqlite-vec-windows-x64` (lock key)
