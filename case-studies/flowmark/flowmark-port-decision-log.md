# Flowmark Port: Decision Log & Tactics

All key decisions, phase-by-phase tactics, and metrics from the flowmark Python-to-Rust
port. For library-specific decisions and workarounds, see
[Library Choices](flowmark-port-library-choices.md).

**Related:**
[Library Choices](flowmark-port-library-choices.md) |
[Analysis](flowmark-port-analysis.md)

**Last update:** 2026-02-08

## Decision Format

Each decision follows: Context → Decision → Consequences → Lessons.

---

## D1: Parser Library Selection (comrak)

> **Note (2026-02-09):** The parser library selection was the most critical decision in
> the port but was documented separately rather than in this log. See
> [Library Choices -- Parser Selection Decision](flowmark-port-library-choices.md#parser-selection-decision)
> for the full evaluation of comrak vs pulldown-cmark vs markdown-rs, selection rationale,
> and consequences.

---

## D9: Error Handling Strategy

**Date:** 2025-11-02 | **Impact:** Low

> **Note (2026-02-09):** This decision was not recorded during the original port.
> Reconstructed from the implementation for completeness.

### Context

Needed to choose an error handling approach for a CLI tool that processes Markdown files.

### Decision

**`anyhow` for the CLI, `thiserror` for the library.** Application-level errors use
`anyhow::Result` for convenience. Library-level errors use `thiserror`-derived enums for
type safety.

### Consequences

- **Good:** Standard Rust pattern. Clean separation between library and application error
  handling.
- **Good:** `anyhow` provides context chaining (`.context("reading input file")`) which
  improves error messages for users.

### Alternatives Considered

- **`anyhow` everywhere** (no typed errors in the library): Rejected because it loses
  type safety for library consumers who may want to match on specific error variants.
- **Custom error enums without `thiserror`**: Rejected as unnecessary boilerplate;
  `thiserror` generates the same code with less maintenance burden.

### Lessons

- For CLI tools, `anyhow` + `thiserror` is the default choice unless you have specific
  reasons to do otherwise.

---

## D10: String Ownership Strategy

**Date:** 2025-11-02 | **Impact:** Medium

> **Note (2026-02-09):** This decision was not recorded during the original port.
> Reconstructed from the implementation for completeness.

### Context

Python strings are immutable and reference-counted. Rust requires explicit ownership
decisions for string data passed between functions and stored in data structures.

### Decision

**Owned `String` types throughout, with `&str` borrows for read-only access.** The
post-processing pipeline takes `&str` and returns `String`. AST nodes use comrak's
arena-allocated strings.

### Consequences

- **Good:** Simple ownership model. No lifetime complexity in the post-processing
  pipeline.
- **Neutral:** Some unnecessary allocations compared to a `Cow<str>` approach, but
  performance is not a bottleneck for this tool.

### Lessons

- **Start with owned types.** For a port, simplicity of ownership beats micro-optimization.
  You can always switch to borrowed types later if profiling shows allocation overhead.
- **Match the Python mental model.** Python developers think in owned values. Starting
  with `String` makes the port more straightforward.

### Alternatives Considered

- **`Cow<'a, str>` throughout** for zero-copy where possible: Rejected because the
  lifetime complexity was not justified; profiling showed no allocation bottleneck.
- **`&str` with explicit lifetimes**: Rejected because tying output lifetimes to input
  lifetimes made the post-processing pipeline unwieldy and hard to compose.

---

## D2: Workspace vs Single Package

**Date:** 2025-11-02 (initial) / 2025-11-03 (changed) | **Impact:** Medium

### Context

Initial setup used a Cargo workspace with two crates:
- `flowmark-core` (library)
- `flowmark-cli` (binary)

This followed the recommended pattern in our best practices doc.

### Decision

**Consolidated to a single package** with feature flags for CLI-only dependencies.

### Consequences

- **Good:** Simpler build, simpler CI, fewer path issues in tests. Integration tests
  could access both library and CLI code directly.
- **Good:** Feature flags cleanly separate library from CLI dependencies.
- **Neutral:** Slightly larger library binary (includes CLI deps if default features
  used), mitigated by non-default features.

### Lessons

- **Single package is right for small-to-medium projects.** The workspace pattern
  adds complexity that isn't justified until you have multiple distinct crates with
  different dependency sets and independent versioning needs.
- **Feature flags are sufficient** for separating CLI from library concerns.
- **Start simple, split later.** You can always extract a workspace later if needed.

### Alternatives Considered

- **Keep the Cargo workspace** with separate `flowmark-core` and `flowmark-cli` crates:
  Rejected after experiencing path issues in tests and unnecessary build complexity. The
  workspace pattern is better suited to larger projects with independent versioning needs.

---

## D3: Escape Handling Strategy

**Date:** 2025-11-02 | **Impact:** High

### Context

Comrak and marko handle character escaping differently. Comrak adds escapes that marko
doesn't (e.g., `\_`, `\<`, `\#`) and removes escapes that marko preserves (e.g., `\-`,
`\$`, `\[`).

