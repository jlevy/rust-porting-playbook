# Rust CLI Best Practices

**A reference for building modern, production-ready Rust CLI applications**

**Related:** [Python to Rust CLI Porting Guide](../playbooks/python-to-rust-porting-guide.md) |
[Initial Port Checklist](../playbooks/port-checklist-initial-template.md) |
[Update Checklist](../playbooks/port-checklist-update-template.md)

Version: 1.3 | Last Updated: 2026-03-03

Cross-referenced against real-world projects: flowmark-rs, ripgrep, bat, fd, jj.

For the concise guideline version, see
[Rust Project Setup](../guidelines/rust-project-setup.md).

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

**Workspace Cargo.toml** (Edition 2024 requires `resolver = "3"`):
```toml
[workspace]
members = ["crates/*"]
resolver = "3"                  # Required for Edition 2024 (was "2" for Edition 2021)

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }

[workspace.dependencies]
clap = { version = "4.6", features = ["derive"] }
```
Virtual workspaces (no root `[package]`) must set `resolver` explicitly since there is
no `package.edition` to infer it from.
Non-virtual workspaces with `edition = "2024"` get `resolver = "3"` automatically.

Start with the single-crate pattern and split into a workspace only when you have
concrete reasons (independent versioning, very different dependency sets, 3+ crates).

**Package Naming Conventions**:

- **Repository**: `project-rs` (optional `-rs` suffix for clarity)

- **Library package**: `project` (matches crates.io convention, no suffix)

- **Binary name**: `project` (the actual command users type)

**Rationale**: Professional Rust tools avoid suffixes in package names (ripgrep, fd,
bat) as suffixes “seem like a lesser port”.
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
regex = "1.12"
thiserror = "2.0"

# CLI deps (optional, behind feature gate)
clap = { version = "4.6", features = ["derive", "cargo", "color"], optional = true }
color-eyre = { version = "0.6", optional = true }
```

This lets library users depend on the crate without pulling in CLI-only deps.
Test without default features in CI: `cargo test --no-default-features`

**Edition & MSRV Policy**:

- **Edition 2024** is now standard.
  ripgrep, fd, and jj all use it.
  [^rust-edition]

  - Editions are NOT calendar years -- they’re language versioning markers released
    ~every 3 years

  - Named for when RFC’d, not released (edition 2024 shipped in Rust 1.85, Feb 2025)

  - All editions interoperate seamlessly

- Always declare `rust-version` field for MSRV -- all major projects do this (bat, fd,
  jj, ripgrep) [^msrv-policy]

- MSRV increases are NOT semver-breaking: use minor version bump (1.1.3 → 1.2.0)
  [^api-guidelines]

- Test MSRV compliance in CI (run full `cargo test`, not just `cargo check`)

## 2. Core Dependencies

### 2.1 Essential CLI Libraries

**Argument Parsing**: `clap` (v4+)
```toml
clap = { version = "4.6", features = ["derive", "cargo"] }
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

**Error Handling**: `anyhow` (recommended) or `color-eyre`
```toml
anyhow = "1.0"      # Recommended for new projects -- simple, well-maintained
# OR
color-eyre = "0.6"  # Rich error display with colored backtraces (maintenance-only)
```

- `anyhow` for most projects — actively maintained, simple, ergonomic

- `color-eyre` for projects that need colored backtraces and rich diagnostics.
  Note: `color-eyre` 0.6 is in **maintenance-only mode** (no active feature
  development). It works well but is not receiving new features.

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

### 2.3 Process Exit and Signal Handling

**Exit Codes**: Use `std::process::ExitCode` instead of `std::process::exit()`:
```rust
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::from(1)
        }
    }
}
```

- **Prefer returning `ExitCode`** from `main` over calling `process::exit()` --
  `process::exit()` skips destructors, which can cause resource leaks and data loss

- If you only need success/failure, `fn main() -> Result<(), Error>` with `color-eyre`
  or `anyhow` is simpler and gives you the `?` operator

- Use `ExitCode::from(n)` when you need specific numeric exit codes

**SIGPIPE Handling**: Rust ignores SIGPIPE by default, which causes CLI tools piped to
`head` or similar to panic with “Broken pipe” errors.
Fix this for Unix CLI tools:
```rust
fn main() -> ExitCode {
    // Reset SIGPIPE to default behavior (terminate silently on broken pipe).
    // Without this, `mytool | head` produces spurious "Broken pipe" errors.
    sigpipe::reset();

    // ... rest of main
}
```

```toml
sigpipe = "0.1"    # Stable workaround for Rust's SIGPIPE default
```

- The `sigpipe` crate calls `libc::signal(SIGPIPE, SIG_DFL)` at program start

- An unstable `#[unix_sigpipe = "sig_dfl"]` attribute exists on nightly but is not yet
  stabilized

