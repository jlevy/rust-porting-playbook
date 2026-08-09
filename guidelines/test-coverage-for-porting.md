---
title: Test Coverage for Porting
description: Rules for turning a source implementation's tests and behavior into an explicit Rust parity contract
---
# Test Coverage for Porting

Use this document when a Rust implementation must preserve behavior from a source
implementation. It covers source-suite preparation, construct enumeration, test mapping,
and differential validation.
Rust-native test design belongs in [`rust-testing-rules.md`](rust-testing-rules.md).

## Tests Are Evidence, Not the Whole Specification

The source test suite is the strongest executable evidence of expected behavior, but it
contains only the cases someone chose to write.
A faithful port needs three independent forms of evidence:

1. mapped source tests;
2. an explicit inventory of the source surface;
3. differential runs over representative and adversarial inputs.

Mirroring every source test can still reproduce the source suite’s blind spots.
Treat uncovered source behavior as a requirement to investigate, not permission to
invent Rust behavior.

## Syntactic Surface Enumeration (Pre-Emptive Class Sweep)

Differential corpus testing is reactive: common inputs dominate a corpus, so rare valid
forms may never appear.
For finite input surfaces, enumerate the classes before porting.

This applies to parsers, formatters, lexers, configuration loaders, query builders,
protocol messages, and other systems whose input forms can be listed.

1. Identify the semantic node or operation families.
2. Enumerate every source form for each family.
3. Include combinations whose nesting changes behavior.
4. Run each case through the pinned source implementation.
5. Store or generate the observed source result.
6. Add a Rust test for each row.
7. Maintain a matrix that links every row to its source and Rust evidence.

For a Markdown image node, for example, the forms include inline, titled, empty-alt,
full reference, collapsed reference, shortcut reference, missing definition, label case
and whitespace variants, and an image nested inside a link.

Do not hand-author expected output when the source implementation can produce it.
A hand-authored expectation can accidentally validate the port author’s assumption
rather than the source contract.

The Flowmark case study includes a worked
[`parity coverage matrix`](https://github.com/jlevy/flowmark-rs/blob/main/docs/parity-coverage-matrix.md)
and the corresponding
[`syntactic-surface tests`](https://github.com/jlevy/flowmark-rs/blob/main/tests/test_syntactic_surface.rs).

## Strengthen the Source Suite First

Before translating code:

- run the complete source suite from its locked environment;
- measure branch and line coverage as discovery signals;
- identify unexecuted parsing, error, and option branches;
- add source-side tests for missing behavior where feasible;
- record tests that are platform-specific, nondeterministic, quarantined, or ignored;
- confirm the suite fails when a representative behavior is deliberately broken;
- pin the source commit and all generated fixture inputs.

Coverage percentage is not the acceptance criterion.
The useful output is a list of unexercised behavior and a decision for each gap.

When a port uncovers a source-suite blind spot, contribute the source-side test upstream
where practical. This improves the contract for the source project and future ports.

## Maintain a Complete Test Map

Map every discovered source test to one of these explicit states:

- one Rust test;
- several Rust tests because the source test covers several behaviors;
- one shared integration or golden test;
- excluded with a current, reviewed reason;
- blocked by a tracked parity gap.

The map must also detect newly added source tests.
Generate the source and Rust test inventories mechanically, preserve manual mappings
during regeneration, and fail CI for unmapped tests or stale identifiers.

Use [`cross-language-test-mapping.md`](../references/cross-language-test-mapping.md) for
the schema and regeneration model.

## Treat Fixtures as Versioned Evidence

- Store source inputs, expected outputs, stderr, and exit metadata in version control
  when their size permits.
- Record the source commit and exact generation command.
- Regenerate expected output from the pinned source; do not hand-edit it.
- Keep fixtures focused enough that a diff identifies one behavior.
- Share inputs between implementations instead of maintaining parallel copies.
- Mark binary fixtures as binary and verify them with an appropriate structural or hash
  comparison.
- Normalize paths, timestamps, random values, colors, and other nondeterminism only when
  the contract says those values are not meaningful.

Fixture updates are behavior changes.
Review their diffs with the same care as source code.

## Translate Assertions by Meaning

Port the behavior each source assertion establishes, not its test-framework mechanics.

- Preserve boundary values, error types, messages, output bytes, and ordering when they
  are observable.
- Split a source test when separate Rust tests make independent behavior clearer, and
  record all resulting IDs in the test map.
- Do not add Rust-specific implementation assertions as substitutes for source behavior.
- Add Rust-native tests for ownership, feature combinations, platform adapters, and
  unsafe boundaries in addition to the mapped parity suite.
- Keep every ignored Rust test linked to a current tracking issue or bead and a concrete
  unblock condition.

Apply [`rust-testing-rules.md`](rust-testing-rules.md) for placement, fixtures,
snapshots, property tests, and failure-path design.

## Cross-Validate Continuously

Run both implementations against the same input and compare every observable output:

- stdout and stderr bytes;
- exit status;
- files, links, metadata, and directory state;
- structured protocol messages;
- ordering and repeated-run behavior;
- performance only when the acceptance contract includes it.

Keep the source and Rust runs isolated.
Build the Rust binary once per validation run, use the locked source environment,
disable incidental color or progress, and retain a useful unified diff for failures.

Cross-validation belongs in CI while the source is available.
If the source cannot be shipped or built indefinitely, archive the pinned evidence and
document the replacement validation strategy before removing the live comparison.

## Investigate Differences Systematically

Classify each difference before changing either implementation:

1. porting defect;
2. source defect;
3. dependency or platform behavior;
4. nondeterministic observation;
5. approved intentional divergence.

First add or identify a failing test that isolates the class.
Then search for other members of that class.
Do not update expected output simply because the Rust result is plausible, and do not
call an improvement intentional without explicit approval.

## Completion Gate

- [ ] The pinned source suite passes from its locked environment.
- [ ] The source surface inventory has no unexplained missing families.
- [ ] Every source test has a current mapping or tracked exclusion.
- [ ] Fixture provenance and regeneration are reproducible.
- [ ] Rust-native tests follow [`rust-testing-rules.md`](rust-testing-rules.md).
- [ ] Differential validation covers success, errors, and stateful side effects.
- [ ] Every difference is fixed or has an approved, tested, tracked disposition.
- [ ] CI detects source-test drift and parity regressions.

## Related Guidelines

- [`rust-testing-rules.md`](rust-testing-rules.md)
- [`python-to-rust-porting-rules.md`](python-to-rust-porting-rules.md)
- [`porting-principles-and-antipatterns.md`](porting-principles-and-antipatterns.md)
- [`cross-language-test-mapping.md`](../references/cross-language-test-mapping.md)
- `tbd guidelines general-testing-rules general-tdd-guidelines golden-testing-guidelines`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