### Decision

**Post-processing pipeline** -- a chain of `fix_*` functions applied after comrak
rendering to match Python's escape handling.

### Consequences

- **Good:** 14 of 17 behavioral differences resolved. The post-processing approach is
  flexible and each fix is independent.
- **Bad:** Post-processing can't restore information lost during parsing (e.g., `\-`
  is removed by comrak's parser, not its renderer, so it can't be recovered).
- **Maintenance cost:** 14 workaround functions that must be tested and maintained.

### Lessons

- **Post-processing is the pragmatic choice** for most parser differences. It's easier
  to fix rendered output than to modify parser input.
- **Pre-processing is needed** when the parser destroys information. The fence list
  marker bug and unreferenced footnotes both required pre-processing.
- **Some differences are truly unfixable** without forking the library. Accept these
  and document them clearly.

### Alternatives Considered

- **Fork comrak** and fix escape handling at the parser level: Rejected because
  maintaining a fork is a long-term burden, and most differences were fixable via
  post-processing without modifying the parser.
- **Pre-processing only** (rewrite input before parsing): Rejected as the primary
  strategy because pre-processing is riskier (modifies parser input) and can't address
  differences that arise during rendering. Used selectively for 2 specific cases.

---

## D4: Cross-Validation Methodology

**Date:** 2025-11-02 | **Impact:** High

### Context

Needed a systematic way to verify that Rust output matches Python output for all inputs.

### Decision

**Automated cross-validation script** that:
1. Builds the Rust binary
2. Runs both Python and Rust against all test fixtures
3. Diffs the outputs
4. Reports pass/fail for each fixture

### Consequences

- **Good:** Caught every parser difference that unit tests missed. Essential for
  achieving byte-for-byte parity.
- **Good:** Served as the acceptance gate -- port wasn't "done" until cross-validation
  passed.
- **Required:** Python repo as a git submodule for the script to work.

### Lessons

- **Cross-validation is non-negotiable** for any port that requires behavioral parity.
  Unit tests alone will miss differences that only show up with complex real-world input.
- **Use real documents as test fixtures**, not just synthetic test cases.
- **Run cross-validation frequently** during development, not just at the end.

### Alternatives Considered

- **Unit tests only** (no cross-validation): Rejected because unit tests with synthetic
  inputs missed behavioral differences that only appeared with complex real-world
  documents. Cross-validation caught every one of these.
- **Manual spot-checking** against Python output: Rejected because it is not repeatable,
  not scalable, and misses regressions when workarounds interact.

---

## D5: Handling Python Bugs Found During Porting

**Date:** 2025-11-03 | **Impact:** Medium

### Context

Cross-validation revealed that Python had inconsistent behavior in two areas:
1. No blank line after headings (inconsistent spacing)
2. Blank lines between ALL list items (even flat lists)

### Decision

**Accepted intentional divergences** where Rust behavior is more systematic.
Documented as "Rust is more consistent" rather than replicating the Python quirks.

### Consequences

- **Good:** Rust's behavior is cleaner and follows Markdown conventions better.
- **Risk:** Test parity is not 100% byte-for-byte for these specific cases.
- **Mitigation:** Documented clearly, could add `--python-compat` flag in future.

### Lessons

- **Porting reveals bugs in the original.** The process of writing exact-match tests
  against Python behavior found inconsistencies that were likely bugs.
- **You must decide: replicate the bug or fix it.** For flowmark, fixing was the right
  call because the Rust behavior is objectively more consistent.
- **Document every intentional divergence.** Future developers need to know these are
  choices, not bugs.

### Alternatives Considered

- **Replicate Python's bugs exactly** for byte-for-byte parity: Rejected because Rust's
  behavior is objectively more consistent (e.g., always adding a blank line after
  headings). Replicating known bugs would make the Rust version worse for users.
- **Add a `--python-compat` flag** to toggle bug-compatible behavior: Deferred to future
  work. Not worth the complexity for the initial port, but remains an option if exact
  parity becomes a requirement.

---

## D6: Comrak Fence Parsing Bug

**Date:** 2025-11-03 | **Impact:** High

### Context

Discovered a bug in comrak where fenced code blocks containing YAML-style indented lists
with blank lines (indentation >= 4 spaces) are incorrectly parsed. The fence closes
prematurely and content leaks out.

### Decision

**Pre-processing workaround**: escape list markers inside fenced code blocks before
passing to comrak, then un-escape after rendering.

### Consequences

