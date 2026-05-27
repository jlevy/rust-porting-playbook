# Feature: Knip TypeScript-to-Rust Port Planning

**Date:** 2026-03-04 (last updated 2026-03-04)

**Author:** Joshua Levy + Claude

**Status:** Draft

## Overview

Plan the porting of **knip** (https://github.com/webpro-nl/knip), a popular TypeScript
CLI for finding unused files, dependencies, and exports, from TypeScript to Rust.

Knip is a strong exemplar for the TS-to-Rust playbook because it combines
performance-critical code paths (AST parsing, module resolution, dependency graph
traversal) with areas where TypeScript integration is acceptable (JS/TS config
evaluation, type-checker queries for opt-in features).
This makes it a realistic test of a **hybrid Rust+TS architecture** where Rust handles
the hot path and TypeScript handles the long tail of ecosystem integration.

## Dependency on Prior Plan

This plan depends on:
- `plan-2026-03-04-typescript-to-rust-porting-path.md` (D1-D9 for general TS-to-Rust
  guidance)
- Existing shared Rust-target guidelines and playbooks

The prior plan provides core TS-to-Rust type mappings, CLI porting patterns, test
coverage strategy, and async guidance.
This plan applies those to a specific, real-world project.

## Why Knip

### The Performance Case

Knip’s maintainer explicitly identifies the bottleneck: *“module resolution and AST
creation and traversal are now the slowest parts of the process and are not easy to
optimize significantly (unless perhaps switching to e.g. Rust).”*

User-reported issues include:
- Out-of-memory crashes on medium-sized TypeScript projects (issue #183).
- Perceived sluggishness on large monorepos, motivating a dedicated performance guide.
- A Go-based competitor (rev-dep) claiming 20x faster performance on the same workloads.

### The Testability Case

Knip produces **deterministic, structured output**: lists of unused files, unused
exports, unused dependencies, and unlisted dependencies.
Given a project directory, the output is fully reproducible.
This makes it ideal for:
- Golden-test parity validation during porting (TS output vs Rust output).
- Cross-validation harnesses comparing results file-by-file.
- Regression testing against real-world open source projects.

### The Ecosystem Case

- 10,400+ GitHub stars, 4.2M weekly npm downloads.
- Canonical successor to three now-archived tools (ts-prune, unimported, depcheck).
- No existing Rust alternative for this problem space.
- 140 framework-specific plugins (ESLint, Vite, Next.js, Jest, etc.).
- Active single-maintainer project with consistent releases (v5.85+).

## Goals

- Produce a detailed architectural plan for porting knip’s core analysis engine to Rust.
- Map every parsing layer to a concrete Rust crate or custom implementation strategy.
- Define a **hybrid architecture** where Rust owns the performance-critical path and
  TypeScript handles ecosystem integration (JS/TS config evaluation, optional
  type-checker queries).
- Ensure the hybrid integration is stable, well-tested, and cleanly packaged.
- Identify all risks and produce spike plans for the hardest problems.
- Use this port as a case study that validates the TS-to-Rust playbook (D1-D9).

## Non-Goals

- Executing the port in this spec (that is implementation work).
- Porting knip’s 140 plugins in the initial phase (staged approach).
- Eliminating all TypeScript dependencies (hybrid is explicitly acceptable).
- Matching every edge-case behavior of knip’s TypeScript type-checker integration in
  pure Rust.

## Background

### Knip’s Architecture

Knip operates in three phases:

**Phase 1 — File Discovery (no type checking needed):**
- Glob patterns + `fast-glob`/`picomatch` for file matching.
- `package.json` entry point extraction (`main`, `module`, `bin`, `exports`, `types`).
- Plugin config resolution: loading 140+ framework config files to find additional entry
  points and dependencies.
- Workspace/monorepo topology discovery from `pnpm-workspace.yaml`, `package.json`
  workspaces.

**Phase 2 — Import/Export Graph Building (partial type checking):**
- `ts.createProgram()` to determine file reachability from entry points.
- AST walking via `ts.forEachChild()` to extract:
  - Static imports (`import x from 'y'`, `import { x } from 'y'`).
  - Dynamic imports (`import('y')`, `require('y')`, `.then()` chains, `Promise.all`
    destructuring).
  - Re-exports (`export { x } from 'y'`, `export * from 'y'`).
  - Namespace member tracking (`NS.foo`, `NS['foo']`, destructuring).
  - CJS patterns (`module.exports`, `exports.x`).
  - JSDoc type imports (`@type {import('y').T}`).
- Module resolution via **dual strategy**:
  - Primary: `oxc-resolver` (Rust via NAPI) for fast resolution.
  - Fallback: `ts.resolveModuleName` for edge cases.
- Bound symbol table (`BoundSourceFile.symbol.exports`, `.locals`) from TypeScript
  binder for connecting import aliases to declaration symbols.

**Phase 3 — Graph Analysis (type checking only for opt-in features):**
- Unused file detection: graph reachability from entry points.
- Unused export detection: cross-file import tracing.
- Unused dependency detection: import specifiers vs `package.json`.
- **Opt-in (default off):** Class member analysis via
  `ts.LanguageService.findReferences()` (only with `--include classMembers`).
- **Opt-in (default off):** External reference checking via `findReferences()` (only
  with `--no-skip-libs`).

### Key Architectural Insight

**~85-90% of knip’s value** requires only AST parsing + module resolution + symbol
binding — **not** the full TypeScript type checker.
The type checker is used in three specific places:
1. `typeChecker.getTypeAtLocation()` — resolving computed namespace access like
   `NS[TypeKey]` (rare).
2. `typeChecker.getSymbolAtLocation()` — in-file reference checking (only with
   `ignoreExportsUsedInFile` config).
3. `LanguageService.findReferences()` — class member analysis and external ref checking
   (both opt-in, both off by default).

This means the hot path (file discovery, import/export extraction, graph building) can
be ported to Rust, while the long-tail features can delegate to a TypeScript subprocess.

### Knip’s Parsing Dependencies

| Layer | TS Dependency | What It Does |
| --- | --- | --- |
| AST parsing | `typescript` compiler API | Full TS/JS/JSX/TSX parsing + type checking |
| Module resolution (primary) | `oxc-resolver` (Rust via NAPI) | Node ESM/CJS resolution, tsconfig paths |
| Module resolution (fallback) | `typescript` (`ts.resolveModuleName`) | Edge cases: virtual files, declaration files |
| Config: JSON/JSONC | `strip-json-comments` + `JSON.parse` | Config file loading |
| Config: YAML | `yaml` | YAML config and catalog parsing |
| Config: TOML | `smol-toml` | TOML config file loading |
| Config: JS/TS | `jiti` | Dynamic import/evaluation of `*.config.ts` files |
| Schema validation | `zod` | Config schema validation |
| File discovery | `fast-glob`, `picomatch`, `@nodelib/fs.walk` | Glob matching, directory walking |
| Shell parsing | `unbash` | Extract binary references from npm scripts |
| CLI | `minimist` | Argument parsing |

### Knip’s Source Code Structure

From the `packages/knip/src/` directory:
- **Core orchestration:** `ConfigurationChief`, `ProjectPrincipal`, `WorkspaceWorker`,
  `DependencyDeputy`, `IssueCollector`, `GraphExplorer`.
- **AST visitors:** 25+ visitor files in `typescript/visitors/` handling imports,
  dynamic imports, exports, and references.
- **Plugins:** 140 plugin directories, each a declarative config object (NOT AST
  parsers). Only 3 plugins register custom AST visitors (webpack, vitest, storybook).
- **Compilers:** Simple regex transforms for non-JS files (Vue, Svelte, Astro, MDX) that
  extract `<script>` tag contents or frontmatter imports.
- **Tests:** 442 test files using Node.js built-in test runner (`node --test`).

## Design

### Executive Decision: Hybrid Rust+TS Architecture

The port uses a **hybrid architecture** where:
- **Rust owns the hot path:** file discovery, AST parsing, module resolution,
  import/export graph building, graph analysis, CLI, and output formatting.
- **TypeScript handles ecosystem integration:** JS/TS config file evaluation (via a
  lightweight Node subprocess), and optional type-checker queries for opt-in features.

This is explicitly acceptable because:
1. JS/TS config evaluation (`eslint.config.ts`, `vite.config.ts`, etc.)
   requires executing arbitrary JavaScript.
   There is no way to do this in pure Rust without embedding a JS runtime, and config
   loading is not on the hot path.
2. The type-checker features are opt-in and off by default.
   Users who need them accept the performance tradeoff.
3. Biome, oxlint, and esbuild all use similar hybrid patterns (Rust/Go core + Node.js
   integration layer) with proven packaging and distribution strategies.

### Hybrid Integration Design

The Rust binary communicates with a small TypeScript helper via:
- **Subprocess with JSON-over-stdio:** Rust spawns a Node.js process that evaluates
  config files and returns structured JSON. The TS helper is a thin wrapper around
  `jiti` + `typescript` compiler API.
- **Lifecycle:** Started on demand, kept alive for the duration of the analysis if
  multiple config evaluations are needed, then terminated.
- **Fallback:** If Node.js is not available, the Rust binary operates in “static-only”
  mode: it can parse JSON/YAML/TOML configs but skips JS/TS config files and
  type-checker features, reporting them as skipped.

Key integration requirements:
- The TS helper must be vendored or installed alongside the Rust binary (npm package or
  bundled JS).
- Communication protocol must be versioned for forward compatibility.
- Startup latency of the TS helper should be measured and documented (expected:
  200-500ms for Node.js cold start, amortized across multiple calls).
- Error handling must be explicit: TS helper crashes should produce clear diagnostics,
  not silent failures.

### Packaging Strategy

Options (to be validated in spike):
1. **npm binary package:** Rust binary distributed via npm with per-platform
   `optionalDependencies` (like esbuild/biome).
   TS helper bundled as a JS file in the same package.
2. **Standalone binary + optional npm helper:** Rust binary distributed via GitHub
   Releases / cargo-dist.
   Optional npm package provides the TS helper for config evaluation.
3. **Single npm package:** Rust binary with NAPI bindings called from a thin Node.js CLI
   wrapper (like `oxc-resolver` today).

Recommended default: Option 1 (npm binary package).
This matches the existing knip distribution model and provides the cleanest upgrade path
for existing users.

### Rust Crate Mapping for Each Parsing Layer

| Parsing Need | Rust Solution | Status | Notes |
| --- | --- | --- | --- |
| JS/TS/JSX/TSX AST parsing | `oxc_parser` | Ready | Production-ready, fastest conformant TS parser in Rust |
| Symbol/scope/reference analysis | `oxc_semantic` | Ready | Bindings, references, scopes; no type inference |
| AST traversal | `oxc_traverse` | Ready | Walking parsed trees |
| Module resolution | `oxc_resolver` | Ready | **Already validated by knip itself** via NAPI |
| JSON parsing | `serde_json` | Ready | Standard |
| JSONC parsing | `jsonc-parser` or custom strip | Ready | Small effort |
| YAML parsing | `serde_yaml_ng` | Ready | `serde_yaml` is archived and `serde_yml` has RUSTSEC-2025-0068; `serde_norway` is an alternative |
| TOML parsing | `toml` | Ready | Standard |
| Glob matching | `globset` | Ready | Production-ready |
| Directory walking | `walkdir` + `ignore` | Ready | `.gitignore` support via `ignore` crate |
| CLI argument parsing | `clap` | Ready | Maps from `minimist` (simpler migration than Commander) |
| Schema validation | `serde` + custom validation | Ready | Replace Zod with Rust struct validation |
| tsconfig.json | `oxc_resolver` tsconfig support | Partial | Paths/extends handled; `include`/`exclude` file computation needs custom code |
| Shell script parsing | `yash-syntax` or `brush-parser` | Partial | Bash/POSIX basics covered; npm script edge cases may differ from `unbash` |
| Dynamic import patterns | `oxc_parser` + custom visitors | Partial | `.then()` chains, `Promise.all` destructuring need porting from knip’s 25+ visitor files |
| JS/TS config evaluation | **TS helper subprocess** | Gap | Cannot be done in pure Rust; requires Node.js |
| TypeScript type checker | **TS helper subprocess** | Gap | Only needed for opt-in features |
| `ts.createProgram` file reachability | Custom graph walker | Gap | Replace with: parse imports → resolve → walk iteratively (well-understood pattern) |

### Porting Strategy: What Moves to Rust vs Stays in TypeScript

**Moves to Rust (performance-critical):**
- File discovery and glob matching.
- AST parsing of all JS/TS/JSX/TSX files.
- Import/export extraction (all 25+ visitor patterns).
- Module resolution (already Rust via `oxc_resolver`).
- Dependency graph construction and traversal.
- Unused file/export/dependency detection.
- CLI, output formatting, reporters.
- JSON/YAML/TOML config parsing.
- Shell script parsing for npm script binary extraction.
- Workspace/monorepo topology discovery.

**Stays in TypeScript (ecosystem integration, not perf-critical):**
- JS/TS config file evaluation (`jiti`-based dynamic import).
- TypeScript type-checker queries (opt-in features: class members, external refs).
- Non-JS file compilers (Vue/Svelte/Astro `<script>` extraction — simple regexes that
  could move to Rust later but are not on the hot path).

### Plugin Architecture

Knip’s 140 plugins are declarative config objects, not AST parsers.
Each plugin provides:
- Config file glob patterns.
- An `isEnabled` check (is this tool a dependency?).
- A `resolveConfig` function that reads the loaded config and returns dependency/input
  references.

In the Rust port:
- **Phase 1:** Port the plugin framework to Rust.
  Each plugin becomes a Rust struct implementing a `Plugin` trait.
  Config files loaded via JSON/YAML/TOML parsers (for static configs) or the TS helper
  (for JS/TS configs).
- **Phase 2:** Port plugins incrementally, starting with the most-used ones (eslint,
  vitest, typescript, webpack, jest, next, storybook, tailwind, etc.).
- **Phase 3:** Provide a plugin API that allows new plugins to be defined in TOML/JSON
  for static cases, reducing the need for code changes.

The 3 plugins with custom AST visitors (webpack `require.context()`, vitest
`import.meta.vitest`, storybook) need their visitors ported to `oxc_parser` AST types.

## Deliverables

### KD1. `docs/project/research/research-knip-construct-coverage-matrix.md`

Purpose: map every knip construct family to the TS-to-Rust playbook and identify gaps.

Must include:
- Audited `attic/knip` commit SHA and audit date.
- Construct inventory: file discovery, AST parsing, module resolution, graph building,
  plugin system, reporters, compilers, config loading, CLI.
- Coverage matrix mapping each construct to playbook docs (D1-D8) and Rust crate
  targets.
- Gap classification with required playbook updates.

DoD:
- Every construct family maps to at least one Rust crate or implementation strategy.
- No critical gap remains without a spike plan or explicit “deferred” decision.

### KD2. `docs/project/research/research-knip-dependency-port-plan.md`

Purpose: dependency-by-dependency migration plan for all knip dependencies.

Must include:
- Full dependency inventory from `packages/knip/package.json` (runtime and dev).
- For each runtime dependency: current role, Rust target, migration strategy, risk
  rating.
- Explicit handling of `typescript` (the dependency) — it stays as TS helper, not
  ported.
- Transitive dependency analysis for runtime deps.

DoD:
- Every runtime dependency has a Rust crate target or explicit “stays in TS” decision.
- Risk ratings reflect actual crate maturity (verified, not just searched).

### KD3. Spike: Hybrid Rust+TS Integration

Purpose: validate that the Rust binary can reliably communicate with a TS helper for
config evaluation and type-checker queries.

Evaluate:
- JSON-over-stdio protocol design and implementation.
- Node.js subprocess lifecycle management (start, keep-alive, terminate).
- Startup latency measurement and amortization strategy.
- Error handling: TS helper crashes, timeouts, malformed responses.
- Packaging: how the TS helper is bundled with the Rust binary in an npm package.
- Fallback: graceful degradation when Node.js is unavailable.

Exit criteria:
- Working prototype: Rust binary spawns TS helper, sends config evaluation requests,
  receives structured JSON responses.
- Latency benchmarks documented (cold start, warm call, amortized over N configs).
- Error scenarios tested: helper crash, timeout, invalid JSON.
- Packaging prototype: npm package with Rust binary + bundled TS helper.

### KD4. Spike: oxc_parser + oxc_semantic for Import/Export Extraction

Purpose: validate that oxc can replace TypeScript’s AST for knip’s import/export
analysis.

Evaluate:
- Parse a representative corpus of TS/JS/JSX/TSX files from real projects.
- Extract all import/export patterns that knip’s 25+ visitors handle.
- Compare extracted data against knip’s own output for the same files.
- Validate `oxc_semantic` symbol binding for namespace member tracking.
- Measure parsing performance vs TypeScript compiler.

Exit criteria:
- Import/export extraction matches knip’s output for >=95% of patterns in test corpus.
- Gap list for any patterns `oxc_parser` cannot handle (with workaround plan).
- Performance benchmarks: parsing throughput (files/sec) vs TypeScript.

### KD5. Spike: Custom Module Graph Walker

Purpose: validate that a custom Rust graph walker can replace `ts.createProgram()` for
file reachability.

Evaluate:
- Build a module graph: parse each file’s imports → resolve with `oxc_resolver` → walk.
- Compare discovered file set against `ts.createProgram().getSourceFiles()` for real
  projects.
- Handle edge cases: circular imports, barrel files, conditional imports, path aliases.

Exit criteria:
- File discovery matches `ts.createProgram()` for >=98% of files in test corpus.
- Performance benchmark: graph construction time vs `ts.createProgram()`.
- Edge case inventory with resolution strategy for each.

### KD6. Spike: Shell Script Parsing Parity

Purpose: validate Rust shell parsers against `unbash` for npm script binary extraction.

Evaluate:
- Parse `scripts` fields from a corpus of real `package.json` files.
- Compare extracted binary references against `unbash` output.
- Test edge cases: pipes, subshells, environment variables, `npx`/`pnpx` invocations.

Exit criteria:
- Binary extraction matches `unbash` for >=95% of scripts in test corpus.
- Gap list with workaround plan for unmatched patterns.

## Implementation Plan

### Phase 1: Research and Spikes

- [ ] Acquire knip source using `tbd shortcut checkout-third-party-repo` (`attic/knip`).
- [ ] Produce construct coverage matrix (KD1).
- [ ] Produce dependency port plan (KD2).
- [ ] Run hybrid integration spike (KD3).
- [ ] Run oxc parser spike (KD4).
- [ ] Run module graph walker spike (KD5).
- [ ] Run shell parsing spike (KD6).

**Exit gate:** All spikes have documented outcomes.
Architecture is validated or revised based on findings.

### Phase 2: Core Engine Port

- [ ] Implement Rust CLI skeleton with `clap` (matching knip’s `minimist` interface).
- [ ] Implement file discovery (glob + workspace topology).
- [ ] Implement AST parsing and import/export extraction using `oxc_parser` +
  `oxc_semantic`.
- [ ] Implement module resolution using `oxc_resolver`.
- [ ] Implement custom module graph walker.
- [ ] Implement graph analysis: unused files, exports, dependencies.
- [ ] Implement JSON/YAML/TOML config loading.
- [ ] Implement shell script parsing for npm scripts.
- [ ] Implement output reporters (text, JSON, markdown, compact).

**Exit gate:** Core analysis produces correct results for a test corpus of real
projects, without any TypeScript integration.
“Static-only” mode works end-to-end.

### Phase 3: Hybrid Integration

- [ ] Implement TS helper subprocess for JS/TS config evaluation.
- [ ] Implement communication protocol (JSON-over-stdio).
- [ ] Implement plugin framework in Rust with TS config delegation.
- [ ] Port top-20 most-used plugins.
- [ ] Implement opt-in type-checker features via TS helper.
- [ ] Implement packaging: npm binary package with bundled TS helper.

**Exit gate:** Full knip feature parity for common use cases.
Golden-test parity with TypeScript knip on real projects.

### Phase 4: Plugin Expansion and Polish

- [ ] Port remaining plugins (prioritized by download count of the tool they support).
- [ ] Performance optimization: parallelism, memory efficiency, incremental analysis.
- [ ] Cross-platform testing (macOS, Linux, Windows).
- [ ] Documentation and migration guide for existing knip users.

**Exit gate:** Feature parity with TypeScript knip.
Published npm package passing CI on all platforms.

## Testing Strategy

### Golden Test Parity

The primary validation strategy: run both TypeScript knip and Rust knip on the same
projects and compare output.

- Build a corpus of 10-20 real open source TypeScript projects of varying complexity.
- For each project, capture knip’s current output as golden files.
- Rust port must match golden output exactly (or document intentional improvements).
- Automate as a CI job that runs on every PR.

### Unit Tests

- Import/export extraction: test each visitor pattern against known AST fixtures.
- Module resolution: test against `oxc_resolver`’s own test suite + knip-specific edge
  cases.
- Graph analysis: test with synthetic dependency graphs covering all detection types.
- Config loading: test each format (JSON, JSONC, YAML, TOML) with real-world configs.

### Integration Tests

- Hybrid integration: TS helper subprocess lifecycle, error handling, timeout behavior.
- Plugin system: end-to-end tests for top-20 plugins with real framework configs.
- Cross-platform: CI matrix covering macOS arm64, Linux x64, Windows x64.

### Performance Benchmarks

- Parse throughput: files/second for AST parsing (oxc vs TypeScript compiler).
- Full analysis: wall-clock time on benchmark projects (small, medium, large monorepo).
- Memory usage: peak RSS on large projects (address the OOM issue).
- Startup time: cold start of Rust binary vs Node.js knip.

## Risks and Mitigations

| Risk | Severity | Mitigation |
| --- | --- | --- |
| oxc_parser AST differences cause import/export extraction gaps | High | KD4 spike validates against real corpus; fallback to TS helper for unhandled patterns |
| Hybrid TS integration adds packaging/distribution complexity | High | KD3 spike validates packaging; follow proven patterns (esbuild, biome) |
| Custom module graph walker misses files `ts.createProgram` finds | High | KD5 spike validates with >=98% parity target; TS fallback for edge cases |
| JS/TS config evaluation is too slow via subprocess | Medium | Amortize startup across calls; batch config requests; measure in KD3 |
| Plugin porting is high volume (140 plugins) | Medium | Staged approach: top-20 first, then community contributions; most plugins are simple config readers |
| `unbash` shell parsing edge cases not covered by Rust parsers | Medium | KD6 spike validates; fall back to regex for unmatched patterns |
| Upstream knip evolves during port, creating a moving target | Medium | Pin to audited commit SHA; periodic sync after initial parity |
| Node.js not available on user’s system for TS helper | Low | Graceful degradation: “static-only” mode with clear messaging about skipped features |

## Open Questions

- Should the Rust port be a new project (`knip-rs`) or a contribution to the upstream
  knip repo?
- What is the minimum plugin coverage needed for a useful v0.1 release?
- Should the TS helper be a bundled `.js` file or a separately installed npm package?
- Can `oxc_semantic` handle enough of the bound symbol table needs, or do we need a
  custom binding pass?
- Is there value in supporting a WASM build for browser-based knip (e.g., knip
  playground)?

## References

### Source Project

- knip repo: https://github.com/webpro-nl/knip
- knip performance guide: https://knip.dev/guides/performance
- knip configuration reference: https://knip.dev/reference/configuration

### Rust Ecosystem (Parsing)

- oxc project: https://github.com/oxc-project/oxc
- oxc_parser: https://crates.io/crates/oxc_parser
- oxc_semantic: https://crates.io/crates/oxc_semantic
- oxc_resolver: https://crates.io/crates/oxc_resolver (also:
  https://github.com/oxc-project/oxc-resolver)
- oxc_traverse: https://crates.io/crates/oxc_traverse
- oxc_module_lexer: https://crates.io/crates/oxc_module_lexer
- swc_ecma_parser: https://crates.io/crates/swc_ecma_parser (alternative)

### Rust Ecosystem (Other)

- clap: https://crates.io/crates/clap
- serde_json: https://crates.io/crates/serde_json
- serde_yaml_ng: https://crates.io/crates/serde_yaml_ng
- toml: https://crates.io/crates/toml
- globset: https://crates.io/crates/globset
- walkdir: https://crates.io/crates/walkdir
- ignore: https://crates.io/crates/ignore
- yash-syntax: https://crates.io/crates/yash-syntax
- brush-parser: https://crates.io/crates/brush-parser

### Hybrid Architecture Precedents

- esbuild: Go core + npm distribution with per-platform binaries
- Biome: Rust core + npm distribution (`@biomejs/biome`)
- oxlint: Rust core + npm distribution (`oxlint`)
- oxc-resolver: Rust crate with NAPI bindings for Node.js consumption

### Prerequisite Plan

- `docs/project/specs/active/plan-2026-03-04-typescript-to-rust-porting-path.md`

### Ecosystem Data (As of 2026-03-04)

- knip: 10,433 GitHub stars, 4.2M weekly npm downloads
- TypeScript: 83.7% of knip codebase
- 423 source files, 442 test files, 140 plugins
- knip already uses `oxc-resolver` (Rust) for module resolution via NAPI
