# Feature: qmd AI-Application Porting Path

**Date:** 2026-03-04 (last status review 2026-08-08)

**Author:** Joshua Levy + Claude

**Status:** Draft

**Tracking:** `rpp-ur4d` (blocked by core plan `rpp-pk9g`)

**Status review:** The dependency-plan and lockfile-inventory inputs remain available at
their fixed 2026-05-27 source commit. No QD1-QD7 implementation item has completed, so
the feature remains blocked on the core D1-D9 work and must refresh the qmd exemplar
before execution.

## Overview

Extend the Rust Porting Playbook to support **AI-application-class TypeScript projects**
using `qmd` as the primary exemplar.
This plan follows the TypeScript-to-Rust core path (D1-D9 from
`plan-2026-03-04-typescript-to-rust-porting-path.md`) and focuses on harder problems
that go beyond CLI/filesystem tooling: LLM inference, MCP server protocols, SQLite with
vector extensions, and cross-platform native packaging. The core path is not yet
complete, so this workstream remains blocked on `rpp-pk9g`.

## Dependency on Prior Plan

This plan depends on:
- `plan-2026-03-04-typescript-to-rust-porting-path.md` (D1-D9 required; not yet
  complete)
- Existing shared Rust-target guidelines and playbooks
- The `tbd` exemplar audit (D11-D12 from prior plan) as a simpler baseline

The prior plan provides the core TS-to-Rust type mappings, CLI porting patterns, test
coverage strategy, and async guidance.
This plan extends those into application-tier complexity.

## Goals

- Prove the TS-to-Rust playbook can handle a real-world AI application (not just CLI
  tools), and identify where it cannot.
- Produce a dependency-by-dependency migration plan for all direct `qmd` dependencies,
  with spike plans for high-risk native/LLM/MCP components.
- Produce a construct coverage matrix mapping `qmd` patterns to playbook docs and
  identifying gaps.
- Document new guidance needed for LLM integration, MCP server porting, SQLite/vector
  extension packaging, and cross-platform native distribution.
- Honestly scope what is feasible vs what requires new playbook sections beyond CLI
  porting.

## Non-Goals

- Executing an actual qmd port (that would be a case study).
- Rewriting or duplicating guidance already covered by the core TS-to-Rust plan.
- Full coverage of every possible AI/ML porting pattern (focus on qmd’s specific stack).
- Bun-specific porting — qmd uses Bun but the Rust target eliminates runtime branching.

## Background

### Why qmd Is Harder Than tbd

The `tbd` exemplar (covered in the prior plan) has a favorable dependency profile for
porting:
- ~85% of its 366 transitive dependencies are tooling-only and disappear in Rust
- 12 runtime dependencies all have clear Rust crate targets
- Moderate complexity: Commander CLI + YAML + frontmatter + git subprocess

`qmd` (v2.5.2) has a fundamentally different profile:
- **~72% of its 353 transitive dependencies are runtime-owned** (inverse of tbd)
- `node-llama-cpp` alone owns **129 transitive entries** (~37% of all transitive deps)
- `@modelcontextprotocol/sdk` owns **91 transitive entries**
- A Tree-sitter parsing stack (`tree-sitter-{go,python,rust,typescript}`,
  `web-tree-sitter`) maps cleanly to native Rust crates and adds little transitive mass
- The LLM and MCP components are application-tier complexity, not CLI-tier
- Cross-platform native packaging (sqlite-vec per-platform binaries) adds distribution
  complexity

This justifies treating qmd as a separate, more ambitious plan rather than bundling it
with the CLI-focused TS-to-Rust path.

### Exemplar: `tobi/qmd`

Source: https://github.com/tobi/qmd

Audited commit: `443760f4d5a17550d77a0e3146b5b8f08452991f` (v2.5.2, 2026-05-27)

Acquisition workflow:
1. Run `tbd shortcut checkout-third-party-repo` to load canonical instructions.
2. Ensure local attic clone path exists and is gitignored (`attic/`).
3. Clone `https://github.com/tobi/qmd` to `attic/qmd`.
4. Record the audited commit SHA in all coverage deliverables.

