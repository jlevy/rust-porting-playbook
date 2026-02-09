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
fn read_input(path: Option<&Path>) -> Result<String> {
    match path {
        Some(p) => std::fs::read_to_string(p)
            .map_err(|e| Error::Io(format!("reading {}: {e}", p.display()))),
        None => {
            let mut buf = String::new();
            std::io::stdin().read_to_string(&mut buf)?;
            Ok(buf)
        }
    }
}

fn write_output(content: &str, path: Option<&Path>) -> Result<()> {
    match path {
        Some(p) => std::fs::write(p, content)
            .map_err(|e| Error::Io(format!("writing {}: {e}", p.display()))),
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
use tempfile::NamedTempFile;

fn atomic_write(path: &Path, content: &str) -> Result<()> {
    let dir = path.parent().unwrap_or(Path::new("."));
    let mut tmp = NamedTempFile::new_in(dir)?;
    tmp.write_all(content.as_bytes())?;
    tmp.persist(path)?;
    Ok(())
}
```

### Backup Before Modification

```rust
fn write_with_backup(path: &Path, content: &str, backup_ext: &str) -> Result<()> {
    if path.exists() {
        let backup = path.with_extension(backup_ext);
        std::fs::copy(path, &backup)?;
    }
    atomic_write(path, content)
}
```

## Error Reporting

### Main Function Pattern

Let `color_eyre` handle error reporting -- return `Result` from `main()` and use `?`
throughout. Do not mix `Result` returns with manual `eprintln!`/`process::exit()`.

```rust
fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    let args = Args::parse();
    setup_logging(args.verbose)?;
    run(&args)?;
    Ok(())
}
```

> **Note:** `color-eyre` is in maintenance mode. For simpler applications, `anyhow` is an
> actively maintained alternative.

### Exit Codes

Follow Unix conventions and match Python when porting:
- `0` -- success
- `1` -- general error
- `2` -- usage/validation error (clap handles this automatically)
- `130` -- interrupted (SIGINT / Ctrl-C)

### Diagnostics to Stderr

- **stdout**: program output only (data, formatted results)
- **stderr**: errors, warnings, progress, status messages
- This allows `cmd input.md > output.md` to work correctly

## Logging and Tracing

```rust
use tracing::{debug, info, warn};
use tracing_subscriber::EnvFilter;

fn setup_logging(verbose: bool) -> Result<()> {
    let filter = if verbose {
        EnvFilter::new("debug")
    } else {
        EnvFilter::new("warn")
    };
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_writer(std::io::stderr)
        .init();
    Ok(())
}
```

Enable with `RUST_LOG=debug` or `--verbose` flag.

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
if !std::io::stderr().is_terminal() {
    pb.set_draw_target(indicatif::ProgressDrawTarget::hidden());
}
```

## Configuration Management

### Builder Pattern

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
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

## Cross-Platform Concerns

- **Path handling:** Use `std::path::Path` and `PathBuf`, never string concatenation.
- **Line endings:** Normalize to `\n` on read. Rust writes bytes verbatim (`\n` stays `\n`
  even on Windows), which is usually correct for text processing tools.
- **Terminal colors:** Use `console` or `crossterm` for cross-platform color support.
- **Signal handling:** Register `ctrlc` handler for graceful shutdown:
  ```rust
  ctrlc::set_handler(move || {
      std::process::exit(130);
  })?;
  ```

## Feature Flags

Use Cargo features to separate CLI-only dependencies from the library:

```toml
[features]
default = ["cli"]
cli = ["clap", "color-eyre", "tracing-subscriber", "indicatif"]

[[bin]]
name = "flowmark"
required-features = ["cli"]
```

This allows `flowmark` to be used as a library without pulling in CLI dependencies.

## Version Tracking for Ports

When the Rust CLI is a port of a Python CLI, show both versions:
```rust
// PYTHON_SOURCE_VERSION set by build.rs — see reference/python-to-rust-porting-guide.md
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

Use `build.rs` to extract the Python version from a git submodule at compile time.

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

## Additional Patterns

### SIGPIPE Handling

Rust ignores SIGPIPE by default, causing "broken pipe" errors when piped to `head`, `less`, etc.

```rust
// At the start of main():
#[cfg(unix)]
unsafe {
    libc::signal(libc::SIGPIPE, libc::SIG_DFL);
}
```

Requires `libc` dependency. This restores Unix default behavior where writing to a closed pipe
terminates quietly.

### Shell Completions

Use `clap_complete` to generate shell completion scripts for bash, zsh, fish, etc.

### Exit Codes

Prefer `fn main() -> ExitCode` over `process::exit()` -- it allows destructors to run and is
cleaner:

```rust
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}
```

## Related Guidelines

- For general Rust rules, see `tbd guidelines rust-general-rules`
- For project setup, see `tbd guidelines rust-project-setup`
- For Python CLI patterns (porting source), see `tbd guidelines python-cli-patterns`
- For TypeScript CLI patterns (parallel reference), see `tbd guidelines typescript-cli-tool-rules`
- For golden testing, see `tbd guidelines golden-testing-guidelines`
