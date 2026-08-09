---
title: Python-to-Rust CLI Porting
description: Rules for mapping and validating Python command-line interfaces against Rust implementations
---
# Python-to-Rust CLI Porting

Use this guideline when a Rust CLI must preserve a Python CLI’s interface and behavior.
It covers mappings, evidence, and parity decisions.
Use [`rust-cli-rules.md`](rust-cli-rules.md) for the target-side architecture and
`tbd guidelines python-cli-patterns` for the source-side architecture.

## Capture the Python CLI Contract Before Implementing

Record the pinned Python version and capture:

- command and subcommand names;
- positional arguments and whether they are optional or repeated;
- long and short flags;
- defaults, environment variables, and config precedence;
- help, version, completion, and invalid-argument output;
- stdin, stdout, stderr, and file behavior;
- colors, progress, prompts, and non-TTY behavior;
- exit codes, signals, broken pipes, and interruption;
- filesystem or external side effects;
- behavior of every meaningful flag combination.

Generate machine-readable parser metadata where the Python framework supports it, but
retain golden help and error sessions because parser metadata does not capture
presentation or process behavior.

## Map Python Argument Definitions to Rust Types

### argparse to clap

| Python `argparse` | Rust clap derive | Parity concern |
| --- | --- | --- |
| `add_argument("file")` | `file: PathBuf` | required positional |
| `nargs="?"` | `Option<PathBuf>` | absent vs present |
| `-w`, `--width` | `#[arg(short = 'w', long)]` | exact aliases |
| `store_true` | `bool` | default and negation |
| `required=True` | non-`Option` field | parser error path |
| `default=80` | `default_value_t = 80` | help and merged config |
| `type=int` | numeric Rust field | accepted syntax and range |
| `choices=[...]` | `ValueEnum` | spelling and case behavior |
| `nargs="+"` | `Vec<T>` with one-or-more constraint | empty-input error |
| `nargs="*"` | `Vec<T>` with zero-or-more constraint | delimiter behavior |
| `metavar="FILE"` | `value_name = "FILE"` | help output |

### Click or Typer to clap

| Python Click/Typer | Rust clap derive | Parity concern |
| --- | --- | --- |
| command decorator | `Parser` or `Subcommand` | command grouping and aliases |
| positional argument | field without `long` or `short` | order and arity |
| option declaration | `#[arg(long, short)]` | flag names and defaults |
| callback | validation after parse or value parser | error timing and message |
| boolean pair | explicit clap action or paired flags | precedence when both appear |
| prompt/confirmation | explicit interactive boundary | non-interactive behavior |

These are structural mappings, not proof of parity.
Parser libraries differ in accepted syntax, wrapping, ordering, usage text, and error
wording.

## Preserve Flag and Help Semantics

- Match long names, short names, aliases, defaults, repeat behavior, and conflicts.
- Test negative flags and paired positive/negative forms explicitly.
- Preserve whether option order is flexible and whether values beginning with `-` are
  accepted.
- Compare help sections, command ordering, wrapping, default annotations, and exit code.
- Treat a clearer Rust help message as a divergence until explicitly approved.
- If exact formatting is impossible, define the meaningful equivalence rules and keep a
  golden test for each parser version.

## Compare Streams and Process Outcomes

For each success and failure case, capture one record with:

```text
argv
stdin bytes
environment overrides
stdout bytes
stderr bytes
exit status or signal
files or external state changed
```

The Rust CLI must use the same stream contract even if its internal output architecture
is different. Verify:

- data vs diagnostic separation;
- trailing newlines and byte encoding;
- buffering and flush failures;
- color and progress in TTY and non-TTY contexts;
- JSON or other structured-output schemas;
- broken-pipe behavior when the consumer closes early;
- SIGINT behavior and cleanup;
- prompts with and without a terminal;
- partial side effects after failure.

Use [`rust-cli-rules.md`](rust-cli-rules.md) to implement these behaviors without
duplicating the target-side design here.

