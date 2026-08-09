---
title: "Repository Refresh: Currency, Automation, and Supply-Chain Review"
status: complete
date: 2026-08-08
review_bead: rpp-fzwy
baseline_commit: afc344c528e519c02da8a3fbc46437b29b5f424d
---
# Repository Refresh: Currency, Automation, and Supply-Chain Review

## Summary and Verdict

**Verdict: approve with tracked follow-ups.**

The repository remains structurally sound.
This pass updated eligible maintenance and security pins, refreshed live ecosystem
guidance, reconciled active plans, and extended the supply-chain model beyond dependency
installation to code loading and workspace opening.
It also converted the 14-day dependency policy into an executable lockfile check without
changing frozen resolver inputs.

No evidence of compromise was found.
One exact-version cool-off exception was approved by the owner for the requested tbd
upgrade. uv 0.12 remains deferred, and four pre-existing design decisions remain tracked
rather than being silently folded into a broad maintenance patch.

## Scope and Method

The review started from `origin/main` at `afc344c528e519c02da8a3fbc46437b29b5f424d` and
covered:

- all 96 tracked files, including 60 Markdown files and 27,193 lines of Markdown;
- the document taxonomy, top-level navigation, three active specs, research currency,
  case-study evidence, and meta-improvement loop;
- six shell hooks/bootstrap scripts, seven Python files, their tests, the sole GitHub
  Actions workflow, Dependabot, CODEOWNERS, and repository security settings;
- the one executable dependency graph: a PEP 723 research script with exactly pinned,
  hash-locked PyYAML 6.0.3;
- tbd integration, the GitHub CLI bootstrap, GitHub Action pins, Python/uv CI versions,
  and version-sensitive Rust guidance;
- 190 non-placeholder external URLs plus every tracked relative Markdown link, heading
  anchor, fence, and forbidden invisible Unicode character;