- This is essential for any CLI tool whose output may be piped

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
unused_qualifications = "warn"    # Catch unnecessary path qualifications
```

**Additional useful restriction lints** (cherry-pick, never enable `restriction` as a
group):
```toml
[lints.clippy]
# From the restriction group -- opt-in individually
print_stderr = "warn"             # Use tracing/logging instead of eprintln!
print_stdout = "warn"             # Use tracing/logging instead of println! (libraries)
dbg_macro = "warn"                # Catch leftover dbg!() calls
```

**Important:** `priority = -1` is required on group lints so that individual overrides
(at the default priority of 0) take precedence.
Without this, the group setting wins and your `"allow"` lines have no effect.

**Three approaches are used in practice:**

- **Blanket pedantic** (flowmark-rs): Enable all pedantic, allow the noisy ones.
  Catches the most but requires more `allow` overrides.

- **Curated lint list** (jj): Cherry-pick specific useful lints like
  `uninlined_format_args`, `use_self`, `explicit_iter_loop`. More maintainable, avoids
  churn when new pedantic lints are added.

- **No lint config** (ripgrep, bat, fd): Just `cargo clippy -- -D warnings` in CI with
  defaults. Simplest.

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
threads), provides better output, and is significantly faster.
Used by jj and many large projects.
Drop-in replacement: `cargo nextest run`.

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
    "MPL-2.0",
    "Unicode-3.0",
    "Unicode-DFS-2016",
    "Zlib",
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

**Important:** Use `version = 2` for `[advisories]` and `[licenses]`. The v1 schema is
deprecated and will cause warnings or errors with current cargo-deny.
The license allow list above covers common Rust ecosystem licenses; add others as needed
(e.g., `Unicode-3.0` is used by `unicode-ident`).

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

### 4.4 Binary Auditing (Recommended)

**cargo-auditable** - Embed dependency metadata in compiled binaries:
```bash
cargo install cargo-auditable
cargo auditable build --release   # Embeds dependency list in the binary
```

This embeds a compressed list of dependencies into the compiled binary, allowing
post-build vulnerability scanning without access to the source or `Cargo.lock`. Anyone
with the binary can run `cargo audit bin ./myproject` to check for known
vulnerabilities. Negligible size and performance overhead (~4KB).

**Policy**: Use `cargo auditable build` in release CI so distributed binaries are
scannable.

### 4.5 Unsafe Code Tracking (Optional)

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
clap_complete = "4.6"
```

Generate completions for bash, zsh, fish, elvish, and PowerShell at build time or via a
hidden CLI subcommand.
This gives users tab-completion for all commands, flags, and arguments with no manual
maintenance.

**Build-time generation** (in `build.rs`):
```rust
use clap::CommandFactory;
use clap_complete::{generate_to, shells::Shell};
use std::env;

fn main() {
    let outdir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let mut cmd = Cli::command();
    for shell in [Shell::Bash, Shell::Zsh, Shell::Fish, Shell::PowerShell] {
        generate_to(shell, &mut cmd, "myproject", &outdir).unwrap();
    }
}
```

**Runtime subcommand** (alternative approach):
```rust
#[derive(Subcommand)]
enum Commands {
    /// Generate shell completions
    Completions {
        #[arg(value_enum)]
        shell: clap_complete::Shell,
    },
}

// In match arm:
Commands::Completions { shell } => {
    clap_complete::generate(shell, &mut Cli::command(), "myproject", &mut std::io::stdout());
}
```

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

**Alternative: `cargo-dist`** (now branded as `dist`): Generates complete CI release
workflows automatically.
Run `dist init` to scaffold a `release.yml` that handles planning, cross-compilation,
artifact upload, and installer generation (shell scripts, Homebrew, MSI). Actively
maintained by axo.dev (v0.31+ as of early 2026). Good for projects that want turnkey releases without
hand-rolling CI. Major projects like ripgrep, bat, and fd hand-roll their release
workflows, but cargo-dist is a solid choice for smaller projects or teams that prefer
convention over configuration.

### 6.4 Release CI Workflow

A tag-triggered orchestrator workflow that builds cross-platform binaries, generates
checksums, and creates a GitHub Release. Optionally invokes channel workflows for
crates.io and PyPI publishing.

**Design principles** (learned from flowmark-rs production release system):
- Use `fail-fast: false` in the build matrix so one target failure doesn't cancel others
- Use `+crt-static` for static linking on musl targets
- Cross-compile Linux ARM64 via apt-get packages + RUSTFLAGS linker overrides (simpler
  and more transparent than `cross` Docker containers)
- Generate SHA256SUMS for all release artifacts
- Use concurrency control to prevent parallel releases of the same tag
- Authenticate with crates.io via OIDC (`rust-lang/crates-io-auth-action@v1`) instead
  of long-lived `CARGO_REGISTRY_TOKEN` secrets

