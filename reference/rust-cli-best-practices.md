# Rust CLI Best Practices

**A reference for building modern, production-ready Rust CLI applications**

**Related:** [Python to Rust CLI Porting Guide](python-to-rust-porting-guide.md) |
[Initial Port Checklist](port-checklist-initial-template.md) |
[Update Checklist](port-checklist-update-template.md)

Version: 1.1 | Last Updated: 2026-02-07

Cross-referenced against real-world projects: flowmark-rs, ripgrep, bat, fd, jj.

For the tbd guideline (more concise, optimized for agent consumption), see
`tbd guidelines rust-project-setup`.

* * *

## Overview

This document establishes the canonical standards for creating professional Rust
command-line tools with modern tooling, comprehensive testing, security validation, and
streamlined publishing workflows.
Use this as a template for all Rust CLI projects.

## 1. Project Structure

### 1.1 Repository Organization

**Recommended: Single Crate with Feature-Gated Binary** (flowmark-rs, bat pattern):
```
project-rs/                     # Repository name (can use -rs suffix)
├── Cargo.toml                  # Single manifest with lib + bin targets
├── src/
│   ├── lib.rs                  # Library (always available)
│   ├── main.rs                 # Binary (behind "cli" feature)
│   └── ...
├── tests/                      # Integration tests
├── deny.toml                   # cargo-deny config
├── release.toml                # cargo-release config
├── rustfmt.toml                # Formatting config
└── justfile                    # Task runner
```

**Workspace Layout** (for larger projects with 3+ crates, e.g., jj):
```
project-rs/
├── Cargo.toml                  # Workspace manifest
├── crates/
│   ├── project-core/           # Library crate
│   └── project-cli/            # Binary crate
```

Start with the single-crate pattern and split into a workspace only when you have
concrete reasons (independent versioning, very different dependency sets, 3+ crates).

**Package Naming Conventions**:

- **Repository**: `project-rs` (optional `-rs` suffix for clarity)

- **Library package**: `project` (matches crates.io convention, no suffix)

- **Binary name**: `project` (the actual command users type)

**Rationale**: Professional Rust tools avoid suffixes in package names (ripgrep, fd,
bat) as suffixes "seem like a lesser port".
The `-rs` suffix remains only in the repository URL for disambiguation.

### 1.2 Cargo.toml Best Practices

**Essential Fields**:
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

**Library + Binary in One Crate** (recommended, used by flowmark-rs and bat):
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
cli = ["clap", "color-eyre", "tracing", "tempfile", "indicatif", "ctrlc"]

[dependencies]
# Core deps (always included)
regex = "1.10"
thiserror = "2.0"

# CLI deps (optional, behind feature gate)
clap = { version = "4.5", features = ["derive", "cargo", "color"], optional = true }
color-eyre = { version = "0.6", optional = true }
```

This lets library users depend on the crate without pulling in CLI-only deps.
Test without default features in CI: `cargo test --no-default-features`

**Edition & MSRV Policy**:

- **Edition 2024** is now standard. ripgrep, fd, and jj all use it. [^rust-edition]

  - Editions are NOT calendar years -- they're language versioning markers released
    ~every 3 years

  - Named for when RFC'd, not released (edition 2024 shipped in Rust 1.85, Feb 2025)

  - All editions interoperate seamlessly

- Always declare `rust-version` field for MSRV -- all major projects do this
  (bat, fd, jj, ripgrep) [^msrv-policy]

- MSRV increases are NOT semver-breaking: use minor version bump (1.1.3 → 1.2.0)
  [^api-guidelines]

- Test MSRV compliance in CI (run full `cargo test`, not just `cargo check`)

## 2. Core Dependencies

### 2.1 Essential CLI Libraries

**Argument Parsing**: `clap` (v4+)
```toml
clap = { version = "4.5", features = ["derive", "cargo"] }
```

- Use **derive API** (recommended for modern projects) [^clap-derive]

- Enable `cargo` feature for automatic version/author from Cargo.toml

- Automatically generates help messages and validation

- Example pattern:
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}
```

**Error Handling**: `color-eyre` or `anyhow`
```toml
color-eyre = "0.6"  # Rich error display with backtraces and suggestions
# OR
anyhow = "1.0"      # Simpler, more minimal
```