- **Good:** Workaround is effective and isolated to one function.
- **Bad:** Pre-processing is fragile -- it has to correctly identify content inside
  fences without parsing Markdown (bootstrap problem).
- **Filed:** Bug report documented in `flowmark-port-comrak-bug.md`.

### Lessons

- **Library bugs are a fact of life.** Even well-maintained libraries have bugs.
- **Pre-processing can work** but is riskier than post-processing because you're
  modifying input before the parser sees it.
- **Document bugs thoroughly.** The bug report serves double duty: it helps the library
  maintainer and documents the workaround for your team.
- **Consider vendoring** for critical bugs. Having a patched local copy is sometimes
  better than a fragile workaround.

### Alternatives Considered

- **Vendor/fork comrak** and fix the fence parsing bug at the source: Rejected for the
  initial port because maintaining a fork is a long-term burden for a single bug. Would
  reconsider if more parser-level bugs accumulate.
- **Accept the bug** and document it as an unfixable difference: Rejected because the bug
  affected real-world documents (YAML in fenced code blocks is common). The pre-processing
  workaround was effective enough.

---

## D7: Wrapping Algorithm Approach

**Date:** 2025-11-02 | **Impact:** Medium

> **Revision note (2026-02-09):** This entry describes the hybrid approach developed
> during the initial port (comrak joins lines via a large `render.width`, custom code
> handles sentence-aware wrapping, `hardbreaks = true` preserves the result). The
> approach later evolved into a simpler configuration-based solution using comrak's
> built-in `render.width` with `hardbreaks = false`, documented in
> [Wrapping Solution](flowmark-port-wrapping-solution.md). The simpler approach
> lets comrak handle basic line wrapping directly, while the hybrid approach described
> here remains relevant for advanced sentence-aware semantic wrapping.

### Context

Needed to match Python's line wrapping behavior: join consecutive lines in paragraphs,
re-wrap to specified width, preserve structure.

Initial approach was complex AST transformations.

### Decision

**Hybrid approach**: use comrak's `render.width` for line joining (with a large width of
999999 so comrak joins but does not wrap), then apply custom sentence-aware paragraph
wrapping via `wrap_paragraphs()` in the AST, then render with `hardbreaks = true` to
preserve the custom line breaks.

### Consequences

- **Good:** Comrak's line joining eliminated the need to manually handle soft breaks.
  Setting `render.width` to a very large value causes comrak to join consecutive lines
  in paragraphs, which is the first step of rewrapping.
- **Complex:** Custom wrapping logic (~240 lines in `paragraph_wrapping.rs`) was still
  needed for sentence-based semantic wrapping, indent-aware width calculation, and
  cross-arena AST node cloning. This was more complex than initially expected.
- **Good:** `hardbreaks = true` during final rendering preserves the line breaks
  created by the custom wrapper, preventing comrak from re-joining them.

### Lessons

- **Library features are building blocks, not complete solutions.** Comrak's
  `render.width` handled line joining but not the semantic wrapping flowmark requires.
  The final solution is a hybrid of library and custom code.
- **Check how a library's options interact.** The interplay between `render.width`,
  `hardbreaks`, and parse-time vs render-time options required careful tuning.

### Alternatives Considered

- **Pure AST transformation** (rewrite paragraph nodes in the tree): Rejected as the
  initial approach because it was too complex -- comrak's arena-based AST makes node
  manipulation verbose, and handling all edge cases (quotes, lists, nested structures)
  required extensive code.
- **Pure `render.width`** (let comrak handle all wrapping): This simpler approach was
  later adopted for basic wrapping (see
  [Wrapping Solution](flowmark-port-wrapping-solution.md)), but was initially
  insufficient because comrak's built-in wrapping is not sentence-aware.

---

## D8: Edition 2024 (Rust 1.85+)

**Date:** 2025-11-02 | **Impact:** Low

### Context

Choosing between Rust editions 2021 and 2024 for the project.

### Decision

**Edition 2024** with MSRV 1.85.

### Consequences

- **Good:** Access to `std::sync::LazyLock` (eliminated `once_cell` dependency).
  Modern language features and improved ergonomics.
- **Good:** Future-proof -- new projects should use the latest edition.
- **Risk:** Some CI environments might not have Rust 1.85+ yet (mitigated: explicit
  MSRV in Cargo.toml and CI check).

### Lessons

- **Use the latest edition for new projects.** The benefits of modern features outweigh
  the minor compatibility risk.
- **Always declare MSRV** in Cargo.toml and test it in CI.

### Alternatives Considered

- **Edition 2021** for broader CI and toolchain compatibility: Rejected because it would
  require the `once_cell` crate for lazy statics (Edition 2024 provides
  `std::sync::LazyLock` in std) and miss other ergonomic improvements. The compatibility
  risk was mitigated by declaring an explicit MSRV.

---

## Pitfall Rankings

