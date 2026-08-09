---
title: Rust Project Setup
description: Rules for structuring, validating, and maintaining modern Rust packages and workspaces
category: rust
---
# Rust Project Setup

Use this guideline when starting or modernizing a Rust package, application, or
workspace. It defines the project-level quality floor: Cargo metadata, package
boundaries, toolchains, linting, CI, documentation, and dependency policy.

**Related:** [`rust-rules.md`](rust-rules.md),
[`rust-testing-rules.md`](rust-testing-rules.md),
[`rust-release-rules.md`](rust-release-rules.md), and
`tbd guidelines supply-chain-hardening`.

## Choose the Smallest Package Shape That Fits

Start with one package unless the code has a concrete reason to be split.

- **Library only:** one `[lib]` target for a reusable API.
- **Binary only:** one `[[bin]]` target when no library surface is useful.
- **Library and binary:** keep domain behavior in the library and make the binary a thin
  process boundary.
- **Workspace:** use separate packages when they need different release lifecycles,
  dependency sets, platform constraints, or public APIs.

Do not create a workspace only to imitate a large project.
Every package boundary adds feature resolution, publishing, ownership, and CI
complexity.

```text
project/
├── Cargo.toml
├── Cargo.lock
├── rust-toolchain.toml
├── src/
│   ├── lib.rs
│   └── main.rs
├── tests/
├── docs/
└── .github/workflows/
```

## Declare the Package Contract

Every published package should declare its edition, MSRV, license, repository, readme,
and a concise description.
Use a valid SPDX expression for `license`.

```toml
[package]
name = "example"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"
description = "A concise description"
repository = "https://github.com/example/example"
readme = "README.md"
```

For a workspace, centralize shared metadata, dependencies, and lint policy:

```toml
[workspace]
members = ["crates/*"]
resolver = "3"

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.lints.rust]
unsafe_code = "forbid"
```

Virtual workspaces must declare the resolver because there is no root package edition
from which Cargo can infer it.

## Separate Optional Surfaces With Features

Use features to prevent consumers from paying for functionality they do not use.
CLI, network, database, and platform integration dependencies are common feature
boundaries.

```toml
[features]
default = ["cli"]
cli = ["dep:clap"]

[[bin]]
name = "example"
path = "src/main.rs"
required-features = ["cli"]
```

- Keep the core library buildable with `--no-default-features` when that is part of the
  package contract.
- Avoid feature combinations that change the meaning of the same public API.
- Test the feature sets users are expected to build; do not assume `--all-features`
  covers mutually exclusive configurations.
- Use target-specific dependencies for OS-specific integrations instead of compiling
  unused platform code everywhere.

## Pin the Development Toolchain Deliberately

Use `rust-toolchain.toml` when contributors and CI should use the same Rust release and
components:

```toml
[toolchain]
channel = "1.97.1"
components = ["clippy", "rustfmt"]
profile = "minimal"
```

The normal toolchain pin and the MSRV serve different purposes:

- the normal pin makes development and CI reproducible;
- `rust-version` states the oldest compiler supported by the package;
- a separate CI job proves the package still builds on the MSRV.

Review and update the toolchain pin intentionally.
Do not use a moving `stable` channel in a reproducibility-sensitive workflow and assume
the result will remain unchanged.

## Let rustfmt Own Formatting

Run rustfmt in fix mode locally and verification mode in CI:

```bash
cargo fmt --all
cargo fmt --all -- --check
```

Keep `rustfmt.toml` small.
Edition should match the package; other settings require a clear readability or
generated-code reason.

```toml
edition = "2024"
max_width = 100
```

Do not mix manual layout rules with rustfmt output.
Format Markdown, TOML, YAML, JSON, and scripts with their appropriate formatters too.

## Define a Clippy Policy

Choose and document one lint strategy:

1. default Clippy lints plus `-D warnings`;
2. a curated set of additional lints; or
3. `clippy::pedantic` with explicit, reviewed exceptions.

For group lints, use a lower priority so specific overrides win:

```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
missing_errors_doc = "allow"
missing_panics_doc = "allow"
module_name_repetitions = "allow"

[lints.rust]
unsafe_code = "forbid"
```

- Never enable the entire Clippy `restriction` group.
  Select individual rules whose tradeoffs fit the project.
- Treat warnings as errors in CI, not necessarily in every local build.
- Add `#[allow(...)]` at the narrowest scope and explain a non-obvious exception.
- Remove obsolete exceptions when the triggering code changes.

## Make One Local Command Match CI

Contributors and CI should run the same named validation entry point, implemented with
`just`, a checked-in script, or another project-standard task runner.

The baseline normally includes:

```bash
cargo fmt --all -- --check
cargo clippy --locked --workspace --all-targets --all-features -- -D warnings
cargo test --locked --workspace --all-features
cargo doc --locked --workspace --all-features --no-deps
```

Add the checks that define the actual project contract:

- MSRV compilation or tests
- no-default-feature and selected-feature builds
- cross-platform tests
- documentation warnings as errors
- dependency policy and advisory scans
- code coverage or semver checks
- tests for release and maintenance scripts

Keep auto-fix and verification separate.
CI verifies; it never commits formatter or lint changes.

## Design CI as Independent Evidence

Use separate jobs when failures answer different questions, such as formatting, linting,
unit tests, platform compatibility, MSRV, docs, or dependency policy.
Parallel jobs improve feedback, but a large matrix without a supported-platform policy
creates cost without clarity.

CI workflows should:

- start with read-only permissions and grant additional permissions per job;
- pin third-party actions to reviewed immutable commit SHAs;
- use `--locked` for Cargo commands that consume the committed lockfile;
- pin or derive the Rust toolchain from reviewed repository configuration;
- avoid downloading and executing unpinned tools at runtime;
- make caches performance-only, never a source of correctness;
- retain actionable logs and fail when a required check did not run.

For release-only permissions and publishing, see
[`rust-release-rules.md`](rust-release-rules.md).

## Apply Dependency and Supply-Chain Policy

Every dependency can execute code at build time through its own `build.rs`, proc macros,
native build tooling, or transitive dependencies.
Treat additions and upgrades as code changes.

- Apply the repository’s cool-off period before adopting a new release.
- Record a concrete reason for adding or upgrading a crate.
- Read new or changed `build.rs` scripts and proc-macro source.
- Review the exact source diff and release notes for an upgrade.
- Minimize enabled features and default features.
- Prefer registry sources; justify git dependencies and pin them to immutable commits.
- Run RustSec, OSV, license, source, and duplicate-version policy checks as appropriate.
- Use `cargo tree` to understand ownership of transitive dependencies.
- Use an unused-dependency tool as supporting evidence, then verify removals by build
  and test.

Commit `Cargo.lock` for applications, binaries, and workspaces that ship or deploy a
resolved tree. For a library-only repository, choose and document a lockfile policy;
remember that downstream users resolve their own graph even when the repository keeps a
lockfile for CI.

The authoritative cross-ecosystem policy is `tbd guidelines supply-chain-hardening` and
this repository’s [`SUPPLY-CHAIN-SECURITY.md`](../SUPPLY-CHAIN-SECURITY.md).

## Keep Development Automation Reviewable

A task runner is useful when it names stable operations such as `format`, `lint`,
`test`, `check`, and `precommit`. It should orchestrate checked-in commands, not hide
network installs or environment mutation.

- Put complex logic in typed or testable scripts rather than long YAML or shell blocks.
- Make scripts accept explicit inputs and return non-zero on partial failure.
- Test failure paths and machine-readable outputs.
- Do not overwrite user configuration as a side effect of ordinary validation.
- Keep editor tasks, agent hooks, and local bootstrap scripts subject to the same review
  and pinning policy as CI.

## Document the Supported Surface

Published projects normally need:

- `README.md` for purpose, installation, and a minimal example;
- license files that match the manifest expression;
- release notes or a changelog according to project policy;
- public API documentation and doctests;
- a security reporting path;
- supported-platform, feature, MSRV, and deprecation policies;
- extended docs only where the README would become difficult to navigate.

Build docs with warnings denied where practical:

```bash
RUSTDOCFLAGS="-D warnings" cargo doc --locked --workspace --all-features --no-deps
```

## Keep Repository Configuration Minimal

Typical repository files include:

```text
Cargo.toml
Cargo.lock
rust-toolchain.toml
rustfmt.toml
README.md
LICENSE-MIT
LICENSE-APACHE
.gitattributes
.gitignore
```

- Ignore build output such as `/target`, not source or lock data needed for a clean
  checkout.
- Use `.gitattributes` to make text newline policy explicit across platforms.
- Do not add generated files unless consumers need them or regeneration is not
  sufficiently deterministic.
- Keep source checkouts used for comparison, vendoring, or fixtures governed by an
  explicit provenance and update policy.

## Related Guidelines

- [`rust-rules.md`](rust-rules.md) for language and API design
- [`rust-testing-rules.md`](rust-testing-rules.md) for test architecture and coverage
- [`rust-release-rules.md`](rust-release-rules.md) for release artifacts and publishing
- [`rust-code-review-rules.md`](rust-code-review-rules.md) for review gates
- `tbd guidelines supply-chain-hardening commit-conventions`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
