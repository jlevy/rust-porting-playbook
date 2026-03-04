# Feature: TypeScript-to-Rust Porting Path

**Date:** 2026-03-04 (last updated 2026-03-04)

**Author:** Joshua Levy + Claude

**Status:** Draft (revised after senior review)

## Overview

Extend the Rust Porting Playbook to support **TypeScript as a source language** with
comparable depth to the existing Python-to-Rust path.

This effort adds TypeScript-specific playbooks/guidelines while keeping core process and
Rust-target guidance shared.
The result should be a reliable, citation-backed path an AI agent can use to port a real
TypeScript project to Rust with strong parity and test rigor.

## Executive Decisions (2026-03-04)

These decisions remove ambiguity and unblock writing:

1. **Runtime scope:** Node.js is primary.
   Bun is supported as a variant where behavior is materially different.
   Deno is explicitly deferred.
2. **Project scope:** CLI tools and filesystem-heavy tooling are first-class.
   Browser/DOM frameworks are out of scope for this iteration.
3. **Structure strategy:** Deliver TypeScript docs in the current flat structure first.
   Directory reorganization is a separate follow-up after content stabilizes.
4. **Evidence standard:** Any claim that is version-sensitive (tool versions, action
   versions, runtime behavior) must have a primary source citation and an as-of date.

## Goals

- Provide a complete TypeScript-to-Rust porting path aligned to the existing 8 phases
  (Assess, Research, Plan, Set Up, Port, Fix, Finalize, Sync).
- Create TypeScript-specific mapping, CLI, testing, and async guidance that is accurate
  for modern TS/Node ecosystems.
- Reuse generic/process-level docs without duplicating them.
- Integrate relevant tbd guidance (`typescript-rules`, `typescript-cli-tool-rules`,
  `typescript-code-coverage`, monorepo patterns, golden testing, TDD/testing rules).
- Keep Python and TypeScript paths equally usable from README entry points.

## Non-Goals

- Executing an actual TypeScript-to-Rust port in this spec (that is a case study).
- Full Deno coverage in this iteration.
- Rewriting stable Rust-target docs that are already language-agnostic.
- Forcing immediate directory moves before content quality is validated.

## Senior Review Findings on the Original Draft

| Finding | Impact | Resolution in this revision |
| --- | --- | --- |
| Runtime scope (Node/Bun/Deno) was ambiguous | Conflicting guidance and tooling choices | Added explicit scope matrix and phase gates for Node-first, Bun-variant, Deno deferred |
| Some TS→Rust mappings were unsafe or oversimplified (`unknown`, conditional types, Promise rejection, `never`) | Could produce incorrect ports | Replaced with fidelity-based mapping rules and explicit caveats |
| Test guidance had internal contradiction (questioning tryscript vs later requiring it) | Confusing execution guidance | Made tryscript an explicit recommended path for CLI golden tests |
| Bun + Vitest coverage interaction not accounted for | Risk of invalid coverage setup | Added runtime-specific testing guidance (Vitest v8 on Node; Bun alternatives documented) |
| Acceptance criteria were broad but not measurable | Hard to know when phase is done | Added per-document DoD and cross-doc validation checklist |
| Version drift policy missing | High risk of stale references | Added version tracking policy and required citation discipline |

## Current Repo Scope (Baseline)

As of 2026-03-04 on this branch:

| Layer | Directory | Current Count | Notes |
| --- | --- | --- | --- |
| Playbooks | `playbooks/` | 11 files | Includes Python-specific and generic docs |
| Guidelines | `guidelines/` | 8 files | Includes Python-specific and Rust-target docs |
| Research | `docs/project/research/` | 2 files | Binary distribution + PyPI distribution research |
| Case Studies | `case-studies/` | 2 directories | flowmark + repren |
| Meta | `_meta/` | multiple files | Plans, templates, improvement process |

### Python-Specific Documents Requiring TypeScript Parallels

1. `playbooks/python-to-rust-playbook.md`
2. `playbooks/python-to-rust-mapping-reference.md`
3. `playbooks/python-to-rust-porting-guide.md`
4. `playbooks/python-to-rust-test-coverage-playbook.md`
5. `guidelines/python-to-rust-porting-rules.md`
6. `guidelines/python-to-rust-cli-porting.md`
7. `playbooks/auto-sync-agent-prompt-template.md` (needs TS variant section)

