# Python to Rust CLI Porting Guide

This document covers a systematic process for porting modern Python CLI applications to
Rust for use by AI agents, maintaining feature parity through comprehensive test
fixtures.

**Checklists:** [Initial Port](port-checklist-initial.md) |
[Subsequent Updates](port-checklist-update.md)

**Related:** [Rust CLI Best Practices](rust-cli-best-practices.md)

**Last update:** 2025-11-02

**Update instructions:** After any port, review this document and make any additions to
reflect the best, tested porting process, in particular adding to the pitfalls or useful
patterns for any general and non-obvious porting situations.

## Version Requirements

- **Python**: 3.11+ (modern type hints for better Rust compatibility)

- **Rust**: 1.85+ (Edition 2024). Use the latest stable Rust edition for new code (2024
  as of now). If your MSRV requires it, 2021 is acceptable.

- **Testing**: pytest 8.0+, cargo-tarpaulin or cargo-llvm-cov

## Version Tracking Requirements

**IMPORTANT**: Every Rust version must explicitly track which Python version it ports.

### Version Display Format

The Rust CLI `--version` output MUST show both versions:
```
project-cli 0.1.0 (port of python-project 0.5.5)
```

### Implementation

**In `Cargo.toml`** (workspace or CLI crate):
```toml
[package]
name = "project-cli"
version = "0.1.0"

[package.metadata.python_source]
# Version of Python project this Rust version is based on
# The version tag in Python already identifies the specific commit
version = "0.5.5"
```

**In CLI version output** (`crates/project-cli/src/main.rs` or similar):
```rust
use clap::Parser;

// Reads env var set by build.rs at compile time
const PYTHON_SOURCE_VERSION: &str = env!("PYTHON_SOURCE_VERSION");

const VERSION_INFO: &str = concat!(
    env!("CARGO_PKG_VERSION"),
    " (port of python-project ",
    env!("PYTHON_SOURCE_VERSION"),
    ")"
);

#[derive(Parser)]
#[command(version = VERSION_INFO)]
struct Cli {
    // ... args
}
```

The `env!()` macro reads an environment variable at compile time.
`concat!()` only accepts literals and other macros (like `env!()`), not `const`
variables. Use a `build.rs` script to set custom env vars at compile time:

**`build.rs`**:
```rust
// build.rs
use std::process::Command;

fn main() {
    // Re-run if the Python source changes
    println!("cargo:rerun-if-changed=python-source");

    let version = Command::new("python3")
        .args(["-c", "import myproject; print(myproject.__version__)"])
        .output()
        .ok()
        .and_then(|o| if o.status.success() {
            String::from_utf8(o.stdout).ok()
        } else {
            None
        })
        .map(|s| s.trim().to_string())
        .unwrap_or_else(|| "unknown".to_string());

    println!("cargo:rustc-env=PYTHON_SOURCE_VERSION={version}");
}
```

Alternatively, read the version from a file with a git-describe fallback:

```rust
// build.rs
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=python-source");

    let version = std::fs::read_to_string("python-source/VERSION")
        .map(|s| s.trim().to_string())
        .unwrap_or_else(|_| {
            // Fallback: try git describe
            Command::new("git")
                .args(["describe", "--tags", "--always"])
                .current_dir("python-source")
                .output()
                .ok()
                .and_then(|o| if o.status.success() {
                    String::from_utf8(o.stdout).ok()
                } else {
                    None
                })
                .map(|s| s.trim().to_string())
                .unwrap_or_else(|| "unknown".to_string())
        });

    println!("cargo:rustc-env=PYTHON_SOURCE_VERSION={version}");
}
```

### Documentation Requirements

1. **README.md** must include a “Version Correspondence” section:
   ```markdown
   ## Version Correspondence
   
   | Rust Version | Python Version | Date |
   |--------------|----------------|------|
   | 0.1.0        | v0.5.5         | 2024-11-02 |
   | 0.1.1        | v0.5.6         | 2024-11-15 |
   ```

