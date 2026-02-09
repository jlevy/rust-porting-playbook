# Rust Porting Playbook

A comprehensive, step-by-step playbook for porting applications to Rust. Built from
real-world experience porting production software with AI coding agents.

Currently focused on **Python-to-Rust** porting. Future editions may cover TypeScript
and other source languages.

## Who This Is For

- **AI coding agents** performing ports with human oversight
- **Engineers** directing AI agents through a porting effort
- **Teams** evaluating whether to port a project to Rust

## Quick Start

**Read one document:**
[`reference/python-to-rust-playbook.md`](reference/python-to-rust-playbook.md) --
the complete 8-phase process from project assessment through ongoing sync. Everything
else in this repo is supporting material referenced from the playbook.

## How This Repo Is Organized

```
rust-porting-playbook/
├── README.md                  # You are here
├── reference/                 # Comprehensive reference docs
│   ├── python-to-rust-playbook.md        ** START HERE **
│   ├── python-to-rust-mapping-reference.md
│   ├── python-to-rust-porting-guide.md
│   ├── rust-cli-best-practices.md
│   ├── rust-code-review-checklist.md
│   ├── python-to-rust-test-coverage-playbook.md
│   ├── port-checklist-initial-template.md
│   └── port-checklist-update-template.md
├── guidelines/                # Compact rules for AI agent context (~2-3k tokens each)
│   ├── python-to-rust-porting-rules.md
│   ├── python-to-rust-cli-porting.md
│   ├── rust-general-rules.md
│   ├── rust-cli-app-patterns.md
│   ├── rust-project-setup.md
│   └── test-coverage-for-porting.md
└── case-studies/              # Real-world porting examples
    └── flowmark/              # Python Markdown formatter → Rust
        ├── flowmark-port-library-choices.md
        ├── flowmark-port-decision-log.md
        ├── flowmark-port-analysis.md
        ├── flowmark-port-migration-plan.md
        ├── flowmark-port-cross-validation.md
        ├── flowmark-port-comrak-bug.md
        └── flowmark-port-wrapping-solution.md
```

### Three layers of documentation

| Layer | Directory | Purpose | When to use |
| --- | --- | --- | --- |
| **Playbook + Reference** | `reference/` | Step-by-step process, detailed mappings, checklists | Start here. The playbook is the primary doc. |
| **Guidelines** | `guidelines/` | Compact rules optimized for AI agent context windows | Load into agent context before porting |
| **Case Studies** | `case-studies/` | Real-world examples with decisions, metrics, lessons | When you hit a specific problem and want to see how it was handled |

## The Porting Process (Summary)

The [playbook](reference/python-to-rust-playbook.md) covers 8 phases:

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
effort, and library workarounds account for roughly half of that. Thorough library
evaluation in Phase 2 is the single highest-leverage activity.

## For AI Agents

The `guidelines/` directory contains compact documents (~2-3k tokens each) designed to
be loaded into an AI agent's context window before starting work. If using
[tbd](https://github.com/jlevy/tbd), load them with:

```bash
tbd guidelines python-to-rust-porting-rules
tbd guidelines rust-project-setup
tbd guidelines test-coverage-for-porting
tbd guidelines python-to-rust-cli-porting
tbd guidelines rust-general-rules
tbd guidelines rust-cli-app-patterns
```

Otherwise, include the raw markdown content in your agent's system prompt or context.

## Case Study: Flowmark

The `case-studies/flowmark/` directory documents the port of
[flowmark](https://github.com/jlevy/flowmark) (a Python Markdown formatter) to
[flowmark-rs](https://github.com/jlevy/flowmark-rs). Key stats:

- ~800 lines Python, ~4,400 lines Rust
- ~6 hours total development time (AI agent + human review)
- 20-40x performance improvement
- 141 tests (139 passing, 2 ignored)
- 14 library workarounds, 3 accepted differences

(See `case-studies/flowmark/` for detailed metrics and methodology.)

The case study covers library evaluation methodology, all technical decisions, workaround
strategies, and a meta-analysis of what can be automated in porting workflows.

## Reference Docs

| Document | What it covers |
| --- | --- |
| [python-to-rust-playbook.md](reference/python-to-rust-playbook.md) | The complete 8-phase porting process |
| [python-to-rust-mapping-reference.md](reference/python-to-rust-mapping-reference.md) | Type mappings, project setup equivalences, dependency tables |
| [python-to-rust-porting-guide.md](reference/python-to-rust-porting-guide.md) | Detailed methodology with pitfalls and automation scripts |
| [rust-cli-best-practices.md](reference/rust-cli-best-practices.md) | Modern Rust CLI project setup (CI, linting, releases, tooling) |
| [rust-code-review-checklist.md](reference/rust-code-review-checklist.md) | Code review checklist for Rust ports |
| [python-to-rust-test-coverage-playbook.md](reference/python-to-rust-test-coverage-playbook.md) | Pre-port test coverage strategy and tooling |
| [port-checklist-initial-template.md](reference/port-checklist-initial-template.md) | 10-phase checklist template (copy and fill in) |
| [port-checklist-update-template.md](reference/port-checklist-update-template.md) | Ongoing sync checklist template |

## Contributing

This playbook is built from real porting experience. If you've ported a project to Rust
and have lessons to share, contributions are welcome -- especially new case studies.

## License

MIT
