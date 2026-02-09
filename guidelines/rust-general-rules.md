---
title: Rust General Rules
description: General Rust coding rules and best practices for modern projects (Edition 2024+)
---
# Rust General Rules

General coding rules for Rust projects. Use these as a baseline for any new Rust
codebase or when reviewing Rust code quality. Focuses on Edition 2024+ (Rust 1.85+)
patterns and modern idioms.

For CLI-specific patterns, see `tbd guidelines rust-cli-app-patterns`.
For project setup and tooling, see `tbd guidelines rust-project-setup`.
For general coding rules (language-agnostic), see `tbd guidelines general-coding-rules`.

## Edition and MSRV

- **Use Edition 2024** for new projects (requires Rust 1.85+). Edition 2021 is acceptable
  for maximum ecosystem compatibility.

- **Declare `rust-version`** in Cargo.toml to enforce MSRV:
  ```toml
  [package]
  edition = "2024"
  rust-version = "1.85"
  ```

- MSRV bumps are NOT semver-breaking. Use minor version bump (1.1.0 -> 1.2.0).

- Test MSRV compliance in CI with an explicit toolchain install.

### Edition 2024 Key Changes (Rust 1.85+)

- **`gen` is a reserved keyword** — rename any variables named `gen` (common in Python ports)
- **`unsafe_op_in_unsafe_fn` is deny-by-default** — unsafe operations inside `unsafe fn` must be wrapped in `unsafe {}` blocks
- **RPIT lifetime captures** — return-position `impl Trait` captures all in-scope lifetimes by default (may need `+ use<'a>` to restrict)
- **`static mut` is soft-deprecated** — use `std::sync::Mutex`, `AtomicT`, or `LazyLock` instead
- **Let chains** — `if let Some(x) = a && x > 0 { ... }` is now stable
- **Resolver v3** — MSRV-aware dependency resolution; use `resolver = "3"` in workspace `Cargo.toml`

## Ownership and Borrowing

- **Accept `&str` over `String`** in function parameters when you only need to read.
  Return `String` when the function creates new data.

- **Prefer borrowing over cloning.** Only clone when ownership transfer is necessary or
  the cost is negligible.

- **Don't fight the borrow checker by copying state.** If you find yourself cloning
  everything to satisfy lifetimes, redesign the data flow.

- **Use `Cow<'_, str>`** when a function sometimes borrows, sometimes owns:
  ```rust
  fn normalize(input: &str) -> Cow<'_, str> {
      if needs_change(input) {
          Cow::Owned(transform(input))
      } else {
          Cow::Borrowed(input)
      }
  }
  ```

- **Arena pattern for tree structures:** When you have self-referential data (AST nodes,
  graphs), use arena allocation with closure-based APIs:
  ```rust
  pub fn with_ast<F, R>(text: &str, f: F) -> Result<R>
  where
      F: for<'a> FnOnce(&'a AstNode<'a>) -> Result<R>,
  {
      let arena = Arena::new();
      let root = parse_document(&arena, text, &options);
      f(root)
  }
  ```

## Error Handling

- **Use `thiserror`** for library error types. Define specific error variants:
  ```rust
  #[derive(Debug, thiserror::Error)]
  pub enum Error {
      #[error("failed to parse: {0}")]
      Parse(String),
      #[error("I/O error: {0}")]
      Io(#[from] std::io::Error),
  }
  ```

- **Use `color-eyre` or `anyhow`** in binary crates for ergonomic error propagation.
  Note: `color-eyre` 0.6 is in maintenance mode (no active feature development). Still
  functional and widely used, but consider `anyhow` for simpler needs.

- **Only use `Result` when the Python equivalent can raise.** When porting, if the
  Python function never raises, don't wrap in Result -- match the behavior exactly.

- **Don't `unwrap()` in library code.** Use `expect()` only for truly impossible states
  with an explanatory message. In application code, prefer `?` propagation.

- **Never panic in library code** unless a contract violation makes continuing dangerous.

For more on error handling, see `tbd guidelines error-handling-rules`.

## String Handling

- **Prefer `&str` for function parameters**, `String` for struct fields and return values.

- **Use `format!()` for string building**, not repeated push/concatenation.

- **Be careful with string slicing** -- `text[start..end]` panics if not on char
  boundaries. Use `text.chars()`, `text.char_indices()`, or the `unicode-segmentation`
  crate for Unicode-safe operations.

- **Use explicit Unicode escapes in tests** for clarity:
  ```rust
  assert_eq!(result, "I\u{2019}m there"); // \u{2019} = right single quote '
  ```

- **String preservation**: Don't "helpfully" modify input. If a Python function returns
  its input unchanged (including whitespace), the Rust version must do the same.

## Regex

- **Use `LazyLock` (stable since Rust 1.80)** for compiled regex. Remove the `once_cell` dependency if present — `LazyLock` fully replaces `once_cell::sync::Lazy` and is part of `std`:
  ```rust
  use std::sync::LazyLock;
  use regex::Regex;

  static PATTERN: LazyLock<Regex> =
      LazyLock::new(|| Regex::new(r"^\d+\.").unwrap());
  ```