### Existing Research (Already Produced)

The following research artifacts were produced during the prior plan’s exploratory phase
and are inputs to this plan:

- `docs/project/research/research-qmd-dependency-port-plan.md` — Direct dependency
  migration plan (22 entries across runtime/optional/peer/dev)
- `docs/project/research/research-qmd-transitive-lockfile-appendix.md` — Lockfile-level
  transitive coverage (376 lock entries, 353 transitive)
- `docs/project/research/data/qmd-lockfile-package-inventory.tsv` — Full per-entry
  inventory
- `docs/project/research/data/qmd-lockfile-summary.json` — Aggregate metrics
- `docs/project/research/data/qmd-lockfile-top-owners.json` — Owner root pressure
  ranking

## Design

### Scope Matrix

| Dimension | In Scope | Out of Scope |
| --- | --- | --- |
| Application type | AI-powered CLI with local inference, vector search, MCP server | Browser apps, cloud-hosted inference services |
| LLM integration | Local llama.cpp-based inference (embedding, generation, reranking) | Cloud API-based LLM (OpenAI, Anthropic SDKs) |
| Database | SQLite + vector extensions | Postgres, cloud databases |
| Protocol server | MCP stdio + streamable HTTP | gRPC, GraphQL, REST API frameworks |
| Distribution | Single binary with optional native extensions | npm/Bun package distribution |

### Construct Families Requiring New Guidance

These construct families are observed in `qmd` but not adequately covered by the core
TS-to-Rust plan (D1-D9):

| Construct Family | Coverage in Core Plan | Gap |
| --- | --- | --- |
| Non-Commander CLI (`util.parseArgs`, manual routing) | Partial (D4 is Commander-focused) | Need parseArgs/manual-routing-to-clap patterns |
| SQLite core (`better-sqlite3` → `rusqlite`) | Not covered | Need DB abstraction migration recipes |
| Vector extension loading (`sqlite-vec`) | Not covered | Need extension probe/load + graceful degradation patterns |
| Local LLM inference (`node-llama-cpp`) | Not covered | Need backend strategy decision tree + lifecycle/timeout mapping |
| MCP server (stdio + HTTP transports) | Not covered | Need protocol porting section + transport validation checklist |
| ANSI/progress/cursor/signal handling | Partial (D4 covers basics) | Need explicit terminal-control and signal-restoration parity |
| Cross-platform native extension packaging | Not covered | Need platform-specific binary distribution guidance |
| Child-process orchestration (spawn, execSync) | Partial (D7 covers async) | Need subprocess lifecycle + daemon workflow patterns |

### Risk-Ordered Dependency Analysis

Based on the existing research, qmd’s dependencies sort into three risk tiers:

**Tier 1 — Very High Risk (Require Dedicated Spikes):**

| Dependency | Transitive Mass | Core Issue |
| --- | --- | --- |
| `node-llama-cpp` | 129 entries | Architectural decision: direct Rust llama.cpp binding vs external inference server. Embedding, reranking, generation, model lifecycle, timeout/cancellation all need parity. |
| `@modelcontextprotocol/sdk` | 90 entries | `rmcp` Rust SDK maturity unknown. Stdio + streamable HTTP transport parity. Tool/resource contract surface. |
| `sqlite-vec` | 2 entries + 4 platform binaries | Cross-platform dynamic extension loading. Graceful degradation when unavailable. Per-OS packaging. |

**Tier 2 — High Risk (Known Patterns but Complex):**

| Dependency | Issue |
| --- | --- |
| `better-sqlite3` → `rusqlite` | Schema, prepared statements, transaction semantics. Well-understood Rust ecosystem but large surface area. |
| `zod` → `serde` + validators | Schema-to-type conversion. Explicit validation error messages with context. |

**Tier 3 — Medium/Low Risk (Clear Mappings):**

| Dependency | Rust Target |
| --- | --- |
| `fast-glob` | `globset`/`wax` + `walkdir`/`ignore` |
| `picomatch` | `globset` or `regex` |
| `yaml` | `serde_yaml_ng` |

## Deliverables

