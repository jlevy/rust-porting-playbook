---
title: Python-to-Rust CLI Porting
description: CLI-specific patterns for porting Python CLI applications to Rust, including argparse-to-clap mapping and cross-validation
---
# Python-to-Rust CLI Porting

CLI-specific patterns for porting Python CLI applications to Rust: argument parsing
migration, output handling, cross-validation, and acceptance criteria.

For general porting rules, see `python-to-rust-porting-rules.md`.
For Rust CLI patterns, see `rust-cli-app-patterns.md`.
For Python CLI patterns, see `python-cli-patterns.md`.

## CLI Argument Mapping

### argparse to clap

| Python argparse | Rust clap (derive) | Notes |
| --- | --- | --- |
| `add_argument("file")` | `file: PathBuf` | Required positional arg |
| `add_argument("file", nargs="?")` | `file: Option<PathBuf>` | Optional positional arg |
| `add_argument("-w", "--width")` | `#[arg(short = 'w', long)] width: Option<String>` | Short + long flag |
| `add_argument("--flag", action="store_true")` | `#[arg(long)] flag: bool` | Boolean flag |
| `add_argument("--count", required=True)` | `#[arg(long)] count: String` | Required named option (no `Option`) |
| `default=80` | `#[arg(default_value_t = 80)]` | Default value |
| `type=int` | `width: usize` | Type validation (clap parses automatically) |
| `choices=["a","b"]` | `#[arg(value_enum)]` with `#[derive(ValueEnum)]` enum | Enum validation |
| `nargs="+"` | `files: Vec<PathBuf>` | One or more values |
| `nargs="*"` | `#[arg(num_args = 0..)] files: Vec<PathBuf>` | Zero or more values |
| `help="description"` | `/// description` (doc comment) | Help text |
| `metavar="FILE"` | `#[arg(value_name = "FILE")]` | Placeholder in help output |

### typer/click to clap

| Python typer/click | Rust clap (derive) | Notes |
| --- | --- | --- |
| `@app.command()` | `#[derive(Parser)]` | Command definition |
| `@app.command()` + multiple | `#[derive(Subcommand)]` enum | Subcommands |
| `typer.Argument()` | Positional field (no `long`/`short`) | Positional |
| `typer.Option("--width", "-w")` | `#[arg(short = 'w', long)]` | Named option |
| `typer.Option(help="...")` | `/// ...` (doc comment) | Help text |
| `callback=...` | Implement in `main()` after parsing | |

### Exact Flag Parity Requirements

The Rust CLI MUST match the Python CLI exactly:
- Same flag names (long and short)
- Same default values
- Same help text (word-for-word when possible)
- Same behavior when flags are combined

Validation approach:
```bash
python -m project --help > python-help.txt
cargo run -- --help > rust-help.txt
diff python-help.txt rust-help.txt  # Must show zero meaningful diffs
```

## I/O Parity

### Stdin/Stdout Behavior

The Rust CLI must handle I/O exactly like Python:
```bash
# File input, stdout output
python -m project input.md    # Python
project input.md              # Rust -- same output

# Stdin input, stdout output
cat input.md | python -m project    # Python
cat input.md | project              # Rust -- same output

# File input, file output
python -m project input.md -o output.md
project input.md -o output.md
diff <(cat output_py.md) <(cat output_rs.md)  # Zero diffs
```

### Buffered Stdout

Python's `print()` buffers efficiently when writing to a pipe. In Rust,
`println!` acquires and releases the stdout lock on every call, which adds
overhead for high-volume output. Lock stdout once and use `BufWriter`:

```rust
use std::io::{self, BufWriter, Write};

fn run() -> io::Result<()> {
    let stdout = io::stdout().lock();
    let mut out = BufWriter::new(stdout);
    for line in results {
        writeln!(out, "{line}")?;
    }
    Ok(())
}
```

This can make a 10--100x difference for tools that emit thousands of lines.

### Error Message Parity

Error messages should match Python's format or be clearly improved:
```
# Python: "error: file not found: missing.md"
# Rust:   "error: file not found: missing.md"  (exact match preferred)
```

All error messages go to stderr. All program output goes to stdout.

### Exit Code Parity

| Condition | Python | Rust | Notes |
| --- | --- | --- | --- |
| Success | 0 | 0 | |
| General error | 1 | 1 | |
| Usage error | 2 | 2 | clap returns 2 by default |
| SIGINT | 130 | 130 | Register `ctrlc` handler |

