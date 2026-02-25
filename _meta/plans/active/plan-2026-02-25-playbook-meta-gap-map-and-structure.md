# Feature: Playbook Meta Gap Map and Documentation Structure

**Date:** 2026-02-25 (last updated 2026-02-25)

**Author:** Joshua Levy + Codex

**Status:** Draft

## Overview

Create a single canonical meta workstream for improving the Rust Porting Playbook:

1. Consolidate meta-process documentation into top-level `_meta/`
2. Establish clean entry points for contributors
3. Maintain a structured, prioritized gap map for documentation and playbook quality
4. Track implemented improvements in a durable changelog

## Goals

- Make meta-process documentation easy to find and navigate
- Create one consolidated gap map with priority and ownership-ready tasks
- Capture both meta-framework gaps and playbook content gaps
- Reduce confusion caused by stale links, duplicate entry points, and inconsistent guidance
- Define a clear dual-mode entry model:
  initial port vs auto-sync update
- Provide a canonical, reusable agent prompt for auto-sync updates

## Non-Goals

- Implement every gap listed in this plan in one pass
- Change the core 8-phase porting methodology
- Redesign the entire repository structure outside the `_meta/` scope

## Background

Recent review identified that the meta framework is strong but unevenly integrated:

- Meta docs existed but were mixed into `playbooks/`
- Some entry-point links and checklist references were stale or inconsistent
- Initial-port and sync-update workflows were not explicitly separated at meta entry points
- The meta implementation spec remained draft/unclosed
- Per-phase observation capture was not wired into each checklist phase as required
- Playbook-wide gaps (generalization, reproducibility, status hygiene) lacked a single backlog

This plan creates a single source of truth for those gaps and their remediation path.

## Design

### Approach

Use `_meta/` as the canonical location for playbook-improvement process docs and planning.
Keep the gap map in this spec and maintain implementation history in
`_meta/playbook-improvement-log.md`.

### Components

- `_meta/README.md` — index and entry points
- `_meta/meta-improving-this-playbook.md` — meta framework
- `_meta/case-study-observations-template.md` — phase observations template
- `_meta/case-study-improvement-triage-template.md` — triage template
- `playbooks/auto-sync-agent-prompt-template.md` — canonical prompt for update/sync runs
- `_meta/playbook-improvement-log.md` — chronological improvements log
- `_meta/plans/active/plan-2026-02-25-playbook-meta-gap-map-and-structure.md` — this plan and gap map

### Gap Map Schema

Each gap entry includes:

- Category
- Gap
- Priority (`P0`..`P3`)
- Impact (`All`, `Most`, `Some`, `Niche`)
- Evidence
- Target doc(s)
- Proposed fix
- Status

## Structured Gap Map

