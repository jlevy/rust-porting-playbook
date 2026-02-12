# Python→Rust Subsequent Update Checklist

**Reference:** This checklist implements the update process described in [Python to Rust
CLI Porting Guide](python-to-rust-porting-guide.md) (see Phase 4: Ongoing
Synchronization of Python Code Changes). See that guide for detailed explanations and
handling strategies.

**Instructions:** Copy this document to `port-checklist-update-YYYY-MM-DD.md` (filling
in the date of the sync). Then fill in the copy, so that this template can be reused
for each subsequent sync cycle.

**Related:** [Initial Port Checklist](port-checklist-initial-template.md) | [Rust CLI Best
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

## Automated Upstream Tracking (Recommended)

Consider setting up automated detection of upstream Python changes to avoid manual
polling:

- **GitHub Actions scheduled workflow**: Run `scripts/sync-from-python.sh` on a
  schedule (e.g., weekly via `cron: '0 0 * * 1'`). If changes are detected, open a PR
  or issue automatically.

- **Dependabot-style submodule updates**: Use a CI job that checks whether the
  submodule pointer is behind `origin/main` and notifies if so.

- **CI parity gate**: Add `scripts/validate-parity.sh` as a CI step so that any
  submodule update that breaks parity is caught automatically.

These are optional but strongly recommended for projects with active Python upstreams.

## Phase 1: Sync Python Changes

- [ ] **Update Submodule**

  - [ ] Run `scripts/sync-from-python.sh` to fetch latest Python changes

  - [ ] Review script output for Python commit range updated

  - [ ] Verify test fixtures copied to `test-fixtures/` directory

  - [ ] Verify submodule pointer updated in git

- [ ] **Review Python Changes**

  - [ ] Identify the previous and current Python commit hashes from the sync script
    output (or from `git log` on the submodule)

  - [ ] Run `cd python-source && git log <previous-commit>..HEAD --oneline` to list
    changes

  - [ ] Read commit messages and diffs: `git log <previous-commit>..HEAD -p`

  - [ ] Identify which modules/functions were modified

  - [ ] Categorize each change as: bug fix, new feature, test addition, or refactor

- [ ] **Update Version Tracking**

  - [ ] Verify `[package.metadata.python_source]` in `Cargo.toml` was updated by sync
    script (version, commit, date) -- update manually if needed

  - [ ] Update `docs/version-history.md` with new Rust/Python version correspondence

- [ ] **Document Changes**

  - [ ] Create new entry in `docs/python-sync-log.md` with date and Python commit hash
    range

  - [ ] List Python changes discovered

  - [ ] List Rust updates required

  - [ ] Mark status as "In progress"

## Phase 2: Port Changes to Rust

- [ ] **Port Bug Fixes**

  - [ ] For each bug fix identified:

    - [ ] Locate corresponding Rust function (check module/function mapping comments)

    - [ ] Port fix to Rust maintaining exact behavior

    - [ ] Verify Python test for bug fix exists

    - [ ] Port or update corresponding Rust test

    - [ ] Run test to confirm fix works

- [ ] **Port New Features** (if applicable to Rust version)

  - [ ] For each new feature to port:

    - [ ] Add function/module structure matching Python

    - [ ] Add mapping comment header

    - [ ] Implement functionality

    - [ ] Port all related tests with 1:1 parity

    - [ ] Update integration tests if needed

    - [ ] Check for critical pitfalls (regex anchors, string preservation, etc.)

- [ ] **Port Test Additions**

  - [ ] For each new Python test:

    - [ ] Add equivalent Rust test (unit or integration)

    - [ ] Implement any missing functionality to make test pass

    - [ ] Verify byte-for-byte output matching

    - [ ] Use `include_str!()` for new fixtures if added

- [ ] **Handle Refactoring**

  - [ ] Determine if Python refactor requires Rust changes

  - [ ] If behavior unchanged, verify existing tests still pass

  - [ ] If internal structure changed, update Rust accordingly

  - [ ] Maintain module/function mapping comments

- [ ] **Document Deferred or Skipped Changes** (if any Python changes are intentionally
  not ported)

  - [ ] Record each skipped change with rationale in `docs/python-sync-log.md`

  - [ ] Create tracking issues for deferred features if they may be ported later

## Phase 3: CLI Updates

- [ ] **Update CLI Interface** (if changed in Python)

  - [ ] Update flag names or short forms if modified

  - [ ] Update default values if changed

  - [ ] Update help text to match Python

  - [ ] Update exit codes if modified

  - [ ] Test stdin/stdout behavior if changed

- [ ] **Validate CLI Parity** *(Completion Gate: Zero diffs on all CLI output)*

  - [ ] Generate Python help: `python -m project --help > python-help.txt` (or
    `python-source/cli.py --help`, depending on project structure)

  - [ ] Generate Rust help: `cargo run -- --help > rust-help.txt`

  - [ ] Run `diff python-help.txt rust-help.txt` (expect zero diffs, byte-for-byte)

  - [ ] Test modified flag combinations

  - [ ] Verify error messages match Python’s new behavior exactly

  - [ ] Verify status/warning messages match exactly

  - [ ] Verify all command output remains identical

## Phase 4: Testing & Validation

- [ ] **Test Coverage**

  - [ ] Achieve ≥90% line coverage in core library

  - [ ] Achieve 100% coverage of public API

  - [ ] Add property tests (via `proptest`) for algorithmic correctness if new
    algorithms added

  - [ ] Run `cargo test --all-features --workspace` (all tests pass)

  - [ ] Run `cargo test --no-default-features --workspace` (library builds without CLI
    deps)

  - [ ] Run `cargo test --doc` (doc tests pass)

- [ ] **Cross-Validation Script** *(Completion Gate: Zero diffs across all fixtures)*

  - [ ] Build release: `cargo build --release`

  - [ ] Run `scripts/validate-parity.sh`

  - [ ] Verify zero diffs between Python and Rust output (byte-for-byte)

  - [ ] Verify all file outputs match exactly (no whitespace/encoding differences)

  - [ ] Document any failures and resolve before proceeding

- [ ] **Quality Checks**

  - [ ] `cargo fmt --all -- --check` (zero diffs)

  - [ ] `cargo clippy --all-targets --all-features -- -D warnings` (zero warnings)

  - [ ] `cargo audit` (no vulnerabilities)

  - [ ] `cargo deny check` (licenses, advisories, bans, sources all pass)

  - [ ] `cargo doc --no-deps` (documentation builds without errors)

- [ ] **CI Verification**

  - [ ] All CI checks pass (or confirm locally with `just check` / equivalent)

  - [ ] Cross-validation script passes in CI environment (not just locally)

## Phase 5: Performance & Optimization

- [ ] **Performance Targets**

  - [ ] Binary size < 10MB (release build, stripped; use `cargo-bloat` to identify size
    issues if needed)

  - [ ] Processing speed maintained or improved vs previous Rust version (benchmark
    critical paths; target remains 50-100x faster than Python)

  - [ ] Startup time < 50ms

  - [ ] No performance regressions in hot paths

- [ ] **Optimization Techniques** (if new code added)

  - [ ] Use `&str` over `String` where possible

  - [ ] Minimize allocations in hot paths

  - [ ] Use lazy static regex patterns (`std::sync::LazyLock`)

  - [ ] Consider `rayon` for parallel processing if applicable

## Phase 6: Documentation

- [ ] **Code Documentation**

  - [ ] Add `///` doc comments to all public APIs (new or modified)

  - [ ] Add `//!` module-level documentation (if new modules added)

  - [ ] Include examples in doc comments for new functionality

  - [ ] Verify documentation builds: `cargo doc --no-deps --open`

- [ ] **User Documentation**

  - [ ] Update `README.md` if features/usage changed

  - [ ] Add entry to `CHANGELOG.md` (use keep-a-changelog format)

  - [ ] Update divergence documentation if any new intentional differences from Python
    were introduced (document rationale and acceptance criteria)

  - [ ] Update `docs/version-history.md` with final version correspondence entry

  - [ ] Update `docs/python-sync-log.md`: mark all items completed, change status to
    "Completed", note any intentional divergences or deferred features

## Phase 7: Final Acceptance Criteria

> **Completion Gate:** ALL items in this phase must be satisfied.
> No exceptions.

### Porting Parity Requirements (Mandatory)

- [ ] **Code Structure and Mapping**

  - [ ] All Python tests still replicated with 1:1 parity

  - [ ] New Python tests replicated with 1:1 parity

  - [ ] Module/function mapping comments updated

  - [ ] `include_str!()` used for any new fixtures

### CLI Parity (Mandatory)

- [ ] **Interface Compatibility** *(Zero diffs required)*

  - [ ] All flags match Python exactly

  - [ ] Help output diff shows zero differences (byte-for-byte)

  - [ ] Exit codes remain correct (0 success, 1 errors, 2 usage)

  - [ ] stdin/stdout piping still works

- [ ] **Output Compatibility** *(Byte-for-byte matching required)*

  - [ ] Error messages match exactly

  - [ ] Warning messages match exactly

  - [ ] Status messages match exactly

  - [ ] All command output identical to Python

### Test Parity (Mandatory)

- [ ] **Test Execution** *(100% pass rate required)*

  - [ ] 100% of tests pass

  - [ ] All new features/fixes working correctly

  - [ ] Edge cases still handled identically

- [ ] **Output Validation** *(Zero diffs required)*

  - [ ] All text comparisons are exact byte-for-byte matches

  - [ ] All binary comparisons are exact byte-for-byte matches

  - [ ] Processing results identical to Python output

  - [ ] File outputs match exactly (no whitespace/encoding differences unless
    documented)

### Cross-Validation (Mandatory)

- [ ] **Fixture Testing** *(Zero diffs required)*

  - [ ] Cross-validation shows zero diffs across all fixtures

  - [ ] All input fixtures processed identically

  - [ ] All output fixtures match byte-for-byte

  - [ ] No encoding, line ending, or whitespace differences (unless documented)

### Performance Targets

- [ ] **Binary Metrics**

  - [ ] Binary size < 10MB (release build, stripped)

  - [ ] Startup time < 50ms

- [ ] **Runtime Performance**

  - [ ] Processing speed maintained or improved vs previous Rust version (target:
    50-100x faster than Python)

  - [ ] No performance regressions in hot paths

### Quality Metrics (Mandatory)

- [ ] **Code Quality** *(Zero warnings/errors required)*

  - [ ] Zero clippy warnings (`cargo clippy --all-targets --all-features -- -D
    warnings`)

  - [ ] Zero format diffs (`cargo fmt --all -- --check`)

  - [ ] Documentation builds without errors (`cargo doc --no-deps`)

- [ ] **Test Coverage** *(Minimum thresholds required)*

  - [ ] ≥90% test coverage maintained in core library

  - [ ] 100% coverage maintained for public API

  - [ ] All public APIs documented

- [ ] **Security & Dependencies** *(All checks must pass)*

  - [ ] `cargo audit` passes (no vulnerabilities)

  - [ ] `cargo deny check` passes (all checks)

  - [ ] No new unsafe code (or documented exceptions)

## Phase 8: Release

- [ ] **Version Management**

  - [ ] Determine version bump type (patch, minor, major)

  - [ ] Update version in `Cargo.toml`

  - [ ] Update `Cargo.lock` via `cargo update --workspace` (or `cargo generate-lockfile`
    for a clean regeneration)

- [ ] **Pre-Release Checks**

  - [ ] Review `CHANGELOG.md` entry completeness

  - [ ] Verify all CI checks would pass

  - [ ] Run `cargo publish --dry-run`

- [ ] **Git Operations**

  - [ ] Commit all changes with descriptive message

  - [ ] Tag and push using `cargo release` (preferred) or manually:
    `git tag v<version> && git push && git push --tags`

- [ ] **Optional Publishing**

  - [ ] Publish to crates.io: `cargo publish` (if appropriate)

  - [ ] Create GitHub release with changelog excerpt

**Update is complete when ALL mandatory items above are checked.
Zero unexplained failures accepted.**
