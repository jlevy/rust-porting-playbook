# Feature: Fix All Issues from Comprehensive Playbook Review

**Date:** 2026-02-08 (last updated 2026-02-08)

**Author:** Senior Engineering Review (automated)

**Status:** Draft

**Review beads:** rpp-1e8z (epic), rpp-yev4 through rpp-z8kz (22 review tasks, all closed)

## Overview

Comprehensive fix plan for all issues identified during senior engineering review of the
21 documents in the Rust Porting Playbook. Findings are organized by severity (CRITICAL
first), then grouped by theme for efficient batch implementation.

## Goals

- Fix every factual error, deprecated recommendation, and non-compiling code example
- Resolve all cross-document contradictions and inconsistent numbers
- Add missing but important technical guidance
- Improve clarity for AI agents following the playbook

## Non-Goals

- Restructuring the 3-layer documentation architecture (it's sound)
- Adding entirely new documents (only fixing/improving existing ones)
- Changing the 8-phase methodology (it's well-designed)

---

## Implementation Plan

### Phase 1: CRITICAL — Factual Errors That Will Break Users

These issues will cause broken builds, wrong dependencies, or silent bugs if followed
as-written. Fix all of these first.

---

#### 1.1 Replace `serde_yaml` with `serde_yaml_ng` everywhere

`serde_yaml` was archived by dtolnay in March 2024. Its final version is literally
`0.9.34+deprecated`. The fork `serde_yml` has a RustSec advisory (RUSTSEC-2025-0068).
The community replacement is `serde_yaml_ng`.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` line 136: Change
  `PyYAML | serde_yaml | Good | Check maintenance status` to
  `PyYAML | serde_yaml_ng | Good | serde_yaml is archived; use serde_yaml_ng 0.10+`

- [ ] `reference/python-to-rust-playbook.md` line 46: Change
  `pyyaml | YAML parsing | serde_yaml | Low` to
  `pyyaml | YAML parsing | serde_yaml_ng | Low`

- [ ] `reference/python-to-rust-mapping-reference.md` line 555: Change
  `PyYAML | serde_yaml 0.9 | Good | Used for config/frontmatter` to
  `PyYAML | serde_yaml_ng 0.10+ | Good | serde_yaml is archived`

- [ ] `reference/python-to-rust-porting-guide.md`: Search for any `serde_yaml`
  references and update

- [ ] `reference/python-to-rust-playbook.md` Phase 3 example line 208: Change
  `YAML config loading | config.py | serde_yaml | Planned` to
  `YAML config loading | config.py | serde_yaml_ng | Planned`

---

#### 1.2 Fix `resolver = "2"` to `resolver = "3"` for Edition 2024

Edition 2024 introduces resolver v3 (MSRV-aware dependency resolution), which is a
flagship feature. Using `resolver = "2"` is wrong for Edition 2024 workspaces.

**Files to change:**

- [ ] `guidelines/rust-project-setup.md` line 79: Change `resolver = "2"` to
  `resolver = "3"`

- [ ] `reference/rust-cli-best-practices.md`: Search for `resolver` references and
  update

- [ ] Any case study files that reference workspace resolver

---

#### 1.3 Fix non-compiling `build.rs` code in porting guide

The version tracking code in `reference/python-to-rust-porting-guide.md` has multiple
compilation errors:

**Error 1** (line 56-57): `env!("CARGO_PKG_METADATA_PYTHON_SOURCE_VERSION", "unknown")`
— `CARGO_PKG_METADATA_*` environment variables do not exist in Cargo. The `env!` macro's
second argument is an error message, not a default value.

**Error 2** (line 61-66): `concat!()` cannot accept `const` variables, only literals and
other macros like `env!()`.

**Error 3** (line 89-91): `.or_else()` on `Result<String, io::Error>` receives a closure
returning `Option<String>` (from `.ok().and_then()`), which is a type mismatch.

**Files to change:**

- [ ] `reference/python-to-rust-porting-guide.md` lines 54-71: Replace the `const
  PYTHON_VERSION` + `concat!` approach with a working `build.rs` pattern using
  `println!("cargo:rustc-env=...")` and then `env!("PYTHON_SOURCE_VERSION")` in the
  binary

- [ ] `reference/python-to-rust-porting-guide.md` lines 76-100: Fix the `build.rs`
  example — the `.or_else()` chain should use `.unwrap_or_else()` consistently, and
  add `println!("cargo:rerun-if-changed=python-source")` for correctness

- [ ] `guidelines/rust-cli-app-patterns.md` lines 319-324: The `concat!(env!(...),
  env!(...))` pattern here is correct but the `PYTHON_SOURCE_VERSION` env var it
  references needs to come from a working `build.rs` — add a comment pointing to
  the build.rs pattern

---

#### 1.4 Fix Pitfall #6 — identical WRONG and CORRECT examples

In `guidelines/python-to-rust-porting-rules.md` lines 248-257, the WRONG and CORRECT
examples show the identical path `project-rs/tests/test_format.rs`, making the pitfall
impossible to understand.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` lines 248-257: Differentiate the
  paths clearly:
  ```
  // WRONG: tests/ at workspace root, outside any member crate
  my-workspace/tests/test_format.rs

  // CORRECT: tests/ inside a specific crate
  my-workspace/crates/core/tests/test_format.rs
  ```

---

#### 1.5 Fix `assert` → `debug_assert!` — dangerous default

In both `guidelines/python-to-rust-porting-rules.md` (line 69) and
`reference/python-to-rust-mapping-reference.md` (line 148), Python `assert` is mapped
to `debug_assert!` as the primary recommendation. `debug_assert!` is stripped from
release builds, silently removing runtime checks.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` line 69: Split the row:
  `assert (invariant) | debug_assert! | Only for debug-only invariants` and
  `assert (validation) | explicit Result-based check | Default for porting`

- [ ] `reference/python-to-rust-mapping-reference.md` line 148: Change
  `debug_assert_eq!(x, y) | Not for production checks` to
  `assert_eq!(x, y) | debug_assert_eq! only for hot-path invariants`

---

#### 1.6 Fix version constraint mappings (swapped)

In `reference/python-to-rust-mapping-reference.md`:

- Line 339: `~=1.4` maps to `"~1.4"` — WRONG. Python `~=1.4` means `>=1.4, <2.0`.
  Cargo `~1.4` means `>=1.4, <1.5`. The correct mapping is `"1.4"` (caret).
- Line 340: `==1.4.*` maps to `"1.4"` — WRONG. Python `==1.4.*` means `>=1.4, <1.5`.
  The correct mapping is `"~1.4"` (tilde).

The two rows are swapped.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` lines 339-340: Swap the Cargo
  equivalents: `~=1.4` → `"1.4"` (caret) and `==1.4.*` → `"~1.4"` (tilde)

---

#### 1.7 Fix `actions/create-release@v1` — archived action

In `guidelines/rust-project-setup.md` line 392, `actions/create-release@v1` is used.
This action was archived by GitHub. The replacement is `softprops/action-gh-release@v2`
or `ncipollo/release-action@v1`.

**Files to change:**

- [ ] `guidelines/rust-project-setup.md` lines 390-398: Replace
  `actions/create-release@v1` with `softprops/action-gh-release@v2`

- [ ] `reference/rust-cli-best-practices.md`: Same fix if this action appears

---

#### 1.8 Fix comrak `CowStr` type name — wrong library

In `guidelines/python-to-rust-porting-rules.md` lines 243-245, the comment says
`NodeValue::Text` might be `CowStr`. `CowStr` belongs to `pulldown-cmark`, not comrak.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` lines 243-245: Replace with accurate
  version history:
  ```rust
  // comrak NodeValue::Text: Vec<u8> (pre-0.4), String (0.4-0.44),
  // Cow<'static, str> (0.45+). pulldown-cmark uses CowStr (different API).
  // Always verify against your Cargo.lock version.
  ```

---

#### 1.9 Fix `dict` → `HashMap` — missing insertion-order warning

Python `dict` preserves insertion order since 3.7. `HashMap` does not. This is the most
common source of subtle bugs in Python→Rust ports.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` line 49: Add note:
  `HashMap<K, V> | **No insertion order!** Use IndexMap if order matters`

- [ ] `reference/python-to-rust-mapping-reference.md` line 31: Same fix plus add
  `IndexMap` to notes

---

#### 1.10 Fix wrapping solution / decision log contradiction

`case-studies/flowmark/flowmark-port-wrapping-solution.md` describes
`hardbreaks=false` + `width=target` ("simple config change"). The decision log D7
describes `hardbreaks=true` + `width=999999` + ~240 lines custom code. These are
mutually exclusive.

**Files to change:**

- [ ] `case-studies/flowmark/flowmark-port-decision-log.md` D7 section: Update to
  reflect the actual final implementation, or add a dated revision note explaining
  the evolution from one approach to the other

- [ ] `case-studies/flowmark/flowmark-port-wrapping-solution.md`: Add a note if D7
  describes a superseded approach

---

#### 1.11 Fix workaround count inconsistencies across case studies

The workaround/issue counts differ across documents: 13, 14, 15, and 17 appear in
different places for the same metrics.

**Files to reconcile:**

- [ ] `case-studies/flowmark/flowmark-port-decision-log.md` lines 70, 74, 344: Make
  counts internally consistent (e.g., "15 differences found, 12 fixed, 3 accepted")

- [ ] `case-studies/flowmark/flowmark-port-cross-validation.md` line 176: Align with
  decision log numbers

- [ ] `case-studies/flowmark/flowmark-port-library-choices.md`: Align counts

- [ ] `case-studies/flowmark/flowmark-port-analysis.md`: Align counts

- [ ] `README.md` line 108: Verify "14 library workarounds, 3 accepted differences"
  matches the reconciled canonical numbers

---

#### 1.12 Fix `main()` error handling contradiction

In `guidelines/rust-cli-app-patterns.md` lines 172-183, `main()` returns
`color_eyre::Result<()>` but then manually catches errors with `if let Err(e)` and
calls `process::exit(1)`. If main returns Result, the error is already reported by
the Result return. These are two conflicting patterns mixed together.

**Files to change:**

- [ ] `guidelines/rust-cli-app-patterns.md` lines 169-183: Choose one pattern:
  Either `fn main() -> Result<()>` (let eyre report errors) OR
  `fn main()` with manual error handling. Don't mix both.

---

### Phase 2: CRITICAL — Missing Content That Causes Confusion

---

#### 2.1 Add Edition 2024 actual changes

Multiple documents claim "Edition 2024 focus" but none describe the actual breaking
changes. Engineers porting to Edition 2024 need to know these.

**Files to change:**

- [ ] `guidelines/rust-general-rules.md` after line 28: Add subsection on Edition 2024
  changes:
  - `gen` is a reserved keyword (rename Python `gen` variables)
  - `unsafe_op_in_unsafe_fn` is deny-by-default
  - RPIT (return-position impl Trait) captures all in-scope lifetimes by default
  - `static mut` is soft-deprecated (use `std::sync::Mutex` or atomics)
  - Let chains in `if`/`while` are stable

- [ ] `guidelines/python-to-rust-porting-rules.md`: Add Edition 2024 note about `gen`
  keyword reservation in Key Pitfalls section

---

#### 2.2 Replace `once_cell` with `std::sync::LazyLock` everywhere

Since the playbook targets Rust 1.85+, `LazyLock` (stable since 1.80) is in stdlib.
`once_cell` is no longer needed.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 295: Change
  `@pytest.fixture | Setup in test function or once_cell` to
  `@pytest.fixture | Setup in test function or LazyLock`

- [ ] `reference/python-to-rust-mapping-reference.md` line 420: Same

- [ ] `reference/python-to-rust-porting-guide.md`: Search for `once_cell` and replace
  with `std::sync::LazyLock`

- [ ] `guidelines/rust-general-rules.md` line 111: Already mentions LazyLock but says
  "Older code may use once_cell::sync::Lazy" — tighten this to recommend removing
  the once_cell dependency

---

#### 2.3 Add `Cow<'_, str>` to type mappings

The main porting rules guide (`guidelines/python-to-rust-porting-rules.md`) omits
`Cow<'_, str>` from its type mapping table, despite this being essential for
text-processing ports.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` after line 42: Add row:
  `str (sometimes modified) | Cow<'_, str> | Avoids allocation when input unchanged`

---

#### 2.4 Add regex `re.search()` and `re.fullmatch()` mappings

The regex pitfall only covers `re.match()`. Engineers will also encounter `re.search()`
(which needs NO anchor — same as Rust) and `re.fullmatch()` (which needs both `^` and
`$`).

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` lines 183-196: Expand to cover:
  - `re.match(pat)` → prepend `^` (or `\A` for multiline safety)
  - `re.search(pat)` → use pattern as-is (both unanchored)
  - `re.fullmatch(pat)` → wrap with `^...$` (or `\A...\z`)

- [ ] `reference/python-to-rust-mapping-reference.md` line 214: Fix — `re.match()`
  doesn't map to `is_match()` when the Python code uses groups. Add
  `regex.captures(s)` for when Match object fields are accessed.

- [ ] `reference/python-to-rust-mapping-reference.md` line 217: Fix — `find_iter()`
  returns `Vec<Match>`, not `Vec<&str>`. Correct to:
  `regex.find_iter(s).map(|m| m.as_str()).collect::<Vec<_>>()`

---

#### 2.5 Add `match command.as_str()` pattern

In `reference/python-to-rust-mapping-reference.md` lines 92-98, `match command { "quit"
=> ... }` won't compile if `command` is `String`. Need `match command.as_str()`.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 93: Change to
  `match command.as_str() {` and add a comment explaining String vs &str in match

---

### Phase 3: IMPORTANT — Wrong or Misleading Guidance

---

#### 3.1 Fix "byte-for-byte" parity contradiction

`guidelines/python-to-rust-porting-rules.md` states "Byte-for-byte output matching is
the acceptance criterion" (line 18) but the Strategy Matrix (lines 281-287) says to
accept cosmetic differences. These contradict each other.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` line 18: Reword to:
  "Byte-for-byte output matching is the *goal*; any deviation must be explicitly
  documented, justified, and tracked. (See Strategy Matrix for handling unavoidable
  differences.)"

- [ ] `reference/port-checklist-initial-template.md` lines 17-19: Soften the completion
  gate similarly — "byte-for-byte matching with documented exceptions"

---

#### 3.2 Add `thiserror` / `anyhow` to dependency mappings

The porting rules mention `Result<T, E>` with custom error enums but omit the two most
established error-handling crates in the Rust ecosystem.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` after line 68: Add to the dependency
  mapping table:
  `Exception classes | thiserror (library) / anyhow (binary) | Excellent |`

---

#### 3.3 Fix `XXX:` comment convention — non-standard

`XXX:` is not recognized by most IDE tools, linters, or CI grep patterns by default.
Standard markers are `TODO:`, `FIXME:`, `HACK:`.

**Files to change (multiple):**

- [ ] `guidelines/python-to-rust-porting-rules.md` lines 291-296: Change `XXX:` to
  `HACK:` or `WORKAROUND:` for library workarounds, `FIXME:` for items needing
  future resolution. If `XXX:` is kept, add a note defining it and explaining IDE
  configuration needed.

- [ ] `reference/python-to-rust-playbook.md` lines 358-362, 425-430: Same change

- [ ] All case study files referencing `XXX:` comments

---

#### 3.4 Fix `frozenset` note — misleading

`reference/python-to-rust-mapping-reference.md` line 33 says `frozenset` maps to
`HashSet<T>` "(immutable by default)". Rust `HashSet` is mutable with `let mut`.
Python `frozenset` is genuinely immutable at the type level and is hashable.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 33: Change note to:
  "Immutability via `let` binding, not the type. For use as hash key, need newtype
  implementing Hash"

---

#### 3.5 Fix `str.find()` — returns byte offset, not char index

`reference/python-to-rust-mapping-reference.md` line 203: Python `str.find()` returns a
character index; Rust `str::find()` returns a byte offset.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 203: Add note:
  "Returns byte offset, not char index! Different for non-ASCII"

---

#### 3.6 Fix effort table percentages

`reference/python-to-rust-playbook.md` effort table (lines 554-563): Percentages sum to
105% (5+10+5+5+35+35+10=105).

**Files to change:**

- [ ] `reference/python-to-rust-playbook.md` lines 554-563: Adjust percentages to sum
  to 100%. Likely reduce Phase 5 and 6 to 30% each, or reduce research to 8%.

---

#### 3.7 Fix `actions/checkout@v5` — should be v6

GitHub Actions `actions/checkout@v5` is used throughout but v6 is current.

**Files to change:**

- [ ] `guidelines/rust-project-setup.md`: Update all `actions/checkout@v5` to
  `actions/checkout@v6`

- [ ] `guidelines/test-coverage-for-porting.md` line 221: Same (currently `@v4`)

---

#### 3.8 Fix `color-eyre` status

`color-eyre` 0.6 is on maintenance-only status (author is no longer actively developing
new features). While still functional, this should be noted.

**Files to change:**

- [ ] `guidelines/rust-general-rules.md` line 79: Add note about maintenance status

- [ ] `guidelines/rust-cli-app-patterns.md` line 172: Add note

---

#### 3.9 Add `Callable` → three Rust function traits explanation

`reference/python-to-rust-mapping-reference.md` line 51: `Callable[[A], B]` maps to
`Fn(A) -> B` but doesn't explain `FnMut` and `FnOnce`.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 51: Expand to show:
  - `Fn` — no mutation of captures, callable repeatedly (most Python callbacks)
  - `FnMut` — mutates captures (closures modifying outer state)
  - `FnOnce` — consumes captures, callable once (ownership transfer)

---

#### 3.10 Fix `TypedDict` coupling with serde

`reference/python-to-rust-mapping-reference.md` line 49: `TypedDict` maps to
"Struct with `serde::Deserialize`" but serde is only needed for deserialization.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 49: Change to:
  "Struct with named fields. Add serde derives only if deserializing from data formats"

---

#### 3.11 Note `Protocol` structural vs nominal difference

`reference/python-to-rust-mapping-reference.md` line 48: Python `Protocol` is structural
(implicit satisfaction); Rust `trait` is nominal (explicit `impl` required).

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 48: Add note:
  "Rust traits are nominal — must write explicit `impl Trait for Type`"

---

#### 3.12 Fix `ring` license hash in `deny.toml`

`guidelines/rust-project-setup.md` line 320: The `ring` license hash
`0xbd0eed23` is version-specific and will go stale on the next `ring` update.

**Files to change:**

- [ ] `guidelines/rust-project-setup.md` lines 317-320: Add a comment:
  `# IMPORTANT: hash is version-specific; update after cargo update`

---

#### 3.13 Fix comrak version pinning — v0.29 is extremely stale

`case-studies/flowmark/flowmark-port-migration-plan.md` references comrak 0.29. Current
comrak is 0.50+. The API has changed significantly (Text type, plugin system, etc.).

**Files to change:**

- [ ] `case-studies/flowmark/flowmark-port-migration-plan.md`: Add a dated note that
  the evaluation was done against comrak 0.29 and the library has evolved
  significantly since then

- [ ] `reference/python-to-rust-mapping-reference.md` line 553: Update
  `comrak 0.47` to note current version availability

---

### Phase 4: IMPORTANT — Missing Content That Should Be Added

---

#### 4.1 Add dunder methods → Rust traits table

This is the highest-value missing content in the mapping reference. Every class port
needs it.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` after line 283 (Classes section):
  Add a table mapping:
  - `__str__()` → `impl fmt::Display`
  - `__repr__()` → `#[derive(Debug)]`
  - `__eq__()`/`__ne__()` → `#[derive(PartialEq)]`
  - `__hash__()` → `#[derive(Hash)]` (requires `PartialEq + Eq`)
  - `__lt__()` etc. → `impl PartialOrd` / `impl Ord`
  - `__len__()` → `.len()` method
  - `__iter__()` + `__next__()` → `impl Iterator`
  - `__getitem__()` → `impl Index<Idx>`
  - `__add__()` etc. → `impl Add` from `std::ops`
  - `__enter__()`/`__exit__()` → `impl Drop` + RAII scope
  - `__contains__()` → `.contains()` method
  - `__bool__()` → no standard trait; use explicit method

---

#### 4.2 Add generators → iterators mapping

Python generators are extremely common and have no trivial Rust equivalent.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md`: Add section showing:
  - Simple generators → `impl Iterator<Item = T>` with closures
  - Stateful generators → struct implementing `Iterator` trait
  - `std::iter::from_fn` for simple cases
  - Mention `gen` blocks (experimental)

---

#### 4.3 Add context managers → RAII mapping with examples

`reference/python-to-rust-mapping-reference.md` line 147 mentions "Scope + `Drop`" but
gives no code example.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` after line 147: Add examples:
  - `with open(f) as fh:` → `std::fs::read_to_string(path)?` (RAII)
  - `with lock:` → `let _guard = mutex.lock().unwrap();`
  - Custom context managers → `impl Drop` or closure-based APIs

---

#### 4.4 Add `dataclasses` → struct-with-derives mapping

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md`: Add example showing
  `@dataclass` → `#[derive(Debug, Clone, PartialEq)]`, `frozen=True` → no `&mut self`
  methods, `order=True` → `#[derive(PartialOrd, Ord)]`

---

#### 4.5 Add `enum.Enum` → Rust enum mapping

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md`: Add example showing string enums
  with `strum` crate for `Display`/`FromStr` derives

---

#### 4.6 Add async patterns mapping

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md`: Add table:
  - `async def foo()` → `async fn foo()`
  - `await bar()` → `bar().await`
  - `asyncio.run(main())` → `#[tokio::main]`
  - `asyncio.gather(a, b)` → `tokio::join!(a, b)`

---

#### 4.7 Add parallelism patterns mapping

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md`: Add table:
  - `multiprocessing.Pool.map` → `items.par_iter().map` (rayon)
  - `threading.Thread` → `std::thread::spawn`
  - `concurrent.futures` → `rayon::ThreadPool` or `tokio::spawn`

---

#### 4.8 Add concurrency/async/logging dependency mappings to porting rules

`guidelines/python-to-rust-porting-rules.md` dependency table omits:
- `logging` → `tracing` / `log`
- `asyncio` → `tokio`
- `threading` → `std::thread` / `rayon`
- `subprocess` → `std::process::Command`

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` after line 147: Add these rows

---

#### 4.9 Add `insta` snapshot testing to test coverage docs

The `insta` crate is the standard for snapshot testing in Rust and is missing from
both test coverage documents.

**Files to change:**

- [ ] `guidelines/test-coverage-for-porting.md`: Add mention of `insta` for snapshot
  testing alongside golden test approach

- [ ] `reference/python-to-rust-test-coverage-playbook.md`: Same

---

#### 4.10 Add missing decision entries to flowmark decision log

The decision log is missing entries for:
- D1 (parser selection — covered in library-choices but should be cross-referenced)
- Error handling strategy
- String ownership strategy (String vs &str vs Cow)
- Arena-based AST pattern rationale

**Files to change:**

- [ ] `case-studies/flowmark/flowmark-port-decision-log.md`: Add note about
  missing D1 and cross-reference to library choices doc. Optionally add brief
  entries for error handling and string ownership decisions.

---

### Phase 5: SUGGESTION — Improvements for Clarity and Completeness

---

#### 5.1 Add file path cross-references alongside `tbd guidelines` references

The `tbd guidelines ...` references are tool-specific. Add file paths in parentheses.

**Files to change:**

- [ ] All `guidelines/*.md` files: Add `(guidelines/filename.md)` after each
  `tbd guidelines` reference

---

#### 5.2 Fix `for/else` mapping — show idiomatic iterator solution

`reference/python-to-rust-mapping-reference.md` line 109: "Use flag variable" is
un-idiomatic. The idiomatic Rust is `if let Some(item) = iter.find(|x| cond(x))`.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 109: Add the iterator
  solution alongside the flag variable option

---

#### 5.3 Add `clippy` quality gate to acceptance criteria

`guidelines/python-to-rust-porting-rules.md` acceptance criteria (lines 303-312) omits
`cargo clippy -- -D warnings`.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` after line 312: Add:
  `- [ ] cargo clippy -- -D warnings passes with zero warnings`

---

#### 5.4 Add derive guidance for ported structs

`guidelines/python-to-rust-porting-rules.md` line 145: `dataclasses → struct + derive
macros` but doesn't specify which derives.

**Files to change:**

- [ ] `guidelines/python-to-rust-porting-rules.md` line 145: Add note:
  "Minimum: `#[derive(Debug, Clone, PartialEq)]`; add `Eq`, `Hash`, `Serialize`,
  `Deserialize` as needed"

---

#### 5.5 Add `cargo-dist` as release alternative

`guidelines/rust-project-setup.md` line 369 dismisses cargo-dist. It has matured
significantly and should at least be mentioned as a valid alternative.

**Files to change:**

- [ ] `guidelines/rust-project-setup.md` line 369: Soften the dismissal — note
  cargo-dist as a simpler alternative for projects that don't need custom release
  workflows

---

#### 5.6 Add SIGPIPE handling guidance

Rust CLI tools need to handle SIGPIPE to avoid "broken pipe" panics when piped to
`head`, `less`, etc. This is missing from both CLI docs.

**Files to change:**

- [ ] `guidelines/rust-cli-app-patterns.md`: Add note about SIGPIPE handling:
  `#[cfg(unix)] unsafe { libc::signal(libc::SIGPIPE, libc::SIG_DFL); }` at the
  start of main, or use the `sigpipe` attribute (nightly)

- [ ] `guidelines/python-to-rust-cli-porting.md`: Note this as a CLI porting pitfall

---

#### 5.7 Add shell completions guidance

`clap_complete` for generating shell completion scripts is missing from CLI docs.

**Files to change:**

- [ ] `guidelines/rust-cli-app-patterns.md`: Add brief mention of `clap_complete`

- [ ] `reference/rust-cli-best-practices.md`: Add shell completions section

---

#### 5.8 Add `std::process::ExitCode` guidance

Modern Rust (1.61+) supports `fn main() -> ExitCode` as an alternative to
`process::exit()`. This is cleaner and allows destructors to run.

**Files to change:**

- [ ] `guidelines/rust-cli-app-patterns.md`: Add note about `ExitCode` as preferred
  pattern over `process::exit()`

---

#### 5.9 Fix `LineBreakMode::None` shadowing `Option::None`

`guidelines/rust-general-rules.md` line 135: `enum LineBreakMode { ..., None }` shadows
`Option::None` which causes confusing compiler errors.

**Files to change:**

- [ ] `guidelines/rust-general-rules.md` line 135: Rename to `NoBreaks` or `Off` with
  a comment explaining why `None` should not be used as an enum variant name

---

#### 5.10 Add `pytest.approx` → `approx` crate mapping

`reference/python-to-rust-mapping-reference.md` line 297: Manual
`(x - y).abs() < epsilon` is error-prone near zero. The `approx` crate provides
`assert_relative_eq!`.

**Files to change:**

- [ ] `reference/python-to-rust-mapping-reference.md` line 297: Add mention of the
  `approx` crate for `assert_relative_eq!` and `assert_abs_diff_eq!`

---

#### 5.11 Fix README statistics discrepancies

README says "141 tests" but the decision log references "111" in one place. The effort
estimate says "5-6 hours" in the README but "5-8 hours" in the playbook.

**Files to change:**

- [ ] `README.md` lines 105-108: Verify all statistics against the canonical source
  (likely the decision log and reconcile). Ensure "5-6 hours" vs "5-8 hours" is
  consistent or explained (one is agent-time, other includes human review).

---

#### 5.12 Add rejected alternatives to decision log

The decision log has no "Rejected Alternatives" section for any decision. This is the
most valuable missing content for future porters.

**Files to change:**

- [ ] `case-studies/flowmark/flowmark-port-decision-log.md`: For each decision (D2-D8),
  add a brief "Alternatives Considered" subsection, even if just one sentence

---

#### 5.13 Add `--cov-branch` to pytest coverage commands

Multiple docs show `pytest --cov` without `--cov-branch`. Branch coverage is more
meaningful than line coverage.

**Files to change:**

- [ ] `reference/python-to-rust-playbook.md` line 57: Add `--cov-branch`

- [ ] `reference/python-to-rust-test-coverage-playbook.md`: Add `--cov-branch`

- [ ] `guidelines/test-coverage-for-porting.md` line 28: Add `--cov-branch`

---

## Testing Strategy

Each phase should be validated by:

1. **Grep verification**: After each batch of changes, grep all documents for the old
   patterns to ensure nothing was missed

2. **Cross-document consistency**: After Phase 1.11 (count reconciliation), verify all
   count references across the 7 flowmark case study files

3. **Code compilation**: For any modified code examples, verify they would compile
   (correct syntax, correct types, correct API usage)

4. **Link validation**: After changes, verify all internal cross-references still work

## Rollout Plan

Apply changes in phase order. Each phase can be committed independently:
- Phase 1: Critical fixes (commit immediately)
- Phase 2: Critical missing content (commit)
- Phase 3: Important fixes (commit)
- Phase 4: Important additions (commit)
- Phase 5: Suggestions (commit)

## Open Questions

- Should `XXX:` be changed to `HACK:` globally or is there a reason for the existing
  convention?
- Should the flowmark case study versions be updated to reflect current comrak (0.50+)
  or left as a historical record?
- Should `color-eyre` be replaced with a different recommendation given its maintenance
  status?
- What are the canonical workaround counts for the flowmark port?

## References

- Review beads: `tbd list --status closed` (23 beads with detailed close-reasons)
- Detailed review transcripts for:
  - `guidelines/python-to-rust-porting-rules.md` (22 findings, 2 CRITICAL)
  - `reference/python-to-rust-mapping-reference.md` (42 findings, 4 CRITICAL)
  - `case-studies/flowmark/flowmark-port-decision-log.md` (21 findings, 1 CRITICAL)
