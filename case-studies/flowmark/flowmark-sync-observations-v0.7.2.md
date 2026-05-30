# Flowmark Sync Observations — v0.7.0 → v0.7.2

**Instructions source:** [meta-improving-this-playbook.md](../../_meta/meta-improving-this-playbook.md)
(Codified Auto-Sync Process, step 9) and the
[observations template](../../_meta/case-study-observations-template.md).

This records playbook feedback from an auto-sync update run (Mode 2 / Phase 8), the first
sync to follow the formal observation, triage, and log loop. Earlier syncs (v0.6.5 to
v0.7.0) produced a sync artifact but did not record categorized observations.

Source artifact:
[flowmark-rs sync artifact](https://github.com/jlevy/flowmark-rs/blob/main/docs/sync-artifacts/2026-05-30-sync-v0.7.0-to-v0.7.2.md)
(PR [jlevy/flowmark-rs#65](https://github.com/jlevy/flowmark-rs/pull/65)).

## Project Summary

| Field | Value |
| --- | --- |
| Project name | flowmark |
| Source repo | github.com/jlevy/flowmark (Python) |
| Rust repo | github.com/jlevy/flowmark-rs |
| Run mode | `auto-sync-update` |
| Baseline Python version | v0.7.0 |
| Target Python version | v0.7.2 |
| Date | 2026-05-30 |

## Sync Update Context

| Field | Value |
| --- | --- |
| Baseline commit | `v0.7.0` (`448aaf73f3ad`) |
| Target commit | `v0.7.2` (`32d367fc189f`) |
| Accepted pre-existing divergence | escaped-backtick code span (`fmr-qmd8`, upstream Python bug; Rust correct) |
| New intentional divergences | `--docs` body; `--install-skill` runner pins; `install_skill` signature break in a patch release (one semver lint allowed) |

Upstream changes: two real Rust formatting gaps (#35 multi-line HTML comments, width-zero
whitespace collapse), two already-correct-in-Rust (#42 task-list spacing, reference-image
inlining — tests ported only), one CLI feature (#44 `--check`), one file-discovery fix
(#43 force-exclude of explicit files), and the cross-agent skill install (`--surfaces`).
Block-span library API and Python packaging were excluded.

## Phase 8 Observations (Ongoing Synchronization)

Categories map to triage: Helpful is `VALIDATE`, Wrong is `FIX`, Misleading is `CLARIFY`,
Missing is `ADD`, Too-specific is `GENERALIZE`.

### OBS-1: Differential sweep against the built binary (VALIDATE)

Playbook: auto-sync-agent-prompt-template steps 4 to 6 ("probe each changed behavior
against the existing Rust binary; the differential sweep, not the diff, is what proves
parity"). Probing each upstream change against the built binary correctly split the six
library-relevant changes into "real Rust gap" (#35, width-zero) versus "already correct,
port tests only" (#42, reference images). Following the diff alone would have wasted effort
re-implementing #42 and missed that #35's fix belongs in a different layer in Rust (comrak
parses block-level HTML comments as an HtmlBlock; Python disables HTMLBlock and treats them
as a paragraph). Strong positive signal — keep this front and center.

### OBS-2: Generated-doc inputs break when upstream shared docs change (ADD)

Playbook: the update checklist mentions regenerating the README but does not warn that the
generator embeds upstream shared-doc text and can fail when that text changes.
`scripts/generate_rust_readme.py` hard-failed twice after the submodule bump: upstream
removed the "two flavors" perspective sentence the generator's anchor constant matched, and
v0.7.2 introduced a `__FLOWMARK_VERSION__` runner-pin placeholder the Rust generator did
not substitute (the Python generator does). Both surfaced only in the CI "README generation
sync" job, not locally, because the generator needs Python 3.14, which the dev shell
lacked. Suggested change: add a checklist item to re-run every generator that embeds
upstream shared content after the submodule bump and reconcile anchored strings and new
placeholders before relying on the diff.

### OBS-3: Embedded content and golden inputs need enforced LF (ADD, high severity)

Playbook: `guidelines/rust-project-setup.md` does not mention a line-ending policy. The
repo had no `.gitattributes`. The binary embeds `SKILL.md` via `include_str!`, so on a
Windows CI checkout (CRLF) the embedded content carried CRLF and the newline-anchored
assertions failed — Windows-only, invisible on Linux and macOS. It cost two CI cycles to
root-cause (the runner logs were also network-restricted in this environment). Fix: add
`.gitattributes` (`* text=auto eol=lf`); `git add --renormalize` confirmed zero content
churn. Suggested change: tell `rust-project-setup.md` to commit a `.gitattributes`
enforcing `eol=lf` from the start. Any port that embeds text or golden-compares files read
from disk will otherwise hit Windows CRLF failures. High severity: silent,
platform-specific, hard to diagnose without the failing runner's logs.

### OBS-4: Public-API breaks versus a published crate and the semver gate (ADD, CLARIFY)

Playbook: "Version Convention" notes the Rust crate is versioned independently but gives no
guidance for a breaking public-API change against an already-published crate. Porting
`--surfaces` changed `skills::install_skill` from one to three parameters. The crate's
0.3.0 was already on crates.io, so `cargo-semver-checks` failed. The maintainer chose to
keep it a patch release (pre-1.0, no library users); resolved by allowing the single
`function_parameter_count_changed` lint in `Cargo.toml` so the rest of the API stays gated.
Suggested change: a sync-checklist note to check the published baseline (`cargo search`) and
the semver gate early when the public Rust API changes, and decide version-bump versus a
targeted lint allowance with the maintainer.

### OBS-5: CLI parity helpers must tolerate early-exit stdin (ADD)

Playbook: `guidelines/python-to-rust-cli-porting.md` covers SIGPIPE for the binary but not
for test harnesses that pipe stdin to it. A parity helper did `write_all(...).unwrap()`
into the child's stdin. The `--inplace -` case makes the binary reject its args and exit
before reading stdin, so the write raced against process teardown and panicked on
BrokenPipe — intermittently, more often on Windows. Flaky CI is worse than a clean failure.
Suggested change: test helpers that feed stdin must tolerate a broken-pipe write (the child
may exit before reading) and assert on stderr and exit code instead.

### OBS-6: Self-versus-sibling version pinning is a tolerated install divergence (ADD)

Playbook: the cross-implementation skill contract is documented in flowmark source, but the
generic lesson is not in the playbook. Each implementation pins its own package version
dynamically and the sibling from a constant. After the Rust crate bumped to 0.3.1,
`--install-skill` emitted `flowmark-rs==0.3.1` while Python (sibling constant, lagging)
emitted `0.3.0`. Correct by design, but a CLI-output divergence that belongs in the
tolerated-variations list; and Rust has no dev-version fallback (it trusts the cargo
version), unlike Python. Suggested change: when a port mirrors a "pin both packages"
feature, note that own-version pins legitimately diverge across implementations, and flag
that a Rust crate version (always a clean release string) can pin an as-yet-unpublished
version.

### OBS-7: Mapping smoke-test counts and external corpus (CLARIFY)

The flowmark-rs runbook lists `pytest tests/test_smoke.py` and `corpus-parity-check.sh` as
gates. `test_smoke.py` asserts hard-coded discovery counts (python, rust, mapping) that
must be bumped every sync; the failure message is clear but the step is not called out.
`corpus-parity-check.sh` needs an external corpus (`attic/test-docs`) absent from a fresh
clone, so the corpus gate could not run locally; a 33-file by 3-mode repo-Markdown
spot-check was substituted (zero new divergences). Suggested change: note that smoke counts
change each sync and that the corpus gate depends on a non-checked-in corpus.

### OBS-8: End-to-end golden coverage for new CLI surfaces (VALIDATE, ADD)

Upstream added tryscript golden coverage for `--surfaces` (V6 to V12); the sync initially
missed porting them (only the old V1 to V5 were present). Caught on review. Added them plus
content-verification scenarios (read the installed SKILL.md and AGENTS.md, not just check
existence) and filed the content-verification idea upstream (jlevy/flowmark#61). Suggested
change: the sync checklist should include porting new or changed golden suites for any new
CLI surface, and prefer asserting installed content and location, not just existence.

## Triage summary

| OBS | Category | Target doc | Impact / Severity |
| --- | --- | --- | --- |
| OBS-1 | VALIDATE | auto-sync-agent-prompt-template | positive |
| OBS-2 | ADD | port-checklist-update-template, auto-sync template | Most / Med |
| OBS-3 | ADD | rust-project-setup.md | All / High |
| OBS-4 | ADD, CLARIFY | python-to-rust-playbook (Version Convention), update checklist | Most / High |
| OBS-5 | ADD | python-to-rust-cli-porting.md | Most / Med |
| OBS-6 | ADD | auto-sync template (tolerated variations) | Some / Med |
| OBS-7 | CLARIFY | consumer runbooks | Some / Low |
| OBS-8 | VALIDATE, ADD | update checklist | Most / Med |

Highest impact and severity first: OBS-3 (`.gitattributes` / CRLF) and OBS-4 (semver gate
versus published baseline). Both generalize beyond flowmark — any embedded-text port, and
any sync touching a published crate's public API.

## Integration status

This PR integrates the high-confidence, generalizable items directly (OBS-3, OBS-4, OBS-5,
and the OBS-8 / process closure-step). The remaining items (OBS-2, OBS-6, OBS-7) are
recorded here for the maintainer to integrate or defer per Phase C.
