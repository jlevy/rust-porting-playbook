---
title: Rust CLI App Patterns
description: Modern patterns for building production-ready Rust CLI applications with clap, tracing, and cross-platform support
---
# Rust CLI App Patterns

Patterns and conventions for building professional Rust CLI applications. Covers project
structure, argument parsing, I/O handling, error reporting, and distribution.

For general Rust rules, see `tbd guidelines rust-general-rules`.
For project setup and CI/CD, see `tbd guidelines rust-project-setup`.
For Python CLI patterns (useful when porting), see `tbd guidelines python-cli-patterns`.

## Project Structure

### Single Binary with Library

The recommended layout separates library logic from CLI wrapper:

```
src/
├── lib.rs          # Public library API
├── main.rs         # CLI entry point (thin wrapper)
├── args.rs         # Argument parsing (clap derive)
├── config.rs       # Configuration types
├── error.rs        # Error types (thiserror)
├── formatter/      # Domain logic modules
│   ├── mod.rs
│   └── ...
└── ...
tests/              # Integration tests
```

**Key principle:** `main.rs` should be thin -- parse args, call library, handle errors.
All logic lives in `lib.rs` and domain modules.

### Binary Naming

- **Repository**: `project-rs` (optional `-rs` suffix for disambiguation)
- **Library crate**: `project` (no suffix -- this is what users `use`)
- **Binary name**: `project` (what users type in terminal)
- **Rationale**: Professional tools avoid suffixes (ripgrep, fd, bat), as they suggest
  a lesser port. The `-rs` goes in the repo URL only.

Dual binary targets for backwards compatibility:
```toml
[[bin]]
name = "project"
path = "src/main.rs"

[[bin]]
name = "project-rs"
path = "src/main.rs"
```

## Argument Parsing with Clap

### Derive API (Recommended)

```rust
use std::path::PathBuf;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(
    name = "flowmark",
    version,
    about = "Markdown auto-formatter",
    long_about = None,
)]
pub struct Args {
    /// Input file (reads from stdin if omitted)
    #[arg(value_name = "FILE")]
    pub input: Option<PathBuf>,

    /// Output file (writes to stdout if omitted)
    #[arg(short, long, value_name = "FILE")]
    pub output: Option<PathBuf>,

    /// Line width for wrapping (0 for no wrapping)
    #[arg(short = 'w', long, default_value_t = 80)]
    pub width: usize,

    /// Enable verbose output
    #[arg(short, long)]
    pub verbose: bool,
}
```

### Flag Conventions

- Match Python's flag names exactly when porting (argparse -> clap)
- Use both short and long flags: `-w` / `--width`
- Document defaults in help text
- Support `--version` and `--help` (clap provides these automatically)

### Subcommands (when needed)

```rust
use clap::Subcommand;

#[derive(Subcommand)]
enum Commands {
    /// Format a document
    Format(FormatArgs),
    /// Check formatting without changes
    Check(CheckArgs),
}
```

## Input/Output Patterns

### Stdin/Stdout with File Fallback

The standard CLI I/O pattern -- read from file or stdin, write to file or stdout:

```rust
use anyhow::Context;
use std::io::Read;

fn read_input(path: Option<&Path>) -> anyhow::Result<String> {
    match path {
        Some(p) => std::fs::read_to_string(p)
            .with_context(|| format!("reading {}", p.display())),
        None => {
            let mut buf = String::new();
            std::io::stdin().read_to_string(&mut buf)?;
            Ok(buf)
        }
    }
}

fn write_output(content: &str, path: Option<&Path>) -> anyhow::Result<()> {
    match path {
        Some(p) => std::fs::write(p, content)
            .with_context(|| format!("writing {}", p.display())),
        None => {
            print!("{content}");
            Ok(())
        }
    }
}
```

### Atomic File Operations

For in-place file modification, use atomic writes via `tempfile`:

```rust
use std::io::Write;
use tempfile::NamedTempFile;

fn atomic_write(path: &Path, content: &str) -> anyhow::Result<()> {
    let dir = path.parent().unwrap_or(Path::new("."));
    let mut tmp = NamedTempFile::new_in(dir)?;
    tmp.write_all(content.as_bytes())?;
    tmp.persist(path)?;
    Ok(())
}
```

### Backup Before Modification

```rust
fn write_with_backup(path: &Path, content: &str, backup_ext: &str) -> anyhow::Result<()> {
    if path.exists() {
        let backup = path.with_extension(backup_ext);
        std::fs::copy(path, &backup)?;
    }
    atomic_write(path, content)
}
```

## Error Handling and Exit Codes

### Recommended: `ExitCode` with explicit error printing

Prefer `fn main() -> ExitCode` over `process::exit()` -- it allows destructors to run
and gives you full control over error formatting. Keep a separate `run()` function that
returns `Result`:

```rust
use std::process::ExitCode;

fn main() -> ExitCode {
    // SIGPIPE: restore default behavior (see "SIGPIPE Handling" below)
    #[cfg(unix)]
    unsafe {
        libc::signal(libc::SIGPIPE, libc::SIG_DFL);
    }

    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e:#}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> anyhow::Result<()> {
    let args = Args::parse();
    setup_logging(args.verbose)?;
    // ... application logic
    Ok(())
}
```