## Research Inputs Used for This Plan

### tbd Guidelines (Consulted)

| Guideline | Key Takeaway for This Plan |
| --- | --- |
| `typescript-rules` | Emphasize strict typing, no `any` shortcuts, discriminated-union exhaustiveness, static imports, and pragmatic exception handling |
| `typescript-cli-tool-rules` | Commander patterns, global options discipline, `--no-*` flag gotcha, color precedence (`--color`, `NO_COLOR`, `FORCE_COLOR`, TTY) |
| `typescript-code-coverage` | Vitest + v8 baseline thresholds and reporting expectations |
| `pnpm-monorepo-patterns` | Workspace/tooling reality for modern Node+TS repos; version drift must be tracked |
| `bun-monorepo-patterns` | Bun-specific workspace/build/test patterns and tradeoffs |
| `typescript-sorting-patterns` | Deterministic ordering and explicit tiebreakers as parity-critical behavior |
| `typescript-yaml-handling-rules` | YAML parser/serializer discipline and validation expectations |
| `golden-testing-guidelines` | Golden/session tests and tryscript workflow for CLI behavior checks |
| `general-tdd-guidelines` | Red-green-refactor and small behavioral increments |
| `general-testing-rules` | Minimal test count with maximal meaningful coverage |

### External Primary Sources (Validated)

| Topic | Source | Planning Implication |
| --- | --- | --- |
| TS structural typing, unions, template literal types, strict null semantics | TypeScript Handbook + TSConfig docs | Mapping docs must separate compile-time typing from runtime JS behavior |
| Node package `exports`/`imports` and module resolution boundaries | Node package docs | Porting guide must treat ESM/CJS boundaries as explicit migration risk |
| npm `optionalDependencies` + `os`/`cpu`/`libc` fields | npm package.json docs | npm-distribution research must cover platform-binary package topology |
| Rust `IsTerminal`, `ExitCode`, `Infallible`, and never-type caveats | Rust std docs | CLI and type-mapping docs must avoid oversimplified TS→Rust equivalence claims |
| Tokio `join!` / `select!` behavior | Tokio docs | Async guide must call out cancellation and race semantics differences |
| Vitest coverage + c8 docs | Vitest + c8 docs | Testing playbook must define runtime-specific coverage tooling |
| Bun test runner coverage | Bun docs | Bun variant requires dedicated coverage instructions (not blind Vitest parity) |
| cargo-dist npm installer support | cargo-dist book | npm distribution research should compare cargo-dist installer path vs custom scripts |

### Local Exemplar Codebase Audit Input: `jlevy/tbd`

To keep this plan grounded in a real, complex TS CLI, we use the `tbd` codebase as an
exemplar for construct coverage.

Acquisition workflow (required):
1. Run `tbd shortcut checkout-third-party-repo` to load canonical instructions.
2. Ensure local attic clone path exists and is gitignored (`attic/`).
3. Clone `https://github.com/jlevy/tbd` to `attic/tbd`.
4. Record the audited commit SHA in the coverage matrix deliverable.

Construct families observed in `tbd` that the porting playbook must cover:
- pnpm monorepo + ESM package setup (`pnpm-workspace.yaml`, root/package `package.json`,
  `exports`, bin bootstrap).
- Commander-heavy CLI architecture (global options, subcommands, `--no-*` semantics,
  grouped help, colorized help).
- Terminal/runtime behavior (`NO_COLOR`, TTY checks, pager usage, EPIPE and SIGINT
  handling, JSON/text dual output).
- Filesystem safety patterns (atomic writes via `atomically`, lock-directory
  coordination, backups, migration paths).
- YAML/Markdown/Zod stack (frontmatter parsing, YAML conflict detection, schema
  validation, canonical field ordering).
- Git subprocess/worktree orchestration (isolated index, merge/retry flow, conflict
  attic, branch health checks).
- Async/process patterns (spawn/execFile, timeout + AbortController, dynamic imports).
- Test architecture (Vitest + tryscript golden tests + coverage workflows).

#### Preliminary Coverage Snapshot (`attic/tbd`, 2026-03-04)

Initial mapping of exemplar constructs against this plan revision:

