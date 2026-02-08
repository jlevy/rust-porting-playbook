# Test Coverage Playbook

Step-by-step playbook for achieving maximum test coverage on a Python CLI codebase
before porting to Rust. High pre-port coverage means the Rust implementation has a
precise specification to match against.

**Related:** [Python-to-Rust Porting Guide](python-to-rust-porting-guide.md) |
`tbd guidelines test-coverage-for-porting` |
`tbd guidelines golden-testing-guidelines`

**Last update:** 2026-02-07

## Overview

This playbook covers four phases of test coverage work:

1. **Measure** -- Understand current coverage
2. **Expand** -- Write tests for uncovered code
3. **Golden** -- Create golden/snapshot tests for CLI behavior
4. **Document** -- Record what can't be automated

Each phase builds on the previous one. Complete them in order.

## Phase 1: Measure Current Coverage

### 1.1 Run pytest Coverage

```bash
cd python-repo
uv run pytest --cov=myproject --cov-report=term-missing --cov-report=html
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

## Coverage Targets

### Before Porting

| Component | Target | Rationale |
| --- | --- | --- |
| Core library | ≥90% | This IS the specification |
| CLI interface | ≥80% | Clap handles validation |
| Error paths | ≥70% | Test main error scenarios |
| Golden tests | 10+ fixtures | Cover feature matrix |
| Integration tests | Full CLI pipeline | End-to-end verification |

### After Porting (Rust)

| Component | Target | Tool |
| --- | --- | --- |
| Core library | ≥90% | cargo-llvm-cov |
| Public API | 100% | cargo-llvm-cov |
| CLI wrapper | ≥80% | assert_cmd integration tests |
| Cross-validation | 0 diffs | cross-validate.sh |

## Checklist

- [ ] Measured baseline Python coverage
- [ ] Identified and tested uncovered edge cases
- [ ] Created golden test fixtures covering all features
- [ ] Set up tryscript CLI tests (if applicable)
- [ ] Verified idempotency
- [ ] Documented manual test procedures
- [ ] Generated expected output files
- [ ] Committed all fixtures to the repo (not just submodule)
- [ ] Achieved ≥90% coverage on core library
- [ ] All tests pass: `pytest --tb=short`
