# Auto-Sync Agent Prompt Template

Use this prompt when the Rust port already exists and upstream Python has released a new
version.

**Use this first for sync work:** [`port-checklist-update-template.md`](port-checklist-update-template.md)

**Related:** [Meta Playbook](../_meta/meta-improving-this-playbook.md) |
[Playbook Phase 8](python-to-rust-playbook.md#phase-8-ongoing-synchronization) |
[Improvement Log](../_meta/playbook-improvement-log.md)

## Inputs Required

- Rust repo path
- Python upstream repo path/submodule path
- Current Python version currently ported
- Target upstream release/tag or commit
- Any known accepted divergences

## Prompt

```text
You are updating an existing Rust port from upstream Python changes.

Context:
- Rust repo: <RUST_REPO_PATH>
- Python source repo/submodule: <PYTHON_REPO_PATH>
- Current port baseline: Python <CURRENT_PYTHON_VERSION>
- Target upstream release: <TARGET_RELEASE_OR_COMMIT>
- Existing accepted divergences: <NONE_OR_LIST>

Primary objective:
Port all upstream changes from <CURRENT_PYTHON_VERSION> to <TARGET_RELEASE_OR_COMMIT>
while preserving parity requirements and using the established playbook process.

Required process:
1. Confirm baseline correspondence in repo metadata/docs before making changes.
2. Compute and summarize upstream diff from baseline to target:
   - changed modules/functions
   - changed tests
   - CLI/interface changes
   - dependency changes
3. Classify changes into:
   - bug fixes
   - new features
   - test additions/updates
   - refactors/no-op behavioral changes
4. Execute the full update workflow from:
   - playbooks/port-checklist-update-template.md
   - playbooks/python-to-rust-playbook.md (Phase 8)
   - relevant guidelines in guidelines/
5. Port changes in Rust with tests-first discipline and parity validation.
6. Run full validation gates (tests, cross-validation, lint/format/docs checks).
7. Update version correspondence and sync documentation.
8. Produce a final sync report with:
   - upstream diff summary
   - what was ported
   - any intentional divergences (with rationale)
   - validation results
   - unresolved blockers (if any)

Hard requirements:
- Do not skip changed upstream tests.
- Do not weaken assertions to pass tests.
- No unexplained output differences.
- If blocked by ambiguity, stop and ask for a decision with clear options.
```

## Expected Deliverables

- Filled copy of update checklist (`port-checklist-update-YYYY-MM-DD.md`)
- Sync report (`docs/python-sync-log.md` or project equivalent)
- Updated version correspondence metadata
- Test and parity validation evidence
