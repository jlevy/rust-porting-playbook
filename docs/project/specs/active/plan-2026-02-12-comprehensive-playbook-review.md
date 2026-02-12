# Feature: Comprehensive Playbook Review — Full Structural, Factual, and Engineering Pass

**Date:** 2026-02-12 (last updated 2026-02-12)

**Author:** Senior Engineering Review

**Status:** Draft

**Prior review:** `plan-2026-02-08-playbook-review-fixes.md` (22 beads, all closed — focused on
specific factual fixes). This new review is a broader, document-by-document pass covering
structural quality, factual accuracy, engineering depth, cross-document consistency, and
completeness.

## Overview

Perform a comprehensive review of every document in the Rust Porting Playbook. Each
document gets a full three-dimensional review:

1. **Structural review** — Is the document well-organized? Are sections logical? Is the
   flow clear for both AI agents and human engineers? Are headings, tables, and examples
   used effectively?

2. **Factual/accuracy review** — Are all technical claims correct? Are code examples
   compilable? Are crate versions current? Are API signatures accurate? Are behavioral
   descriptions of Python and Rust semantics correct?

3. **Engineering depth review** — Does the document cover the right topics at the right
   depth? Are there important patterns, pitfalls, or alternatives missing? Would a senior
   Rust engineer find the guidance sound and complete?

