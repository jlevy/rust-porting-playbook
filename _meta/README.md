# Meta Documentation

This directory contains documentation for improving the Rust Porting Playbook itself.

## Entry Points

| Document | Purpose |
| --- | --- |
| [meta-improving-this-playbook.md](meta-improving-this-playbook.md) | Primary framework for using case studies to improve the playbook |
| [playbook-improvement-log.md](playbook-improvement-log.md) | Chronological change log of playbook/meta-process improvements |
| [plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md](plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md) | Consolidated gap map and implementation record |
| [plans/done/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md](plans/done/plan-2026-02-25-flowmark-case-study-sync-and-readme-highlight.md) | Completed plan for Flowmark case-study sync and README highlight |
| `plans/active/` | Active playbook-improvement plans currently being worked |
| `plans/done/` | Completed playbook-improvement plans kept for history |
| [case-study-observations-template.md](case-study-observations-template.md) | Template for structured per-phase observations during a case study |
| [case-study-improvement-triage-template.md](case-study-improvement-triage-template.md) | Template for converting observations into actionable changes |

## Usage Flow

1. Choose mode:
   initial port via [meta-improving-this-playbook.md](meta-improving-this-playbook.md)
   or sync update via
   [playbooks/auto-sync-agent-prompt-template.md](../playbooks/auto-sync-agent-prompt-template.md).
2. Capture observations with [case-study-observations-template.md](case-study-observations-template.md).
3. Triage findings with [case-study-improvement-triage-template.md](case-study-improvement-triage-template.md).
4. Track active work in `plans/active/` and archive completed plans to `plans/done/`.
5. Record approved changes and outcomes in [playbook-improvement-log.md](playbook-improvement-log.md).

## Ownership and Cadence

- **Owner:** repository maintainers (`@jlevy` + collaborators for this repo)
- **Review cadence:** monthly meta-doc review, plus ad-hoc review after each significant
  case-study update or upstream sync cycle
- **Definition of done for doc changes:** merged doc update + corresponding entry in
  [playbook-improvement-log.md](playbook-improvement-log.md)

## Link Validation

Before merging meta/playbook changes, run a link check across core docs:

```bash
lychee README.md _meta/**/*.md playbooks/**/*.md guidelines/**/*.md case-studies/**/*.md
```