Prefer `std::process::ExitCode` over `std::process::exit()` -- it lets destructors
run and avoids abrupt termination:

```rust
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::from(1)
        }
    }
}
```

Use `process::exit()` only in signal handlers (e.g., the `ctrlc` handler) where
you need immediate termination with a specific code.

### SIGPIPE Handling

Rust ignores SIGPIPE by default, which causes "broken pipe" panics when output is
piped to tools like `head`, `less`, or any process that closes the read end early.
Python handles SIGPIPE transparently, so this is a **common gotcha** when porting
CLI tools. Users will see `Error: Broken pipe (os error 32)` where Python worked fine.

**Option 1 (recommended):** Reset SIGPIPE to the default behavior at the start of `main()`.
Requires the `libc` crate:
```rust
// Reset SIGPIPE signal handling to default (terminate silently).
// Without this, piping to `head` etc. causes "broken pipe" errors.
#[cfg(unix)]
{
    // SAFETY: We are restoring default SIGPIPE behavior before any I/O.
    // This is standard practice for CLI tools and has no unsafe side effects.
    unsafe {
        libc::signal(libc::SIGPIPE, libc::SIG_DFL);
    }
}
```

**Option 2:** Handle `BrokenPipe` errors gracefully in your error handler:
```rust
use std::io;
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) if e.kind() == io::ErrorKind::BrokenPipe => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::from(1)
        }
    }
}
```

Option 1 is preferred because it matches Python's behavior exactly and handles
SIGPIPE in all code paths, including third-party libraries. Option 2 only catches
errors that propagate through your own write calls.

### Colored Output and Piping

Python CLIs often use `colorama` or `rich` for colored output and automatically
disable color when piped. Rust equivalents must replicate this behavior:

- Use a color-aware crate such as `anstream` (from the clap ecosystem) or `console`.
- Detect whether stdout/stderr is a terminal and suppress color/formatting when piped
  or redirected:
  ```rust
  use std::io::IsTerminal;

  let use_color = std::io::stdout().is_terminal();
  ```