| Exemplar Construct Family | Coverage Status | Primary Destination Docs | Required Strengthening |
| --- | --- | --- | --- |
| pnpm monorepo + ESM packaging (`exports`, `bin`) | partial | D3, D8 | Add explicit ESM/CJS + bin-bootstrap migration patterns |
| Commander subcommands + global options + `--no-*` | covered | D4 | Keep parity checklist strict |
| Terminal behavior (`NO_COLOR`, TTY, pager, EPIPE, SIGINT) | partial | D4, D6 | Add dedicated runtime behavior parity subsection |
| YAML + markdown frontmatter + schema validation (Zod) | partial | D1, D2, D6 | Add schema-validation and frontmatter migration recipe |
| Atomic writes + lock-directory coordination + backups | partial | D6 + existing filesystem-heavy guideline | Add cross-reference and lock/atomic migration patterns |
| Git subprocess/worktree sync + conflict attic/merge strategy | partial | D6, D8 | Add advanced git-workflow porting section with failure modes |
| Async subprocess timeout/cancellation (`AbortController`) | partial | D7, D6 | Add cancellation/timeouts mapping examples |
| Dynamic imports for lazy/conditional loading | partial | D1, D6 | Add decision rule: preserve/lift/replace dynamic imports |
| Vitest + tryscript golden testing + coverage merge | covered | D5 | Keep Node vs Bun tooling caveats explicit |

The D11 and D12 deliverables formalize this snapshot at a fixed commit SHA and track gap
closure.

### Ecosystem Snapshot (As of 2026-03-04)

Validated from npm registry metadata during this review:

- `typescript`: `5.9.3`
- `vitest`: `4.0.18`
- `@vitest/coverage-v8`: `4.0.18`
- `commander`: `14.0.3`
- `picocolors`: `1.1.1`
- `c8`: `11.0.0`
- `esbuild`: `0.27.3`
- `@biomejs/biome`: `2.4.5`
- `oxlint`: `1.51.0`

This snapshot is informative only; documents should cite sources and verify again when
writing/refreshing concrete commands.

## Design

### Scope Matrix

| Dimension | In Scope (Phase 1-3) | Deferred |
| --- | --- | --- |
| Source runtime | Node.js (primary), Bun (variant notes) | Deno |
| App types | CLI tools, filesystem-heavy tools, service-style TS libraries | Browser/DOM-heavy apps, React/Next frontends |
| Packaging | crates.io, GitHub Releases, npm binary distribution patterns | npm + Deno hybrid publish flows |
| Testing | Vitest/Jest/Bun test mapping + tryscript golden approach | Browser mode/testing frameworks beyond porting needs |

### Repository Layout Strategy

Short term (this initiative): keep current directories and add new files in-place.

Long term (optional follow-up): reorganize into `general/`, `python-to-rust/`,
`typescript-to-rust/`, `rust/` subtrees after links and agent prompts are validated.

### Proposed Future Structure (Deferred)

```
rust-porting-playbook/
├── playbooks/
│   ├── general/
│   ├── python-to-rust/
│   ├── typescript-to-rust/
│   └── rust/
├── guidelines/
│   ├── general/
│   ├── python-to-rust/
│   ├── typescript-to-rust/
│   └── rust/
└── docs/project/research/
```

## Deliverables (Required Content + Definition of Done)

### D1. `guidelines/typescript-to-rust-porting-rules.md`

Purpose: compact, high-signal rules for agent context windows.

Must include:
- Type mapping table with **fidelity tags**: `exact`, `lossy`, `requires redesign`.
- Explicit handling of `number` safety (`Number.isSafeInteger` implications) and
  `bigint` mapping.
- `Promise` mapping that includes rejection/error channel semantics.
- `unknown`, `never`, discriminated unions, conditional/mapped/template literal types
  treatment.
- Module/import/export and `exports` boundary guidance.
- Common dependency mapping table (TS package → Rust crate candidates).

DoD:
- Every non-trivial mapping has at least one concrete example.
- No claim implies Rust trait specialization is required/stable.
- References included for runtime-sensitive claims.

### D2. `playbooks/typescript-to-rust-mapping-reference.md`

Purpose: exhaustive construct-by-construct reference (deep companion to D1).

Must include:
- Types, collections, control flow, classes/interfaces, async, modules, errors,
  filesystem, regex, testing, packaging.
- TS-only tricky areas: structural typing, type erasure at runtime, optional chaining,
  nullish coalescing, spread/rest semantics, decorators caveats.
- Sort determinism and YAML handling appendices aligned with tbd guidelines.

