# Feature: TypeScript-to-Rust Porting Path

**Date:** 2026-03-04 (last updated 2026-03-04)

**Author:** Joshua Levy + Claude

**Status:** Draft

## Overview

Extend the Rust Porting Playbook to support **TypeScript as a source language**,
providing equivalent coverage to what currently exists for Python-to-Rust porting.
This means creating a parallel set of documents — playbooks, guidelines, mapping
references, checklists, and templates — that guide an AI agent through porting a
TypeScript application to Rust with the same rigor, test discipline, and process quality
as the Python path.

## Goals

- Provide a complete TypeScript-to-Rust porting path with the same 8-phase methodology
  (Assess, Research, Plan, Set Up, Port, Fix, Finalize, Sync)
- Create TypeScript-specific type mapping, dependency mapping, and CLI porting references
- Reuse generic/process-level docs (porting principles, cross-language test mapping,
  checklist templates) without duplication
- Incorporate relevant TypeScript best practices from tbd guidelines
  (`typescript-rules`, `typescript-cli-tool-rules`, `pnpm-monorepo-patterns`,
  `bun-monorepo-patterns`, etc.) as source material
- Reorganize the repo so that Python-specific, TypeScript-specific, Rust-specific, and
  generic docs are clearly distinguished
- Make the playbook genuinely multi-source-language without losing depth on either path

## Non-Goals

- Executing an actual TypeScript-to-Rust port (that would be a separate case study)
- Covering other source languages beyond Python and TypeScript in this iteration
- Rewriting docs that are already correct and generic
- Changing the core 8-phase porting methodology
- Duplicating tbd guidelines verbatim — we adapt and reference them

## Background

### Current State

The Rust Porting Playbook currently has ~20 docs (~300 pages) organized into 5 layers:

| Layer | Directory | Count | Focus |
| --- | --- | --- | --- |
| Playbooks | `playbooks/` | 11 files | Process, reference, checklists |
| Guidelines | `guidelines/` | 8 files | Compact rules for agent context |
| Research | `docs/project/research/` | 2 files | Deep dives (distribution) |
| Case Studies | `case-studies/` | 2 dirs | Flowmark (done), repren (planning) |
| Meta Process | `_meta/` | 6+ files | Self-improvement framework |

### Document Classification

**Python-specific docs** (7 docs — these need TypeScript parallels):

1. `playbooks/python-to-rust-playbook.md` — 8-phase process with Python-specific
   commands, tooling (uv, pytest, coverage.py)
2. `playbooks/python-to-rust-mapping-reference.md` — exhaustive type/construct mappings
3. `playbooks/python-to-rust-porting-guide.md` — detailed methodology with Python
   pitfalls
4. `playbooks/python-to-rust-test-coverage-playbook.md` — pre-port coverage strategy
   using Python tooling
5. `guidelines/python-to-rust-porting-rules.md` — type mappings, module patterns,
   dependency mapping
6. `guidelines/python-to-rust-cli-porting.md` — argparse/click/typer to clap mapping
7. `playbooks/auto-sync-agent-prompt-template.md` — sync prompt referencing Python repos

**Rust-specific docs** (8 docs — these are shared across both paths):

1. `guidelines/rust-general-rules.md` — Edition 2024+, ownership, error handling
2. `guidelines/rust-cli-app-patterns.md` — clap, project structure, error reporting
3. `guidelines/rust-project-setup.md` — Cargo.toml, CI, release workflows
4. `guidelines/filesystem-heavy-cli-porting.md` — atomic writes, backups, walkdir
5. `playbooks/rust-cli-best-practices.md` — modern Rust CLI patterns
6. `playbooks/rust-code-review-checklist.md` — code review criteria
7. `docs/project/research/research-rust-cli-binary-distribution.md`
8. `docs/project/research/research-rust-cli-pypi-distribution.md`

**Generic/process docs** (7 docs — reusable as-is):

1. `guidelines/porting-principles-and-antipatterns.md` — 9 principles (need minor
   generalization)