| ID | Category | Gap | Priority | Impact | Evidence | Target doc(s) | Proposed fix | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G01 | Meta integration | Per-phase observation recording is not embedded in each checklist phase | P1 | Most | `playbooks/port-checklist-initial-template.md` has only optional tail section | `playbooks/port-checklist-initial-template.md` | Add an explicit "Record OBS-N" item at end of each phase gate | Open |
| G02 | Entry points | Broken checklist links (`port-checklist-initial.md`, `port-checklist-update.md`) | P1 | All | `playbooks/python-to-rust-porting-guide.md` references non-existent files | `playbooks/python-to-rust-porting-guide.md`, `playbooks/port-checklist-initial-template.md` | Update links to `*-template.md` or add generated non-template docs | Done |
| G03 | Threshold consistency | Candidate test-coverage minimum in meta doc (60%) conflicts with core playbook readiness gate (80% core) | P2 | Most | `_meta/meta-improving-this-playbook.md` vs `playbooks/python-to-rust-playbook.md` | `_meta/meta-improving-this-playbook.md` | Align thresholds or define explicit "quick mode" with reduced bar | Open |
| G04 | Data freshness | Flowmark baseline in meta doc is stale (~2,000 lines) | P3 | Some | Current README shows ~4,400 Python lines | `_meta/meta-improving-this-playbook.md` | Update baseline numbers and date-stamp metrics | Open |
| G05 | Governance | Meta implementation spec remains draft with unchecked tasks | P2 | Some | `_meta/plans/active/plan-2026-02-09-meta-playbook-improvement.md` | Old spec + this plan | Mark historical completion/deprecations and cross-link to this active plan | Open |
| G06 | Navigation | Meta docs were split between `playbooks/` and other areas | P1 | Most | Prior structure increased findability cost | `README.md`, `_meta/README.md` | Keep all meta docs in `_meta/`; ensure top-level README points there | Done |
| G07 | Reproducibility | Metrics collection lacks standardized command recipes | P2 | Most | LOC/test/time guidance is conceptual, not scripted | `_meta/meta-improving-this-playbook.md`, templates | Add command snippets for LOC/test counts and timing capture | Open |
| G08 | Evidence quality | Observation template lacks explicit command/output artifact fields | P2 | Most | Current template focuses on narrative assessment | `_meta/case-study-observations-template.md` | Add fields for repro command, artifact path, and commit hash | Open |
| G09 | Prioritization rigor | Triage template lacks explicit decision rule for severity x impact outcomes | P2 | Some | Priority summary is present but rubric is implicit | `_meta/case-study-improvement-triage-template.md` | Add clear priority matrix (e.g., P0/P1 mapping) | Open |
| G10 | Applicability breadth | Meta framework still leans CLI-first in examples and implied assumptions | P2 | Most | Candidate ordering and examples skew CLI | `_meta/meta-improving-this-playbook.md` | Add explicit guidance for services, libraries, async apps, data pipelines | Open |
| G11 | Status loop | No mandatory closure loop from approved triage item to merged diff + log entry | P1 | Most | Integration section describes implementation but not closure checklist | `_meta/meta-improving-this-playbook.md`, log | Add closure checklist and required log update for each merged change | Open |
| G12 | Link hygiene | Link integrity checks are suggested but not standardized | P2 | Some | Validation is generic text only | `_meta/meta-improving-this-playbook.md`, CI docs | Add concrete link-check command/workflow | Open |
| G13 | Terminology consistency | "playbook", "guide", "checklist", "template" boundaries are still blurred | P3 | Some | Multiple docs overlap process narratives | `README.md`, core reference docs | Add short "doc taxonomy" section in README | Open |
| G14 | Maintenance model | Meta docs lack explicit owner/review cadence | P3 | Niche | No cadence field in docs | `_meta/README.md`, meta plan | Add lightweight review cadence and owner notes | Open |
| G15 | Improvement visibility | No consolidated feed of what changed in playbook quality work | P1 | Most | No dedicated changelog before this effort | `_meta/playbook-improvement-log.md` | Maintain dated entries for each merged _meta/playbook improvement | In progress |
| G16 | Workflow clarity | No explicit "start here" split between initial port and auto-sync update | P1 | All | Users can enter wrong checklist for sync tasks | `_meta/meta-improving-this-playbook.md`, `_meta/README.md`, `README.md` | Add explicit two-mode entry section and references | Done |
| G17 | Agent operability | No canonical prompt for update/sync runs over existing ports | P1 | Most | Sync runs vary in quality without a stable prompt | `playbooks/auto-sync-agent-prompt-template.md` | Add and maintain clean prompt template with required inputs and gates | Done |
| G18 | Diff discipline | Auto-sync process not consistently forcing baseline→target diff triage before coding | P1 | Most | Sync attempts can miss changed tests/interfaces | `_meta/meta-improving-this-playbook.md`, `playbooks/port-checklist-update-template.md` | Codify diff-first step and change categorization gates | Open |
| G19 | Update-mode evidence | Meta templates emphasize full-port case studies more than sync cycles | P2 | Some | Less guidance for recording sync-cycle observations | `_meta/case-study-observations-template.md` | Add guidance for update-cycle observations and artifacts | Open |
| G20 | Plan organization | Playbook-improvement plans were mixed in a generic specs location | P2 | Some | Plan discoverability was low | `_meta/plans/active/`, `_meta/plans/done/` | Keep active/done segregation for playbook-improvement plans | Done |
| G21 | Case-study currency | Flowmark case-study docs are not consistently synced with current flowmark-rs learnings/metrics | P1 | All | Flowmark is the primary real-world example but metrics/history can drift | `case-studies/flowmark/`, `README.md` | Run full case-study sync pass and normalize current-vs-historical claims | Open |
| G22 | README signal | Top-level README lacks a concise “featured case study” callout with direct start link | P2 | Most | Users may miss the strongest concrete example | `README.md` | Add short highlighted summary + direct link to Flowmark case study | Done |