- **Anchor patterns explicitly.** Python's `re.match()` implicitly anchors to start;
  Rust's `is_match()` matches anywhere. Add `^` for start-anchored matching.

- **Use `fancy-regex`** only when you need look-around or backreferences. Keep hot paths
  on the standard `regex` crate for performance.

## Type System

- **Use newtypes** for domain-specific values:
  ```rust
  struct LineWidth(usize);
  ```

- **Prefer enums over booleans** for function parameters:
  ```rust
  // AVOID: `None` as a variant name — it shadows `Option::None` and causes confusing
  // compiler errors. Use `Off`, `NoBreaks`, etc. instead.
  enum LineBreakMode { Sentence, Width, Off }
  // NOT: fn format(text: &str, sentence_breaks: bool, width_breaks: bool)
  ```

- **Use `Option<T>`** instead of sentinel values. Never use `-1` or empty string as
  "no value".

- **Derive liberally:** `Debug`, `Clone`, `PartialEq` on most types. Add `Eq`, `Hash`,
  `Serialize`, `Deserialize` when needed.

## Code Organization

- **One module per file** as the default. Use `mod.rs` directories only for modules with
  3+ submodules.

- **Put tests in the same file** as the code they test (`#[cfg(test)] mod tests`). Use
  `tests/` directory only for integration tests.

- **Keep modules focused.** If a file exceeds ~500 lines, consider splitting.

- **Use `pub(crate)` over `pub`** for internal APIs. Only `pub` what's part of the
  library's external contract.

- **Maintain clear Python-to-Rust module mapping** when porting. Add a comment at the
  top of each module:
  ```rust
  //! Rust port of Python `flowmark/formatter/filling.py`
  ```

## Formatting and Linting

- **Zero tolerance for `cargo fmt` failures** in CI:
  ```bash
  cargo fmt --all -- --check
  ```

- **Enable clippy pedantic** with selective allows:
  ```toml
  [workspace.lints.clippy]
  pedantic = "warn"
  missing_errors_doc = "allow"
  missing_panics_doc = "allow"
  module_name_repetitions = "allow"
  must_use_candidate = "allow"
  ```

- **Forbid unsafe code** unless explicitly needed:
  ```toml
  [workspace.lints.rust]
  unsafe_code = "forbid"
  ```

- **Treat warnings as errors in CI:**
  ```bash
  cargo clippy --all-targets --all-features -- -D warnings
  ```

## Common Patterns

- **Builder pattern** for configuration:
  ```rust
  let config = Config::builder()
      .line_width(80)
      .typography(true)
      .build();
  ```

- **Iterator chains** over manual loops:
  ```rust
  // Prefer
  let results: Vec<_> = items.iter().filter(|x| x.is_valid()).map(|x| x.name()).collect();
  // Over
  let mut results = Vec::new();
  for item in &items {
      if item.is_valid() { results.push(item.name()); }
  }
  ```

- **`impl Into<T>` for flexible APIs:**
  ```rust
  fn set_title(title: impl Into<String>) { /* ... */ }
  ```

## Anti-Patterns to Avoid

- **Don't clone to satisfy the borrow checker.** Redesign data flow instead.

- **Don't use `Box<dyn Error>`** in libraries. Use concrete error types with `thiserror`.

- **Don't use `String` everywhere.** Accept `&str`, return `String`.

- **Don't ignore warnings.** Fix them or explicitly `#[allow]` with a comment explaining why.

- **Don't use `unsafe` without a safety comment** explaining the invariant being upheld.

- **Don't suppress test output.** Let `cargo test` show assertion details on failure.

## Testing

- **Test behavior, not implementation.** Compare full output, not internal state:
  ```rust
  // WRONG: counting internal nodes
  assert_eq!(count_nodes(root), 5);
  // RIGHT: comparing rendered output
  assert_eq!(render(root), expected_output);
  ```

- **Use `include_str!()` for test fixtures:**
  ```rust
  const INPUT: &str = include_str!("../fixtures/input.md");
  const EXPECTED: &str = include_str!("../fixtures/expected.md");
  ```

- **Use `proptest` for property-based testing** of algorithmic code.

- **Name tests descriptively:** `test_wrap_preserves_code_blocks`, not `test_wrap_1`.

For comprehensive testing guidelines, see `tbd guidelines general-testing-rules` and
`tbd guidelines general-tdd-guidelines`.

## Performance

- **Profile before optimizing.** Use `cargo flamegraph` or `perf` to find hot spots.

- **Allocation-aware hot paths:** Avoid allocating in tight loops. Reuse buffers.

- **Use `&str` slicing over `String` creation** when you're extracting substrings that
  don't outlive the source.

- **Benchmark with `criterion`** for performance-critical code.

## Related Guidelines

- For CLI application patterns, see `tbd guidelines rust-cli-app-patterns`
- For project setup and CI/CD, see `tbd guidelines rust-project-setup`
- For Python-to-Rust porting, see `tbd guidelines python-to-rust-porting-rules`
- For general coding rules, see `tbd guidelines general-coding-rules`
- For error handling, see `tbd guidelines error-handling-rules`
- For testing, see `tbd guidelines general-testing-rules`
