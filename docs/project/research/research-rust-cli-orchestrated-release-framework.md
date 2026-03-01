# Research: Reusable Rust CLI Release Orchestration Framework

**Date:** 2026-03-01

## Problem

Rust CLI projects often publish to multiple channels (GitHub Releases, crates.io, PyPI,
Homebrew). Independent workflows make partial success common and recovery hard.

Examples of failure mode:
- GitHub release succeeds, PyPI fails
- crates.io publishes, Homebrew is skipped or stale
- reruns create duplicate publish errors

## Recommendation

Use one orchestrator workflow (`release.yml`) that controls the full release DAG and
invokes reusable channel workflows.

Keep channel workflows reusable (`workflow_call`) so the same job logic can be run
standalone via `workflow_dispatch` for debugging.

## Target Architecture

```text
release.yml (orchestrator)
  |- plan (tag, mode, prerelease)
  |- build release artifacts + checksums
  |- call crates workflow (publish.yml)
  |- call PyPI workflow (pypi.yml)
  |- announce (create/update GitHub Release)
  '- homebrew update (only after channel success)
```

## Core Practices

### 1. Explicit dry-run mode

Support `workflow_dispatch` with defaults:
- `tag = dry-run`
- `publish = false`

Dry-runs should execute full build and packaging validation without pushing to external
registries.

### 2. Reusable channel workflows

Define channels as reusable workflows:
- `.github/workflows/publish.yml` for crates.io
- `.github/workflows/pypi.yml` for PyPI

Both should accept a `publish` boolean input.

### 3. Idempotent publish steps

Reruns must be safe.

- crates.io:
  - resolve crate name/version
  - check if version exists
  - skip publish if already present
- PyPI:
  - `uv publish --check-url https://pypi.org/simple/ ...`
  - skips already-uploaded files
- GitHub release:
  - create if missing
  - otherwise upload artifacts with `--clobber`
- Homebrew:
  - update formula only when content changes

### 4. Gated publish order

Make channel-side effects happen before announcement and Homebrew.

Suggested order:
1. Build + validate artifacts
2. Publish crates.io/PyPI
3. Create GitHub Release
4. Update Homebrew tap

This avoids the specific bad state where Homebrew points to a release before registries
are published.

### 5. Channel-specific sanity checks

Add checks that catch packaging regressions early:
- `cargo publish --dry-run --locked`
- wheel and sdist build smoke tests
- wheel-content checks (expected entrypoints)
- local install smoke (`--no-index --find-links`)

## Recovery Runbook

- rerun failed jobs:
  - `gh run rerun <run-id> --failed`
- rerun one job:
  - `gh run view <run-id> --json jobs --jq '.jobs[] | {name, databaseId}'`
  - `gh run rerun <run-id> --job <databaseId>`

If an incorrect version is already published to crates.io or PyPI, publish a new patch
version. Do not try to mutate immutable registry state.

## Trusted Publishing Notes

- crates.io trusted publisher should reference the crates workflow file path.
- PyPI trusted publisher should reference the PyPI workflow file path.
- no explicit GitHub environment is required for simple single-maintainer repos unless
  policy gates are desired.

## Reference Implementations

- Astral uv and ruff both use orchestrated release DAGs with publish gating and dry-run
  support.
- flowmark-rs applies the same pattern without cargo-dist, using custom workflows.

## Portable Template

For new projects, start with:
- `release.yml` orchestrator
- reusable `publish.yml` and `pypi.yml`
- optional `homebrew` update job after channel publish
- docs section for dry-run, publish, and rerun recovery

This yields a small, maintainable, and high-reliability release framework for Rust CLIs.
