# Flowmark Port: Library Choices

Case study of library evaluation, selection, and workarounds from the flowmark
Python-to-Rust port. Covers the evaluation methodology used, the comrak experience,
all workarounds implemented, and alternative parser options.

**Related:**
[Decision Log](flowmark-port-decision-log.md) |
[Analysis](flowmark-port-analysis.md)

**Last update:** 2026-02-08

## Why Library Choice Matters

Library choice is the **#1 risk factor** in a Python-to-Rust port. The flowmark port
spent ~50% of total effort working around differences between the Python Markdown parser
(marko) and the Rust parser (comrak). A better library choice could have reduced this to
near zero.

**Key insight:** The cost of working around a bad library choice grows super-linearly.
The first workaround is cheap, but the 12th workaround means you're maintaining a
fragile layer of fixes that interact in unexpected ways.

## Evaluation Methodology

### Evaluation Criteria

#### Tier 1: Must-Have (Eliminatory)

| Criterion | Question | How to Evaluate |
| --- | --- | --- |
| **Spec compliance** | Does it implement the same standard? | Check test suite coverage, spec version |
| **Feature coverage** | Does it support all features the Python lib uses? | Create feature matrix, test each |
| **API capability** | Can it produce the same outputs? | Run against real inputs from Python |
| **Active maintenance** | Is it actively maintained? | Last commit date, response to issues |

#### Tier 2: Important (Differentiators)

| Criterion | Question | How to Evaluate |
| --- | --- | --- |
| **Output fidelity** | Does output match Python byte-for-byte? | Cross-validation on test fixtures |
| **Customization** | Can behavior be adjusted/overridden? | Review API docs for hooks/plugins |
| **Error handling** | Does it handle edge cases gracefully? | Fuzz testing, edge case inputs |
| **Performance** | Is it fast enough? | Benchmarks on representative inputs |
| **Community** | Are issues responded to? PRs accepted? | GitHub activity metrics |

#### Tier 3: Nice-to-Have

| Criterion | Question |
| --- | --- |
| **Documentation quality** | Are docs comprehensive with examples? |
| **Compile time impact** | Does it add significant compile time? |
| **Dependency tree** | How many transitive dependencies? |
| **Binary size impact** | How much does it add to the binary? |

### Evaluation Process

**Step 1: Identify candidates.** Search crates.io and lib.rs. For critical
dependencies, identify at least 2-3 candidates.

**Step 2: Feature matrix.** Create a comparison table:

| Feature | Python Lib | Candidate A | Candidate B | Candidate C |
| --- | --- | --- | --- | --- |
| CommonMark 0.31 | Y | Y | Y | Partial |
| GFM Tables | Y | Y | N | Y |
| Footnotes | Y | Y | N | Y |
| AST access | Y | Y | Y | Event-only |
| Custom rendering | Y | Plugin | N | N |

**Step 3: Proof-of-concept testing.** Before committing, write a minimal test that
processes 5-10 representative inputs and compare output against Python's output.
Document any differences found. This step saved the flowmark port from choosing
pulldown-cmark.

**Step 4: Cross-validation.** Run full cross-validation against the Python
implementation on all test fixtures. Count and categorize differences:
- **Zero diffs:** Ideal -- proceed
- **1-5 cosmetic diffs:** Acceptable if workaround-able
- **6+ diffs or structural diffs:** Consider alternatives

**Step 5: Document decision.** Record candidates evaluated, selection rationale, known
limitations with workarounds, and fallback plan.

## Parser Selection Decision

**Date:** 2025-11-02 | **Impact:** Critical

### Candidates Evaluated

Three Rust Markdown parsers were evaluated:
- **comrak** -- Full GFM, footnotes, AST access, plugin system
- **pulldown-cmark** -- Fast, widely used, event-based, footnotes as optional extension
- **markdown-rs** -- By unified.js author, spec-compliant, event-based

### Decision: Selected comrak

Based on:
1. 670/670 GFM spec compliance
2. Built-in footnote support (critical for flowmark)
3. Full AST access (needed for tree transformations)
4. Plugin system for custom rendering

### Consequences

- **Good:** Full feature coverage from day one. No missing features blocked development.
- **Bad:** 17 behavioral differences with Python's marko discovered during testing. 50%
  of total effort spent on workarounds.
- **Unfixable:** 3 issues due to hardcoded behavior (footnote positioning, list marker
  normalization, hyphen escape removal).

### Lessons

- **Spec compliance does not guarantee behavioral equivalence.** Two parsers can both
  pass 100% of the CommonMark spec and still produce different output on real-world
  content.
- **Test with actual project inputs during evaluation, not just feature checkboxes.**
  A 30-minute cross-validation test would have revealed these differences before
  committing to comrak.
- **Have a fallback plan.** Know what you'll do if the library proves problematic.

## Handling Library Problems

### Strategy Matrix

| Problem Type | Severity | Strategy | Example |
| --- | --- | --- | --- |
| Cosmetic output diff | Low | Accept and document | List markers `-` vs `*` |
| Rare edge case | Low | Workaround with post-processing | Escape handling |
| Behavioral difference | Medium | Workaround or pre/post-process | Footnote formatting |
| Parser bug | High | Vendor/fork, or pre-processing | Fence parsing bug |
| Missing feature | Critical | Switch library or implement yourself | No footnote support |

