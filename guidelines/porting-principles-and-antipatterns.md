---
title: Porting Principles and Anti-Patterns
description: Principles for agent-driven porting and the anti-patterns that violate them
---
# Porting Principles and Anti-Patterns

Non-negotiable principles for agent-driven Python-to-Rust porting, with real-world
anti-patterns observed during porting work.
These principles override convenience, speed, and local judgment.
There are no exceptions.

See also: [Python-to-Rust Porting Rules](guidelines/python-to-rust-porting-rules.md) and
[Test Coverage for Porting](guidelines/test-coverage-for-porting.md) (for implementation
specifics: fixture organization, golden test patterns, coverage tools, and
cross-validation mechanics).

## Key Principles

Every principle below was learned from an actual mistake during agent-driven porting.
None are hypothetical.

1. **Parity must be defined crisply and never redefined without explicit user
   approval.** The parity definition is the contract for the entire port.
   An agent may never narrow, reinterpret, or implicitly change what parity means.
   If the scope must change, the agent must escalate and get explicit approval.

2. **Agents must actively pursue parity, not passively document gaps.** Every discovered
   parity gap is a severe blocker.
   The agent’s job is to fix it or ensure it fails loudly in CI — never to note it in
   passive language and move on.
   Every known discrepancy must have a failing test.

3. **Tests must always run in CI.** A test that exists but doesn’t run in CI is worse
   than no test. Wiring into CI is part of writing the test, not a follow-up task.

4. **Tests must never hide failures.** Any code that converts a failure into a silent
   pass — returning early, truncating output, encoding wrong expected values — is a bug
   in the test. It is always better to commit a failing test than a test that hides
   errors.

5. **Fix the process, not the test.** If a failing test blocks your workflow, fix the
   workflow. Never disable, skip, or weaken a test to unblock development.

6. **Environment dependencies must be explicit and enforced.** If a test needs a tool,
   CI must provide it. Never silently skip when a dependency is missing.

7. **Ignored tests are only allowed for work that’s been explicitly deferred by the
   user.** Every `#[ignore]` needs a reason string and a tracking issue.
   Ignored tests are debt.

8. **Disparities must be tested before they are fixed, and investigated
   systematically.** When a disparity is found, write a discriminating test before
   attempting any fix. If no equivalent test exists in the original, add one there first.
   Then investigate the class of behavior the disparity represents — one discovered gap
   usually means more are hiding nearby.

* * *

## Illustrations

The sections below give detailed examples of how each principle has been violated in
practice, why agents make these mistakes, and what to do instead.

* * *

## Principle 1: Parity Must Be Defined Crisply and Never Redefined Without Explicit Approval

**The definition of “parity” is the contract for the entire porting effort.
An agent may never narrow, reinterpret, or implicitly change what parity means.**

Parity is the single most important concept in a port.
If the definition is ambiguous, it creates room for misunderstandings that compound
across every agent session.
If the definition is changed without explicit user approval, the entire porting effort
drifts away from its objective.

The parity definition must be:

1. **Crisp and unambiguous.** Not “the core formatting should match” but “the Rust
   binary is a drop-in replacement for the Python binary at the CLI level — identical
   flags, identical output, identical file discovery, identical error behavior.”

2. **Explicit about tolerated variations.** If certain behaviors are allowed to differ
   (e.g., auto-generated `--help` layout differences between argparse and clap), these
   must be enumerated. Everything not listed as a tolerated variation is required to be
   identical.

3. **Immutable without user approval.** If an agent encounters an obstacle that seems to
   require narrowing the parity definition, the agent must escalate to the user.
   The agent does not have authority to decide that some category of behavior “doesn’t
   need to match.”

### Anti-Pattern: Implicit Scope Reduction

**What happens:** A spec says “exact parity.”
An agent refines the spec and quietly scopes it down — defining “parity” as covering
only core formatting but excluding CLI flags, file discovery, error messages, or skill
installation. Future agents inherit this narrowed definition and never question it.

