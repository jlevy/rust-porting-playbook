---
title: Rust CLI Rules
description: Rules for composable, testable, and cross-platform Rust command-line applications
author: Joshua Levy (github.com/jlevy) with LLM assistance
category: rust
---
# Rust CLI Rules

Use these rules for command-line applications written in Rust, whether they are new or
ports. They define the target CLI behavior and architecture.
Source-language flag and behavior mappings belong in the porting guidelines.

**Related:** [`rust-rules.md`](rust-rules.md),
[`rust-filesystem-rules.md`](rust-filesystem-rules.md),
[`rust-testing-rules.md`](rust-testing-rules.md), and
`tbd guidelines error-handling-rules`.

## Keep the Process Boundary Thin

The executable entry point should initialize process-wide concerns, parse arguments,
call domain logic, render results, and select an exit status.
Put reusable behavior in library modules.

```text
src/
├── lib.rs
├── main.rs
├── cli.rs
├── config.rs
├── error.rs
└── domain/
```

- Keep argument parser types in a CLI-facing module.
- Keep filesystem, network, and terminal adapters at boundaries.
- Do not make domain code print, exit the process, read global arguments, or depend on a
  terminal.
- For a library/CLI package, feature-gate CLI-only dependencies if library consumers do
  not need them.

## Define Arguments as a Stable Interface

Use `clap` derive by default.
It keeps the parser, generated help, value enums, and completion metadata on one typed
definition. Use another parser only when a documented binary-size, compile-time, syntax,
or compatibility constraint outweighs that shared contract.

- Make required values required in the type instead of validating an `Option` later.
- Use enums for closed value sets.
- Distinguish an omitted override from a defaulted value when configuration layers need
  that information.
- Treat `--help`, `--version`, exit codes, completion output, and invalid-input behavior
  as tested interfaces.
- Add `--non-interactive` or `--yes` only when the program actually prompts.
- Add `--dry-run` for destructive or externally visible operations when a faithful
  preview is possible.

```rust
use clap::{Parser, ValueEnum};
use std::path::PathBuf;

#[derive(Clone, Copy, Debug, ValueEnum)]
enum OutputFormat {
    Text,
    Json,
}

#[derive(Debug, Parser)]
struct Args {
    /// Input path; reads stdin when omitted.
    input: Option<PathBuf>,

    /// Structured output format.
    #[arg(long, value_enum, default_value_t = OutputFormat::Text)]
    format: OutputFormat,

    /// Show the planned changes without writing them.
    #[arg(long)]
    dry_run: bool,
}
```

## Preserve Stream Composability

- **Write primary data to stdout.** This includes content intended for pipes or files.
- **Write diagnostics to stderr.** Errors, warnings, progress, debug output, and status
  belong there.
- **Do not mix machine-readable data with prose.** JSON or JSON Lines mode should emit
  one documented schema and keep diagnostics on stderr.
- **Buffer high-volume output.** Lock stdout once and use `BufWriter` instead of
  repeatedly acquiring it.
- **Flush fallible output.** Propagate write and flush errors so the CLI cannot claim
  success after truncated output.
- **Test redirected streams.** A command that works only when attached to a terminal is
  not pipeline-safe.

```rust
use std::io::{self, BufWriter, Write};

fn write_lines(lines: impl IntoIterator<Item = String>) -> io::Result<()> {
    let stdout = io::stdout().lock();
    let mut output = BufWriter::new(stdout);
    for line in lines {
        writeln!(output, "{line}")?;
    }
    output.flush()
}
```

## Make Terminal Behavior Conditional

Use `std::io::IsTerminal` to decide whether interactive presentation is appropriate.

- Suppress progress animation when its stream is not a terminal.
- Respect `NO_COLOR`; support a documented `--color=auto|always|never` policy if users
  need an override.
- Keep ANSI escapes out of redirected output unless the user explicitly forces them.
- Size tables and help output for the available terminal, with a readable maximum.
- Use `PAGER` only for terminal output, and make paging opt-out and failure-safe.
- Disable prompts in CI and non-interactive modes; never wait indefinitely for input
  that cannot arrive.

Progress and status output should normally use stderr so stdout remains composable.

## Report Success Only After Every Required Operation Succeeds

Use a `run` function that returns a result and one top-level boundary that maps the
outcome to user-visible diagnostics and an exit code.

```rust
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error:#}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> anyhow::Result<()> {
    // Parse arguments and perform the complete operation.
    Ok(())
}
```

- Prefer returning `ExitCode` to calling `process::exit`, which skips destructors.
- Reserve exit code 0 for complete success.
- Use stable non-zero codes for documented failure classes when automation needs to
  distinguish them.
- Preserve error causes for debug output while presenting concise default messages.
- Treat partial success as failure unless the command contract explicitly defines a
  successful partial mode.
