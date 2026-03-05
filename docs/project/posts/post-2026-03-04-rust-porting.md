# A Self-Improving Methodology for Porting Python to Rust

After experimenting with this over the past few weeks, I’m excited to share what feels
for me like a milestone in agentic coding: automation of 100% agent-written,
high-quality porting of complex Python codebases to Rust.

I just finished a third port of a reasonably complex tool, writing zero code and zero
specs myself. For many projects, I think this is now fully achievable.
And critically, the testing is extensive and transparent, so it helps give you
confidence that the port is high fidelity.

Of course I should mention caveats:

- The source project does not need to have great test coverage initially, but it should
  be *amenable* to testing via “golden testing” (more on this below).

- It works best if there are roughly equivalent libraries in both ecosystems.
  Most common Python libraries (CLI parsing, HTTP, regex, serialization, async) map
  cleanly to mature Rust crates.
  But some areas of deep learning have notable gaps, e.g. Rust has PyTorch bindings
  (tch-rs) and native frameworks like Burn, but the surrounding ecosystem still is not
  fully covered in Rust.

- Although I’ve used Python for a very long time, I’m quite new to Rust so would
  appreciate critique from Rust experts on the results here.

Anyone can ask a coding agent, “please port this to Rust.”
Easy parts will port quickly—then you hit harder parts.
How far you get depends on necessary elements and tools being in place.

I’ll walk through what I’ve learned and how it all works here.
I’ve open sourced the **rust-porting-playbook** and a real-life case study,
**flowmark-rs**, a port of the Python **flowmark** Markdown auto-formatter.
(Links to all repos in replies.)

A few hours of automated porting now gives a usable, published tool with exact feature
parity and ~50x the speed of the Python implementation.

Even better, any changes made to the Python version can now flow downstream to Rust with
almost no human effort.

Markdown parsing is a nice use case, because it is filled with tiny corner cases and
parser bugs.
I tried this process a few months ago with the same project, but there was a
lot of friction, especially when it came to managing the many subtle differences in
libraries, especially Markdown parsing in Python vs Rust.
But now, with the techniques I describe here plus Opus 4.6 and/or GPT-5.3 Codex, I’ve
found automated porting is now achievable for this and other real tools.
The era of auto-ported multi-language software is here!

The non-obvious parts of this playbook are:

1. **Knowledge curation:** Assembling extensive, reusable, reliable background knowledge
   on best practices and pitfalls related to source and target languages, libraries, and
   tooling. Can’t an agent figure these things out itself?
   Of course, sometimes.
   But having pre-curated knowledge significantly raises the quality, reliability, and
   speed of porting. The rust-porting-playbook has ~200 pages of Rust best practices
   across its `guidelines/`, `references/`, `playbooks/`, and `case-studies/`
   directories.

2. **Golden testing:** Golden testing is an alternative to classic unit and integration
   testing that offers *transparency* and *readability* to both agents and humans.
   It’s incredibly powerful but often neglected.
   It describes behavior clearly like a spec but is executable as a test.
   I’ve built a new agent-friendly CLI tool for this, **tryscript**, that lets agents
   write golden tests in plain Markdown for CLI-based apps.
   (Also newly released open source.
   Link below.)

3. **Test backfilling:** Assuming a given Python project has good tests is not
   realistic. Very few projects have truly thorough test coverage.
   But once you have a golden testing methodology, it’s straightforward for an agent to
   backfill extensive golden tests and iterate until coverage is thorough.
   This could uncover bugs!

4. **Test mapping:** Meta-tests that systematically map and automate parity checks
   across the two implementations.
   The beauty of golden testing is that the tests across the ports are actually the
   same! So CLI tests written in tryscript’s Markdown format can be reused between Python
   and Rust.

5. **Codified principles:** Without explicit engineering principles in context, agents
   drift: silently reducing scope, skipping hard bugs, or “moving the goalposts” on
   tests. A principles doc fixes this.

6. **Task management:** Agents struggle to manage hundreds of sub-tasks on their own.
   Git-native issue tracking (beads) helps enormously (more below).

7. **Meta-process improvement:** The playbook improves itself through a structured case
   study feedback loop (more below).

This is a lot, but the key point is, with sufficient directions in the playbook, *the
whole process itself can be automated*.

I’ve done this for Python to Rust but the playbook could easily be extended to other
source languages; I’d love to see someone try it for TypeScript.

I’ll go through each of these in a bit more detail below.
You can then try these techniques in your own way or use the whole playbook.

But first, let’s look at the results from the example project.

## Results of Flowmark Rust Port

Everything below was written by Claude Opus 4.6, with a final pass on PRs by GPT-5.3
Codex Extra High.

![Release Status](article-2026-03-04-rust-porting.assets/release-status.png)

