# Rust Code Review Checklist (Advanced, 2024+)

*Aim:* use this **after** CI (fmt, Clippy incl.
pedantic, tests) has passed.
This checklist focuses on what tools **won’t** reliably catch: ownership design,
abstraction quality, unsafe contracts, async/concurrency correctness, performance hot
spots, and long-term maintainability.

Scope: **general Rust** (libs, services, agents, tools)

Assumptions: edition = `2024`, MSRV declared; workspace lints configured; formatting
enforced.

* * *

## 1. Ownership & Borrowing

- [ ] **Clones are deliberate, not accidental.** For every `.clone()`, ask: “Why is this
  clone here?” If it’s to “make the borrow checker happy,” require a redesign (pass refs,
  restructure data flow, or use `Cow`) rather than copying whole data structures.

- [ ] **Prefer borrowing to owning.** API signatures should lean toward `&T` / `&str` /
  slices where mutation or ownership transfer is not required.
  Owning parameters (`String`, `Vec<T>`) should be justified (e.g. function consumes or
  stores them).

- [ ] **No gratuitous `'static`.** Check for `&'static str` or `'static` bounds added
  “just to make it compile.”
  Accept `'static` only when values truly outlive the program (global registries, tasks
  spawned without join, plugin tables).

- [ ] **Lifetimes are as narrow as possible.** If a function or struct has explicit
  lifetimes, verify they express a real relation between inputs/outputs, not a
  “catch-all” lifetime that makes everything live too long.

- [ ] **Don’t fight the borrow checker by copying state.** If a function keeps doing
  “clone → modify → reassign,” suggest refactoring to smaller, mutating helpers or to a
  struct that owns exactly what it needs.

- [ ] **Shared ownership is justified.** Uses of `Arc<T>`, `Arc<Mutex<T>>`,
  `Arc<RwLock<T>>` should explain *why multiple owners* are needed.
  If a value is never actually shared across threads/tasks, prefer single ownership or
  borrowed access.

- [ ] **Locks don’t escape unnecessarily.** Don’t return `MutexGuard` from public APIs.
  Keep lock scopes tight and internal; expose plain data or operations instead.

* * *

## 2. Error Handling

- [ ] **No unreviewed `.unwrap()` / `.expect()` in non-test code.** If present, it must
  (a) be in startup/one-off initialization or (b) have a strong invariant + clear
  message. Otherwise, require `?` or explicit error handling.

- [ ] **`?` is used to propagate, not to hide.** When a function returns `Result<_, E>`,
  errors should be passed upward with `?` or mapped to a richer error.
  Manual `match` on `Result` just to rewrap the same error is a smell.

- [ ] **Errors carry context.** Check that `map_err` / `with_context` (or
  `anyhow::Context`) is used on I/O, parsing, network, or external calls, so you know
  *what* failed and *with which input*.

- [ ] **Application vs library error strategy is clear.**

  - Apps/CLIs: `anyhow` / `color-eyre` are ok for fast composition.

  - Libraries: strongly prefer typed errors (`thiserror`) or a small enum to keep API
    stable.

- [ ] **No silent discard of errors.** Look for `_ = some_fallible_call()` or `let _ =
  …;` patterns. These should be logged, bubbled, or explicitly documented as ignorable.

- [ ] **Async task errors are handled.** For `tokio::spawn(...)` or equivalent, the
  `JoinHandle` should be awaited or errors logged; don’t spawn-and-forget unless it’s
  truly fire-and-forget and documented.

- [ ] **Panic is intentional and documented.** If some code must panic (e.g. “this
  branch is unreachable due to X invariant”), require an inline comment or docstring to
  that effect.

* * *

## 3. Unsafe Code

- [ ] **Every `unsafe` block has a safety comment.** E.g. “// SAFETY: `ptr` was obtained
  from `alloc` and is still valid here.”
  Reject unsafe without such explanation.

