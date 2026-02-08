# Python→Rust Initial Port Checklist

**Reference:** This checklist implements the process described in [Python to Rust CLI
Porting Guide](python-to-rust-porting-guide.md).
See that guide for detailed explanations, pitfalls, and patterns.

**Instructions:** Copy this document to port-checklist-initial-202Y-MM-DD.md (filling in
the date as appropriate).
Use a copy so this original template is not altered.
(But only one copy should be needed per project.)

**Related:** [Subsequent Update Checklist](port-checklist-update.md) | [Rust CLI Best
Practices](rust-cli-best-practices.md)

* * *

> **Completion Gate:** Acceptance requires exact 100% passing of every test, exact 100%
> parity with every original Python test, and exact byte-for-byte matching on all
> comparisons (zero diffs).
> This includes:
> 
> - Test output and processing results
>
> - CLI command output (help, errors, warnings, status messages)
>
> - Cross-validation across all fixtures
>
> - File outputs (no whitespace or encoding differences unless documented)

## Phase 1: Project Setup

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

## Phase 2: Dependencies & Core Setup

- [ ] **Map and Add Core Dependencies**

  - [ ] CLI parsing: `clap = { version = "4.5", features = ["derive", "cargo"] }`

  - [ ] Error handling: `color-eyre = "0.6"` or `anyhow = "1.0"`

  - [ ] Logging: `tracing = "0.1"`, `tracing-subscriber = { version = "0.3", features =
    ["env-filter"] }`

  - [ ] Serialization (if needed): `serde`, `toml`, `serde_json`, `serde_yaml`

  - [ ] Domain-specific libraries (markdown, file ops, etc.)

  - [ ] Testing utilities: `assert_cmd`, `predicates` (for CLI testing)

- [ ] **Test Infrastructure**

  - [ ] Copy or generate test fixtures from Python to `test-fixtures/`

  - [ ] Create `crates/project-core/tests/` directory for integration tests

  - [ ] Set up fixture loading patterns using `include_str!()` or file reads

  - [ ] Verify fixtures are committed to repository (not gitignored)

## Phase 3: Porting Process

- [ ] **Module-by-Module Porting**

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

- [ ] **Critical Pitfalls Checklist**

  - [ ] Regex: Add `^` anchor to patterns used with Python’s `re.match()`

  - [ ] Regex: Use `fancy-regex` if look-arounds/backreferences needed

  - [ ] Strings: Return unchanged input when Python does (no “helpful” transforms)

  - [ ] Function signatures: Match exactly (no `Option<>` or `Result<>` mismatches)

  - [ ] Arena patterns: Use closure-based API for AST nodes (comrak, pulldown-cmark)

  - [ ] Line endings: Normalize CRLF/LF in tests if not semantically significant

  - [ ] Unicode: Test with explicit escapes; assume UTF-8

  - [ ] String slicing: Use `.chars()` iterator to avoid panics on char boundaries

  - [ ] Library types: Convert explicitly (e.g., comrak’s `CowStr`/`Vec<u8>` to
    `String`)

- [ ] **Integration Tests**

  - [ ] Create integration tests in `crates/project-core/tests/`

  - [ ] Use `include_str!()` for embedding fixtures

  - [ ] Test exact byte-for-byte output matching

  - [ ] Verify all original Python tests are replicated 1:1

  - [ ] Add Rust-specific unit tests for development/edge cases (beyond Python parity)

## Phase 4: CLI Implementation

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

  - [ ] Run: `diff python-help.txt rust-help.txt` (expect zero diffs, byte-for-byte)

  - [ ] Test all flag combinations match Python behavior

  - [ ] **Completion Gate: Zero diffs on all CLI output**

    - [ ] Verify error messages match exactly (byte-for-byte)

    - [ ] Verify status/warning messages match exactly

    - [ ] Verify exit codes match (0 success, 1 errors, 2 usage)

## Phase 5: Testing & Validation

- [ ] **Test Coverage**

  - [ ] Achieve ≥90% line coverage in core library

  - [ ] Achieve 100% coverage of public API

  - [ ] Add property tests (via `proptest`) for algorithmic correctness

  - [ ] Run `cargo test --all` (all tests pass)

  - [ ] Run `cargo test --all-features` (with feature combinations)

  - [ ] Run `cargo test --doc` (doc tests pass)

- [ ] **Cross-Validation Script** *(Completion Gate: Zero diffs across all fixtures)*

  - [ ] Create `scripts/validate-parity.sh` (template in porting guide)

  - [ ] Build release: `cargo build --release`

  - [ ] Run validation across all fixtures

  - [ ] Verify zero diffs between Python and Rust output (byte-for-byte)

  - [ ] Verify all file outputs match exactly (no whitespace/encoding differences)

  - [ ] Document any failures and resolve before proceeding