### QD1. `docs/project/research/research-qmd-construct-coverage-matrix.md`

Purpose: prove construct coverage and identify gaps in the TS-to-Rust playbook for
AI-application patterns.

Must include:
- Audited `attic/qmd` commit SHA and audit date.
- Construct inventory extracted from `qmd` (CLI routing, SQLite, vector search, LLM
  inference, MCP server, terminal UX, subprocess, config).
- Coverage matrix mapping each construct family to playbook docs (D1-D9 + shared docs).
- Gap classification (`covered`, `partially covered`, `not covered`) with explicit
  criteria for each level.
- Prioritized follow-up list for uncovered/partial areas.

DoD:
- Every construct family from the exemplar has at least one mapped destination doc.
- No `not covered` item remains without an explicit planned update or “out of scope”
  justification.

### QD2. Update `research-qmd-dependency-port-plan.md`

Purpose: finalize the existing draft dependency plan with spike results.

Must include:
- All updates from spike outcomes (QD4-QD7).
- Concrete Rust crate selections (not just candidates) for all runtime dependencies.
- Updated risk ratings based on spike findings.

DoD:
- Every runtime dependency has a validated Rust target (not just “cargo search”
  verified).
- Spike results are incorporated with measurable exit criteria status.

### QD3. New Playbook Sections for AI-Application Patterns

Purpose: extend the playbook with guidance specific to AI-application porting.

Candidate new sections (determine final scope after QD1 gap analysis):
- SQLite + extension porting patterns (`better-sqlite3` → `rusqlite`, extension loading)
- MCP server porting patterns (transport parity, tool/resource contracts)
- Local LLM integration porting patterns (binding vs service, lifecycle, cancellation)
- Cross-platform native extension distribution
- Non-Commander CLI routing migration

These may be added as sections in existing docs or as new standalone docs depending on
size. Decide after QD1.

DoD:
- Every `not covered` gap from QD1 has corresponding guidance or an explicit “out of
  scope” decision.

### QD4. Spike: LLM Backend Decision

Purpose: determine whether the Rust port should use a direct llama.cpp binding or an
external inference server.

Evaluate:
- `llama_cpp` / `llama-cpp-2` crate maturity, API surface, build complexity.
- External llama.cpp server + HTTP client approach (simpler build, process management).
- Embedding, reranking, generation, and query-expansion API parity.
- Model lifecycle management (load, unload, timeout, cancellation).
- Build/CI implications (C++ compilation, cross-platform, binary size).

Exit criteria:
- Clear recommendation with rationale documented.
- Proof-of-concept for chosen approach: embedding + generation working.
- Timeout/cancellation behavior validated.

### QD5. Spike: MCP Transport Parity

Purpose: validate `rmcp` (Rust MCP SDK) for stdio and streamable HTTP transports.

Evaluate:
- `rmcp` crate maturity and maintenance status.
- Stdio transport: tool registration, resource serving, instruction handling.
- HTTP transport: streaming, connection management, error handling.
- Tool/resource contract surface coverage vs JS SDK.

Exit criteria:
- Both transports working with representative tool/resource contracts.
- Integration test showing bidirectional protocol validation.
- Gap list for any JS SDK features not covered by `rmcp`.

### QD6. Spike: sqlite-vec Cross-Platform Packaging

Purpose: validate sqlite-vec extension loading across macOS, Linux, and Windows.

Evaluate:
- `rusqlite` extension loading API.
- sqlite-vec availability as prebuilt binary vs build-from-source.
- Graceful degradation when extension is unavailable.
- Packaging strategy: bundle with release binary vs documented prerequisite.

Exit criteria:
- Extension loads and vector search works on macOS arm64 and Linux x64 at minimum.
- Fallback behavior (no vector search) validated.
- Packaging/distribution strategy documented.

### QD7. Spike: Glob/Pattern Parity

Purpose: validate `globset`/`walkdir` against qmd’s current file discovery behavior.

Evaluate:
- Glob pattern behavior parity with `fast-glob` and `picomatch`.
- Exclude pattern handling.
- Deterministic ordering.