**Example (real):** A spec titled “Exact Cross-Language Parity” was refined by an agent
to cover only content formatting.
CLI flags, file discovery, config loading, and the skill system were excluded from the
parity definition. The user had to intervene to restore the original intent: the Rust
binary must be a complete drop-in replacement at the CLI level.

**Why agents do this:** The full scope feels large and risky.
Narrowing the definition makes the task feel more achievable and lets the agent report
progress sooner. The agent rationalizes that the excluded areas “can be done later” or
“aren’t critical.”

**The fix:** The parity definition is set by the user, not the agent.
If the agent believes the scope should be narrowed, it must propose the change
explicitly and get approval.
Silently redefining scope in a spec document is not acceptable — it poisons every
downstream decision.

When writing or refining a parity spec:
- Start from the broadest interpretation of “drop-in replacement.”
- Enumerate every dimension of behavior (output, flags, errors, file discovery, config,
  informational messages).
- Only exclude something if the user explicitly approves the exclusion.
- Document tolerated variations as a short, closed list — not an open-ended “and similar
  differences.”

### Anti-Pattern: Improving on the Original Without Approval

**What happens:** An agent discovers the Python implementation has a bug or suboptimal
behavior. Instead of matching it exactly, the agent “improves” the Rust port to do the
right thing. The port now diverges from the original intentionally, but with no test
comparing the two, the divergence is invisible.

**Why agents do this:** Matching a known bug feels wrong.
The correct behavior seems obvious, and the agent reasons the user would want the
improvement.

**The fix:** Parity means parity, including bugs.
The default is to match the original's behavior exactly.

1. Match the buggy behavior in the port.
2. Write a test that captures the (buggy) behavior and passes against both
   implementations.
3. Note the bug in the spec or as a tracked issue — agents should absolutely document
   bugs they discover in the original. But documenting is not fixing. The bug is a
   separate issue to escalate as unresolved at the end of the current development
   cycle, not a reason to diverge from the original now.
4. If the user explicitly approves fixing the bug during the current cycle, fix it in
   both implementations and add the intentional divergence to the tolerated variations
   list.

* * *

## Principle 2: Agents Must Actively Pursue Parity, Not Passively Document Gaps

**Every discovered parity gap is a severe blocker.
The agent’s most important job is achieving parity.
Passive documentation of gaps is a failure of that job.**

When an agent discovers that the Rust port produces different output than the Python
original, this is not a footnote.
It is a fundamental failure of the porting objective.
The agent must treat every parity gap with urgency: fix it, or if it cannot be fixed
immediately, ensure it is a visible, tracked, CI-failing blocker.

The onus is on the agent to seek out discrepancies, correct them, and track them.
The onus is never on the user to follow up on gaps the agent has passively noted.

### Anti-Pattern: Passive Gap Acknowledgment

**What happens:** An agent discovers parity differences — reference links are inlined
differently, escape handling diverges, file discovery produces different results.
Instead of fixing these or surfacing them as blocking failures, the agent writes a PR
description noting that “these behavioral differences may warrant separate tracking” or
“this difference is worth documenting.”
CI is green. The differences are buried in prose.

**Example (real):** A PR included this language:

> Parity gap: reference links & footnotes — uses `head -20` to avoid output differences
> where Rust inlines reference links differently.
> These are real Rust-Python differences that may warrant separate tracking.
> 
> Parity gap: escape handling — `\"` is handled differently.
> This is a behavioral difference worth documenting.

Investigation revealed why CI was green despite these gaps: tests had been **massaged to
hide the differences**. One test used `head -20` to truncate output before the
divergence appeared.
Another encoded the Rust behavior as the expected output instead of the Python behavior.
A third used `basename | sort` and `grep -c` to mask path differences.

Every one of these gaps should have been a failing test.
Instead, the tests were shaped to pass, and the gaps were mentioned in passive language
that put the burden on the user to notice and act.

**Why agents do this:** Fixing parity gaps is hard.
Noting them feels like transparency.
The agent wants to ship a green PR and move forward, treating the gaps as follow-up
work.

