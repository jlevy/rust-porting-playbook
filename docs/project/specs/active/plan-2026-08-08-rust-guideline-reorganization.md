# Feature: Reusable Rust Guideline Reorganization

**Date:** 2026-08-08 (last updated 2026-08-08)

**Author:** Joshua Levy + Codex

**Status:** Implemented and delivered

**Delivery:** [Draft PR #22](https://github.com/jlevy/rust-porting-playbook/pull/22)

## Overview

Reorganize the repository’s Rust guidance into a reusable, source-language-independent
guideline suite while preserving Python-to-Rust mappings, parity rules, and porting
workflows as a separate documentation layer.

The resulting Rust documents should be useful when creating a Rust project from scratch,
reviewing an existing Rust codebase, or loading candidate guidelines into tbd.
Porting documents should describe only the translation, parity, traceability, and
synchronization concerns that arise because another implementation exists.

## Goals

- Establish one navigable suite of standalone Rust best-practice documents.
- Extract reusable Rust guidance from porting documents and oversized references.
- Give each rule one authoritative home and replace duplicate explanations with links.
- Keep source-language mappings and porting workflows independently usable.
- Shape the general Rust documents so they can later be proposed as official tbd
  guidelines.
- Resolve contradictory or unsafe examples exposed while assigning authoritative homes,
  without weakening the parity contract.
- Record every implementation step and follow-up as tbd beads.

## Non-Goals

- Relax the parity or test-completion criteria of the Python-to-Rust porting method.
- Add TypeScript-to-Rust deliverables planned by the existing active specifications.
- Modify the separately maintained tbd package in this repository.
- Preserve large duplicated examples solely to keep existing document lengths stable.
- Add or upgrade executable dependencies.

## Background

The review covered seven documents with 76 second-level sections and about 18,700 words
of section content:

- `guidelines/rust-general-rules.md`
- `guidelines/rust-project-setup.md`
- `guidelines/filesystem-heavy-cli-porting.md`
- `guidelines/test-coverage-for-porting.md`
- `references/rust-cli-app-patterns.md`
- `references/rust-cli-best-practices.md`
- `references/rust-code-review-checklist.md`

The strongest duplication is between project setup and the CLI best-practices reference:
Cargo structure, CI, security, releases, development tooling, and documentation are
described twice. CLI architecture is already source-independent but lives under
`references/`. Filesystem safety and much of Rust testing are reusable but are framed as
porting guidance. The code-review checklist is general Rust guidance but is also under
`references/`.

The tbd Python and TypeScript guideline groups provide a useful structure:

- one baseline language-rules document;
- focused CLI, tooling, testing, or formatting documents;
- concise related-guideline links rather than repeating shared rules;
- YAML frontmatter with a stable name and one-line description;
- actionable rules and examples that do not depend on a specific repository.

## Design

### Documentation Boundary

Classify material by the question it answers:

| Question | Layer | Examples |
| --- | --- | --- |
| How should Rust code or a Rust project be built? | General Rust guideline | Ownership, errors, Cargo, CLI output, filesystem safety, tests, releases |
| How does a source construct map to Rust? | Porting guideline or mapping reference | `argparse` to clap, Python `dict` ordering, exception parity |
| How should a port be executed and kept synchronized? | Porting playbook | Sequencing, cross-validation, version correspondence, upstream sync |
| What evidence came from a particular project or date? | Research or case study | Flowmark measurements, distribution surveys, library evaluations |

General Rust documents may mention porting documents in related-guideline links, but
their rules and examples must stand alone without a Python or TypeScript source tree.

### Target Rust Guideline Suite

The audit supports seven general Rust guideline documents.
Five become newly standalone topics; two existing topics are retained and refocused.

| Guideline | Disposition | Scope |
| --- | --- | --- |
| `rust-rules.md` | Rename and refocus `rust-general-rules.md` | Language idioms, ownership, types, errors, organization, unsafe, async, performance |
| `rust-project-setup.md` | Retain and consolidate | Cargo/package layout, MSRV, CI gates, security, development workflow, documentation |
| `rust-cli-rules.md` | Move and refocus `rust-cli-app-patterns.md` | CLI architecture, clap, streams, exit behavior, configuration, terminal behavior |
| `rust-filesystem-rules.md` | Extract from filesystem porting guidance | Atomic writes, backups, collision policy, traversal, paths, mutation testing |
| `rust-testing-rules.md` | Extract from test-porting guidance and duplicated references | Rust test placement, fixtures, snapshots, property tests, coverage, CI behavior |
| `rust-release-rules.md` | Extract from project setup and the oversized CLI reference | Release design, artifacts, channels, trusted publishing, checksums, idempotency |
| `rust-code-review-rules.md` | Move and normalize the review checklist | Ownership, soundness, APIs, async, dependencies, performance, reviewer flow |

Add `guidelines/README.md` as the navigation root for the general Rust and porting
groups. Each general document must have tbd-compatible frontmatter, a concise scope
statement, actionable rules, examples where useful, related-guideline links, and the
repository’s documentation footer.

### Porting Layer to Preserve

Keep these documents explicitly source- or process-oriented:

- `porting-principles-and-antipatterns.md`
- `python-to-rust-porting-rules.md`
- `python-to-rust-cli-porting.md`
- `filesystem-heavy-cli-porting.md`
- `test-coverage-for-porting.md`
- `python-to-rust-mapping-reference.md`
- `cross-language-test-mapping.md`
- the phased playbooks and checklist templates under `playbooks/`

`filesystem-heavy-cli-porting.md` should retain cross-implementation validation and
filesystem parity concerns, while linking to `rust-filesystem-rules.md` for target-side
implementation. `test-coverage-for-porting.md` should retain source-suite preparation,
test mapping, syntactic-surface enumeration, and differential validation, while linking
to `rust-testing-rules.md` for target-side testing practices.

### Duplicate Reference Consolidation

Replace `references/rust-cli-best-practices.md` with a concise best-practices map that
routes readers to the seven guideline documents and the detailed distribution research.
Remove duplicated CI, Cargo, release, testing, and CLI explanations from that reference.
Move the content of `references/rust-cli-app-patterns.md` and
`references/rust-code-review-checklist.md` into their guideline homes, then update all
internal links.

### tbd Upstream Readiness

This repository will stage candidate guideline content in its existing `guidelines/`
architecture. A separate follow-up bead will propose the reusable suite to the tbd
repository, where official guidelines live and can be tested with `tbd guidelines`. This
avoids maintaining a second project-local copy under `.tbd/docs/guidelines/`.

## Implementation Plan

### Phase 1: Reorganize and Validate

- [x] Create the seven-document Rust guideline suite and `guidelines/README.md`.
- [x] Separate port-only material from general CLI, filesystem, and testing guidance.
- [x] Consolidate release and project-setup duplication from the CLI reference.
- [x] Update repository navigation and every internal cross-reference.
- [x] Produce a review document with a section-level disposition map and reusable-topic
  count.
- [x] Run the complete repository validation matrix and review the final diff.
- [x] Publish the work as a separate pull request and verify CI.

## Testing Strategy

- Run `scripts/check_docs.py` to verify links, anchors, fences, and tracked text.
- Run the complete unit suite because documentation tests cover repository navigation
  and validation behavior.
- Search for obsolete filenames and stale links after moves.
- Verify each general Rust guideline has required frontmatter, a scope statement,
  related-guideline links, and the common documentation footer.
- Confirm porting documents still expose every mapping, parity, traceability, and
  synchronization concern removed from general docs.
- Run all remaining checks required by `CONTRIBUTING.md` before publishing.

## Rollout Plan

Published this work as
[stacked draft PR #22](https://github.com/jlevy/rust-porting-playbook/pull/22), based on
the completed repository-refresh branch.
After the base pull request merges, retarget or rebase the guideline pull request onto
`main` without mixing the two review scopes.

## Decisions

- Propose `rust-rules`, `rust-project-setup`, `rust-cli-rules`, and `rust-testing-rules`
  to tbd first, followed by the specialized filesystem, release, and review documents.
- Evaluate a `review-code-rust` shortcut with the upstreaming work tracked by
  `rpp-u657`, rather than coupling it to this repository reorganization.

## References

- `CONTRIBUTING.md`
- `README.md`
- `tbd guidelines python-rules python-modern-guidelines python-cli-patterns`
- `tbd guidelines typescript-rules typescript-lint-format-rules typescript-cli-tool-rules`
- `tbd shortcut new-guideline`
- `docs/project/specs/active/plan-2026-03-04-typescript-to-rust-porting-path.md`
- `docs/reviews/rust-guideline-reuse-review-2026-08-08.md`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