DoD:
- Section parity with Python mapping reference where applicable.
- Explicit “no direct equivalent” strategy patterns (not just warnings).

### D3. `playbooks/typescript-to-rust-playbook.md`

Purpose: full 8-phase workflow for TS→Rust execution.

Must include:
- Phase gates and pass/fail criteria per phase.
- Source assessment for `package.json`, lockfiles, workspace topology, tsconfig, test
  tooling.
- Port order strategy, parity matrix template, traceability requirements.
- Sync/update workflow for upstream TypeScript releases.

DoD:
- Matches structure quality of `python-to-rust-playbook.md`.
- Includes Node-primary and Bun-variant notes where behavior/tooling differs.

### D4. `guidelines/typescript-to-rust-cli-porting.md`

Purpose: CLI-specific mapping for Commander/yargs/oclif to clap.

Must include:
- Option/flag mapping patterns and Commander gotchas (`--no-*` behavior).
- Output/color behavior parity and precedence policy.
- TTY, piping, pager integration, EPIPE/SIGPIPE, SIGINT, and exit-code parity
  expectations.
- Shell completion and help-output parity guidance.

DoD:
- Includes a parity checklist usable in PR review.
- Uses modern Rust primitives (`IsTerminal`, `ExitCode`) accurately.

### D5. `playbooks/typescript-to-rust-test-coverage-playbook.md`

Purpose: test sufficiency before and during port.

Must include:
- Baseline coverage workflow for Vitest (and Jest/Bun variant notes).
- Golden testing strategy with tryscript for CLI behavior.
- Cross-validation harness patterns (TS vs Rust output comparisons).
- Coverage threshold policy and CI enforcement.

DoD:
- No contradictory guidance on tryscript applicability.
- Runtime/tooling caveats documented (Node vs Bun coverage differences).

### D6. `playbooks/typescript-to-rust-porting-guide.md`

Purpose: deep methodology and recurring pitfall handling.

Must include:
- JS numeric semantics, null/undefined behavior, prototype/class migration, `this`
  binding pitfalls, module boundaries, error propagation patterns.
- File safety and durability patterns: atomic writes, lock coordination,
  backup/migration workflows.
- Git subprocess + worktree orchestration patterns (including conflict and retry flows).
- Dynamic import migration patterns (preserve vs replace).
- Practical “investigate before fix” workflow for parity diffs.

DoD:
- Contains actionable recipes, not just warnings.

### D7. `guidelines/typescript-to-rust-async-porting.md`

Purpose: async-specific source-to-target guidance.

Must include:
- Promise chains, async/await, `Promise.all`/`race`/`allSettled` mapping patterns.
- Cancellation/backpressure/runtime shutdown differences.
- Subprocess timeout/cancellation patterns (`AbortController`-style behavior).
- Error and timeout handling in async paths.

DoD:
- Explicitly documents semantic mismatches (not one-to-one syntax mapping).

### D8. `docs/project/research/research-rust-cli-npm-distribution.md`

Purpose: evidence-backed npm distribution strategy for Rust CLIs.

Must include:
- Optional dependency topology for per-platform binaries.
- `os`/`cpu`/`libc` constraints and installation behavior.
- Comparison of approaches: custom installer scripts vs cargo-dist npm installer.
- Case-study patterns (esbuild, Biome, oxlint).

DoD:
- Includes concrete release workflow recommendations and security considerations.
- Contains explicit “recommended default for this playbook” section.

### D9. Generalize Existing Shared Docs

Required updates:
- `guidelines/porting-principles-and-antipatterns.md`
- `guidelines/test-coverage-for-porting.md`
- `playbooks/cross-language-test-mapping.md`
- `playbooks/auto-sync-agent-prompt-template.md` (TS variant)
- `playbooks/python-to-rust-sync-release-workflow.md` (language-neutral framing or TS
  companion section)
- `README.md`

DoD:
- Shared docs no longer imply Python-only source language.
- README has clear entry points for Python and TypeScript paths.

### D10. Optional Reorganization

Required only after D1-D9 are validated.

DoD:
- All internal links updated.
- Old paths remain discoverable via clear migration notes.
- Agent prompts/configs updated only after link validation passes.

### D11. `docs/project/research/research-tbd-construct-coverage-matrix.md`

Purpose: prove the TS→Rust path can handle a real-world TS CLI with complex setup and
runtime behavior.

