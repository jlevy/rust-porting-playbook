---
title: Rust Rules
description: General Rust coding rules for modern libraries, applications, services, and command-line tools
category: rust
---
# Rust Rules

Use these rules for any modern Rust codebase, whether it was written in Rust from the
start or ported from another language.
They cover language and API design.
Project tooling, CLI behavior, testing, releases, and review each have focused
guidelines.

**Related:** [`rust-project-setup.md`](rust-project-setup.md),
[`rust-testing-rules.md`](rust-testing-rules.md), and
`tbd guidelines general-coding-rules error-handling-rules`.

## Toolchain, Edition, and MSRV

- **Use the newest Rust edition supported by the declared minimum supported Rust version
  (MSRV).** New projects should normally use Edition 2024.
- **Declare the MSRV.** Set `rust-version` in `Cargo.toml` and test that toolchain in
  CI. A `rust-toolchain.toml` may pin the normal development toolchain separately.
- **Treat MSRV changes as an explicit compatibility decision.** Document the project’s
  policy and release the change according to that policy; do not assume every consumer
  treats an MSRV bump the same way.
- **Use the edition migration tools.** Run `cargo fix --edition` and the full validation
  suite before changing an existing package’s edition.

Edition 2024 changes worth checking during review include the reserved `gen` keyword,
explicit unsafe operations inside `unsafe fn`, return-position `impl Trait` lifetime
capture, shorter tail-expression temporary lifetimes, and resolver version 3.

## Ownership and Borrowing

- **Borrow when the callee only reads.** Prefer `&str`, `&Path`, and slices over owned
  arguments when the function neither stores nor consumes the value.
- **Own data when ownership is part of the contract.** Accept `String`, `PathBuf`, or
  `Vec<T>` when the function stores, transforms, or transfers the value.
- **Make every clone explainable.** A clone used only to silence a borrow-checker error
  is a design signal. Shorten borrow scopes, split state, or change ownership before
  copying a large value.
- **Use `Cow` only for a real borrow-or-own result.** It is useful when the common path
  returns the input unchanged and an uncommon path allocates.
- **Keep shared ownership narrow.** `Rc`, `Arc`, `Mutex`, and `RwLock` should reflect a
  concrete ownership or concurrency requirement, not uncertainty about lifetimes.
- **Do not expose lock guards through public APIs.** Complete the protected operation
  inside the abstraction and return plain data or a result.

```rust
use std::borrow::Cow;

fn normalize(input: &str) -> Cow<'_, str> {
    if input.contains("\r\n") {
        Cow::Owned(input.replace("\r\n", "\n"))
    } else {
        Cow::Borrowed(input)
    }
}
```

## Types and API Design

- **Use domain types instead of primitive aliases.** Newtypes make units and validated
  values explicit.
- **Use enums for modes and states.** Avoid several related booleans or magic sentinel
  values.
- **Use `Option<T>` for absence.** Do not encode absence as `-1`, an empty string, or a
  special path.
- **Make matches exhaustive.** Avoid wildcard arms when adding a new enum variant should
  force callers to make a decision.
- **Keep public APIs minimal.** Default to private or `pub(crate)` and make an item
  `pub` only when it is part of the supported external contract.
- **Avoid allocation-forcing APIs.** Accept borrowed inputs where practical and return
  iterators or slices when callers do not need a newly allocated collection.
- **Use `#[must_use]` when ignoring a result is likely to be a bug.** Apply it to
  important values, builders, guards, and operation results.
- **Introduce traits for actual polymorphism.** A trait with one implementation and no
  generic caller, public extension point, or test seam is usually unnecessary.

```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct RetryCount(u8);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum OutputMode {
    Text,
    Json,
}
```

## Error Handling

- **Use typed errors at library boundaries.** A small error enum, commonly derived with
  `thiserror`, lets callers match recoverable cases without parsing messages.
- **Use contextual reports at application boundaries.** `anyhow` or another report type
  can be appropriate in binaries where errors are displayed rather than matched.
- **Preserve the source error.** Add context with error chaining; do not replace a
  detailed error with a generic string.
- **Do not discard fallible results.** A `let _ = operation()` requires an explicit
  reason that failure is safe to ignore.
- **Avoid `unwrap()` in production paths.** Use `expect()` only for a proven invariant
  and state that invariant in the message.
- **Do not panic across a library’s normal input surface.** Panics are for violated
  programmer contracts or states that are genuinely unreachable.
- **Classify retryable failures explicitly.** Network and service code should not infer
  retry behavior from error strings.

```rust
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("failed to read configuration at {path}")]
    Read {
        path: std::path::PathBuf,
        #[source]
        source: std::io::Error,
    },
    #[error("invalid configuration: {0}")]
    Parse(String),
}
```

