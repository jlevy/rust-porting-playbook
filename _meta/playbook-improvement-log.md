# Playbook Improvement Log

Chronological log of improvements to the Rust Porting Playbook and its meta-process.

## 2026-03-03

### Multi-channel distribution documentation (from flowmark-rs sync)

Synced the flowmark-rs submodule and reviewed all changes since the last update.
The primary new learning is the production-grade multi-channel publishing system
(crates.io, PyPI via maturin, Homebrew tap, GitHub Releases) with orchestrated
workflows, testable release scripts, and idempotent publishing.

**Changes made:**

- Added new section 6.5 "Multi-Channel Distribution" to
  `references/rust-cli-best-practices.md` covering:
  - PyPI distribution via maturin (`bindings = "bin"`) with full workflow template
  - Homebrew tap distribution with formula template
  - Orchestrated multi-channel release patterns (reusable workflows, script-driven
    logic, idempotent publishing, concurrency control)
- Added condensed multi-channel distribution guidance to
  `guidelines/rust-project-setup.md`.
- Expanded Phase 7.5 in `playbooks/python-to-rust-playbook.md` to recommend
  multi-channel distribution for Python-to-Rust ports (PyPI, Homebrew, crates.io).
- Added "Multi-Channel Distribution Learnings" section to
  `case-studies/flowmark/flowmark-port-analysis.md` documenting key innovations.
- Updated `README.md`:
  - Added `docs/project/research/` to structure map.
  - Added "Research Docs" section to reference tables.
  - Updated documentation layers from four to five (adding Research layer).

**Source of improvements:** flowmark-rs submodule review — specifically the publishing
system (release.yml orchestrator, publish.yml for crates.io, pypi.yml for PyPI,
scripts/ for testable release logic, docs/publishing.md runbook).

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
  linker overrides + apt-get packages (simpler, more transparent). Added: plan job
  with script-driven decision logic, concurrency control, SHA256SUMS checksum
  generation, `fail-fast: false`, `fail_on_unmatched_files: true`, static linking
  via `+crt-static`, reusable channel workflow invocation, crates.io OIDC auth via
  `rust-lang/crates-io-auth-action@v1`.
- Added "Release Automation Scripts" section documenting the pattern of extracting
  workflow logic into testable Python scripts (resolve_release_plan, package_archive,
  resolve_crate_metadata, validate_wheel_entrypoints, pypi_smoke_test) with code
  examples and directory layout.
- Updated `guidelines/rust-project-setup.md` CI workflow to match (13 jobs, env vars,
  coverage, semver-checks, workflow-scripts). Rewrote release workflow section to
  document RUSTFLAGS cross-compilation, OIDC auth, and script-driven automation.

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