Must include:
- Audited `attic/tbd` commit SHA and audit date.
- Construct inventory extracted from `tbd` (setup, runtime, filesystem, git, testing,
  typing patterns).
- Coverage matrix mapping each construct family to specific playbook deliverables
  (D1-D8) and existing shared docs.
- For each construct family, explicit Rust-side destination mapping (stdlib primitive,
  crate, and/or implementation pattern expected in the port).
- Gap classification (`covered`, `partially covered`, `not covered`) with required doc
  updates.
- Prioritized follow-up checklist for uncovered/partial areas.

DoD:
- Every construct family from the exemplar has at least one mapped destination doc.
- No `not covered` item remains without an explicit planned update.

### D12. `docs/project/research/research-tbd-dependency-port-plan.md`

Purpose: dependency-by-dependency migration plan for all direct `tbd` dependencies.

Must include:
- Full direct dependency inventory (runtime, optional, peer, dev/build toolchain).
- For each dependency: current role, Rust target (crate/pattern), migration steps,
  validation gates, and risk rating.
- Explicit plans for CLI, markdown/frontmatter, YAML/schema, color/output, and
  test/coverage tool migration.
- Companion lockfile-level transitive appendix with one-row-per-lock-entry inventory and
  action classification.

DoD:
- No direct dependency from `attic/tbd/package.json` and
  `attic/tbd/packages/tbd/package.json` is omitted.
- Dependency tables are one row per dependency entry (no grouped dependency rows),
  preserving package-scope distinctions.
- Every runtime dependency has either a Rust crate target or an explicit in-house
  implementation plan.
- No lock entry from `attic/tbd/pnpm-lock.yaml` is left without an action classification
  or owner mapping.

## Content Mapping: Python Documents to TypeScript Counterparts

| Python Doc | TypeScript Counterpart | Critical Adaptation |
| --- | --- | --- |
| `python-to-rust-playbook.md` | `typescript-to-rust-playbook.md` | Replace Python tooling/process examples with TS runtime/tooling reality and Node/Bun variants |
| `python-to-rust-mapping-reference.md` | `typescript-to-rust-mapping-reference.md` | Rebuild type/construct mapping around structural typing + runtime JS semantics |
| `python-to-rust-porting-guide.md` | `typescript-to-rust-porting-guide.md` | Replace Python-centric pitfalls with TS/Node pitfalls and module-runtime concerns |
| `python-to-rust-test-coverage-playbook.md` | `typescript-to-rust-test-coverage-playbook.md` | Replace pytest/coverage.py with Vitest/Jest/Bun test coverage and tryscript integration |
| `python-to-rust-porting-rules.md` | `typescript-to-rust-porting-rules.md` | Compact TS→Rust mappings with fidelity labels and caveats |
| `python-to-rust-cli-porting.md` | `typescript-to-rust-cli-porting.md` | Commander/yargs/oclif patterns mapped to clap + terminal behavior parity |
| (none) | `typescript-to-rust-async-porting.md` | Async semantics and cancellation model differences |
| `research-rust-cli-pypi-distribution.md` | `research-rust-cli-npm-distribution.md` | npm binary topology instead of wheel/maturin model |

## Implementation Plan

### Phase 0: Finalize Constraints and Templates

- [ ] Confirm runtime scope in this plan text (Node primary, Bun variant, Deno
  deferred).
- [ ] Define standard section templates for D1-D7 so docs are structurally consistent.
- [ ] Add reference discipline rule: version-sensitive claims need source + as-of date.

### Phase 1: Core TypeScript Path (D1-D5)

- [ ] Create `guidelines/typescript-to-rust-porting-rules.md` (D1).
- [ ] Create `playbooks/typescript-to-rust-mapping-reference.md` (D2).
- [ ] Create `playbooks/typescript-to-rust-playbook.md` (D3).
- [ ] Create `guidelines/typescript-to-rust-cli-porting.md` (D4).
- [ ] Create `playbooks/typescript-to-rust-test-coverage-playbook.md` (D5).

**Exit gate:** A TypeScript CLI project can be assessed, planned, ported, and validated
using only existing Rust docs + D1-D5.

### Phase 2: Depth + Research (D6-D8)

