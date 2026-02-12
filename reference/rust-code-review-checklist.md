# Rust Code Review Checklist

*Aim:* use this **after** CI (fmt, Clippy incl.
pedantic, tests) has passed.
This checklist focuses on what tools **won't** reliably catch: ownership design,
abstraction quality, unsafe contracts, async/concurrency correctness, performance hot
spots, and long-term maintainability.

Scope: **general Rust** (libs, services, agents, tools)

Assumptions: edition 2024 or later, MSRV declared in `Cargo.toml`/`rust-toolchain.toml`;
workspace lints configured; formatting enforced.

### Severity key

| Tag | Meaning |
|-----|---------|
| **[CRITICAL]** | Must fix before merge -- correctness or soundness issue |
| **[HIGH]** | Strong recommendation -- significant maintainability or safety concern |
| **[MEDIUM]** | Should fix -- idiom, clarity, or moderate quality concern |
| **[LOW]** | Nice to have -- style preference or minor improvement |

* * *

## 1. Ownership & Borrowing

- [ ] **[HIGH] Clones are deliberate, not accidental.** For every `.clone()`, ask: "Why
  is this clone here?" If it's to "make the borrow checker happy," require a redesign
  (pass refs, restructure data flow, or use `Cow`) rather than copying whole data
  structures.

- [ ] **[MEDIUM] Prefer borrowing to owning.** API signatures should lean toward `&T` /
  `&str` / slices where mutation or ownership transfer is not required.
  Owning parameters (`String`, `Vec<T>`) should be justified (e.g. function consumes or
  stores them).

- [ ] **[HIGH] No gratuitous `'static`.** Check for `&'static str` or `'static` bounds
  added "just to make it compile."
  Accept `'static` only when values truly live for the duration of the program (global
  registries, tasks spawned without join, plugin tables).

- [ ] **[MEDIUM] Lifetimes are as narrow as possible.** If a function or struct has
  explicit lifetimes, verify they express a real relation between inputs/outputs, not a
  "catch-all" lifetime that makes everything live too long.

- [ ] **[HIGH] Don't fight the borrow checker by copying state.** If a function keeps
  doing "clone -> modify -> reassign," suggest refactoring to smaller, mutating helpers or
  to a struct that owns exactly what it needs.

- [ ] **[MEDIUM] Shared ownership is justified.** Uses of `Arc<T>`, `Arc<Mutex<T>>`,
  `Arc<RwLock<T>>` should explain *why multiple owners* are needed.
  If a value is never actually shared across threads/tasks, prefer single ownership or
  borrowed access.

- [ ] **[HIGH] Locks don't escape unnecessarily.** Don't return `MutexGuard` from public
  APIs. Keep lock scopes tight and internal; expose plain data or operations instead.

* * *

## 2. Error Handling

- [ ] **[CRITICAL] No unreviewed `.unwrap()` / `.expect()` in non-test code.** If
  present, it must (a) be in startup/one-off initialization or (b) have a strong
  invariant + clear `.expect("reason")` message. Otherwise, require `?` or explicit error
  handling.

- [ ] **[HIGH] `?` is used to propagate, not to hide.** When a function returns
  `Result<_, E>`, errors should be passed upward with `?` or mapped to a richer error.
  Manual `match` on `Result` just to rewrap the same error is a smell.

- [ ] **[HIGH] Errors carry context.** Check that `map_err` / `with_context` (or
  `anyhow::Context`) is used on I/O, parsing, network, or external calls, so you know
  *what* failed and *with which input*.

- [ ] **[HIGH] Application vs library error strategy is clear.**

  - Apps/CLIs: `anyhow` / `color-eyre` are fine for fast composition.

  - Libraries: strongly prefer typed errors (`thiserror`) or a small enum to keep API
    stable and `Send + Sync`.

- [ ] **[HIGH] Error types implement `Display` and `Debug`.** Custom error enums should
  derive or implement `Debug` and have meaningful `Display` output (e.g. via `thiserror`
  `#[error(...)]` attributes). Callers should be able to log or print errors without
  guessing their content.

- [ ] **[CRITICAL] No silent discard of errors.** Look for `_ = some_fallible_call()` or
  `let _ = ...;` patterns. These should be logged, bubbled, or explicitly documented as
  ignorable.

- [ ] **[HIGH] Async task errors are handled.** For `tokio::spawn(...)` or equivalent,
  the `JoinHandle` should be awaited or errors logged; don't spawn-and-forget unless it's
  truly fire-and-forget and documented.

