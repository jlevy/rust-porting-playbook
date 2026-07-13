# Contributing

Contributions should improve the playbook with evidence from real ports, correct a
specific technical error, or make the existing process easier to apply.

## Choose the Right Location

- Put executable workflows and checklists in `playbooks/`.
- Put concise, reusable engineering rules in `guidelines/`.
- Put lookup material and pattern catalogs in `references/`.
- Put source-backed investigations in `docs/project/research/`.
- Put evidence from completed or active ports in `case-studies/`.
- Put changes to the playbook-improvement process in `_meta/`.

Avoid duplicating guidance across layers.
Add a concise cross-reference to the detailed source instead.

## Validate Changes

Run the same checks as CI from the repository root:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/check_docs.py
uv --no-config lock --check \
  --script docs/project/research/data/extract_lockfile_inventory.py
bash -n \
  .claude/hooks/tbd-closing-reminder.sh \
  .claude/scripts/ensure-gh-cli.sh \
  .claude/scripts/tbd-session.sh \
  .codex/ensure-gh-cli.sh \
  .codex/tbd-closing-reminder.sh \
  .codex/tbd-session.sh
```

The tests include an end-to-end run of the lockfile inventory script in its locked `uv`
environment. `scripts/check_docs.py` checks every tracked Markdown file for broken
relative links, missing anchors, and unclosed fenced code blocks.

## Submit Changes

Explain the evidence behind factual or process changes.
For new case studies, start with `_meta/case-study-observations-template.md` and follow
the closure loop in `_meta/meta-improving-this-playbook.md`.

Keep pull requests focused.
Separate broad mechanical reformatting from substantive documentation changes so
reviewers can evaluate technical content.