- [ ] Create `playbooks/typescript-to-rust-porting-guide.md` (D6).
- [ ] Create `guidelines/typescript-to-rust-async-porting.md` (D7).
- [ ] Create `docs/project/research/research-rust-cli-npm-distribution.md` (D8).

**Exit gate:** Deep pitfalls and npm distribution decisions are fully documented with
primary-source evidence.

### Phase 2.5: Exemplar Audit and Dependency Plan (D11-D12)

- [ ] Acquire/update `tbd` exemplar using `tbd shortcut checkout-third-party-repo` flow
  (`attic/tbd`).
- [ ] Produce `research-tbd-construct-coverage-matrix.md` with audited commit SHA and
  construct inventory.
- [ ] Produce `research-tbd-dependency-port-plan.md` with full dependency mapping and
  migration strategy.
- [ ] Produce `research-tbd-transitive-lockfile-appendix.md` with `pnpm-lock.yaml`
  inventory and action coverage.
- [ ] Map exemplar constructs and dependencies to target docs (D1-D8/shared docs) and
  classify coverage.
- [ ] Create explicit follow-up items for any uncovered or weakly covered construct or
  dependency.

**Exit gate:** No critical construct or dependency from `tbd` remains unmapped to the
TS-to-Rust playbook without an action item.

Note: A separate plan spec covers `qmd` as a more complex AI-application exemplar (LLM
inference, MCP server, vector DB). That work depends on D1-D9 from this plan being
complete. See `plan-2026-03-04-qmd-ai-application-porting-path.md`.

### Phase 3: Integration (D9)

- [ ] Generalize shared docs and README so both source-language paths are first-class.
- [ ] Add TS variant to sync prompt template.

**Exit gate:** README navigation is symmetric for Python and TypeScript users/agents.

### Phase 4: Optional Reorganization (D10)

- [ ] Implement directory move only after link and usability validation passes.

**Exit gate:** No broken links; migration notes published.

## Validation Strategy

### Accuracy and Citation Checks

- [ ] Every version-sensitive claim has a source URL and as-of date.
- [ ] Type/async mappings reviewed for semantic correctness (not just syntax
  similarity).
- [ ] CLI behavior mappings validated against Node/Rust docs for terminal and exit
  behavior.

### Cross-Document Consistency Checks

- [ ] Terminology is consistent (`source language`, `target language`, `parity`,
  `cross-validation`).
- [ ] No conflicting guidance between compact guidelines and deep playbooks.
- [ ] All new docs link to relevant existing Rust/general docs.

### Mechanical Checks

- [ ] Run markdown link validation (e.g., `lychee`).
- [ ] Run `rg` sweeps for stale Python-only phrasing in generalized docs.
- [ ] Verify file references used by README and templates resolve correctly.

### Agent Usability Check

- [ ] Simulate a TS project assessment prompt and confirm D1-D5 produce actionable,
  concrete steps.
- [ ] Confirm generated guidance includes explicit caveats where mapping is lossy.

### Exemplar Coverage Check (`attic/tbd`)

- [ ] Verify all major construct families from `tbd` appear in D11 matrix and map to
  specific docs.
- [ ] For each `partially covered` or `not covered` family, verify a planned doc update
  exists (with owner and phase).
- [ ] Confirm high-risk runtime behaviors (signals, EPIPE, TTY/color precedence, pager,
  subprocess+timeout, git worktree merge/conflict flows) are explicitly addressed in
  TypeScript-path docs.

### Dependency Coverage Check (`attic/tbd`)

- [ ] Verify every direct dependency from audited package manifests appears in D12.
- [ ] Verify each runtime dependency has a concrete Rust target or explicit in-house
  implementation plan.
- [ ] Verify high-risk dependencies have spike plans and measurable exit criteria.
- [ ] Verify every lock entry from `attic/tbd/pnpm-lock.yaml` appears in transitive
  inventory artifacts with action classification.

## Risks and Mitigations

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Overstated one-to-one TS→Rust mappings | High | Use fidelity tags and explicit redesign patterns |
| Tool/version drift (TS, Node, Vitest, Actions, etc.) | High | Source + as-of policy; periodic refresh checklist |
| Node/Bun differences create inconsistent advice | High | Node-primary baseline + clearly marked Bun variants |
| Synthetic examples miss real-world construct complexity | High | Run D11 `tbd` exemplar coverage matrix and close uncovered areas |
| Dependency blind spots in `tbd` runtime stack | High | Run D12 full dependency plan and require spike gates for high-risk deps |
| Reorganization breaks references | Medium | Defer move; validate links before and after |
| Docs become too broad and lose practical focus | Medium | Keep CLI/filesystem tooling as primary scenario |

