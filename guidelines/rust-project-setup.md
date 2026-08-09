---
title: Rust Project Setup
description: Complete guide for setting up Rust packages, repos, CI/CD, security auditing, and release workflows
---
# Rust Project Setup

Complete guide for setting up a production-ready Rust project from scratch, including
Cargo configuration, CI/CD pipelines, security tooling, release workflows, and
development tooling.

Cross-referenced against real-world projects: flowmark-rs, ripgrep, bat, fd, jj.

See also: [Rust General Rules](rust-general-rules.md),
[Rust CLI App Patterns](../references/rust-cli-app-patterns.md).
For commit conventions, see `tbd guidelines commit-conventions`.

## Cargo.toml Configuration

### Essential Fields

```toml
[package]
name = "myproject"
version = "0.1.0"
edition = "2024"                    # Use latest edition for new projects
rust-version = "1.85"               # MSRV -- enforced by cargo and CI
authors = ["Your Name <email>"]
license = "MIT OR Apache-2.0"       # SPDX expression (dual license is standard)
description = "Brief description for crates.io"
repository = "https://github.com/user/project-rs"
keywords = ["cli", "tool", "utility"]   # Up to 5, for crates.io search
categories = ["command-line-utilities"]  # From crates.io fixed list
readme = "README.md"
```

**Edition 2024** is now standard for new projects (stabilized in Rust 1.85). Always
declare `rust-version` -- all major projects do this (bat, fd, jj, ripgrep).

### Library + Binary in One Crate (Recommended)

For projects that are both a library and a CLI tool, use feature-gated binaries:

```toml
# Library target (always available)
[lib]
name = "myproject"
path = "src/lib.rs"

# Binary target (only with cli feature)
[[bin]]
name = "myproject"
path = "src/main.rs"
required-features = ["cli"]

[features]
default = ["cli"]
cli = ["clap", "color-eyre", "tracing", "tempfile", "indicatif", "ctrlc"]

[dependencies]
# Core deps (always included)
regex = "1.13"
thiserror = "2.0"

# CLI deps (optional, behind feature gate)
clap = { version = "4.6", features = ["derive", "cargo", "color"], optional = true }
color-eyre = { version = "0.6", optional = true }
```

This pattern (used by flowmark-rs and bat) lets library users depend on the crate
without pulling in CLI-only deps like clap and color-eyre.

Test without default features in CI: `cargo test --no-default-features`

### Workspace (for Larger Projects)

```toml
[workspace]
members = ["crates/project-core", "crates/project-cli"]
resolver = "3"                     # Edition 2024 uses resolver v3 (MSRV-aware)

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
```

Use workspaces when: independent versioning needed, very different dependency sets, or
project has 3+ crates.
jj uses a workspace (~30 crates).
Start with single package and split only when you have a concrete reason.

### Release Profile

```toml
[profile.release]
opt-level = 3           # Maximum optimization
lto = true              # Link-time optimization for smaller, faster binaries
codegen-units = 1       # Better optimization at cost of compile time
strip = true            # Remove debug symbols (smaller binary)
panic = "abort"         # Smaller binary, no unwinding
```

This is the standard aggressive profile used by bat, fd, and flowmark-rs.

**Consider:** ripgrep keeps `debug = 1` in the default release profile for useful
backtraces, and uses a separate `release-lto` profile for maximum optimization:

```toml
[profile.release]
debug = 1               # Keep some debug info for backtraces

[profile.release-lto]
inherits = "release"
opt-level = 3
lto = "fat"
strip = true
panic = "abort"
codegen-units = 1
```

This lets you build quick release builds during development (`cargo build --release`)
and use the full LTO profile only for distribution
(`cargo build --profile release-lto`).

### Lint Configuration

Three approaches are used in practice:

**Approach A: Blanket pedantic** (flowmark-rs).
Enables all pedantic lints, allows the noisy ones individually.
Catches more but requires more `allow` overrides:

```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
# Selectively allow noisy pedantic lints
missing_errors_doc = "allow"
missing_panics_doc = "allow"
module_name_repetitions = "allow"
must_use_candidate = "allow"

[lints.rust]
unsafe_code = "forbid"
```

Note: `priority = -1` is required on group lints so individual overrides take
precedence.

**Approach B: Curated lint list** (jj).
Cherry-picks specific useful lints.
More maintainable, avoids churn when new pedantic lints are added:

```toml
[lints.clippy]
cloned_instead_of_copied = "warn"
explicit_iter_loop = "warn"
flat_map_option = "warn"
implicit_clone = "warn"
manual_let_else = "warn"
needless_pass_by_value = "warn"
redundant_closure_for_method_calls = "warn"
semicolon_if_nothing_returned = "warn"
uninlined_format_args = "warn"
use_self = "warn"

[lints.rust]
unsafe_code = "forbid"
unused_qualifications = "warn"
```

**Approach C: No lint config** (ripgrep, bat, fd).
Just run `cargo clippy -- -D warnings` in CI with defaults.
Simplest, but catches fewer issues.

All approaches are valid.
Choose based on project size and team preference.

**Why `warn` in Cargo.toml + `-D warnings` in CI:** Setting pedantic lints to `warn`
(not `deny`) in Cargo.toml lets developers see warnings during local development without
blocking compilation. The CI command `cargo clippy -- -D warnings` then promotes all
warnings to errors, enforcing zero-warning builds. This two-tier strategy gives fast
local iteration while maintaining strict quality gates in CI.

## CI/CD with GitHub Actions

### Recommended: Separate Jobs (Modern Pattern)

Split CI into independent parallel jobs for fast feedback.
The example below defines 11 jobs; the three-platform test matrix expands it to 13 job
executions. This is the pattern used by flowmark-rs, jj, and delta.
Format and clippy fail fast; test and audit run in parallel.

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

env:
  CARGO_TERM_COLOR: always
  CARGO_INCREMENTAL: 0             # Faster CI (no incremental overhead)
  CARGO_PROFILE_TEST_DEBUG: 0      # Smaller test binaries

jobs:
  fmt:
    name: Format check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    name: Clippy lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo clippy --locked --all-targets --all-features -- -D warnings

  test:
    name: Test (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --all-features
        env:
          RUSTFLAGS: "-D warnings"

  test-lib-only:
    name: Test library (no default features)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --no-default-features
        env:
          RUSTFLAGS: "-D warnings"

  msrv:
    name: MSRV check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@1.85   # Match rust-version in Cargo.toml
      - uses: Swatinem/rust-cache@v2
      - run: cargo check --locked --all-features

  deny:
    name: Dependency audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: EmbarkStudios/cargo-deny-action@v2

  audit:
    name: Vulnerability audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: rustsec/audit-check@v2

  docs:
    name: Documentation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --locked --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"

  coverage:
    name: Code coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-llvm-cov
      - run: cargo llvm-cov --locked --all-features --lcov --output-path lcov.info
        env:
          RUSTFLAGS: "-D warnings"
      - uses: codecov/codecov-action@v7
        with:
          files: lcov.info
          fail_ci_if_error: false
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

  semver-checks:
    name: Semver compatibility
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - uses: obi1kenobi/cargo-semver-checks-action@v2

  workflow-scripts:
    name: Workflow script tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
```

**Key patterns from real-world projects:**
- Use `actions/checkout@v7` (current), `dtolnay/rust-toolchain` (not `actions-rs`)
- `Swatinem/rust-cache@v2` for build caching across jobs
- `--locked` on all cargo commands enforces Cargo.lock reproducibility
- `RUSTFLAGS: "-D warnings"` in test/build jobs treats warnings as errors
- `CARGO_INCREMENTAL: 0` + `CARGO_PROFILE_TEST_DEBUG: 0` for faster CI builds
- `test-lib-only` verifies library builds without CLI feature deps
- `coverage` via `cargo-llvm-cov` + Codecov (use `taiki-e/install-action` for speed)
- `semver-checks` on PRs only (needs `fetch-depth: 0`) catches API breakage
- `workflow-scripts` validates testable release automation scripts
- Use `EmbarkStudios/cargo-deny-action@v2` (no manual install needed)
- Doc build with `RUSTDOCFLAGS: "-D warnings"` catches broken doc links

### Cross-Platform Test Matrix

For CLI tools, test on all three major platforms.
The test job above already does this.
For builds, add target-specific builds in the release workflow (see below).

### MSRV Policy

- Declare `rust-version` in `Cargo.toml` (all major projects do this)
- Test MSRV in CI with `dtolnay/rust-toolchain@<version>` pinned to your MSRV
- Update MSRV when you need new features, not on every Rust release
- Document MSRV in README

## Security Auditing

### cargo-audit

Checks for known vulnerabilities in dependencies via the RustSec advisory database:
```bash
cargo install cargo-audit
cargo audit
cargo audit fix   # Automatically update vulnerable dependencies when possible
```

In CI, use the `rustsec/audit-check@v2` action (faster, no install step).
Alternative: `actions-rust-lang/audit` supports ignoring specific advisories via config.

### cargo-deny

Comprehensive dependency policy: licenses, advisories, bans, source restrictions.

**`deny.toml` configuration** (based on flowmark-rs, validated against jj):
```toml
[advisories]
version = 2                         # Use v2 schema (required for current cargo-deny)
# db-path and db-urls use sensible defaults; override only if needed

[licenses]
version = 2
confidence-threshold = 0.8
allow = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0 WITH LLVM-exception",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-3.0",
]

