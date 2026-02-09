# Feature: Meta-Playbook for Improving the Porting Playbook

**Date:** 2026-02-09 (last updated 2026-02-09)

**Author:** Senior Engineering Review (automated)

**Status:** Draft

## Overview

Create a "meta-playbook" — a systematic process for improving the Rust Porting Playbook
itself by conducting real-world case studies. An agent follows the playbook end-to-end
with a new Python codebase, documents what worked and what didn't, and then those
learnings are integrated back into the playbook. This creates a feedback loop where
each case study makes the playbook more accurate and complete.

## Goals

- Define a repeatable process for conducting a case study port using the playbook
- Define how to capture structured learnings during the port
- Define how to integrate those learnings back into the playbook
- Make the whole process agent-drivable with minimal human intervention
- Add a "Improving This Playbook" section to the main README

## Non-Goals

- Actually conducting a new case study (this spec plans the meta-process only)
- Restructuring the existing playbook (only additive improvements from learnings)
- Automating the integration step fully (human review is required for playbook changes)

## Background

The playbook was built primarily from the flowmark case study. While flowmark is a good
test case (text-processing CLI, ~2,000 lines, marko→comrak), it represents a single data
point. The playbook will improve significantly with additional case studies covering:

- Different domains (web services, data processing, ML tooling, DevOps)
- Different sizes (100-line scripts to 10,000+ line applications)
- Different dependency profiles (heavy I/O, database, HTTP, async)
- Different library mapping challenges (good equivalents vs no equivalents)

Each case study is an opportunity to discover:
- Guidelines that are wrong or misleading in practice
- Missing guidance that agents need but the playbook doesn't provide
- Patterns that generalize beyond flowmark
- Patterns that were flowmark-specific and shouldn't be presented as universal

## Design

### The Meta-Playbook: Three Phases

The meta-playbook is a document (`meta-improving-this-playbook.md`) in the `reference/`
directory that describes three phases:

#### Phase A: Conduct a Case Study Port

An agent follows the playbook to port a real Python project to Rust:

1. **Setup:** Agent reads all playbook guidelines, sets up the project per
   `rust-project-setup.md`, and creates a case study directory
   `case-studies/<project-name>/`.

2. **Execute the 8-phase methodology** from `python-to-rust-playbook.md`:
   research, plan, setup, map, port, fix, document, validate.

3. **Record structured observations** as the port proceeds. For each phase, the agent
   captures in a `<project>-port-observations.md` file:
   - What the playbook said to do
   - What actually happened
   - Where the playbook was helpful (with specific doc + section)
   - Where the playbook was wrong or misleading (with specific doc + section + what
     should change)
   - Where the playbook was silent but guidance was needed (what to add and where)
   - Time spent and difficulty level for this phase

