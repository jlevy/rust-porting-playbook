# Python→Rust Initial Port Checklist

**Reference:** This checklist implements the process described in the [Python-to-Rust
Playbook](python-to-rust-playbook.md) (8-phase process) and the [Python to Rust CLI
Porting Guide](python-to-rust-porting-guide.md).
See those guides for detailed explanations, pitfalls, and patterns.

**Instructions:** Copy this document to port-checklist-initial-202Y-MM-DD.md (filling in
the date as appropriate).
Use a copy so this original template is not altered.
(But only one copy should be needed per project.)

**Related:** [Subsequent Update Checklist](port-checklist-update.md) | [Rust CLI Best
Practices](rust-cli-best-practices.md)

* * *

> **Completion Gate:** Acceptance requires exact 100% passing of every test, exact 100%
> parity with every original Python test, and byte-for-byte matching with documented
> exceptions on all comparisons (zero unexplained diffs).
> This includes:
>
> - Test output and processing results
>
> - CLI command output (help, errors, warnings, status messages)
>
> - Cross-validation across all fixtures
>
> - File outputs (no whitespace or encoding differences unless documented)
>
> Documented exceptions are acceptable when: (a) the Rust output is objectively correct
> and the Python output is a bug, (b) the difference is cosmetic and both outputs are
> valid per specification, or (c) the difference is an intentional improvement. All
> exceptions must be recorded with rationale.

## Phase 1: Assess the Original Project

