# Flowmark Port: Analysis & Future Research

Analysis of the flowmark Python-to-Rust port looking for generalizable patterns, areas
for automation, and future research directions.

**Related:**
[Library Choices](flowmark-port-library-choices.md) |
[Decision Log](flowmark-port-decision-log.md) |
[Python-to-Rust Porting Guide](../../reference/python-to-rust-porting-guide.md)

**Last update:** 2026-02-08

## What Could Be Automated

### Fully Automatable (with good docs)

| Task | Automation Approach |
| --- | --- |
| Project setup | Template generation (Cargo.toml, directory structure, CI/CD) |
| Dependency mapping | Lookup table (Python pkg → Rust crate) |
| Module structure creation | Mirror Python's module tree in Rust |
| Function signature porting | Type mapping rules + code generation |
| Unit test porting | Mechanical translation with type mapping |
| CI/CD setup | Template GitHub Actions workflows |
| Formatting/linting config | Standard rustfmt.toml and clippy config |

### Partially Automatable (agent-guided)

| Task | What Can Be Automated | What Needs Judgment |
| --- | --- | --- |
| Library selection | Feature matrix, search | Final choice, risk assessment |
| Module porting | Initial translation | Ownership/lifetime design |
| Integration testing | Test framework setup | Test case design |
| Cross-validation | Script generation, diff analysis | Interpreting differences |
| Bug workarounds | Pattern recognition | Fix strategy selection |

### Requires Human Judgment

| Task | Why It Can't Be Automated |
| --- | --- |
| Accepting intentional divergences | Requires domain knowledge |
| Deciding to vendor/fork | Requires risk/effort assessment |
| Python bug discovery/filing | Requires understanding original intent |
| Performance optimization | Requires profiling and trade-off analysis |

## Patterns That Generalize

### 1. Research-Plan-Implement-Fix Pattern

Every successful port follows this pattern:
1. **Research** (30-60 min): Ecosystem survey, library evaluation
2. **Plan** (30-60 min): Feature matrix, architecture, risk assessment
3. **Implement** (2-4 hours): TDD, module-by-module, leaf-first
4. **Fix** (2-4 hours): Cross-validation, workarounds, documentation

The fix phase consistently takes 30-50% of total effort. This is not waste -- it's
where the port achieves production quality.

### 2. Tests as Specification

The Python test suite is the most important artifact for a port. Not the source code.
With 100% passing tests, the Rust implementation is correct by definition. Without
tests, you're guessing.

**Implication:** Before porting any Python app, invest in maximizing test coverage.
Every untested code path is a potential bug in the Rust version.

### 3. Post-Processing Pipeline

For any port that uses a library with behavioral differences, the post-processing
pattern works:

```
Input → Pre-process → Library → Post-process → Output
```

This is general-purpose. It works for Markdown parsers, JSON formatters, HTML renderers,
or any library where output needs adjustment.

### 4. Cross-Validation as Quality Gate

Running both implementations against the same inputs and diffing outputs is the most
effective quality assurance technique for ports. It catches issues that:
- Unit tests miss (complex input interactions)
- Code review misses (subtle behavioral differences)
- Static analysis can't detect (runtime output differences)

### 5. Workaround Tracking with XXX Comments

Marking every workaround with `XXX:` creates a searchable inventory of technical debt.
This pattern generalizes to any project where you're working around third-party library
behavior.

## How AI Agents Can Drive Porting

### The Ideal Agent-Driven Workflow

1. **Agent reads guidelines** (`tbd guidelines python-to-rust-porting-rules` etc.)
2. **Agent sets up project** using templates and checklists
3. **Agent evaluates libraries** using the evaluation framework
4. **Agent ports tests first** (mechanical translation with type mapping)
5. **Agent implements modules** to make tests pass
6. **Agent runs cross-validation** and categorizes differences
7. **Human reviews** agent's categorization of differences
8. **Agent implements workarounds** for approved categories
9. **Human decides** on unfixable differences (accept, fork, or switch)
10. **Agent writes documentation** for all decisions and workarounds

### What Agents Need

For this workflow to work, agents need:

1. **Comprehensive guidelines** (the docs we're creating in this effort)
2. **Evaluation framework** for library selection (with real-world test criteria)
3. **Type mapping tables** (Python → Rust, maintained and tested)
4. **Workaround pattern library** (common fixes for common library differences)
5. **Decision templates** (structured way to present choices to humans)
6. **Cross-validation tooling** (scripts that diff outputs automatically)

### What Agents Struggle With

Based on the flowmark experience:
- **Library bugs:** Agents can identify the bug but need human judgment on whether to
  vendor, fork, or work around.
- **Intentional divergences:** Deciding when Rust should differ from Python requires
  domain understanding.
- **Performance optimization:** Profiling and trade-off analysis require human judgment.
- **Architecture decisions:** When to use workspace vs single package, trait vs enum,
  etc.

## Handling Library Bugs: Generalizable Strategies

### Triage Framework

```
Bug discovered → Categorize → Choose strategy → Implement → Document
```

**Categories:**
1. **Cosmetic** -- output differs but is valid/acceptable
2. **Functional** -- output is incorrect but workaround exists
3. **Blocking** -- core feature broken, no workaround possible

**Strategies by category:**

| Category | Strategy 1 | Strategy 2 | Strategy 3 |
| --- | --- | --- | --- |
| Cosmetic | Accept and document | Post-process fix | -- |
| Functional | Post-process fix | Pre-process fix | Vendor/patch |
| Blocking | Switch library | Fork and fix | Implement from scratch |

## Handling Bugs in the Original App

### Discovery Pattern

Porting frequently reveals bugs in the original because:
- Test writing forces exact specification of behavior
- Cross-validation exposes inconsistencies
- The act of translation requires understanding every edge case

### Response Playbook

1. **Confirm it's a bug.** Run the Python code manually to verify.
2. **Write a failing test** in the Python repo.
3. **File a bug/PR** on the Python repo.
4. **Decide:** replicate the bug for parity, or fix it in the Rust version.
5. **If fixing:** document the intentional divergence and add a test proving Rust is
   correct.
6. **Track for sync.** When Python fixes the bug, remove the divergence note.

## Future Research Areas

### 1. Alternative Markdown Parsers

**markdown-rs** (a Rust reimplementation inspired by micromark, by the unified.js
author) deserves a thorough evaluation. It may provide better behavioral equivalence
with web-ecosystem Markdown tools because it shares lineage with remark/rehype.

**Research needed:**
- Does markdown-rs support GFM tables, footnotes, task lists?
- Does it provide AST access or just events?
- How does its output compare to marko (Python) on flowmark's test fixtures?
- Is the ecosystem mature enough for production use?

### 2. Automated Cross-Validation Tooling

Build a generic cross-validation tool that:
- Takes two CLI commands (Python and Rust)
- Runs both against a directory of inputs
- Reports differences with categorization hints
- Tracks difference counts over time (regression detection)

### 3. Type Mapping Verification

Build a tool or test suite that verifies the type mapping table is correct:
- For each Python→Rust type mapping, generate test cases
- Verify both implementations handle edge cases identically
- Catch mapping errors before they become test failures

### 4. Library Evaluation Test Suite

Create a standardized test suite for evaluating Rust libraries:
- For Markdown parsers: a set of inputs covering all CommonMark + GFM features
- Compare output against a reference implementation
- Score libraries on behavioral equivalence, not just spec compliance

### 5. Incremental Porting Support

Research how to support incremental porting where Python and Rust coexist:
- FFI bridge between Python and Rust (PyO3)
- Gradual module replacement
- Shared test fixtures that run against both implementations

### 6. Port Quality Metrics

Define quantitative metrics for port quality:
- Test parity percentage (passing Rust tests / total Python tests)
- Output equivalence score (matching bytes / total bytes across fixtures)
- Workaround count (lower is better)
- Performance multiplier (Rust speed / Python speed)

## Conclusions

The flowmark port demonstrates that **Python-to-Rust porting is highly automatable**
for CLI applications with good test suites. The key bottleneck is library behavioral
differences, which require human judgment for triage and strategy selection.

With the right documentation, guidelines, and tooling:
- Project setup: 100% automatable
- Module porting: 80-90% automatable
- Library workarounds: 50% automatable (pattern matching)
- Decision making: 0% automatable (human judgment required)

A significant reduction in human effort (10-20X today, potentially more with mature
tooling) is achievable for projects that:
1. Have comprehensive Python test coverage (>=90%)
2. Use libraries with well-matched Rust equivalents
3. Don't require complex concurrent/async behavior
4. Have well-documented requirements (tests as specification)

For projects like flowmark (a CLI text processor with good tests), a complete port can
go from days of effort to hours, with most human time spent on library evaluation and
difference triage rather than coding.
