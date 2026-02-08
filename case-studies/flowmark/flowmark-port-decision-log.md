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

- **Good:** 12 of 15 escape differences resolved. The post-processing approach is
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

---

## D7: Wrapping Algorithm Approach

**Date:** 2025-11-02 | **Impact:** Medium

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
- Single-process approach decision. For a project this size (~800 lines Python), porting
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
| Parser workarounds | 14 (12 fixable, 3 unfixable) |
| Performance improvement | 20-40x over Python |
| Binary size | ~2.5MB (stripped) |
| Startup time | <10ms |
| Lines of Rust | ~4,400 |
| Lines of tests | ~1,260 |

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
