---
title: Rust Code Review Rules
description: A severity-ranked review checklist for Rust correctness, soundness, APIs, async behavior, and maintainability
category: rust
---
# Rust Code Review Rules

Use this checklist after formatting, Clippy, tests, docs, and project-specific automated
checks pass. It focuses on properties tools do not establish reliably: ownership design,
unsafe invariants, public contracts, failure behavior, concurrency, performance, and
long-term maintainability.

**Related:** [`rust-rules.md`](rust-rules.md),
[`rust-project-setup.md`](rust-project-setup.md), and `tbd shortcut review-code`.

## Severity

| Tag | Meaning |
| --- | --- |
| **Blocker** | Must fix before merge; correctness, security, or soundness failure |
| **High** | Strongly recommended; substantial API, reliability, or maintenance risk |
| **Medium** | Should fix; idiom, clarity, test, or moderate design concern |
| **Low** | Optional improvement with a concrete benefit |

Assign severity from impact and likelihood, not personal preference.
A review finding should name the violated contract, show evidence, and propose a bounded
correction.

## Review the Highest-Risk Boundaries First

Review in this order unless the change has a more specific risk profile:

1. unsafe code and FFI;
2. data loss, authentication, authorization, and destructive operations;
3. errors, partial failure, and recovery;
4. public APIs and compatibility;
5. concurrency, cancellation, and shutdown;
6. ownership and resource lifetimes;
7. dependencies and build-time execution;
8. performance-sensitive paths;
9. tests, docs, organization, and idiom.

Do not spend the review budget on formatting that automated checks already own while a
high-risk boundary remains unread.

## Ownership and Resource Lifetimes

- [ ] **High: Clones are deliberate.** Each meaningful `.clone()` reflects required
  ownership or a measured cheap value, not an attempt to silence the borrow checker.
- [ ] **Medium: APIs borrow when they only read.** Owned arguments are consumed, stored,
  or otherwise justified.
- [ ] **High: `'static` bounds describe real lifetime needs.** They are not used as a
  catch-all to make spawned work compile.
- [ ] **High: Shared ownership is necessary.** `Rc`, `Arc`, `Mutex`, and `RwLock` model
  actual sharing, and lock guards do not escape public APIs.
- [ ] **High: Resource cleanup runs on every path.** Files, temp state, transactions,
  subprocesses, tasks, permits, and locks are released after success and failure.
- [ ] **Medium: Borrow scopes are narrow.** Long borrows do not force unrelated state
  into clones or broad locks.
- [ ] **Medium: Builders and state transitions make ownership clear.** Callers can tell
  which values are borrowed, retained, consumed, or returned.

## Errors and Recovery

- [ ] **Blocker: No required error is silently discarded.** `let _ =` and ignored task
  results have a reviewed reason or are handled.
- [ ] **High: Errors retain context and causes.** I/O, parsing, network, subprocess, and
  registry errors identify the failed operation and relevant non-secret input.
- [ ] **High: Library errors are matchable where callers recover.** Applications may use
  report-style errors at their outer boundary.
- [ ] **High: Success is reported only after every required operation succeeds.**
  Partial results, cleanup failures, and publish failures cannot fall through to a
  success message.
- [ ] **High: Retry behavior distinguishes transient and permanent failures.** Retries
  are bounded, idempotent, and observable.
- [ ] **High: Destructive partial failure has a recovery story.** The user can identify
  completed work and restore or resume safely.
- [ ] **Medium: Panics express violated programmer invariants.** Normal invalid input
  and external failure return errors.
- [ ] **Medium: `expect` messages explain the invariant.** Unexplained `unwrap` and
  `expect` calls are removed from production paths.

## Unsafe Code and FFI

- [ ] **Blocker: Every unsafe block has a specific `// SAFETY:` argument.** The stated
  invariant is established by code the reviewer can trace.
- [ ] **Blocker: Unsafe scope is minimal.** A safe wrapper prevents callers from
  violating the invariant.
- [ ] **Blocker: Safe inputs cannot trigger undefined behavior.** Length, alignment,
  aliasing, initialization, provenance, and lifetime requirements are enforced.
