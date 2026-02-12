# Case Study Observations Template

**Instructions:** Copy this file to `case-studies/<project-name>/<project>-port-observations.md`
before starting the port. Fill in each phase section as you complete it. Do not skip
phases — even if a phase was trivial, record that it was trivial and why.

**Observation IDs:** Number each observation sequentially across all phases (OBS-1,
OBS-2, etc.) so they can be referenced during triage. A phase may produce zero or
multiple observations.

**Category mapping to triage:** The per-phase assessment checkboxes map to triage
categories as follows:

| Assessment | Triage category | Action |
| --- | --- | --- |
| Helpful | `VALIDATE` | No change needed (positive signal) |
| Wrong | `FIX` | Must fix (factual error, non-compiling code) |
| Misleading | `CLARIFY` | Rewrite for clarity |
| Missing | `ADD` | Add new content |
| Too specific | `GENERALIZE` | Rewrite to be general |

**Related:**
[Meta-playbook](meta-improving-this-playbook.md) |
[Improvement Triage Template](case-study-improvement-triage-template.md)

---

## Project Summary

| Field | Value |
| --- | --- |
| Project name | |
| Source repo | |
| Rust repo | |
| Python version | |
| Python LOC (app) | |
| Python LOC (tests) | |
| Domain | |
| Key dependencies | |
| Date started | |
| Date completed | |

---

## Phase 1: Assess the Original Project

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from `reference/python-to-rust-playbook.md`, Phase 1, with section reference]

### What actually happened
[Description of actual experience during assessment]

### Playbook assessment
- [ ] Helpful — guidance was accurate and useful → `VALIDATE`
- [ ] Wrong — guidance was factually incorrect: [what should change] → `FIX`
- [ ] Misleading — guidance was technically correct but led astray: [why] → `CLARIFY`
- [ ] Missing — no guidance existed for this situation: [what to add] → `ADD`
- [ ] Too specific — guidance was flowmark-specific, not general: [how to generalize] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 1"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[How hard was this phase? Easy / Moderate / Hard — and why]

### Time spent
[e.g., "15 minutes, all agent"]

---

## Phase 2: Research and Library Evaluation

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 2]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 2"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 3: Plan the Port

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 3]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 3"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 4: Set Up the Rust Project

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 4]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `guidelines/rust-project-setup.md` or `reference/python-to-rust-playbook.md` section "Phase 4"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 5: Port the Code

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 5]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 5" or `guidelines/python-to-rust-porting-rules.md`]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 6: Handle Library Differences

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 6]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 6"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 7: Finalize and Validate

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 7]

### What actually happened
[Description]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 7" or `reference/rust-cli-best-practices.md`]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why]

### Time spent

---

## Phase 8: Ongoing Synchronization

### Observation ID: OBS-[N]

### What the playbook said
> [Quote from playbook Phase 8]

### What actually happened
[Description — note: if the Python project has not been updated since the port,
record "Not applicable yet" and describe whether the playbook's sync guidance
seems sufficient based on the project's structure]

### Playbook assessment
- [ ] Helpful → `VALIDATE`
- [ ] Wrong: [details] → `FIX`
- [ ] Misleading: [details] → `CLARIFY`
- [ ] Missing: [details] → `ADD`
- [ ] Too specific: [details] → `GENERALIZE`
- [ ] Not yet applicable — no Python updates during case study period

### Suggested playbook change
**File:** [e.g., `reference/python-to-rust-playbook.md` section "Phase 8"]
**Change:** [Specific text change or addition, or "None"]

### Difficulty
[Easy / Moderate / Hard — and why, or "N/A" if sync not yet exercised]

### Time spent

---

## Overall Summary

### Final metrics

| Metric | Value |
| --- | --- |
| Python LOC (app) | |
| Python LOC (tests) | |
| Rust LOC (app) | |
| Rust LOC (tests) | |
| Rust/Python ratio (app) | |
| Rust/Python ratio (total) | |
| Test count (unit) | |
| Test count (integration) | |
| Test count (doctests) | |
| Total time | |
| Time per phase | |
| Agent vs. human time | |
| Playbook issues found | [total, by category: FIX/ADD/CLARIFY/GENERALIZE/VALIDATE] |

### Dependency LOC comparison

| Python dep | LOC | Rust dep | LOC | Notes |
| --- | --- | --- | --- | --- |

### Playbook issue counts

| Category | Triage | Count | Examples |
| --- | --- | --- | --- |
| Helpful | `VALIDATE` | | |
| Wrong | `FIX` | | |
| Misleading | `CLARIFY` | | |
| Missing | `ADD` | | |
| Too specific | `GENERALIZE` | | |
| **Total observations** | | | |

### Top insights

1. [Most important thing learned about the playbook from this port]
2. [Second most important]
3. [Third most important]