This pattern is preferred because:
- `ExitCode` runs destructors and flushes buffers (unlike `process::exit()`)
- Error formatting is explicit -- you control what the user sees
- `run()` returns `Result` so you can use `?` throughout your logic

### Alternative: `color-eyre` for rich error reports

For tools where backtraces and rich error context aid debugging, use `color-eyre`.
Return `Result` from `main()` directly -- do **not** also catch errors manually with
`if let Err(e)` and call `process::exit(1)`, as that defeats `color-eyre`'s formatting:

```rust
fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    let args = Args::parse();
    setup_logging(args.verbose)?;
    run(&args)?;
    Ok(())
}
```

> **Maintenance note:** `color-eyre` is in maintenance mode (last published 2023).
> It still works, but `anyhow` is actively maintained and is the safer long-term choice
> for most CLIs. Use `color-eyre` only when you specifically need its colorized
> backtraces and `SpanTrace` integration.

### Exit Codes

Follow Unix conventions and match Python when porting:
- `0` -- success
- `1` -- general error
- `2` -- usage/validation error (clap handles this automatically)
- `130` -- interrupted (SIGINT / Ctrl-C)

Avoid `process::exit()` in library code -- it terminates immediately without running
destructors. If you need custom exit codes beyond SUCCESS/FAILURE, use
`ExitCode::from(n)`.

### Diagnostics to Stderr

- **stdout**: program output only (data, formatted results)
- **stderr**: errors, warnings, progress, status messages
- This allows `cmd input.md > output.md` to work correctly

## Logging and Tracing

### `tracing` vs `log`

Rust has two major logging ecosystems:

- **`log`** -- the original facade crate. Simple, widely supported, sufficient for basic
  CLI apps that only need leveled log messages.
- **`tracing`** -- a superset of `log`. Adds structured fields, spans (timed scopes),
  and async-aware instrumentation. Preferred for new projects because it is backwards-
  compatible with `log` (libraries using `log` emit events into `tracing` subscribers).

**Recommendation:** Use `tracing` + `tracing-subscriber` for CLI applications. Libraries
should depend on `tracing` (or just `log` if they want minimal dependencies -- `tracing`
picks up `log` events automatically).

### Setup

```rust
use tracing::{debug, info, warn};
use tracing_subscriber::EnvFilter;

fn setup_logging(verbose: bool) -> anyhow::Result<()> {
    let filter = if verbose {
        EnvFilter::new("debug")
    } else {
        EnvFilter::from_default_env()  // respects RUST_LOG if set, else "warn"
            .add_directive("warn".parse()?)
    };
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_writer(std::io::stderr)
        .init();
    Ok(())
}
```

Enable with `RUST_LOG=debug` or `--verbose` flag. The `EnvFilter::from_default_env()`
call lets users override with `RUST_LOG` even without `--verbose`.

## Progress Reporting

Use `indicatif` for progress bars (stderr only):

```rust
use indicatif::{ProgressBar, ProgressStyle};

let pb = ProgressBar::new(file_count as u64);
pb.set_style(ProgressStyle::default_bar()
    .template("{spinner:.green} [{bar:40}] {pos}/{len} {msg}")
    .unwrap());

for file in files {
    pb.set_message(file.display().to_string());
    process_file(&file)?;
    pb.inc(1);
}
pb.finish_with_message("done");
```

**Agent/CI compatibility:** Disable progress bars when not a TTY:
```rust
use std::io::IsTerminal;

if !std::io::stderr().is_terminal() {
    pb.set_draw_target(indicatif::ProgressDrawTarget::hidden());
}
```

## Configuration Management

### Config Struct with Defaults

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct Config {
    pub line_width: usize,
    pub typography: TypographyOptions,
    pub line_break_mode: LineBreakMode,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            line_width: 80,
            typography: TypographyOptions::default(),
            line_break_mode: LineBreakMode::Sentence,
        }
    }
}
```

The `#[serde(default)]` attribute ensures missing fields in a config file fall back to
`Default::default()`, so users only need to specify values they want to override.

### Config from CLI Args

Map from clap args to config in one place:
```rust
impl From<&Args> for Config {
    fn from(args: &Args) -> Self {
        Config {
            line_width: args.width,
            ..Config::default()
        }
    }
}
```

### Layered Configuration

For tools that support config files, layer sources with CLI args taking highest priority:

1. **Built-in defaults** (`Config::default()`)
2. **Config file** (e.g., `.project.toml` or `pyproject.toml` section)
3. **Environment variables** (optional)
4. **CLI arguments** (highest priority)

```rust
fn load_config(args: &Args) -> anyhow::Result<Config> {
    let mut config = Config::default();

    // Layer 2: config file
    if let Some(path) = find_config_file()? {
        let text = std::fs::read_to_string(&path)?;
        config = toml::from_str(&text)?;
    }

    // Layer 4: CLI overrides
    if let Some(width) = args.width {
        config.line_width = width;
    }

    Ok(config)
}
```