## Rollout and Version Drift Policy

1. Ship D1-D5 first (usable path).
2. Add D6-D8 depth and research.
3. Run D11-D12 exemplar audit and dependency plan (`tbd`) and close critical gaps.
4. Integrate D9 and validate navigation.
5. Consider D10 reorganization only after stability.

Version drift policy:
- Maintain an “as-of” date at the top of each research-heavy document.
- Re-verify tool versions and workflow actions before each major refresh.
- Prefer linking to official docs/release pages over tertiary summaries.

## Open Questions (Non-Blocking)

- Should Deno support become a separate Phase 5 after Node/Bun docs stabilize?
- Should we add a small TS-to-Rust case study in parallel to validate D1-D7 sooner?
- For optional reorganization, should we keep compatibility shim files for one release
  cycle?

## References

### Existing Playbook Documents

- `playbooks/python-to-rust-playbook.md`
- `playbooks/python-to-rust-mapping-reference.md`
- `playbooks/python-to-rust-porting-guide.md`
- `playbooks/python-to-rust-test-coverage-playbook.md`
- `guidelines/python-to-rust-porting-rules.md`
- `guidelines/python-to-rust-cli-porting.md`
- `guidelines/porting-principles-and-antipatterns.md`
- `guidelines/test-coverage-for-porting.md`

### tbd Guidelines (Source Material)

- `tbd guidelines typescript-rules`
- `tbd guidelines typescript-cli-tool-rules`
- `tbd guidelines typescript-code-coverage`
- `tbd guidelines typescript-sorting-patterns`
- `tbd guidelines typescript-yaml-handling-rules`
- `tbd guidelines pnpm-monorepo-patterns`
- `tbd guidelines bun-monorepo-patterns`
- `tbd guidelines golden-testing-guidelines`
- `tbd guidelines general-tdd-guidelines`
- `tbd guidelines general-testing-rules`
- `tbd shortcut checkout-third-party-repo`

### External Primary Sources

- TypeScript Handbook:
  https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
- TypeScript Generics: https://www.typescriptlang.org/docs/handbook/2/generics.html
- TypeScript Conditional Types:
  https://www.typescriptlang.org/docs/handbook/2/conditional-types.html
- TypeScript Template Literal Types:
  https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html
- TSConfig `strictNullChecks`:
  https://www.typescriptlang.org/tsconfig/strictNullChecks.html
- Node package entry points (`exports`/`imports`): https://nodejs.org/api/packages.html
- Node process/TTY behavior: https://nodejs.org/api/process.html
- npm `package.json` fields (`optionalDependencies`, `os`, `cpu`, `libc`):
  https://docs.npmjs.com/cli/v11/configuring-npm/package-json
- Rust `std::io::IsTerminal`: https://doc.rust-lang.org/std/io/trait.IsTerminal.html
- Rust `std::process::ExitCode`:
  https://doc.rust-lang.org/std/process/struct.ExitCode.html
- Rust `std::convert::Infallible`:
  https://doc.rust-lang.org/std/convert/enum.Infallible.html
- Rust never type docs: https://doc.rust-lang.org/std/primitive.never.html
- Tokio `join!`: https://docs.rs/tokio/latest/tokio/macro.join.html
- Tokio `select!`: https://docs.rs/tokio/latest/tokio/macro.select.html
- clap docs: https://docs.rs/clap/latest/clap/
- Commander.js: https://github.com/tj/commander.js
- Vitest coverage guide: https://vitest.dev/guide/coverage.html
- c8 package: https://www.npmjs.com/package/c8
- Bun test coverage: https://bun.sh/docs/test/coverage
- cargo-dist npm installers:
  https://opensource.axo.dev/cargo-dist/book/installers/npm.html
- tryscript package/docs entry: https://www.npmjs.com/package/tryscript
- esbuild package: https://www.npmjs.com/package/esbuild
- Biome package: https://www.npmjs.com/package/@biomejs/biome
- oxlint package: https://www.npmjs.com/package/oxlint
- tbd exemplar repo: https://github.com/jlevy/tbd
- qmd exemplar repo (deferred to separate plan): https://github.com/tobi/qmd