2. `guidelines/test-coverage-for-porting.md` — strategy (needs minor generalization)
3. `playbooks/cross-language-test-mapping.md` — YAML-based mapping (generic)
4. `playbooks/port-checklist-initial-template.md` — execution checklist (generic)
5. `playbooks/port-checklist-update-template.md` — sync checklist (generic)
6. `playbooks/python-to-rust-sync-release-workflow.md` — two-stage workflow (mostly
   generic)

### tbd Guidelines as Source Material

The tbd tool ships with extensive TypeScript and monorepo guidelines that are valuable
source material for the TypeScript-to-Rust porting path:

| tbd Guideline | Relevance to Porting Path |
| --- | --- |
| `typescript-rules` | Type system mapping, coding patterns, error handling idioms — essential for understanding TypeScript source code patterns that map to Rust |
| `typescript-cli-tool-rules` | Commander.js/picocolors patterns — the TypeScript equivalent of argparse/click, maps to clap in Rust |
| `pnpm-monorepo-patterns` | TypeScript project structure (pnpm workspaces, tsdown, CI) — informs TypeScript project assessment |
| `bun-monorepo-patterns` | Alternative TS toolchain (Bun workspaces, bunup, Biome) — informs TypeScript project assessment |
| `typescript-code-coverage` | Vitest coverage (v8 provider) — TypeScript equivalent of pytest --cov |
| `typescript-sorting-patterns` | Deterministic sorting — porting pitfall area |
| `typescript-yaml-handling-rules` | YAML parsing patterns — maps to serde_yaml_ng |
| `golden-testing-guidelines` | Golden/snapshot testing — shared technique, already used |
| `general-tdd-guidelines` | TDD methodology — shared across both paths |
| `general-testing-rules` | Testing best practices — shared across both paths |

These guidelines should be read and adapted (not copied verbatim) when creating the
TypeScript-specific porting documents. They provide the TypeScript-side context that
mirrors what the Python docs already provide for the Python-to-Rust path.

### Key Differences: TypeScript vs Python as Source Language

Understanding these differences is essential for accurate porting documentation:

**Type system:**
- TypeScript has a sophisticated static type system (generics, conditional types,
  mapped types, template literals) — closer to Rust than Python's optional type hints
- TypeScript's structural typing vs Rust's nominal typing creates unique mapping
  challenges
- TypeScript interfaces/type aliases have no runtime presence — Rust structs/enums do

**Runtime and ecosystem:**
- TypeScript compiles to JavaScript — runtime behavior is JavaScript, not TypeScript
- `null` and `undefined` (two kinds of nothing) vs Rust's `Option<T>`
- JavaScript's prototype-based OOP vs Rust's trait-based system
- npm/pnpm/bun ecosystem vs Cargo ecosystem
- Node.js async model (event loop, Promises) vs Rust async (futures, tokio)

**Project structure:**
- `package.json` / `tsconfig.json` vs `Cargo.toml`
- `node_modules` vs Cargo's dependency management
- ESM/CJS module system vs Rust's module system
- Monorepo patterns (pnpm workspaces, Bun workspaces) vs Cargo workspaces

**Testing:**
- Vitest/Jest vs cargo test
- c8/v8 coverage vs cargo-llvm-cov
- Snapshot testing (Vitest inline snapshots) vs insta
- No equivalent of `tryscript` golden tests for TS CLIs (or is there?)

**CLI tooling:**
- Commander.js / yargs / oclif vs clap
- picocolors / chalk vs anstream / console
- process.exit() vs std::process::ExitCode
- Node.js SIGPIPE handling differences

**Error handling:**
- try/catch with untyped exceptions vs Result<T, E>
- throw vs return Err()
- No equivalent of Python's exception hierarchy richness in TS
- TypeScript errors are stringly-typed at runtime

**Package distribution:**
- npm publish vs crates.io / cargo-dist
- npx vs cargo install
- Bun compile (standalone binary) as an interesting comparison point

## Design

### Approach

Create a parallel document set following the same layered architecture, with clear
naming conventions that distinguish source language. Reorganize the repo directory
structure to make the multi-language nature explicit.

### Proposed Repository Structure