**The fix:**

1. **Every known parity discrepancy must have a failing test.** It is always better to
   commit a failing test than to have a test that hides the error.
   A red CI for a real gap is correct behavior.
   A green CI that masks a gap is a lie.

2. **Never massage a test to pass.** If the output differs, the expected output must
   reflect the Python behavior, not the Rust behavior.
   If the test fails, that failure is the correct result.
   Do not truncate output (`head -20`), strip paths (`basename`), or weaken assertions
   to make a test pass.

3. **Gaps that cannot be immediately fixed must be severe blockers.** Create a
   high-priority tracking issue.
   The issue title should make the severity clear: “PARITY FAILURE: reference links
   inlined differently than Python.”
   This is not a nice-to-have.
   It means the porting effort is not achieving its objective.

4. **Report gaps prominently, not passively.** In PR descriptions, commit messages, and
   status reports, parity gaps go at the top, not buried in a footnote.
   Use language that conveys severity: “This PR introduces a failing test for a known
   parity gap in escape handling” — not “this difference is worth documenting.”

### Anti-Pattern: Stale Ignores and Asking Permission for the Obvious

**What happens:** An agent fixes the underlying bugs that caused parity failures, but
leaves the corresponding tests `#[ignore]`d. The agent reports “364 tests pass (2
ignored parity-gap)” as if this is a healthy state.
When the user notices and asks about the ignored tests, the agent responds: “Those may
now be stale. Want me to un-ignore them and see if they pass?”

This is a triple violation:

1. **The tests should never have been ignored.** They should have been failing visibly,
   not silenced.
2. **After fixing the bugs, the agent didn’t re-enable the tests.** The agent’s own
   fixes made the ignores stale, but the agent didn’t close the loop.
3. **The agent asked permission to do the obviously correct thing.** Re-enabling tests
   after fixing the bugs they test is not a judgment call that requires user input.
   It is the baseline expectation.
   Asking “want me to un-ignore them?”
   shifts the burden to the user to drive the porting effort forward.

**The fix:** After fixing a bug, immediately un-ignore every test that was waiting on
that fix and run the full suite.
If the tests pass, report the progress.
If they fail for a new reason, report the new failure prominently.
Never leave stale `#[ignore]` annotations.
Do NOT ask for permission to add better coverage or enable a test: enabling tests and
pursuing parity is the agent’s primary job.

### Anti-Pattern: Dismissing Failures as “Pre-Existing” or “Out of Scope”

**What happens:** An agent encounters a failing test or parity gap that wasn’t
introduced by the agent’s current task.
Instead of fixing it or ensuring it’s tracked with a visible failure, the agent
dismisses it as “a pre-existing failure” or “outside the scope of this work” and moves
on. The failure remains untracked, unfixed, and invisible.

**Example (real):** An agent working on formatting parity discovers that file discovery
produces different results than the Python implementation.
The agent notes “this appears to be a pre-existing issue unrelated to the current
formatting work” and proceeds without creating a failing test, filing an issue, or
escalating. The gap persists silently across multiple sessions because every agent
considers it someone else’s problem.

**Why agents do this:** Agents are given specific tasks and naturally scope their
responsibility to that task.
Addressing “unrelated” failures feels like scope creep.
The agent reasons that fixing pre-existing issues would delay the assigned work and that
someone else will handle it.
This reasoning is reinforced by how agents are typically evaluated — on the specific
task they were given, not on the overall health of the port.

**The fix:**

1. **There is no “out of scope” for parity failures.** The agent’s job is to achieve
   parity. Any failure that affects parity is the agent’s concern, regardless of when it
   was introduced or which task the agent was assigned.

2. **Pre-existing failures still need failing tests.** If the agent discovers a gap they
   can’t fix immediately, they must ensure there’s a failing test that makes the gap
   visible in CI. “It was already broken” is not an excuse for leaving it silently
   broken.

3. **Create a tracked issue with clear severity.** Even if the agent can’t fix the gap
   in this session, it must be tracked as a blocker with a failing test — not dismissed.

