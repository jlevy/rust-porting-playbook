---
title: Rust Code Review Rules
description: A risk-ordered process for reviewing Rust correctness, soundness, APIs, and maintainability
author: Joshua Levy (github.com/jlevy) with LLM assistance
category: rust
---
# Rust Code Review Rules

Use this process after formatting, Clippy, tests, docs, and project-specific automated
checks pass. The topic guidelines own the rules for Rust code, projects, CLIs,
filesystems, tests, and releases.
This document defines how to load those rules, order the review, inspect unsafe
boundaries, assign severity, and report findings without restating each topic checklist.

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
A finding should name the violated contract, show evidence, and propose a bounded
correction.

## Load the Rules That Own the Changed Surface

Load `rust-rules.md` for every Rust review, then add only the documents that match the
diff and its runtime boundaries:

| Changed surface | Additional guideline |
| --- | --- |
| Cargo layout, toolchains, CI, dependencies, or repository automation | `rust-project-setup.md` |
| Arguments, streams, terminal behavior, subprocesses, or exits | `rust-cli-rules.md` |
| Paths, traversal, mutation, metadata, links, or recovery | `rust-filesystem-rules.md` |
| Test placement, fixtures, snapshots, matrices, or coverage | `rust-testing-rules.md` |
| Artifacts, publishing authority, channels, or incidents | `rust-release-rules.md` |

Also load the project’s own contracts and any language-agnostic tbd guidelines that
apply, such as `backward-compatibility-rules`, `error-handling-rules`, or
`supply-chain-hardening`. Do not review from this process document alone.

## Establish the Review Baseline

Before looking for findings:

1. Read the request, specification, linked issues, and repository instructions.
2. Inspect the full diff and enough surrounding code to understand changed control flow,
   ownership, failure paths, and external effects.
3. Run or inspect the required automated checks.
   Confirm how many tests ran and whether any selection was skipped.
4. Identify the public, persisted, cross-process, unsafe, and destructive contracts the
   change can affect.
5. Reproduce a suspected defect or trace an exact failing path before reporting it as
   fact.

Automated formatting or lint ownership should not consume manual review time unless the
automation is missing, disabled, or demonstrably failed.

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

Do not spend the review budget on low-risk style while a higher-risk boundary remains
unread.

## Review Unsafe Code and FFI

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
- [ ] **High: FFI ownership is unambiguous.** Allocation and free pairs, pointer
  lifetime, nullability, strings, callbacks, and thread affinity match the foreign
  contract.
- [ ] **High: A safe alternative was considered.** Performance-motivated unsafe code has
  representative benchmark evidence.
- [ ] **High: Platform layout assumptions are tested.** Sizes, alignment, calling
  convention, and generated bindings match supported targets.

For safe Rust, use the loaded topic guidelines instead of recreating their checklists
here.

## Write Findings That Can Be Acted On

Each finding should contain:

- a severity from the table above;
- the narrowest file and line range that demonstrates the problem;
- the violated behavior, invariant, or policy;
- the concrete consequence or failure path;
- a bounded fix that does not expand the requested scope unnecessarily.

Do not report a preference as a defect.
If evidence is incomplete, say what remains uncertain and what check would resolve it.
Group repeated instances under one root-cause finding when one correction addresses all
of them.

End the review with a short verdict, the validation evidence inspected, and any
remaining risks that could not be tested locally.

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
It does not replace reading the changed control flow, contracts, and topic guidelines.

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