# ring uses a non-standard license file; clarify it.
# ring does not set a `license` field in Cargo.toml, only `license-file`,
# so cargo-deny cannot determine the license automatically.
[[licenses.clarify]]
name = "ring"
expression = "MIT AND ISC AND OpenSSL"
license-files = [{ path = "LICENSE", hash = 0xbd0eed23 }]
# IMPORTANT: hash is version-specific; if ring updates its LICENSE file,
# run `cargo deny check licenses` to get the new hash from the error output.

# ring's clarified license includes OpenSSL, which must be explicitly allowed
[[licenses.exceptions]]
allow = ["OpenSSL"]
name = "ring"

[bans]
multiple-versions = "warn"          # Warn on duplicate deps in tree
deny = []

[sources]
unknown-registry = "deny"           # Only allow crates.io
unknown-git = "deny"                # No git dependencies
```

**Important:** Use `version = 2` for `[advisories]` and `[licenses]`. The v1 schema is
deprecated and will cause warnings or errors with current cargo-deny.

## Release Workflow

### cargo-release (Version Bumping and Tagging)

```bash
cargo install cargo-release
cargo release patch --execute   # or minor, major
```

**`release.toml` configuration** (based on flowmark-rs):
```toml
# Don't publish to crates.io from local machine (let CI handle it)
publish = false

# Tag format
tag-prefix = "v"
tag-name = "v{{version}}"

# Push tag to remote (triggers release CI)
push = true
allow-branch = ["main", "master"]

