---
title: "Rust Guideline Reuse Review"
status: complete
date: 2026-08-08
review_bead: rpp-djiw
baseline_commit: 911f7cd484777a31b32953c0efbbb86b10a96e06
pull_request: 22
---
# Rust Guideline Reuse Review

## Summary and Verdict

**Verdict: extract seven standalone Rust guidelines and keep a thin, explicit porting
layer.**

The prior documentation mixed three different jobs: teaching Rust practices, mapping
Python behavior to Rust, and executing a port.
Most of the material was useful outside porting, but its location and framing made that
reuse difficult.
This reorganization creates a source-language-independent Rust suite for
new and existing Rust projects, while retaining mappings, parity evidence, differential
testing, and upstream-sync workflows in porting documents.

The section audit found that 64 of 76 second-level sections were wholly or substantially
reusable as general Rust guidance.
Six were genuinely port-specific and six were navigation or document metadata.
Mixed sections were split rather than classified by filename.

## Precommit Engineering Review

**Verdict: approve after fixes.**

The tbd precommit review found five internal consistency issues.
All were corrected in this change set; no unresolved Blocker, High, Medium, or Low
finding remains.

| ID | Severity | Finding and evidence | Resolution |
| --- | --- | --- | --- |
| RGREV-001 | High | `guidelines/python-to-rust-porting-rules.md:26` called tests the entire specification and `:55` prohibited `Result` based only on Python syntax | Defined tests as one evidence source alongside surface enumeration and differential runs; made Rust failure typing follow the actual API and parity contract |
| RGREV-002 | Medium | `guidelines/rust-code-review-rules.md:20` used `Critical`, which did not match tbd’s review artifact severity vocabulary | Standardized the reusable checklist on Blocker, High, Medium, and Low |
| RGREV-003 | Medium | `docs/project/specs/active/plan-2026-03-04-typescript-to-rust-porting-path.md:373` would have reintroduced source-language setup into a general Rust guideline | Kept Rust setup source-independent and routed TypeScript checkout behavior to its porting workflow |
| RGREV-004 | Low | `guidelines/rust-testing-rules.md:185` assumed every consumer calls a tracking item a bead | Uses “tracking issue or bead,” preserving tbd guidance without coupling the general rule to one tracker |
| RGREV-005 | Low | `docs/project/research/research-tbd-dependency-port-plan.md:36` and its qmd counterpart retained an obsolete numbered-section reference after consolidation | Replaced the stale section pointer with direct links to the project-setup and release authorities |

### Design Assessment

The focused suite is preferable to either a single Rust monolith or one document per
source language.
It gives each rule one authority, lets agents load only relevant topics,
and allows Python and TypeScript mappings to evolve without branching the Rust rules.
The cost is more files and navigation, addressed by one index and explicit
related-guideline links.

Three alternatives were rejected:

- keeping the 7,000-word CLI reference as the hub would preserve duplication and make
  selective context loading difficult;
- deleting the old paths immediately would break historical links and external
  bookmarks;
- copying the candidates directly into tbd in the same PR would couple two repository
  lifecycles and make review provenance unclear.

Compatibility files are therefore intentionally small, and tbd upstreaming is tracked
separately.

### Documentation Consistency

The top-level README, contributor guidance, flow overview, active TypeScript plan,
playbooks, mapping references, research plans, and meta templates now point to the new
authorities. Historical plans and dated reviews retain their original filenames because
they describe the repository state at their recorded commits.

Confirmed benign during review:

- legacy filenames remain only in compatibility maps, historical artifacts, and the
  reorganization audit;
- Python appears in the general release guideline only as the audience for an optional
  PyPI binary-wheel channel;
- general Rust guidelines may link to porting documents under “Related Guidelines”
  without depending on their source-language assumptions.

Non-blocking follow-ups already tracked in tbd include upstreaming the Rust candidates
(`rpp-u657`), a repository-wide Flowmark baseline (`rpp-iasa`), executable validation
for canonical snippets (`rpp-8woy`), immutable pins in educational workflow examples
(`rpp-3ddo`), and hardened-hook compatibility with generated tbd state (`rpp-gdrk`).

## Scope and Method

The audit covered the seven documents where target-side Rust advice had accumulated:

| Source document | H2 sections | Whole-document words | General | Port-only | Navigation/meta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `guidelines/rust-general-rules.md` | 13 | 1,402 | 12 | 0 | 1 |
| `guidelines/rust-project-setup.md` | 9 | 3,130 | 8 | 0 | 1 |
| `guidelines/filesystem-heavy-cli-porting.md` | 6 | 1,103 | 6 | 0 | 0 |
| `guidelines/test-coverage-for-porting.md` | 11 | 1,985 | 5 | 5 | 1 |
| `references/rust-cli-app-patterns.md` | 14 | 1,914 | 12 | 1 | 1 |
| `references/rust-cli-best-practices.md` | 12 | 7,168 | 10 | 0 | 2 |
| `references/rust-code-review-checklist.md` | 11 | 2,844 | 11 | 0 | 0 |
| **Total** | **76** | **19,546** | **64** | **6** | **6** |

The review compared the content with tbd’s Python and TypeScript guideline families.
Those families work well because they use a baseline language document, focused topic
documents, stable frontmatter, actionable rules, and related-guideline links instead of
repeating shared material.
The Rust suite adopts the same structure without copying language-specific rules.

Date-sensitive Rust claims were checked against the official
[Rust 1.97.1 announcement](https://blog.rust-lang.org/2026/07/16/Rust-1.97.1/),
[Edition 2024 resolver guidance](https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html),
and the crates.io team’s
[trusted-publishing announcement](https://blog.rust-lang.org/2025/07/11/crates-io-development-update-2025-07/).

## Classification Rule

Each section was classified by the question it answers:

- **General Rust:** How should this Rust code, project, CLI, test suite, release, or
  review be designed?
- **Porting:** How does an existing source contract map to Rust, and how is parity
  demonstrated or maintained?
- **Research or case-study evidence:** What happened in a particular project or at a
  particular point in time?
- **Navigation/meta:** Where should a reader go next, or how is the document organized?

This rule keeps the same Rust guidance usable for code written from scratch.
It also prevents general documents from accumulating Python and TypeScript branches as
new porting paths are added.

## Resulting General Rust Suite

| Guideline | Authoritative scope | Main source disposition | tbd candidacy |
| --- | --- | --- | --- |
| [`rust-rules.md`](../../guidelines/rust-rules.md) | Language idioms, ownership, types, errors, modules, unsafe, async, and performance | Renamed and refocused the old general rules; moved project tooling and tests to focused documents | First wave |
| [`rust-project-setup.md`](../../guidelines/rust-project-setup.md) | Cargo shape, metadata, features, toolchains, formatting, Clippy, CI, dependency policy, and docs | Consolidated project setup and the project/CI portions of the oversized CLI reference | First wave |
| [`rust-cli-rules.md`](../../guidelines/rust-cli-rules.md) | Process boundaries, arguments, streams, terminal behavior, exits, configuration, interruption, and CLI tests | Promoted source-independent CLI patterns from `references/` | First wave |
| [`rust-filesystem-rules.md`](../../guidelines/rust-filesystem-rules.md) | Paths, traversal, mutation planning, replacement, durability, metadata, links, recovery, and failure tests | Extracted target-side rules from filesystem porting guidance | Specialized wave |
| [`rust-testing-rules.md`](../../guidelines/rust-testing-rules.md) | Unit, integration, property, snapshot, CLI, async, feature, toolchain, platform, and coverage tests | Extracted Rust testing from port coverage guidance and duplicated references | First wave |
| [`rust-release-rules.md`](../../guidelines/rust-release-rules.md) | Release identity, gates, artifacts, permissions, channels, publishing, smoke tests, and incidents | Split release policy from project setup and the CLI reference | Specialized wave |
| [`rust-code-review-rules.md`](../../guidelines/rust-code-review-rules.md) | Severity-ranked correctness, soundness, APIs, concurrency, dependencies, tests, and reviewer flow | Promoted and normalized the general review checklist | Specialized wave |

[`guidelines/README.md`](../../guidelines/README.md) is now the navigation root.
Each general guideline has tbd-style frontmatter, a standalone scope statement,
actionable rules, related-guideline links, and the repository’s documentation footer.

## Source Disposition

| Previous source | Disposition |
| --- | --- |
| `rust-general-rules.md` | Compatibility redirect to `rust-rules.md`; formatting, setup, and test material moved to focused guidelines |
| `rust-project-setup.md` | Retained as an authority, shortened, and separated from release mechanics |
| `filesystem-heavy-cli-porting.md` | Retains filesystem contract inventory, source/target parity, fixture matrices, and differential validation; implementation rules moved to `rust-filesystem-rules.md` |
| `test-coverage-for-porting.md` | Retains source-suite evidence, syntactic-surface enumeration, test mapping, fixture provenance, and differential validation; Rust test design moved to `rust-testing-rules.md` |
| `rust-cli-app-patterns.md` | Compatibility redirect to `rust-cli-rules.md`; version-correspondence behavior remains in `python-to-rust-cli-porting.md` |
| `rust-cli-best-practices.md` | Reduced to a compatibility map routing project, CLI, test, release, review, porting, and research topics to their authorities |
| `rust-code-review-checklist.md` | Compatibility redirect to `rust-code-review-rules.md` |

The compatibility files preserve established paths and the historical anchors still used
by completed plans and reviews.
Live navigation links directly to the new authorities.

## Porting Layer Retained

The following concerns remain separate because they exist only when another
implementation is authoritative:

- source construct and dependency mappings;
- flag, help, stream, exit-code, error, and version correspondence;
- source-suite inventory and syntactic-surface enumeration;
- cross-language test traceability and fixture provenance;
- byte-for-byte or semantic differential validation;
- classification and documentation of intentional differences;
- source-version tracking and ongoing upstream synchronization.

The authoritative porting documents are indexed separately in
[`guidelines/README.md`](../../guidelines/README.md).
The construct lookup remains in
[`python-to-rust-mapping-reference.md`](../../references/python-to-rust-mapping-reference.md),
and the execution sequence remains in the playbooks.

## Consolidation and Quality Improvements

The seven audited sources contained 19,546 words.
Their reorganized general suite, port-specific filesystem and test documents, navigation
index, and four compatibility files contain 12,759 words: 6,787 fewer words, or about
35% less material in this overlapping cluster.
The reduction comes from removing repeated Cargo, CI, release, testing, and CLI
explanations rather than dropping the porting contract.

The rewrite also corrects several unsafe or over-broad patterns:

- standalone test guidance uses coverage as evidence, not a universal percentage gate;
- porting guidance treats tests as executable evidence alongside surface enumeration and
  differential validation, not correctness by definition;
- release channels are selected by audience instead of treating PyPI or any other
  channel as universally primary;
- compact guidelines describe workflow invariants instead of embedding large templates
  with mutable action tags;
- filesystem traversal propagates material errors rather than silently dropping
  `walkdir` failures;
- atomic visibility is distinguished from crash durability;
- temporary and cross-validation roots must be private and safely allocated rather than
  predictable shared `/tmp` paths;
- release authority, dependency cool-off, source review, and artifact provenance are
  explicit supply-chain requirements.

## tbd Upstream Recommendation

Do not copy the porting layer into tbd’s general guidelines.
Propose the reusable suite in two reviewable waves:

1. `rust-rules`, `rust-project-setup`, `rust-cli-rules`, and `rust-testing-rules`;
2. `rust-filesystem-rules`, `rust-release-rules`, and `rust-code-review-rules`.

The first wave establishes the common language, project, application, and test floor.
The second adds specialized operational and review guidance.
A Rust-specific review shortcut can then load `rust-code-review-rules` plus only the
topic guidelines relevant to the diff.

The upstream proposal is tracked as `rpp-u657` so this repository reorganization can be
reviewed independently from changes to tbd itself.

## Validation

All required checks passed:

- 36 unit and integration tests, including three new guideline-structure regressions;
- tracked-text and Markdown structure checks across all 69 Markdown files, including
  links, anchors, fences, and forbidden invisible Unicode;
- frozen PEP 723 uv lock validation with builds disabled;
- the independent 14-day dependency cool-off gate;
- byte-for-byte lockfile inventories regenerated from pinned tbd and qmd upstream
  commits;
- shell syntax for all six Claude and Codex integration scripts;
- Flowmark’s full auto-format check for every new or substantially rewritten document;
- `git diff --check`;
- tbd repository, issue, dependency, worktree, and local sync consistency checks.

At validation time, `tbd doctor` reported two expected delivery-state warnings: the
hardened Codex hook file differs from tbd’s generated stock file (`rpp-gdrk` tracks
compatibility), and the remote `tbd-sync` branch did not yet exist.
The final `tbd sync` created the remote issue state successfully.
The remaining generated-hook warning does not affect the documentation or test result.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
