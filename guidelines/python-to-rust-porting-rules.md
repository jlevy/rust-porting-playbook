---
title: Python-to-Rust Porting Rules
description: General patterns, type mappings, and pitfalls for porting Python applications to Rust
---
# Python-to-Rust Porting Rules

Rules and patterns for systematically porting Python applications to Rust.
Focuses on maintaining exact behavioral parity through test-driven porting.

**Read first:**
[Porting Principles and Anti-Patterns](porting-principles-and-antipatterns.md)
— non-negotiable principles that override all other guidance.

See also: [CLI-Specific Porting Patterns](python-to-rust-cli-porting.md),
[Rust General Rules](rust-general-rules.md),
[Test Coverage for Porting](test-coverage-for-porting.md).
For Python rules, see `tbd guidelines python-rules`.

## Core Principles

1. **Tests are the specification.** The Python test suite defines exactly what the Rust
   port must do. Byte-for-byte output matching is the *goal*; any deviation must be
   explicitly documented, justified, and tracked.
   (See Strategy Matrix for handling unavoidable differences.)

2. **Port behavior, not implementation.** Don’t translate Python idioms literally into
   Rust. Achieve the same behavior using idiomatic Rust patterns.

3. **Maintain clear traceability.** Every Rust module should have a comment indicating
   which Python module it corresponds to.
   Every major function should reference its Python equivalent.

4. **Zero-tolerance for test failures.** 100% of ported tests must pass.
   If a difference is unavoidable (e.g., library behavior), document it explicitly and
   mark the test `#[ignore]` with an explanation.

## Type Mappings

### Basic Types

| Python | Rust | Notes |
| --- | --- | --- |
| `str` | `String` / `&str` | Accept `&str`, return `String` |
| `int` | `i32` / `i64` / `usize` | Match the semantic range |
| `float` | `f64` |  |
| `bool` | `bool` |  |
| `None` | `Option<T>` | Never use sentinel values |
| `bytes` | `Vec<u8>` / `&[u8]` |  |
| `str` (sometimes modified) | `Cow<'_, str>` | Avoids allocation when input unchanged |

### Collections

| Python | Rust | Notes |
| --- | --- | --- |
| `list[T]` | `Vec<T>` |  |
| `dict[K, V]` | `HashMap<K, V>` | Python dict preserves insertion order since 3.7; `HashMap` does **not**. Use `IndexMap` if order matters |
| `set[T]` | `HashSet<T>` | Or `BTreeSet` for sorted |
| `tuple[A, B]` | `(A, B)` | Named struct if >3 elements |
| `deque` | `VecDeque<T>` |  |
| `defaultdict` | `HashMap` with `.entry().or_default()` |  |

### Optional and Union Types

| Python | Rust | Notes |
| --- | --- | --- |
| `Optional[T]` / `T \| None` | `Option<T>` |  |
| `Union[A, B]` | Enum with variants |  |
| `Any` | Generics or `Box<dyn Trait>` | Avoid if possible |

### Error Handling

| Python | Rust | Notes |
| --- | --- | --- |
| `try / except` | `Result<T, E>` with `?` |  |
| `raise ValueError(...)` | `return Err(Error::Validation(...))` |  |
| `assert` (invariant check) | `debug_assert!` | Only for debug-only invariants in hot paths |
| `assert` (validation) | `assert!` or explicit `Result`-based check | Default for porting |
| Exception classes | `thiserror` (library) / `anyhow` (binary) | Standard error handling |
| Functions that never raise | Return `T` directly, NOT `Result<T>` | Match Python exactly |

**Critical rule:** If the Python function never raises an exception, the Rust function
should NOT return `Result`. Match the Python signature exactly.

## Module Mapping

### Python Modules to Rust Modules

```python
# Python
flowmark/
    __init__.py          # Package init
    formatter/
        filling.py       # Core formatting
        markdown.py      # AST manipulation
    wrapping/
        text_wrapping.py # Text wrapping
        sentence.py      # Sentence splitting
    typography/
        quotes.py        # Smart quotes
```

```rust
// Rust
src/
    lib.rs               // Pub API (like __init__.py)
    formatter/
        mod.rs
        filling.rs       // Port of filling.py
        markdown.rs      // Port of markdown.py
    wrapping/
        mod.rs
        text_wrapping.rs // Port of text_wrapping.py
        sentence.rs      // Port of sentence.py
    typography/
        mod.rs
        quotes.rs        // Port of quotes.py
```

### Module Header Convention

Every ported Rust module MUST have a header comment:
```rust
//! Port of Python `flowmark/formatter/filling.py`
//!
//! Main formatting pipeline for normalizing Markdown documents.
```

### Function Mapping Convention

Every major ported function MUST reference its Python origin:
```rust
/// Port of Python `fill_markdown()` in `filling.py`
///
/// Formats a Markdown document with line wrapping and normalization.
pub fn fill_markdown(text: &str, config: &Config) -> Result<String> {
```

