# Rust Porting Playbook

A comprehensive, step-by-step **agent playbook** for **automated porting** of
applications to Rust.
It is a collection of **20 in-depth docs** (about 300 pages!) all agent written but
pretty carefully curated, to guide agents in the porting process.

I suggest using the playbook with a strong model (I’ve used Opus 4.6 or Codex 5.3 Extra
High), and beads (I use my own [tbd](https://github.com/jlevy/tbd) but
[the original](https://github.com/steveyegge/beads) should work too) to better automate
the porting plans.

## How Does it Work?

This is new! But it seems to work quite well.
This [Markdown auto-formatter](https://github.com/jlevy/flowmark-rs) was automatically
ported and imho it’s now the best and fastest auto-formatter for Markdown.

In addition to guidelines and playbooks, it’s structurted with meta-playbooks to self
improve as we do more ports.
If you do a port, have it track a case study, using my last port as an example, and then
the meta playbook will help improve the overall porting playbook!

Notes and caveats:

- Currently focused on **Python-to-Rust** porting.
  (But a lot is reusable so future editions may cover TypeScript and other source
  languages.)

- This requires **thoroughly testable** Python apps where all features can be mapped to
  Rust. (You don’t need prefect tests to begin with, as long as the agent can add them
  and write equivalent tests in Rust.)

- Ports of libraries and CLI applications are great if they can have
  [golden session tests](https://github.com/jlevy/tbd/blob/main/packages/tbd/docs/guidelines/golden-testing-guidelines.md).
  See my [tryscript](https://github.com/jlevy/tryscript) CLI to make thorough testing
  scripts easy for CLI apps.

- Even if you don’t use the whole playbook, you’ll find giving agents these docs will
  make their coding quality really improve.

The overall idea is
- Increasing test coverage (if needed) on the original app
- Systematically mapping tests from the original to the target Rust application’s tests
- Making heavy use of reusable guidelines to streamline project setup and avoid pitfalls
- Using **case studies** for ports to refine the overall process
- Codifying the process for future port updates into into two kinds: improvements to
  Rust port (type A) and port synchronization with a new release (type B)

## Case Study: Flowmark

Here’s the first nontrivial use of this playbook.
The result demonstrates full-port execution plus ongoing upstream sync discipline.
It was mostly Opus 4.6.

- Source project: [flowmark (Python)](https://github.com/jlevy/flowmark)

- Ported project: [flowmark-rs (Rust)](https://github.com/jlevy/flowmark-rs)

This is packaged here as a [case study](case-studies/flowmark/) with
[details and lessons](case-studies/flowmark/flowmark-port-analysis.md) to illustrate:

- Full Python→Rust lifecycle, including post-port synchronization

- Decision logs, library tradeoffs, discrepancy handling, and cross-validation

All this is docs that help an agent make better Rust ports!
The case studies can be reused for helping agents on the meta-process of playbook
improvement.

## Quick Start

### New port (bootstrapping a Rust project from Python)

Copy-paste the following **bootstrap instructions** to your agent to get started.
The agent will set up the workspace, pull in the playbook as a submodule, and then use
the playbook itself to drive the rest of the process.

> **Bootstrap a Python-to-Rust port**
>
> I want to port `<PYTHON_PROJECT>` (at `<PYTHON_REPO_URL>`) to Rust.
> Follow these steps to set up the workspace, then use the playbook to drive the port.
>
> **Step 1 — Create the Rust project and workspace**
>
> ```bash
> cargo init <PROJECT>-rs
> cd <PROJECT>-rs
> ```
>
> **Step 2 — Add the Python source and porting playbook as submodules**
>
> ```bash
> mkdir repos
> git submodule add <PYTHON_REPO_URL> repos/<PYTHON_PROJECT>
> git submodule add https://github.com/jlevy/rust-porting-playbook.git repos/rust-porting-playbook
> ```
>
> **Step 3 — Read the playbook and begin the port**
>
> Read `repos/rust-porting-playbook/playbooks/python-to-rust-playbook.md` and follow it
> from Phase 1.
> Load guidelines as needed from `repos/rust-porting-playbook/guidelines/`.
> Use the case study at `repos/rust-porting-playbook/case-studies/flowmark/` as a
> reference for decisions and tradeoffs.
>
> *(If using [tbd](https://github.com/jlevy/tbd) for issue tracking, also run
> `tbd setup --auto --prefix=<PREFIX>` and load guidelines with
> `tbd guidelines python-to-rust-porting-rules`, etc.)*

Replace `<PYTHON_PROJECT>`, `<PYTHON_REPO_URL>`, `<PROJECT>`, and `<PREFIX>` with your
actual values.

### Existing port (syncing with a new upstream release)

- [`playbooks/port-checklist-update-template.md`](playbooks/port-checklist-update-template.md)
  + [`playbooks/auto-sync-agent-prompt-template.md`](playbooks/auto-sync-agent-prompt-template.md)

Everything else in this repo is supporting material referenced from these entry points.

## How This Repo Is Organized

```
rust-porting-playbook/
├── README.md                  # You are here
├── _meta/                     # Meta-process docs for improving the playbook
│   ├── README.md
│   ├── meta-improving-this-playbook.md
│   ├── case-study-observations-template.md
│   ├── case-study-improvement-triage-template.md
│   ├── playbook-improvement-log.md
│   └── plans/
│       ├── README.md
│       ├── active/
│       └── done/
├── playbooks/                 # Core playbook and detailed reference docs
│   ├── python-to-rust-playbook.md        ** START HERE **
│   ├── python-to-rust-mapping-reference.md
│   ├── python-to-rust-porting-guide.md
│   ├── rust-cli-best-practices.md
│   ├── rust-code-review-checklist.md
│   ├── cross-language-test-mapping.md
│   ├── python-to-rust-test-coverage-playbook.md
│   ├── port-checklist-initial-template.md
│   ├── port-checklist-update-template.md
│   ├── auto-sync-agent-prompt-template.md
│   └── python-to-rust-sync-release-workflow.md
├── guidelines/                # Compact rules for AI agent context (~2-3k tokens each)
│   ├── python-to-rust-porting-rules.md
│   ├── python-to-rust-cli-porting.md
│   ├── rust-general-rules.md
│   ├── rust-cli-app-patterns.md
│   ├── rust-project-setup.md
│   ├── test-coverage-for-porting.md
│   ├── porting-principles-and-antipatterns.md
│   └── ...
├── docs/project/research/     # In-depth research on specific topics
│   ├── research-rust-cli-binary-distribution.md
│   └── research-rust-cli-pypi-distribution.md
├── case-studies/              # Real-world porting examples
│   └── flowmark/              # Python Markdown formatter → Rust
│       ├── README.md
│       ├── flowmark-port-library-choices.md
│       ├── flowmark-port-decision-log.md
│       ├── flowmark-port-analysis.md
│       ├── flowmark-port-metrics.md
│       ├── flowmark-port-migration-plan.md
│       ├── flowmark-port-cross-validation.md
│       ├── flowmark-port-comrak-bug.md
│       └── flowmark-port-wrapping-solution.md
```

### Five layers of documentation

| Layer | Directory | Purpose | When to use |
| --- | --- | --- | --- |
| **Playbook + Reference** | `playbooks/` | Step-by-step process, detailed mappings, checklists | Start here. The playbook is the primary doc. |
| **Guidelines** | `guidelines/` | Compact rules optimized for AI agent context windows | Load into agent context before porting |
| **Research** | `docs/project/research/` | In-depth investigation of specific topics (distribution, packaging) | When you need deep research on a specific area |
| **Case Studies** | `case-studies/` | Real-world examples with decisions, metrics, lessons | When you hit a specific problem and want to see how it was handled |
| **Meta Process** | `_meta/` | How to improve the playbook itself via case studies | Use when contributing playbook improvements |

### Documentation Taxonomy

- **Playbook:** normative end-to-end process (what to do, in order)
- **Guide:** deep explanatory detail and implementation patterns
- **Checklist template:** copy-and-fill execution checklist for a run
- **Guideline:** compact high-signal rules for agent context windows
- **Case study:** empirical evidence from a real port
- **Meta plan:** backlog/planning artifact for improving the docs themselves

## The Porting Process (Summary)

The [playbook](playbooks/python-to-rust-playbook.md) covers these core phases:

| Phase | What happens | Key output |
| --- | --- | --- |
| 1. **Assess** | Measure codebase, test coverage, dependencies | Dependency risk table, go/no-go decision |
| 2. **Research** | Evaluate Rust library candidates with real inputs | Library decisions with fallback plans |
| 3. **Plan** | Architecture, module order, feature parity matrix | Porting plan with effort budget |
| 4. **Set up** | Cargo.toml, CI, test fixtures, Python submodule | Building, tested, CI-green skeleton |
| 5. **Port** | Tests first, module by module, leaf to root | All tests passing |
| 6. **Fix** | Cross-validate, categorize diffs, build workarounds | All differences resolved or documented |
| 7. **Finalize** | CLI parity, docs, release config | Production-ready |
| 8. **Sync** | Track Python updates, manage divergences | Ongoing maintenance |

**Key insight from real ports:** Phases 5-6 (porting + fixing) consume ~70% of total
effort, and library workarounds account for roughly half of that.
Thorough library evaluation in Phase 2 is the single highest-leverage activity.

## For AI Agents

The `guidelines/` directory contains compact documents (~2-3k tokens each) designed to
be loaded into an AI agent’s context window before starting work.
If using [tbd](https://github.com/jlevy/tbd), load them with:

```bash
tbd guidelines python-to-rust-porting-rules    # guidelines/python-to-rust-porting-rules.md
tbd guidelines rust-project-setup               # guidelines/rust-project-setup.md
tbd guidelines test-coverage-for-porting        # guidelines/test-coverage-for-porting.md
tbd guidelines python-to-rust-cli-porting       # guidelines/python-to-rust-cli-porting.md
tbd guidelines rust-general-rules               # guidelines/rust-general-rules.md
tbd guidelines rust-cli-app-patterns            # guidelines/rust-cli-app-patterns.md
```

Otherwise, include the raw markdown files from `guidelines/` in your agent’s system
prompt or context.

## Case Study: Flowmark

The `case-studies/flowmark/` directory documents the port of
[flowmark](https://github.com/jlevy/flowmark) (a Python Markdown formatter) to
[flowmark-rs](https://github.com/jlevy/flowmark-rs).
Current outcomes include:

- A non-trivial Python CLI codebase successfully ported to Rust
- Full Python test-to-Rust mapping discipline
- Cross-language parity validation and CI enforcement
- Documented workaround tracking and ongoing upstream sync workflow

(See `case-studies/flowmark/` for detailed methodology.
Canonical metrics are in
[`case-studies/flowmark/flowmark-port-metrics.md`](case-studies/flowmark/flowmark-port-metrics.md).)

The case study covers library evaluation methodology, all technical decisions,
workaround strategies, and a meta-analysis of what can be automated in porting
workflows.

## Reference Docs

| Document | What it covers |
| --- | --- |
| [python-to-rust-playbook.md](playbooks/python-to-rust-playbook.md) | The complete phased porting process |
| [python-to-rust-mapping-reference.md](playbooks/python-to-rust-mapping-reference.md) | Type mappings, project setup equivalences, dependency tables |
| [python-to-rust-porting-guide.md](playbooks/python-to-rust-porting-guide.md) | Detailed methodology with pitfalls and automation scripts |
| [rust-cli-best-practices.md](playbooks/rust-cli-best-practices.md) | Modern Rust CLI project setup (CI, linting, releases, tooling) |
| [rust-code-review-checklist.md](playbooks/rust-code-review-checklist.md) | Code review checklist for Rust ports |
| [cross-language-test-mapping.md](playbooks/cross-language-test-mapping.md) | YAML-based test mapping with CI enforcement |
| [python-to-rust-test-coverage-playbook.md](playbooks/python-to-rust-test-coverage-playbook.md) | Pre-port test coverage strategy and tooling |
| [port-checklist-initial-template.md](playbooks/port-checklist-initial-template.md) | Expanded execution checklist template (copy and fill in) |
| [port-checklist-update-template.md](playbooks/port-checklist-update-template.md) | Ongoing sync checklist template |
| [auto-sync-agent-prompt-template.md](playbooks/auto-sync-agent-prompt-template.md) | Canonical prompt for syncing existing Rust ports to new upstream Python releases |
| [python-to-rust-sync-release-workflow.md](playbooks/python-to-rust-sync-release-workflow.md) | Two-stage release-refresh workflow: Rust-only stabilization release, then upstream sync release |

## Research Docs

| Document | What it covers |
| --- | --- |
| [research-rust-cli-binary-distribution.md](docs/project/research/research-rust-cli-binary-distribution.md) | Survey of how 14 Rust CLI tools distribute binaries (GitHub Actions, cargo-dist, cross-compilation) |
| [research-rust-cli-pypi-distribution.md](docs/project/research/research-rust-cli-pypi-distribution.md) | Distributing Rust CLI binaries via PyPI using maturin (ruff/uv pattern, workflow templates, platform targets) |

## Meta Docs

| Document | What it covers |
| --- | --- |
| [meta-improving-this-playbook.md](_meta/meta-improving-this-playbook.md) | Process for improving the playbook through case studies |
| [case-study-observations-template.md](_meta/case-study-observations-template.md) | Template for recording observations during a port |
| [case-study-improvement-triage-template.md](_meta/case-study-improvement-triage-template.md) | Template for triaging observations into playbook changes |
| [playbook-improvement-log.md](_meta/playbook-improvement-log.md) | Chronological log of playbook and meta-process improvements |
| [plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md](_meta/plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md) | Consolidated gap map and implementation plan for playbook improvements |
| [plans/done/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md](_meta/plans/done/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md) | Completed plan to synchronize Flowmark case-study docs and improve top-level summary |

## Improving This Playbook

This playbook improves through real-world case studies.
Each port conducted using the playbook generates structured feedback that is integrated
back into the playbook, making it more accurate and complete with every case study.

See [`_meta/meta-improving-this-playbook.md`](_meta/meta-improving-this-playbook.md) for
the full process.

### How to contribute a case study

1. Pick a Python project to port (ideally 500+ lines with good test coverage)
2. Follow the playbook end-to-end, recording observations using the
   [observation template](_meta/case-study-observations-template.md)
3. Submit a PR with your case study in `case-studies/<project-name>/`
4. The observations will be triaged and integrated into the playbook

### Case studies completed

| Project | Size | Domain | Key learnings |
| --- | --- | --- | --- |
| [flowmark](case-studies/flowmark/) | Complex multi-thousand-line Python app ported to Rust | Markdown formatting CLI | Parser workarounds dominate effort; cross-language test mapping as CI gate; porting principles distilled |

## Contributing

This playbook is built from real porting experience.
If you’re ported a project to Rust and have lessons to share, PR them or especially try
adding an entire new case study so the process keeps improving.

## License

MIT
