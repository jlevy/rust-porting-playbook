# Playbook Improvement Log

Chronological log of improvements to the Rust Porting Playbook and its meta-process.

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

- Added `playbooks/auto-sync-agent-prompt-template.md` as a canonical prompt for syncing an
  existing Rust port to a new upstream Python release.
- Updated `_meta/meta-improving-this-playbook.md` with explicit dual-mode entry points:
  initial port vs auto-sync update.
- Expanded the active gap-map plan to include auto-sync-specific clarity and process
  gaps.

### Structure rename for clarity

- Renamed `reference/` to `playbooks/` to make operational playbook docs easier to find.
- Renamed `meta/` to `_meta/` so meta-process docs sort to the top.
- Updated markdown links across the repo to the new `playbooks/` and `_meta/` paths.
- Fixed README structure map:
  removed duplicate `guidelines/` block and moved `auto-sync-agent-prompt-template.md`
  under `playbooks/`.

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
- Updated gap-map statuses to reflect completed items:
  G02, G06, G16, G17, G20, and G22.