# Pre-release checks
pre-release-commit-message = "Bump version to {{version}}"
tag-message = "Release {{version}}"
pre-release-hook = ["just", "check"]    # Run all checks before release
```

**Key decision:** `publish = false` locally, let GitHub Actions handle `cargo publish`
after the tag push. This ensures binaries are built and uploaded alongside the crates.io
publish. In workspaces, set `publish = false` in `Cargo.toml` for crates that should not
be published (internal crates, test utilities, etc.).

### Release CI Workflow

All major Rust CLI projects (ripgrep, bat, fd, jj) hand-roll their release workflows.

**Alternative: `cargo-dist`** (by axodotdev, now branded `dist`) can generate complete
release CI workflows with `dist init`. It handles cross-compilation, installer
generation (shell scripts, Homebrew, MSI), and GitHub Release uploads with minimal
configuration.
It has matured significantly (v0.32+ as of August 2026) and is a good choice when you
don’t need full control over the release pipeline.
See https://axodotdev.github.io/cargo-dist/ for details.

For full control, the standard hand-rolled pattern:

1. **cargo-release** bumps version, commits, tags, pushes
2. **Tag push** triggers `release.yml` orchestrator
3. **Release workflow** plans, builds binaries, generates checksums, publishes to
   channels, and creates GitHub Release

**Cross-compilation approach:** Use RUSTFLAGS linker overrides with apt-get packages
instead of Docker-based `cross`. For musl targets, install `musl-tools`; for Linux
ARM64, install `gcc-aarch64-linux-gnu` and set linker override via
`--codegen linker=aarch64-linux-gnu-gcc`. This is simpler and more transparent.

**Static linking:** Use `--codegen target-feature=+crt-static` for statically linked
binaries on musl targets.

**crates.io OIDC auth:** Use `rust-lang/crates-io-auth-action@v1` instead of
long-lived `CARGO_REGISTRY_TOKEN` secrets. Same principle as PyPI trusted publishing.

**Release automation scripts:** Extract complex workflow logic into testable Python
scripts (`scripts/*.py`) with unit tests. Scripts handle semver parsing, archive
creation, idempotency checks, and wheel validation. Run tests in CI with
`python3 -m unittest discover -s scripts/tests -p 'test_*.py'`.

See [Rust CLI Best Practices](../references/rust-cli-best-practices.md#64-release-ci-workflow)
for the complete release workflow template with plan job, concurrency control,
checksum generation, and reusable channel workflows.

### Multi-Channel Distribution

Beyond crates.io and GitHub Releases, distribute Rust CLI binaries through additional
channels for broader reach. See
[Rust CLI Best Practices](../references/rust-cli-best-practices.md#65-multi-channel-distribution)
for full workflow templates.

**PyPI via maturin is the recommended primary distribution channel** for Rust CLI
binaries targeting a broad audience. `uvx <tool>` provides instant ephemeral execution
with no Rust toolchain required — there is no cargo equivalent to this (`cargo install`
compiles from source; `cargo binstall` requires a separate install and has no ephemeral
mode). uv is now standard in modern Python environments, making PyPI the
lowest-friction cross-platform distribution channel for Rust CLIs.

Add `pyproject.toml` at repo root with `[tool.maturin] bindings = "bin"` and
`dynamic = ["version"]` (reads from `Cargo.toml`). Build cross-platform wheels with
`PyO3/maturin-action` in CI; publish with `uv publish --trusted-publishing always`.
This is the pattern used by ruff, uv, and maturin itself.

**Homebrew tap** (`brew install <tap>/<tool>`):
Create a personal tap repo (`<user>/homebrew-<project>`) with a formula that downloads
GitHub Release archives. Pin SHA256 checksums; update manually after each release.

**Orchestration:** For multi-channel projects, use a single `release.yml` orchestrator
that invokes reusable channel workflows (`publish.yml`, `pypi.yml`) with conditional
gating. Keep complex logic in testable scripts, not inline YAML.

**Idempotent publishing:** Each channel should detect already-published versions and skip
gracefully (crates.io: API query; PyPI: `--check-url`; GitHub Releases: naturally
idempotent).

## Development Tooling

### Task Runner: just

`just` is the standard task runner for Rust projects (used by flowmark-rs, jj, delta).
It replaces Makefiles with a simpler, cross-platform syntax.

**`justfile`** for common development tasks (based on flowmark-rs):
```just
# Run all CI checks locally (same as CI)
check: format-check lint test

# Format Rust code (auto-fix)
format-rust:
    cargo fmt --all

# Check code formatting (CI check only, no changes)
format-check:
    cargo fmt --all -- --check

# Run clippy (CI check only, no changes)
lint:
    cargo clippy --all-targets --all-features --workspace -- -D warnings

# Auto-fix clippy warnings where possible
lint-fix:
    cargo clippy --fix --all-targets --all-features --workspace --allow-dirty --allow-staged

# Run tests
test:
    cargo test --all-features --workspace

# Run tests (no default features -- verifies library builds alone)
test-no-default:
    cargo test --no-default-features --workspace

# Auto-fix everything possible (format + clippy)
fix: format-rust lint-fix

# Run before committing (auto-fix then verify all checks pass)
precommit: fix check

# Build release binary
build:
    cargo build --release

# Clean build artifacts
clean:
    cargo clean

# Release a new version (requires cargo-release)
# Usage: just release patch|minor|major
release level:
    cargo release {{level}} --execute
```

**Key patterns:**
- `check` mirrors CI exactly (format-check + lint + test)
- `precommit` runs auto-fix first, then verifies everything passes
- `--workspace` flag ensures all crates are covered
- `lint-fix` uses `--allow-dirty --allow-staged` so it can fix in-progress work
- `test-no-default` catches library-only build issues early
- `release` wraps cargo-release for convenience

### Recommended Dev Tools

```bash
# Essential
cargo install just              # Task runner (or: cargo binstall just)
cargo install cargo-audit       # Security audit
cargo install cargo-deny        # Dependency policy
cargo install cargo-release     # Version bumping and tagging

# Faster installs (pre-built binaries, no compile)
cargo install cargo-binstall    # Then use: cargo binstall <tool>

# Testing
cargo install cargo-nextest     # Faster test runner (parallel, better output)

# Development
cargo install cargo-watch       # Auto-rebuild on file change
cargo install bacon             # Background code checker (continuous clippy/test)

# Analysis
cargo install cargo-expand      # Expand macros for debugging
cargo install cargo-bloat       # Analyze binary size
cargo install cargo-udeps       # Find unused dependencies (requires nightly)
cargo install cargo-machete     # Find unused dependencies (fast, no nightly needed)
cargo install cargo-outdated    # Check for dependency updates
```

**`cargo-binstall`** is highly recommended: it downloads pre-built binaries instead of
compiling from source, making tool installation 10-100x faster.

**`cargo-nextest`** is used by jj and many large projects.
It runs tests in parallel processes (not just threads), provides better output, and is
significantly faster on multi-core machines.
It’s a drop-in replacement: `cargo nextest run` instead of `cargo test`.

### Editor Configuration

**`rustfmt.toml`** (based on flowmark-rs):
```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Max"
```

These three settings are the most common customizations.
Most projects use the defaults for everything else.
`use_small_heuristics = "Max"` tells rustfmt to use the full `max_width` for all
constructs (structs, function args, etc.)
rather than applying shorter limits.

## Documentation

### In-Code Documentation

- Document all public items with `///` doc comments
- Use `//!` for module-level documentation
- Include examples in doc comments (they become doctests):
  ```rust
  /// Wraps text to the given width.
  ///
  /// # Examples
  ///
  /// ```
  /// use myproject::wrap;
  /// assert_eq!(wrap("hello world", 5), "hello\nworld");
  /// ```
  pub fn wrap(text: &str, width: usize) -> String { /* ... */ }
  ```

### cargo doc

```bash
cargo doc --open --no-deps  # Build and open docs locally
```

Add doc build to CI with `-D warnings` to catch broken links and missing docs (already
included in the CI workflow above).

### User Documentation

Standard files for any published crate:
- `README.md` -- quick start, installation, basic usage
- `CHANGELOG.md` -- version history (keep-a-changelog format)
- `LICENSE` or `LICENSE-MIT` + `LICENSE-APACHE` -- project license(s)

For complex tools, consider `clap_mangen` to auto-generate man pages from clap
definitions.

## Dependency Management

- **Specify minimum minor versions:** Use `"4.5"` not `"4"` or `"*"` in Cargo.toml
- **Commit `Cargo.lock`** for binary projects (ensures reproducible builds)
- **Don’t commit `Cargo.lock`** for library-only crates (let downstream resolve)
- **Review dependency diffs** before updating with `cargo update`
- **Minimize dependency count.** Each dependency is a supply chain risk and compile time
  cost. flowmark-rs has ~14 runtime deps; ripgrep has ~30+ but most are internal crates
- **Use `--locked` in CI** to enforce that `Cargo.lock` is up to date and builds are
  reproducible
- **Feature-gate heavy deps:** Put CLI-only deps behind a feature flag (see lib+bin
  pattern above) so library users don’t pay for them

## Git Configuration

### `.gitignore`

```
/target
*.swp
*.swo
.DS_Store
```

### `.gitattributes`

Commit a `.gitattributes` that enforces LF line endings on every platform:

```gitattributes
* text=auto eol=lf
```

This matters more than it looks for ports. A port that embeds text with `include_str!`
(a `SKILL.md`, a help/usage doc, a template) bakes the file's bytes in at compile time,
and golden tests often read fixtures from disk. Without `eol=lf`, a Windows checkout
rewrites those files to CRLF, so embedded content and disk-read fixtures carry `\r\n` while
the program emits `\n` — and newline-anchored assertions (`starts_with("---\n")`,
`find("\n---\n")`) fail **only on Windows**, invisibly green on Linux and macOS. The
failure is silent, platform-specific, and hard to diagnose when CI logs are not accessible.
All sources are normally authored LF, so `git add --renormalize .` should report zero
content changes; this only stops Windows from rewriting them on checkout.

### Git Submodules (for ports)

When porting from Python, include the source as a submodule:
```bash
git submodule add https://github.com/org/python-project.git python-repo
```

This lets agents read the Python source directly and provides an exact commit reference.

## Related Guidelines

- [Rust General Rules](rust-general-rules.md)
- [Rust CLI App Patterns](../references/rust-cli-app-patterns.md)
- [Python-to-Rust Porting Rules](python-to-rust-porting-rules.md)
- For commit conventions, see `tbd guidelines commit-conventions`
- For release notes, see `tbd guidelines release-notes-guidelines`
