# Playbook Improvement Log

Chronological log of improvements to the Rust Porting Playbook and its meta-process.

## 2026-05-30

### Auto-sync observations + integrations from flowmark-rs v0.7.0 → v0.7.2

First sync run to follow the formal observation → triage → log loop end-to-end (the prior
v0.6.5→v0.7.0 sync produced a sync artifact but skipped categorized observations).
Observations recorded in
[`case-studies/flowmark/flowmark-sync-observations-v0.7.2.md`](../case-studies/flowmark/flowmark-sync-observations-v0.7.2.md)
(OBS-1…OBS-8). Source: flowmark-rs
[PR #65](https://github.com/jlevy/flowmark-rs/pull/65).

Changes integrated in this pass:

- **`guidelines/rust-project-setup.md` (OBS-3, All/High)** — added a line-endings rule:
  commit a `.gitattributes` enforcing `eol=lf` from project setup. Embedded text
  (`include_str!`) and golden files read from disk otherwise carry CRLF on a Windows
  checkout and fail newline-anchored assertions — silent and Linux/macOS-green (cost two
  CI cycles on flowmark-rs).
- **`guidelines/python-to-rust-cli-porting.md` (OBS-5)** — added a note that CLI test
  harnesses piping stdin must tolerate a broken-pipe write (a binary that rejects its args
  exits before reading stdin), to avoid flaky races.
- **`playbooks/python-to-rust-sync-release-workflow.md` (OBS-4)** — added a published-crate
  + semver-gate check: when a sync changes the public Rust API, check the crates.io
  baseline and `cargo-semver-checks` early and decide version-bump vs. a targeted lint
  allowance with the maintainer.
- **`playbooks/auto-sync-agent-prompt-template.md` (process, OBS-8)** — added a final step
  prompting the record-observations + improvement-log closure loop. The operational
  template previously ended at validation/deliverables and never pointed back to the meta
  process, so two consecutive syncs skipped the loop. Also noted re-running
  upstream-embedding doc generators (OBS-2) and porting new golden suites for new CLI
  surfaces (OBS-8).

Recorded for maintainer triage (not yet integrated): OBS-2 (generator drift detail),
OBS-6 (own-vs-sibling version-pin divergence as a tolerated variation), OBS-7 (smoke-count
bumps each sync; external corpus). OBS-1 is a `VALIDATE` (the differential-sweep guidance
worked as intended).

## 2026-05-19

### Bidirectional library-divergence + mandatory differential sweep (from flowmark-rs v0.6.5 stabilization)

A senior review of the flowmark-rs v0.6.5 sync ([PR #55](https://github.com/jlevy/flowmark-rs/pull/55))
concluded "no formatter behavior blocker", but a full-corpus differential sweep plus a
reference-link truth-table sweep then found **two genuine parity bugs** that the upstream
diff never touched: thematic-break spacing (comrak forced blank lines Python preserves)
and reference-link normalization (released v0.6.5's shortcut form; fixed upstream as
issue #45). Lessons folded back into the workflow:

- **`playbooks/auto-sync-agent-prompt-template.md`** —
  - Made empirical pre-port verification **bidirectional**: the replacement library can
    diverge in either direction. "comrak already does the upstream fix" is necessary but
    not sufficient; the port can also carry its own divergence the original never had.
  - Added a **mandatory differential parity sweep** step (corpus diff + class-level truth
    tables) that runs *even for "tests-only" / "metadata-only" syncs*, because a clean
    test suite and a small upstream diff do not prove parity.
  - Added guidance to consult upstream `main`/unreleased as the **oracle** for which side
    is canonical when Python and Rust differ (with Principle 1 approval to adopt
    not-yet-released fixes).
  - Strengthened the cross-binary churn routine from a single sample to a full corpus
    sweep, and the minimal copy/paste prompt to include the sweep + per-feature test
    mapping.

- **`playbooks/python-to-rust-sync-release-workflow.md`** — made Mode B step 4
  bidirectional, added the mandatory differential-sweep step and a per-feature
  port+test+mapping step to both Mode A and Mode B, and added the sweep to both modes'
  acceptance gates.

Source artifacts:
[stabilization artifact](https://github.com/jlevy/flowmark-rs/blob/main/docs/sync-artifacts/2026-05-19-stabilization-d17-d18.md).

## 2026-05-07

### Sync-workflow improvements from flowmark-rs v0.6.4 → v0.6.5 sync

Real-world Mode B sync surfaced several gaps in the current sync guidance.
Source case study: [flowmark-rs PR #55](https://github.com/jlevy/flowmark-rs/pull/55)
and the
[sync artifact](https://github.com/jlevy/flowmark-rs/blob/main/docs/sync-artifacts/2026-05-07-sync-v0.6.4-to-v0.6.5.md).

Changes (all `ADD` / `CLARIFY`):

- **`guidelines/porting-principles-and-antipatterns.md`** — added a Sub-rule under
  Principle 8 (Disparities tested before fixed) titled “Empirical pre-port
  verification”. When an upstream behavior fix lands with new tests, the agent must run
  the new tests against the *existing* Rust binary first.
  If they pass, port only the tests; the Rust port may use a different parser/library
  that already implements the upstream fix.
  This was the most impactful gap exposed by this sync — every behavior change in v0.6.5
  was already correct in Rust because comrak handles GFM flanking, so 100% of the diff
  was test/metadata, not code.

- **`playbooks/port-checklist-update-template.md`** —
  - Added a new “Preflight” section at the top with
    `git submodule update --init --recursive` as the very first step.
  - Added a step to install the upstream binary at the **target** version so
    cross-binary parity tests target the right baseline.
  - Added a step to run a clean clippy on the current Rust HEAD before sync work begins;
    CI uses a floating `dtolnay/rust-toolchain@stable` and a recent stable bump may add
    new pedantic lints that flag pre-existing code unrelated to the sync.
    Land those fixes first so they don’t get conflated.
  - Added a new **Phase 0: Empirical Pre-Port Verification** as a hard gate before Phase
    1 implementation.
  - Added a “Refresh Test Mapping” sub-checklist in Phase 2 covering the
    discover/init/check loop and the smoke-test count constants that drift on every
    sync.
  - Fixed broken link to `rust-cli-best-practices.md` (was pointing at non-existent
    `../references/`).

- **`playbooks/auto-sync-agent-prompt-template.md`** —
  - Added an “Auto-detecting the target” snippet so agents can compute
    baseline-vs-latest without being told the target tag.
  - Inserted “Empirical pre-port verification” as step 4 in the prompt so the agent
    records per-change Rust impact before writing code.
  - Added a “library-replaced” reminder to Hard Requirements.
  - Added a “Per-change Rust impact table format” with the exact table format the sync
    report should use.
  - Added a “Sync artifact naming convention”:
    `<rust-repo>/docs/sync-artifacts/YYYY-MM-DD-sync-v<BASELINE>-to-v<TARGET>.md`.
  - Added a “Cross-binary churn investigation” section: when users report diff churn
    between Python and Rust binaries on real-world docs, first verify both binaries are
    at the same parity surface; mismatched intermediate versions commonly produce
    false-positive churn.

- **`playbooks/python-to-rust-sync-release-workflow.md`** — Mode B step 1 now
  cross-references the auto-detect snippet, and a new step 4 mandates empirical
  verification before checklist execution.

- **`references/cross-language-test-mapping.md`** —
  - Added “Update smoke-test count constants” to the ongoing-sync workflow, calling out
    that count assertions are not parity issues and just need to be bumped alongside the
    YAML refresh.
  - Added “Mapping new test files (not just new tests inside existing files)” with
    concrete decisions: parallel Rust file, excluded with rationale, or partial.

### Underlying observations

- **OBS-1:** The v0.6.4 → v0.6.5 sync had zero Rust code changes — every upstream “fix”
  already worked correctly under comrak.
  Without the empirical pre-port gate, an agent would have ported the regex/find
  override unnecessarily.
- **OBS-2:** CI’s `Clippy lint` job failed on the initial sync push because Rust 1.95
  stable added two new pedantic lints (`map_unwrap_or`, `unnecessary_trailing_comma`)
  that flagged pre-existing code unrelated to the sync.
  Trivial mechanical fixes, but the failure was confusing because the local toolchain
  was 1.94.1.
- **OBS-3:** Smoke-test count constants in the case-study repo
  (`EXPECTED_PYTHON_TEST_COUNT`, etc.)
  needed updating, but the playbook didn’t mention this.
  Easy to miss.
- **OBS-4:** A user reported diff churn between Python and Rust binaries on three
  real-world docs. Investigation showed all three produced byte-identical output once
  both binaries were at v0.6.5. The churn was version-mismatch, not parity.
  The sync workflow should mention this troubleshooting routine.

## 2026-03-03

### Multi-channel distribution documentation (from flowmark-rs sync)

Synced the flowmark-rs submodule and reviewed all changes since the last update.
The primary new learning is the production-grade multi-channel publishing system
(crates.io, PyPI via maturin, Homebrew tap, GitHub Releases) with orchestrated
workflows, testable release scripts, and idempotent publishing.

**Changes made:**

- Added new section 6.5 “Multi-Channel Distribution” to
  `references/rust-cli-best-practices.md` covering:
  - PyPI distribution via maturin (`bindings = "bin"`) with full workflow template
  - Homebrew tap distribution with formula template
  - Orchestrated multi-channel release patterns (reusable workflows, script-driven
    logic, idempotent publishing, concurrency control)
- Added condensed multi-channel distribution guidance to
  `guidelines/rust-project-setup.md`.
- Expanded Phase 7.5 in `playbooks/python-to-rust-playbook.md` to recommend
  multi-channel distribution for Python-to-Rust ports (PyPI, Homebrew, crates.io).
- Added “Multi-Channel Distribution Learnings” section to
  `case-studies/flowmark/flowmark-port-analysis.md` documenting key innovations.
- Updated `README.md`:
  - Added `docs/project/research/` to structure map.
  - Added “Research Docs” section to reference tables.
  - Updated documentation layers from four to five (adding Research layer).

**Source of improvements:** flowmark-rs submodule review — specifically the publishing
system (release.yml orchestrator, publish.yml for crates.io, pypi.yml for PyPI, scripts/
for testable release logic, docs/publishing.md runbook).

### CI workflow and release automation hardening (from flowmark-rs sync)

Extracted comprehensive CI and release workflow patterns from the flowmark-rs production
setup into playbook guidance.

**Changes made:**

- Rewrote CI section (7.2) in `references/rust-cli-best-practices.md` with 13-job
  workflow from flowmark-rs: added `test-lib-only`, `coverage` (cargo-llvm-cov +
  Codecov), `semver-checks` (PR-only), `workflow-scripts` (unit tests for release
  scripts); added `CARGO_INCREMENTAL: 0` and `CARGO_PROFILE_TEST_DEBUG: 0` env vars;
  added `--locked` on clippy; added `RUSTFLAGS: "-D warnings"` to test jobs.
- Rewrote release workflow (6.4) to replace `cross` Docker approach with RUSTFLAGS
  linker overrides + apt-get packages (simpler, more transparent).
  Added: plan job with script-driven decision logic, concurrency control, SHA256SUMS
  checksum generation, `fail-fast: false`, `fail_on_unmatched_files: true`, static
  linking via `+crt-static`, reusable channel workflow invocation, crates.io OIDC auth
  via `rust-lang/crates-io-auth-action@v1`.
- Added “Release Automation Scripts” section documenting the pattern of extracting
  workflow logic into testable Python scripts (resolve_release_plan, package_archive,
  resolve_crate_metadata, validate_wheel_entrypoints, pypi_smoke_test) with code
  examples and directory layout.
- Updated `guidelines/rust-project-setup.md` CI workflow to match (13 jobs, env vars,
  coverage, semver-checks, workflow-scripts).
  Rewrote release workflow section to document RUSTFLAGS cross-compilation, OIDC auth,
  and script-driven automation.

## 2026-02-26

### Scope and claim calibration

- Tightened primary scope language to avoid over-claiming universality.
- Reframed top-level messaging around complex Python apps, especially CLI-oriented
  ports.
- Replaced brittle count-driven wording in top-level summaries with stable outcome
  framing.

### Checklist applicability and phase-consistency hardening

- Updated initial checklist to explicitly distinguish broad core workflow vs
  CLI-specific sections.
- Marked CLI parity as mandatory only for CLI applications and added non-CLI
  applicability guidance.
- Removed stale phase-count wording from top-level reference tables and replaced with
  stable phrasing.

### Case-study discoverability and evidence hygiene

- Added `case-studies/flowmark/README.md` as a local index/start-here entry point.
- Added reproducibility/evidence protocol to
  `case-studies/flowmark/flowmark-port-metrics.md` (commit+command+artifact
  expectations).

### Meta plan hygiene

- Archived `_meta/plans/active/plan-2026-02-12-comprehensive-playbook-review.md` to
  `_meta/plans/done/` as superseded.
- Updated historical references to the new archived plan location.

### Sync-release workflow codification

- Added `playbooks/python-to-rust-sync-release-workflow.md` to codify two release modes
  for existing ports:
  - Mode A: Rust-only stabilization release (same Python baseline)
  - Mode B: Upstream sync release (new Python baseline)
- Updated `playbooks/port-checklist-update-template.md` with explicit scope guard so it
  is used only for upstream baseline changes.
- Expanded `playbooks/auto-sync-agent-prompt-template.md` with a minimal copy-paste sync
  prompt and cross-links to the two-mode workflow.
- Added cross-links from `README.md` and `playbooks/python-to-rust-playbook.md` to keep
  the sync-release process discoverable from primary entry points.

## 2026-02-25

### Meta documentation reorganization

- Created top-level `_meta/` directory for all meta-process documentation.
- Moved meta-process docs from `playbooks/` to `_meta/`:
  - `meta-improving-this-playbook.md`
  - `case-study-observations-template.md`
  - `case-study-improvement-triage-template.md`
- Added this log to make meta improvements traceable over time.
- Added a new meta plan spec for consolidated gap mapping and follow-on updates.

### Plan structure refinement

- Moved playbook-improvement plans from `docs/project/specs/active/` to
  `_meta/plans/active/`.
- Moved completed playbook-improvement plans to `_meta/plans/done/`.
- Added `_meta/plans/README.md` describing active vs done plan placement.

### Auto-sync update clarity

- Added `playbooks/auto-sync-agent-prompt-template.md` as a canonical prompt for syncing
  an existing Rust port to a new upstream Python release.
- Updated `_meta/meta-improving-this-playbook.md` with explicit dual-mode entry points:
  initial port vs auto-sync update.
- Expanded the active gap-map plan to include auto-sync-specific clarity and process
  gaps.

### Structure rename for clarity

- Renamed `reference/` to `playbooks/` to make operational playbook docs easier to find.
- Renamed `meta/` to `_meta/` so meta-process docs sort to the top.
- Updated markdown links across the repo to the new `playbooks/` and `_meta/` paths.
- Fixed README structure map: removed duplicate `guidelines/` block and moved
  `auto-sync-agent-prompt-template.md` under `playbooks/`.

### Flowmark case-study planning and README signal

- Added active plan:
  `_meta/plans/active/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md`
  for full Flowmark case-study sync against current learnings.
- Added concise top-level README “Featured Example” section with direct links to:
  - `case-studies/flowmark/`
  - `case-studies/flowmark/flowmark-port-analysis.md`

### Link hygiene and checklist path normalization

- Normalized internal markdown links across `README.md`, `_meta/`, `playbooks/`,
  `guidelines/`, and `case-studies/flowmark/` after directory renames.
- Fixed stale checklist links to non-existent docs:
  - `port-checklist-initial.md` -> `port-checklist-initial-template.md`
  - `port-checklist-update.md` -> `port-checklist-update-template.md`
- Completed a core-doc link sweep and resolved broken relative paths.
- Updated gap-map statuses to reflect completed items: G02, G06, G16, G17, G20, and G22.

### Meta gap-closure pass (framework hardening)

- Closed remaining process gaps in the meta framework and templates:
  - per-phase observation gating in the initial checklist
  - standardized metrics command recipes
  - evidence fields in observations template
  - severity x impact priority matrix in triage template
  - mandatory closure loop (triage -> merge evidence -> log entry)
  - explicit diff-first hard gate in update checklist
  - sync-update observation context fields
- Added documentation taxonomy to `README.md`.
- Added owner/review cadence and link-validation guidance to `_meta/README.md`.

### Flowmark case-study sync completion

- Added canonical metrics source file: `case-studies/flowmark/flowmark-port-metrics.md`.
- Updated Flowmark case-study docs to reference canonical metrics and clearly separate:
  historical baseline (2025) vs current v2 metrics.
- Added/updated review timestamps and historical-artifact notes across Flowmark docs.
- Completed plan archival moves:
  - `_meta/plans/done/plan-2026-02-09-meta-playbook-improvement.md`
  - `_meta/plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md`
  - `_meta/plans/done/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md`