| Pitfall | Impact | Avoidable? | How |
| --- | --- | --- | --- |
| Parser behavioral differences | Critical | Partially | Cross-validate in research phase |
| Parser bugs (fence parsing) | High | No | Workaround or vendor |
| Escape handling differences | High | Partially | Budget time for workarounds |
| Python bugs discovered | Medium | No | Decide to replicate or fix |
| Workspace complexity | Low | Yes | Start with single package |
| Regex anchoring differences | Low | Yes | Add `^` to all `re.match()` patterns |

---

## Phase-by-Phase Tactics

### Phase 1: Background Research (~30 min)

**What worked:**
- Writing a best-practices doc first (`rust-cli-best-practices.md`). Forced a survey of
  the Rust CLI ecosystem before writing any code.
- Evaluating 3 Markdown parsers with a feature matrix before committing. The matrix
  revealed that pulldown-cmark lacked robust footnotes.
- Using Claude Code for research. Web searches + document synthesis produced a
  comprehensive 730-line best practices guide efficiently.

**What we'd do differently:**
- More cross-validation in research phase. Would test candidate parsers against actual
  flowmark inputs, not just check feature lists.

### Phase 2: Planning (~30 min)

**What worked:**
- Comprehensive migration plan (200+ lines covering feature parity matrix, architecture
  decisions, and library selection justification).
- Feature parity matrix listing every Python feature mapped to the Rust library.
- Single-process approach decision. For a project this size (~2,000 lines Python app code), porting
  everything at once was the right call.

**What we'd do differently:**
- Include a "known risks" section specifically calling out parser library behavioral
  differences as the #1 risk.

### Phase 3: Initial Implementation (~2-3 hours)

**What worked:**
- Test-driven development. Progress was measurable: 2/45 → 45/45 → 87/87 → 111/111.
- Module-by-module porting order: core data types → leaf modules → integration modules
  → CLI last.
- Maintaining function name parity with Python for traceability.
- `include_str!()` for test fixtures (compile-time embedding, no path issues).
- `LazyLock` for compiled regex (Edition 2024, eliminated `once_cell`).

**Key implementation patterns:**
1. Arena-based AST with closures (`with_markdown_ast<F, R>`)
2. Visitor pattern for AST traversal (`walk_ast`)
3. Post-processing pipeline of `fix_*` functions

**What we'd do differently:**
- Start with a single package, not workspace. Single package is simpler for projects
  this size.

### Phase 4: Bug-Fixing & Parity (~2-3 hours)

Most painful phase and source of the most important lessons. See
[Library Choices](flowmark-port-library-choices.md) for the full workaround table.

**Systematic approach:**
1. Run all tests, categorize failures: parser difference / porting bug / Python bug
2. For each parser difference: can we pre-process? post-process? or is it unfixable?
3. Track everything with `XXX:` comments in the code

**Python bugs discovered** during cross-validation:
- Inconsistent heading spacing (no blank line after headings)
- Inconsistent list item spacing (blanks between all items)
- Documented as intentional divergences where Rust is more systematic.

### Phase 5: Refinement

- Cross-validation script for systematic comparison against Python
- Comprehensive documentation of all differences and workarounds
- Version tracking between Python and Rust versions
- CI/CD pipeline with format, clippy, test, and security checks

## Key Metrics

| Metric | Value |
| --- | --- |
| Total development time | ~5-6 hours |
| Implementation time | ~2-3 hours |
| Bug-fixing time | ~2-3 hours (50% of total!) |
| Tests ported | 111 (100% passing) |
| Parser workarounds | 17 total (14 fixable, 3 unfixable) |
| Performance improvement | 20-40x over Python |
| Binary size | ~2.5MB (stripped) |
| Startup time | <10ms |
| Lines of Python (app) | ~2,000 |
| Lines of Python (tests) | ~1,500 |
| Lines of Rust (app) | ~3,400 |
| Lines of Rust (tests) | ~2,900 (1,600 inline + 1,300 integration) |
| Rust/Python app code ratio | ~1.7x |

## Summary of Key Tactics

1. **Research before coding.** Spend 30-60 min on ecosystem research. Write it down.
2. **Plan comprehensively.** Feature matrix, library evaluation, architecture decisions.
3. **Port tests first.** TDD ensures you know when you're done.
4. **Port leaf modules first, integration modules last, CLI last.**
5. **Expect parser differences.** Budget 50% of time for workarounds.
6. **Use post-processing liberally.** A chain of `fix_*` functions is practical.
7. **Document everything with `XXX:` comments.**
8. **Accept unfixable differences.** Document them clearly, move on.
9. **Cross-validate continuously.** Run both implementations, diff outputs.
10. **Keep the Rust version cleaner where it makes sense.** Matching Python bugs
    verbatim isn't always the right call.