- [ ] **Quality Checks**

  - [ ] `cargo fmt --all -- --check` (zero diffs)

  - [ ] `cargo clippy --all-targets --all-features -- -D warnings` (zero warnings)

  - [ ] `cargo audit` (no vulnerabilities)

  - [ ] `cargo deny check` (licenses, advisories, bans, sources all pass)

  - [ ] `cargo doc --no-deps` (documentation builds without errors)

## Phase 6: Performance & Optimization

- [ ] **Performance Targets**

  - [ ] Binary size < 10MB (release build, stripped; ue `cargo-bloat` to identify size
    issues)

  - [ ] Processing speed >10X faster than Python (benchmark critical paths, profile with
    `cargo flamegraph` or `perf` if needed)

  - [ ] Startup time < 50ms

- [ ] **Optimization Techniques Applied**

  - [ ] Use `&str` over `String` where possible

  - [ ] Minimize allocations in hot paths

  - [ ] Use lazy static regex patterns (`once_cell::sync::Lazy`)

  - [ ] Consider `rayon` for parallel processing if applicable

## Phase 7: Documentation

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

## Phase 8: CI/CD Setup

- [ ] **Essential CI Checks (Tier 1)**

  - [ ] `cargo fmt --all -- --check`

  - [ ] `cargo clippy --all-targets --all-features -- -D warnings`

  - [ ] `cargo test --all`

  - [ ] `cargo audit` (or use `rustsec/audit-check@v2` action)

- [ ] **Pre-Release Checks (Tier 2)**

  - [ ] `cargo deny check`

  - [ ] `cargo doc --no-deps`

  - [ ] MSRV compliance test (test with declared `rust-version`)

  - [ ] Cross-platform build matrix (Linux, macOS, Windows)

- [ ] **Optional Periodic Checks (Tier 3)**

  - [ ] `cargo +nightly udeps --all-targets` (unused dependencies)

  - [ ] `cargo geiger --update` (unsafe code audit)

  - [ ] `cargo outdated` (dependency updates)

- [ ] **GitHub Actions Workflow**

  - [ ] Create `.github/workflows/ci.yml` with all checks

  - [ ] Configure matrix builds for multiple platforms

  - [ ] Set up caching for faster builds

  - [ ] Add MSRV testing job

## Phase 9: Scripts & Automation

- [ ] **Create Sync Script**

  - [ ] Create `scripts/sync-from-python.sh` (template in porting guide)

  - [ ] Make executable: `chmod +x scripts/sync-from-python.sh`

  - [ ] Test script execution

  - [ ] Document usage in README

- [ ] **Create Validation Script**

  - [ ] Create `scripts/validate-parity.sh` (template in porting guide)

  - [ ] Make executable: `chmod +x scripts/validate-parity.sh`

  - [ ] Test with current fixtures

  - [ ] Verify zero-diff detection works

## Phase 10: Final Acceptance Criteria

> **Completion Gate:** ALL items in this phase must be satisfied.
> No exceptions.

### Porting Parity Requirements (Mandatory)

- [ ] **Code Structure and Mapping**

  - [ ] All Python tests replicated with exact 1:1 behavioral parity

  - [ ] Additional Rust-specific unit tests present (fast feedback, edge cases)

  - [ ] `include_str!()` used for test fixtures

  - [ ] Clear module mapping maintained (Python → Rust)

  - [ ] Comments at top of each module indicating source Python module

  - [ ] Comments at top of every major function indicating source Python function

### CLI Parity (Mandatory)

- [ ] **Interface Compatibility** *(Zero diffs required)*

  - [ ] Exact flag names, short flags, defaults match

  - [ ] Help text matches byte-for-byte (zero diff on `--help` output)

  - [ ] Exit codes match exactly (0 success, 1 errors, 2 usage)

  - [ ] stdin/stdout piping works identically

- [ ] **Output Compatibility** *(Byte-for-byte matching required)*

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

- [ ] **Output Validation** *(Zero diffs required)*

  - [ ] All text comparisons are exact byte-for-byte matches (zero diffs)

  - [ ] All binary comparisons are exact byte-for-byte matches (zero diffs)

  - [ ] Processing results identical to Python output

  - [ ] File outputs match exactly (no whitespace/encoding differences unless
    documented)

### Cross-Validation (Mandatory)

- [ ] **Fixture Testing** *(Zero diffs required)*

  - [ ] Cross-validation script shows zero diffs across all fixtures

  - [ ] All input fixtures processed identically

  - [ ] All output fixtures match byte-for-byte

  - [ ] No encoding, line ending, or whitespace differences (unless documented)

### Performance Targets

- [ ] **Binary Metrics**

  - [ ] Binary size < 10MB (release build, stripped)

  - [ ] Startup time < 50ms

- [ ] **Runtime Performance**

  - [ ] Processing speed 50-100x faster than Python (benchmark critical paths)

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

**Port is complete when ALL items above are checked.
Zero failures accepted.**
