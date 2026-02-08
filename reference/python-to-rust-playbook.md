# Python-to-Rust Playbook

A step-by-step process for porting a Python application to Rust. Designed for AI
coding agents with human oversight at key decision points. Built from the experience
of porting [flowmark](https://github.com/jlevy/flowmark) and validated against the
full knowledge base.

**Scope:** Any Python application with a test suite. Emphasis on CLI tools but the
process applies to libraries, services, and other application types.

**Time estimate:** For a well-tested Python CLI of ~1,000 lines, expect 5-8 hours of
agent time with 2-3 human review points. Half of that time will be spent on library
workarounds and cross-validation, not initial implementation.

**Key principle:** Tests are the specification. The Python test suite defines what the
Rust port must do. Without tests, porting is guesswork. With them, 100% passing tests
equals correctness by definition.

For detailed reference on any step, see the companion docs listed in the
[README](../README.md).

---

## Phase 1: Assess the Original Project

**Goal:** Understand what you're porting and whether it's ready.

**Time:** 15-30 minutes.

### 1.1 Measure the codebase

- Count lines of source code (excluding tests, docs, config)
- Count lines of test code
- List all modules/files and their responsibilities
- Identify the entry point(s) and public API surface
- Note the Python version and any version-specific features used

### 1.2 Inventory dependencies

Create a dependency table:

| Python Package | Purpose | Rust Equivalent | Risk |
| --- | --- | --- | --- |
| argparse/click/typer | CLI parsing | clap | Low |
| pytest | Testing | cargo test | Low |
| pyyaml | YAML parsing | serde_yaml | Low |
| marko | Markdown parsing | comrak / pulldown-cmark | **High** |

**Risk levels:**
- **Low:** Well-known Rust equivalent with similar API (regex, serde, clap)
- **Medium:** Rust equivalent exists but behavior may differ
- **High:** Core dependency where behavioral equivalence is critical and not guaranteed

### 1.3 Assess test coverage

```bash
pytest --cov=myproject --cov-report=term-missing
```

**Coverage thresholds for porting readiness:**

| Component | Minimum | Ideal |
| --- | --- | --- |
| Core library | 80% | 90%+ |
| Public API | 90% | 100% |
| CLI wrapper | 60% | 80%+ |
| Error paths | 50% | 70%+ |

If coverage is below these thresholds, **stop and write more tests first.** Every
untested code path is a potential bug in the Rust version that you won't catch. Test
coverage investment before porting pays for itself many times over.

### 1.4 Identify areas to clarify

Look for:
- **Implicit behavior:** Things the code does that aren't tested or documented
- **Ambiguous edge cases:** What happens with empty input? Unicode? Very large files?
- **Known bugs:** Existing issues that you'll need to decide whether to replicate
- **Platform-specific behavior:** File paths, line endings, locale handling

Write tests for anything ambiguous. The act of writing exact-match tests often reveals
bugs in the original -- this is expected and valuable.

### 1.5 Decision: Is this project ready to port?

**Proceed if:**
- Core test coverage is >= 80%
- All critical dependencies have identified Rust equivalents
- No high-risk dependency has more than one candidate to evaluate
- The project scope is well-understood

**Pause and prepare if:**
- Test coverage is below thresholds (write more tests first)
- A critical dependency has no clear Rust equivalent (research more)
- The project has significant undocumented behavior

---

## Phase 2: Research and Library Evaluation

**Goal:** Choose all Rust dependencies, especially the high-risk ones. This phase
determines 50% of total porting effort.

**Time:** 30-60 minutes.

### 2.1 Evaluate candidates for every high-risk dependency

For each dependency rated Medium or High risk:

1. **Identify 2-3 candidates** (search crates.io, lib.rs, ask for recommendations)

2. **Create a feature matrix:**

   | Feature | Python Lib | Candidate A | Candidate B |
   | --- | --- | --- | --- |
   | Core feature 1 | Y | Y | Y |
   | Core feature 2 | Y | Y | N |
   | Feature you need | Y | Partial | Y |
   | AST/API access | Y | Full | Event-only |

3. **Run proof-of-concept tests** (5-10 representative inputs from your actual project):

   ```bash
   # Process with candidate library, diff against Python output
   for input in test-fixtures/input/*; do
       candidate_process "$input" > candidate_out
       diff candidate_out "test-fixtures/expected/$(basename $input)"
   done
   ```

4. **Count and categorize differences:**
   - 0 diffs: Ideal -- proceed
   - 1-5 cosmetic diffs: Acceptable if workaround-able
   - 6+ diffs or structural diffs: Consider alternatives

5. **Document the decision** with rationale, known limitations, and fallback plan

### 2.2 Evaluation criteria

**Tier 1 (Must-Have):**
- Spec compliance (same standard as Python lib)
- Feature coverage (all features your project uses)
- API capability (can produce the same outputs)
- Active maintenance (commits in last 6 months, issues responded to)

**Tier 2 (Differentiators):**
- Output fidelity (byte-for-byte match with Python)
- Customization (hooks, plugins, configuration)
- Performance and compile time impact

### 2.3 Critical lesson: spec compliance is a false signal

Two libraries can both pass 100% of a specification's test suite and still produce
different output on real-world inputs. The flowmark port discovered 15 behavioral
differences between two spec-compliant Markdown parsers. **Always test with your actual
inputs, not just feature checkboxes.**

### 2.4 Write a best-practices survey (optional but recommended)

Before writing any code, spend 30 minutes surveying the Rust ecosystem for your
application type. Document: recommended libraries, project setup patterns, CI
configuration, release workflow. This prevents rework from poor initial choices.

See `tbd guidelines rust-project-setup` and
[rust-cli-best-practices.md](rust-cli-best-practices.md) for CLI projects.

---

## Phase 3: Plan the Port

**Goal:** Create a concrete plan that an agent can execute without ambiguity.

**Time:** 15-30 minutes.

### 3.1 Define the architecture

**Single package vs workspace:**
- **Single package** (recommended for most projects): One `Cargo.toml` with
  feature-gated binaries. Simpler build, simpler CI, fewer path issues.
- **Workspace:** Only when you have 3+ crates with independent versioning or very
  different dependency sets. You can always split later.

**For CLI tools:** Use the lib+bin feature-gate pattern:
```toml
[lib]
name = "myproject"
path = "src/lib.rs"

[[bin]]
name = "myproject"
path = "src/main.rs"
required-features = ["cli"]

[features]
default = ["cli"]
cli = ["clap", "color-eyre", "tracing"]
```

### 3.2 Create a feature parity matrix

List every feature/behavior in Python and map to Rust:

| Python Feature | Module | Rust Approach | Status |
| --- | --- | --- | --- |
| Sentence splitting | text_utils.py | regex + unicode-segmentation | Planned |
| Paragraph wrapping | formatter.py | Custom + comrak render.width | Planned |
| CLI --auto flag | cli.py | clap derive | Planned |
| YAML config loading | config.py | serde_yaml | Planned |

### 3.3 Plan the module porting order

Port in dependency order -- leaf modules first:

1. **Core data types** (Config, Error, constants)
2. **Leaf modules** (utilities, text processing, pure functions)
3. **Integration modules** (modules that combine leaf modules)
4. **CLI layer** (thin wrapper, port last)

### 3.4 Define acceptance criteria

- 100% of ported tests passing
- Cross-validation against Python on all test fixtures
- All differences documented with explicit decisions (accepted / fixed / workaround)
- CI pipeline passing (format, lint, test, audit)

### 3.5 Budget for workarounds

Based on the flowmark experience and general patterns:

| Phase | % of Total Effort |
| --- | --- |
| Research + planning | 15-20% |
| Implementation | 35-40% |
| Bug-fixing + cross-validation | 40-50% |

The fix phase is not waste -- it's where the port achieves production quality. Plan for
it explicitly rather than treating it as contingency.

---

## Phase 4: Set Up the Rust Project

**Goal:** A fully configured project that builds and has CI before any porting begins.

**Time:** 15-30 minutes.

### 4.1 Create the project

```bash
cargo init myproject-rs
cd myproject-rs
```

### 4.2 Configure Cargo.toml

Essential fields:
```toml
[package]
name = "myproject"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"
description = "Brief description"
repository = "https://github.com/user/myproject-rs"
```

Add lint configuration:
```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
missing_errors_doc = "allow"
missing_panics_doc = "allow"
module_name_repetitions = "allow"
must_use_candidate = "allow"

[lints.rust]
unsafe_code = "forbid"
```

See `tbd guidelines rust-project-setup` for complete configuration including release
profile, deny.toml, release.toml, and justfile.

### 4.3 Include the Python source as a submodule

```bash
git submodule add https://github.com/org/python-project.git python-repo
```

This lets agents read the Python source directly and provides an exact commit reference
for version correspondence.

### 4.4 Set up test fixtures

```
test-fixtures/
├── input/           # Shared inputs (copy from Python)
└── expected/        # Expected outputs (generated by Python)
```

Generate expected outputs from the Python implementation:
```bash
cd python-repo
for input in ../test-fixtures/input/*; do
    python -m myproject "$input" > "../test-fixtures/expected/$(basename $input)"
done
```

### 4.5 Set up CI

Create GitHub Actions with 7 parallel jobs: format, clippy, test, MSRV, audit, deny,
docs. See `tbd guidelines rust-project-setup` for the complete workflow.

### 4.6 Track version correspondence

Add to Cargo.toml:
```toml
[package.metadata.python_source]
version = "0.5.5"  # Python version this port is based on
```

---

## Phase 5: Port the Code

**Goal:** A working Rust implementation with all tests passing.

**Time:** 2-4 hours for a ~1,000-line Python project.

### 5.1 Port tests first

For each module, port its tests before (or alongside) the implementation. This gives
immediate feedback and makes progress measurable.

Progress tracking example: 0/45 → 12/45 → 45/45 → 87/87 → 111/111.

### 5.2 Per-module workflow

For each module, in dependency order:

1. **Read the Python source** and understand what it does
2. **Create the Rust file** with a mapping header comment:
   ```rust
   //! Ported from Python: myproject/text_utils.py
   ```
3. **Port the tests** for this module
4. **Implement** until all tests pass
5. **Run cross-validation** against Python output

### 5.3 Maintain traceability

- Keep function names aligned with Python where reasonable
- Add mapping comments for non-obvious translations:
  ```rust
  // Python: re.match(pattern, text) -- note: anchored at start
  if regex.is_match(text) { ... }
  ```
- Mark every workaround with `XXX:` comments:
  ```rust
  /// XXX: comrak escapes underscores but Python doesn't.
  /// Workaround: post-process to remove unnecessary escapes.
  fn fix_underscore_escaping(text: &str) -> String { ... }
  ```

### 5.4 Key pitfalls to watch for

**Regex anchoring:** Python's `re.match()` anchors at start; Rust's `is_match()` does
not. Add `^` to patterns translated from `re.match()`.

**String handling:** Don't add `.trim()` unless Python does. Whitespace preservation
matters for text formatters, config parsers, etc.

**Arena/lifetime patterns:** When a library uses arena allocation (like comrak), use
the closure pattern:
```rust
pub fn with_ast<F, R>(text: &str, f: F) -> Result<R>
where F: for<'a> FnOnce(&'a AstNode<'a>) -> Result<R>
```

**Error types:** Map Python exceptions to a Rust error enum with `thiserror`. Don't use
`unwrap()` in library code.

**Unicode:** Use `\u{XXXX}` for Unicode escapes (not `\uXXXX`). Consider
`unicode-segmentation` for grapheme-aware text processing.

---

## Phase 6: Handle Library Differences

**Goal:** Systematic resolution of all behavioral differences between Python and Rust
libraries.

**Time:** 2-4 hours (often 40-50% of total effort).

### 6.1 Run cross-validation and categorize failures

Run both implementations against all test fixtures and categorize every difference:

| Category | Action |
| --- | --- |
| **Porting bug** | Fix immediately (your code is wrong) |
| **Library difference** | Evaluate: workaround or accept? |
| **Python bug** | Decide: replicate for parity or fix in Rust? |
| **Intentional improvement** | Document and accept |

### 6.2 Workaround strategy

For each library difference, try in order:

1. **Post-processing** (fix library output): Safer, most common. Build a pipeline of
   `fix_*` functions applied after the library processes input.

2. **Pre-processing** (modify input before library): Use sparingly. Riskier because
   you're modifying input without full parsing context.

3. **Accept and document:** When the difference is cosmetic and both outputs are valid.

4. **Vendor/fork:** When the library has a bug with a known fix < 50 lines.

5. **Switch libraries:** When there are > 3 unfixable differences or a core feature is
   broken.

### 6.3 Track workarounds systematically

Every workaround gets a consistent `XXX:` comment with:
- What the difference is
- Why it exists (library behavior)
- Impact level (cosmetic / functional / critical)

This creates a searchable inventory: `grep -n "XXX:" src/`

### 6.4 Handling bugs in the original

Porting frequently reveals bugs in the original because test writing forces exact
specification of behavior. When you find one:

1. Confirm it's a bug (run the Python code manually)
2. Write a failing test in the Python repo
3. File a bug/PR upstream
4. Decide: replicate the bug for byte-for-byte parity, or fix it in Rust
5. If fixing: document the intentional divergence and add a test proving Rust is correct
6. Track for sync: when Python fixes the bug, remove the divergence note

### 6.5 Decision point: library switch

**Switch libraries if:**
- More than 3 unfixable behavioral differences
- A core feature is broken or missing
- The cost of workarounds exceeds the cost of switching
- You're early enough in the port to absorb the cost

**Don't switch if:**
- Differences are cosmetic and both outputs are valid
- Workarounds are isolated and testable
- You're past 50% implementation

---

## Phase 7: Finalize and Validate

**Goal:** Production-ready port with full CI, documentation, and cross-validation.

**Time:** 30-60 minutes.

### 7.1 Cross-validation gate

Write a cross-validation script that:
1. Builds the Rust binary
2. Runs both Python and Rust against all test fixtures
3. Diffs the outputs
4. Reports pass/fail per fixture

**The port is not done until cross-validation passes** (with documented exceptions for
intentional divergences).

### 7.2 CLI parity (for CLI tools)

If porting a CLI tool, verify:
- `--help` output matches Python's format and content
- All flags and arguments work identically
- Exit codes match (0 = success, 1 = error, 2 = usage error)
- stdin/stdout/stderr routing matches
- Error messages are comparable

For argument mapping from Python to Rust:
- `argparse` / `click` / `typer` all map to `clap` with derive API
- Enable `cargo` feature for automatic `--version` from Cargo.toml
- Use `color-eyre` for rich error display

See `tbd guidelines python-to-rust-cli-porting` for detailed argument mapping tables.

### 7.3 CI verification

All CI jobs must pass:
- `cargo fmt --check`
- `cargo clippy -- -D warnings`
- `cargo test --all-features --locked`
- `cargo test --no-default-features --locked`
- `cargo audit`
- `cargo deny check`
- `cargo doc` with `-D warnings`
- MSRV check against declared `rust-version`

### 7.4 Documentation

- README with installation, usage, and comparison to Python version
- `--version` output showing both Rust and Python source versions
- CHANGELOG documenting the port
- All intentional divergences from Python documented

### 7.5 Release configuration

Set up `release.toml` for cargo-release and a release CI workflow for cross-platform
binary builds. See `tbd guidelines rust-project-setup` for templates.

---

## Phase 8: Ongoing Synchronization

**Goal:** Keep the Rust port in sync as the Python version evolves.

### 8.1 When Python updates

1. Update the git submodule to the new Python version
2. Regenerate expected test fixtures from Python
3. Run cross-validation to find new differences
4. Categorize each change: bug fix / new feature / test addition / refactor
5. Port changes to Rust, running tests after each change
6. Update version correspondence in Cargo.toml metadata

### 8.2 Sync tracking

Maintain a sync log documenting each update:

```markdown
## Sync: Python 0.5.5 → 0.5.6 (2026-02-15)
- Bug fix: heading spacing (ported, test added)
- New feature: --json output (ported)
- Refactor: split utils module (not ported, Rust structure differs)
- Intentional divergence: list spacing (maintained)
```

### 8.3 Divergence management

Over time, intentional divergences accumulate. Track them:
- Divergences where Rust is better (keep)
- Divergences forced by library differences (revisit if library updates)
- Divergences from Python bugs (remove when Python fixes them)

---

## Quick Reference: Effort Allocation

| Phase | Time (1K-line project) | % of Total |
| --- | --- | --- |
| 1. Assess | 15-30 min | 5% |
| 2. Research | 30-60 min | 10% |
| 3. Plan | 15-30 min | 5% |
| 4. Set up | 15-30 min | 5% |
| 5. Port | 2-4 hours | 35% |
| 6. Library fixes | 2-4 hours | 35% |
| 7. Finalize | 30-60 min | 10% |
| **Total** | **5-8 hours** | **100%** |

Phase 6 (library fixes) is consistently the largest time sink. Budget for it explicitly.
If your library evaluation in Phase 2 is thorough, Phase 6 shrinks significantly.

## Checklist Summary

```
ASSESS
☐ Measure codebase (lines, modules, dependencies)
☐ Inventory dependencies with risk ratings
☐ Measure test coverage (>= 80% core before proceeding)
☐ Identify ambiguous behavior and write tests for it
☐ Decision: ready to port?

RESEARCH
☐ Evaluate 2-3 candidates for each high-risk dependency
☐ Create feature comparison matrices
☐ Run proof-of-concept with real inputs (not just feature checkboxes)
☐ Document decisions with rationale and fallback plans

PLAN
☐ Choose architecture (single package + feature flags recommended)
☐ Create feature parity matrix
☐ Plan module porting order (leaf-first)
☐ Define acceptance criteria
☐ Budget 40-50% of time for workarounds

SET UP
☐ Create project with Cargo.toml, lints, release profile
☐ Add Python source as git submodule
☐ Set up test fixtures (input/ and expected/)
☐ Set up CI (7 jobs: fmt, clippy, test, msrv, audit, deny, docs)
☐ Create justfile with check/fix/precommit targets

PORT
☐ Port tests first, then implementation
☐ Port modules in dependency order (leaf → integration → CLI)
☐ Maintain traceability (mapping comments, function name parity)
☐ Mark all workarounds with XXX: comments
☐ Run cross-validation continuously

LIBRARY FIXES
☐ Categorize all failures (porting bug / library diff / Python bug)
☐ Build post-processing pipeline for library differences
☐ Accept unfixable differences and document them
☐ Decide on Python bugs (replicate vs fix)
☐ Evaluate: switch libraries if > 3 unfixable differences

FINALIZE
☐ Cross-validation passes on all fixtures
☐ CLI parity verified (if applicable)
☐ All CI jobs passing
☐ Documentation complete (README, --version, CHANGELOG)
☐ Release workflow configured
```