- `color-eyre` provides enhanced error reports for end users

- `anyhow` for libraries where error display is less critical

**Logging/Tracing**: `tracing` ecosystem
```toml
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
```

- Structured logging with multiple levels

- Configurable via environment variables (`RUST_LOG`)

### 2.2 Common Domain Libraries

**Terminal UI**:

- `crossterm` - Cross-platform terminal manipulation

- `indicatif` - Progress bars and spinners

- `console` - Terminal colors and styles

- `ratatui` - Full TUI framework (formerly tui-rs)

**Configuration/Serialization**:

- `serde` - Serialization/deserialization framework

- `toml` - TOML parsing

- `serde_json` - JSON support

- `config` - Layered configuration system

**File/Path Operations**:

- `walkdir` - Recursive directory traversal

- `globset` - Glob pattern matching

- `tempfile` - Temporary files and directories

## 3. Code Quality & Linting

### 3.1 Formatting (Mandatory)

**cargo fmt** - Consistent code formatting
```bash
cargo fmt --all -- --check  # CI check
cargo fmt --all             # Local formatting
```

**Configuration** (`rustfmt.toml` or `.rustfmt.toml`):
```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Max"
```

**Policy**: All code must pass `cargo fmt --check` in CI (zero tolerance) [^rust-clippy]

### 3.2 Linting (Mandatory)

**cargo clippy** - Rust linter with 600+ rules
```bash
# CI command (strict mode)
cargo clippy --all-targets --all-features -- -D warnings

# Development
cargo clippy --all-targets
```

**Recommended Configuration** (`Cargo.toml`):
```toml
[lints.clippy]
# Enable pedantic for maximum quality
pedantic = { level = "warn", priority = -1 }  # priority = -1 required for group lints

# Selectively allow pedantic lints with false positives
missing_errors_doc = "allow"      # Not always necessary
missing_panics_doc = "allow"      # Documentation overhead
module_name_repetitions = "allow" # Often reasonable
must_use_candidate = "allow"      # Too aggressive

[lints.rust]
unsafe_code = "forbid"            # No unsafe without explicit allow
```

**Important:** `priority = -1` is required on group lints so that individual overrides
(at the default priority of 0) take precedence. Without this, the group setting wins
and your `"allow"` lines have no effect.

**Three approaches are used in practice:**

- **Blanket pedantic** (flowmark-rs): Enable all pedantic, allow the noisy ones.
  Catches the most but requires more `allow` overrides.

- **Curated lint list** (jj): Cherry-pick specific useful lints like
  `uninlined_format_args`, `use_self`, `explicit_iter_loop`. More maintainable, avoids
  churn when new pedantic lints are added.

- **No lint config** (ripgrep, bat, fd): Just `cargo clippy -- -D warnings` in CI
  with defaults. Simplest.

**Lint Groups** [^clippy-lints]:

- `warn` (default) - Common mistakes and idioms

- `pedantic` - Strict lints, occasional false positives (opt-in)

- `nursery` - New/experimental lints (use cautiously)

- `restriction` - Never enable wholesale; pick specific lints

**Best Practice**: Enable `pedantic`, then selectively `allow` specific lints
[^clippy-workspace]

### 3.3 Testing (Mandatory)

**cargo test** - Run all test suites
```bash
cargo test --all-features --workspace         # All features, all crates
cargo test --no-default-features --workspace  # Verify library builds alone
cargo test --all-features --workspace --locked # CI mode (reproducible)
```

**Test Organization**:
```
src/
├── lib.rs              # Unit tests in #[cfg(test)] mod tests { }
├── module.rs           # Inline tests next to the code they test
tests/
├── integration_test.rs # Integration tests (separate compilation unit)
└── fixtures/           # Test data
```

**Coverage Expectations**:

- Aim for 80%+ code coverage

- 100% for critical paths (parsing, data transformation)

- Use integration tests for CLI behavior

- Property-based testing (via `proptest` or `quickcheck`) for edge cases

**CLI Testing Tools**:

- `assert_cmd` - Test CLI applications end-to-end

- `predicates` - Assertions for command output

- `insta` - Snapshot testing (good for output-heavy tools, used by cargo itself)

