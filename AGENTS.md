# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this
project.

<!-- BEGIN TBD INTEGRATION format=f06 surface=agents-md -->
## tbd

This repository uses **tbd** for git-native issue tracking (beads), spec-driven
planning, and on-demand engineering guidelines.
As the agent, you operate tbd on the user’s behalf: translate their requests into tbd
actions rather than telling them to run commands.

- Run `tbd prime` to load current project state and the full tbd workflow.
- Run `tbd skill` for the complete reusable tbd skill instructions.
- Run `tbd shortcut --list` and `tbd guidelines --list` for on-demand resources.
- Track all work as beads: `tbd create`, `tbd ready`, `tbd close`, and `tbd sync`.

<!-- END TBD INTEGRATION -->

## Build & Test

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/check_docs.py
uv --no-config lock --check --script docs/project/research/data/extract_lockfile_inventory.py
```

## Architecture Overview

This is a documentation-first repository.
`playbooks/` contains executable workflows, `guidelines/` contains compact agent rules,
`references/` contains lookup material, `case-studies/` contains evidence from real
ports, and `_meta/` governs improvements to the playbook itself.
The only executable research utility is the locked PEP 723 script under
`docs/project/research/data/`.

## Conventions & Patterns

Read `CONTRIBUTING.md` before changing documentation and `SUPPLY-CHAIN-SECURITY.md`
before adding or updating executable dependencies.