```
rust-porting-playbook/
├── README.md                          # Updated: multi-source-language overview
├── playbooks/
│   ├── general/                       # Language-agnostic process docs
│   │   ├── porting-playbook.md        # Generalized 8-phase process template
│   │   ├── cross-language-test-mapping.md
│   │   ├── port-checklist-initial-template.md
│   │   ├── port-checklist-update-template.md
│   │   ├── sync-release-workflow.md
│   │   └── auto-sync-agent-prompt-template.md
│   ├── python-to-rust/               # Python-specific playbooks
│   │   ├── python-to-rust-playbook.md
│   │   ├── python-to-rust-mapping-reference.md
│   │   ├── python-to-rust-porting-guide.md
│   │   └── python-to-rust-test-coverage-playbook.md
│   ├── typescript-to-rust/            # NEW: TypeScript-specific playbooks
│   │   ├── typescript-to-rust-playbook.md
│   │   ├── typescript-to-rust-mapping-reference.md
│   │   ├── typescript-to-rust-porting-guide.md
│   │   └── typescript-to-rust-test-coverage-playbook.md
│   └── rust/                          # Target-language (Rust) docs
│       ├── rust-cli-best-practices.md
│       └── rust-code-review-checklist.md
├── guidelines/
│   ├── general/                       # Language-agnostic guidelines
│   │   ├── porting-principles-and-antipatterns.md
│   │   └── test-coverage-for-porting.md
│   ├── python-to-rust/               # Python-specific guidelines
│   │   ├── python-to-rust-porting-rules.md
│   │   └── python-to-rust-cli-porting.md
│   ├── typescript-to-rust/            # NEW: TypeScript-specific guidelines
│   │   ├── typescript-to-rust-porting-rules.md
│   │   ├── typescript-to-rust-cli-porting.md
│   │   └── typescript-to-rust-async-porting.md
│   └── rust/                          # Target-language guidelines
│       ├── rust-general-rules.md
│       ├── rust-cli-app-patterns.md
│       ├── rust-project-setup.md
│       └── filesystem-heavy-cli-porting.md
├── docs/project/research/            # Research docs (add TS-relevant ones)
│   ├── research-rust-cli-binary-distribution.md
│   ├── research-rust-cli-pypi-distribution.md
│   └── research-rust-cli-npm-distribution.md  # NEW
├── case-studies/                      # Unchanged structure
│   ├── flowmark/
│   └── repren/
└── _meta/                             # Unchanged
```

**Note on reorganization:** This is an ideal target structure. The reorganization itself
is a significant effort and could be done incrementally. The initial phase could create
the new TypeScript docs in the existing flat structure, with reorganization as a
follow-up phase. The key principle: old URLs/paths should be handled gracefully if the
repo has external references.

### New Documents Required

The following new documents need to be created for the TypeScript-to-Rust path. Each
document is modeled after its Python-to-Rust counterpart but with TypeScript-specific
content.

#### Tier 1: Core Playbook and Guidelines (Must-Have)

These are the essential documents that enable a TypeScript-to-Rust port.

**1. `typescript-to-rust-playbook.md`** (modeled on `python-to-rust-playbook.md`)
- Same 8-phase structure
- TypeScript-specific tooling in each phase:
  - Phase 1: Assess with `tsc`, Vitest coverage, npm/pnpm dependency audit
  - Phase 2: Research with TypeScript → Rust library equivalents
  - Phase 3: Plan with TypeScript module → Rust module mapping
  - Phase 4: Set up with TypeScript source as submodule, `npm install` or `pnpm install`
  - Phase 5: Port with TypeScript tests → Rust tests
  - Phase 6: Fix library differences (different ecosystem pitfalls)
  - Phase 7: Finalize with npm-compatible distribution
  - Phase 8: Sync with TypeScript upstream

