# Improving This Playbook

A systematic process for improving the Rust Porting Playbook through real-world case
studies. Each port conducted using the playbook generates structured feedback that is
integrated back, creating a feedback loop where every case study makes the playbook more
accurate and complete.

**Related:** [Playbook](../playbooks/python-to-rust-playbook.md) |
[Observation Template](case-study-observations-template.md) |
[Improvement Triage Template](case-study-improvement-triage-template.md) |
[Improvement Log](playbook-improvement-log.md) |
[Current Gap Map Plan](plans/done/plan-2026-02-25-playbook-meta-gap-map-and-structure.md)
| [Auto-Sync Agent Prompt](../playbooks/auto-sync-agent-prompt-template.md)

* * *

## Why Case Studies Matter

The playbook was built primarily from the flowmark case study.
Initial port baseline (2025-11) was ~2,000 lines Python app code; current flowmark state
(2026-03-04) is ~4,250 lines Python app code and ~7,250 lines Rust app code.
While flowmark is a good test case, it represents a single data point.
The playbook will improve significantly with additional case studies covering:

- **Different domains:** web services, data processing, ML tooling, DevOps utilities
- **Different sizes:** 100-line scripts to 10,000+ line applications
- **Different dependency profiles:** heavy I/O, database, HTTP, async
- **Different library mapping challenges:** good equivalents vs.
  no equivalents

Each case study is an opportunity to discover:

- Guidelines that are wrong or misleading in practice
- Missing guidance that agents need but the playbook doesn’t provide
- Patterns that generalize beyond flowmark
- Patterns that were flowmark-specific and shouldn’t be presented as universal

## The Process: Three Phases

### Phase A: Conduct a Case Study Port

An agent follows the playbook end-to-end to port a real Python project to Rust,
recording structured observations along the way.

#### A.1 Select a candidate project

Good candidates for case studies have:

- **Test coverage (standard mode):** At minimum 80% core-library line coverage.
  Without tests, the playbook’s test-first approach can’t be followed.
- **Test coverage (exploratory mode):** 60-79% can be used only if explicitly marked as
  exploratory and non-generalizing in conclusions.
- **Sufficient size:** At least 500 lines of Python app code.
  Smaller projects don’t exercise enough of the playbook to produce useful feedback.
- **Clear dependencies:** A `requirements.txt`, `pyproject.toml`, or `setup.py` that
  lists all dependencies explicitly.
- **Different character from existing case studies:** Cover a domain, size bracket, or
  dependency profile not yet represented.

Ideal candidates by priority mix:

1. **HTTP clients/servers:** Exercises async, reqwest/hyper, serde — areas the playbook
   needs broader validation in
2. **Data processing pipelines:** Exercises iterators, parallelism, file I/O patterns
3. **Libraries with public APIs:** Exercises API design guidance, trait-based
   abstractions
4. **CLI tools with I/O:** Still valuable, but should not dominate case-study mix

#### A.2 Set up the case study

1. Read all playbook guidelines (load the `guidelines/` directory into agent context)
2. Set up the Rust project per `guidelines/rust-project-setup.md`
3. Create the case study directory: `case-studies/<project-name>/`
4. Create the observation file:
   `case-studies/<project-name>/<project>-port-observations.md` (copy from
   [`case-study-observations-template.md`](case-study-observations-template.md))

#### A.3 Execute the 8-phase methodology

Follow `python-to-rust-playbook.md` phases 1-8 (assess, research, plan, set up, port,
fix, finalize, sync).
For each phase, **before moving to the next phase**, record an observation entry in the
observations file. Number each observation sequentially (OBS-1, OBS-2, etc.)
for traceability into triage.

**Note on Phase 8 (Ongoing Synchronization):** This phase is only exercisable if the
Python project has been updated since the port began.
If not, record the observation as “Not yet applicable” and note whether the playbook’s
sync guidance appears sufficient based on the project’s structure.

The observation captures:

- What the playbook said to do (quote the specific doc, section, and line)
- What actually happened
- Where the playbook was helpful, wrong, misleading, missing, or too specific
- A suggested playbook change if applicable

See the [observation template](case-study-observations-template.md) for the full format.

#### A.4 Produce standard case study artifacts

Mirror flowmark’s structure:

| Artifact | Purpose |
| --- | --- |
| `<project>-port-analysis.md` | What could be automated vs. what required judgment |
| `<project>-port-library-choices.md` | Library evaluation: candidates, selection criteria, decision |
| `<project>-port-decision-log.md` | All decisions with rationale and alternatives considered |
| `<project>-port-observations.md` | Structured playbook feedback (the key new artifact) |

