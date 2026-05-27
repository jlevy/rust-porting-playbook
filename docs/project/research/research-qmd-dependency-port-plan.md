---
title: "Research: qmd Dependency-by-Dependency Rust Port Plan"
status: draft
date: 2026-05-27
source_repo: https://github.com/tobi/qmd
source_commit: 443760f4d5a17550d77a0e3146b5b8f08452991f
---
# Research: qmd Dependency-by-Dependency Rust Port Plan

## Scope

This document defines a detailed Rust-port plan for all direct dependencies used by
`qmd`, including runtime, optional, peer, and development dependencies.

Input package file:
- `attic/qmd/package.json` (qmd v2.5.2)

Inventory snapshot (direct dependency entries):
- `dependencies`: 13
- `optionalDependencies`: 5
- `peerDependencies`: 1
- `devDependencies`: 3
- total: 22 entries (22 unique names)

Since the original 2026-03-04 snapshot (v2.x, 16 entries), qmd added a Tree-sitter
parsing stack (`tree-sitter-go/python/rust/typescript`, `web-tree-sitter`),
`better-sqlite3`, and `zod`, and a fifth `sqlite-vec` platform package.

Validation notes (as of 2026-05-27):
- Dependency inventory extracted directly from the input package manifest.
- Candidate Rust crate targets verified for existence with `cargo search`.

## Supply-Chain Note

The **Risk** column below rates *porting difficulty*, not supply-chain risk. Treat
dependency selection as a supply-chain decision in both directions: audit the **source**
npm tree before trusting it as the parity oracle (`npm audit` / `pnpm audit signatures`,
review lifecycle scripts), and vet each proposed **target** crate (`cargo deny` /
`cargo audit`, 14-day cool-off for brand-new versions, read any `build.rs`/proc-macro,
`cargo-vet` for teams). This matters most for the native/LLM stack (`node-llama-cpp` →
`llama_cpp`/`llama-cpp-2`, `sqlite-vec`), where C/C++ build systems widen the attack
surface. See `tbd guidelines supply-chain-hardening`, §4.6 of
`references/rust-cli-best-practices.md`, and the Supply Chain Hardening guidebook
(<https://github.com/jlevy/supply-chain-hardening>).

## Runtime Dependency Plan (`dependencies`)

| JS Dependency | Current Role in `qmd` | Rust Target | Port Plan | Validation Gate | Risk |
| --- | --- | --- | --- | --- | --- |
| `@modelcontextprotocol/sdk` | MCP server (stdio + streamable HTTP), tools/resources contracts | `rmcp` (Rust MCP SDK) | Build MCP layer using `rmcp`; preserve tool/resource surface and instructions behavior; mirror stdio and HTTP transport options | MCP integration tests with same tool/resource contracts | high |
| `better-sqlite3` | primary SQLite runtime API on Node | `rusqlite` | Port DB abstraction to `rusqlite`; preserve prepared statements, transaction semantics, and schema behavior | DB unit tests + migration/integrity tests | high |
| `sqlite-vec` | vector extension loading/search in SQLite | `sqlite-vec` crate + `rusqlite` extension loading | implement extension probe/load path; preserve graceful degradation when vec unavailable | vector/no-vector test matrix, fallback behavior parity | high |
| `fast-glob` | file discovery for indexing and retrieval | `globset`/`wax` + `walkdir`/`ignore` | implement deterministic file walker matching current glob behavior and exclude patterns | corpus discovery parity tests | medium |
| `picomatch` | pattern matching for filters/rules | `globset` or `regex` (case-specific) | identify each picomatch use and replace with explicit matcher wrappers | matcher unit tests from current fixtures | medium |
| `web-tree-sitter` | Tree-sitter runtime (WASM binding) for source parsing | `tree-sitter` crate (native binding to the same C library) | replace the WASM runtime with the native Rust binding; load grammars from the crates below | parse-tree parity over corpus fixtures | low |
| `tree-sitter-go` | Go grammar for chunking/symbol extraction | `tree-sitter-go` crate | depend on the Rust grammar crate (same upstream C grammar) and register with the `tree-sitter` parser | node-type/range parity tests | low |
| `tree-sitter-python` | Python grammar | `tree-sitter-python` crate | as above | node-type/range parity tests | low |
| `tree-sitter-rust` | Rust grammar | `tree-sitter-rust` crate | as above | node-type/range parity tests | low |
| `tree-sitter-typescript` | TypeScript/TSX grammar | `tree-sitter-typescript` crate | as above | node-type/range parity tests | low |
| `node-llama-cpp` | local embedding/generation/reranking and session management | Rust llama.cpp binding (`llama_cpp`, `llama-cpp-2`) or external llama.cpp server client | run spike to choose binding vs subprocess service; preserve embedding/rerank/query-expansion APIs and timeout/abort behavior | LLM smoke tests + latency/quality benchmarks | very high |
| `yaml` | collection config and serialization | `serde_yaml_ng` (preferred) or `serde_norway` | typed config structs + deterministic emit rules where needed; avoid archived `serde_yaml` and advisory-flagged `serde_yml` (RUSTSEC-2025-0068) | config roundtrip and invalid-config tests | medium |
| `zod` | runtime input/schema validation | `serde` + custom validators (`validator` if needed) | replace zod schemas with explicit typed request/response/input validation | invalid input/error message tests | high |

## Optional Dependency Plan (`optionalDependencies`)

| JS Dependency | Current Role | Rust Target | Port Plan | Validation Gate |
| --- | --- | --- | --- | --- |
| `sqlite-vec-darwin-arm64` | platform-specific vec binary | Rust build/release artifacts per target | package extension with release bundles or documented runtime prerequisite | install/run checks on macOS arm64 |
| `sqlite-vec-darwin-x64` | platform-specific vec binary | same as above | same as above | install/run checks on macOS x64 |
| `sqlite-vec-linux-arm64` | platform-specific vec binary | same as above | same as above | install/run checks on linux arm64 |
| `sqlite-vec-linux-x64` | platform-specific vec binary | same as above | same as above | install/run checks on linux x64 |
| `sqlite-vec-windows-x64` | platform-specific vec binary | same as above | same as above | install/run checks on windows x64 |

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
5. **Tree-sitter parsing parity (low risk, high leverage)**:
   the grammars are the same upstream C parsers, so the Rust `tree-sitter` crate plus the
   `tree-sitter-{go,python,rust,typescript}` grammar crates are a near-direct swap for
   `web-tree-sitter`. Validate node types and byte ranges against corpus fixtures.

## Migration Order (qmd)

1. Port storage/indexing core (`rusqlite`, schema, search basics).
2. Port glob/pattern discovery and indexing pipeline.
3. Port source parsing/chunking onto the native `tree-sitter` crate + grammar crates.
4. Port CLI parsing/output behavior and command routing.
5. Port MCP server layer and tool/resource contracts.
6. Port LLM subsystem and verify embedding/rerank/query-expansion parity.
7. Port tests and release pipeline.

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

Snapshot from `attic/qmd/pnpm-lock.yaml` (2026-05-27):
- lock entries: 376
- transitive entries: 353
- transitive unique package names: 335
- unmapped/unreachable lock entries: 0

Basis note: the original snapshot used `bun.lock`; this refresh uses `pnpm-lock.yaml`
(now present in the repo) for parity with the tbd analysis and the shared extraction
script. The earlier `sqlite-vec-win32-x64` → `sqlite-vec-windows-x64` alias no longer
applies — the manifest now lists `sqlite-vec-windows-x64` directly.
