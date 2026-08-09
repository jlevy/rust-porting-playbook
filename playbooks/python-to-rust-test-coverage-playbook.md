# Test Coverage Playbook

Step-by-step playbook for achieving maximum test coverage on a Python CLI codebase
before porting to Rust.
High pre-port coverage means the Rust implementation has a precise specification to
match against.

**Related:** [Python-to-Rust Porting Guide](python-to-rust-porting-guide.md) |
[Test Coverage for Porting](../guidelines/test-coverage-for-porting.md) |
[Rust Testing Rules](../guidelines/rust-testing-rules.md) |
`tbd guidelines golden-testing-guidelines`

**Last update:** 2026-05-27

## Overview

This playbook covers seven phases of test coverage work:

0. **Assess & Enhance** -- Evaluate whether existing Python tests are sufficient to
   serve as a specification; enhance them if not
1. **Measure** -- Understand current coverage quantitatively
2. **Expand** -- Write tests for uncovered code
3. **Golden** -- Create golden/snapshot tests for CLI behavior
4. **Document** -- Record what can’t be automated
5. **Property Test** -- Add property-based tests for invariants
6. **Rust Coverage & CI** -- Set up Rust-side coverage and enforce in CI

Each phase builds on the previous one.
Complete them in order.

## Phase 0: Assess Test Sufficiency and Enhance

**Goal:** Before measuring coverage or beginning the Rust port, determine whether the
existing Python test suite is comprehensive enough to serve as the *specification* for
the port. If not, enhance it first.

This phase is critical. If the Python tests are thin, the Rust port will have no
reliable source of truth to match against, and cross-validation will be meaningless.

### 0.1 Test Sufficiency Gate

Answer these questions. If any answer is "no," enhancement is required before proceeding
to Phase 1.

- [ ] Does every public CLI option / flag have at least one test exercising it?
- [ ] Does every major feature (not just happy path) have test coverage?
- [ ] Are error paths tested (invalid input, missing files, bad arguments)?
- [ ] Are edge cases covered (empty input, Unicode, very large input)?
- [ ] Is the test suite runnable with a single command (e.g., `make test`)?
- [ ] If golden/integration tests exist, do they cover the full CLI surface area?

### 0.2 Systematic Gap Identification

Run the test suite and check coverage:

```bash
uv run pytest --cov=myproject --cov-branch --cov-report=term-missing
```

Then review each uncovered function/branch and ask: "Would a Rust port need to replicate
this behavior?" If yes, write a test for it now.

Common gap categories:
- **CLI argument combinations** -- mutually exclusive flags, default values
- **File I/O edge cases** -- permissions, missing files, empty files, binary files
- **Unicode and encoding** -- CJK, emoji, mixed scripts, invalid UTF-8
- **Platform differences** -- line endings, path separators, symlinks
- **Error handling** -- every error message the user can see should have a test

### 0.3 Migrate Legacy Test Formats

If the project uses ad-hoc shell scripts for integration testing (common for CLIs), this
is the time to migrate them to tryscript or a structured testing framework.

**When to migrate to tryscript:**
- Existing bash golden tests capture CLI output and compare against a baseline
- Tests rely on output normalization (stripping timestamps, line numbers, paths)
- Tests use `set -e` + `diff` for pass/fail determination
- The test harness is hard to extend with new test cases

**Tryscript format reference:**

```markdown
---
sandbox: true
env:
  NO_COLOR: "1"
path:
  - $TRYSCRIPT_GIT_ROOT/.venv/bin
patterns:
  VERSION: 'v\d+\.\d+\.\S+'
  TIMESTAMP: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
before: |
  mkdir -p test-dir
  printf 'test content\n' > test-dir/file.txt
---

# CLI Golden Tests

## Basic usage

\`\`\`console
$ mytool --flag test-dir/file.txt
expected output here
\`\`\`

## Error: missing file

\`\`\`console
$ mytool nonexistent.txt 2>&1
Error: file not found: nonexistent.txt
? 1
\`\`\`
```

**Migration steps:**
1. Read each test scenario in the existing bash script
2. Create a `.tryscript.md` file grouped by feature area
3. Add `patterns:` frontmatter for output normalization (replaces perl/sed filters)
4. Add `before:` block for fixture setup (replaces `cp -a` setup)
5. Translate `expect_error` patterns to tryscript’s `? N` exit code syntax
6. Run `tryscript test` to verify the migration produces identical results
7. Organize into multiple files by feature area for maintainability