- [ ] **[MEDIUM] Panic is intentional and documented.** If some code must panic (e.g.
  "this branch is unreachable due to X invariant"), require an inline comment or docstring
  to that effect.

* * *

## 3. Unsafe Code

- [ ] **[CRITICAL] Every `unsafe` block has a `// SAFETY:` comment.** E.g.
  `// SAFETY: ptr was obtained from alloc and is still valid here.`
  Reject unsafe without such explanation.

- [ ] **[CRITICAL] Scope of unsafe is minimal.** Isolate unsafe into small, well-named
  internal functions with safe public wrappers. In edition 2024, `unsafe fn` bodies are no
  longer implicitly unsafe -- each unsafe operation requires its own explicit `unsafe {}`
  block, which is the correct granularity. Avoid sprinkling unsafe across call sites;
  contain it in one auditable place.

- [ ] **[CRITICAL] Invariants are traceable.** If unsafe assumes non-null, alignment,
  non-aliasing, or length >= N, verify where that guarantee is established.
  Link to the call site or constructor that enforces it.

- [ ] **[HIGH] FFI calls validate inputs/outputs.** Check `extern "C"` or bindings for:
  correct types, error codes handled, C strings null-terminated, and no `&mut` aliasing of
  the same memory passed to C.

- [ ] **[HIGH] Safe alternative was actually considered.** If unsafe is used for
  performance, confirm that a safe standard-lib or crate alternative doesn't exist -- or
  that benchmarks justify this choice.

- [ ] **[CRITICAL] No unchecked indexing without reason.** If you see `get_unchecked` /
  `get_unchecked_mut`, require a clear argument why the index is always in range.

- [ ] **[CRITICAL] Unsafe does not leak UB to safe callers.** Public safe APIs must not
  expose footguns created inside unsafe blocks. A safe function must never cause undefined
  behavior regardless of its inputs.

* * *

## 4. Abstraction & API Design

- [ ] **[MEDIUM] Traits are justified.** A trait with only one impl, no clear polymorphic
  call site, or no test seam is suspect.
  Ask: "Can this be a free function or a generic over `Fn` instead?"

- [ ] **[MEDIUM] No Java-style layering.** Avoid "service -> manager -> provider ->
  adapter" stacks for simple operations.
  If the feature is simple, the code should be simple.

- [ ] **[HIGH] Public surface is minimal.** Modules should expose the smallest set of
  types/functions needed.
  Extra types should stay `pub(crate)` or private so the crate can evolve without breaking
  changes.

- [ ] **[MEDIUM] Modules are coherent.** Related types/functions live together.
  If a module mixes parsing, network calls, and business logic, suggest splitting.

- [ ] **[MEDIUM] APIs don't force allocation.** Don't make callers give you `String` when
  `&str` works; don't return `Vec<T>` when an iterator or slice would do.
  Avoid "eager" APIs if lazy/streaming is possible.

- [ ] **[MEDIUM] Data ownership is clear in APIs.** For builder patterns or config
  structs, ensure it's clear what the API keeps, what it borrows, and what gets consumed.

- [ ] **[LOW] Enums over booleans for multi-state.** If you see multiple related bools or
  "mode" bools in APIs, suggest an enum to make call sites self-describing.

- [ ] **[MEDIUM] Feature flags are contained.** If the crate supports features, ensure
  code doesn't become a tangle of `#[cfg(feature = ...)]` inside business logic -- push
  those to integration or boundary modules.

- [ ] **[HIGH] `#[must_use]` on important return values.** Functions that return a value
  the caller must act on (e.g., `Result`, builder, resource handle) should be annotated
  with `#[must_use]`. Check that types where ignoring the return value is a bug carry this
  attribute.

- [ ] **[HIGH] Semver compliance for libraries.** Any change to public types, trait
  bounds, function signatures, or re-exports must be evaluated for semver impact. Removing
  a public item or adding a required trait bound is a breaking change.

* * *

## 5. Performance & Efficiency

- [ ] **[HIGH] Hot paths are allocation-aware.** In loops or per-request logic, check
  for: `to_string()`, `collect::<Vec<_>>()`, `clone()`, `format!`, `String::new()` --
  each iteration. Suggest hoisting or reusing buffers.

