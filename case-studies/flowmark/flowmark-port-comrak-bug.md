# Comrak Bug Report: Code Fence Parsing with Indented Lists

**Bug Summary:** Fenced code blocks containing YAML-style indented lists with blank
lines are incorrectly parsed, causing the fence to close prematurely and content to leak
out.

**Severity:** High - causes data loss and incorrect parsing of valid CommonMark

## Environment

- **comrak version:** 0.29.0

- **Rust version:** 1.85+

- **Platform:** All platforms

- **Extensions enabled:** GFM (GitHub Flavored Markdown)

## Minimal Reproduction

### Input Markdown:

    ```yaml
    jobs:
      steps:
        - item1

        - item2
    ```

### Expected Output (Python marko, compliant parsers):

The fence should remain intact with all content inside.

### Actual Output (comrak 0.29.0):

    ```yaml
    jobs:
      steps:
        - item1
    ```

    - item2
    ```
    ```

The fence closes early, `- item2` leaks out as a list item, followed by an empty fence pair.

## Root Cause Analysis

Through code analysis of comrak's parser (`parser/mod.rs`):

1. **Trigger Condition:** Content indented >= 4 spaces (`CODE_INDENT`) inside a fenced code block, following a blank line, that begins with a list marker (`-`)

2. **Parser Logic Flaw:**
   - When parsing line `    - item2` (4 spaces + list marker) inside an open fenced code block:
   - The parser's `parse_code_block_prefix()` correctly identifies we're in a fenced block
   - However, `open_new_blocks()` is subsequently called
   - The `CODE_INDENT` check (>= 4 spaces) triggers indented code block logic
   - This causes the fence to close prematurely
   - The line is then re-interpreted as a Markdown list item

3. **Specific Code Path:**
   - `check_open_blocks_inner()` matches `NodeValue::CodeBlock`
   - Calls `parse_code_block_prefix()` which returns `true` (continue)
   - Control returns to caller, then `open_new_blocks()` is invoked
   - Line 1514-1526: List marker parsing happens despite being inside fence
   - When indent == CODE_INDENT (4), the parser gets confused

## Test Cases

### Case 1: Works (3 spaces - below CODE_INDENT)

Input with 3-space indentation:

    ```yaml
    jobs:
      steps:
       - item1

       - item2
    ```

✅ Parses correctly

### Case 2: FAILS (4 spaces - exactly CODE_INDENT)

Input with 4-space indentation (standard YAML):

    ```yaml
    jobs:
      steps:
        - item1

        - item2
    ```

❌ Fence breaks, content leaks

### Case 3: FAILS (5+ spaces - above CODE_INDENT)

Input with 5-space indentation:

    ```yaml
    jobs:
      steps:
         - item1

         - item2
    ```

❌ Fence breaks, content leaks

### Case 4: Works (no blank line)

Input without blank line between items:

    ```yaml
    jobs:
      steps:
        - item1
        - item2
    ```

✅ Parses correctly - blank line is required trigger

## Impact

This bug affects:
- GitHub Actions workflow examples
- Any YAML/configuration documentation
- CI/CD pipeline documentation  
- Kubernetes manifests
- Any indented list syntax in code examples

Real-world example from Rust project documentation:
```yaml
jobs:
  fmt:
    name: Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
```
This breaks into 3 fragments instead of remaining in one code block.

## Proposed Fix

The fix should be in `parse_code_block_prefix()` or `open_new_blocks()`:

**Option A:** When inside a fenced code block, `open_new_blocks()` should skip ALL
block-opening logic, not just for non-CodeBlock containers.

**Option B:** `parse_code_block_prefix()` should consume the entire line and signal that
no further parsing should occur for this line.

**Option C:** The CODE_INDENT check should be disabled when the current container is a
fenced CodeBlock.

## Workarounds

### Workaround 1: Adjust Indentation
Use 3 spaces or other non-4-space indentation in examples (breaks YAML validity).

### Workaround 2: Remove Blank Lines
Eliminate blank lines between list items in code examples (reduces readability).

### Workaround 3: Post-Processing (lossy)
Regex-based repairs after rendering, but this loses indentation information:
```rust
// Pattern: \n\n```\n<leaked>\n```\n```
// Replace with: \n\n<leaked>```
// Problem: Original indentation is already lost by parser
```

### Workaround 4: Vendor comrak
Fork comrak and patch the parser (recommended for production use).

## References

- Comrak repository: https://github.com/kivikakk/comrak

- Similar issues in other parsers:

  - blackfriday #239: Fenced code block with list fails

  - Hugo discourse: YAML snippets in code fences rendering bug

## Testing

To verify the fix, create a test file with this content:

    ```yaml
    jobs:
      steps:
        - item1

        - item2
    ```

Then test with comrak:

```bash
comrak test.md
```

**Expected result:** single code block with all content preserved
**Current result:** broken fence with leaked content