### 0.4 Establish the Baseline

Once enhancement is complete:
- Run the full test suite and confirm 100% pass rate
- Record the final coverage numbers (target: ≥90% line, ≥80% branch on core library)
- Commit all new tests, fixtures, and tryscript files
- This test suite is now the **specification** for the Rust port

## Phase 1: Measure Current Coverage

### 1.1 Run pytest Coverage

```bash
cd python-repo
uv run pytest --cov=myproject --cov-branch --cov-report=term-missing --cov-report=html
```

Open `htmlcov/index.html` to see line-by-line coverage visualization.

### 1.2 Assess Coverage by Module

| Module | Coverage | Priority for Testing |
| --- | --- | --- |
| Core formatting | X% | High -- port depends on exact behavior |
| CLI parsing | X% | Medium -- clap handles most of this |
| Config handling | X% | Low -- straightforward mapping |
| Error paths | X% | Medium -- important for correctness |

### 1.3 Identify Coverage Gaps

Focus on:
- Functions with <80% coverage
- Code paths only reached by rare inputs
- Error handling branches
- Platform-specific code

## Phase 2: Expand Unit Test Coverage

### 2.1 Edge Case Tests

For each core function, write tests for:

```python
# Empty input
def test_format_empty():
    assert format_document("") == ""

# Whitespace-only input
def test_format_whitespace():
    assert format_document("   \n  \n") == "   \n  \n"

# Single character
def test_format_single_char():
    assert format_document("x") == "x\n"

# Unicode
def test_format_unicode():
    assert format_document("Hello \u2019world\u201d") == "Hello \u2019world\u201d\n"

# Very long lines
def test_format_long_line():
    long_line = "word " * 1000
    result = format_document(long_line)
    assert all(len(line) <= 80 for line in result.splitlines())
```

### 2.2 Boundary Condition Tests

```python
# Width boundaries
def test_wrap_at_exact_width():
    # Line exactly at width -- should NOT wrap
    assert wrap("x" * 80, width=80) == "x" * 80

def test_wrap_one_over_width():
    # Line one char over -- should wrap
    result = wrap("x" * 81, width=80)
    assert "\n" in result
```

### 2.3 Feature Interaction Tests

Test combinations of features that might interact:
- Code blocks inside quotes
- Lists inside footnotes
- Typography inside headings
- Nested quotes with varying depth

### 2.4 Idempotency Tests

Ensure running the tool twice produces the same output:

```python
def test_idempotent():
    input_text = "# Heading\n\nSome text."
    first_pass = format_document(input_text)
    second_pass = format_document(first_pass)
    assert first_pass == second_pass, "Formatting is not idempotent"
```

## Phase 3: Create Golden Tests

### 3.1 Select Representative Inputs

Create input files that cover the full feature surface:

| File | Covers |
| --- | --- |
| `basic.md` | Paragraphs, headings, simple formatting |
| `complex-formatting.md` | Nested lists, code blocks, tables |
| `edge-cases.md` | Empty sections, special characters, Unicode |
| `footnotes.md` | Footnote definitions, references, positioning |
| `frontmatter.md` | YAML frontmatter with various content |
| `real-world.md` | Actual documentation from a real project |
| `large-document.md` | 1000+ line document for performance testing |

### 3.2 Generate Expected Outputs

```bash
#!/usr/bin/env bash
# scripts/generate-golden.sh
set -euo pipefail

PY_CMD=(uv run -q --project python-repo python -m myproject)

mkdir -p test-fixtures/expected

for input in test-fixtures/input/*.md; do
    name="$(basename "$input")"
    echo "Generating: $name"
    "${PY_CMD[@]}" "$input" > "test-fixtures/expected/$name"
done

echo "Done: $(ls test-fixtures/expected/ | wc -l) golden files"
```

### 3.3 Golden Test Assertions in Python

```python
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"

@pytest.mark.parametrize("name", [
    "basic", "complex-formatting", "edge-cases",
    "footnotes", "frontmatter", "real-world",
])
def test_golden(name):
    input_text = (FIXTURE_DIR / "input" / f"{name}.md").read_text()
    expected = (FIXTURE_DIR / "expected" / f"{name}.md").read_text()
    result = format_document(input_text)
    assert result == expected, f"Golden test failed for {name}"
```