**2. `typescript-to-rust-porting-rules.md`** (modeled on
`python-to-rust-porting-rules.md`)
- TypeScript → Rust type mappings:
  - `string` → `String` / `&str`
  - `number` → `f64` / `i64` / `usize` (JavaScript numbers are all f64!)
  - `boolean` → `bool`
  - `null | undefined` → `Option<T>` (two nothings → one)
  - `T[]` / `Array<T>` → `Vec<T>`
  - `Map<K, V>` → `HashMap<K, V>`
  - `Set<T>` → `HashSet<T>`
  - `Record<string, T>` → `HashMap<String, T>`
  - `Promise<T>` → `Future<Output = T>` / `async fn`
  - `interface` / `type` → `struct` + `impl`
  - `enum` (TS string unions) → Rust `enum`
  - `unknown` → generics / `Box<dyn Any>`
  - `never` → `!` (never type) or `Infallible`
  - Discriminated unions → Rust enums (natural fit!)
  - Generic types `<T extends Foo>` → `<T: Foo>` trait bounds
  - Conditional types → (no direct equivalent, use trait specialization patterns)
- Module mapping patterns (`import/export` → `mod`/`pub`)
- Error handling mapping (`try/catch` → `Result<T, E>`)
- Dependency mapping table (TypeScript → Rust library equivalents)
- Key pitfalls unique to TypeScript-to-Rust
- Sources: tbd `typescript-rules`, original research

**3. `typescript-to-rust-mapping-reference.md`** (modeled on
`python-to-rust-mapping-reference.md`)
- Exhaustive construct-by-construct mapping with code examples
- Sections: Types, Collections, Control Flow, Functions, Classes/Interfaces → Traits,
  Async/Await, Modules, Error Handling, Testing, I/O, String Operations, Regex
- TypeScript-specific sections not in Python version:
  - Generics and type parameters → Rust generics
  - Decorators → procedural macros (limited parallel)
  - Prototype chain / class hierarchy → trait hierarchy
  - Symbol / WeakMap / WeakSet → (no direct Rust equivalent)
  - TypeScript enums (numeric and string) → Rust enums
  - Template literal types → (no direct equivalent)
  - Optional chaining (`?.`) → `.map()` / `if let` / `?` operator
  - Nullish coalescing (`??`) → `.unwrap_or()` / `.unwrap_or_else()`
  - Spread operator (`...`) → `.clone()` / `.extend()` / struct update syntax
- Sources: tbd `typescript-rules`, original research

**4. `typescript-to-rust-cli-porting.md`** (modeled on
`python-to-rust-cli-porting.md`)
- Commander.js / yargs / oclif → clap mapping table
- Commander global options → clap derive API
- picocolors / chalk → anstream / console
- `process.stdout.isTTY` → `std::io::IsTerminal`
- `process.exit()` → `std::process::ExitCode`
- Node.js stream piping → Rust BufReader/BufWriter
- `NO_COLOR` / `FORCE_COLOR` support mapping
- Shell completion: `--completions` patterns
- SIGPIPE handling in Node.js vs Rust
- npm bin installation → cargo install / cargo-dist
- Sources: tbd `typescript-cli-tool-rules`, original research

**5. `typescript-to-rust-test-coverage-playbook.md`** (modeled on
`python-to-rust-test-coverage-playbook.md`)
- Pre-port coverage strategy using TypeScript tooling:
  - Vitest with v8 coverage provider
  - c8 / istanbul coverage
  - Jest coverage (if source uses Jest)
- Coverage thresholds matching the Python ones
- Golden test patterns for TypeScript CLIs
- tryscript usage for TypeScript CLI golden tests
- Cross-validation scripts for TypeScript + Rust
- Test fixture organization
- Sources: tbd `typescript-code-coverage`, tbd `golden-testing-guidelines`

#### Tier 2: Supporting Documents (High Value)

**6. `typescript-to-rust-porting-guide.md`** (modeled on
`python-to-rust-porting-guide.md`)
- Detailed methodology for TypeScript-to-Rust porting
- TypeScript-specific pitfalls and solutions:
  - JavaScript number semantics (all numbers are f64, integer overflow is different)
  - `undefined` vs `null` collapse to `Option`
  - Prototype-based OOP → trait-based design
  - Dynamic dispatch in TS → static dispatch in Rust
  - Closure semantics differences (TS closures capture by reference to mutable
    variables)
  - `this` binding complexity → explicit self in Rust
  - Module resolution differences (Node.js resolution vs Rust module tree)
  - Async/Promise patterns → Rust futures/tokio
- Automation scripts for cross-validation

