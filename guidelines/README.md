# Guidelines

This directory has two distinct guideline groups:

1. standalone Rust rules for codebases written in Rust from the start or ported from
   another language;
2. porting rules for preserving behavior, mapping constructs, and synchronizing with a
   source implementation.

Load only the documents relevant to the task.
Playbooks under `playbooks/` provide step-by-step workflows; references under
`references/` provide lookup tables and schemas.

## General Rust Guidelines

These seven documents form the reusable Rust suite and are candidates for future tbd
guidelines.

| Guideline | Use it for |
| --- | --- |
| [`rust-rules.md`](rust-rules.md) | Language idioms, ownership, types, errors, modules, unsafe, async, and performance |
| [`rust-project-setup.md`](rust-project-setup.md) | Cargo packages, workspaces, toolchains, formatting, Clippy, CI, dependencies, and docs |
| [`rust-cli-rules.md`](rust-cli-rules.md) | CLI architecture, arguments, streams, exits, terminal behavior, configuration, and interruption |
| [`rust-filesystem-rules.md`](rust-filesystem-rules.md) | Safe mutation, atomic replacement, metadata, traversal, symlinks, and failure testing |
| [`rust-testing-rules.md`](rust-testing-rules.md) | Unit, integration, property, snapshot, async, feature, platform, and coverage testing |
| [`rust-release-rules.md`](rust-release-rules.md) | Release identity, artifacts, permissions, channels, trusted publishing, and incidents |
| [`rust-code-review-rules.md`](rust-code-review-rules.md) | Risk-ordered review process, severity, guideline routing, unsafe and FFI analysis, and actionable findings |

## Start a New Rust Project

Load `rust-rules.md` and `rust-project-setup.md`, then add only the focused guideline
for each surface the project actually contains.
For example, a library with no binary does not need the CLI rules, and an internal
service with no published artifacts does not need the release rules.

Apply each guideline as a default policy.
Record a concrete reason when project constraints require a different tool or rule.

## Improve or Review an Existing Rust Codebase

Load `rust-rules.md` plus the topic guidelines that match the changed files and runtime
boundaries. Load `rust-code-review-rules.md` last; it defines the review process and
severity model without repeating the topic rules.

Run the repository’s automated checks before spending review time on properties they
already establish. Report each remaining finding with severity, file and line evidence,
the violated contract, and a bounded correction.

## Porting Guidelines

These documents apply because a source implementation exists.
They should link to the general Rust suite for target-side implementation rules instead
of duplicating them.

| Guideline | Use it for |
| --- | --- |
| [`porting-principles-and-antipatterns.md`](porting-principles-and-antipatterns.md) | Parity scope, gap handling, test integrity, and agent process |
| [`python-to-rust-porting-rules.md`](python-to-rust-porting-rules.md) | Python-to-Rust sequencing, traceability, pitfalls, and acceptance |
| [`python-to-rust-cli-porting.md`](python-to-rust-cli-porting.md) | Python CLI flag, stream, error, and version parity |
| [`filesystem-heavy-cli-porting.md`](filesystem-heavy-cli-porting.md) | Cross-implementation filesystem contracts and full-state comparison |
| [`test-coverage-for-porting.md`](test-coverage-for-porting.md) | Source-suite preparation, construct enumeration, test mapping, and differential validation |

Construct-by-construct mappings live in
[`python-to-rust-mapping-reference.md`](../references/python-to-rust-mapping-reference.md),
and the complete execution workflow starts in
[`python-to-rust-playbook.md`](../playbooks/python-to-rust-playbook.md).

## tbd Guideline Readiness

The general Rust documents follow the tbd guideline shape: descriptive filenames,
frontmatter, a clear scope statement, actionable rules, examples, related-guideline
links, and the common documentation footer.
This repository remains their development home until a separate upstream change adds
selected documents to tbd itself.

The dated
[reuse review](../docs/reviews/rust-guideline-reuse-review-2026-08-08.md#tbd-upstream-recommendation)
owns the upstream grouping and order so this navigation index does not duplicate that
decision.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
