---
title: Rust Project Setup
description: Complete guide for setting up Rust packages, repos, CI/CD, security auditing, and release workflows
---
# Rust Project Setup

Complete guide for setting up a production-ready Rust project from scratch, including
Cargo configuration, CI/CD pipelines, security tooling, release workflows, and
development tooling.

Cross-referenced against real-world projects: flowmark-rs, ripgrep, bat, fd, jj.

For general Rust rules, see `tbd guidelines rust-general-rules`.
For CLI-specific patterns, see `tbd guidelines rust-cli-app-patterns`.
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

**Edition 2024** is now standard. ripgrep, fd, and jj all use it.
Always declare `rust-version` -- all major projects do this (bat, fd, jj, ripgrep).

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
regex = "1.10"
thiserror = "2.0"

# CLI deps (optional, behind feature gate)
clap = { version = "4.5", features = ["derive", "cargo", "color"], optional = true }
color-eyre = { version = "0.6", optional = true }
```

This pattern (used by flowmark-rs and bat) lets library users depend on the crate
without pulling in CLI-only deps like clap and color-eyre.

Test without default features in CI: `cargo test --no-default-features`

### Workspace (for Larger Projects)

```toml
[workspace]
members = ["crates/project-core", "crates/project-cli"]
resolver = "2"

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
```

Use workspaces when: independent versioning needed, very different dependency sets,
or project has 3+ crates. jj uses a workspace (~30 crates). Start with single package
and split only when you have a concrete reason.

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
and use the full LTO profile only for distribution (`cargo build --profile release-lto`).

### Lint Configuration

Two approaches are used in practice:

**Approach A: Blanket pedantic** (flowmark-rs). Enables all pedantic lints, allows
the noisy ones individually. Catches more but requires more `allow` overrides:

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

Note: `priority = -1` is required on group lints so individual overrides take precedence.

**Approach B: Curated lint list** (jj). Cherry-picks specific useful lints. More
maintainable, avoids churn when new pedantic lints are added:

```toml
[lints.clippy]
cloned_instead_of_copied = "warn"
explicit_iter_loop = "warn"
flat_map_option = "warn"
implicit_clone = "warn"
manual_let_else = "warn"
semicolon_if_nothing_returned = "warn"
uninlined_format_args = "warn"
use_self = "warn"

