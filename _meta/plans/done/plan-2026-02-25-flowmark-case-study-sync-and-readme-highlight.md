# Feature: Flowmark Case Study Sync and README Highlight

**Date:** 2026-02-25 (last updated 2026-02-25)

**Author:** Joshua Levy + Codex

**Status:** Done

## Overview

Fully review and synchronize the Flowmark case-study documents with current flowmark-rs
port learnings, metrics, and process outcomes, then add a brief high-signal summary in
the top-level README linking directly to the case study.

## Goals

- Audit all Flowmark case-study docs for stale metrics, stale process claims, and
  contradictions
- Align case-study documentation with current flowmark-rs results and parity learnings
- Preserve historical context where useful but clearly label it as historical
- Add a concise “featured example” summary in top-level README that links to the
  Flowmark case study

## Non-Goals

- Rewriting every case-study file from scratch
- Expanding the case study to cover unrelated future work
- Changing the core 8-phase methodology

## Background

Flowmark is currently the most complete and useful real-world example in this playbook.
Several playbook and case-study docs were authored across multiple port iterations; some
metrics and narrative points are now stale or inconsistent with the current port state.
This creates confusion for agents and humans using the case study as a reference model.

## Design

### Scope

Flowmark case-study files under:

- `case-studies/flowmark/`

And top-level summary updates in:

- `README.md`

### Synchronization Rules

- Prefer current canonical metrics where available
- If historical metrics are retained, label them explicitly as historical and include
  date/version context
- Keep numbers consistent across README, case-study analysis, decision log, and
  cross-validation docs
- Ensure case-study links in README point to the most useful entry doc(s)

## Implementation Plan

### Phase 1: Case Study Sync

- [x] Create a metric/source-of-truth table (metric, value, source file/line, date)
- [x] Audit all files in `case-studies/flowmark/` for stale or contradictory claims
- [x] Normalize key metrics across case-study docs (tests, LOC ratios, parity claims,
  workaround counts, coverage mapping)
- [x] Add explicit historical labels where old metrics are intentionally retained
- [x] Reconcile references to old port iterations versus current port
- [x] Add/refresh “last updated” markers where missing

### Phase 2: README Highlight

- [x] Add a brief “Featured Case Study: Flowmark” summary near top-level README entry
  flow
- [x] Keep summary short (2-4 bullets + one direct link)
- [x] Ensure summary emphasizes why it is the best current example of playbook usage
- [x] Link directly to `case-studies/flowmark/` and one recommended starting doc

### Phase 3: Consistency and Validation

- [x] Run consistency sweep for repeated metrics across README and case-study docs
- [x] Validate internal markdown links
- [x] Add a changelog entry in `_meta/playbook-improvement-log.md` for this sync

## Testing Strategy

- Manual consistency checks across the Flowmark doc set for key metrics/claims
- Link checks for all updated README + case-study references
- Spot-check that historical values are clearly marked and not presented as current

## Rollout Plan

1. Land metric consistency fixes in case-study docs.
2. Add concise top-level README highlight and links.
3. Record completion details in `_meta/playbook-improvement-log.md`.

## Open Questions

- Should a single case-study “source of truth” metrics file be introduced to reduce
  future drift?
- Which one Flowmark doc should be the canonical “start here” link from README?

## References

- `case-studies/flowmark/`
- `README.md`
- `_meta/plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md`