Additionally, several cross-cutting reviews cover the playbook as a whole:
- Overall document organization and navigation
- Cross-document consistency (terminology, numbers, recommendations)
- Completeness gaps (topics that should exist but don't)
- Audience calibration (is the level right for AI agents + engineers?)

## Goals

- Every document reviewed for structural quality, factual accuracy, and engineering depth
- All findings documented with specific file, section, and line references
- Cross-document inconsistencies identified and resolved
- Missing topics and patterns identified
- Actionable improvements proposed (not just observations)

## Non-Goals

- Rewriting documents from scratch (improve what exists)
- Adding entirely new documents (unless a critical gap is found)
- Changing the 3-layer architecture (reference / guidelines / case-studies)
- Changing the 8-phase porting methodology

## Background

The playbook contains 24 content files across 3 directories (~12,450 lines total):

- **`reference/`** (11 files, ~5,289 lines) — The core playbook, mapping reference,
  porting guide, CLI best practices, code review checklist, test coverage playbook,
  templates, and meta-improvement docs
- **`guidelines/`** (6 files, ~2,246 lines) — Compact rules optimized for AI agent
  context windows
- **`case-studies/flowmark/`** (7 files, ~5,000 lines) — Real-world porting example

A prior review (2026-02-08) identified 53+ specific fixes across 5 severity phases.
This new review is a systematic document-by-document pass to catch anything the prior
review missed and to evaluate each document holistically.

## Design

### Review Approach

Each document review produces:
- A list of **structural findings** (organization, flow, clarity)
- A list of **factual findings** (errors, outdated info, non-compiling code)
- A list of **engineering findings** (missing patterns, incomplete guidance, depth gaps)
- A **summary assessment** (overall quality grade and top 3 priorities for improvement)

### Review Dimensions

| Dimension | What to check |
| --- | --- |
| Structure | Headings hierarchy, logical flow, table formatting, section length balance |
| Facts | Code compilation, crate versions, API signatures, Python/Rust semantics |
| Engineering | Pattern completeness, pitfall coverage, alternative approaches, edge cases |
| Cross-refs | Links to other docs, consistency of recommendations across documents |
| Audience | Appropriate detail level for AI agents and engineers directing them |

## Implementation Plan

### Phase 1: Reference Documents Review (11 files)

Core playbook and reference material — the most critical documents.

- [ ] Review `reference/python-to-rust-playbook.md` (619 lines) — the primary document;
  8-phase process, effort estimates, dependency tables, phase gate criteria
- [ ] Review `reference/python-to-rust-mapping-reference.md` (788 lines) — type mappings,
  control flow, error handling, classes, testing, project setup, dependencies
- [ ] Review `reference/python-to-rust-porting-guide.md` (807 lines) — detailed methodology,
  automation scripts, version tracking, pitfalls, cross-validation
- [ ] Review `reference/rust-cli-best-practices.md` (832 lines) — CI/CD, linting, releases,
  tooling, GitHub Actions workflows
- [ ] Review `reference/rust-code-review-checklist.md` (285 lines) — review checklist
  categories, items, severity levels
- [ ] Review `reference/python-to-rust-test-coverage-playbook.md` (312 lines) — pre-port
  test strategy, coverage tooling, gap analysis
- [ ] Review `reference/port-checklist-initial-template.md` (546 lines) — 10-phase
  checklist template with completion gates
- [ ] Review `reference/port-checklist-update-template.md` (379 lines) — ongoing sync
  checklist for tracking Python upstream changes
- [ ] Review `reference/meta-improving-this-playbook.md` (236 lines) — meta-process for
  case study feedback integration
- [ ] Review `reference/case-study-observations-template.md` (252 lines) — observation
  recording template for ports
- [ ] Review `reference/case-study-improvement-triage-template.md` (148 lines) — triage
  template for converting observations to playbook changes

### Phase 2: Guidelines Review (6 files)

Compact rules for AI agent context — must be accurate, concise, and self-contained.

- [ ] Review `guidelines/python-to-rust-porting-rules.md` (360 lines) — core porting rules,
  type mappings, dependency table, pitfalls, acceptance criteria
- [ ] Review `guidelines/python-to-rust-cli-porting.md` (285 lines) — CLI-specific porting
  patterns, argument mapping, output handling
- [ ] Review `guidelines/rust-general-rules.md` (286 lines) — general Rust rules, edition
  2024, error handling, testing patterns
- [ ] Review `guidelines/rust-cli-app-patterns.md` (403 lines) — CLI architecture, error
  handling, configuration, logging, version strings
- [ ] Review `guidelines/rust-project-setup.md` (626 lines) — Cargo.toml, CI, linting,
  deny.toml, release workflows, GitHub Actions
- [ ] Review `guidelines/test-coverage-for-porting.md` (286 lines) — test strategy,
  coverage tools, fixture management

### Phase 3: Case Studies Review (7 files)

Real-world porting documentation — must be internally consistent and well-referenced.

- [ ] Review `case-studies/flowmark/flowmark-port-analysis.md` (326 lines) — automation
  analysis, what required judgment, metrics
- [ ] Review `case-studies/flowmark/flowmark-port-library-choices.md` (257 lines) — library
  evaluation methodology and decisions
- [ ] Review `case-studies/flowmark/flowmark-port-decision-log.md` (523 lines) — all
  decisions (D2-D8) with rationale
- [ ] Review `case-studies/flowmark/flowmark-port-migration-plan.md` (3339 lines) — full
  migration plan with module-by-module details
- [ ] Review `case-studies/flowmark/flowmark-port-cross-validation.md` (189 lines) —
  cross-validation methodology and results
- [ ] Review `case-studies/flowmark/flowmark-port-comrak-bug.md` (211 lines) — comrak
  library bug documentation
- [ ] Review `case-studies/flowmark/flowmark-port-wrapping-solution.md` (155 lines) —
  line wrapping workaround documentation

### Phase 4: Cross-Cutting Reviews

Whole-playbook quality and organization.

- [ ] Review `README.md` (167 lines) — top-level navigation, statistics, quick start,
  case study summary, contributing guide
- [ ] Cross-document consistency audit — verify terminology, numbers, crate recommendations,
  and methodology descriptions are consistent across all 24 files
- [ ] Overall structure and organization review — evaluate the 3-layer architecture,
  document boundaries, duplication vs. cross-referencing, navigation flow
- [ ] Completeness gap analysis — identify topics that should be covered but aren't
  (e.g., async porting, FFI, WASM, workspace patterns, CI/CD for dual-language repos)

## Testing Strategy

Each review is validated by:
1. **Code examples** — all modified code examples verified for compilation correctness
2. **Cross-references** — all internal links verified after changes
3. **Grep sweeps** — after fixing a pattern, grep all files to ensure no instances remain
4. **Consistency checks** — after reconciling numbers/terms, verify across all documents

## Rollout Plan

Reviews can be performed and committed independently per-phase:
- Phase 1 (reference docs) first — highest impact
- Phase 2 (guidelines) second — most read by AI agents
- Phase 3 (case studies) third — internal consistency focus
- Phase 4 (cross-cutting) last — depends on phases 1-3 findings

## Open Questions

- Should findings from the prior review (plan-2026-02-08) that weren't yet implemented
  be re-verified during this pass?
- Are there any new documents that should be added (e.g., async porting guide, FFI guide)?
- Should the case study migration plan (3,339 lines) be reviewed at full depth or
  summarized?

## References

- Prior review spec: `docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md`
- Meta-playbook spec: `docs/project/specs/active/plan-2026-02-09-meta-playbook-improvement.md`
- All playbook content: `reference/`, `guidelines/`, `case-studies/flowmark/`
