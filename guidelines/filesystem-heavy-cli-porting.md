---
title: Filesystem-Heavy CLI Porting
description: Parity rules for translating and cross-validating filesystem-mutating CLIs
---
# Filesystem-Heavy CLI Porting

Use this document when a source CLI and its Rust port create, rename, replace, back up,
restore, or delete files.
Target-side implementation rules live in
[`rust-filesystem-rules.md`](rust-filesystem-rules.md).
This document defines what must be mapped and compared across implementations.

## Inventory the Filesystem Contract

Before implementing the Rust side, record the source behavior for:

- accepted file, directory, glob, and stdin inputs;
- traversal order and excluded directories;
- symlink handling and whether links may escape the requested root;
- backup naming, replacement, retention, restore, and cleanup;
- collision policy for files and directories;
- permission, timestamp, ownership, and extended-metadata preservation;
- behavior across filesystem boundaries;
- dry-run output and confirmation prompts;
- partial-failure behavior and retry safety;
- output ordering, diagnostics, and exit codes.

Do not infer the contract from function names.
Run the pinned source implementation against fixtures that expose each behavior.

## Map Source Operations to Explicit Rust Policies

| Source behavior | Rust decision to document |
| --- | --- |
| in-place write | atomic replacement strategy and metadata policy |
| `shutil.copy2` backup | which metadata is preserved and what happens on collision |
| `os.walk` pruning | `walkdir::filter_entry` policy, ordering, and error propagation |
| string path manipulation | `Path`/`OsStr` operations and non-UTF-8 behavior |
| rename | same-filesystem atomic move and cross-device fallback policy |
| ignored filesystem error | whether parity requires an ignore, warning, or hard failure |
| glob order | deterministic sort key and platform normalization |
| symlink traversal | follow, copy link, operate on target, or reject |

If the source behavior is unsafe or ambiguous, first add a source-side test that fixes
the observed behavior.
Any intentional improvement on the Rust side is a documented parity exception, not an
implicit rewrite of the contract.

## Build a Full-State Fixture Matrix

Each fixture should declare both its initial tree and its expected final tree.
Cover at least:

- empty and nested directories;
- Unicode and non-UTF-8 names where the platform supports them;
- dotfiles and ignored directories;
- existing backups and destination collisions;
- files with read-only or executable permissions;
- symlinks to files, directories, missing targets, and external targets;
- an operation that fails after earlier targets succeeded;
- a cross-device move when the feature promises to support it;
- interrupted or simulated pre-commit failure;
- dry-run, undo, and cleanup modes.

Compare names, file types, bytes, links, relevant metadata, backups, diagnostics, and
exit codes. Comparing only final file contents misses much of the interface.

## Cross-Validate in Private Temporary Directories

Run the source and Rust implementations on separate copies of the same fixture.
Use one private temporary root and clean up that exact path.

```bash
#!/usr/bin/env bash
set -euo pipefail

run_root="$(mktemp -d "${TMPDIR:-/tmp}/filesystem-parity.XXXXXX")"
trap 'rm -rf -- "$run_root"' EXIT

source_root="$run_root/source"
rust_root="$run_root/rust"
cp -a test-fixtures/input/. "$source_root"
cp -a test-fixtures/input/. "$rust_root"

SOURCE_CMD=(uv run --project source-repo python -m example)
RUST_CMD=(cargo run --locked --)

"${SOURCE_CMD[@]}" "$source_root"
"${RUST_CMD[@]}" "$rust_root"
diff -r -- "$source_root" "$rust_root"
```

Adapt metadata comparison to the supported platforms.
Do not use predictable shared temporary paths or broad cleanup globs.

## Treat Error Behavior as Parity

For every mutation failure, compare:

- whether earlier writes remain visible;
- whether a temp file, backup, or lock remains;
- whether retrying repeats or corrupts work;
- the exit code and user-visible diagnostic;
- whether the source continues to later targets;
- whether dry-run detects the same conflict before mutation.

If the Rust implementation provides stronger atomicity, record exactly where behavior
differs and ensure callers are not depending on the weaker intermediate state.

## Acceptance Criteria

- [ ] Every filesystem operation has an explicit source behavior and Rust policy.
- [ ] Shared fixtures cover collision, symlink, metadata, ordering, and failure cases.
- [ ] Source and Rust runs use isolated copies of identical initial state.
- [ ] Final trees, diagnostics, and exit codes match or have tracked exceptions.
- [ ] Temporary test state is private and cleanup targets only that state.
- [ ] General Rust filesystem behavior follows
  [`rust-filesystem-rules.md`](rust-filesystem-rules.md).

## Related Guidelines

- [`rust-filesystem-rules.md`](rust-filesystem-rules.md)
- [`python-to-rust-cli-porting.md`](python-to-rust-cli-porting.md)
- [`test-coverage-for-porting.md`](test-coverage-for-porting.md)
- [`porting-principles-and-antipatterns.md`](porting-principles-and-antipatterns.md)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