- [ ] **Scope of unsafe is minimal.** Prefer `fn do_thing_unsafe(...) { unsafe { ... }
  }` over sprinkling unsafe across call sites.
  Contain it in one place so it can be audited.

- [ ] **Invariants are traceable.** If unsafe assumes non-null, alignment, non-aliasing,
  or length ≥ N, verify where that guarantee is established.
  Link to the call site or constructor that enforces it.

- [ ] **FFI calls validate inputs/outputs.** Check `extern "C"` or bindings for: correct
  types, error codes handled, C strings null-terminated, and no `&mut` aliasing of the
  same memory passed to C.

- [ ] **Safe alternative was actually considered.** If unsafe is used for performance,
  confirm that a safe standard-lib or crate alternative doesn’t exist — or that
  benchmarks justify this choice.

- [ ] **No unchecked indexing without reason.** If you see `get_unchecked` /
  `get_unchecked_mut`, require a clear argument why the index is always in range.

- [ ] **Unsafe does not leak UB to safe callers.** Public safe APIs must not expose
  footguns created inside unsafe blocks.

* * *

## 4. Abstraction & API Design

- [ ] **Traits are justified.** A trait with only one impl, no clear polymorphic call
  site, or no test seam is suspect.
  Ask: “Can this be a free function or a generic over `Fn` instead?”

- [ ] **No Java-style layering.** Avoid “service → manager → provider → adapter” stacks
  for simple operations.
  If the feature is simple, the code should be simple.

- [ ] **Public surface is minimal.** Modules should expose the smallest set of
  types/functions needed.
  Extra types should stay `pub(crate)` or private so the crate can evolve.

- [ ] **Modules are coherent.** Related types/functions live together.
  If a module mixes parsing, network calls, and business logic, suggest splitting.

- [ ] **APIs don’t force allocation.** Don’t make callers give you `String` when `&str`
  works; don’t return `Vec<T>` when an iterator or slice would do.
  Avoid “eager” APIs if lazy/streaming is possible.

- [ ] **Data ownership is clear in APIs.** For builder patterns or config structs,
  ensure it’s clear what the API keeps, what it borrows, and what gets consumed.

- [ ] **Enums over booleans for multi-state.** (Still an advanced rule.)
  If you see multiple related bools or “mode” bools in APIs, suggest an enum to make
  call sites self-describing.

- [ ] **Feature flags are contained.** If the crate supports features, ensure code
  doesn’t become a tangle of `#[cfg(feature = ...)]` inside business logic — push those
  to integration or boundary modules.

* * *

## 5. Performance & Efficiency

- [ ] **Hot paths are allocation-aware.** In loops or per-request logic, check for:
  `to_string()`, `collect::<Vec<_>>()`, `clone()`, `format!`, `String::new()` — each
  iteration. Suggest hoisting or reusing buffers.

- [ ] **Iterator/slice APIs are used.** Prefer `iter().map(...).collect()` or
  `slice.chunks()` over manual index loops that allocate temporaries.
  Idiomatic iterator chains are often clearer and compiled efficiently.

- [ ] **Right collection for the job.**

  - Frequent membership tests → `HashSet`

  - Sorted/range queries → `BTreeMap/BTreeSet`

  - Small, fixed-size, hot data → arrays/slices

  - Don’t use `Vec` + linear search by default if it’s on a hot path.

- [ ] **Async code doesn’t block.** Any `std::fs`, heavy CPU, or network-without-timeout
  inside `async fn` should be offloaded (`spawn_blocking`, dedicated workers).

- [ ] **Lock contention is minimized.** Long operations (I/O, parsing, network) must not
  run under a `Mutex`. Acquire, copy what’s needed, drop the lock, then do the slow
  work.

- [ ] **No unnecessary `Arc`/`Rc`.** If a value is only ever passed down, not shared,
  don’t wrap it. Atomic refcounting has a cost.

