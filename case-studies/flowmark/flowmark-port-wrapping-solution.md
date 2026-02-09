# Wrapping Algorithm Solution

**Status**: ✅ COMPLETE - Systematic wrapping fully implemented

> **Note (2026-02-09):** This document describes the final refined wrapping approach
> using comrak's built-in `render.width` option with `hardbreaks = false`. An earlier,
> more complex hybrid approach (using `render.width = 999999` for line joining + custom
> `wrap_paragraphs()` for sentence-aware wrapping + `hardbreaks = true` to preserve
> custom line breaks, totaling ~240 lines of custom code) is documented in
> [Decision Log D7](flowmark-port-decision-log.md#d7-wrapping-algorithm-approach).
> The approach described here supersedes D7 for basic line wrapping by letting comrak
> handle wrapping directly, while the D7 hybrid approach remains relevant for
> advanced sentence-aware semantic wrapping.

## Problem Statement

The Rust port needed to match Python's line wrapping behavior:
- Join consecutive lines within paragraphs
- Re-wrap to specified width
- Preserve structure (quotes, lists, code blocks)

Initial approach using AST transformations was complex and incomplete.

## Solution

**Simple configuration change**: Enable comrak's built-in `render.width` option.

### Implementation

```rust
// In flowmark_comrak_options_with_width()
options.render.hardbreaks = false;  // Join lines with spaces
options.render.width = width;       // Enable wrapping at width

// In fill_markdown()
let options = if line_width > 0 {
    flowmark_comrak_options_with_width(Some(line_width))
} else {
    flowmark_comrak_options()  // No wrapping
};
```

### How It Works

When `render.hardbreaks = false` and `render.width > 0`, comrak automatically:

1. **Converts soft breaks to spaces** - Single newlines become spaces
2. **Joins lines within paragraphs** - Consecutive lines merged
3. **Re-wraps at width** - Text broken at word boundaries
4. **Preserves structure** - Quotes, lists, code blocks stay intact

This matches Python's marko behavior exactly for the core wrapping algorithm.

## Test Coverage

### 1. Formatting Bugs (`test_formatting_bugs`)

All 8 discovered bugs now fixed:
- ✅ Thematic breaks: `* * *` preserved
- ✅ Numbered headings: No escaping `## 1.`
- ✅ Underscore escaping: `x86_64` not escaped
- ✅ Less-than escaping: `< 10ms` not escaped
- ✅ Hash escaping: `##` not escaped
- ✅ Quote blank lines: Correct `>` vs `> ` spacing
- ✅ Code fence bug: YAML lists preserved (pre-processing workaround)
- ✅ Image link wrapping: Badge links stay separate

### 2. Wrapping Behaviors (`test_wrapping_behaviors`)

Comprehensive line joining tests:
- ✅ Regular paragraphs: Lines joined and re-wrapped
- ✅ Quote blocks: Lines joined within paragraphs
- ✅ Regular links: Consecutive links joined
- ✅ Inline images: Consecutive images joined
- ✅ Badge links: Kept on separate lines

### 3. Spacing Rules (`test_comprehensive_spacing`)

Block element spacing consistency:
- ✅ Heading → Paragraph: One blank line (systematic)
- ✅ Heading → Block element: One blank line
- ✅ Block → Heading: One blank line
- ✅ List items: Blanks only when indentation increases

## Python Discrepancies

Two **intentional** differences where Rust is MORE systematic:

### 1. Heading Spacing

**Python (marko)**: No blank line after headings
```markdown
## Heading
Paragraph text
```

**Rust (comrak)**: One blank line after headings
```markdown
## Heading

Paragraph text
```

**Rationale**: 
- Comrak's behavior follows Markdown best practices
- Improves readability
- Consistent with standard formatters

### 2. List Item Spacing

**Python (marko)**: Blanks between ALL items (even same level)
```markdown
- Item one

- Item two
```

**Rust (comrak)**: Blanks only when indentation increases
```markdown
- Item one
- Item two

  - Nested item
```

**Rationale**:
- Comrak's behavior is semantically meaningful
- Blank lines indicate nesting/grouping changes
- More compact for simple lists

## Decision

**Keep Rust's systematic behavior as default.**

Python's spacing appears inconsistent and may be bugs in marko. Rust's
behavior is:
- More systematic and predictable
- Follows Markdown formatting conventions
- More readable (especially for headings)
- Semantically meaningful (for lists)

## Future Work

If exact Python parity is needed:
1. Add CLI flag `--python-spacing` or similar
2. Implement post-processing to match Python quirks
3. Document as compatibility mode

For now, the cleaner systematic behavior is preferred.

## References

- Comrak documentation: `render.hardbreaks` and `render.width` options
- Test files: `test_formatting_bugs.rs`, `test_wrapping_behaviors.rs`
- Bug report: `flowmark-port-comrak-bug.md`