```yaml
name: Release
on:
  push:
    tags: ["*"]
  workflow_dispatch:
    inputs:
      tag:
        description: "Release tag (e.g. v0.2.5). Use dry-run for validation-only."
        required: true
        type: string
        default: dry-run
      publish:
        description: "Publish channels + create GitHub Release"
        type: boolean
        default: false

defaults:
  run:
    shell: bash

env:
  CARGO_TERM_COLOR: always

permissions:
  contents: read

concurrency:
  group: release-${{ github.ref_name || inputs.tag || github.run_id }}
  cancel-in-progress: false

jobs:
  plan:
    runs-on: ubuntu-latest
    outputs:
      release_tag: ${{ steps.plan.outputs.release_tag }}
      artifact_tag: ${{ steps.plan.outputs.artifact_tag }}
      prerelease: ${{ steps.plan.outputs.prerelease }}
      publish: ${{ steps.plan.outputs.publish }}
      publish_channels: ${{ steps.plan.outputs.publish_channels }}
    steps:
      - uses: actions/checkout@v6
      - name: Resolve release mode
        id: plan
        run: python3 ./scripts/resolve_release_plan.py ...
        # See "Release Automation Scripts" section below for the script

  package:
    needs: [plan]
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        target:
          - aarch64-apple-darwin
          - aarch64-unknown-linux-musl
          - x86_64-apple-darwin
          - x86_64-pc-windows-msvc
          - x86_64-unknown-linux-musl
        include:
          - { target: aarch64-apple-darwin, os: macos-latest, target_rustflags: "" }
          - { target: aarch64-unknown-linux-musl, os: ubuntu-latest,
              target_rustflags: "--codegen linker=aarch64-linux-gnu-gcc" }
          - { target: x86_64-apple-darwin, os: macos-latest, target_rustflags: "" }
          - { target: x86_64-pc-windows-msvc, os: windows-latest, target_rustflags: "" }
          - { target: x86_64-unknown-linux-musl, os: ubuntu-latest, target_rustflags: "" }
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Install Linux ARM64 musl deps
        if: matrix.target == 'aarch64-unknown-linux-musl'
        run: sudo apt-get update && sudo apt-get install -y gcc-aarch64-linux-gnu musl-tools

      - name: Install Linux x86_64 musl deps
        if: matrix.target == 'x86_64-unknown-linux-musl'
        run: sudo apt-get update && sudo apt-get install -y musl-tools

      - name: Add Rust target
        run: rustup target add ${{ matrix.target }}

      - name: Build
        run: >-
          RUSTFLAGS="--deny warnings --codegen target-feature=+crt-static
          ${{ matrix.target_rustflags }}"
          cargo build --release --locked --target ${{ matrix.target }}

      - name: Package archive
        id: package
        run: python3 ./scripts/package_release_archive.py
          --artifact-tag "${{ needs.plan.outputs.artifact_tag }}"
          --target "${{ matrix.target }}"
          --runner-os "${{ matrix.os }}"
          --github-output "$GITHUB_OUTPUT"

      - uses: actions/upload-artifact@v4
        with:
          name: release-archives-${{ matrix.target }}
          path: ${{ steps.package.outputs.archive }}

  checksum:
    needs: [plan, package]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: release-archives-*
          merge-multiple: true
          path: release
      - run: (cd release && shasum -a 256 * > ../SHA256SUMS)
      - uses: actions/upload-artifact@v4
        with:
          name: release-checksums
          path: SHA256SUMS

  # Invoke reusable channel workflows (see Multi-Channel Distribution)
  crates:
    needs: [plan, package, checksum]
    uses: ./.github/workflows/publish.yml
    permissions:
      id-token: write
      contents: read
    with:
      publish: ${{ needs.plan.outputs.publish_channels == 'true' }}

  pypi:
    needs: [plan, package, checksum]
    uses: ./.github/workflows/pypi.yml
    permissions:
      id-token: write
      contents: read
    with:
      publish: ${{ needs.plan.outputs.publish_channels == 'true' }}

  announce:
    needs: [plan, checksum, crates, pypi]
    if: needs.plan.outputs.publish == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: release-*
          merge-multiple: true
          path: release
      - uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ needs.plan.outputs.release_tag }}
          prerelease: ${{ needs.plan.outputs.prerelease == 'true' }}
          files: release/*
          generate_release_notes: true
          fail_on_unmatched_files: true
```

**Key points:**
- Use `softprops/action-gh-release@v2` for creating GitHub Releases (not the archived
  `actions/create-release@v1`) with `fail_on_unmatched_files: true`
- Cross-compile Linux ARM64 via `gcc-aarch64-linux-gnu` + RUSTFLAGS linker override
  (no Docker containers needed). This is simpler and more transparent than `cross`.
- Static linking with `--codegen target-feature=+crt-static` for musl targets
- Use `actions/upload-artifact@v4` and `actions/download-artifact@v4` (current versions)
  with `merge-multiple: true` for collecting artifacts from matrix jobs
- SHA256SUMS file generated from all release archives
- `concurrency` block prevents parallel releases of the same tag
- `plan` job with script-driven logic resolves dry-run vs. publish mode
- Channel workflows (`publish.yml`, `pypi.yml`) invoked as reusable `workflow_call`
  workflows with conditional gating
- `permissions: contents: read` at workflow level (least-privilege); `contents: write`
  only on the `announce` job that creates the GitHub Release

**crates.io authentication:** Use OIDC trusted publishing via
`rust-lang/crates-io-auth-action@v1` instead of long-lived `CARGO_REGISTRY_TOKEN`
secrets. This is the same approach used for PyPI trusted publishing — no secrets to
rotate, no tokens to leak.

```yaml
# In publish.yml (crates.io channel)
permissions:
  id-token: write
  contents: read

steps:
  - uses: rust-lang/crates-io-auth-action@v1
    id: auth
  - run: cargo publish --locked
    if: steps.crate.outputs.already_published != 'true'
    env:
      CARGO_REGISTRY_TOKEN: ${{ steps.auth.outputs.token }}
```

### Release Automation Scripts

Complex release workflow logic should live in testable Python scripts, not inline YAML
bash. This is a key pattern from the flowmark-rs project that dramatically improves
maintainability and debuggability of release workflows.

**Why scripts, not YAML:**
- YAML doesn't support conditionals, error handling, or structured output cleanly
- Inline bash in YAML is hard to test, hard to read, and hard to debug
- Python scripts can be unit-tested locally with `unittest`
- Scripts produce structured `$GITHUB_OUTPUT` key-value pairs
- Each script has a clear, single responsibility

**Recommended scripts** (`scripts/` directory):

