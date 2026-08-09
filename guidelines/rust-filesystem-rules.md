---
title: Rust Filesystem Rules
description: Rules for safe, deterministic, and testable filesystem operations in Rust
category: rust
---
# Rust Filesystem Rules

Use these rules for Rust code that reads directory trees or mutates files, directories,
links, or metadata. Filesystem code crosses process, platform, and failure boundaries;
its API must state more than the happy-path bytes.

**Related:** [`rust-rules.md`](rust-rules.md), [`rust-cli-rules.md`](rust-cli-rules.md),
and [`rust-testing-rules.md`](rust-testing-rules.md).

## Use Filesystem-Native Types

- Accept `&Path` for borrowed paths and `PathBuf` for owned paths.
- Preserve `OsStr` and `OsString` when names do not need to be Unicode.
- Use `join`, `strip_prefix`, `parent`, `file_name`, and `with_extension`; do not parse
  path separators with string operations.
- Remember that `with_extension` replaces the final extension.
  Append a suffix through `OsString` when `archive.tar.gz` must become
  `archive.tar.gz.old`.
- Define whether relative paths are interpreted against the process directory, a
  workspace root, or an explicit base.
- Canonicalize only when resolving links and requiring existence is the intended
  behavior. Canonicalization changes semantics and can expose paths outside a root.

```rust
use std::ffi::OsString;
use std::path::{Path, PathBuf};

fn append_suffix(path: &Path, suffix: &str) -> PathBuf {
    let mut value = OsString::from(path.as_os_str());
    value.push(suffix);
    PathBuf::from(value)
}
```

## Separate Planning From Mutation

For multi-target or destructive operations, compute a plan first.
The plan should contain resolved sources, destinations, collisions, exclusions, and the
action for each target.

- Validate the whole plan before writing where the contract requires all-or-nothing
  behavior.
- Make dry-run render the same plan the executor consumes.
- Do not rediscover paths independently during execution unless concurrent changes are
  part of the design.
- Revalidate security-sensitive assumptions immediately before mutation.
- Return structured per-target outcomes for partial-success operations.

This separation makes review, confirmation, deterministic output, and failure testing
substantially easier.

## Distinguish Atomic Visibility From Crash Durability

An atomic rename prevents observers from seeing a partially written destination.
It does not by itself guarantee that bytes and directory entries survive a power loss.
State which property the operation promises.

A common same-filesystem replacement sequence is:

1. create a private temp file in the destination directory;
2. write all bytes and flush the writer;
3. copy required permissions to the temp file;
4. sync the temp file when crash durability is required;
5. atomically replace the destination using a platform-appropriate operation;
6. sync the parent directory where supported and required.

```rust
use std::io::Write;
use std::path::Path;
use tempfile::NamedTempFile;

fn stage_replacement(path: &Path, content: &[u8]) -> anyhow::Result<NamedTempFile> {
    let directory = path.parent().unwrap_or_else(|| Path::new("."));
    let mut staged = NamedTempFile::new_in(directory)?;
    staged.write_all(content)?;
    staged.flush()?;
    staged.as_file().sync_all()?;
    Ok(staged)
}
```

The final replacement call and overwrite semantics differ by platform and crate API.
Review that exact operation rather than assuming every rename overwrites atomically.

## Make Metadata Policy Explicit

Decide whether replacement preserves:

- permissions and executable bits;
- ownership;
- timestamps;
- extended attributes and access-control lists;
- hard-link relationships;
- sparse-file or platform-specific attributes.

Preserving content and preserving a file are different contracts.
Copy only the metadata the feature promises, and test it on supported platforms.

## Choose Backup and Collision Policies Before Writing

- Define whether an existing backup is replaced, versioned, reused, or an error.
- Never derive backup names through lossy path conversion.
- Make restore behavior explicit when both the backup and destination exist.
- For rename collisions, choose fail, deterministic suffix, or explicit overwrite.
- Bound suffix searches or make cancellation possible; do not hide an unbounded search
  in a critical operation.
- Create destination parents only when the command contract says it may.
- Record enough information to undo a batch when undo is a supported feature.

Do not make overwrite the fallback for an unhandled collision.

## Treat Cross-Device Moves as Copy Operations

An ordinary rename can fail when source and destination are on different filesystems.
A copy-then-delete fallback is not atomic and introduces new failure states.

If cross-device moves are supported:

1. copy to a temp file in the destination directory;
2. validate bytes and required metadata;
3. commit the destination atomically;
4. remove the source only after the destination is durable enough for the contract;
5. report and preserve recoverable state if source removal fails.

If these semantics are not supported, fail clearly without partially copying.

## Traverse Deterministically and Propagate Errors

- Use `filter_entry` to prune excluded directory subtrees before descent.
- Sort by a documented key when output or mutation order is observable.
- Decide whether symlinks are followed; do not inherit a library default accidentally.
- Detect link cycles when following directory symlinks.
- Do not use `filter_map(Result::ok)` when unreadable paths matter.
  It silently drops errors and can turn incomplete work into apparent success.
- Keep traversal and mutation separate when deleting or renaming entries could change
  what remains to be visited.

```rust
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

fn regular_files(root: &Path) -> anyhow::Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    for entry in WalkDir::new(root).follow_links(false) {
        let entry = entry?;
        if entry.file_type().is_file() {
            files.push(entry.into_path());
        }
    }
    files.sort();
    Ok(files)
}
```

## Define Symlink and Root-Boundary Behavior

Before operating recursively, decide whether each operation acts on a link, its target,
or neither.

- Avoid following links outside an authorized root unless that is explicitly allowed.
- Check the resolved target after link resolution, not only the lexical input path.
- Expect time-of-check/time-of-use races when untrusted users can mutate the tree.
- Use directory-relative or capability-oriented APIs for adversarial trees when the
  standard path APIs cannot enforce the security boundary.
- Never recursively delete a path whose exact resolved scope has not been verified.

## Report Partial Failure Honestly

Batch operations should return enough information to identify completed, skipped, and
failed targets.

- Do not print success merely because at least one target changed.
- Preserve the first error and relevant later errors without losing context.
- State whether execution stops at the first failure or continues collecting failures.
- Make retry behavior explicit and idempotent where possible.
- Leave temporary and backup files in a documented recoverable state or clean them up
  deterministically.

## Test the State Machine, Not Just Final Bytes

Use an isolated `tempfile::TempDir` for every mutating test.
Test:

- empty, nested, Unicode, and platform-specific paths;
- destination and backup collisions;
- permissions and other promised metadata;
- files, directories, symlinks, and broken links;
- failure before commit, during commit, and after destination commit;
- cross-device behavior when supported;
- deterministic traversal and result ordering;
- dry-run equivalence with the executed plan;
- retry, undo, cleanup, and partial-batch outcomes.

A test that asserts only `old == content || new == content` does not prove atomicity.
Inject a failure before the commit point and verify that observers retain the original
destination and no success is reported.

## Related Guidelines

- [`rust-rules.md`](rust-rules.md)
- [`rust-cli-rules.md`](rust-cli-rules.md)
- [`rust-testing-rules.md`](rust-testing-rules.md)
- [`filesystem-heavy-cli-porting.md`](filesystem-heavy-cli-porting.md) for parity with a
  source implementation
- `tbd guidelines error-handling-rules general-testing-rules`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