2. **CHANGELOG.md** must reference Python version in each entry:
   ```markdown
   ## [0.1.0] - 2024-11-02
   
   ### Port Status
   - Ported from python-project v0.5.5
   - 100% feature parity achieved
   - All 111 tests passing
   
   ### Added
   - Initial Rust port
   ```

3. **Git commit messages** for sync updates must include:
   ```
   Sync from Python repo v0.5.6 @ def456e
   
   Python changes:
   - Added smart quote feature
   - Fixed list formatting edge case
   
   Rust updates:
   - Ported smart quote logic
   - Updated tests
   ```

### Automation in Sync Script

Update `scripts/sync-from-python.sh` to automatically update version tracking:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd python-source
git fetch origin
LATEST_COMMIT=$(git rev-parse origin/main)
PYTHON_VERSION=$(git describe --tags --always origin/main)

# Update Cargo.toml metadata
cd ..
# Use toml-cli or sed to update python_source metadata
# Example with sed (adjust to your TOML structure):
sed -i.bak "s/^commit = .*/commit = \"${LATEST_COMMIT:0:7}\"/" Cargo.toml
sed -i.bak "s/^date = .*/date = \"$(date +%Y-%m-%d)\"/" Cargo.toml

# If Python has a VERSION file, update that reference too
if [ -f python-source/VERSION ]; then
    PYTHON_VERSION=$(cat python-source/VERSION)
    sed -i.bak "s/^version = .*/version = \"$PYTHON_VERSION\"/" Cargo.toml
fi

echo "Updated Cargo.toml with Python version: $PYTHON_VERSION @ ${LATEST_COMMIT:0:7}"
```

## Phase 1: Project Setup

**See:** [Initial Port Checklist - Phase 1: Project
Setup](port-checklist-initial.md#phase-1-project-setup) for complete setup instructions
including repository structure, workspace configuration, best practices configuration,
and release profile optimization.

### Key Concepts

**Repository Structure:**
```
project-rs/
├── python-source/              # Git submodule (read-only reference)
├── test-fixtures/              # Committed test data (self-contained)
│   ├── input/
│   └── expected/
├── crates/
│   ├── project-core/          # Library implementation
│   └── project-cli/           # Binary/CLI wrapper
├── scripts/
│   ├── sync-from-python.sh    # Update Python source & fixtures
│   └── validate-parity.sh     # Cross-check outputs
└── Cargo.toml                 # Workspace definition
```

**Python Source as Submodule:**

Why use a submodule?

- AI agents can directly read Python source using standard file operations

- Submodule pointer records exact Python commit being ported

- Can run Python tests to verify expected behavior

- Git history shows Python version correspondence

```bash
git submodule add https://github.com/org/project-python.git python-source
git submodule update --init --recursive
git add .gitmodules python-source/
git commit -m "Add Python source as submodule for porting reference"
```

**Important**: CI/CD uses committed test fixtures, not the submodule.

## Phase 2: Dependencies & Porting Process

**See:** [Initial Port Checklist - Phase 2: Dependencies & Core
Setup](port-checklist-initial.md#phase-2-dependencies--core-setup) for detailed
dependency setup and [Phase 3: Porting
Process](port-checklist-initial.md#phase-3-porting-process) for complete
module-by-module porting instructions, critical pitfalls checklist, and integration test
setup.

### Dependency Mappings

| Python | Rust | Notes |
| --- | --- | --- |
| argparse/click | [clap](https://docs.rs/clap) | CLI parsing |
| PyYAML | [serde_yaml_ng](https://docs.rs/serde_yaml_ng) | Successor to archived serde_yaml |
| pytest | Built-in #[test] + cargo test |  |
| Markdown libs | [comrak](https://github.com/kivikakk/comrak) / [pulldown-cmark](https://docs.rs/pulldown-cmark) | Choose based on features |

**Key ecosystem crates**: [anyhow](https://docs.rs/anyhow) (app errors),
[thiserror](https://docs.rs/thiserror) (library errors), [serde](https://serde.rs/)
(serialization)

### Porting Sequence

**For each module:**

1. Read Python source from `python-source/` submodule

2. Create Rust equivalent with exact function names and structurally equivalent return
   types

3. Port inline tests to Rust `#[cfg(test)]` modules