![Porting Methodology](article-2026-03-04-rust-porting.assets/porting-methodology.png)

![Test Results](article-2026-03-04-rust-porting.assets/test-results.png)

Next I’ll walk through each of the techniques in more detail.

Keep in mind, *all* of this is explained to the agent via the playbook docs!
My job was not to tell it to do each of these things step by step, but to make sure the
playbook gives it the right structure to use each of these techniques itself.

## Knowledge Curation

Agents can figure out many things on their own, but pre-curated knowledge dramatically
reduces wasted time and context, like slow web searches and common confusions.
Agents read these docs before and during the port:

**Guidelines** are compact rules and methodology docs:

- **porting-principles-and-antipatterns.md:** The “north star” rules for porting, saying
  we demand *exact parity* in behavior and *forbid* things like changing scope or
  skipping tests.

- **test-coverage-for-porting.md:** How to build comprehensive golden test coverage
  *before* porting, so the Rust implementation has a precise spec to match against.

- **python-to-rust-porting-rules.md:** Porting methodology: principles, workflow,
  pitfalls, and acceptance criteria.

**References** are lookup tables, checklists, and pattern catalogs:

- **python-to-rust-mapping-reference.md:** Exhaustive lookup table mapping Python
  constructs to Rust equivalents, organized by category (types, collections, functions,
  error handling, async, project setup).

- **rust-cli-app-patterns.md:** Production patterns for clap, tracing, error handling,
  and cross-platform I/O, cross-referenced against real projects (ripgrep, bat, fd).

- **cross-language-test-mapping.md:** How to maintain traceable test coverage between
  Python and Rust with CI enforcement to prevent coverage drift.

- **rust-cli-best-practices.md:** Multi-channel distribution (crates.io, PyPI via
  maturin, Homebrew tap, GitHub Releases).

**Playbooks** are step-by-step process guides:

- **python-to-rust-playbook.md:** The main porting process, end to end.
  A key insight described here: ~50% of effort goes to library workarounds and
  cross-validation, not the initial implementation.

## Golden Testing

**Golden testing** is in my opinion one of the most-neglected yet powerful types of
testing. And it’s now even more relevant for agentic coding.
It might be because the idea is simply to capture the behavior of a system, including
actual inputs, outputs, and intermediate states, serialize it to a readable file, then
use it as a reference for specifying behavior, reviewing changes, and detecting
regressions.

It has sometimes been called “snapshot testing” or “characterization testing” but I find
“golden testing” is more descriptive: you capture a wide range of meaningful detail on a
golden session, not just specific inputs and outputs.
This gives situational awareness around code changes without the maintenance burden of
writing unit or integration tests specifically targeting each line or function.

Unit, integration, and even end-to-end tests tend to verify *narrow expectations*. In
contrast, golden tests *contextually reveal broad state*, confirming expected results
while simultaneously making unexpected changes obvious.
When you modify one thing and something else unexpectedly changes, a diff on what
changed in the captured session reveals it immediately in a contextual,
easy-to-interpret way.

Golden testing can be done for many kinds of code and even UIs and web applications, if
you define an appropriate clean and diff-able serialization for sessions.
But for CLI tools, it’s especially easy to do!

I built **tryscript** specifically for CLI golden testing.
It runs shell commands from Markdown files, captures output in the Markdown document,
and diffs subsequent runs against expected results:

````markdown
### Wrap long lines

Let's see how narrow wrap widths work!

```console
$ echo "This is a paragraph that has been wrapped so that it reads well in a terminal or diff view." | flowmark --width 40 -
This is a paragraph that has been
wrapped so that it reads well in a
terminal or diff view.
? 0
```
````

Each test block has a heading, a command, the expected output, and the exit code
(`? 0`). Tryscript supports regex patterns for normalizing timestamps and IDs
(`[PATTERN]`), line elisions (`...` for zero or more lines, `[..]` for any text on a
single line), sandbox isolation, setup blocks, and environment variables, all in plain
Markdown that humans and agents can both understand readily.

This design is ideal for agent testing and porting:

1. **Tests are the spec.** You can have agents write specs and review the actual
   behavior exhaustively.

2. **Tests show behavior, not intent.** Unit tests usually verify a developer (or
   agent’s) expectations.
   Golden tests capture the actual input and output.

3. **Shared tests across languages.** The tests are simply tryscript-format Markdown so
   are the same for both source and target language.

4. **Agents are great at creating and understanding golden tests.** Writing golden tests
   is mechanical: an agent runs the test in “update” mode, which records the outputs,
   reviews and checks in the result.
   An agent can generate hundreds of golden tests, review them, commit.

5. **Humans can read golden tests.** Reviewing a golden test is much easier than a long
   code file with integration tests.
   The behavior is shown in context of a real run.