## Implementation Plan

### Phase 1: Meta Structure and Canonical Entry Points

- [x] Create top-level `_meta/` directory
- [x] Move meta framework and case-study templates from `playbooks/` to `_meta/`
- [x] Add `_meta/README.md` as index
- [x] Add `_meta/playbook-improvement-log.md`
- [x] Create this plan spec using `tbd template plan-spec`
- [x] Update primary README and key cross-links to new `_meta/` paths
- [x] Move playbook-improvement plans into `_meta/plans/active/`
- [x] Move completed playbook-improvement plans into `_meta/plans/done/`
- [x] Add canonical auto-sync prompt template
- [x] Sweep remaining references for stale paths and broken links

### Phase 2: Gap Closure Backlog (Meta-First)

- [ ] Implement G01: per-phase observation capture in checklist phases
- [x] Implement G02: resolve checklist link targets in reference docs
- [ ] Implement G03/G04: align thresholds and refresh baseline metrics
- [ ] Implement G08/G09: strengthen templates with evidence and prioritization rubric
- [ ] Implement G11/G12: add closure loop + concrete validation checks
- [ ] Implement G18: enforce diff-first triage in update workflow docs
- [ ] Implement G19: add sync-cycle observation guidance
- [ ] Create and execute dedicated Flowmark case-study sync plan:
  `_meta/plans/active/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md`
- [ ] Record each merged change in `_meta/playbook-improvement-log.md`

### Phase 3: Broader Playbook Documentation Gaps

- [ ] Expand non-CLI guidance surface (services, async, libraries, data pipelines)
- [ ] Clarify "initial port playbook" vs "auto-sync update playbook" in top-level entry docs
- [ ] Add reproducibility command recipes for metrics collection
- [ ] Add doc taxonomy and ownership/review cadence
- [ ] Re-run comprehensive consistency pass across playbooks/guidelines/meta

## Testing Strategy

- Run link search sweeps for old paths:
  - no references to moved `playbooks/meta-*.md` locations except historical notes
- Verify `README.md` entry points resolve and reflect `_meta/` organization
- Validate new plan and log docs are discoverable from top-level README and `_meta/README.md`
- For each gap closure PR, include before/after evidence and update the improvement log

## Rollout Plan

1. Land meta directory reorganization and canonical links.
2. Treat this plan as the backlog source for _meta/playbook doc work.
3. Execute high-priority (`P0`/`P1`) gaps first, then medium-priority generalization work.
4. Keep history in `_meta/playbook-improvement-log.md` for every merged change.

## Open Questions

- Should `_meta/plans/active/plan-2026-02-09-meta-playbook-improvement.md` be
  marked implemented and archived once this plan is active?
- Resolved: standardized checklist links on `*-template.md` (no generated non-template
  docs required at this time).
- Do we want a lightweight CI check for internal markdown link validity in this repo?

## References

- `_meta/meta-improving-this-playbook.md`
- `playbooks/auto-sync-agent-prompt-template.md`
- `_meta/case-study-observations-template.md`
- `_meta/case-study-improvement-triage-template.md`
- `_meta/playbook-improvement-log.md`
- `_meta/plans/active/plan-2026-02-09-meta-playbook-improvement.md`
- `_meta/plans/active/plan-2026-02-12-comprehensive-playbook-review.md`
- `_meta/plans/active/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md`
- `_meta/plans/done/plan-2026-02-08-playbook-review-fixes.md`
- `playbooks/port-checklist-update-template.md`