**7. `typescript-to-rust-async-porting.md`** (new — no Python equivalent because
Python's async is less pervasive)
- Unique guideline for porting async TypeScript to Rust
- Promise chains → Future combinators
- `async/await` mapping (similar syntax, very different semantics)
- Event loop (Node.js) → tokio runtime
- `Promise.all()` → `futures::join!` / `tokio::join!`
- `Promise.race()` → `tokio::select!`
- Callback patterns → channels or async streams
- Error handling in async contexts
- Sources: original research, tbd `typescript-rules` (async section)

**8. `research-rust-cli-npm-distribution.md`** (new research doc)
- How to distribute Rust CLI binaries via npm (the TypeScript equivalent of the
  PyPI/maturin research)
- Patterns from real projects: `@biomejs/biome`, `esbuild`, `@oxlint/oxlint`
- npm optional dependencies pattern for platform-specific binaries
- postinstall scripts for binary download
- Alternative: Bun compile for standalone executables

#### Tier 3: Generalization of Existing Docs

**9. Generalize `porting-principles-and-antipatterns.md`**
- Currently says "Python-to-Rust" in title and throughout
- Change to be language-agnostic while keeping all 9 principles
- Examples can reference both Python and TypeScript
- Minimal changes needed — the principles are inherently generic

**10. Generalize `test-coverage-for-porting.md`**
- Currently references `pytest`, `uv run`, Python-specific tooling
- Add TypeScript-equivalent commands alongside Python ones
- Or split into: generic strategy + language-specific tool appendices

**11. Generalize `cross-language-test-mapping.md`**
- Currently says "Python-to-Rust" in several places
- The YAML schema and CI approach is fully generic
- Generalize language in text; keep the flowmark-specific examples as illustrations

**12. Generalize sync/release workflow docs**
- `auto-sync-agent-prompt-template.md` — add TypeScript variant
- `sync-release-workflow.md` — already mostly generic
- `port-checklist-initial-template.md` — already generic
- `port-checklist-update-template.md` — already generic

**13. Update README.md**
- Reflect multi-source-language nature
- Add TypeScript quick-start bootstrap instructions
- Update the "Five Layers" table
- Add TypeScript to the "For AI Agents" section

#### Tier 4: Reorganization (Can Be Deferred)

**14. Directory restructuring** (as shown in proposed structure above)
- Move files into `general/`, `python-to-rust/`, `typescript-to-rust/`, `rust/`
  subdirectories
- Update all cross-references
- Handle redirects / old paths gracefully

### Content Mapping: Python Doc → TypeScript Equivalent

This table shows exactly what each new TypeScript doc should cover, mapped from its
Python counterpart:

| Python Doc | TypeScript Equivalent | Key Content Adaptations |
| --- | --- | --- |
| `python-to-rust-playbook.md` | `typescript-to-rust-playbook.md` | Replace `uv`/`pytest` with `pnpm`/`vitest`; replace `pyproject.toml` with `package.json`/`tsconfig.json`; adjust Phase 1 assessment for TS tooling; adjust Phase 4 for TS submodule setup |
| `python-to-rust-mapping-reference.md` | `typescript-to-rust-mapping-reference.md` | Full rewrite of type tables; add generics, interfaces, discriminated unions, template literals; address `null`/`undefined` duality; add async/Promise mapping |
| `python-to-rust-porting-guide.md` | `typescript-to-rust-porting-guide.md` | Replace Python pitfalls with TS pitfalls (number semantics, `this` binding, prototype chain, closure capture, module resolution); adjust automation scripts |
| `python-to-rust-test-coverage-playbook.md` | `typescript-to-rust-test-coverage-playbook.md` | Replace pytest/coverage.py with vitest/v8; adjust fixture generation scripts; same golden test patterns |
| `python-to-rust-porting-rules.md` | `typescript-to-rust-porting-rules.md` | Rewrite type mapping tables; adjust dependency mapping table; replace Python idiom examples with TS equivalents |
| `python-to-rust-cli-porting.md` | `typescript-to-rust-cli-porting.md` | Replace argparse/click/typer with Commander.js/yargs; replace colorama/rich with picocolors/chalk; adjust I/O and process handling |
| (no equivalent) | `typescript-to-rust-async-porting.md` | NEW — async is pervasive in TypeScript in ways it isn't in Python |
| `research-rust-cli-pypi-distribution.md` | `research-rust-cli-npm-distribution.md` | npm distribution patterns instead of PyPI/maturin |

### tbd Guidelines Usage Plan

The following tbd guidelines should be consulted when writing each TypeScript-to-Rust
document:

| New Document | tbd Guidelines to Consult | How to Use |
| --- | --- | --- |
| `typescript-to-rust-porting-rules.md` | `typescript-rules` | Source for TS type patterns, idioms, and conventions that need Rust equivalents |
| `typescript-to-rust-cli-porting.md` | `typescript-cli-tool-rules` | Source for Commander.js patterns, color handling, option parsing that maps to clap |
| `typescript-to-rust-test-coverage-playbook.md` | `typescript-code-coverage`, `golden-testing-guidelines`, `general-tdd-guidelines` | Source for Vitest/v8 coverage patterns and golden test methodology |
| `typescript-to-rust-playbook.md` | `pnpm-monorepo-patterns`, `bun-monorepo-patterns` | Source for understanding TS project structure, CI, build tooling |
| `typescript-to-rust-mapping-reference.md` | `typescript-rules`, `typescript-sorting-patterns`, `typescript-yaml-handling-rules` | Source for type system details, sorting patterns, YAML handling |
| `typescript-to-rust-async-porting.md` | `typescript-rules` (async section) | Source for Promise/async patterns |

## Implementation Plan

### Phase 1: Core TypeScript Porting Documents

Create the essential documents that enable a TypeScript-to-Rust port. These are Tier 1
from the design section.

- [ ] Create `typescript-to-rust-porting-rules.md` in `guidelines/` — the compact
  agent-context guideline with type mappings, dependency mappings, module patterns, and
  key pitfalls. (Consult tbd `typescript-rules`.)
- [ ] Create `typescript-to-rust-mapping-reference.md` in `playbooks/` — exhaustive
  construct-by-construct mapping with code examples for every TypeScript concept and its
  Rust equivalent. (Consult tbd `typescript-rules`,
  `typescript-sorting-patterns`, `typescript-yaml-handling-rules`.)
- [ ] Create `typescript-to-rust-playbook.md` in `playbooks/` — the 8-phase process
  adapted for TypeScript source projects. (Consult tbd `pnpm-monorepo-patterns`,
  `bun-monorepo-patterns`.)
- [ ] Create `typescript-to-rust-cli-porting.md` in `guidelines/` — CLI-specific
  patterns for Commander.js/yargs/oclif → clap. (Consult tbd
  `typescript-cli-tool-rules`.)
- [ ] Create `typescript-to-rust-test-coverage-playbook.md` in `playbooks/` — pre-port
  coverage strategy using Vitest/v8/c8. (Consult tbd `typescript-code-coverage`,
  `golden-testing-guidelines`.)

### Phase 2: Supporting Documents and Research

Create the supporting documents that add depth and handle TypeScript-specific concerns.

- [ ] Create `typescript-to-rust-porting-guide.md` in `playbooks/` — detailed
  methodology with TypeScript-specific pitfalls and solutions.
- [ ] Create `typescript-to-rust-async-porting.md` in `guidelines/` — async-specific
  porting patterns (Promises → futures, event loop → tokio).
- [ ] Create `research-rust-cli-npm-distribution.md` in `docs/project/research/` —
  survey of how Rust CLIs distribute via npm (Biome, esbuild, oxlint patterns).

### Phase 3: Generalization and Integration

Generalize existing docs and update the top-level README.

- [ ] Generalize `porting-principles-and-antipatterns.md` — remove Python-specific
  language, make examples language-agnostic or dual-language.
- [ ] Generalize `test-coverage-for-porting.md` — add TypeScript tooling alongside
  Python tooling references.
- [ ] Generalize `cross-language-test-mapping.md` — update language to be
  source-agnostic while keeping concrete examples.
- [ ] Add TypeScript variant to `auto-sync-agent-prompt-template.md`.
- [ ] Update `README.md` — add TypeScript path, update quick-start with TypeScript
  bootstrap instructions, update tables and agent guidance.

### Phase 4: Repository Reorganization (Optional / Deferred)

Restructure directories for clean multi-language organization.

- [ ] Create subdirectory structure (`general/`, `python-to-rust/`,
  `typescript-to-rust/`, `rust/`) under both `playbooks/` and `guidelines/`.
- [ ] Move existing files into appropriate subdirectories.
- [ ] Update all internal cross-references.
- [ ] Verify no broken links.
- [ ] Update `.claude/` and `.tbd/` configuration if needed.

## Testing Strategy

- **Link validation:** Run `lychee` or equivalent on all markdown files to verify no
  broken cross-references after reorganization.
- **Content review:** Each new TypeScript doc should be reviewed for:
  - Completeness against its Python counterpart (same sections covered)
  - Accuracy of TypeScript → Rust type/construct mappings
  - Correctness of library equivalence claims
  - No stale or wrong tbd guideline references
- **Agent usability test:** Load the new TypeScript guidelines into an agent context and
  verify they provide actionable guidance for a real TypeScript project assessment.
- **Cross-reference audit:** Verify that all documents reference each other correctly
  and that the README entry points work for both Python and TypeScript paths.

## Rollout Plan

1. **Phase 1 first:** Create the core 5 documents. These alone make the TypeScript path
   usable.
2. **Phase 2 next:** Add depth with the porting guide, async guide, and npm research.
3. **Phase 3 after:** Generalize existing docs and update README. This is lower risk and
   can be done incrementally.
4. **Phase 4 deferred:** Directory reorganization is valuable but not blocking. Can be
   done as a separate effort once the content is stable.

## Open Questions

- Should we pursue a TypeScript-to-Rust case study in parallel with writing the docs?
  (A small project like a TS CLI tool would validate the new docs and generate a case
  study.)
- For the directory restructuring (Phase 4), should we use symlinks or redirects for
  backward compatibility, or just accept the one-time breakage?
- Should the generalized 8-phase playbook be a standalone document that both
  language-specific playbooks reference, or should each language-specific playbook be
  self-contained?
- Are there TypeScript-to-Rust porting projects in the wild that we should survey for
  lessons? (Similar to how the Python path learned from the flowmark port.)
- Should we cover Deno as a TypeScript runtime variant, or focus exclusively on
  Node.js/Bun?

## References

### Existing Playbook Docs

- `playbooks/python-to-rust-playbook.md` — primary model for TypeScript playbook
- `playbooks/python-to-rust-mapping-reference.md` — primary model for mapping reference
- `guidelines/python-to-rust-porting-rules.md` — primary model for porting rules
- `guidelines/python-to-rust-cli-porting.md` — primary model for CLI porting
- `guidelines/porting-principles-and-antipatterns.md` — to be generalized
- `guidelines/test-coverage-for-porting.md` — to be generalized

### tbd Guidelines (Source Material)

- `tbd guidelines typescript-rules` — TypeScript coding rules and best practices
- `tbd guidelines typescript-cli-tool-rules` — CLI tool rules for Commander.js,
  picocolors, TypeScript
- `tbd guidelines typescript-code-coverage` — Vitest code coverage with v8 provider
- `tbd guidelines typescript-sorting-patterns` — deterministic sorting patterns
- `tbd guidelines typescript-yaml-handling-rules` — YAML parsing/serialization
- `tbd guidelines pnpm-monorepo-patterns` — pnpm workspace architecture
- `tbd guidelines bun-monorepo-patterns` — Bun workspace architecture
- `tbd guidelines golden-testing-guidelines` — golden/snapshot testing
- `tbd guidelines general-tdd-guidelines` — TDD methodology
- `tbd guidelines general-testing-rules` — testing best practices

### External References

- TypeScript Handbook: https://www.typescriptlang.org/docs/handbook/
- Rust Book: https://doc.rust-lang.org/book/
- clap documentation: https://docs.rs/clap/latest/clap/
- Commander.js: https://github.com/tj/commander.js
- Vitest: https://vitest.dev/
- Biome (Rust CLI distributed via npm): https://biomejs.dev/