In the Flowmark case study, golden testing caught many bugs that unit tests would have
missed, such as mode-specific parity issues and systematic differences between the
Python parser (marko) and Rust parser (comrak).

## Test Backfilling

Most real-world projects don’t have thorough test coverage.
But with a golden testing framework like tryscript, backfilling coverage is
straightforward: an agent runs the tool against a wide variety of inputs, records the
outputs, and reviews and commits the results.
This can be done quickly and systematically before porting begins, giving the Rust
implementation a precise spec to match against.
The playbook’s **python-to-rust-test-coverage-playbook.md** documents this process in
detail.

## Test Mapping

Test count alone is misleading.
A Rust port can have 400+ tests while still missing coverage for critical Python
behaviors.

Test mapping solves this by creating a formal, traceable link from every Python test to
its Rust equivalent(s). In the playbook, this is a YAML manifest:

```yaml
- python_file: tests/test_alerts.py
  python_function: test_alert_after_heading
  status: mapped
  rust_file: tests/test_alerts.rs
  rust_function: test_alert_after_heading
```

Every Python test gets a status: `mapped` (has a Rust equivalent), `partial` (one Python
test split into multiple Rust tests), `excluded` (intentionally not ported, with a
documented reason), or `missing` (not yet ported).

The process has three parts:

1. **Discovery:** Auto-scan Python tests (via AST parsing) and Rust tests (via
   `cargo test --list`) to generate inventories of all tests on both sides.

2. **Mapping:** Link each Python test to its Rust counterpart(s). If a single Python
   test with many assertions becomes multiple focused Rust tests, the mapping tracks all
   of them explicitly.

3. **Meta-test in CI:** A validation check runs on every push, confirming the mapping is
   complete: no unmapped Python tests, no dangling references.
   This prevents silent coverage drift as the port evolves.

Golden tests (tryscript files) are shared directly between the two implementations, so
they don’t need additional mapping.
The mapping tracks unit and integration tests, where the Python and Rust implementations
naturally diverge in structure.

In the flowmark port, this produced 292 Python tests mapped to 442 Rust tests, with 100%
mapping coverage enforced in CI.

## Codified Principles

A pitfall I found when trying earlier versions of the porting playbook was that the
tests would be correct, and the mapping correct, but then during the implementation
process, Claude Opus would “move the goalposts.”
It might change the scope of the porting spec, state something was impossible, or
quietly skip some tests.

The fix was a short document codifying **engineering principles and anti-patterns** for
the porting process.
Having these explicitly in the agent’s context meant it would constantly remember its
job was **exact parity**, not “close enough.”

Putting principles and anti-patterns in the same doc works well: the principles say what
to do, and the anti-patterns give concrete examples of what *not* to do.
Agents respond well to both positive and negative examples: just saying “ensure exact
parity” is less effective than also specifying “do NOT disable a failing test.”
These are in **porting-principles-and-antipatterns.md** in the playbook repo.

## Task Management

Agents can handle a handful of ad-hoc tasks, but longer spec-driven development and
porting requires tracking many steps.
Usual to-do lists are good for a few tasks but not for dozens or more.
Agents lose track, repeat work, or silently drop tasks between sessions.

Agent-friendly issue tracking solves this.
**Beads**, created by Steve Yegge, are a remarkably effective way to scale an agent’s
capacity from ~5-10 ad-hoc tasks to hundreds of structured, trackable issues that
persist across sessions in Git.

I recommend **tbd** (“To Be Done”), my own TypeScript port of Beads that I find is more
reliable.
It uses simple Markdown for each bead, which avoids many of the merge conflicts
and complexity of Beads’ JSONL format.
It also has optional other CLI commands for spec-driven planning (shortcuts and
templates for writing plans), knowledge injection (additional engineering guidelines
agents can load on demand), and shortcuts (reusable instructions for code review, PR
creation, commits).

With beads, you can leave an agent running for hours.
Both Beads and tbd are open source (links below).

## Meta-Process Improvement

Every port conducted using the playbook is a **case study**, and every case study
generates observations that flow back into the playbook.

This is documented in **meta-improving-this-playbook.md** in the `_meta/` directory.

As the final phase of the playbook, an agent reviews the case study and triages
observations into categories: `FIX` (factual error), `ADD` (missing guidance), `CLARIFY`
(ambiguous), `GENERALIZE` (too project-specific), or `VALIDATE` (confirmed correct).

There’s a long way to go to make this work for more complex applications.
But I’ve gone through it about 3 times and it’s improving.

* * *

This is all an evolving process.
Even if you’re not porting a whole program, I hope some of these techniques are useful.
Let me know what you think and what works for you!

Josh