## Treat Error Behavior as a First-Class Surface

Build a case table for:

- unknown command or flag;
- missing required value;
- invalid enum, number, path, or encoding;
- missing or unreadable input;
- malformed config or data;
- permission and destination collision errors;
- empty, binary, or otherwise unsupported input;
- external command, network, or service failure;
- interruption and broken output pipes.

Compare error class, text or documented equivalence, stderr, exit code, side effects,
and recovery guidance.
Do not validate only the happy path and assume both frameworks classify errors the same
way.

## Cross-Validate With a Structured Harness

Build the Rust binary once, then run both programs through one harness that records
streams and status separately.
Use private temporary directories for each case and keep inputs immutable.

The harness should:

1. load a declarative case containing argv, stdin, environment, and initial filesystem
   state;
2. run the pinned Python command;
3. run the exact Rust binary under test;
4. normalize only approved nondeterministic fields;
5. compare streams, status, and state;
6. write a useful per-field diff;
7. exit non-zero if any unexplained difference remains.

A child can reject arguments and exit before reading piped stdin.
The harness must treat a broken write to that child’s stdin as incidental and still
collect its intended stderr and exit status; it must not panic before the assertion.

Use a transcript or golden-session tool when shell composition, multiple invocations, or
interactive behavior is part of the contract.
Apply `tbd guidelines golden-testing-guidelines`.

## Track Source and Rust Versions Together

Every released port should identify the source version or commit whose behavior it
implements. Keep one machine-readable correspondence record with:

| Rust release | Python version or commit | Parity status | Exceptions |
| --- | --- | --- | --- |
| `vX.Y.Z` | immutable source identifier | validated | linked records |

Expose the source version in `--version` when that helps users assess compatibility.
Derive it from reviewed build input rather than running unbounded network or source
discovery during the build.

## Handle Source Bugs Explicitly

When validation reveals a likely Python defect:

1. isolate it with a source-side test;
2. confirm the pinned Python behavior;
3. file or propose the source correction where practical;
4. decide whether the Rust port temporarily preserves the defect or intentionally
   diverges;
5. add tests and a tracked disposition for that decision;
6. remove temporary compatibility behavior when the source baseline advances and the
   project policy permits it.

Do not silently improve the behavior while still claiming exact parity.

## Synchronize Without Redefining the Contract

For each Python update:

- update the source reference to an exact reviewed commit;
- inventory source code, tests, CLI metadata, and dependency changes;
- update the test map before implementation;
- port behavior and fixtures;
- rerun the full structured CLI comparison;
- update the correspondence record and exception list;
- release according to the project’s synchronization policy.

Source refactors with no observed behavioral change still need evidence that the CLI
surface and test inventory did not drift.

## Acceptance Criteria

- [ ] The Python source version and CLI contract inventory are fixed and reproducible.
- [ ] Every Python command, argument, option, and alias has a Rust disposition.
- [ ] Help, version, invalid-input, and completion behavior are tested.
- [ ] Success and failure cases compare stdout, stderr, exit status, and side effects.
- [ ] TTY, non-TTY, interruption, prompt, and broken-pipe behavior are covered where
  applicable.
- [ ] Every difference is fixed or explicitly approved and tracked.
- [ ] The implementation follows [`rust-cli-rules.md`](rust-cli-rules.md).
- [ ] Source and Rust version correspondence is current.
- [ ] CI detects source test and CLI parity drift.

## Related Guidelines

- [`python-to-rust-porting-rules.md`](python-to-rust-porting-rules.md)
- [`rust-cli-rules.md`](rust-cli-rules.md)
- [`filesystem-heavy-cli-porting.md`](filesystem-heavy-cli-porting.md)
- [`test-coverage-for-porting.md`](test-coverage-for-porting.md)
- [`cross-language-test-mapping.md`](../references/cross-language-test-mapping.md)
- `tbd guidelines python-cli-patterns golden-testing-guidelines`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