- [ ] **Avoid needless conversions.** Repeated `String` ↔ `&str` ↔ `PathBuf` ↔
  `OsString` with no need is a smell; stick to the most native type for the layer you’re
  in.

- [ ] **Check formatting cost.** Logging or user messages in tight loops should avoid
  repeated `format!` — pre-build strings or use structured logging with fields.

* * *

## 6. Idiomatic & Readable Code

- [ ] **Pattern matching for enums.** Replace long `if let Some(..)` / `if kind == ...`
  chains with a `match` that covers all variants.
  This also future-proofs for added variants.

- [ ] **Use `if let` / `while let` for option/result flows.** Don’t manually match just
  to extract the inner value.

- [ ] **No homegrown std reimpl.** If the code manually parses ints, walks directories,
  de/serializes JSON/TOML/YAML in an ad-hoc way — suggest std or well-known crate
  alternatives.

- [ ] **Names are domain-precise.** `process_data` / `handle_thing` → ask for a more
  descriptive name. Call things by the domain concept they represent.

- [ ] **Clarity over cleverness.** If a one-liner iterator chain is hard to read, ask to
  split it into named steps.

- [ ] **Consistent coding style across crate.** If the project uses builders, error
  enums, or newtypes, additions should follow the existing pattern — don’t introduce a
  new style for similar problems.

- [ ] **Dead code / unused features removed.** If a function exists “for later,” it
  should be behind a feature, documented, or removed.

* * *

## 7. Testing & Documentation

- [ ] **New logic → new tests.** Any non-trivial function, parser, or state machine
  should come with unit tests (including edge/boundary conditions).

- [ ] **Error paths are tested.** If the code constructs detailed errors, ensure at
  least one test asserts the error variant/message/context.

- [ ] **Integration tests for flows.** For multi-step flows (agents, async tasks,
  pipelines), prefer an integration test so regressions get caught at the orchestration
  level.

- [ ] **Doc comments on public items.** `pub fn`, `pub struct`, `pub enum` — should say
  what they do and (if relevant) what invariants/costs they have.

- [ ] **Comments are current.** Flag TODOs or comments that no longer describe the code.
  Outdated docs are worse than none.

- [ ] **Hard-to-test code is refactored.** If a reviewer can’t test it without spinning
  the whole world, suggest extracting pure logic into testable units and keeping
  I/O/glue thin.

* * *

## 8. Forbidden Practices (Confirm None Present)

- [ ] **No `unwrap()` / `expect()` in library or agent logic** without a strong,
  documented invariant.

- [ ] **No undocumented `unsafe`.** Every unsafe must explain its safety.

- [ ] **No “clone everywhere” to appease the borrow checker.** If you see `clone` in
  multiple adjacent lines, it likely needs design work.

- [ ] **No blocking I/O or heavy CPU inside `async fn`** (unless offloaded).

- [ ] **No over-generic / trait-heavy code for a single concrete use.** Simplicity
  first.

- [ ] **No global shared mutable state** where plain ownership or scoped state would
  work.

- [ ] **No unchecked indexing (`get_unchecked`) in user-facing / non-hot code** without
  proof and comment.

- [ ] **No silent error swallowing** (`let _ = ...;` without log or comment).

- [ ] **No “magic constants”** in logic without naming/explanation.

* * *

## 9. Reviewer Flow (How to Use This)

- [ ] **Start with ownership/borrowing**: can this be done with refs instead of
  clones/Arcs?

- [ ] **Then check error paths**: do we lose context or panic?

- [ ] **Then scan for unsafe**: are invariants documented and minimal?

- [ ] **Then look at abstraction**: are we adding traits/types we don’t need?

- [ ] **Then review performance**: any hot-path allocations / blocking / locks?

- [ ] **Then ensure idioms & tests**: code looks like Rust, not Java/Python; tests/docs
  added.

* * *

**Goal:** This checklist keeps the repo *idiomatic, auditable, and refactorable* in 6–12
months, even as the team grows and as Rust 2024+ features arrive.