[lints.rust]
unsafe_code = "forbid"
```

**Approach C: No lint config** (ripgrep, bat, fd). Just run `cargo clippy -- -D warnings`
in CI with defaults. Simplest, but catches fewer issues.

All approaches are valid. Choose based on project size and team preference.

## CI/CD with GitHub Actions

### Recommended: Separate Jobs (Modern Pattern)

Split CI into independent parallel jobs for fast feedback. This is what flowmark-rs,
jj, and delta do. Format and clippy fail fast; test and audit run in parallel.

```yaml
name: CI
on:
  push:
    branches: ["*"]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  fmt:
    name: Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    name: Clippy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo clippy --all-targets --all-features -- -D warnings

  test:
    name: Tests (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "ci-${{ matrix.os }}"
      - run: cargo test --all-features --locked
      - run: cargo test --no-default-features --locked   # Verify library builds alone

  msrv:
    name: MSRV Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@1.85   # Match rust-version in Cargo.toml
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features --locked  # Full test, not just check

  audit:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: rustsec/audit-check@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

  deny:
    name: Dependency Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: EmbarkStudios/cargo-deny-action@v2

  docs:
    name: Documentation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"
```

**Key patterns from real-world projects:**
- Use `actions/checkout@v5` (current), `dtolnay/rust-toolchain` (not `actions-rs`)
- `Swatinem/rust-cache@v2` with `shared-key` per job type
- `--locked` in test/build to enforce Cargo.lock reproducibility
- Test with `--no-default-features` to verify library builds without CLI deps
- MSRV job should run `cargo test`, not just `cargo check` (flowmark-rs does this)
- Use `rustsec/audit-check@v2` action, not `cargo install cargo-audit` (faster)
- Use `EmbarkStudios/cargo-deny-action@v2` (no manual install needed)
- Doc build with `-D warnings` catches broken doc links and missing docs

### Cross-Platform Test Matrix

For CLI tools, test on all three major platforms. The test job above already does this.
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
```

In CI, use the `rustsec/audit-check@v2` action (faster, no install step).

### cargo-deny

Comprehensive dependency policy: licenses, advisories, bans, source restrictions.

**`deny.toml` configuration** (based on flowmark-rs, validated against jj):
```toml
[advisories]
version = 2                         # Use v2 schema (required for current cargo-deny)
db-path = "~/.cargo/advisory-db"
db-urls = ["https://github.com/rustsec/advisory-db"]

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

# ring uses a non-standard license file; clarify it
[[licenses.clarify]]
name = "ring"
expression = "MIT AND ISC AND OpenSSL"
license-files = [{ path = "LICENSE", hash = 0xbd0eed23 }]

[bans]
multiple-versions = "warn"          # Warn on duplicate deps in tree
deny = []

[sources]
unknown-registry = "deny"           # Only allow crates.io
unknown-git = "deny"                # No git dependencies
```

**Important:** Use `version = 2` for `[advisories]` and `[licenses]`. The v1 schema
is deprecated and will cause warnings or errors with current cargo-deny.

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
after the tag push. This ensures binaries are built and uploaded alongside the
crates.io publish.

### Release CI Workflow

All major Rust CLI projects (ripgrep, bat, fd, jj) hand-roll their release workflows.
No major project uses cargo-dist. The standard pattern:

1. **cargo-release** bumps version, commits, tags, pushes
2. **Tag push** triggers release workflow
3. **Release workflow** creates GitHub Release, builds cross-platform binaries, publishes to crates.io

```yaml
name: Release
on:
  push:
    tags: ["v[0-9]+.*"]

permissions:
  contents: write

jobs:
  create-release:
    runs-on: ubuntu-latest
    outputs:
      upload_url: ${{ steps.release.outputs.upload_url }}
    steps:
      - uses: actions/checkout@v5
      - id: release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref_name }}
          release_name: Release ${{ github.ref_name }}

  build:
    needs: create-release
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - { os: ubuntu-latest, target: x86_64-unknown-linux-gnu, name: linux-x86_64 }
          - { os: ubuntu-latest, target: x86_64-unknown-linux-musl, name: linux-x86_64-musl }
          - { os: macos-latest, target: x86_64-apple-darwin, name: macos-x86_64 }
          - { os: macos-latest, target: aarch64-apple-darwin, name: macos-aarch64 }
          - { os: windows-latest, target: x86_64-pc-windows-msvc, name: windows-x86_64 }
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      - name: Install musl tools
        if: contains(matrix.target, 'musl')
        run: sudo apt-get update && sudo apt-get install -y musl-tools
      - run: cargo build --release --locked --target ${{ matrix.target }}
      # ... archive and upload steps

  publish-crates-io:
    needs: [create-release, build]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo publish --locked
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
```

**For Linux ARM64**, use `cross` (cross-compilation tool):
```yaml
      - run: cargo install cross --git https://github.com/cross-rs/cross
      - run: cross build --release --locked --target aarch64-unknown-linux-gnu
```

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
cargo install cargo-outdated    # Check for dependency updates
```

**`cargo-binstall`** is highly recommended: it downloads pre-built binaries instead of
compiling from source, making tool installation 10-100x faster.

**`cargo-nextest`** is used by jj and many large projects. It runs tests in parallel
processes (not just threads), provides better output, and is significantly faster on
multi-core machines. It's a drop-in replacement: `cargo nextest run` instead of
`cargo test`.

### Editor Configuration

**`rustfmt.toml`** (based on flowmark-rs):
```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Max"
```

These three settings are the most common customizations. Most projects use the defaults
for everything else. `use_small_heuristics = "Max"` tells rustfmt to use the full
`max_width` for all constructs (structs, function args, etc.) rather than applying
shorter limits.

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

Add doc build to CI with `-D warnings` to catch broken links and missing docs
(already included in the CI workflow above).

### User Documentation

Standard files for any published crate:
- `README.md` -- quick start, installation, basic usage
- `CHANGELOG.md` -- version history (keep-a-changelog format)
- `LICENSE` or `LICENSE-MIT` + `LICENSE-APACHE` -- project license(s)

For complex tools, consider `clap_mangen` to auto-generate man pages from clap
definitions.

## Dependency Management

- **Pin major versions:** Use `"4.5"` not `"4"` or `"*"` in Cargo.toml
- **Commit `Cargo.lock`** for binary projects (ensures reproducible builds)
- **Don't commit `Cargo.lock`** for library-only crates (let downstream resolve)
- **Review dependency diffs** before updating with `cargo update`
- **Minimize dependency count.** Each dependency is a supply chain risk and compile time
  cost. flowmark-rs has ~14 runtime deps; ripgrep has ~30+ but most are internal crates
- **Use `--locked` in CI** to enforce that `Cargo.lock` is up to date and builds are
  reproducible
- **Feature-gate heavy deps:** Put CLI-only deps behind a feature flag (see lib+bin
  pattern above) so library users don't pay for them

## Git Configuration

### `.gitignore`

```
/target
*.swp
*.swo
.DS_Store
```

### Git Submodules (for ports)

When porting from Python, include the source as a submodule:
```bash
git submodule add https://github.com/org/python-project.git python-repo
```

This lets agents read the Python source directly and provides an exact commit reference.

## Related Guidelines

- For general Rust rules, see `tbd guidelines rust-general-rules`
- For CLI patterns, see `tbd guidelines rust-cli-app-patterns`
- For commit conventions, see `tbd guidelines commit-conventions`
- For Python-to-Rust porting, see `tbd guidelines python-to-rust-porting-rules`
- For release notes, see `tbd guidelines release-notes-guidelines`