Exit criteria:
- Corpus discovery parity tests passing against current fixtures.
- Edge cases (symlinks, hidden files, large directories) documented.

## Implementation Plan

### Phase 1: Audit and Gap Analysis (QD1)

- [ ] Acquire/update `qmd` exemplar using `tbd shortcut checkout-third-party-repo`.
- [ ] Produce construct coverage matrix (QD1).
- [ ] Classify all gaps and determine which require new playbook sections vs are already
  covered.

**Exit gate:** Complete gap inventory with prioritized follow-up list.

### Phase 2: Spikes (QD4-QD7)

Run spikes in priority order (QD4 is highest leverage):

- [ ] LLM backend decision spike (QD4).
- [ ] MCP transport parity spike (QD5).
- [ ] sqlite-vec packaging spike (QD6).
- [ ] Glob/pattern parity spike (QD7).

**Exit gate:** All spikes have documented outcomes with clear recommendations.

### Phase 3: Documentation and Finalization (QD2, QD3)

- [ ] Update dependency port plan with spike results (QD2).
- [ ] Write new playbook sections for uncovered patterns (QD3).

**Exit gate:** No critical gap from QD1 remains unaddressed.

## Validation Strategy

### Construct Coverage Check

- [ ] Every construct family from `qmd` maps to at least one playbook doc.
- [ ] No `not covered` item remains without planned guidance or explicit scope
  exclusion.

### Dependency Coverage Check

- [ ] Every direct dependency from `attic/qmd/package.json` appears in QD2.
- [ ] Every runtime dependency has a validated Rust crate target (not just candidate).
- [ ] High-risk dependencies have spike results with pass/fail status.
- [ ] Every lock entry from `attic/qmd/pnpm-lock.yaml` appears in transitive inventory with
  action classification.
- [ ] Lockfile alias (`sqlite-vec-win32-x64` → `sqlite-vec-windows-x64`) documented and
  handled.

### Spike Validation

- [ ] Each spike has proof-of-concept code or documented evaluation.
- [ ] Each spike has explicit exit criteria with pass/fail assessment.

## Risks and Mitigations

| Risk | Severity | Mitigation |
| --- | --- | --- |
| LLM Rust bindings too immature for production use | Very High | Spike QD4 evaluates fallback to external server approach |
| `rmcp` SDK lacks feature parity with JS MCP SDK | High | Spike QD5 produces gap list; worst case: partial hand-rolled transport |
| sqlite-vec not available on all target platforms | High | Spike QD6 validates; graceful degradation is required behavior |
| Scope creep into general AI-application porting patterns | Medium | Keep guidance focused on qmd’s specific stack; generalize only if validated |
| This plan becomes stale if core TS plan (D1-D9) changes | Medium | Explicit dependency declaration; re-validate after D9 completion |

## Open Questions

- Should the LLM integration guidance be general (any local inference) or qmd-specific
  (llama.cpp only)?
- Is `rmcp` mature enough to recommend, or should the playbook document a hand-rolled
  MCP transport as the primary path?
- Should this plan produce a standalone “AI application porting” guideline, or should
  findings be integrated as sections into existing docs?
- After spikes complete, is qmd actually portable with reasonable effort, or should the
  playbook explicitly document it as “beyond current scope”?

## References

### Existing Research (Inputs)

- `docs/project/research/research-qmd-dependency-port-plan.md`
- `docs/project/research/research-qmd-transitive-lockfile-appendix.md`
- `docs/project/research/data/qmd-lockfile-package-inventory.tsv`
- `docs/project/research/data/qmd-lockfile-summary.json`
- `docs/project/research/data/qmd-lockfile-top-owners.json`

### Prerequisite Plan

- `docs/project/specs/active/plan-2026-03-04-typescript-to-rust-porting-path.md`

### External Sources

- qmd repo: https://github.com/tobi/qmd
- rmcp crate: https://crates.io/crates/rmcp
- rusqlite: https://crates.io/crates/rusqlite
- sqlite-vec: https://github.com/asg017/sqlite-vec
- llama-cpp-2: https://crates.io/crates/llama-cpp-2
- llama_cpp crate: https://crates.io/crates/llama_cpp