Use `Option<T>` in the Args struct for overridable fields so you can distinguish
"user passed a value" from "clap used a default".

## Cross-Platform Concerns

- **Path handling:** Use `std::path::Path` and `PathBuf`, never string concatenation.
- **Line endings:** Normalize to `\n` on read. Rust writes bytes verbatim (`\n` stays `\n`
  even on Windows), which is usually correct for text processing tools.
- **Terminal colors:** Use `console` or `crossterm` for cross-platform color support.
- **Signal handling:** For graceful Ctrl-C shutdown, use the `ctrlc` crate. Set an
  `AtomicBool` flag and check it in your processing loop rather than calling
  `process::exit()` (which skips destructors):
  ```rust
  use std::sync::atomic::{AtomicBool, Ordering};
  use std::sync::Arc;

  let interrupted = Arc::new(AtomicBool::new(false));
  let flag = interrupted.clone();
  ctrlc::set_handler(move || {
      flag.store(true, Ordering::Relaxed);
  })?;
  ```

## Feature Flags

Use Cargo features to separate CLI-only dependencies from the library:

```toml
[features]
default = ["cli"]
cli = ["clap", "anyhow", "tracing-subscriber", "indicatif"]

[[bin]]
name = "flowmark"
required-features = ["cli"]
```

This allows `flowmark` to be used as a library without pulling in CLI dependencies.

## Version Tracking for Ports

When the Rust CLI is a port of a Python CLI, show both versions:
```rust
// PYTHON_SOURCE_VERSION set by build.rs -- see reference/python-to-rust-porting-guide.md
const VERSION_INFO: &str = concat!(
    env!("CARGO_PKG_VERSION"),
    " (port of python-project ",
    env!("PYTHON_SOURCE_VERSION"),
    ")"
);

#[derive(Parser)]
#[command(version = VERSION_INFO)]
struct Args { /* ... */ }
```

> **Important:** `env!("PYTHON_SOURCE_VERSION")` will fail to compile unless a `build.rs`
> script sets this variable via `cargo:rustc-env=PYTHON_SOURCE_VERSION=...`. See
> `tbd reference python-to-rust-porting-guide` for complete `build.rs` examples that
> extract the version from a Python submodule, a VERSION file, or `git describe`.
>
> If you do not have a Python source to track, omit this pattern entirely and use the
> built-in `version` attribute from `Cargo.toml` (which clap reads automatically).

## Testing CLI Applications

- **Integration tests** should test the full CLI pipeline (args -> processing -> output).
- **Use `assert_cmd`** for testing binary invocations:
  ```rust
  use assert_cmd::Command;

  #[test]
  fn test_stdin_to_stdout() {
      let mut cmd = Command::cargo_bin("flowmark").unwrap();
      cmd.write_stdin("hello  world")
          .assert()
          .success()
          .stdout("hello world\n");
  }
  ```
- **Golden tests** for complex output -- compare against expected output files.
- **Test error cases** -- missing files, invalid args, permission errors.

For golden testing patterns, see `tbd guidelines golden-testing-guidelines`.
For general testing rules, see `tbd guidelines general-testing-rules`.

## SIGPIPE Handling

Rust ignores SIGPIPE by default, which causes "broken pipe" errors when output is piped
to `head`, `less`, or any command that closes the read end early. This is a common
surprise when porting Unix CLI tools.

Add this at the very start of `main()`:

```rust
// Restore default SIGPIPE behavior so piping to `head` etc. works correctly.
// Must be the first thing in main(), before any I/O.
#[cfg(unix)]
unsafe {
    libc::signal(libc::SIGPIPE, libc::SIG_DFL);
}
```

Add `libc` as a dependency:
```toml
[target.'cfg(unix)'.dependencies]
libc = "0.2"
```

Without this fix, `your-tool generate | head -5` will print an error on every run.
This is already included in the recommended `main()` pattern above.

## Shell Completions

Use `clap_complete` to generate shell completion scripts at build time or via a hidden
subcommand:

```rust
use clap::CommandFactory;
use clap_complete::{generate, Shell};

/// Print shell completions to stdout.
fn print_completions(shell: Shell) {
    let mut cmd = Args::command();
    generate(shell, &mut cmd, "project", &mut std::io::stdout());
}
```

Typical usage: `project completions bash > ~/.local/share/bash-completion/completions/project`

For build-time generation (e.g., for packaging), generate completions in `build.rs` and
include them in your release artifacts. See the
[clap_complete documentation](https://docs.rs/clap_complete) for details.

## Related Guidelines

- For general Rust rules, see `tbd guidelines rust-general-rules`
- For project setup, see `tbd guidelines rust-project-setup`
- For Python CLI patterns (porting source), see `tbd guidelines python-cli-patterns`
- For TypeScript CLI patterns (parallel reference), see `tbd guidelines typescript-cli-tool-rules`
- For golden testing, see `tbd guidelines golden-testing-guidelines`