- `proptest` - Property-based testing (used by flowmark-rs for fuzzing)

**Faster test runner:** `cargo-nextest` runs tests in parallel processes (not just
threads), provides better output, and is significantly faster. Used by jj and many
large projects. Drop-in replacement: `cargo nextest run`.

## 4. Security & Dependency Management

### 4.1 Security Auditing (Mandatory)

**cargo audit** - Check for security vulnerabilities
```bash
cargo audit  # Check against RustSec Advisory Database
```

**Tool Details** [^rustsec]:

- Audits dependencies against [RustSec Advisory Database](https://rustsec.org/)

- Install: `cargo install cargo-audit`

- Requires Rust 1.74+

- Supports automatic fixing: `cargo install cargo-audit --features=fix`

**Policy**: Must pass in CI; failing audits block releases

### 4.2 Dependency Management (Highly Recommended)

**cargo deny** - Comprehensive dependency validation
```bash
cargo deny check          # Run all checks
cargo deny check licenses # License compliance only
```

**Installation**:
```bash
cargo install cargo-deny
cargo deny init           # Create deny.toml template
```

**Configuration** (`deny.toml`) [^cargo-deny]:
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
is deprecated and will cause warnings or errors with current cargo-deny. The license
allow list above covers common Rust ecosystem licenses; add others as needed (e.g.,
`Unicode-3.0` is used by `unicode-ident`).

**Checks Performed**:

1. **Advisories** - Security vulnerabilities

2. **Licenses** - SPDX license compatibility

3. **Bans** - Disallowed/duplicate dependencies

4. **Sources** - Allowed registry sources

### 4.3 Unused Dependencies (Optional)

**cargo udeps** - Find unused dependencies
```bash
cargo +nightly udeps --all-targets
```

**Note**: Requires **nightly** toolchain.
Use in CI or locally for cleanup.

### 4.4 Unsafe Code Tracking (Optional)

**cargo geiger** - Audit unsafe code usage
```bash
cargo geiger --update
```

**Use Case**: Projects requiring minimal `unsafe` code or security audits

## 5. Documentation

### 5.1 Code Documentation

**Required**:

- Public API documentation (`///` doc comments)

- Module-level docs (`//!`)

- Examples in doc comments (tested via `cargo test --doc`)

**Check**:
```bash
cargo doc --no-deps           # Generate docs
cargo doc --no-deps --open    # Generate and open
```

### 5.2 User Documentation

**Required Files**:

- `README.md` - Quick start, installation, basic usage

- `CHANGELOG.md` - Version history ([keep-a-changelog](https://keepachangelog.com/)
  format)

- `LICENSE` - Project license

- `docs/` - Extended documentation

**Optional Enhancements**:

- `clap_mangen` - Auto-generate man pages from clap definitions [^clap-mangen]

- `mdbook` - Long-form documentation (like Rust CLI Book [^cli-book])

### 5.3 Shell Completions

**`clap_complete`** - Generate shell completion scripts from clap definitions:
```toml
clap_complete = "4.5"
```

Generate completions for bash, zsh, fish, elvish, and PowerShell at build time or via
a hidden CLI subcommand. This gives users tab-completion for all commands, flags, and
arguments with no manual maintenance.

## 6. Build & Release

### 6.1 Build Configuration

**Optimized Release** (`Cargo.toml`):
```toml
[profile.release]
opt-level = 3           # Maximum optimization
lto = true              # Link-time optimization
codegen-units = 1       # Better optimization (slower build)
strip = true            # Strip symbols (smaller binary)
panic = 'abort'         # Smaller binary, faster panic
```

**Target Size**: Expect 2-5MB static binaries for typical CLI tools

### 6.2 Cross-Platform Support

**Common Targets**:

- `x86_64-unknown-linux-gnu` (Linux x86_64)

- `x86_64-unknown-linux-musl` (Linux x86_64 static)

- `x86_64-apple-darwin` (macOS Intel)

- `aarch64-apple-darwin` (macOS Apple Silicon)

- `x86_64-pc-windows-msvc` (Windows x86_64)

- `aarch64-unknown-linux-gnu` (Linux ARM64)

**Build Tools**:

- `cross` - Cross-compilation via Docker

- `cargo-zigbuild` - Cross-compile with Zig

- GitHub Actions matrix builds

### 6.3 Publishing and Release Workflow

**Use `cargo-release`** for version bumping, tagging, and pushing:
```bash
cargo install cargo-release
cargo release patch --execute   # or minor, major
```

**`release.toml` configuration** (based on flowmark-rs):
```toml
publish = false                                 # Let CI handle crates.io publish
tag-prefix = "v"
tag-name = "v{{version}}"
push = true
allow-branch = ["main", "master"]
pre-release-commit-message = "Bump version to {{version}}"
tag-message = "Release {{version}}"
pre-release-hook = ["just", "check"]            # Run all checks before release
```

**Release pattern** (used by ripgrep, bat, fd, jj -- all hand-roll their release CI):
1. `cargo release` bumps version, commits, tags, pushes
2. Tag push triggers release CI workflow
3. Release CI creates GitHub Release, builds cross-platform binaries, publishes to
   crates.io

No major Rust CLI project uses `cargo-dist`. All hand-roll their release workflows.

**Versioning**: Follow [Semantic Versioning](https://semver.org/) (semver)

## 7. Continuous Integration

### 7.1 Essential CI Checks

**Tier 1 (Required for all commits)**:
```yaml
- cargo fmt --all -- --check
- cargo clippy --all-targets --all-features -- -D warnings
- cargo test --all
- cargo audit
```

**Tier 2 (Required before release)**:
```yaml
- cargo deny check
- cargo doc --no-deps
```

**Tier 3 (Optional, run periodically)**:
```yaml
- cargo +nightly udeps --all-targets
- cargo geiger --update
```

### 7.2 GitHub Actions (Modern Pattern)

Split CI into independent parallel jobs for fast feedback. This is the pattern used by
flowmark-rs, jj, and delta. See `tbd guidelines rust-project-setup` for the full
recommended workflow with all 7 jobs.

**Key patterns from real-world projects:**

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
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    name: Clippy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
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
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "ci-${{ matrix.os }}"
      - run: cargo test --all-features --workspace --locked
      - run: cargo test --no-default-features --workspace --locked

  msrv:
    name: MSRV Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@1.85
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features --workspace --locked

  audit:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: rustsec/audit-check@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

  deny:
    name: Dependency Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: EmbarkStudios/cargo-deny-action@v2

  docs:
    name: Documentation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"
```

**Key points:**
- Use `actions/checkout@v6` (current), `dtolnay/rust-toolchain` (not deprecated `actions-rs`)
- `Swatinem/rust-cache@v2` with `shared-key` per job type for cache isolation
- `--locked` in test/build to enforce Cargo.lock reproducibility
- Test with `--no-default-features` to verify library builds without CLI deps
- MSRV job should run `cargo test`, not just `cargo check` (catches runtime issues)
- Use `rustsec/audit-check@v2` action, not `cargo install cargo-audit` (faster)
- Use `EmbarkStudios/cargo-deny-action@v2` (no manual install needed)
- Doc build with `-D warnings` catches broken doc links and missing docs

## 8. Development Workflow

### 8.1 Task Runner: just

Use `just` instead of manual Git hooks or Makefiles. The standard pattern is a
`precommit` target that auto-fixes then verifies:

```bash
just precommit    # Auto-fix formatting + clippy, then run all checks
just check        # Run all CI checks locally (no auto-fix)
just fix          # Auto-fix only (format + clippy)
```

See `tbd guidelines rust-project-setup` for a complete justfile template.

### 8.2 Recommended Tools

**Essential:**

- `just` - Task runner (replaces Makefiles)

- `cargo-audit` - Security vulnerability audit

- `cargo-deny` - Dependency policy (licenses, bans, sources)

- `cargo-release` - Version bumping, tagging, pushing

- `cargo-binstall` - Install pre-built binaries (10-100x faster than compiling)

**Testing:**

- `cargo-nextest` - Faster parallel test runner (used by jj)

**Development:**

- `bacon` - Background code checker (continuous clippy/fmt/test)

- `cargo-watch` - Auto-recompile on file changes

**Analysis:**

- `cargo-bloat` - Find what's taking up space in binary

- `cargo-tree` - Visualize dependency tree (built into cargo: `cargo tree`)

- `cargo-outdated` - Check for dependency updates

- `cargo-udeps` - Find unused dependencies (requires nightly)

- `cargo-expand` - Expand macros for debugging

## 9. Performance Considerations

### 9.1 Rust Performance Advantages

Rust CLI vs interpreted languages:

- **10-100x faster** execution for CPU-bound tasks

- Single static binary (no runtime dependencies)

- Minimal memory footprint

- Instant startup time

- Predictable performance (no GC pauses)

### 9.2 Optimization Techniques

- Use `&str` over `String` where possible

- Minimize allocations in hot paths

- Consider `rayon` for parallel processing

- Profile with `cargo flamegraph` or `perf`

- Use `cargo-llvm-lines` to find bloated code

## 10. Summary Checklist

**Before First Release**:

- [ ] `Cargo.toml` fully configured (edition 2024, MSRV, metadata, license)
- [ ] Library + binary feature-gate pattern (if applicable)
- [ ] `rustfmt.toml` configured; `cargo fmt` passing
- [ ] Lint configuration chosen (pedantic with `priority = -1`, curated list, or defaults)
- [ ] `cargo test` suite with >80% coverage
- [ ] `cargo audit` passing (no vulnerabilities)
- [ ] `deny.toml` configured with v2 schema for license/dependency checks
- [ ] Documentation complete (README, API docs, CHANGELOG)
- [ ] CI/CD pipeline: 7 parallel jobs (fmt, clippy, test, msrv, audit, deny, docs)
- [ ] Cross-platform test matrix (Linux, macOS, Windows)
- [ ] Release profile optimized (LTO, strip, panic=abort)
- [ ] `release.toml` configured for cargo-release
- [ ] Release CI workflow for cross-platform binary builds
- [ ] `justfile` with check/fix/precommit targets
- [ ] `Cargo.lock` committed (for binary projects)

**Maintenance**:

- [ ] `cargo audit` and `cargo deny` run in CI on every push
- [ ] Update dependencies regularly (`cargo update`)
- [ ] Test MSRV compliance on bumps
- [ ] Keep CHANGELOG updated

## References

[^cli-book]: [Command Line Applications in Rust](https://rust-cli.github.io/book/) -
    Official Rust CLI Working Group book

[^cli-recommendations]: [Rain’s Rust CLI
    Recommendations](https://rust-cli-recommendations.sunshowers.io/) - Advanced
    patterns and best practices

[^rust-clippy]: [Clippy Documentation](https://doc.rust-lang.org/clippy/) - Official
    lints documentation

[^clippy-lints]: [Clippy Lint Groups](https://rust-lang.github.io/rust-clippy/master/index.html) -
    Comprehensive lint reference

[^clippy-pedantic]: [Practical Pedantism](https://dystroy.org/blog/practical-pedantism/)
    \- Using clippy::pedantic effectively

[^clippy-workspace]: [clippy::pedantic and Workspace
    Lints](https://coreyja.com/til/clippy-pedantic-workspace) - Workspace-level
    configuration

[^rustsec]: [RustSec Advisory Database](https://rustsec.org/) - Security vulnerability
    tracking

[^cargo-deny]: [cargo-deny Documentation](https://embarkstudios.github.io/cargo-deny/) -
    Dependency validation tool

[^clap-derive]: [Clap Derive Tutorial](https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html)
    \- Modern CLI argument parsing

[^clap-mangen]: [clap_mangen](https://crates.io/crates/clap_mangen) - Auto-generate man
    pages

[^msrv-policy]: [RFC 3537: MSRV-aware
    Resolver](https://rust-lang.github.io/rfcs/3537-msrv-resolver.html) - Cargo MSRV
    support

[^api-guidelines]: [Rust API Guidelines: MSRV
    Policy](https://github.com/rust-lang/api-guidelines/discussions/231) - Semver and
    MSRV

[^rust-edition]: [The Rust Edition Guide](https://doc.rust-lang.org/edition-guide/) -
    Rust editions explained

* * *

**This document is a living reference.**
Cross-referenced against flowmark-rs, ripgrep, bat, fd, and jj as of 2026-02-07.