4. **Never use “pre-existing” or “out of scope” to justify ignoring a failure.** The
   correct response is: “I found an additional parity gap.
   I’ve added a failing test and created issue #NNN to track it.
   Here’s what I observed: ...”

The distinction matters: an agent who says “this is pre-existing, not my problem” is
abandoning the porting objective.
An agent who says “this is pre-existing, I’ve added a failing test and a tracking issue
so it can’t be missed” is doing the job correctly.

* * *

## Principle 3: Tests Must Always Run in CI

**Every test must run as part of the standard CI pipeline, by default, on every
commit.**

Tests that exist but don’t run are worse than no tests at all — they create a false
sense of coverage. If you write a test, it must be wired into the build system and CI
configuration immediately.
Not “later”, not “in a follow-up PR”, not “once the infrastructure is ready.”

### Anti-Pattern: Orphaned Tests

**What happens:** An agent writes a new test file (e.g., a golden test suite) but does
not add it to the CI workflow, the test runner configuration, or the build system’s test
discovery. The tests exist on disk but never execute in CI.

**Why agents do this:** The agent focuses on writing the test code and considers the
task “done” when the file compiles.
Wiring tests into CI is a separate concern that falls outside the agent’s immediate
scope.

**The fix:** Treat “test runs in CI” as the definition of done for any test.
A test that isn’t in CI doesn’t exist.
After writing any test, verify it runs with the project’s standard test command (e.g.,
`cargo test --all-features`) and confirm it appears in CI output.

* * *

## Principle 4: Tests Must Never Hide Failures

**A test that silently passes when it should fail is a bug in the test.**

The purpose of a test is to make failure conspicuous.
Any code that converts a test failure into a silent pass — catching exceptions,
returning early on error, printing a message instead of failing, truncating output to
avoid a diff, encoding the wrong expected value — defeats the entire purpose of testing.

It is **always** better to have a failing test than a test that is patched to hide
errors.

### Anti-Pattern: “Graceful” Degradation in Tests

**What happens:** An agent writes a test that depends on an external tool (e.g., `npx`
for tryscript). Instead of failing when the tool is missing, the test prints “npx not
available” and returns `Ok(())`. The agent describes this as “graceful skip when npx
isn’t available.”

**Example (real):**

```rust
// BAD: This hides a real failure
fn run_tryscript_test(script: &str) -> Result<()> {
    if !command_exists("npx") {
        println!("npx not available, skipping");
        return Ok(()); // Silent pass — this is a lie
    }
    // ... actual test logic
}
```

**Why agents do this:** The agent encounters an environment where the dependency is
missing and wants the test suite to pass.
“Graceful degradation” sounds like good engineering.
In production code, it often is.
In test code, it is the opposite — it masks the problem.

**The fix:** If a dependency is required, the test must fail when it’s missing.
If the dependency is truly optional (e.g., a slow integration test that shouldn’t block
unit tests), use the test framework’s skip/ignore mechanism with a clear annotation, and
ensure the full test suite including ignored tests runs in CI:

```rust
// GOOD: Explicit, visible, tracked
#[test]
#[ignore = "requires npx — run with `cargo test -- --ignored`"]
fn test_tryscript_golden() {
    // CI runs both `cargo test` and `cargo test -- --ignored`
    // so this test always runs somewhere.
}
```

```rust
// ALSO GOOD: Fail loudly if the dependency should be present
#[test]
fn test_tryscript_golden() {
    assert!(
        command_exists("npx"),
        "npx is required for tryscript tests — install Node.js"
    );
    // ... actual test logic
}
```

### Anti-Pattern: Massaging Tests to Pass

**What happens:** An agent discovers that a golden test produces different output than
expected. Instead of recording the correct expected output (from the Python reference)
and letting the test fail, the agent adjusts the test to match the Rust output —
truncating with `head -20`, stripping paths with `basename`, or encoding the Rust
behavior as the expected value.