- [ ] **[MEDIUM] Iterator/slice APIs are used.** Prefer `iter().map(...).collect()` or
  `slice.chunks()` over manual index loops that allocate temporaries.
  Idiomatic iterator chains are often clearer and optimize well.

- [ ] **[MEDIUM] Right collection for the job.**

  - Frequent membership tests -> `HashSet`

  - Sorted/range queries -> `BTreeMap/BTreeSet`

  - Small, fixed-size, hot data -> arrays/slices

  - Don't use `Vec` + linear search by default if it's on a hot path.

- [ ] **[CRITICAL] Async code doesn't block.** Any `std::fs`, heavy CPU, or
  network-without-timeout inside `async fn` should be offloaded (`spawn_blocking`,
  dedicated workers). Blocking the async runtime stalls all tasks on that thread.

- [ ] **[HIGH] Lock contention is minimized.** Long operations (I/O, parsing, network)
  must not run under a `Mutex`. Acquire, copy what's needed, drop the lock, then do the
  slow work.

- [ ] **[MEDIUM] No unnecessary `Arc`/`Rc`.** If a value is only ever passed down, not
  shared, don't wrap it. Atomic refcounting has a cost.

- [ ] **[LOW] Avoid needless conversions.** Repeated `String` <-> `&str` <-> `PathBuf`
  <-> `OsString` with no need is a smell; stick to the most native type for the layer
  you're in.

- [ ] **[MEDIUM] Check formatting cost.** Logging or user messages in tight loops should
  avoid repeated `format!` -- pre-build strings or use structured logging with fields.

* * *

## 6. Idiomatic & Readable Code

- [ ] **[MEDIUM] Pattern matching for enums.** Replace long `if let Some(..)` /
  `if kind == ...` chains with a `match` that covers all variants.
  This also future-proofs for added variants.

- [ ] **[LOW] Use `if let` / `while let` / `let-else` for option/result flows.** Don't
  manually match just to extract the inner value. Use `let Some(x) = expr else { ... };`
  (stabilized since Rust 1.65) for early-return guard patterns.

- [ ] **[MEDIUM] No homegrown std reimpl.** If the code manually parses ints, walks
  directories, de/serializes JSON/TOML/YAML in an ad-hoc way -- suggest std or well-known
  crate alternatives.

- [ ] **[MEDIUM] Names are domain-precise.** `process_data` / `handle_thing` -> ask for
  a more descriptive name. Call things by the domain concept they represent.

- [ ] **[LOW] Clarity over cleverness.** If a one-liner iterator chain is hard to read,
  ask to split it into named steps.

- [ ] **[MEDIUM] Consistent coding style across crate.** If the project uses builders,
  error enums, or newtypes, additions should follow the existing pattern -- don't
  introduce a new style for similar problems.

- [ ] **[MEDIUM] Dead code / unused features removed.** If a function exists "for later,"
  it should be behind a feature, documented, or removed.

* * *

## 7. Testing & Documentation

- [ ] **[HIGH] New logic -> new tests.** Any non-trivial function, parser, or state
  machine should come with unit tests (including edge/boundary conditions).

- [ ] **[HIGH] Error paths are tested.** If the code constructs detailed errors, ensure
  at least one test asserts the error variant/message/context.

- [ ] **[MEDIUM] Integration tests for flows.** For multi-step flows (agents, async
  tasks, pipelines), prefer an integration test so regressions get caught at the
  orchestration level.

- [ ] **[HIGH] Doc comments on public items.** `pub fn`, `pub struct`, `pub enum` --
  should say what they do and (if relevant) what invariants/costs they have. Include
  `# Examples` sections for non-obvious APIs.

- [ ] **[MEDIUM] Comments are current.** Flag TODOs or comments that no longer describe
  the code. Outdated docs are worse than none.

- [ ] **[MEDIUM] Hard-to-test code is refactored.** If a reviewer can't test it without
  spinning the whole world, suggest extracting pure logic into testable units and keeping
  I/O/glue thin.

- [ ] **[MEDIUM] Doc-tests compile and pass.** Code examples in `///` doc comments are
  compiled and run by `cargo test`. Ensure they are correct and not marked `ignore` without
  reason.

* * *

## 8. Dependencies & Supply Chain

- [ ] **[HIGH] Dependencies are audited.** Run `cargo-deny` or `cargo-audit` to check
  for known vulnerabilities. New dependencies should be reviewed for maintenance status,
  download counts, and trust level.