4. **Produce standard case study artifacts** (mirroring flowmark's structure):
   - `<project>-port-analysis.md` — what could be automated, what required judgment
   - `<project>-port-library-choices.md` — library evaluation and selection
   - `<project>-port-decision-log.md` — all decisions with rationale and alternatives
   - `<project>-port-observations.md` — the structured playbook feedback (new)

5. **Produce a final metrics summary:**
   - Python LOC (app + tests, counted from actual repo)
   - Rust LOC (app + tests, counted from actual repo)
   - Dependency LOC comparison
   - Test count and breakdown
   - Time per phase
   - Number of issues where playbook was wrong/missing/helpful

#### Phase B: Extract Playbook Improvements

After the case study is complete, a second pass extracts actionable improvements:

1. **Triage observations** from the case study into categories:
   - `FIX` — playbook says something wrong (factual error, non-compiling code, etc.)
   - `ADD` — playbook is missing guidance that was needed
   - `CLARIFY` — playbook is ambiguous or misleading
   - `GENERALIZE` — playbook is too flowmark-specific; needs to be broadened
   - `VALIDATE` — playbook guidance was confirmed correct (positive signal)

2. **Draft specific changes** for each `FIX`, `ADD`, `CLARIFY`, and `GENERALIZE` item:
   - Target file and section
   - Current text (if modifying)
   - Proposed new text
   - Justification from the case study

3. **Prioritize** by impact (how many future ports would benefit) and severity (how
   likely to cause a failed port if unfixed).

4. **Create a plan spec** (like `plan-2026-02-08-playbook-review-fixes.md`) with all
   changes organized by file and priority.

#### Phase C: Integrate Improvements

Apply the changes to the playbook:

1. **Human reviews** the proposed changes (5-15 minutes for a typical case study's worth
   of improvements).

2. **Agent implements** approved changes, using beads for tracking.

3. **Update the case study index** in the README and any cross-references.

4. **Update the "validated by N case studies" count** as the playbook matures.

### Observation Template

The structured observation format for Phase A step 3:

```markdown
## Phase N: [Phase Name]

### What the playbook said
> [Quote from specific playbook doc, section, and line]

### What actually happened
[Description of actual experience]

### Playbook assessment
- [ ] Helpful — guidance was accurate and useful
- [ ] Wrong — guidance was factually incorrect: [what should change]
- [ ] Misleading — guidance was technically correct but led us astray: [why]
- [ ] Missing — no guidance existed for this situation: [what to add]
- [ ] Too specific — guidance was flowmark-specific, not general: [how to generalize]

### Suggested playbook change
**File:** `guidelines/xyz.md` section "ABC"
**Change:** [Specific text change or addition]
```

### README Section

Add to `README.md`:

```markdown
## Improving This Playbook

This playbook improves through real-world case studies. Each port conducted using the
playbook generates structured feedback that is integrated back.

See [`reference/meta-improving-this-playbook.md`](reference/meta-improving-this-playbook.md)
for the full process.

### How to contribute a case study

1. Pick a Python project to port (ideally with good test coverage)
2. Follow the playbook end-to-end, recording observations
3. Submit a PR with your case study in `case-studies/<project-name>/`
4. The observations will be triaged and integrated into the playbook

### Case studies completed

| Project | Size | Domain | Key learnings |
| --- | --- | --- | --- |
| [flowmark](case-studies/flowmark/) | ~2,000 lines | Markdown formatting CLI | Parser library differences dominate effort |
```

## Implementation Plan

### Phase 1: Create the meta-playbook document and README section

- [ ] Create `reference/meta-improving-this-playbook.md` with the full three-phase
  process (Phase A: Conduct, Phase B: Extract, Phase C: Integrate)
- [ ] Include the observation template
- [ ] Include a checklist for "minimum viable case study" (what must be captured)
- [ ] Include guidance on selecting good candidate projects for case studies
- [ ] Add "Improving This Playbook" section to `README.md` with case study table
- [ ] Add cross-references from the playbook overview and analysis docs

### Phase 2: Create supporting templates

- [ ] Create `reference/case-study-observations-template.md` — the observation recording
  template agents fill out during a port
- [ ] Create `reference/case-study-improvement-triage-template.md` — the template for
  Phase B triage of observations into playbook changes
- [ ] Update `reference/port-checklist-initial-template.md` to include an observation
  recording step in each phase

## Testing Strategy

The meta-playbook is validated by using it:
1. Conduct one new case study (e.g., a small HTTP client or data pipeline) following the
   meta-playbook process
2. Verify the observation template captures all relevant feedback
3. Verify the Phase B triage process produces actionable playbook changes
4. Verify the Phase C integration is straightforward

## Open Questions

- What is the minimum project size that produces useful case study data? (Likely 500+
  lines Python with tests)
- Should case study observations be stored as tbd beads, or as markdown files?
  (Recommendation: markdown files in the case study directory, with a summary bead)
- How many case studies are needed before the playbook stabilizes? (Hypothesis: 3-5
  covering different domains)
- Should the meta-playbook include a "quick mode" for small projects (<500 lines) that
  skips some documentation steps?

## References

- Current playbook: `reference/python-to-rust-playbook.md`
- Existing case study: `case-studies/flowmark/`
- Playbook review spec: `docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md`