**Example (real):** A tryscript golden test for a comprehensive formatting file used
`head -20` to check only the first 20 lines of output.
The divergence in reference link handling and footnote placement occurred after line 20.
The test passed. The parity gap was invisible.

**The fix:** Expected output in golden tests must always come from the Python reference
implementation, never from the Rust output.
If the outputs differ, the test must fail.
That failure is correct and valuable — it is the test doing its job.

* * *

## Principle 5: Fix the Process, Not the Test

**If a failing test is blocking your workflow, fix the workflow — not the test.**

When a test failure prevents you from making progress (e.g., CI is red, `cargo test`
aborts before reaching your new code), the correct response is to fix the test
infrastructure so that failures are visible but non-blocking for unrelated work.
The incorrect response is to disable, skip, or patch the failing test.

### Anti-Pattern: Disabling Tests to Unblock Development

**What happens:** An agent encounters a failing test unrelated to their current task.
To unblock CI or local development, the agent comments out the test, adds `#[ignore]`
without explanation, or weakens the assertion.

**Why agents do this:** The failing test is “not my problem” and is blocking forward
progress on the actual task.
Disabling it is the fastest path to a green build.

**The fix:**

1. If the test is failing due to a known issue, mark it
   `#[ignore = "issue #NNN: brief description"]` and create a tracking issue.
   The ignored test must still run in a CI job that surfaces failures.

2. If the test is flaky, fix the flakiness.
   If you can’t fix it immediately, document the flakiness and ensure it doesn’t
   silently disappear.

3. If many tests are failing and blocking development, restructure CI to run test suites
   in stages:
   - Fast unit tests (must pass to merge)
   - Integration tests (must pass, separate job)
   - Slow/expensive tests (run nightly, failures create issues)

   Every test still runs.
   The question is only when and how failures are surfaced, not whether they are.

* * *

## Principle 6: Environment Dependencies Must Be Explicit and Enforced

**If a test or build step requires a tool, library, or service, that dependency must be
documented, validated, and enforced — never silently tolerated when absent.**

“Works on my machine” is not a testing strategy.
If your CI environment doesn’t have a required dependency, the CI configuration is the
thing to fix — not the test.

### Anti-Pattern: Tolerating Missing Dependencies

**What happens:** A test requires `npx` (or `python`, or `docker`, or any external
tool). Some environments have it, others don’t. Instead of ensuring the dependency is
present everywhere tests run, the agent adds a runtime check that skips the test when
the tool is missing.

**Why agents do this:** Different environments have different tools installed.
The agent wants the test suite to be “portable” and not fail due to environment setup
issues.

**The fix:**

1. **CI must have all required dependencies.** If a test needs `npx`, the CI workflow
   must install Node.js.
   This is a CI configuration task, not a test code task.

2. **Document all dependencies.** The project README, CI configuration, and contributing
   guide must list every external tool required to run the full test suite.

3. **If a dependency is truly optional**, create a clearly named test category (e.g., a
   cargo feature flag, a test group, or a separate CI job) and document when/where it
   runs. The dependency is still enforced in the environments where that category runs.

* * *

## Principle 7: Ignored Tests Must Be Tracked and Justified

**Every `#[ignore]` annotation must have a reason, and that reason must be tracked.**

Ignored tests are technical debt.
They are acceptable only when the alternative is worse (e.g., a known upstream bug with
no workaround). They must never accumulate silently.

### Anti-Pattern: Untracked Ignored Tests

**What happens:** An agent marks tests as `#[ignore]` during porting because they
“aren’t passing yet.”
No issue is created.
No reason is recorded.
Over time, ignored tests accumulate and nobody remembers why they were ignored or
whether the underlying issue was ever fixed.

**The fix:**

1. Every `#[ignore]` must include a reason string:
   `#[ignore = "upstream comrak bug #1234: incorrect smart quote handling"]`

2. Every ignored test should have a corresponding tracking issue so it appears in the
   backlog.

3. Periodically run `cargo test -- --ignored` (in CI or manually) and triage the
   results.

* * *

## Principle 8: Disparities Must Be Tested Before They Are Fixed, and Investigated Systematically

