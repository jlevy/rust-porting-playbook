# Meta Documentation

This directory contains documentation for improving the Rust Porting Playbook itself.

## Entry Points

| Document | Purpose |
| --- | --- |
| [meta-improving-this-playbook.md](meta-improving-this-playbook.md) | Primary framework for using case studies to improve the playbook |
| [playbook-improvement-log.md](playbook-improvement-log.md) | Chronological change log of playbook/meta-process improvements |
| [plans/README.md](plans/README.md) | Stable lifecycle index for active and completed meta-plan records |
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

## Repository Validation

Before merging meta/playbook changes, run the repository validator
from the repository root:

```bash
python3 scripts/check_docs.py
```

This checks forbidden invisible Unicode across all tracked text, plus local links,
anchors, and code fences across all tracked Markdown, including files outside the core
directories.