- [ ] **Blocker: Manual `Send` or `Sync` implementations are sound.** Every contained
  field and mutation path is considered.
- [ ] **Blocker: Unwinding across FFI is prevented or explicitly supported.** Panic and
  foreign-exception behavior is defined.
- [ ] **High: FFI ownership is unambiguous.** Allocation/free pairs, pointer lifetime,
  nullability, strings, callbacks, and thread affinity match the foreign contract.
- [ ] **High: A safe alternative was considered.** Performance-motivated unsafe code has
  representative benchmark evidence.
- [ ] **High: Platform layout assumptions are tested.** Sizes, alignment, calling
  convention, and generated bindings match supported targets.

## Public API and Compatibility

- [ ] **High: The public surface is no larger than required.** Internal items use
  private or `pub(crate)` visibility.
- [ ] **High: Public changes have a compatibility disposition.** Removed items, new
  trait bounds, changed defaults, feature changes, and altered re-exports are assessed
  against project policy.
- [ ] **High: Important return values are difficult to ignore.** `#[must_use]` is
  applied where omission is likely a bug.
- [ ] **Medium: Types encode valid states.** Enums and newtypes replace sentinel values,
  related booleans, and loosely coupled primitives.
- [ ] **Medium: APIs do not force avoidable allocation.** Borrowed input, slices, and
  iterators are used where they fit the contract.
- [ ] **Medium: Traits have a polymorphic consumer.** Single-use indirection is removed
  unless it is a deliberate public extension or test seam.
- [ ] **Medium: Feature flags stay at boundaries.** Business logic is not tangled with
  scattered `cfg` branches.
- [ ] **Medium: Serialization and on-disk formats remain compatible or migrate
  explicitly.** Round-trip and older-version fixtures cover the change.

Apply `tbd guidelines backward-compatibility-rules` when compatibility is in scope.

## Concurrency and Async

- [ ] **Blocker: Async code does not perform blocking I/O or heavy CPU work on the
  executor.** Blocking work uses a bounded dedicated path.
- [ ] **Blocker: Lock ordering cannot deadlock.** Multiple-lock paths share one order or
  are redesigned.
- [ ] **High: No slow I/O or unrelated await occurs while holding a lock.** Critical
  sections contain only protected state transitions.
- [ ] **High: Spawned tasks are awaited or supervised.** Failures cannot disappear.
- [ ] **High: Cancellation is safe at every relevant await.** Dropping a future does not
  leave corrupt state or leaked ownership.
- [ ] **High: Shutdown is defined.** The system stops intake, signals workers, and
  drains or cancels in-flight work according to policy.
- [ ] **Medium: Queues and spawning are bounded.** Load produces backpressure rather
  than unbounded memory or task growth.
- [ ] **Medium: Atomic ordering is justified.** `Relaxed` and stronger orderings match a
  documented synchronization argument.

## Filesystem, Subprocess, and External Boundaries

- [ ] **Blocker: Destructive scope is resolved exactly.** No broad path, unresolved
  environment variable, or unvalidated glob identifies deletion targets.
- [ ] **High: Writes are atomic or explicitly non-atomic.** Metadata, backup, collision,
  and crash-durability policies are stated.
- [ ] **High: Traversal errors are not silently dropped.** Symlink and root-boundary
  behavior is explicit.
- [ ] **High: Subprocesses use argument vectors.** Shell interpretation is used only
  when it is the requested feature.
- [ ] **High: Exit status, stdout, and stderr are all checked.** A spawned command
  cannot fail while the caller reports success.
- [ ] **Medium: Timeouts terminate and reap subprocesses.** Child processes and pipes do
  not leak after cancellation.
- [ ] **Medium: Environment inheritance is intentional.** Secrets and ambient flags are
  removed when the child should run reproducibly.

See [`rust-filesystem-rules.md`](rust-filesystem-rules.md) and
[`rust-cli-rules.md`](rust-cli-rules.md).

## Performance and Efficiency

- [ ] **High: Performance claims have representative measurements.** Benchmarks include
  inputs, toolchain, target, and relevant environment.