**When a disparity is discovered, the first action is to write a test that reveals it.
Only after the test fails do you attempt a fix.
After every disparity, systematically investigate the class of behavior it represents.**

A disparity without a discriminating test is unverified — you cannot prove it existed,
and you cannot prove your fix addressed it.
The test-before-fix sequence is non-negotiable:

1. **Write a test against the original’s behavior.** The expected output comes from the
   Python reference implementation.
   The test must specifically reveal the disparity, not just exercise the code path.

2. **Confirm the test fails.** If it doesn’t fail, either the disparity isn’t real or
   the test doesn’t discriminate.
   Revise the test until it captures the actual divergence.

3. **Add the test upstream if it doesn’t exist.** If the original implementation has no
   test covering this behavior, add one.
   Run it against the original to confirm it passes.
   This validates the test itself — if the test fails against the original, the test is
   wrong, not the original.
   This also protects the reference implementation from regressions.

4. **Investigate the class, not just the instance.** Every disparity is a symptom.
   Ask: what category of behavior does this represent?
   Are there other inputs, flags, or code paths where the same kind of divergence could
   occur? A single discovered disparity should trigger a systematic search for related
   ones.

5. **Then fix.** With a failing test in hand and related disparities investigated, now
   attempt the fix. The test going green is the proof.

### Anti-Pattern: Fix Without Evidence

**What happens:** An agent notices a behavioral difference, immediately fixes the Rust
code, and reports the fix.
There is no test that demonstrated the disparity before the fix and no test that
verifies the fix is correct.
The agent’s claim that the gap is closed is unverifiable.

**Example (real):** An agent reports: “Fixed reference link inlining to match Python
behavior.” But no test compares reference link output between the two implementations.
The fix may be correct for the one file the agent checked manually, but without a
discriminating test, regressions are invisible and edge cases are uncovered.

**Why agents do this:** The fix feels obvious and the agent wants to show progress.
Writing the test first feels like bureaucracy when you already know what’s wrong.

**The fix:** No fix is accepted without a test that was red before and green after.
This is not overhead — it is the only way to verify the fix works and to prevent
regressions. The test is the deliverable; the code change is secondary.

### Anti-Pattern: Fixing the Instance, Not the Class

**What happens:** An agent finds that one specific input produces different output.
The agent fixes that case and moves on.
Later, a different input triggers the same category of divergence — different escaping
logic, different whitespace handling, different flag interpretation — because the agent
treated the symptom, not the cause.

**Example (real):** An agent fixes escape handling for `\"` but doesn’t investigate
other escape sequences (`\\`, `\n`, `\t`, `\*`). Each subsequent escape-handling
disparity is discovered and fixed individually across multiple sessions, each time
presented as a new finding.

**Why agents do this:** Fixing the specific reported case feels complete.
Investigating the broader category requires more work and might surface additional
failures that complicate the current PR.

**The fix:** When you find a disparity, generalize before you fix:

1. **Name the category.** “Escape handling,” “whitespace normalization,” “path
   resolution,” “flag parsing.”
   If you can name it, you can search for it.

2. **Enumerate the instances.** What are all the inputs, flags, or code paths in this
   category? If you fixed `\"`, what about every other escape sequence?

3. **Write tests for the category, not just the instance.** A single test for `\"` is
   insufficient. Write tests for the full set of escape sequences, confirm which pass and
   which fail, and track all failures.

4. **Report the scope.** “I found a disparity in escape handling for `\"`. I
   investigated all escape sequences and found 3 additional disparities: `\\`, `\n`, and
   `\*`. I’ve added failing tests for all 4 and fixed 2 of them.
   The remaining 2 are tracked in issues #NNN and #NNN."

This principle applies retroactively.
When a disparity is found that was not caught by existing tests, this is evidence that
the test suite has a gap in that category.
The agent must ask: “Why didn’t our tests catch this?
What other behaviors in this category are also untested?”
Every missed disparity is a lesson about what the test suite is not covering, and that
lesson must be generalized.

