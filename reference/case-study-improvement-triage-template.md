# Case Study Improvement Triage Template

**Instructions:** After completing a case study port, use this template to triage
observations into actionable playbook improvements. Copy this file and fill it in
during Phase B of the meta-playbook process.

**Related:**
[Meta-playbook](meta-improving-this-playbook.md) |
[Observation Template](case-study-observations-template.md)

---

## Case Study

| Field | Value |
| --- | --- |
| Project name | |
| Observations file | `case-studies/<project>/<project>-port-observations.md` |
| Date triaged | |
| Triaged by | |

---

## Triage Categories

- **FIX** — Playbook says something wrong (factual error, non-compiling code, outdated
  dependency)
- **ADD** — Playbook is missing guidance that was needed during the port
- **CLARIFY** — Playbook is ambiguous or misleading (technically correct but confusing)
- **GENERALIZE** — Playbook is too flowmark-specific; needs to be broadened
- **VALIDATE** — Playbook guidance was confirmed correct (no change needed)

---

## FIX Items

### FIX-1: [Short title]

**Source phase:** [Phase N from observations]
**Severity:** [High / Medium / Low]
**Impact:** [How many future ports affected]

**Target file:** `[e.g., reference/python-to-rust-playbook.md]`
**Section:** [Section heading]

**Current text:**
> [Quote the incorrect text]

**Proposed text:**
> [The corrected text]

**Justification:**
[What happened in the case study that revealed this was wrong]

---

## ADD Items

### ADD-1: [Short title]

**Source phase:** [Phase N from observations]
**Severity:** [High / Medium / Low]
**Impact:** [How many future ports affected]

**Target file:** `[e.g., guidelines/rust-general-rules.md]`
**Section:** [Section heading, or "New section after X"]

**Proposed text:**
> [The new content to add]

**Justification:**
[What happened in the case study that revealed this was missing]

---

## CLARIFY Items

### CLARIFY-1: [Short title]

**Source phase:** [Phase N from observations]
**Severity:** [High / Medium / Low]
**Impact:** [How many future ports affected]

**Target file:** `[e.g., reference/python-to-rust-mapping-reference.md]`
**Section:** [Section heading]

**Current text:**
> [Quote the ambiguous text]

**Proposed text:**
> [The clarified text]

**Justification:**
[What happened in the case study that revealed this was misleading]

---

## GENERALIZE Items

### GENERALIZE-1: [Short title]

**Source phase:** [Phase N from observations]
**Severity:** [High / Medium / Low]
**Impact:** [How many future ports affected]

**Target file:** `[e.g., case-studies/flowmark/flowmark-port-analysis.md]`
**Section:** [Section heading]

**Current text:**
> [Quote the too-specific text]

**Proposed text:**
> [The generalized text]

**Justification:**
[What in the case study showed the original was too narrow]

---

## VALIDATE Items

List observations that confirmed the playbook was correct. These are valuable positive
signals — they indicate which parts of the playbook are stable.

| Phase | What was validated | Playbook doc + section |
| --- | --- | --- |
| | | |

---

## Priority Summary

Rank all FIX, ADD, CLARIFY, and GENERALIZE items by priority for implementation:

| # | ID | Category | Title | Severity | Impact | Target file |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

---

## Next Steps

- [ ] Human review of proposed changes (estimated time: __ minutes)
- [ ] Create plan spec for approved changes
- [ ] Implement changes (Phase C of meta-playbook)
- [ ] Update README case study table