- [ ] **High: Hot paths avoid accidental allocation.** Repeated `clone`, `to_string`,
  `format!`, and `collect` calls are justified or removed.
- [ ] **High: Lock contention is measured or structurally bounded.** Slow operations do
  not serialize unrelated work.
- [ ] **Medium: Collections match access patterns.** Simpler structures remain preferred
  for small bounded data.
- [ ] **Medium: Parsing and serialization do not repeat avoidable work.** Reusable state
  is cached only with a clear invalidation and memory policy.
- [ ] **Medium: Optimizations preserve readability or carry evidence explaining the
  tradeoff.** Cleverness without a measured need is removed.

## Dependencies and Supply Chain

- [ ] **Blocker: New build-time execution is identified.** `build.rs`, proc macros,
  native build tools, generators, and install scripts are reviewed.
- [ ] **High: Every new dependency has a concrete need.** Maintenance signals or
  popularity alone are not a trust argument.
- [ ] **High: New and upgraded versions satisfy cool-off policy or have a recorded
  exception.** Exact source and release diffs were reviewed.
- [ ] **High: Lockfile and source policy are preserved.** Registry, git, path, and
  vendored dependencies match project rules.
- [ ] **High: Licenses and advisories pass policy.** RustSec and cross-ecosystem
  evidence are both considered where applicable.
- [ ] **Medium: Enabled features are minimal.** Heavy default features and native code
  are not pulled in accidentally.
- [ ] **Medium: Duplicate and unused dependencies are understood.** Tool output is
  verified before changing manifests.
- [ ] **Medium: The declared MSRV still resolves and builds.** Dependency upgrades do
  not silently raise it.

Apply `tbd guidelines supply-chain-hardening`.

## Tests and Documentation

- [ ] **High: Changed behavior has direct evidence.** Tests cover success, failure, and
  relevant boundaries.
- [ ] **High: Regression tests fail without the fix.** A passing test that never reaches
  the changed branch is insufficient.
- [ ] **High: Supported feature, toolchain, and platform combinations are exercised by
  policy.** Empty or skipped selections cannot appear green.
- [ ] **Medium: Tests assert behavior rather than implementation detail.** Refactors can
  preserve the suite when the contract is unchanged.
- [ ] **Medium: Public docs describe invariants, errors, and costs.** Examples compile
  as doctests where practical.
- [ ] **Medium: Ignored and flaky tests have current tracking issues or beads and
  unblock conditions.**
- [ ] **Medium: Comments describe the present code.** Stale migration or refactor notes
  are removed.

See [`rust-testing-rules.md`](rust-testing-rules.md).

## Quick Scan

| Pattern | Default severity |
| --- | --- |
| unsafe block without a safety argument | Blocker |
| safe API can trigger undefined behavior | Blocker |
| required error or task result discarded | Blocker |
| blocking work inside async executor | Blocker |
| destructive operation with unresolved scope | Blocker |
| success printed before all required work is verified | High |
| unexplained production `unwrap` or `expect` | High |
| repeated clones to satisfy borrowing | High |
| lock held across I/O or await | High |
| public item used only inside the crate | High |
| mutable or unreviewed build dependency pin | High |
| ignored test without a tracking issue or bead | Medium |
| `#[allow]` without a non-obvious reason | Medium |
| trait or abstraction without a consumer | Medium |
| TODO, FIXME, or HACK without tracking | Medium |

The quick scan identifies where to investigate.
It does not replace reading the changed control flow and contracts.

## Related Guidelines

- [`rust-rules.md`](rust-rules.md)
- [`rust-project-setup.md`](rust-project-setup.md)
- [`rust-cli-rules.md`](rust-cli-rules.md)
- [`rust-filesystem-rules.md`](rust-filesystem-rules.md)
- [`rust-testing-rules.md`](rust-testing-rules.md)
- [`rust-release-rules.md`](rust-release-rules.md)
- `tbd shortcut review-code`
- `tbd guidelines backward-compatibility-rules error-handling-rules supply-chain-hardening`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