- Handle interruption as a first-class outcome and state whether in-flight work was
  rolled back, committed, or left for recovery.

Apply `tbd guidelines error-handling-rules` for the full error contract.

## Broken Pipes and SIGPIPE

Consumers such as `head` can close a pipe before the producer finishes.
Rust programs must choose and test a broken-pipe policy.

Two common policies are:

1. propagate writes and convert `ErrorKind::BrokenPipe` into quiet success at the
   executable boundary; or
2. on Unix, restore default SIGPIPE behavior before output begins.

The first policy is safe Rust and explicit.
The second matches traditional Unix process behavior but usually needs a small
dependency or a narrowly reviewed unsafe call.
If using an unsafe signal call, include a `// SAFETY:` argument and isolate it in one
function.

```rust
use std::io;
use std::process::ExitCode;

fn exit_for_io(result: io::Result<()>) -> ExitCode {
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) if error.kind() == io::ErrorKind::BrokenPipe => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error}");
            ExitCode::FAILURE
        }
    }
}
```

Whichever policy the project chooses, test stdout and stderr pipes and ensure a closed
consumer does not produce a panic or misleading error.

## Layer Configuration Explicitly

Configuration precedence should be documented and implemented in one place.
A common order is:

1. built-in defaults;
2. configuration files;
3. environment variables;
4. command-line arguments.

- Use optional CLI fields when omission must be distinguishable from an explicit value.
- Validate the merged configuration before starting side effects.
- Report which configuration file failed and why.
- Do not silently ignore an unreadable explicitly requested file.
- Keep secret values out of debug dumps and error messages.
- Define deterministic discovery rules; avoid searching an unbounded set of parent
  directories without a documented boundary.

## Keep Logging Separate From User Output

Use a logging or tracing facade when the program needs diagnostic levels or structured
events. Libraries should not choose a global subscriber.

- Send logs to stderr or a configured sink, never the data stream.
- Make verbose and debug modes additive; they must not change results.
- Avoid formatting expensive diagnostic values unless the level is enabled.
- Redact credentials, tokens, private paths, and payloads according to policy.
- Do not treat logging an error as handling it.
  Failure must still change control flow or be an explicitly supported degraded result.

## Design Destructive Commands for Recovery

- Provide `--dry-run` when the plan can be computed without mutation.
- Summarize the exact scope before an interactive confirmation.
- Make `--yes` bypass only that confirmation, not validation.
- Prefer atomic replacement, recoverable backups, or transactions.
- Return non-zero if any requested target failed, and identify successful and failed
  targets separately.
- Make retries idempotent or detect the prior partial state and guide recovery.

Use [`rust-filesystem-rules.md`](rust-filesystem-rules.md) for file mutations.

## Handle Cross-Platform Behavior at Boundaries

- Use `Path` and `PathBuf`; do not assemble paths with string separators.
- Preserve non-UTF-8 paths unless the documented interface requires Unicode.
- Make newline and encoding behavior explicit for text-processing commands.
- Test supported platforms rather than assuming Unix behavior.
- Contain platform-specific code in adapters or `cfg` modules.
- Treat signal handling, file replacement, permissions, executable suffixes, and shell
  quoting as platform contracts.
- Pass subprocess arguments as an argument vector, never a shell-composed string, unless
  shell interpretation is the feature being implemented.

## Generate Completions From the Parser

When completions are part of the supported interface, generate them from the argument
definition with `clap_complete` or the parser’s equivalent.

- Offer a command that writes a selected shell’s completion script to stdout.
- Do not write directly into a user’s shell configuration.
- Package generated completions as release artifacts when distribution channels expect
  them.
- Test that generation succeeds for every supported shell.

## Test the Executable Contract

CLI integration tests should cover:

- help, version, and invalid-argument behavior;
- stdin, stdout, stderr, files, and exit codes;
- TTY and non-TTY presentation decisions;
- broken pipes and interruption;
- text and machine-readable modes;
- configuration precedence;
- dry-run and destructive-operation failure paths;
- platform-specific path and newline behavior.

Use [`rust-testing-rules.md`](rust-testing-rules.md) for fixture, snapshot, and property
testing guidance.

## Related Guidelines

- [`rust-rules.md`](rust-rules.md) for language and API design
- [`rust-project-setup.md`](rust-project-setup.md) for Cargo, CI, and dependency policy
- [`rust-filesystem-rules.md`](rust-filesystem-rules.md) for safe mutation
- [`rust-testing-rules.md`](rust-testing-rules.md) for executable tests
- [`rust-release-rules.md`](rust-release-rules.md) for packaging commands and artifacts
- [`python-to-rust-cli-porting.md`](python-to-rust-cli-porting.md) for Python CLI parity
- `tbd guidelines error-handling-rules python-cli-patterns typescript-cli-tool-rules`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