### 3.4 CLI Golden Tests with tryscript

[tryscript](https://github.com/jlevy/tryscript) captures CLI sessions as test scripts:

```bash
# Install
pip install tryscript

# Record a test session
tryscript record tests/cli-basic.try
# (interact with the CLI, then exit)

# Replay and verify
tryscript test tests/cli-basic.try
```

Example tryscript test file:
```
# Test basic formatting
$ cat test-fixtures/input/basic.md | python -m myproject
<expected output here>

# Test with width flag
$ python -m myproject --width 60 test-fixtures/input/basic.md
<expected output here>

# Test error handling
$ python -m myproject nonexistent.md
error: file not found: nonexistent.md
? 1
```

### 3.5 Golden Tests in Rust

In the Rust port, golden tests use `include_str!()`:

```rust
macro_rules! golden_test {
    ($name:ident, $file:expr) => {
        #[test]
        fn $name() {
            let input = include_str!(concat!("../../test-fixtures/input/", $file));
            let expected = include_str!(concat!("../../test-fixtures/expected/", $file));
            let result = format_document(input, &Config::default()).unwrap();
            assert_eq!(result, expected, "Golden test failed: {}", $file);
        }
    };
}

golden_test!(golden_basic, "basic.md");
golden_test!(golden_complex, "complex-formatting.md");
golden_test!(golden_edge_cases, "edge-cases.md");
```

**Alternative: `insta` for snapshot testing.** The
[`insta`](https://crates.io/crates/insta) crate provides snapshot testing that
automatically manages expected output files.
On first run it captures output; on subsequent runs it compares against the stored
snapshot. Use `cargo insta review` to interactively accept or reject changes.
This is particularly useful for output-heavy CLI tools and is used by cargo itself.

```rust
use insta::assert_snapshot;

#[test]
fn test_format_basic_snapshot() {
    let input = include_str!("../../test-fixtures/input/basic.md");
    let result = format_document(input, &Config::default()).unwrap();
    assert_snapshot!(result);
}
```

Add to `Cargo.toml`:
```toml
[dev-dependencies]
insta = "1"
```

## Phase 4: Document Manual Test Procedures

### 4.1 Template for Manual Tests

```markdown
## Manual Test: [Feature Name]

**Purpose:** [What this test verifies]
**Prerequisites:** [Setup needed]

### Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Results
- [Expected result 1]
- [Expected result 2]

### Notes
- [Any special considerations]
```

### 4.2 Common Manual Tests for CLIs

1. **Progress bar display** -- verify visual output in interactive terminal
2. **Signal handling** -- Ctrl-C during processing, verify graceful shutdown
3. **Large file performance** -- process a 10MB file, verify no memory issues
4. **Concurrent access** -- two processes writing to same output file
5. **Permission errors** -- read-only file, no-write directory

### 4.3 Cross-Validation Manual Tests

```markdown
## Manual Cross-Validation

### Real-World Document Test
1. Choose 5 real Markdown documents from different projects
2. Run through Python: `python -m myproject doc.md > py-out.md`
3. Run through Rust: `myproject doc.md > rs-out.md`
4. Diff: `diff py-out.md rs-out.md`
5. Document any differences

### Stress Test
1. Generate a 10,000-line Markdown document with diverse features
2. Run both implementations
3. Compare output and processing time
```

## Phase 5: Property-Based Testing

Property-based testing generates random inputs to verify invariants, catching edge cases
that hand-written tests miss.
Add property tests on both the Python and Rust sides.

### 5.1 Python Side: Hypothesis

[Hypothesis](https://hypothesis.readthedocs.io/) generates arbitrary inputs to test
properties of your functions:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_format_never_crashes(text):
    """Formatting should never raise, regardless of input."""
    result = format_document(text)
    assert isinstance(result, str)

@given(st.text(), st.integers(min_value=10, max_value=200))
def test_wrap_respects_width(text, width):
    """No output line should exceed the requested width (unless a single word is longer)."""
    result = wrap(text, width=width)
    for line in result.splitlines():
        assert len(line) <= width or " " not in line

@given(st.text())
def test_format_idempotent(text):
    """Formatting twice should produce the same result as formatting once."""
    first = format_document(text)
    second = format_document(first)
    assert first == second
```

Install: `pip install hypothesis`

### 5.2 Rust Side: proptest

[`proptest`](https://crates.io/crates/proptest) is the standard property-based testing
crate for Rust. [`quickcheck`](https://crates.io/crates/quickcheck) is a lighter
alternative but `proptest` offers more control over input generation.

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn format_never_panics(s in "\\PC{0,500}") {
        // Should never panic, regardless of input
        let _ = format_document(&s, &Config::default());
    }

    #[test]
    fn wrap_respects_width(s in "\\PC{1,200}", width in 10..200usize) {
        let wrapped = wrap(&s, width);
        for line in wrapped.lines() {
            prop_assert!(
                line.len() <= width || !line.contains(' '),
                "Line too long: {} chars (width: {})", line.len(), width
            );
        }
    }

    #[test]
    fn format_is_idempotent(s in "\\PC{0,500}") {
        let first = format_document(&s, &Config::default()).unwrap_or_default();
        let second = format_document(&first, &Config::default()).unwrap_or_default();
        prop_assert_eq!(&first, &second);
    }
}
```

Add to `Cargo.toml`:
```toml
[dev-dependencies]
proptest = "1"
```

## Phase 6: Rust Coverage Tools and CI Integration

### 6.1 Rust Coverage with cargo-tarpaulin

[`cargo-tarpaulin`](https://crates.io/crates/cargo-tarpaulin) provides line and branch
coverage for Rust. It is easy to set up but less accurate than LLVM-based coverage on
complex codebases:

```bash
cargo install cargo-tarpaulin
cargo tarpaulin --out html --all-features
# Open tarpaulin-report.html
```

### 6.2 Rust Coverage with cargo-llvm-cov (Recommended)

[`cargo-llvm-cov`](https://crates.io/crates/cargo-llvm-cov) uses LLVM’s source-based
instrumentation for more accurate results.
This is the recommended tool for production-quality coverage measurement:

```bash
cargo install cargo-llvm-cov
cargo llvm-cov --html --all-features
# Open target/llvm-cov/html/index.html
```

### 6.3 CI Integration

Add coverage enforcement to GitHub Actions:

```yaml
# .github/workflows/coverage.yml
name: Coverage
on: [push, pull_request]
jobs:
  python-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v9
      - run: |
          cd python-repo
          uv run pytest --cov=myproject --cov-branch \
            --cov-report=term-missing --cov-fail-under=90

  rust-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview
      - uses: taiki-e/install-action@cargo-llvm-cov
      - run: cargo llvm-cov --all-features --fail-under-lines 90
```

## Coverage Targets

### Before Porting

| Component | Target | Rationale |
| --- | --- | --- |
| Core library | ≥90% | This IS the specification |
| CLI interface | ≥80% | Clap handles validation |
| Error paths | ≥70% | Test main error scenarios |
| Golden tests | 10+ fixtures | Cover feature matrix |
| Property tests | Key invariants | Catch edge cases humans miss |
| Integration tests | Full CLI pipeline | End-to-end verification |

### After Porting (Rust)

| Component | Target | Tool |
| --- | --- | --- |
| Core library | ≥90% | cargo-llvm-cov (or cargo-tarpaulin) |
| Public API | 100% | cargo-llvm-cov (or cargo-tarpaulin) |
| CLI wrapper | ≥80% | assert_cmd integration tests |
| Property tests | Key invariants | proptest |
| Cross-validation | 0 diffs | cross-validate.sh |

## Checklist

- [ ] Measured baseline Python coverage
- [ ] Identified and tested uncovered edge cases
- [ ] Created golden test fixtures covering all features
- [ ] Set up tryscript CLI tests (if applicable)
- [ ] Verified idempotency
- [ ] Added property-based tests (Hypothesis for Python, proptest for Rust)
- [ ] Documented manual test procedures
- [ ] Generated expected output files
- [ ] Committed all fixtures to the repo (not just submodule)
- [ ] Set up CI coverage enforcement (fail-under thresholds)
- [ ] Achieved ≥90% coverage on core library
- [ ] All tests pass: `uv run pytest --cov=myproject --cov-branch --tb=short`