- Respect the `NO_COLOR` environment variable (see <https://no-color.org/>).
  `anstream` handles this automatically. If using `console`, check with
  `console::colors_enabled()`.
- Respect `--color=auto|always|never` flags when the Python CLI supports them:
  ```rust
  #[arg(long, default_value = "auto")]
  color: clap::ColorChoice,
  ```

**Porting pitfall:** If the Python CLI's output includes ANSI escape codes that end
up in cross-validation diffs, strip them before diffing or ensure both sides use
the same color mode (`--color=never`).

### Shell Completions

Python CLIs using `argcomplete` or click's built-in completion should have equivalent
Rust completions generated via `clap_complete`:

```rust
use clap::CommandFactory;
use clap_complete::{generate, Shell};

// Typically behind a hidden `--completions <SHELL>` flag or a subcommand
fn print_completions(shell: Shell) {
    let mut cmd = Args::command();
    generate(shell, &mut cmd, "project", &mut std::io::stdout());
}
```

Add `clap_complete` as an optional dependency so it does not bloat the binary for
users who do not need completions:
```toml
[dependencies]
clap_complete = { version = "4", optional = true }

[features]
completions = ["clap_complete"]
```

## Cross-Validation Methodology

Cross-validation is the most important quality gate for a port. It runs both
implementations against the same inputs and diffs the outputs.

### Setup

1. **Python source as submodule:**
   ```bash
   git submodule add https://github.com/org/project-python.git python-repo
   ```

2. **Shared test fixtures:**
   ```
   test-fixtures/
   ├── input/          # Input files
   │   ├── basic.md
   │   ├── complex.md
   │   └── edge-cases.md
   └── expected/       # Expected outputs (generated by Python)
       ├── basic.md
       ├── complex.md
       └── edge-cases.md
   ```

3. **Cross-validation script** (`scripts/cross-validate.sh`):
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail

   cargo build --release
   RUST_BIN="target/release/project"
   PY_CMD=(uv run -q --project python-repo python -m project)

   PASSED=0; FAILED=0
   for input in test-fixtures/input/*.md; do
       name="$(basename "$input")"
       py_out=$(mktemp); rs_out=$(mktemp)

       "${PY_CMD[@]}" "$input" > "$py_out"
       "$RUST_BIN" "$input" > "$rs_out"

       if diff -q "$py_out" "$rs_out" >/dev/null; then
           echo "PASS: $name"
           PASSED=$((PASSED + 1))
       else
           echo "FAIL: $name"
           diff -u "$py_out" "$rs_out" | head -20
           FAILED=$((FAILED + 1))
       fi
       rm -f "$py_out" "$rs_out"
   done

   echo "Results: $PASSED passed, $FAILED failed"
   [ "$FAILED" -eq 0 ]
   ```

### Running Cross-Validation

1. Ensure Python environment is set up: `cd python-repo && uv sync`
2. Build Rust: `cargo build --release`
3. Run: `./scripts/cross-validate.sh`
4. Investigate any diffs -- they reveal parser/behavioral differences

### Interpreting Differences

When cross-validation finds diffs:

1. **Categorize the difference:**
   - Parser behavior (different library, not a code bug)
   - Porting bug (code error, fix immediately)
   - Python bug (found a bug in the original -- coordinate with Python repo)
   - Intentional improvement (Rust behavior is better -- document and accept)

2. **For parser differences:**
   - Can it be worked around with post-processing? (preferred)
   - Is it an edge case that rarely occurs? (accept and document)
   - Is it a core behavior difference? (consider switching libraries)

3. **Document everything** in `cross-validation-assessment.md`

## Version Tracking Between Repos

### Build-Time Version Extraction

Use `build.rs` to extract the Python version from the submodule:
```rust
fn main() {
    // Re-run only when the submodule HEAD changes
    println!("cargo:rerun-if-changed=python-repo/.git/HEAD");

    // Try git describe on the submodule
    let version = std::process::Command::new("git")
        .args(["describe", "--tags", "--always"])
        .current_dir("python-repo")
        .output()
        .ok()
        .and_then(|o| String::from_utf8(o.stdout).ok())
        .unwrap_or_else(|| "unknown".into());

    println!("cargo:rustc-env=PYTHON_SOURCE_VERSION={}", version.trim());
}
```

### Version Display

```
$ project --version
project 0.1.0 (port of python-project 0.5.5)
```

### Version Correspondence Table

Maintain in `docs/version-history.md`:
```markdown
| Rust Version | Python Version | Date       | Notes         |
|--------------|----------------|------------|---------------|
| 0.1.0        | v0.5.5         | 2024-11-02 | Initial port  |
| 0.1.1        | v0.5.6         | 2024-11-15 | Bug fixes     |
```

## Handling Python Bugs Found During Porting

The porting process often discovers bugs in the original Python code. Strategy:

1. **Confirm it's a bug** -- not a feature or intentional behavior difference
2. **File a bug/PR** on the Python repo with a test case
3. **Decide whether to replicate the bug** in Rust for parity or fix it
4. **If fixing:** document the intentional divergence from Python
5. **If replicating:** add a `XXX: Python bug` comment and track for future cleanup

## Ongoing Synchronization

When the Python repo gets updates:

1. Update the submodule: `cd python-repo && git pull origin main`
2. Categorize changes: bug fixes, new features, test additions, refactoring
3. Port relevant changes to Rust
4. Run cross-validation to verify parity is maintained
5. Update version correspondence table
6. Document in sync log

## Acceptance Criteria for CLI Parity

**All of these must pass before the port is considered complete:**

Behavioral parity:
- [ ] `--help` output matches Python (format may differ slightly due to clap)
- [ ] `--version` shows both Rust and Python source versions
- [ ] All Python CLI flags have Rust equivalents with same names and defaults
- [ ] Stdin/stdout/file-output behavior is identical
- [ ] Exit codes match for all error conditions
- [ ] Cross-validation passes with zero meaningful diffs on all test fixtures
- [ ] Error messages go to stderr, program output to stdout
- [ ] Piping to `head`/`less` works without errors (SIGPIPE handled)
- [ ] Color output is suppressed when piped or when `NO_COLOR` is set

Non-functional (adjust thresholds per project):
- [ ] Performance meets or exceeds Python (typically 5--50x for Rust CLI tools)
- [ ] Binary size is reasonable for distribution (check with `cargo bloat` if large)
- [ ] Startup time is acceptable (measure with `hyperfine`)

## Related Guidelines

- General porting rules: `python-to-rust-porting-rules.md`
- Rust CLI patterns: `rust-cli-app-patterns.md`
- Python CLI patterns: `python-cli-patterns.md`
- Test coverage for porting: `test-coverage-for-porting.md`
- Golden testing: `golden-testing-guidelines.md`