## Dependency Mapping

### Common Python-to-Rust Library Mappings

| Python | Rust | Quality | Notes |
| --- | --- | --- | --- |
| argparse / click / typer | clap | Excellent | Use derive API |
| PyYAML | serde_yaml_ng | Good | serde_yaml is archived; use serde_yaml_ng 0.10+ |
| json | serde_json | Excellent |  |
| re | regex | Excellent | Different anchoring behavior! |
| re (look-arounds) | fancy-regex | Good | Only when needed |
| pathlib | std::path | Built-in |  |
| os / shutil | std::fs | Built-in |  |
| textwrap | textwrap (crate) | Good | Or roll your own |
| pytest | cargo test (built-in) | Excellent |  |
| typing | Rust type system | Built-in |  |
| dataclasses | struct + derive macros | Built-in | Minimum: `#[derive(Debug, Clone, PartialEq)]`; add `Eq`, `Hash`, `Serialize`, `Deserialize` as needed |
| abc (ABCs) | traits | Built-in |  |
| Exception hierarchy | thiserror (library) / anyhow (binary) | Excellent | thiserror for typed errors; anyhow for ad-hoc |
| marko (Markdown) | comrak / pulldown-cmark | Varies | See parser selection guide |
| logging | tracing / log | Excellent | tracing is preferred for new code |
| asyncio | tokio | Excellent | De facto async runtime |
| threading | std::thread / rayon | Excellent | rayon for data parallelism |
| subprocess | std::process::Command | Excellent | stdlib |

### Library Evaluation Checklist

Before choosing a Rust crate equivalent:
- [ ] Check spec compliance (does it implement the same standards?)
- [ ] Check maintenance status (last commit, open issues, maintainer activity)
- [ ] Check API compatibility (can it produce the same outputs?)
- [ ] Test with real-world inputs from the Python version
- [ ] Document any behavioral differences
- [ ] Have a backup plan (alternative crate, vendoring, forking)

## Porting Sequence

### Recommended Order

1. **Project setup** -- Cargo.toml, directory structure, Python submodule
2. **Core data types** -- Config, Error types, shared structs
3. **Innermost modules first** -- Leaf modules with no internal dependencies
4. **Test as you go** -- Port unit tests alongside each module
5. **Integration modules** -- Modules that combine the leaves
6. **CLI last** -- Thin wrapper once library works
7. **Cross-validation** -- Run both implementations against same inputs

### Per-Module Workflow

For each Python module:
1. Read the Python source (from submodule)
2. Create Rust file with module header comment
3. Port the tests first (TDD style)
4. Implement the functions to make tests pass
5. Run `cargo test` -- all new tests must pass
6. Run cross-validation against Python output

## Key Pitfalls

### 1. Regex Anchoring

Python and Rust regex have different anchoring behavior.
All three Python regex functions need careful translation:

- `re.match(pat)` -- anchors to start of string.
  Prepend `^` (or `\A` for multiline safety).
- `re.search(pat)` -- matches anywhere.
  Use pattern as-is (both are unanchored).
- `re.fullmatch(pat)` -- matches entire string.
  Wrap with `^...$` (or `\A...\z`).

```python
# Python
re.match(r"\w+", "$hello")      # None (anchored to start)
re.search(r"\w+", "$hello")     # Match (anywhere)
re.fullmatch(r"\w+", "hello")   # Match (entire string)
```
```rust
// Rust -- all unanchored by default, must add anchors explicitly
Regex::new(r"\w+").unwrap().is_match("$hello")      // true! (wrong for re.match)
Regex::new(r"^\w+").unwrap().is_match("$hello")      // false (correct for re.match)
Regex::new(r"\w+").unwrap().is_match("$hello")       // true (correct for re.search)
Regex::new(r"^\w+$").unwrap().is_match("hello")      // true (correct for re.fullmatch)
```

**Rule:** Add `^` to EVERY pattern used with Python `re.match()`. Wrap with `^...$` for
`re.fullmatch()`. Use `\A`/`\z` instead of `^`/`$` when multiline mode is active.

### 2. String Preservation

Don’t “helpfully” modify input:
```rust
// WRONG: trims whitespace Python doesn't trim
pub fn process(text: &str) -> String {
    text.trim().to_string()
}

// CORRECT: preserves input exactly as Python does
pub fn process(text: &str) -> String {
    text.to_string()
}
```

### 3. Function Signatures Must Match

```python
def split_frontmatter(text: str) -> tuple[str, str]:
    return ("", text)  # Returns tuple, never None
```
```rust
// WRONG: different return type
fn split_frontmatter(text: &str) -> Option<(String, String)> { ... }

// CORRECT: matches Python exactly
fn split_frontmatter(text: &str) -> (String, String) {
    (String::new(), text.to_string())
}
```

### 4. String Indexing