#### A.5 Produce a final metrics summary

Include in the decision log:

| Metric | How to measure |
| --- | --- |
| Python LOC (app) | Count `.py` files excluding tests, from actual repo |
| Python LOC (tests) | Count test files, from actual repo |
| Rust LOC (app) | Count `.rs` files in `src/` excluding `#[cfg(test)]` blocks |
| Rust LOC (tests) | Inline `#[cfg(test)]` blocks + `tests/` directory |
| Rust/Python ratio | App code and total |
| Dependency LOC | Third-party only, not stdlib |
| Test count | Unit, integration, doctests — separately |
| Time per phase | Wall clock, with agent vs. human breakdown |
| Playbook issues found | Count by category: FIX, ADD, CLARIFY, GENERALIZE, VALIDATE |

#### A.6 Metrics command recipes (standardized)

Capture commands and artifacts in the case-study repo so metrics are reproducible.

```bash
# Python app LOC (exclude tests)
rg --files -g '*.py' | rg -v '(^|/)(test|tests)/|(_test\\.py$)' | xargs wc -l

# Python test LOC
rg --files -g '*.py' | rg '(^|/)(test|tests)/|(_test\\.py$)' | xargs wc -l

# Rust app LOC (src only)
rg --files src -g '*.rs' | xargs wc -l

# Rust test LOC (tests/ directory + inline #[cfg(test)] blocks via grep count)
rg --files tests -g '*.rs' | xargs wc -l
rg -n '#\\[cfg\\(test\\)\\]' src

# Python test count
pytest --collect-only -q > artifacts/python-tests-collected.txt

# Rust test count
cargo test -- --list > artifacts/rust-tests-listed.txt
```

For each metric set, record:
- command run
- output artifact path
- repo commit hash used for measurement

### Phase B: Extract Playbook Improvements

After the port is complete, a second pass extracts actionable improvements from the
observations.

#### B.1 Triage observations

Categorize each observation:

| Category | Meaning | Action |
| --- | --- | --- |
| `FIX` | Playbook says something wrong (factual error, non-compiling code) | Must fix |
| `ADD` | Playbook is missing guidance that was needed | Add new content |
| `CLARIFY` | Playbook is ambiguous or misleading | Rewrite for clarity |
| `GENERALIZE` | Playbook is too flowmark-specific; needs broadening | Rewrite to be general |
| `VALIDATE` | Playbook guidance was confirmed correct | No change needed (positive signal) |

Use the [improvement triage template](case-study-improvement-triage-template.md) to
organize the triage.

#### B.2 Draft specific changes

For each `FIX`, `ADD`, `CLARIFY`, and `GENERALIZE` item, document:

- **Target file and section** in the playbook
- **Current text** (if modifying existing content)
- **Proposed new text** (the specific change)
- **Justification** citing the case study observation

#### B.3 Prioritize

Rank by two dimensions:

- **Impact:** How many future ports would benefit?
  (All / Most / Some / Niche)
- **Severity:** How likely to cause a failed port if unfixed?
  (High = agent gets stuck, Low = minor inconvenience)

Focus on high-impact, high-severity items first.

#### B.4 Create a plan spec

Write a plan spec (following the project’s spec format) with all proposed changes
organized by target file and priority.
This becomes the implementation plan for Phase C.

### Phase C: Integrate Improvements

Apply the approved changes to the playbook.

#### C.1 Human review

A human reviews the proposed changes from Phase B. This typically takes 5-15 minutes for
a single case study’s worth of improvements.
The reviewer:

- Approves, modifies, or rejects each proposed change
- Flags any changes that need more investigation
- Identifies any cross-cutting concerns (changes that affect multiple docs)

#### C.2 Agent implements

The agent implements all approved changes:

- Use beads (tbd) or issues to track each change
- Group changes by file to minimize merge conflicts
- Run validation checks:
  - link integrity
  - markdown syntax and formatting
  - code-block syntax sanity for shell/code snippets

#### C.2a Mandatory closure loop (required)

Each approved triage item is complete only when all of the following are recorded:

- Observation ID(s) linked to the change (`OBS-N`, `FIX-N`/`ADD-N`/etc.)
- Target doc(s) updated and merged
- Merge evidence recorded (PR/commit SHA)
- `_meta/playbook-improvement-log.md` entry added with date and outcome
- Any rejected/deferred item documented with rationale

Do not close a triage item without merge evidence and log entry.

#### C.2b Standard link-check workflow

Use one of the following before merging meta/playbook doc changes:

```bash
# Option A: lychee (preferred if available)
lychee README.md _meta/**/*.md playbooks/**/*.md guidelines/**/*.md case-studies/**/*.md

# Option B: repo script/check command (if configured)
make check-links
```

#### C.3 Update the case study index

- Add the new case study to the table in `README.md`
- Update any cross-references in the playbook and analysis docs
- Update the “validated by N case studies” count as the playbook matures

* * *

## Two Porting Modes (Avoid Confusion)

Use different entry points depending on whether this is a first port or an update to an
existing Rust port.

### Mode 1: Initial Port (new Rust implementation)

Start with:

- [`../playbooks/python-to-rust-playbook.md`](../playbooks/python-to-rust-playbook.md)
- [`../playbooks/port-checklist-initial-template.md`](../playbooks/port-checklist-initial-template.md)

### Mode 2: Auto-Sync Update (existing Rust port, new upstream Python release)

Start with:

- [`../playbooks/port-checklist-update-template.md`](../playbooks/port-checklist-update-template.md)
- [`auto-sync-agent-prompt-template.md`](../playbooks/auto-sync-agent-prompt-template.md)
- Phase 8 in the core playbook:
  [`../playbooks/python-to-rust-playbook.md#phase-8-ongoing-synchronization`](../playbooks/python-to-rust-playbook.md#phase-8-ongoing-synchronization)

If the work is an upstream release sync, do not begin from the initial-port checklist.
Begin from the update checklist and run a baseline-to-target diff first.

## Codified Auto-Sync Process

When upstream Python releases a new version, follow this sequence:

1. Identify baseline and target versions (currently ported Python version vs new
   release).
2. Diff upstream changes from baseline to target: modules/functions, tests,
   CLI/interface, dependencies.
3. Categorize changes: bug fix, new feature, test addition/update, refactor.
4. **Hard gate:** record baseline->target diff summary artifact before coding.
5. Execute the update checklist end-to-end.
6. Port changes with tests-first discipline.
7. Re-run parity and quality gates.
8. Update version correspondence and sync log.
9. Record observations on update-playbook guidance quality (`FIX`, `ADD`, `CLARIFY`,
   `GENERALIZE`, `VALIDATE`).

Use the
[auto-sync agent prompt template](../playbooks/auto-sync-agent-prompt-template.md) to
keep agent runs consistent and reproducible.

* * *

## Minimum Viable Case Study

Not every case study needs the full treatment.
At minimum, a useful case study must capture:

- [ ] Project name, size (LOC app + tests), and domain
- [ ] Dependency mapping table (Python → Rust)
- [ ] At least one observation per playbook phase (8 total)
- [ ] Final metrics summary (LOC, tests, time, ratio)
- [ ] List of playbook issues found (even if just “none for this phase”)

The full artifact set (analysis, library choices, decision log) adds significant value
but is optional for smaller projects.

## Selecting Good Candidate Projects

### Applicability by application type

When writing conclusions from a case study, state which app types the conclusion applies
to:

- CLI tools
- libraries
- HTTP services/clients
- data pipelines/batch processing
- async/event-driven apps

Avoid presenting CLI-specific conclusions as universal unless validated by at least one
non-CLI case study.

### Must-haves

- Open source (so the case study can be published)
- Has a test suite (the playbook’s approach is test-driven)
- Dependencies are installable (no proprietary or unavailable packages)
- Reasonably self-contained (not deeply embedded in a larger system)

### Nice-to-haves

- Active maintenance (so the sync phase can be evaluated)
- Multiple dependency types (not just stdlib)
- Some complexity in control flow or data structures
- Different domain from existing case studies

### Red flags (avoid)

- No tests at all (the playbook can’t be evaluated without them)
- Heavy C extension dependencies (complicates the port beyond playbook scope)
- Massive codebases (>10,000 lines for initial case studies; tackle these later)
- Abandoned projects with outdated dependencies

## How Many Case Studies?

The playbook likely stabilizes after 3-5 case studies covering different domains.
Diminishing returns set in once the major gaps are filled.
The signal to look for: consecutive case studies where most observations are `VALIDATE`
rather than `FIX` or `ADD`.

Suggested progression:

1. **CLI tool** (flowmark — done)
2. **HTTP client or API wrapper** (exercises async, reqwest, serde serialization)
3. **Data processing pipeline** (exercises iterators, file I/O, parallelism)
4. **Library with public API** (exercises trait design, API ergonomics, documentation)
5. **DevOps/infrastructure tool** (exercises system calls, process management,
   networking)