- [ ] **[HIGH] License compliance.** All dependencies must have licenses compatible with
  the project. Configure `cargo-deny` advisories and license checks. Watch for
  copyleft licenses (GPL, AGPL) in transitive dependencies.

- [ ] **[MEDIUM] Minimal dependency tree.** Avoid adding a crate for trivial
  functionality that can be written in a few lines. Each dependency is an ongoing
  maintenance and supply-chain risk.

- [ ] **[MEDIUM] Feature flags on dependencies.** Pull in only the features you need.
  E.g., `tokio = { features = ["rt", "macros"] }` rather than `features = ["full"]`.

- [ ] **[HIGH] MSRV is respected.** New code and new dependencies must compile on the
  declared minimum supported Rust version. Check `rust-version` in `Cargo.toml` and test
  with that toolchain in CI.

- [ ] **[MEDIUM] No vendored C code surprises.** Dependencies that compile C/C++ via
  `cc` or `cmake` crates add build complexity and cross-compilation risk. Flag these for
  review.

* * *

## 9. Concurrency & Async Patterns

- [ ] **[CRITICAL] `Send`/`Sync` bounds are correct.** Types shared across threads or
  passed to `tokio::spawn` must be `Send`. Types behind `Arc` for shared access must be
  `Sync`. Verify that manual `Send`/`Sync` impls (especially `unsafe impl`) are sound.

- [ ] **[HIGH] Deadlock potential reviewed.** If multiple locks are acquired, verify
  consistent ordering. Prefer single-lock designs or lock-free approaches where possible.

- [ ] **[HIGH] Cancellation safety.** Async code used with `tokio::select!` or timeouts
  must be cancellation-safe. Dropping a future mid-`.await` must not leave state
  inconsistent. Document cancellation behavior for public async APIs.

- [ ] **[MEDIUM] Backpressure is handled.** Unbounded channels (`mpsc::unbounded`) and
  unbounded spawning can cause memory exhaustion under load. Prefer bounded channels and
  explicit backpressure strategies.

- [ ] **[MEDIUM] Graceful shutdown.** Long-running services should handle shutdown signals
  (e.g., `tokio::signal`) and drain in-flight work rather than terminating abruptly.

* * *

## 10. Quick-Scan: Forbidden Patterns

Use this as a rapid first pass. Each item here corresponds to a detailed check in
sections 1-9 above.

| Pattern | Severity | Section |
|---------|----------|---------|
| `unwrap()` / `expect()` in library code without invariant comment | CRITICAL | 2 |
| `unsafe` block without `// SAFETY:` comment | CRITICAL | 3 |
| `.clone()` on multiple adjacent lines to appease borrow checker | HIGH | 1 |
| Blocking I/O or heavy CPU inside `async fn` | CRITICAL | 5, 9 |
| Over-generic / trait-heavy code for a single concrete use | MEDIUM | 4 |
| Global shared mutable state (`static mut`, `lazy_static` + `Mutex`) | HIGH | 1 |
| `get_unchecked` in non-hot code without proof and comment | CRITICAL | 3 |
| Silent error swallowing (`let _ = ...;` without log or comment) | CRITICAL | 2 |
| Magic constants in logic without naming/explanation | MEDIUM | 6 |
| `TODO` / `FIXME` / `HACK` without a tracking issue | MEDIUM | 7 |
| `#[allow(clippy::...)]` without justification comment | MEDIUM | 6 |

* * *

## 11. Reviewer Flow (How to Use This)

Suggested review order, from highest impact to lowest:

1. **Unsafe & soundness** (section 3): are invariants documented and minimal?
2. **Error handling** (section 2): do we lose context, panic, or swallow errors?
3. **Ownership & borrowing** (section 1): can this be done with refs instead of
   clones/Arcs?
4. **Concurrency** (section 9): `Send`/`Sync` correct? cancellation-safe? no deadlocks?
5. **Performance** (section 5): any hot-path allocations / blocking / lock contention?
6. **Abstraction & API** (section 4): are we adding traits/types we don't need?
7. **Dependencies** (section 8): new crates justified and audited?
8. **Idioms & tests** (sections 6-7): code looks like Rust, not Java/Python; tests and
   docs added.

For a quick scan, use the table in section 10 to spot forbidden patterns before doing a
detailed review.

* * *

**Goal:** This checklist keeps the repo *idiomatic, auditable, and refactorable* in
6-12 months, even as the team grows and new Rust edition features arrive.