| Script | Purpose | Key outputs |
| --- | --- | --- |
| `resolve_release_plan.py` | Determine release mode (dry-run vs. publish, stable vs. pre-release) from event type, tag, and inputs | `release_tag`, `artifact_tag`, `prerelease`, `publish`, `publish_channels` |
| `package_release_archive.py` | Create platform-specific archives (.tar.gz/.zip) with LICENSE and README | `archive` (filename) |
| `resolve_crate_metadata.py` | Extract name/version from Cargo.toml, query crates.io API to detect already-published versions | `crate_name`, `crate_version`, `already_published` |
| `validate_wheel_entrypoints.py` | Verify expected binaries exist in all built wheels | (exits non-zero on failure) |
| `pypi_smoke_test.py` | Install wheel, run `--version` check; auto-skip cross-compiled targets | (exits non-zero on failure) |

**Common patterns in these scripts:**

1. **GitHub Actions output:** All scripts write to `$GITHUB_OUTPUT` via a shared helper:
   ```python
   def _write_outputs(outputs: dict[str, str], github_output_path: str | None) -> None:
       lines = [f"{key}={value}" for key, value in outputs.items()]
       for line in lines:
           print(line)
       if github_output_path:
           with Path(github_output_path).open("a") as f:
               for line in lines:
                   f.write(f"{line}\n")
   ```

2. **Idempotency detection:** The crate metadata script queries the registry API to
   check if a version already exists before publishing:
   ```python
   def _crate_version_exists(registry_url: str, name: str, version: str) -> bool:
       url = f"{registry_url.rstrip('/')}/{name}/{version}"
       try:
           urllib.request.urlopen(url, timeout=10)
           return True
       except urllib.error.HTTPError as exc:
           if exc.code == 404:
               return False
           raise
   ```

3. **Platform-aware smoke testing:** The PyPI smoke test detects the runner's OS and
   architecture, then skips tests for cross-compiled targets that can't run natively:
   ```python
   def _skip_reason(target: str, runner_os: str, runner_arch: str) -> str | None:
       target_os, target_arch = _target_os_and_arch(target)
       if target_os != runner_os:
           return f"target OS {target_os} != runner OS {runner_os}"
       if target_arch != runner_arch:
           return f"target arch {target_arch} != runner arch {runner_arch}"
       return None
   ```

4. **Unit tests for all scripts:** Each script has tests in `scripts/tests/`:
   ```
   scripts/
   ├── resolve_release_plan.py
   ├── package_release_archive.py
   ├── resolve_crate_metadata.py
   ├── validate_wheel_entrypoints.py
   ├── pypi_smoke_test.py
   └── tests/
       ├── test_resolve_release_plan.py
       ├── test_package_release_archive.py
       ├── test_resolve_crate_metadata.py
       └── test_validate_wheel_entrypoints.py
   ```
   Run in CI with: `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v`

**Archive naming convention** (compatible with `cargo-binstall`):
`<project>-v<version>-<target>.tar.gz` (Unix) or `.zip` (Windows).
Each archive includes the binary, LICENSE, and README.

