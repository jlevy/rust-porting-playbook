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
   - parity/cross-validation against current Python baseline
   - mapping/completeness checks (if used by project)
5. Prepare release notes clearly stating:
   - Python baseline unchanged
   - nature of Rust-only improvements
6. Cut Rust release.
7. Update sync log with a “stabilization release” entry.

Mode A acceptance gates:
- Python baseline metadata unchanged
- zero unexplained parity diffs vs current baseline
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
   concluding code must change.** The Rust port may use a different parser/library that
   already implements the upstream fix.
   Port the tests regardless — they’re the parity contract going forward — but do not
   auto-port the implementation change.
5. Execute [port-checklist-update-template.md](port-checklist-update-template.md)
   end-to-end.
6. Update version correspondence metadata to target baseline.
7. Cut release and publish sync report.

Mode B acceptance gates:
- no skipped changed upstream tests without documented rationale
- zero unexplained parity diffs
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