4. Validate with fixtures after each module

### Test Strategy

**Integration tests** in `crates/project-core/tests/`:
```rust
#[test]
fn test_format_document_basic() {
    let input = include_str!("../../test-fixtures/input/basic.md");
    let expected = include_str!("../../test-fixtures/expected/basic.md");
    let result = format_document(input, &Config::default());
    assert_eq!(result, expected);
}
```

Adjust fixture paths to your repository layout.
For large fixtures, consider reading from disk in tests to keep binaries smaller.

### Porting Parity Requirements

**Important test requirements:**

- Must maintain exact 1:1 replication of all Python tests (behavioral parity).

- Additional Rust-specific unit tests encouraged (faster feedback, during development of
  the port, covering Rust edge cases, confirming return types, etc.)

- Use `include_str!()` to embed fixtures (like input and expected output text files) at
  compile time

**Important commenting and structure requirements:**

- Must maintain clear mapping of modules in Python to modules in Rust

- Must maintain comments at the top of each module indicating which Python module it
  corresponds to

- Must maintain comments at the top of every major function indicating which Python
  function it corresponds to

### CLI Parity

**See:** [Initial Port Checklist - Phase 4: CLI
Implementation](port-checklist-initial.md#phase-4-cli-implementation) for complete CLI
parity requirements and validation procedures.

**Key Requirements:**

The Rust CLI must **exactly** match Python’s interface:

- Same flag names, short flags, defaults, help text

- Same exit codes (0 success, 1 errors, 2 usage)

- Accept stdin/stdout piping

- Identical error messages (or improved but consistent)

**Validation:**
```bash
python-source/cli.py --help > python-help.txt
cargo run -- --help > rust-help.txt
diff python-help.txt rust-help.txt  # Must show zero diffs
```

**Critical:** CLI output must be identical byte-for-byte.
This includes help text, error messages, warnings, status messages, and all command
output (not just processing results).

## Phase 3: Testing & Validation

**See:** [Initial Port Checklist - Phase 5: Testing &
Validation](port-checklist-initial.md#phase-5-testing--validation) for complete testing
requirements including test coverage targets, cross-validation procedures, and quality
checks.

### Cross-Validation Script

`scripts/validate-parity.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

FIXTURES_DIR="test-fixtures/input"
TEMP_DIR="$(mktemp -d)"
cargo build --release
RUST_BIN="target/release/project-cli"

# How to run the Python reference CLI (adjust to your project)
PY_REF_CMD=(uv run -q --project python-source python -m project_cli)

pushd python-source >/dev/null
uv sync -q
popd >/dev/null

PASSED=0
FAILED=0
for input_file in "$FIXTURES_DIR"/*.md; do
  filename="$(basename "$input_file")"
  printf "Testing %s... " "$filename"
  "${PY_REF_CMD[@]}" "$input_file" > "$TEMP_DIR/python-$filename"
  "$RUST_BIN" "$input_file" > "$TEMP_DIR/rust-$filename"

  if diff -q "$TEMP_DIR/python-$filename" "$TEMP_DIR/rust-$filename" >/dev/null; then
    echo "PASS"
    ((PASSED++))
  else
    echo "FAIL"
    diff -u "$TEMP_DIR/python-$filename" "$TEMP_DIR/rust-$filename" | head -20
    ((FAILED++))
  fi
done

echo "Results: $PASSED passed, $FAILED failed"
rm -rf "$TEMP_DIR"
test $FAILED -eq 0
```

### Coverage Targets

- ≥90% line coverage in core library

- 100% coverage of public API

- Property tests for algorithmic correctness

**Tools**: pytest-cov (Python); cargo-llvm-cov or cargo-tarpaulin (Rust); proptest
(property tests); criterion (benchmarks)

## Phase 4: Ongoing Synchronization of Python Code Changes

### Sync Process

`scripts/sync-from-python.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

cd python-source
git fetch origin
LATEST_COMMIT=$(git rev-parse origin/main)
CURRENT_COMMIT=$(git rev-parse HEAD)

if [ "$LATEST_COMMIT" = "$CURRENT_COMMIT" ]; then
    echo "Already up to date with Python repo"
    exit 0
fi

echo "Updating from $CURRENT_COMMIT to $LATEST_COMMIT"
git checkout "$LATEST_COMMIT"
cd ..

# Copy test fixtures
rsync -av --delete python-source/tests/fixtures/input/ test-fixtures/input/
rsync -av --delete python-source/tests/fixtures/expected/ test-fixtures/expected/

# Regenerate expected outputs with Python
pushd python-source >/dev/null
uv sync -q
uv run -q python -m pytest tests/ --update-fixtures
popd >/dev/null
cp python-source/tests/fixtures/expected/* test-fixtures/expected/

CHANGE_SUMMARY=$(cd python-source && git log --oneline "$CURRENT_COMMIT".."$LATEST_COMMIT")

git add python-source test-fixtures/
git commit -m "Sync from Python repo @ ${LATEST_COMMIT:0:7}

Python changes since last sync:
$CHANGE_SUMMARY

Regenerated test fixtures and updated submodule pointer."

echo "Next steps:"
echo "1. Review Python changes: cd python-source && git log $CURRENT_COMMIT..HEAD"
echo "2. Port any new features to Rust"
echo "3. Run tests: cargo test"
echo "4. Validate parity: ./scripts/validate-parity.sh"
```

### Handling Python Code Updates

**See:** [Subsequent Update Checklist](port-checklist-update.md) for the complete
workflow when syncing Python updates to Rust.

**Quick Reference - Categorize updates:**

- **Bug fixes**: Port fix to Rust, verify tests pass

- **New features**: Decide if needed in Rust version

- **Test additions**: Port tests, implement functionality

- **Refactoring**: May not need Rust changes if behavior unchanged

**Maintain sync log** in `docs/python-sync-log.md`:

```markdown
## 2024-03-15: Sync from Python @ abc1234

**Python changes:**
- Added smart quote feature
- Fixed edge case in list formatting

**Rust updates required:**
- [ ] Port smart quote logic (src/typography.rs)
- [ ] Port list formatting fix (src/formatter.rs)
- [x] Update tests (no code changes needed)

**Status**: In progress
```

### Gradual Divergence

**When to diverge:**

- Rust-specific optimizations

- Performance features leveraging Rust’s strengths

- Platform-specific integrations (WebAssembly)

**How to manage:**

- Document differences clearly in README

- Maintain core behavioral parity

- Mark tests as “Rust-specific” or “Python-specific”

## Checklists

- **[Initial Port Checklist](port-checklist-initial.md)** - Complete checklist for
  porting a Python CLI to Rust for the first time

- **[Subsequent Update Checklist](port-checklist-update.md)** - Checklist for syncing
  and porting updates from Python to existing Rust port

## Final Acceptance Criteria

**Completion Gate:** All items below must be satisfied.
Acceptance requires exact 100% passing of every test, exact 100% parity with every
original Python test, and exact byte-for-byte matching on all comparisons (zero diffs).
This includes test output, CLI command output, help text, error messages, and all
processing results.

**See:** [Initial Port Checklist - Phase 10: Final Acceptance
Criteria](port-checklist-initial.md#phase-10-final-acceptance-criteria) for the
complete, detailed checklist.

### Summary

The acceptance criteria cover:

- **Porting Parity Requirements (Mandatory):** All Python tests replicated with exact
  1:1 behavioral parity, module/function mapping comments, proper use of
  `include_str!()` for fixtures

- **CLI Parity (Mandatory):** Exact flag names/defaults/help text, zero diffs on all CLI
  output (help, errors, warnings, status), correct exit codes, stdin/stdout piping

- **Test Parity (Mandatory):** 100% of tests pass, every original Python test replicated
  with exact behavior, all output comparisons are byte-for-byte matches (zero diffs)

- **Cross-Validation (Mandatory):** Zero diffs across all fixtures, byte-for-byte
  matching of all file outputs

- **Performance Targets:** Binary size < 10MB, processing speed 50-100x faster than
  Python, startup time < 50ms

- **Quality Metrics (Mandatory):** Zero clippy warnings, ≥90% test coverage in core
  library, 100% coverage of public API, all public APIs documented, security audits pass

## Key Non-Obvious Pitfalls

### Regex Pattern Differences

**Problem:** Python’s `re.match()` implicitly anchors to start; Rust’s `is_match()`
matches anywhere.

```python
# Python - matches only at start
pattern = r"\w*[sS]'$"
re.match(pattern, "James'")      # Matches
re.match(pattern, "$James'")     # Does NOT match
```

```rust
// Rust - WITHOUT explicit anchor
let pattern = Regex::new(r"\w*[sS]'$").unwrap();
pattern.is_match("$James'")      // ALSO matches (incorrect!)

// Rust - WITH explicit anchor (correct)
let pattern = Regex::new(r"^\w*[sS]'$").unwrap();
pattern.is_match("$James'")      // Does NOT match
```

**Takeaway:** Any pattern used with `re.match()` needs `^` anchor in Rust.

### Regex Feature Parity (look-arounds, backrefs)

Python’s `re` supports look-around and backreferences; the Rust `regex` crate does not.
If parity is required, use `fancy-regex` for those patterns, understanding it can be
slower; keep hot paths on `regex` where possible.

### String Preservation

**Problem:** Don’t “helpfully” transform input when Python doesn’t.

```python
def first_sentence(text: str) -> str:
    sentences = split_sentences(text)
    return sentences[0] if sentences else text  # Original text unchanged
```

```rust
// WRONG - modifies input
pub fn first_sentence(text: &str) -> String {
    if sentences.is_empty() {
        text.trim().to_string()  // WRONG!
    } else { sentences[0].clone() }
}

// CORRECT - preserves input
pub fn first_sentence(text: &str) -> String {
    if sentences.is_empty() {
        text.to_string()  // Unchanged
    } else { sentences[0].clone() }
}
```

**Test case:** `assert first_sentence(" ") == " " # Not ""!`

### Line Endings and Encodings

- Normalize CRLF/LF in tests when line endings are not semantically significant

- Assume UTF-8; reject or normalize invalid encodings at boundaries

- For byte-for-byte parity tests, compare exact bytes and document expectations

### Arena Pattern for AST Nodes

**Problem:** Tree structures create self-referential lifetimes.

```rust
// DOESN'T work - self-referential struct
pub struct MarkdownDocument<'a> {
    arena: Arena<AstNode<'a>>,     // Owns the arena
    root: &'a AstNode<'a>,         // Borrows from arena - IMPOSSIBLE
}
```

**Solution:** Closure-based API with higher-rank trait bounds:

```rust
pub fn with_markdown_ast<F, R>(text: &str, f: F) -> Result<R>
where
    F: for<'a> FnOnce(&'a AstNode<'a>) -> Result<R>,
{
    let arena = Arena::new();
    let options = Options::default();
    let root = parse_document(&arena, text, &options);
    f(root)
}  // Arena drops after user code completes
```

**Takeaway:** Use closures to control borrow scope; common with comrak, pulldown-cmark.

### Function Signature Compatibility

**Problem:** Even small differences in return types break compatibility.

```python
def split_frontmatter(text: str) -> tuple[str, str]:
    return ("", text)  # Returns ("", text) if no frontmatter
```

```rust
// WRONG - different return type
pub fn extract_frontmatter(text: &str) -> Result<Option<(String, String)>> {
    Ok(None)  // NOT COMPATIBLE
}

// CORRECT - matches Python
pub fn split_frontmatter(text: &str) -> (String, String) {
    ("".to_string(), text.to_string())
}
```

**Takeaway:** Function names, return types, and empty/None cases must match exactly.

### Unicode Handling

**Note:** Rust supports Unicode string literals.
Using explicit escapes in tests avoids encoding/visual issues and makes intent
unambiguous.

```python
assert smart_quotes("I'm there") == "I’m there"  # Direct Unicode literal is fine
```

```rust
assert_eq!(smart_quotes("I'm there"), "I\u{2019}m there");  // \u{2019} = '
```

**Common escapes:** `\u{2018}` ‘, `\u{2019}` ’, `\u{201c}` “, `\u{201d}` ”, `\u{2026}` …

### Test Output Validation

**Problem:** Internal state changes don’t guarantee correct output.

```rust
// WRONG - counting nodes
let strong_before = count_strong_nodes(root);
unbold_headings(root);
assert_eq!(count_strong_nodes(root), strong_before - 4);  // Could still render wrong!

// CORRECT - compare full rendered output byte-for-byte
let arena = Arena::new();
let root = parse_document(&arena, INPUT, &options);
unbold_headings(root);

let mut output = Vec::new();
format_commonmark(root, &options, &mut output).unwrap();
let result = String::from_utf8(output).unwrap();

assert_eq!(result.trim(), EXPECTED_OUTPUT.trim());  // Exact match
```

**Takeaway:** Prefer exact byte-for-byte comparisons.
Only trim if trailing whitespace is explicitly non-semantic for your project.

### Integration Test Location

**Problem:** Cargo only discovers tests in specific locations.

```
# WRONG - workspace root NOT discovered
project-rs/
├── tests/
│   └── test_cleanups.rs
└── crates/project-core/src/

# CORRECT - crate's tests/ discovered
project-rs/
└── crates/project-core/
    ├── tests/test_cleanups.rs
    └── src/
```

**Takeaway:** Integration tests go in `<crate>/tests/`, not workspace root.

### Error Reporting Consistency

- Use `thiserror` for library error types and `color-eyre` (or similar) in the CLI for
  consistent, readable diagnostics

- Send human-readable diagnostics to stderr; reserve stdout for program output

- Match Python’s exit codes and error phrasing where parity is required

### Error Handling for Compatibility

```rust
// When Python never raises, don't use Result
pub fn split_frontmatter(text: &str) -> (String, String) {
    // No Result needed - matches Python's behavior
    ("".to_string(), text.to_string())
}
```

**Takeaway:** Only use `Result` if Python function can raise.

### Other Common Issues

- **String slicing**: `text[start..end]` panics if not on char boundaries; use `chars()`
  iterator

- **Library types**: `comrak` `NodeValue::Text` is not a `String` (version-dependent;
  often `CowStr`/`Vec<u8>`). Check current docs and convert explicitly.

- **Module system**: Rust requires explicit `mod` declarations

- **Unit test timing**: Port function → write unit tests → run/fix → move to next →
  integration tests last

## Useful Patterns

### Closure-based API for Borrowed Data

```rust
pub fn with_resource<F, R>(f: F) -> Result<R>
where
    F: for<'a> FnOnce(&'a Resource<'a>) -> Result<R>,
{
    let resource = create_resource();
    f(&resource)
}
```

**Use when:** Resource has internal borrows (like Arena + AST nodes)

### Lazy Static Regex

```rust
use std::sync::LazyLock;
use regex::Regex;

static PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"pattern").unwrap());

pub fn process(text: &str) -> String {
    PATTERN.replace_all(text, "replacement").to_string()
}
```

**Use when:** Regex pattern used multiple times (compilation is expensive)

### Build size and performance tips

- In `Cargo.toml` release profile: enable LTO, reduce codegen units, consider `panic =
  "abort"`

- For smaller binaries: use `opt-level = "z"` or `"s"`, and strip symbols in CI

- Avoid heavy dependencies in the CLI crate; keep them in the library when reusable

- Benchmark with `criterion` and inspect size with `cargo-bloat`