**Versioning**: Follow [Semantic Versioning](https://semver.org/) (semver)

### 6.5 Multi-Channel Distribution

For production Rust CLI tools, distribute through multiple channels to maximize reach.
The flowmark-rs project provides a proven template: three coordinated channels
(crates.io, PyPI, Homebrew) orchestrated by a single release workflow.

**Channel overview:**

| Channel | Audience | Install command | Mechanism |
| --- | --- | --- | --- |
| **PyPI via uv** | General users (recommended) | `uvx <name>` / `uv tool install <name>` / `pip install <name>` | maturin `bindings = "bin"` — packages Rust binary into Python wheel |
| **crates.io** | Rust developers | `cargo install <name>` / `cargo binstall <name>` | `cargo publish` with OIDC trusted publisher |
| **Homebrew** | macOS users | `brew install <tap>/<name>` | Personal tap with SHA256-pinned formula |
| **GitHub Releases** | Direct downloads | Browser / curl | Binary archives (.tar.gz, .zip) + SHA256SUMS |

#### Why PyPI/uv Is the Recommended Distribution Channel

**PyPI via uv is the recommended primary distribution channel for Rust CLI binaries**
that target a broad audience, not just Rust developers. The reasons:

1. **Zero bootstrapping:** uv is now standard in modern Python environments. Most
   developer machines already have uv or pip installed. In contrast, `cargo binstall`
   requires a Rust toolchain or a separate install step.

2. **Cross-platform out of the box:** `uvx <tool>` works on Linux, macOS, and Windows
   with the same command. Platform selection is automatic via wheel tags.

3. **Instant ephemeral execution:** `uvx <tool>` downloads and runs the binary in a
   single command with no persistent install needed. There is no cargo equivalent to
   this — `cargo install` compiles from source (takes minutes) and requires a full Rust
   toolchain, while `cargo binstall` requires installing a separate tool first and has
   no ephemeral run mode. `uvx` is the closest thing Rust CLIs have to `npx` — and it
   works without any Rust infrastructure.

4. **Established pattern:** This is how **ruff**, **uv**, and **maturin** itself are
   distributed. These are among the most-installed Rust CLI tools in the world.

5. **No Rust toolchain required:** Users do not need `rustc`, `cargo`, or any Rust
   infrastructure. The binary is pre-compiled and packaged into a Python wheel.

6. **Familiar to the Python ecosystem:** For Python-to-Rust ports, this preserves the
   exact install experience that existing users expect (`pip install <tool>` or
   `uvx <tool>`).

For Rust developers, crates.io (`cargo install` / `cargo binstall`) remains the natural
channel. For macOS power users, a Homebrew tap provides `brew install` convenience.
But for general distribution, PyPI via uv has the broadest reach with the least friction.

#### PyPI Distribution via Maturin

Distributing Rust CLI binaries on PyPI via maturin packages the compiled binary into
a Python wheel. This is the mechanism behind `uvx <tool>`, `uv tool install <tool>`,
and `pip install <tool>` for Rust CLIs.

**Minimal `pyproject.toml`** (at repo root, alongside `Cargo.toml`):
```toml
[build-system]
requires = ["maturin>=1.9,<2.0"]
build-backend = "maturin"

[project]
name = "myproject-rs"
description = "Short description"
requires-python = ">=3.8"
license = { text = "MIT" }
dynamic = ["version"]       # Reads version from Cargo.toml automatically

[tool.maturin]
bindings = "bin"             # Standalone CLI binary, not a Python extension
strip = true                 # Strip debug symbols for smaller wheels
```

**How it works:**
- Maturin compiles the Rust binary and places it into the wheel's `.data/scripts/`
- pip/uv installs it into the appropriate `bin/` directory
- No Python code runs at binary invocation — it is pure Rust
- Platform tags (e.g., `manylinux_2_17_x86_64`) ensure the correct wheel is selected

**Versioning:** Use `dynamic = ["version"]` so maturin reads the version from
`Cargo.toml`. This avoids maintaining version numbers in two places.
Ruff and uv use manual sync instead (via rooster) because they are Cargo workspaces,
but for single-crate projects, dynamic versioning is simpler and less error-prone.

**Standard platform targets** (covers ~99% of users):

| Target | Platform Tag | Runner |
| --- | --- | --- |
| `x86_64-unknown-linux-gnu` | `manylinux_2_17_x86_64` | `ubuntu-latest` |
| `aarch64-unknown-linux-gnu` | `manylinux_2_17_aarch64` | `ubuntu-latest` |
| `x86_64-apple-darwin` | `macosx_10_12_x86_64` | `macos-13` or `macos-14` |
| `aarch64-apple-darwin` | `macosx_11_0_arm64` | `macos-14` |
| `x86_64-pc-windows-msvc` | `win_amd64` | `windows-latest` |

Add musl targets (`musllinux_1_2_*`) for Alpine Linux support if needed.

**PyPI workflow** (`pypi.yml`, reusable):
```yaml
name: PyPI
on:
  workflow_call:
    inputs:
      publish:
        type: boolean
        default: false
  workflow_dispatch:

jobs:
  build:
    name: Build (${{ matrix.target }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - { target: x86_64-unknown-linux-gnu, os: ubuntu-latest, manylinux: "2_17" }
          - { target: aarch64-unknown-linux-gnu, os: ubuntu-latest, manylinux: "2_17" }
          - { target: x86_64-apple-darwin, os: macos-14 }
          - { target: aarch64-apple-darwin, os: macos-14 }
          - { target: x86_64-pc-windows-msvc, os: windows-latest }
    steps:
      - uses: actions/checkout@v6
      - uses: PyO3/maturin-action@v1
        with:
          command: build
          args: --release --locked --out dist
          target: ${{ matrix.target }}
          manylinux: ${{ matrix.manylinux || 'auto' }}
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.target }}
          path: dist/*.whl

  sdist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: PyO3/maturin-action@v1
        with:
          command: sdist
          args: --out dist
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-sdist
          path: dist/*.tar.gz

  publish:
    if: inputs.publish
    needs: [build, sdist]
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write
    steps:
      - uses: astral-sh/setup-uv@v7
      - uses: actions/download-artifact@v4
        with:
          pattern: wheels-*
          merge-multiple: true
          path: wheels/
      - run: uv publish --trusted-publishing always --check-url wheels/*
```

**Key points:**
- Use `PyO3/maturin-action@v1` for cross-platform wheel builds (pin the version)
- Use `uv publish --trusted-publishing always` with OIDC (no long-lived API tokens)
- Add `--check-url` to skip already-published versions (idempotent reruns)
- Set up trusted publishing on PyPI: link your GitHub repo/workflow to the PyPI project
- Include an sdist for users who want to build from source on unsupported platforms

For detailed research on this pattern, see
[research-rust-cli-pypi-distribution.md](../docs/project/research/research-rust-cli-pypi-distribution.md).

#### Homebrew Tap Distribution

For macOS users, a personal Homebrew tap provides `brew install` access.

**Setup:**
1. Create a tap repository: `<user>/homebrew-<project>`
2. Add a formula that downloads the GitHub Release binary archive
3. Pin SHA256 checksums from the release's `SHA256SUMS` file

**Formula template** (`Formula/<project>.rb`):
```ruby
class MyProject < Formula
  desc "Short description"
  homepage "https://github.com/<user>/<project>"
  version "X.Y.Z"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/<user>/<project>/releases/download/vX.Y.Z/<project>-vX.Y.Z-aarch64-apple-darwin.tar.gz"
      sha256 "<sha256>"
    end
    on_intel do
      url "https://github.com/<user>/<project>/releases/download/vX.Y.Z/<project>-vX.Y.Z-x86_64-apple-darwin.tar.gz"
      sha256 "<sha256>"
    end
  end

  def install
    bin.install "<binary-name>"
  end
end
```

**Update process:** After each GitHub Release, extract SHA256 checksums from the release
assets and update the formula version and hashes. This is typically a manual step to keep
auditable.

#### Orchestrated Multi-Channel Releases

For projects publishing to multiple channels, use a single orchestrator workflow that
coordinates all channels. The flowmark-rs pattern:

```
cargo release patch --execute
  → tag push triggers release.yml (orchestrator)
    ├── plan job: resolve release mode (dry-run vs. publish, stable vs. pre-release)
    ├── package job: build 6 targets → GitHub Release artifacts + SHA256SUMS
    ├── publish.yml (reusable): test → dry-run → crates.io publish
    ├── pypi.yml (reusable): maturin build 5 targets → PyPI publish
    └── announce job: create/update GitHub Release (gated on success)
```

**Key orchestration patterns:**

1. **Reusable channel workflows:** Both `publish.yml` (crates.io) and `pypi.yml` (PyPI)
   are reusable workflows (`workflow_call`) that can also be triggered independently via
   `workflow_dispatch`. This enables testing channels in isolation.

2. **Script-driven decision logic:** Complex release decisions (semver parsing,
   dry-run detection, idempotency checks) live in testable Python scripts
   (`scripts/*.py`), not inline YAML. Each script has unit tests.

3. **Idempotent publishing:** Each channel detects already-published versions and skips:
   - crates.io: API query before publish
   - PyPI: `uv publish --check-url`
   - GitHub Releases: naturally idempotent (updates existing)

4. **Concurrency control:** Prevent parallel releases of the same tag:
   ```yaml
   concurrency:
     group: release-${{ github.ref_name || inputs.tag }}
     cancel-in-progress: false
   ```

5. **Conditional channel gating:** Orchestrator outputs control which channels publish:
   ```yaml
   crates:
     uses: ./.github/workflows/publish.yml
     with:
       publish: ${{ needs.plan.outputs.publish_channels == 'true' }}
   ```

#### References (Multi-Channel Distribution)

**Maturin and PyPI distribution:**
- [Maturin User Guide — Distribution](https://www.maturin.rs/distribution.html)
- [Maturin — Bindings](https://www.maturin.rs/bindings) (`bin` mode for CLI binaries)
- [PyO3/maturin-action](https://github.com/PyO3/maturin-action) (GitHub Actions)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (OIDC setup)

**Real-world examples (Rust CLIs distributed via PyPI):**
- [astral-sh/ruff](https://github.com/astral-sh/ruff) — pyproject.toml, CI workflows
- [astral-sh/uv](https://github.com/astral-sh/uv) — pyproject.toml, CI workflows
- [jlevy/flowmark-rs](https://github.com/jlevy/flowmark-rs) — multi-channel publishing

**GitHub Actions used in workflows:**
- [actions/checkout@v6](https://github.com/actions/checkout)
- [dtolnay/rust-toolchain](https://github.com/dtolnay/rust-toolchain)
- [Swatinem/rust-cache@v2](https://github.com/Swatinem/rust-cache)
- [softprops/action-gh-release@v2](https://github.com/softprops/action-gh-release)
- [EmbarkStudios/cargo-deny-action@v2](https://github.com/EmbarkStudios/cargo-deny-action)
- [obi1kenobi/cargo-semver-checks-action@v2](https://github.com/obi1kenobi/cargo-semver-checks-action)
- [taiki-e/install-action](https://github.com/taiki-e/install-action) (cargo-llvm-cov)
- [codecov/codecov-action@v5](https://github.com/codecov/codecov-action)
- [rust-lang/crates-io-auth-action@v1](https://github.com/rust-lang/crates-io-auth-action) (OIDC)

**Platform tags and wheel specifications:**
- [PEP 600 — Future manylinux](https://peps.python.org/pep-0600/)
- [PEP 656 — musllinux](https://peps.python.org/pep-0656/)
- [Python Packaging: Platform Compatibility Tags](https://packaging.python.org/specifications/platform-compatibility-tags/)

## 7. Continuous Integration

### 7.1 Essential CI Checks

**Tier 1 (Required for all commits)**:
```yaml
- cargo fmt --all -- --check
- cargo clippy --locked --all-targets --all-features -- -D warnings
- cargo test --all-features --workspace --locked
- cargo deny check
```

**Tier 2 (Required before release)**:
```yaml
- cargo doc --locked --no-deps --all-features   # with RUSTDOCFLAGS="-D warnings"
- MSRV check (cargo check with pinned toolchain)
- cargo-semver-checks (on PRs)
- Code coverage (cargo-llvm-cov + Codecov)
```

**Tier 3 (Optional, run periodically)**:
```yaml
- cargo +nightly udeps --all-targets
- cargo geiger --update
```

### 7.2 GitHub Actions (Modern Pattern)

Split CI into independent parallel jobs for fast feedback.
This is the pattern used by flowmark-rs (13 jobs), jj, and delta.
See [Rust Project Setup](../guidelines/rust-project-setup.md) for the condensed version.

**CI environment variables** — set globally for all jobs:
```yaml
env:
  CARGO_TERM_COLOR: always
  CARGO_INCREMENTAL: 0            # Faster CI builds (no incremental overhead)
  CARGO_PROFILE_TEST_DEBUG: 0     # Smaller test binaries, faster CI
```

These speed up CI builds significantly. `CARGO_INCREMENTAL: 0` disables incremental
compilation (useless in CI where each build starts fresh) and
`CARGO_PROFILE_TEST_DEBUG: 0` skips debug info for test binaries.

**Complete CI workflow** (13 jobs from flowmark-rs production setup):

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

env:
  CARGO_TERM_COLOR: always
  CARGO_INCREMENTAL: 0
  CARGO_PROFILE_TEST_DEBUG: 0

jobs:
  fmt:
    name: Format check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    name: Clippy lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
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
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --all-features
        env:
          RUSTFLAGS: "-D warnings"

  test-lib-only:
    name: Test library (no default features)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --no-default-features
        env:
          RUSTFLAGS: "-D warnings"

  msrv:
    name: MSRV check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@1.85    # Pin to declared rust-version
      - uses: Swatinem/rust-cache@v2
      - run: cargo check --locked --all-features

  deny:
    name: Dependency audit
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
      - run: cargo doc --locked --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"

  coverage:
    name: Code coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-llvm-cov
      - run: cargo llvm-cov --locked --all-features --lcov --output-path lcov.info
        env:
          RUSTFLAGS: "-D warnings"
      - uses: codecov/codecov-action@v5
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
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - uses: obi1kenobi/cargo-semver-checks-action@v2

  workflow-scripts:
    name: Workflow script tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
```

**Key points:**
- Use `actions/checkout@v6` (current), `dtolnay/rust-toolchain` (not deprecated
  `actions-rs`)
- `Swatinem/rust-cache@v2` for build caching across jobs
- `--locked` on all cargo commands enforces Cargo.lock reproducibility
- `RUSTFLAGS: "-D warnings"` in test/build jobs treats warnings as errors
- `test-lib-only` verifies library builds without CLI feature deps
- `coverage` uses `cargo-llvm-cov` with `taiki-e/install-action` (faster than
  `cargo install`) and reports to Codecov
- `semver-checks` runs only on PRs (needs `fetch-depth: 0` for baseline comparison)
  to catch API-breaking changes before merge
- `workflow-scripts` validates the testable release automation scripts
  (see [Release Automation Scripts](#release-automation-scripts) below)
- Use `EmbarkStudios/cargo-deny-action@v2` (no manual install needed)
- Doc build with `-D warnings` catches broken doc links and missing docs
- Set `CARGO_INCREMENTAL: 0` and `CARGO_PROFILE_TEST_DEBUG: 0` globally for faster
  CI builds

### 7.3 Parity Drift Detection for Ports

When porting from another language (Python, TypeScript, etc.), prevent gradual
divergence from the source implementation by enforcing parity in CI.

**Problem:** Without automated checks, the Rust port can drift from the source as:
- New tests are added to the source but not ported
- Source bugs are fixed but not reflected in the port
- Rust-only tests are added without verifying source behavior

**Solution:** Cross-language test mapping as a CI hard gate.

#### Test Mapping Validation

Maintain a YAML manifest (`test-mapping.yaml`) that maps every source test to its Rust
equivalent(s), then validate completeness in CI:

```yaml
test-mapping:
  name: Test Mapping Check
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v6
      with:
        submodules: true  # If source is a submodule
    - uses: dtolnay/rust-toolchain@stable
    - run: cargo test --list > rust-tests.txt
    - run: python scripts/check-mapping.py
```

**Check script** (`scripts/check-mapping.py`):
```python
# Verify that test-mapping.yaml accounts for all source tests
# Report: missing, excluded (with reasons), partial (split tests)
# Exit non-zero if any tests are unmapped without justification
```

**See also:** [Cross-Language Test Mapping](cross-language-test-mapping.md)
for the full YAML schema and tooling patterns.

#### Smoke Test for Test Count

Add an assertion on total test count to catch unmapped tests:

```python
# In source repo: tests/test_smoke.py
def test_rust_port_completeness():
    """Verify Rust port has expected test count."""
    result = subprocess.run(
        ["cargo", "test", "--list"],
        capture_output=True, text=True, cwd="../rust-port"
    )
    rust_test_count = len([l for l in result.stdout.splitlines() if ": test" in l])

    # Update this number when new tests are added
    assert rust_test_count >= 442, \
        f"Rust port has {rust_test_count} tests, expected >= 442"
```

Update the threshold whenever new tests are added to either repo.

#### Dynamic Corpus Validation

Run both implementations over a shared corpus and diff outputs:

```yaml
cross-validation:
  name: Cross-Validation
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v6
      with:
        submodules: true
    - name: Set up source environment
      run: |
        cd python-repo
        uv sync
    - name: Build Rust
      run: cargo build --release
    - name: Run cross-validation
      run: |
        ./scripts/cross-validate.sh test-corpus/
        # Fails if any diffs between Python and Rust output
```

This catches behavioral drift that unit tests might miss (e.g., whitespace changes,
Unicode handling, edge case regressions).

**Example:** flowmark-rs enforces 100% test mapping coverage in CI and maintains a
292-test mapping manifest.
Any unmapped Python test causes CI to fail.

## 8. Development Workflow

### 8.1 Task Runner: just

Use `just` instead of manual Git hooks or Makefiles.
The standard pattern is a `precommit` target that auto-fixes then verifies:

```bash
just precommit    # Auto-fix formatting + clippy, then run all checks
just check        # Run all CI checks locally (no auto-fix)
just fix          # Auto-fix only (format + clippy)
```

See [Rust Project Setup](../guidelines/rust-project-setup.md) for a complete justfile
template.

### 8.2 Recommended Tools

**Essential:**

- `just` - Task runner (replaces Makefiles)

- `cargo-audit` - Security vulnerability audit

- `cargo-deny` - Dependency policy (licenses, bans, sources)

- `cargo-release` - Version bumping, tagging, pushing

- `cargo-binstall` - Install pre-built binaries (10-100x faster than compiling)

- `cargo-auditable` - Embed dependency metadata in release binaries

**Release:**

- `cargo-dist` (dist) - Automated release CI generation and binary packaging

**Testing:**

- `cargo-nextest` - Faster parallel test runner (used by jj)

**Development:**

- `bacon` - Background code checker (continuous clippy/fmt/test)

- `cargo-watch` - Auto-recompile on file changes

**Analysis:**

- `cargo-bloat` - Find what’s taking up space in binary

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
- [ ] Workspace uses `resolver = "3"` (Edition 2024; virtual workspaces must set
  explicitly)
- [ ] Library + binary feature-gate pattern (if applicable)
- [ ] `rustfmt.toml` configured; `cargo fmt` passing
- [ ] Lint configuration chosen (pedantic with `priority = -1`, curated list, or
  defaults)
- [ ] `cargo test` suite with >80% coverage
- [ ] `cargo audit` passing (no vulnerabilities)
- [ ] `deny.toml` configured with v2 schema for license/dependency checks
- [ ] Documentation complete (README, API docs, CHANGELOG)
- [ ] Shell completions via `clap_complete` (build-time or runtime subcommand)
- [ ] CI/CD pipeline: 7 parallel jobs (fmt, clippy, test, msrv, audit, deny, docs)
- [ ] Cross-platform test matrix (Linux, macOS, Windows)
- [ ] Release profile optimized (LTO, strip, panic=abort)
- [ ] `release.toml` configured for cargo-release
- [ ] Release CI workflow for cross-platform binary builds
  (softprops/action-gh-release@v2)
- [ ] `justfile` with check/fix/precommit targets
- [ ] `Cargo.lock` committed (for binary projects)
- [ ] SIGPIPE handling: `sigpipe::reset()` at start of main (Unix CLI tools)
- [ ] Exit codes: return `ExitCode` from main instead of calling `process::exit()`

**Maintenance**:

- [ ] `cargo audit` and `cargo deny` run in CI on every push
- [ ] Update dependencies regularly (`cargo update`)
- [ ] Test MSRV compliance on bumps
- [ ] Keep CHANGELOG updated
- [ ] Use `cargo auditable build` in release CI for scannable binaries

## References

[^cli-book]: [Command Line Applications in Rust](https://rust-cli.github.io/book/) -
    Official Rust CLI Working Group book

[^cli-recommendations]: [Rain’s Rust CLI Recommendations](https://rust-cli-recommendations.sunshowers.io/) -
    Advanced patterns and best practices

[^rust-clippy]: [Clippy Documentation](https://doc.rust-lang.org/clippy/) - Official
    lints documentation

[^clippy-lints]: [Clippy Lint Groups](https://rust-lang.github.io/rust-clippy/master/index.html) -
    Comprehensive lint reference

[^clippy-pedantic]: [Practical Pedantism](https://dystroy.org/blog/practical-pedantism/)
    \- Using clippy::pedantic effectively

[^clippy-workspace]: [clippy::pedantic and Workspace Lints](https://coreyja.com/til/clippy-pedantic-workspace)
    \- Workspace-level configuration

[^rustsec]: [RustSec Advisory Database](https://rustsec.org/) - Security vulnerability
    tracking

[^cargo-deny]: [cargo-deny Documentation](https://embarkstudios.github.io/cargo-deny/) -
    Dependency validation tool

[^clap-derive]: [Clap Derive Tutorial](https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html)
    \- Modern CLI argument parsing

[^clap-mangen]: [clap_mangen](https://crates.io/crates/clap_mangen) - Auto-generate man
    pages

[^msrv-policy]: [RFC 3537: MSRV-aware Resolver](https://rust-lang.github.io/rfcs/3537-msrv-resolver.html)
    \- Cargo MSRV support

[^api-guidelines]: [Rust API Guidelines: MSRV Policy](https://github.com/rust-lang/api-guidelines/discussions/231)
    \- Semver and MSRV

[^rust-edition]: [The Rust Edition Guide](https://doc.rust-lang.org/edition-guide/) -
    Rust editions explained

[^cargo-dist]: [cargo-dist (dist)](https://opensource.axo.dev/cargo-dist/) - Automated
    release packaging and distribution by axo.dev

[^sigpipe]: [SIGPIPE in Rust](https://github.com/rust-lang/rust/issues/62569) - Tracking
    issue for Rust’s SIGPIPE default behavior

[^exitcode]: [ExitCode](https://doc.rust-lang.org/stable/std/process/struct.ExitCode.html) -
    std::process::ExitCode documentation

[^cargo-auditable]: [cargo-auditable](https://github.com/rust-secure-code/cargo-auditable) - Embed
    dependency info in binaries for post-build auditing

[^clap-complete]: [clap_complete](https://docs.rs/clap_complete/latest/clap_complete/) -
    Shell completion generation for clap

* * *

**This document is a living reference.** Cross-referenced against flowmark-rs, ripgrep,
bat, fd, and jj as of 2026-02-12.
