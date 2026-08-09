# Contributing

Contributions should improve the playbook with evidence from real ports, correct a
specific technical error, or make the existing process easier to apply.

## Choose the Right Location

- Put executable workflows and checklists in `playbooks/`.
- Put source-language-independent Rust engineering rules in the general suite indexed
  by `guidelines/README.md`.
- Put translation, parity, traceability, and synchronization rules in the porting
  section of `guidelines/`.
- Put lookup material and pattern catalogs in `references/`.
- Put source-backed investigations in `docs/project/research/`.
- Put evidence from completed or active ports in `case-studies/`.
- Put changes to the playbook-improvement process in `_meta/`.

Classify guidance by the question it answers: how Rust should be built belongs in the
general Rust suite; how source behavior maps to Rust belongs in porting guidance.
Avoid duplicating guidance across layers. Add a concise cross-reference to the
authoritative document instead.

## Validate Changes

Run the same checks as CI from the repository root:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/check_docs.py
UV_NO_BUILD=1 uv --no-config lock --check \
  --script docs/project/research/data/extract_lockfile_inventory.py
python3 scripts/check_dependency_cooloff.py
python3 scripts/check_lockfile_inventories.py
bash -n \
  .claude/hooks/tbd-closing-reminder.sh \
  .claude/scripts/ensure-gh-cli.sh \
  .claude/scripts/tbd-session.sh \
  .codex/ensure-gh-cli.sh \
  .codex/tbd-closing-reminder.sh \
  .codex/tbd-session.sh
```

The unit suite runs the lockfile inventory script end to end against a deterministic
synthetic lockfile. `scripts/check_lockfile_inventories.py` downloads the exact tbd and
qmd source commits, verifies each lockfile’s SHA-256 digest, regenerates all six
research artifacts, and fails on byte-level drift.
`scripts/check_dependency_cooloff.py` independently verifies that every registry
artifact in tracked PEP 723 uv lockfiles has at least 14 days of public exposure.
`scripts/check_docs.py` checks every tracked text file for forbidden invisible or
bidirectional Unicode and every Markdown file for broken relative links, missing
anchors, and unclosed fenced code blocks.

## Review Supply-Chain Changes

Read [`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md) before adding or upgrading
executable dependencies, actions, tool downloads, agent hooks, or editor automation.
Apply the 14-day cool-off, require a concrete reason for each upgrade, review immutable
source changes, and record any exception in
[`SUPPLY-CHAIN-AUDIT-LOG.md`](SUPPLY-CHAIN-AUDIT-LOG.md).

## Submit Changes

Explain the evidence behind factual or process changes.
For new case studies, start with `_meta/case-study-observations-template.md` and follow
the closure loop in `_meta/meta-improving-this-playbook.md`.

Keep pull requests focused.
Separate broad mechanical reformatting from substantive documentation changes so
reviewers can evaluate technical content.