```rust
// WRONG: panics on multi-byte characters
let ch = &text[5..6];

// CORRECT: char-boundary safe
let ch = text.chars().nth(5);
// or use char_indices() for slicing
```

### 5. Library Type Differences

Library types are version-dependent.
Check current docs:
```rust
// comrak NodeValue::Text: String (pre-0.45), Cow<'static, str> (0.45+).
// pulldown-cmark uses CowStr (different API). Always verify against your Cargo.lock version.
```

### 6. Integration Test Location

```
// WRONG: tests/ at workspace root, outside any member crate
my-workspace/tests/test_format.rs

// CORRECT: tests/ inside a specific crate
my-workspace/crates/core/tests/test_format.rs
```

### 7. Arena Pattern for AST Libraries

Python AST libraries let you hold references freely.
Rust libraries like comrak use arenas that require closure-based APIs:
```rust
pub fn with_markdown_ast<F, R>(text: &str, f: F) -> Result<R>
where
    F: for<'a> FnOnce(&'a AstNode<'a>) -> Result<R>,
{
    let arena = Arena::new();
    let root = parse_document(&arena, text, &options);
    f(root)
}
```

### 8. Edition 2024 Reserved Keywords

Rust Edition 2024 reserves `gen` as a keyword.
If the Python code uses `gen` as a variable or function name (common in
generator-related code), you must rename it in Rust:
```rust
// WRONG: `gen` is a reserved keyword in Edition 2024
let gen = create_generator();

// CORRECT: rename to avoid keyword conflict
let generator = create_generator();
```

### 9. Line Ending Differences

Normalize line endings in tests when they’re not semantically significant.
Be explicit about expectations in byte-for-byte comparison tests.

## Handling Library Bugs and Differences

### Strategy Matrix

| Severity | Impact | Strategy |
| --- | --- | --- |
| Cosmetic | Output differs but is valid | Accept and document |
| Functional | Output incorrect but rare | Workaround with post-processing |
| Critical | Core behavior broken | Vendor/fork the library, or switch libraries |

### Workaround Pattern

Mark all workarounds with structured comment prefixes:
- `HACK:` for library workarounds that are intentional and stable.
- `FIXME:` for items needing future resolution.

Avoid `XXX:` — it is not recognized by most linters, IDEs, or CI grep patterns.
Use `HACK:` for workarounds and `FIXME:` for known issues instead.

```rust
/// WORKAROUND: comrak normalizes list markers to `-`, but Python preserves `*`.
/// This is unfixable without forking comrak's renderer.
/// Impact: minor -- both are valid Markdown.

/// FIXME: This post-processing step should be removed once comrak #567 is merged.
```

### When to Switch Libraries

Switch if you find >3 unfixable differences that affect core behavior.
The cost of working around one library’s bugs accumulates rapidly.
Research alternatives early.

## Post-Port Cleanup

### Stale Python-Reference Comments

During porting, agents add comments mapping Rust code back to Python (e.g.,
`// Python: self._format_line(text)`). After the port stabilizes, many of these become
stale as the Rust code evolves independently. Schedule a cleanup pass:

1. **Verify each Python reference comment is still accurate.** If the Rust
   implementation has diverged, update or remove the comment.
2. **Keep module-level mapping comments** (`//! Ported from Python: flowmark/filling.py`)
   — these remain valuable for traceability.
3. **Remove per-line Python comments** that describe implementation details no longer
   relevant to the Rust code. Rust code should explain itself idiomatically, not as a
   translation of Python.
4. **Keep comments that explain non-obvious behavioral parity** — e.g., "matches Python's
   behavior of returning empty string for None input."

### Visibility Audit

After porting is complete, audit `pub` visibility. During porting, agents tend to make
everything `pub` for convenience. Convert internal-only items to `pub(crate)`. See
[Code Review Checklist](../playbooks/rust-code-review-checklist.md) for details.

## Acceptance Criteria

**Zero-tolerance completion gate:**
- [ ] 100% of Python tests pass in Rust
- [ ] Byte-for-byte output match on all test fixtures (goal; document deviations with
  `WORKAROUND:` if a library difference makes exact match impossible)
- [ ] Cross-validation with zero diffs on representative documents (or all diffs
  explained by documented workarounds)
- [ ] All known differences documented with `HACK:` or `FIXME:` comments
- [ ] All `#[ignore]` tests have documented reasons
- [ ] CLI help text matches Python exactly
- [ ] Exit codes match Python behavior
- [ ] cargo clippy -- -D warnings passes with zero warnings
- [ ] cargo fmt -- --check passes (consistent formatting)

## Related Guidelines

- [CLI-Specific Porting](python-to-rust-cli-porting.md)
- [Rust General Rules](rust-general-rules.md)
- [Test Coverage for Porting](test-coverage-for-porting.md)
- For Python rules, see `tbd guidelines python-rules`
- For golden testing, see `tbd guidelines golden-testing-guidelines`
- For TDD methodology, see `tbd guidelines general-tdd-guidelines`