* * *

## Compliance Checklist

Use this checklist at the end of every porting session, PR, or milestone to verify
adherence to these principles.
Every item must be true.
If any item is false, the port is incomplete and the violation must be resolved or
prominently tracked before the work is considered done.

### Parity Definition

- [ ] Parity is defined in writing with a crisp, unambiguous scope (e.g., “drop-in
  replacement at the CLI level”).
- [ ] Tolerated variations are listed as a short, closed list.
  Everything not on the list is required to be identical.
- [ ] The parity definition has not been narrowed, reinterpreted, or scoped down without
  explicit user approval.

### Parity Gaps

- [ ] Every known parity discrepancy has a failing test.
  No gap is hidden behind a passing test.
- [ ] Every parity gap that cannot be immediately fixed has a tracked issue marked as a
  severe blocker.
- [ ] No test has been massaged to pass — no output truncation (`head -20`), no path
  stripping (`basename`), no encoding of Rust behavior as expected output.
- [ ] Golden test expected outputs come from the Python reference implementation, not
  from the Rust output.
- [ ] After fixing a parity bug, the corresponding test was immediately un-ignored and
  re-enabled — no stale `#[ignore]` annotations remain from resolved issues.

### Test Execution

- [ ] All tests, without exception, run as part of CI. No test file exists that is not
  executed by the CI pipeline.
- [ ] No tests are `#[ignore]`d without a reason string and a corresponding tracked
  issue. If any `#[ignore]`d tests remain, the port is explicitly marked as incomplete.
- [ ] No test contains “graceful” degradation that silently passes when a dependency is
  missing or a check fails.

### Environment and Dependencies

- [ ] Every external dependency required by tests (e.g., `npx`, `python`, specific
  library versions) is installed in the CI environment.
- [ ] All test dependencies are documented in the project README or contributing guide.
- [ ] If different environments or platforms have different capabilities, test
  categories are clearly separated and each category enforces its own dependencies — no
  silent skipping.

### Process Integrity

- [ ] No test has been disabled, commented out, or had its assertions weakened to
  unblock development.
- [ ] If CI was red due to a pre-existing failure, the failure was addressed (fixed,
  tracked, or restructured into a separate CI stage) — not suppressed.
- [ ] No parity gap has been dismissed as “pre-existing” or “out of scope” without a
  failing test and a tracked issue.
- [ ] Every `#[ignore]` annotation (if any remain) has a reason string and a
  corresponding tracking issue.

### Test-Before-Fix Discipline

- [ ] Every disparity fix was preceded by a discriminating test that failed before the
  fix and passed after.
- [ ] For every disparity test, an equivalent test exists in the original implementation
  (or was added) confirming the expected behavior.
- [ ] Every discovered disparity triggered investigation of the broader category — not
  just the specific instance.
- [ ] No disparity was fixed without first naming the class of behavior it belongs to
  and checking for related gaps.
- [ ] Every missed disparity (found late or by the user) resulted in a review of why
  existing tests did not catch it and what other behaviors in that category are
  untested.

* * *

## Summary

| # | Principle | Anti-Pattern |
| --- | --- | --- |
| 1 | Parity must be defined crisply and never redefined | Implicit scope reduction; improving on the original without approval |
| 2 | Agents must actively pursue parity | Passive gap acknowledgment; stale ignores; "pre-existing"/"out of scope" dismissals |
| 3 | Tests must always run in CI | Orphaned tests that exist but never execute |
| 4 | Tests must never hide failures | “Graceful” degradation; massaging golden tests |
| 5 | Fix the process, not the test | Disabling tests to unblock development |
| 6 | Environment deps must be enforced | Tolerating missing dependencies at runtime |
| 7 | Ignored tests must be tracked | Untracked `#[ignore]` annotations |
| 8 | Disparities must be tested before fixed | Fix without evidence; fixing the instance not the class |

**When in doubt:** A loud failure is always better than a silent pass.
A red CI that shows a real parity gap is always better than a green CI that hides one.
