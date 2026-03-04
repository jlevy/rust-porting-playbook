# Rust Porting Playbook

A comprehensive, step-by-step **agent playbook** for **automated porting** of
applications to Rust.
It is a collection of **20 in-depth docs** (about 300 pages!)
all agent written but pretty carefully curated, to guide agents in the porting process.

I suggest using the playbook with a strong model (I’ve used Opus 4.6 or Codex 5.3 Extra
High), and beads (I use my own [tbd](https://github.com/jlevy/tbd) but
[the original](https://github.com/steveyegge/beads) should work too) to better automate
the porting plans.

## How Does it Work?

This is new! But it seems to work quite well.
This [Markdown auto-formatter](https://github.com/jlevy/flowmark-rs) was automatically
ported and imho it’s now the best and fastest auto-formatter for Markdown.

In addition to guidelines and playbooks, it’s structured with meta-playbooks to self
improve as we do more ports.
If you do a port, have it track a case study, using my last port as an example, and then
the meta playbook will help improve the overall porting playbook!

Notes and caveats:

- Currently focused on **Python-to-Rust** porting.
  (But a lot is reusable so future editions may cover TypeScript and other source
  languages.)

- This requires **thoroughly testable** Python apps where all features can be mapped to
  Rust. (You don’t need perfect tests to begin with, as long as the agent can add them
  and write equivalent tests in Rust.)

- Ports of libraries and CLI applications are great if they can have
  [golden session tests](https://github.com/jlevy/tbd/blob/main/packages/tbd/docs/guidelines/golden-testing-guidelines.md).
  See my [tryscript](https://github.com/jlevy/tryscript) CLI to make thorough testing
  scripts easy for CLI apps.

- Even if you don’t use the whole playbook, you’ll find giving agents these docs will
  make their coding quality really improve.

Key elements of the approach:

- Increasing test coverage (if needed) on the original app

- Systematically mapping tests from the original to the target Rust application’s tests

- Making heavy use of reusable guidelines to streamline project setup and avoid pitfalls

- Using **case studies** from other ports to refine the overall process

- Codifying the process for ongoing port updates into two kinds: improvements to Rust
  port (type A) and port synchronization with a new release (type B)

## Case Study: Flowmark

The idea of the playbook is it improves via case studies of each porting process.
A good case study is the port of Flowmark, a Markdown formatter.
The result demonstrates full-port execution plus ongoing upstream sync discipline.

- Source project: [flowmark (Python)](https://github.com/jlevy/flowmark)

- Ported project: [flowmark-rs (Rust)](https://github.com/jlevy/flowmark-rs)

With the exception of a few paragraphs in the project README, all code, specs, and docs
in `flowmark-rs` were written entirely by Opus 4.6 and GPT-5.3 Codex.

Opus 4.6 was the vast majority but I did hand off a few sessions to GPT-5.3 for review.
My involvement was in the prompting meta-loop, over about a dozen sessions, telling it
to continue following the playbook.

See the [case study](case-studies/flowmark/) and
[the full port analysis](case-studies/flowmark/flowmark-port-analysis.md) for details:

- Full Python-to-Rust test mapping discipline

- Library evaluation methodology

- Log of technical decisions and workaround strategies for library issues

- Cross-language parity validation and CI enforcement

- Ongoing upstream sync workflow

- A meta-analysis of what can be automated in porting workflows

Beyond the case study docs here, the `flowmark-rs` repo is very useful to agents as a
working reference for what a completed port looks like, including CI workflows, release
automation, test structure, deny.toml, build.rs, and PyPI distribution via maturin.
The bootstrap instructions above include it as a submodule so your agents have direct
access.

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
> **Step 2 — Add the Python source, porting playbook, and reference project as
> submodules**
> 
> ```bash
> mkdir repos
> git submodule add <PYTHON_REPO_URL> repos/<PYTHON_PROJECT>
> git submodule add https://github.com/jlevy/rust-porting-playbook.git repos/rust-porting-playbook
> git submodule add https://github.com/jlevy/flowmark-rs.git repos/flowmark-rs
> ```
> 
> The `flowmark-rs` repo is included as a **working reference project** — a real,
> production Rust port built with this playbook.
> Use it to see concrete examples of Cargo.toml config, CI workflows, release
> automation, test organization, deny.toml, build.rs, maturin/PyPI setup, and more.
> 
> **Step 3 — Read the playbook and begin the port**
> 
> Read `repos/rust-porting-playbook/playbooks/python-to-rust-playbook.md` and follow it
> from Phase 1. Load guidelines as needed from
> `repos/rust-porting-playbook/guidelines/`. Use the case study at
> `repos/rust-porting-playbook/case-studies/flowmark/` for decisions and tradeoffs, and
> browse `repos/flowmark-rs/` for working examples of every config file and workflow.
> 
> *(If using [tbd](https://github.com/jlevy/tbd) for task tracking, also run
> `tbd setup --auto --prefix=<PREFIX>`.)*

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

```mermaid
flowchart TD
    BEGIN([Phase 1 gate passed ✓]) --> P2

    subgraph P2["Phase 2: Research & Library Evaluation"]
        P2_fast{Low-dependency<br/>project?}
        P2_fast -->|Yes| P2_quick[Map to standard equivalents<br/>regex, serde_json, clap]
        P2_fast -->|No| P2_1[Evaluate 2-3 candidates<br/>per high-risk dep]
        P2_1 --> P2_2[Create feature matrices]
        P2_2 --> P2_3[Run proof-of-concept<br/>with real inputs]
        P2_3 --> P2_4[Count and categorize diffs]
        P2_4 --> P2_5[Document decisions<br/>rationale + fallback plans]
        P2_quick --> P2_5
        P2_5 --> P2_6[Optional: best-practices<br/>survey for app type]
    end

    P2 --> P3

    subgraph P3["Phase 3: Plan"]
        P3_1[Define architecture<br/>single crate vs workspace]
        P3_2[Create feature parity matrix]
        P3_3[Plan module porting order<br/>leaf → integration → CLI]
        P3_4[Define acceptance criteria]
        P3_5[Budget effort<br/>35-50% for workarounds]
        P3_1 --> P3_2 --> P3_3 --> P3_4 --> P3_5
    end

    P3 --> P4

    subgraph P4["Phase 4: Set Up"]
        P4_1["cargo init project-rs"]
        P4_2[Configure Cargo.toml<br/>edition, MSRV, lints]
        P4_3[Add Python source<br/>as git submodule]
        P4_4[Set up test fixtures<br/>input/ and expected/]
        P4_5[Set up CI<br/>7+ parallel jobs]
        P4_6[Track version correspondence<br/>in package.metadata]
        P4_1 --> P4_2 --> P4_3 --> P4_4 --> P4_5 --> P4_6
    end

    P4 --> P5

    subgraph P5["Phase 5: Port the Code"]
        P5_loop["For each module (leaf → root):"]
        P5_1[Port tests first]
        P5_2[Implement until tests pass]
        P5_3[Add traceability comments]
        P5_4[Run cross-validation]
        P5_5[Update parity tracking spec]
        P5_loop --> P5_1 --> P5_2 --> P5_3 --> P5_4 --> P5_5
        P5_5 -->|Next module| P5_loop
    end

    P5 --> P6

    subgraph P6["Phase 6: Handle Library Differences"]
        P6_1[Cross-validate all fixtures]
        P6_2[Categorize every diff:<br/>porting bug / library diff /<br/>Python bug / improvement]
        P6_3{Diff category?}
        P6_1 --> P6_2 --> P6_3
        P6_3 -->|Porting bug| P6_fix[Fix immediately]
        P6_3 -->|Library diff| P6_workaround[Try: post-process →<br/>pre-process → accept →<br/>vendor → switch lib]
        P6_3 -->|Python bug| P6_decide[Replicate for parity<br/>or fix in Rust?]
        P6_3 -->|Improvement| P6_doc[Document and accept]
        P6_fix --> P6_track
        P6_workaround --> P6_track
        P6_decide --> P6_track
        P6_doc --> P6_track
        P6_track[Track all with<br/>HACK:/FIXME: comments]
    end

    P6_track --> G6{"More than 3 unfixable diffs<br/>or core feature broken?"}
    G6 -->|"No, or past 50%"| READY([Proceed to Phase 7 ▶])
    G6 -->|"Yes, early enough"| G6_ret(["⟲ Return to Phase 2:<br/>re-evaluate library choices"])

    style G6_ret fill:#efebe9,stroke:#795548
    style P2 fill:#e8f4f8,stroke:#2196F3
    style P3 fill:#e8f4f8,stroke:#2196F3
    style P4 fill:#e8f4f8,stroke:#2196F3
    style P5 fill:#fff3e0,stroke:#FF9800
    style P6 fill:#fff3e0,stroke:#FF9800
    style G6 fill:#fff9c4,stroke:#FFC107
```

For the full set of process flow diagrams (Phases 0-1, 2-6, and 7-8), resource
dependency maps, and document relationships, see the
[Playbook Flow Overview](docs/project/playbook-flow-overview.md).

## For AI Agents

The `guidelines/` directory contains compact documents (~2-3k tokens each) designed to
be loaded into an AI agent’s context window before starting work.
Include the raw markdown files from `guidelines/` in your agent’s system prompt or
context. The key guidelines for porting are:

- `guidelines/python-to-rust-porting-rules.md` — Core porting rules
- `guidelines/rust-project-setup.md` — Project setup patterns
- `guidelines/rust-general-rules.md` — General Rust best practices
- `guidelines/rust-cli-app-patterns.md` — CLI application patterns
- `guidelines/python-to-rust-cli-porting.md` — CLI-specific porting rules
- `guidelines/test-coverage-for-porting.md` — Test coverage strategy
- `guidelines/porting-principles-and-antipatterns.md` — Principles and antipatterns

For a **working reference project**, check out
[flowmark-rs](https://github.com/jlevy/flowmark-rs) — it demonstrates all of these
patterns in a real, production codebase (Cargo.toml, CI workflows, deny.toml, release
automation, test organization, maturin/PyPI distribution, and more).

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
If you’ve ported a project to Rust and have lessons to share, PR them or especially try
adding an entire new case study so the process keeps improving.

## License

MIT
