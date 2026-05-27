# Auto-Sync Agent Prompt Template

Use this prompt when the Rust port already exists and upstream Python has released a new
version.

**Use this first for sync work:**
[`port-checklist-update-template.md`](port-checklist-update-template.md).

For two-stage release planning (Rust-only stabilization release first, then upstream
sync), see
[`python-to-rust-sync-release-workflow.md`](python-to-rust-sync-release-workflow.md).

**Related:** [Meta Playbook](../_meta/meta-improving-this-playbook.md) |
[Playbook Phase 8](python-to-rust-playbook.md#phase-8-ongoing-synchronization) |
[Improvement Log](../_meta/playbook-improvement-log.md)

## Inputs Required

- Rust repo path
- Python upstream repo path/submodule path
- Current Python version currently ported
- Target upstream release/tag or commit
- Any known accepted divergences

### Auto-detecting the target

If the target is not given, an agent can discover it from the upstream submodule:

```bash
# Project-specific: read the current pinned baseline. Adapt path/keys for your repo.
BASELINE=$(grep -A1 '\[package.metadata.parity\]' Cargo.toml | grep version | sed 's/.*"\(.*\)"/\1/')
git -C <PYTHON_REPO_PATH> fetch --tags >/dev/null
LATEST=$(git -C <PYTHON_REPO_PATH> tag -l 'v[0-9]*' | sort -V | tail -1)
echo "Baseline: v${BASELINE} | Latest upstream: ${LATEST}"
```

If `LATEST > v${BASELINE}`, the target is `LATEST`. If equal, no sync is needed
(consider Mode A from `python-to-rust-sync-release-workflow.md` instead).

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
4. **Empirical pre-port verification (bidirectional).** Before porting any code
   change, run the new upstream tests (or representative inputs) against the
   *existing* Rust binary and record the result for each one.
   - If the new tests already pass, the upstream code change is not required in
     Rust — port the tests only. (Common when the Rust port uses a different
     parser/library that already implements the upstream fix.)
   - **But the replacement library can also DIVERGE the other way**: it may carry
     its own behavior the original never had. Verifying "comrak already does the
     upstream fix" is necessary but NOT sufficient. You must also confirm the Rust
     binary does not differ from Python on inputs the upstream diff never touched.
     That requires the differential sweep in step 5 — do not skip it just because
     the triage says "no code change needed."
5. **Mandatory differential parity sweep — even for "tests-only" / "metadata-only"
   syncs.** A sync that touches no formatter code can still ship with latent parity
   bugs, because the replacement library's behavior is independent of the upstream
   diff. Run a real differential, do not reason about it:
   - Corpus sweep: run BOTH binaries over a directory of diverse real documents and
     diff every file. Capture the FULL diff (never truncate with `head`/`basename`/
     `grep -c` — see Principle 2). Investigate every non-empty diff.
   - Class sweep (truth table): for any discrepancy found, enumerate the whole class
     it belongs to (e.g. every reference-link form: shortcut, collapsed, full,
     label==text, uppercase, no-definition) and build a truth table of
     `input → Python output → Rust output` before fixing. See Principle 8.
   - For each real divergence, decide which side is canonical (step 6), write a
     discriminating test (red→green), then fix.
6. **Deciding which side is correct — consult upstream `main`/unreleased as an
   oracle.** When Python and Rust differ and it is unclear which is right, check
   whether upstream has already fixed it on `main` or in a release newer than the
   target tag (e.g. `git log <target>..origin/main`, issue/PR references). An
   existing upstream fix is the authoritative statement of intended behavior. Per
   Principle 1, adopting a not-yet-released upstream fix (diverging from the pinned
   baseline) requires maintainer approval; record it as a documented tolerated
   variation when approved.
7. Execute the full update workflow from:
   - playbooks/port-checklist-update-template.md
   - playbooks/python-to-rust-playbook.md (Phase 8)
   - relevant guidelines in guidelines/
8. Port changes in Rust with tests-first discipline and parity validation. For each
   new upstream FEATURE: port the behavior, port ALL of its tests, and add the new
   Python tests to the test-mapping manifest so completeness checks stay green.
9. Run full validation gates (tests, cross-validation, lint/format/docs checks).
10. Update version correspondence and sync documentation.
11. Produce a final sync report with:
    - upstream diff summary
    - per-change Rust impact (using the table format below)
    - what was ported
    - any intentional divergences (with rationale)
    - validation results (each command + exit status)
    - unresolved blockers (if any)

Hard requirements:
- Do not skip changed upstream tests.
- Do not weaken assertions to pass tests.
- No unexplained output differences.
- Run the differential parity sweep regardless of how small the triage looks.
- If blocked by ambiguity, stop and ask for a decision with clear options.

When the upstream change targets a library or framework that the Rust port
replaced with a different one (e.g. Python `marko` vs Rust `comrak`), DO NOT
auto-port the implementation change. The divergence is bidirectional:
- The replacement may ALREADY implement the upstream fix → port the tests only.
- The replacement may have its OWN divergence the original never had → that is a
  genuine parity bug in the port that the upstream diff will never reveal; only the
  differential sweep (step 5) catches it.
Verify the new tests against the existing Rust binary AND run the differential
sweep. Port the upstream tests regardless — they are the parity contract going
forward.
```

### Per-change Rust impact table format

The sync report should categorize each upstream change with its concrete Rust effect.
Use this table format:

| Upstream commit | Type | Rust impact |
| --- | --- | --- |
| `<sha>` | fix / feat / docs / test / refactor | None — comrak already handles it. Tests ported. |
| `<sha>` | feat(cli) | None — Rust already emits the new behavior. Tests ported. |
| `<sha>` | feat | New `--xyz` flag added to `src/main.rs`; tests ported. |
| `<sha>` | docs | None applicable to Rust. |

The table makes “what we changed in Rust for this upstream commit” reviewable at a
glance, and makes “tests-only” syncs auditable rather than mysterious.

### Sync artifact naming convention

Save the diff summary + per-change table + validation evidence to a single artifact at:

```
<rust-repo>/docs/sync-artifacts/YYYY-MM-DD-sync-v<BASELINE>-to-v<TARGET>.md
```

Recommended sections in the artifact:

1. Baseline and target tags / commits
2. Upstream commits in range (from `git log --oneline <baseline>..<target>`)
3. Changed files (from `git diff --name-status`)
4. Per-change Rust impact (the table above)
5. Test fixture changes (or “none — fixtures byte-identical between versions”)
6. Required Rust update checklist (with `[x]` as items complete)
7. Validation evidence (each gate command + result)
8. User-reported regressions investigated, if any (see “Cross-binary churn”, below)

### Cross-binary churn investigation (user-reported)

When users report diff churn between Python and Rust binaries on real-world documents,
the first step is *always* to confirm both binaries are at the same parity surface.
Frequently the churn is from running mismatched flowmark versions across formatting
passes (older Python vs newer Rust, or vice versa), not a true parity bug.
The investigation routine:

```bash
# Both binaries on the same input
flowmark --auto sample.md            # produces output A
./target/release/flowmark --auto sample.md  # produces output B
diff sample-A.md sample-B.md
```

If the diff is empty, the user’s churn is version-mismatch, not a parity gap.
If the diff is non-empty *and* parity is supposed to hold, the case is a genuine
regression and must be tested + fixed before the sync ships.

Do not stop at one sample. Promote this to the full corpus sweep (step 5 of the
prompt): run both binaries over a directory of diverse real documents and diff every
file, capturing the complete output. A single-file check passing does not mean parity
holds — the two clean parity bugs found during the flowmark v0.6.5 sync (thematic-break
spacing and reference-link normalization) were both invisible to the upstream diff and
only surfaced under a full corpus + class-level truth-table sweep.

## Expected Deliverables

- Filled copy of update checklist (`port-checklist-update-YYYY-MM-DD.md`)
- Sync report (`docs/python-sync-log.md` or project equivalent)
- Updated version correspondence metadata
- Test and parity validation evidence

## Minimal Prompt (Copy/Paste)

```text
Update this existing Rust port to match a newer upstream Python release.

Inputs:
- Rust repo path: <RUST_REPO_PATH>
- Python source path: <PYTHON_REPO_PATH>
- Current Python baseline in Rust: <CURRENT_PYTHON_VERSION>
- Target upstream Python release/commit: <TARGET_RELEASE_OR_COMMIT>
- Known accepted divergences: <NONE_OR_LIST>

Required:
1. Diff baseline -> target first and summarize changed modules/tests/interfaces/dependencies.
2. Follow playbooks/port-checklist-update-template.md end-to-end.
3. Port changed behavior tests-first; do not skip changed upstream tests. For each new
   FEATURE, port the behavior, port ALL its tests, and add the new Python tests to the
   test-mapping manifest so completeness checks stay green.
4. Run a mandatory differential parity sweep regardless of triage: both binaries over a
   diverse corpus, full (untruncated) diff, plus a class-level truth table for any
   discrepancy. The replacement library can diverge in either direction independently of
   the upstream diff.
5. For each real divergence, consult upstream main/unreleased to decide which side is
   canonical; write a discriminating test (red->green) before fixing.
6. Run full validation gates (tests, parity, lint/format/docs/CI checks).
7. Update version correspondence metadata and sync log.
8. Return a concise sync report with what changed, validation evidence, and any blockers.
```