- the
  [Supply Chain Hardening guidebook](https://github.com/jlevy/supply-chain-hardening) at
  immutable commit
  [`06c6e1e6`](https://github.com/jlevy/supply-chain-hardening/commit/06c6e1e6d6a00258728dd111a64dd197de2bd6f0).

Third-party repositories were cloned without checkout into the ignored `attic/`
directory and inspected as untrusted data.
The guidebook’s workspace auditor was read in full before its read-only checks were run.
No install, build, editor-trust, or repository-supplied autostart action was accepted
implicitly.

## Findings and Resolutions

### Supply-chain model stopped at install time

The prior policy covered dependency pins and install scripts but not Python `.pth`
load-time execution, repository-supplied hooks, editor tasks, development containers,
MCP configuration, or hidden agent instructions.

**Resolved:** expanded the threat model and operating rules; hardened the README
bootstrap; added named ownership for execution and instruction surfaces; and made
zero-width, soft-hyphen, and bidirectional-control text fail across all tracked text,
including automation configuration and Markdown code fences.
The complete evidence is in the
[supply-chain audit log](../../SUPPLY-CHAIN-AUDIT-LOG.md).

### The cool-off was policy, not a deterministic gate

A rolling `UV_EXCLUDE_NEWER` environment value was considered, but testing showed that
it changes resolver inputs and invalidates an otherwise frozen lock check.
That would make CI non-reproducible as time advances.

**Resolved:** added `scripts/check_dependency_cooloff.py`, which fails closed when any
locked registry artifact lacks a verifiable upload time and rejects a package until its
newest locked artifact is at least 14 days old.
CI retains `UV_NO_BUILD=1` and uv `--locked`/`lock --check`; maintainers apply uv’s
`exclude-newer = "14 days"` only during intentional resolution.

### Pull requests could populate a reusable dependency cache

The validation workload is small, so allowing an untrusted pull request to save a uv
cache offered little value for its extra state-sharing surface.

**Resolved:** set setup-uv’s `enable-cache: false` explicitly because v9 defaults to
`auto` on GitHub-hosted runners.
The workflow retains read-only permissions, disables checkout credential persistence,
prohibits `pull_request_target`, and regression-tests these invariants and all immutable
action pins.

### Eligible executable pins had drifted

Every adopted pin had a maintenance or security reason and was at least 14 days old on
the 2026-08-08 review date, except for the owner-requested tbd exception.

| Component | Previous | Reviewed result | Reason |
| --- | --- | --- | --- |
| tbd integration | 0.4.0 | 0.4.2 | Owner-requested exact-version exception; stock hooks re-hardened |
| GitHub CLI bootstrap | 2.92.0 | 2.96.0 | Includes the fix for `GHSA-8cg3-r6g9-fpg2`; release assets remain checksum-verified and extract in a private temporary directory |
| `actions/checkout` | 7.0.0 | 7.0.1 | Eligible maintenance release, pinned to full SHA |
| `actions/setup-python` | 6.3.0 | 7.0.0 | Eligible Node runtime refresh, pinned to full SHA |
| `astral-sh/setup-uv` | 8.2.0 | 9.0.0 | Eligible Node runtime refresh, pinned to full SHA |
| uv in CI | 0.11.25 | 0.11.32 | Eligible lock-check correctness and maintenance fixes |
| CI Python | 3.13 | 3.14 | Validate the locked script on the current stable interpreter generation |

Registry integrity, publisher/provenance metadata, immutable tags, release/source diffs,
and platform checksums were reviewed before adoption.
OSV returned no known advisories for `get-tbd@0.4.2` or `PyYAML==6.0.3` at review time.

### Live documentation versions had drifted

Current workflow templates and mapping guidance lagged reviewed release generations.
Dated survey observations and completed plans, however, are evidence and should not be
rewritten as if upstream projects used today’s versions.

**Resolved:** current guidance now uses checkout 7, setup-python 7, setup-uv 9,
action-gh-release 3, Rust 1.97.1, regex 1.13, cargo-dist 0.32, and maturin 1.14.1. The
relevant action/source diffs and release notes were reviewed.
Historical observations retain their original versions.

### Navigation and maintenance records had small gaps

The README did not expose all current research plans/reproducibility appendices or the
dated review surface, meta documentation named stale validation recipes, and
`.gitignore` repeated `attic/` three times.

**Resolved:** expanded navigation, corrected validation commands, deduplicated the
ignore rule, added this dated review, and recorded the changes in the playbook
improvement log. All active specs were reconciled to their tbd features and retain
truthful planned/blocked state.

## Workspace and Link Audit

The supply-chain workspace scan found no hidden Unicode, executable `.pth` files, or
host persistence. Its autostart scan reported eight high-severity entries: the tracked
Claude and Codex tbd hooks already in review scope.
One informational result was a user-local Claude permission file.
Manual inspection and targeted integration tests found no malicious behavior in those
surfaces.

The external-link audit checked 190 non-placeholder URLs.
No confirmed broken link was found.
Direct registry web pages that returned bot-protection errors were cross-checked against
their successful official APIs rather than being misclassified as dead links.

GitHub reports Dependabot security updates, secret scanning, and push protection as
enabled, with no open Dependabot alerts.
The current `main` workflow is green, but the branch still has no ruleset or classic
protection; that deliberate owner decision remains `rpp-m7uy` below.

## Deliberately Deferred or Carried Forward

| Work | Tracking | Disposition |
| --- | --- | --- |
| Re-evaluate uv 0.12 | `rpp-1gar` | Deferred until 2026-08-22; every reviewed 0.12 release was inside the cool-off |
| Make customized hooks doctor-compatible | `rpp-gdrk` | tbd 0.4.2 flags the intentionally anchored/reordered Codex hooks as stale; stock regeneration would regress tested behavior |
| Choose a `main` branch ruleset | `rpp-m7uy` | Owner workflow decision still required; GitHub reports no active protection |
| Immutable pins in educational snippets | `rpp-3ddo` | Keep readable major tags in examples pending a coordinated generation/update policy |
| Executable canonical snippets | `rpp-8woy` | Requires designating complete examples before adding compilation/parsing gates |
| Repository-wide Flowmark baseline | `rpp-iasa` | Keep the large mechanical rewrite separate from substantive maintenance changes |
| TypeScript, qmd, and knip porting plans | linked active beads | Reconciled, not implemented by this maintenance pass |

## Validation

Local validation completed on 2026-08-08:

| Check | Result |
| --- | --- |
| Python 3.14.6 unit and integration suite | 33 passed |
| Repository text and Markdown structure | 97 tracked text files and 62 Markdown files passed |
| PEP 723 uv lock and 14-day artifact gate | Passed; PyYAML 6.0.3 remains hash-locked and eligible |
| Pinned upstream tbd/qmd lockfile inventories | All six generated artifacts match byte-for-byte |
| Python, shell, workflow YAML, and JSON syntax | Passed |
| Immutable-action, cache, permissions, CODEOWNERS, and diff policy checks | Passed |

The pull request’s exact uv 0.11.32/Python 3.14 CI run is the durable execution record
for the committed patch.