*(Corresponds to [Playbook Phase 1](python-to-rust-playbook.md#phase-1-assess-the-original-project))*

- [ ] **Codebase Measurement**

  - [ ] Count lines of source code (excluding tests, docs, config)

  - [ ] Count lines of test code

  - [ ] List all modules/files and their responsibilities

  - [ ] Identify entry point(s) and public API surface

  - [ ] Note Python version and any version-specific features used

- [ ] **Dependency Inventory**

  - [ ] Create dependency table with risk ratings (Low/Medium/High)

  - [ ] Identify Rust equivalent for each Python dependency

  - [ ] Flag any dependency with no clear Rust equivalent

- [ ] **Test Coverage Assessment**

  - [ ] Run `pytest --cov` and record coverage percentages

  - [ ] Verify core library coverage >= 80% (write more tests if not)

  - [ ] Verify public API coverage >= 90%

- [ ] **Readiness Decision**

  - [ ] All critical dependencies have identified Rust equivalents

  - [ ] Test coverage meets minimum thresholds

  - [ ] No significant undocumented behavior remains

> **Completion Gate:** Proceed only when core test coverage >= 80%, all high-risk
> dependencies have Rust candidates identified, and project scope is well-understood.

## Phase 2: Research and Library Evaluation

*(Corresponds to [Playbook Phase 2](python-to-rust-playbook.md#phase-2-research-and-library-evaluation))*

- [ ] **High-Risk Dependency Evaluation**

  - [ ] For each Medium/High-risk dependency, identify 2-3 Rust candidates

  - [ ] Create feature comparison matrix for each

  - [ ] Run proof-of-concept tests with real project inputs (not just feature checkboxes)

  - [ ] Count and categorize differences (0 = ideal, 1-5 cosmetic = acceptable, 6+ =
    consider alternatives)

- [ ] **Document Decisions**

  - [ ] Record chosen library with rationale for each dependency

  - [ ] Note known limitations and fallback plans

  - [ ] Document any expected behavioral differences

> **Completion Gate:** Every dependency has a chosen Rust equivalent with documented
> rationale. High-risk dependencies validated with proof-of-concept tests.

## Phase 3: Plan the Port

*(Corresponds to [Playbook Phase 3](python-to-rust-playbook.md#phase-3-plan-the-port))*

- [ ] **Architecture Decision**

  - [ ] Choose single package vs workspace (single package recommended for most projects)

  - [ ] Define crate structure (library + binary)

- [ ] **Feature Parity Matrix**

  - [ ] List every Python feature/behavior with Rust approach and status

  - [ ] Plan module porting order (leaf modules first, CLI last)

- [ ] **Acceptance Criteria**

  - [ ] 100% of ported tests passing

  - [ ] Cross-validation against Python on all test fixtures

  - [ ] All differences documented with explicit decisions

  - [ ] CI pipeline passing

> **Completion Gate:** Concrete plan exists that specifies architecture, module order,
> and acceptance criteria. Budget allocates 40-50% of effort for library workarounds.

## Phase 4: Project Setup

*(Corresponds to [Playbook Phase 4](python-to-rust-playbook.md#phase-4-set-up-the-rust-project))*

- [ ] **Repository Structure**

  - [ ] Add Python source as submodule: `git submodule add <url> python-source`

  - [ ] Initialize and commit submodule pointer

  - [ ] Create `test-fixtures/` directory with `input/` and `expected/` subdirectories

  - [ ] Create `scripts/` directory for automation scripts

- [ ] **Workspace Configuration**

  - [ ] Create workspace `Cargo.toml` with proper package naming

    - [ ] Repository: `project-rs` (optional `-rs` suffix)

    - [ ] Library crate: `project-core` or `project` (no `-rs` suffix)

    - [ ] Binary crate: `project-cli` or `project`

  - [ ] Set edition to `2024` (Rust 1.85+) or `2021` for compatibility and declare
    `rust-version` (MSRV) explicitly

  - [ ] Configure essential metadata: authors, license, description, repository,
    keywords, categories

  - [ ] Add `readme = "README.md"`

- [ ] **Python Version Tracking** (see
  [Version Tracking Requirements](python-to-rust-porting-guide.md#version-tracking-requirements))

  - [ ] Add `[package.metadata.python_source]` section to CLI `Cargo.toml`:

    - [ ] `version` = Python project version (version tag identifies the commit)

  - [ ] Create `build.rs` to extract Python version from submodule for `--version`
    display

  - [ ] Update CLI to show both versions: `project-cli 0.1.0 (port of python-project
    0.5.5)`

  - [ ] Create `docs/version-history.md` with table tracking version correspondence:
    ```markdown
    # Version History
    
    | Rust Version | Python Version | Date       | Notes |
    |--------------|----------------|------------|-------|
    | 0.1.0        | v0.5.5         | 2024-11-02 | Initial port |
    ```

  - [ ] Add “Version Correspondence” section to README.md referencing
    `docs/version-history.md`

- [ ] **Best Practices Configuration**

  - [ ] Create `.rustfmt.toml` with edition and formatting rules

  - [ ] Configure workspace-level clippy lints in `Cargo.toml`

    - [ ] Enable `pedantic = "warn"`

    - [ ] Selectively allow false-positive lints

    - [ ] Set `unsafe_code = "forbid"` (or document exceptions)

  - [ ] Initialize `deny.toml` via `cargo deny init`

    - [ ] Configure allowed licenses

    - [ ] Set up advisory checks

    - [ ] Configure ban policies

    - [ ] Set source restrictions

- [ ] **Release Profile Optimization**

  - [ ] Set `opt-level = 3`

  - [ ] Enable `lto = true`

  - [ ] Set `codegen-units = 1`

  - [ ] Enable `strip = true`

  - [ ] Set `panic = 'abort'` (if appropriate)

> **Completion Gate:** Project builds with `cargo build`, CI skeleton is in place,
> Python submodule is committed, and test fixtures directory is populated.

## Phase 5: Dependencies & Core Setup

*(Corresponds to [Playbook Phase 4](python-to-rust-playbook.md#phase-4-set-up-the-rust-project), continued)*

- [ ] **Map and Add Core Dependencies**

  - [ ] CLI parsing: `clap = { version = "4.5", features = ["derive", "cargo"] }`

  - [ ] Error handling: `thiserror = "2"` (library errors), `color-eyre = "0.6"` or
    `anyhow = "1.0"` (application errors)

  - [ ] Logging: `tracing = "0.1"`, `tracing-subscriber = { version = "0.3", features =
    ["env-filter"] }`

  - [ ] Serialization (if needed): `serde`, `toml`, `serde_json`, `serde_yaml_ng`

  - [ ] Domain-specific libraries (markdown, file ops, etc.)

  - [ ] Testing utilities: `assert_cmd`, `predicates` (for CLI testing)

- [ ] **Test Infrastructure**

  - [ ] Copy or generate test fixtures from Python to `test-fixtures/`

  - [ ] Create `crates/project-core/tests/` directory for integration tests

  - [ ] Set up fixture loading patterns using `include_str!()` or file reads

  - [ ] Verify fixtures are committed to repository (not gitignored)

> **Completion Gate:** All dependencies compile, test fixtures load successfully,
> `cargo test` runs (even if tests are stubs).

## Phase 6: Porting Process

*(Corresponds to [Playbook Phase 5](python-to-rust-playbook.md#phase-5-port-the-code))*

- [ ] **Module-by-Module Porting** (port in dependency order: leaf modules first)

  - [ ] For each Python module:

    - [ ] Add comment header indicating source Python module

    - [ ] Port all functions with identical names

    - [ ] Match return types structurally (tuple→tuple, str→String, etc.)

    - [ ] Add function-level comments mapping to Python equivalents

    - [ ] Port inline Python tests to `#[cfg(test)]` modules

    - [ ] Watch for regex differences (anchor `^` for `re.match()` patterns)

    - [ ] Preserve string behavior (no `.trim()` unless Python does)

    - [ ] Match error handling (no `Result` if Python never raises)

    - [ ] Use Unicode escapes (`\u{2019}`) in tests for clarity

- [ ] **Critical Pitfalls Checklist** (see [Key Non-Obvious Pitfalls](python-to-rust-porting-guide.md#key-non-obvious-pitfalls))

  - [ ] Regex: Add `^` anchor to patterns used with Python's `re.match()`

  - [ ] Regex: Use `fancy-regex` if look-arounds/backreferences needed

  - [ ] Strings: Return unchanged input when Python does (no "helpful" transforms)

  - [ ] Function signatures: Match exactly (no `Option<>` or `Result<>` mismatches)

  - [ ] Arena patterns: Use closure-based API for AST nodes (comrak, pulldown-cmark)

  - [ ] Line endings: Normalize CRLF/LF in tests if not semantically significant

  - [ ] Unicode: Test with explicit escapes; assume UTF-8

  - [ ] String slicing: Use `.chars()` iterator to avoid panics on char boundaries

  - [ ] Library types: Convert explicitly (e.g., comrak's `CowStr`/`Vec<u8>` to
    `String`)

  - [ ] Dict ordering: Use `IndexMap` if Python dict iteration order matters

  - [ ] Integer overflow: Use `checked_*` or `saturating_*` for user-supplied values

- [ ] **Integration Tests**

  - [ ] Create integration tests in `crates/project-core/tests/`

  - [ ] Use `include_str!()` for embedding fixtures

  - [ ] Test exact output matching with documented exceptions

  - [ ] Verify all original Python tests are replicated 1:1

  - [ ] Add Rust-specific unit tests for development/edge cases (beyond Python parity)

> **Completion Gate:** All ported unit tests pass. Integration tests confirm output
> matches expected fixtures (with documented exceptions only).

## Phase 7: Handle Library Differences

*(Corresponds to [Playbook Phase 6](python-to-rust-playbook.md#phase-6-handle-library-differences))*

- [ ] **Cross-Validation and Failure Categorization**

  - [ ] Run both Python and Rust against all test fixtures

  - [ ] Categorize every difference: porting bug / library difference / Python bug /
    intentional improvement

  - [ ] Fix porting bugs immediately

- [ ] **Library Difference Workarounds** (try in order)

  - [ ] Post-processing: fix library output after processing (safest, most common)

  - [ ] Pre-processing: modify input before library (use sparingly)

  - [ ] Accept and document: when difference is cosmetic and both outputs are valid

  - [ ] Vendor/fork: when library has a bug with a known fix < 50 lines

  - [ ] Switch libraries: when > 3 unfixable differences or a core feature is broken

- [ ] **Workaround Documentation**

  - [ ] Every workaround has a `HACK:` comment explaining what, why, and impact level

  - [ ] Items needing future resolution marked with `FIXME:` comments

  - [ ] Searchable via `grep -rn "HACK:\|FIXME:" src/`

- [ ] **Python Bug Handling**

  - [ ] Confirmed bugs documented (run Python code manually to verify)

  - [ ] Decision recorded for each: replicate for parity, or fix in Rust

  - [ ] Intentional divergences documented with rationale

> **Completion Gate:** All cross-validation differences are categorized and resolved.
> Remaining differences are documented as intentional divergences with rationale.

## Phase 8: CLI Implementation

- [ ] **CLI Parity Requirements**

  - [ ] Match all flag names (long and short forms)

  - [ ] Match default values exactly

  - [ ] Replicate help text and descriptions

  - [ ] Maintain identical exit codes (0 success, 1 errors, 2 usage)

  - [ ] Support stdin/stdout piping

  - [ ] Match or improve error messages (keep consistent style)

  - [ ] Customize clap’s `help_template` to mirror Python’s layout

  - [ ] Disable colors in CI for stable output

  - [ ] Force fixed terminal width for stable text wrapping

- [ ] **CLI Validation**

  - [ ] Generate help text: `python-source/cli.py --help > python-help.txt`

  - [ ] Generate Rust help: `cargo run -- --help > rust-help.txt`

  - [ ] Run: `diff python-help.txt rust-help.txt` (expect zero unexplained diffs)

  - [ ] Test all flag combinations match Python behavior

  - [ ] **Completion Gate: Zero unexplained diffs on all CLI output**

    - [ ] Verify error messages match (byte-for-byte with documented exceptions)

    - [ ] Verify status/warning messages match (byte-for-byte with documented exceptions)

    - [ ] Verify exit codes match (0 success, 1 errors, 2 usage)

## Phase 9: Testing & Validation

*(Corresponds to [Playbook Phase 7](python-to-rust-playbook.md#phase-7-finalize-and-validate))*

- [ ] **Test Coverage**

  - [ ] Achieve ≥90% line coverage in core library

  - [ ] Achieve 100% coverage of public API

  - [ ] Add property tests (via `proptest`) for algorithmic correctness

  - [ ] Run `cargo test --all` (all tests pass)

  - [ ] Run `cargo test --all-features --locked` (with feature combinations)

  - [ ] Run `cargo test --no-default-features --locked` (library-only builds)

  - [ ] Run `cargo test --doc` (doc tests pass)

- [ ] **Cross-Validation Script** *(Completion Gate: Zero unexplained diffs across all
  fixtures)*

  - [ ] Create `scripts/validate-parity.sh` (template in porting guide)

  - [ ] Build release: `cargo build --release`

  - [ ] Run validation across all fixtures

  - [ ] Verify zero unexplained diffs between Python and Rust output (byte-for-byte
    with documented exceptions)

  - [ ] Verify all file outputs match (no whitespace/encoding differences unless
    documented)

  - [ ] Document any remaining differences with rationale and resolve before proceeding

- [ ] **Quality Checks**

  - [ ] `cargo fmt --all -- --check` (zero diffs)

  - [ ] `cargo clippy --all-targets --all-features -- -D warnings` (zero warnings)

  - [ ] `cargo audit` (no vulnerabilities)

  - [ ] `cargo deny check` (licenses, advisories, bans, sources all pass)

  - [ ] `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` (documentation builds without
    warnings or errors)

> **Completion Gate:** All tests pass, cross-validation shows zero unexplained diffs,
> all quality checks pass.

## Phase 10: Performance & Optimization

- [ ] **Performance Targets**

  - [ ] Binary size < 10MB (release build, stripped; use `cargo-bloat` to identify size
    issues)

  - [ ] Processing speed 10-100x faster than Python (benchmark critical paths, profile
    with `cargo flamegraph` or `perf` if needed)

  - [ ] Startup time < 50ms

- [ ] **Optimization Techniques Applied**

  - [ ] Use `&str` over `String` where possible

  - [ ] Minimize allocations in hot paths

  - [ ] Use lazy static regex patterns (`std::sync::LazyLock`)

  - [ ] Consider `rayon` for parallel processing if applicable

## Phase 11: Documentation

- [ ] **Code Documentation**

  - [ ] Add `///` doc comments to all public APIs

  - [ ] Add `//!` module-level documentation

  - [ ] Include examples in doc comments

  - [ ] Verify documentation builds: `cargo doc --no-deps --open`

- [ ] **User Documentation**

  - [ ] Create/update `README.md` with quick start, installation, basic usage

  - [ ] Create `CHANGELOG.md` (use keep-a-changelog format)

  - [ ] Ensure `LICENSE` file present

  - [ ] Document any intentional divergences from Python version

  - [ ] Create `docs/python-sync-log.md` for tracking updates

## Phase 12: CI/CD Setup

- [ ] **Essential CI Checks (Tier 1)**

  - [ ] `cargo fmt --all -- --check`

  - [ ] `cargo clippy --all-targets --all-features -- -D warnings`

  - [ ] `cargo test --all-features --locked`

  - [ ] `cargo test --no-default-features --locked`

  - [ ] `cargo audit` (or use `rustsec/audit-check@v2` action)

- [ ] **Pre-Release Checks (Tier 2)**

  - [ ] `cargo deny check`

  - [ ] `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps`

  - [ ] MSRV compliance test (test with declared `rust-version`)

  - [ ] Cross-platform build matrix (Linux, macOS, Windows)

- [ ] **Optional Periodic Checks (Tier 3)**

  - [ ] `cargo +nightly udeps --all-targets` (unused dependencies)

  - [ ] `cargo geiger` (unsafe code audit)

  - [ ] `cargo outdated` (dependency updates)

- [ ] **GitHub Actions Workflow**

  - [ ] Create `.github/workflows/ci.yml` with all checks

  - [ ] Configure matrix builds for multiple platforms

  - [ ] Set up caching for faster builds

  - [ ] Add MSRV testing job

## Phase 13: Scripts & Automation

*(Corresponds to [Playbook Phase 8](python-to-rust-playbook.md#phase-8-ongoing-synchronization))*

- [ ] **Create Sync Script** (for ongoing Python synchronization)

  - [ ] Create `scripts/sync-from-python.sh` (template in porting guide)

  - [ ] Make executable: `chmod +x scripts/sync-from-python.sh`

  - [ ] Test script execution

  - [ ] Document usage in README

- [ ] **Verify Validation Script** (created in Phase 9)

  - [ ] `scripts/validate-parity.sh` exists and is executable

  - [ ] Runs successfully with current fixtures

  - [ ] Correctly detects intentional diff when introduced

## Final Acceptance Criteria

> **Completion Gate:** ALL mandatory items below must be satisfied.
> Documented exceptions require recorded rationale (see top-level gate criteria).

### Porting Parity Requirements (Mandatory)

- [ ] **Code Structure and Mapping**

  - [ ] All Python tests replicated with exact 1:1 behavioral parity

  - [ ] Additional Rust-specific unit tests present (fast feedback, edge cases)

  - [ ] `include_str!()` used for test fixtures

  - [ ] Clear module mapping maintained (Python → Rust)

  - [ ] Comments at top of each module indicating source Python module

  - [ ] Comments at top of every major function indicating source Python function

### CLI Parity (Mandatory)

- [ ] **Interface Compatibility** *(Zero unexplained diffs required)*

  - [ ] Exact flag names, short flags, defaults match

  - [ ] Help text matches (zero diff on `--help` output, with documented exceptions)

  - [ ] Exit codes match exactly (0 success, 1 errors, 2 usage)

  - [ ] stdin/stdout piping works identically

- [ ] **Output Compatibility** *(Byte-for-byte matching with documented exceptions)*

  - [ ] Error messages match exactly (or improved consistently)

  - [ ] Warning messages match exactly

  - [ ] Status messages match exactly

  - [ ] All command output identical to Python (not just processing results)

### Test Parity (Mandatory)

- [ ] **Test Execution** *(100% pass rate required)*

  - [ ] 100% of Rust tests pass (unit, integration, property)

  - [ ] All Python CLI flags, features, tests ported and passing

  - [ ] Every original Python test replicated with exact behavior

  - [ ] Edge cases handled identically

- [ ] **Output Validation** *(Zero unexplained diffs required)*

  - [ ] All text comparisons are byte-for-byte matches (with documented exceptions)

  - [ ] All binary comparisons are byte-for-byte matches (with documented exceptions)

  - [ ] Processing results identical to Python output

  - [ ] File outputs match (no whitespace/encoding differences unless documented)

### Cross-Validation (Mandatory)

- [ ] **Fixture Testing** *(Zero unexplained diffs required)*

  - [ ] Cross-validation script shows zero unexplained diffs across all fixtures

  - [ ] All input fixtures processed identically

  - [ ] All output fixtures match (byte-for-byte with documented exceptions)

  - [ ] No encoding, line ending, or whitespace differences (unless documented)

### Performance Targets

- [ ] **Binary Metrics**

  - [ ] Binary size < 10MB (release build, stripped)

  - [ ] Startup time < 50ms

- [ ] **Runtime Performance**

  - [ ] Processing speed >= 10x faster than Python (benchmark critical paths; 50-100x
    is typical for well-optimized ports)

  - [ ] No performance regressions in hot paths

### Quality Metrics (Mandatory)

- [ ] **Code Quality** *(Zero warnings/errors required)*

  - [ ] Zero clippy warnings (`cargo clippy --all-targets --all-features -- -D
    warnings`)

  - [ ] Zero format diffs (`cargo fmt --all -- --check`)

  - [ ] Documentation builds without errors (`cargo doc --no-deps`)

- [ ] **Test Coverage** *(Minimum thresholds required)*

  - [ ] ≥90% line coverage in core library

  - [ ] 100% coverage of public API

  - [ ] All public APIs documented with `///` comments

- [ ] **Security & Dependencies** *(All checks must pass)*

  - [ ] `cargo audit` passes (no vulnerabilities)

  - [ ] `cargo deny check` passes (licenses, advisories, bans, sources)

  - [ ] No unsafe code (or documented exceptions)

### Release Preparation

- [ ] **Versioning and Documentation**

  - [ ] Version set appropriately in `Cargo.toml` (likely `0.1.0` for initial)

  - [ ] `CHANGELOG.md` populated with initial release notes

  - [ ] `README.md` complete with installation and usage

  - [ ] Any intentional divergences from Python documented

- [ ] **Git and Publishing**

  - [ ] Git repository tagged (`v0.1.0`)

  - [ ] Ready for `cargo publish --dry-run` (passes without errors)

  - [ ] CI/CD pipeline passes all checks

### Documented Exceptions Log

Record all byte-for-byte matching exceptions here with rationale:

| # | Location | Description | Category | Rationale |
|---|----------|-------------|----------|-----------|
| 1 | *(example: help text line wrapping)* | *(clap wraps at 80 cols vs argparse at 79)* | *(cosmetic)* | *(both valid, difference is 1 char)* |

Categories: **Python bug** (Rust is correct), **cosmetic** (both outputs valid),
**intentional improvement** (documented enhancement)

### Case Study Observations (Optional)

If conducting this port as a case study to improve the playbook:

- [ ] Observations recorded for each phase using the
  [observation template](case-study-observations-template.md)
- [ ] Final metrics summary completed (LOC, tests, time, dependency comparison)
- [ ] Playbook issues triaged using the
  [improvement triage template](case-study-improvement-triage-template.md)
- [ ] Case study artifacts placed in `case-studies/<project-name>/`

See the [meta-playbook](meta-improving-this-playbook.md) for the full process.

**Port is complete when ALL mandatory items above are checked.
Zero unexplained failures accepted. All exceptions must be documented with rationale.**