### Pre-Processing and Post-Processing

Two patterns for working around library behavior:

**Pre-processing** (modify input before library processes it):
```rust
fn preprocess(input: &str) -> String {
    // Escape fence list markers before comrak sees them
    escape_fence_list_markers(input)
}
```

**Post-processing** (fix library output):
```rust
fn postprocess(output: &str) -> String {
    let result = fix_thematic_breaks(output);
    let result = fix_escape_handling(&result);
    let result = fix_footnote_formatting(&result);
    result
}
```

Post-processing is more common and generally safer because you're working with the
rendered text rather than modifying the parser's input.

### When to Vendor/Fork/Switch

**Vendor** (copy source into your repo) when:
- The library has a bug with a known fix (< 50 lines)
- You need it working now
- Upstream is responsive but slow

**Fork** (maintain your own version) when:
- Multiple fixes needed over time
- Upstream is unresponsive or abandoned
- You need to add features, not just fix bugs

**Switch libraries** when:
- >3 unfixable behavioral differences
- Core feature is broken or missing
- The cost of workarounds exceeds the cost of switching
- Early enough in the project to absorb the cost

## All Workarounds Implemented

### Post-Processing Workarounds (12)

| Issue | Function | Technique |
| --- | --- | --- |
| Thematic break normalization | `fix_thematic_breaks()` | Regex replace |
| Numbered heading escaping | `preserve_heading_escaping()` | Regex replace |
| Underscore escaping | `fix_underscore_escaping()` | Regex replace |
| Angle bracket escaping | `fix_angle_bracket_escaping()` | String replace |
| Hash escaping | `fix_hash_escaping()` | String replace |
| URL paren escaping | `fix_url_escaping()` | String replace |
| Footnote reference format | `fix_footnote_escaping()` | Regex replace |
| Footnote definition format | `fix_footnote_definitions()` | Regex replace |
| Quote blank lines | `fix_quote_blank_lines()` | Regex replace |
| Image link wrapping | `fix_image_link_wrapping()` | Regex replace |
| Dollar escaping | `preserve_dollar_escaping()` | Regex replace |
| Square bracket escaping | `fix_square_bracket_escaping()` | Regex replace |

### Pre-Processing Workarounds (2)

| Issue | Function | Technique |
| --- | --- | --- |
| Unreferenced footnotes | `preserve_unreferenced_footnotes()` | Add dummy refs before parsing |
| Fence parsing bug | `escape_fence_list_markers()` | Modify input before parsing |

### Unfixable Issues (Accepted)

| Issue | Root Cause | Impact | Decision |
| --- | --- | --- | --- |
| Footnote positioning | comrak hardcodes `append(fd.node)` | Medium | Accept: both valid |
| List marker normalization | comrak hardcodes `-` renderer | Low | Accept: both valid Markdown |
| Hyphen escape removal | comrak removes `\-` during parsing | Very low | Accept: rare in real use |

All workarounds use consistent `XXX:` comment marking for searchability:
```rust
/// XXX: comrak escapes underscores like `x86\_64` but Python doesn't.
/// Workaround: post-process to remove unnecessary escapes.
/// Impact: low -- cosmetic only.
fn fix_underscore_escaping(text: &str) -> String {
    // ...
}
```

## Wrapping Algorithm: A Hybrid Solution

The line wrapping problem required a hybrid library + custom approach:

**Approach:** Use comrak's `render.width` for line joining (with a large width of 999999
so comrak joins but does not wrap), then apply custom sentence-aware paragraph wrapping
via `wrap_paragraphs()` in the AST, then render with `hardbreaks = true` to preserve
the custom line breaks.

**Lesson:** Library features are building blocks, not complete solutions. The final
solution is ~240 lines of custom wrapping code that uses comrak for the parts it handles
well and implements custom logic for the rest.

## Alternative Markdown Parsers

For future ports or library switches:

| Parser | Pros | Cons | Best For |
| --- | --- | --- | --- |
| **comrak** | Full GFM, footnotes, AST access | Hardcoded rendering behaviors | Ports needing full GFM |
| **pulldown-cmark** | Fast, event-based, widely used | Footnotes optional/non-GFM, event-based (no tree AST) | Simple Markdown tools |
| **markdown-rs** | By unified/micromark author, good spec compliance, AST support | Younger ecosystem, fewer users than comrak | New projects, ports from JS/unified ecosystem |

**markdown-rs** deserves thorough evaluation for future work. It shares lineage with
remark/rehype and may provide better behavioral equivalence with web-ecosystem Markdown
tools.

## Checklist for Library Evaluation

- [ ] Identified 2+ candidates
- [ ] Created feature comparison matrix
- [ ] Ran proof-of-concept with representative inputs
- [ ] Cross-validated against Python output on full test suite
- [ ] Documented decision with rationale
- [ ] Identified known limitations and workarounds
- [ ] Defined fallback plan if choice proves unworkable
- [ ] Estimated workaround effort (budget 30-50% of porting time)