For user-visible failures, exit codes, and success verification, also apply
`tbd guidelines error-handling-rules`.

## Strings, Text, and Regular Expressions

- **Remember that Rust string indices are byte offsets.** Use `chars`, `char_indices`,
  or `unicode-segmentation` when the requirement is based on Unicode scalar values or
  grapheme clusters.
- **Use `Path` and `OsStr` for filesystem values.** Do not require paths to be valid
  UTF-8 merely for convenience.
- **Make normalization a declared behavior.** Preserve bytes, whitespace, newlines, and
  normalization forms unless the API promises to transform them.
- **Compile repeated regular expressions once.** `std::sync::LazyLock` is sufficient for
  static regex values.
- **State matching boundaries explicitly.** Readers should not have to infer whether a
  regex is intended to match a substring, a line, or the entire input.
- **Use a more capable regex engine only when the required syntax needs it.** Extra
  engines increase dependency and performance costs.

```rust
use regex::Regex;
use std::sync::LazyLock;

static IDENTIFIER: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*$").expect("valid regex"));
```

## Modules and Documentation

- **Organize modules around coherent responsibilities.** Split files when distinct
  concepts change for different reasons, not at an arbitrary line threshold.
- **Prefer descriptive module files.** Use a directory module when it owns a meaningful
  family of submodules; do not add indirection solely for symmetry.
- **Keep binaries thin.** Put reusable domain behavior in library modules and keep
  process setup at the executable boundary.
- **Document public contracts and invariants.** Public items need concise `///` docs;
  modules with non-obvious responsibilities need `//!` docs.
- **Use doctests for examples that should compile.** Mark an example `no_run` only when
  it must not execute, and explain any `ignore`.
- **Explain why, not syntax.** Comments should record invariants, safety arguments,
  compatibility constraints, or surprising tradeoffs.

## Unsafe Code and FFI

- **Forbid unsafe code by default.** Enable it only in the smallest module or package
  that has a reviewed requirement.
- **Put a `// SAFETY:` argument on every unsafe block.** State the invariant that makes
  the operation sound and where that invariant is established.
- **Keep unsafe blocks minimal.** Wrap them in safe interfaces whose inputs cannot
  trigger undefined behavior.
- **Audit manual `Send` and `Sync` implementations as unsafe code.** Document every
  field and aliasing assumption.
- **Validate FFI boundaries.** Check layouts, ownership, nullability, string encoding,
  error codes, unwinding, and the lifetime of every pointer passed across the boundary.
- **Benchmark before using unsafe for speed.** A safe implementation is the baseline;
  retain unsafe optimization only when measurements justify it.

## Concurrency and Async

- **Do not block an async executor.** Use async I/O or a bounded blocking pool for
  filesystem, CPU-heavy, and synchronous foreign calls.
- **Await or supervise spawned tasks.** Detached tasks need an explicit lifecycle,
  failure-reporting path, and shutdown policy.
- **Design for cancellation.** Code used in `select!`, timeouts, or aborted tasks must
  leave state consistent when a future is dropped at any await point.
- **Use bounded queues unless unbounded growth is proven safe.** Define backpressure
  behavior rather than allowing load to become memory usage.
- **Never hold a lock across slow I/O or an unrelated await.** Copy or move the needed
  state out of the critical section first.
- **Acquire multiple locks in one documented order.** Prefer a design with fewer locks
  when possible.
- **Support graceful shutdown.** Stop accepting work, signal workers, drain or cancel
  in-flight operations according to policy, and report incomplete work.

## Performance

- **Measure before optimizing.** Use representative workloads and retain benchmark
  inputs with the code.
- **Inspect allocations in hot paths.** Reuse buffers and avoid repeated `to_string`,
  `format!`, `collect`, and clone operations inside tight loops.
- **Choose collections for access patterns.** A linear scan can be best for a tiny
  collection; use sets or maps when membership or key lookup dominates.
- **Keep correctness tests separate from benchmarks.** A benchmark should not be the
  only evidence that an optimization preserves behavior.
- **Record the tradeoff.** Non-obvious optimizations need a comment or benchmark link
  explaining the constraint they satisfy.

## Related Guidelines

- [`rust-project-setup.md`](rust-project-setup.md) for Cargo, lint, CI, and dependency
  policy
- [`rust-cli-rules.md`](rust-cli-rules.md) for command-line applications
- [`rust-filesystem-rules.md`](rust-filesystem-rules.md) for filesystem mutation
- [`rust-testing-rules.md`](rust-testing-rules.md) for Rust testing strategy
- [`rust-release-rules.md`](rust-release-rules.md) for packaging and publishing
- [`rust-code-review-rules.md`](rust-code-review-rules.md) for the review checklist
- `tbd guidelines general-comment-rules error-handling-rules general-testing-rules`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
