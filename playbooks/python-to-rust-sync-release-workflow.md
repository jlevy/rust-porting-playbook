# Python→Rust Sync Release Workflow

Use this workflow for an **existing Rust port** with an active upstream Python project.
It codifies the two-stage release pattern:

1. **Mode A: Rust-only stabilization release** (same Python baseline)
2. **Mode B: Upstream sync release** (new Python baseline)

This keeps releases lower risk and keeps version correspondence easy to audit.

**Related:** [Python-to-Rust Playbook](python-to-rust-playbook.md) |
[Update Checklist](port-checklist-update-template.md) |
[Auto-Sync Prompt Template](auto-sync-agent-prompt-template.md)

* * *

## Decision Gate

Choose release mode before writing code:

- **If Python baseline does not change:** Mode A
- **If Python baseline changes to a new release/tag/commit:** Mode B

Avoid mixing both modes in one release unless the change set is trivial.

## Mode A: Rust-Only Stabilization Release

Use when you need a clean Rust release pinned to the current Python baseline.

Typical scope:
- docs cleanup
- internal refactors
- build/release pipeline hardening
- parity bug fixes against the current baseline

Required sequence:

1. Record current Python baseline from Rust metadata/docs.
2. Confirm baseline will remain unchanged for this release.
3. Implement Rust-only changes.
4. Run full validation:
   - Rust tests and quality gates
   - **differential parity sweep** vs the current Python baseline: both binaries over a
     diverse corpus, full untruncated diff, plus class-level truth tables for any
     discrepancy. This is how latent parity bugs (independent of any upstream change)
     are found — a clean test suite does not prove parity.
   - mapping/completeness checks (if used by project)
5. Prepare release notes clearly stating:
   - Python baseline unchanged
   - nature of Rust-only improvements
6. Cut Rust release.
7. Update sync log with a “stabilization release” entry.

Mode A acceptance gates:
- Python baseline metadata unchanged
- differential parity sweep run; zero unexplained parity diffs vs current baseline
- release pipeline green

## Mode B: Upstream Sync Release

Use when upstream Python has a new version and you are updating Rust to match it.

Required sequence:

1. Identify baseline and target Python versions/tags/commits.
   See
   [auto-sync-agent-prompt-template.md → Auto-detecting the target](auto-sync-agent-prompt-template.md#auto-detecting-the-target)
   for a snippet that diffs the current parity baseline against upstream’s latest tag.
2. Produce baseline->target diff summary artifact.
3. Categorize changes:
   - bug fixes
   - features
   - test changes
   - refactors/no-op behavior changes
4. **For each upstream behavior change, verify against the existing Rust binary *before*
   concluding code must change (bidirectional).** The divergence between a replaced
   library and the original runs both ways:
   - the Rust library may *already* implement the upstream fix → port the tests only,
     do not auto-port the implementation change;
   - the Rust library may carry its *own* divergence the original never had → a genuine
     parity bug that the upstream diff will never reveal.
   Port the upstream tests regardless — they are the parity contract going forward.
5. **Run a mandatory differential parity sweep (step shared with Mode A).** Do not rely
   on triage: run both binaries over a diverse corpus, diff every file with the full
   (untruncated) output, and build a class-level truth table for any discrepancy. A
   sync that touches no formatter code can still ship latent parity bugs because the
   replacement library's behavior is independent of the upstream diff. For each real
   divergence, consult upstream `main`/unreleased to decide which side is canonical,
   then write a discriminating test (red→green) before fixing.
6. For each new FEATURE: port the behavior, port ALL of its tests, and add the new
   Python tests to the test-mapping manifest so completeness checks stay green.
7. Execute [port-checklist-update-template.md](port-checklist-update-template.md)
   end-to-end.
8. Update version correspondence metadata to target baseline.
9. **If the sync changed the public Rust API, check the published crates.io baseline
   (`cargo search`) and `cargo-semver-checks` early.** A breaking change at the same
   published version blocks CI. Decide with the maintainer: bump the version to match the
   change class, or, for a deliberate small break in a pre-1.0 / no-downstream-users crate,
   allow the specific lint in `Cargo.toml`
   (`[package.metadata.cargo-semver-checks.lints]`) so the rest of the API stays gated.
   This otherwise surfaces only as a late, confusing CI failure.
10. Cut release and publish sync report.

Mode B acceptance gates:
- no skipped changed upstream tests without documented rationale
- if the public Rust API changed: crates.io baseline + `cargo-semver-checks` checked, and
  a version bump or maintainer-approved lint allowance decided
- differential parity sweep run (corpus + class truth tables), with every diff either
  resolved or recorded as an approved tolerated variation
- new features: behavior + tests ported, mapping manifest updated, completeness green
- version correspondence updated
- release pipeline green

## Suggested Cadence

When both internal cleanups and new upstream Python changes exist:

1. Run **Mode A** first and release.
2. Then run **Mode B** and release.

This produces cleaner changelogs and simpler rollback boundaries.

## Agent Prompts (Minimal)

### Mode A Prompt

```text
Prepare a Rust-only stabilization release for an existing Python->Rust port.

Constraints:
- Keep Python baseline version/tag/commit unchanged.
- Scope to Rust-only improvements (docs, cleanup, build/release hardening, parity fixes).

Required:
1. Confirm and record current Python baseline.
2. Implement Rust-only changes.
3. Run full tests/parity/quality/release checks.
4. Produce release notes explicitly stating baseline unchanged.
5. Update sync log and provide validation evidence.
```

### Mode B Prompt

Use the template in
[auto-sync-agent-prompt-template.md](auto-sync-agent-prompt-template.md).

## Required Artifacts

For either mode, produce:

- release-mode declaration (`Mode A` or `Mode B`)
- validation evidence summary
- updated changelog/release notes
- updated sync/version correspondence records
