---
title: "Research: Distributing Rust CLI Binaries as Python Packages via PyPI"
status: complete
date: 2026-03-01
last_reviewed: 2026-07-13
---
# Research: Distributing Rust CLI Binaries as Python Packages via PyPI

**Case study:**
[flowmark-rs #36 — Distribute flowmark-rs on PyPI via maturin](https://github.com/jlevy/flowmark-rs/issues/36)

## Overview

This research investigates the best approaches for distributing a Rust CLI binary
(flowmark-rs) as a Python package on PyPI, so that users can install and run it with
`uvx flowmark-rs`, `uv tool install flowmark-rs`, or `pip install flowmark-rs`.

**Motivating use case:** The original flowmark is a Python package on PyPI. The Rust
rewrite is dramatically faster.
Distributing the Rust binary through PyPI keeps the install experience identical — just
a different package name.
This is the same pattern used by **ruff**, **uv**, and **maturin** itself.

**Decision context:** flowmark-rs already has GitHub Releases (binary archives),
Homebrew tap, and crates.io publishing.
Adding PyPI distribution would complete the set of install methods, making
`uvx flowmark-rs` work on any platform.

## Questions to Answer

1. What is the standard approach for packaging Rust CLI binaries as Python wheels?
2. How do major projects (ruff, uv, maturin) implement this?
3. What platform targets are needed, and how do wheel platform tags work?
4. How does maturin’s `bindings = "bin"` mode work?
5. What CI/CD workflow is needed to build multi-platform wheels and publish to PyPI?
6. How should PyPI trusted publishing (OIDC) be set up?
7. What can we borrow from the simple-modern-uv template for workflow patterns?
8. What are the best practices and pitfalls?
9. What’s the recommended approach for flowmark-rs specifically?

## Scope

**Included:**
- Maturin `bindings = "bin"` for standalone CLI distribution
- Cross-platform wheel building with maturin-action
- PyPI trusted publishing (OIDC)
- Platform tags (manylinux, musllinux, macOS, Windows)
- Python wrapper/shim patterns
- CI/CD workflow design
- Comparison with existing flowmark-rs release infrastructure

**Excluded:**
- PyO3 bindings (not relevant — flowmark-rs is a standalone CLI, not a Python extension)
- npm/other non-Python distribution channels
- Shell/PowerShell installers (covered in the build-publishing spec)

## Findings

### 1. Maturin `bindings = "bin"` — The Core Mechanism

[Maturin](https://www.maturin.rs/) is the standard tool for building Python wheels from
Rust projects. Its `bindings = "bin"` mode packages a compiled Rust binary into a Python
wheel as a “script” — when installed, the binary is placed on the user’s PATH (e.g., in
a virtualenv’s `bin/` directory).

**How it works:**
- The compiled Rust binary goes into the wheel’s `.data/scripts/` directory
- pip/uv installs it into the appropriate `bin/` or `Scripts/` directory
- No Python code runs when the binary is invoked — it’s pure Rust
- The wheel is platform-tagged (e.g., `manylinux_2_17_x86_64`) so pip/uv selects the
  right one

**Minimal configuration** in `pyproject.toml`:

```toml
[build-system]
requires = ["maturin>=1.9,<2.0"]
build-backend = "maturin"

[project]
name = "flowmark-rs"
version = "0.2.4"
description = "Fast Markdown auto-formatter, written in Rust"
requires-python = ">=3.8"

[tool.maturin]
bindings = "bin"
strip = true
```

**Auto-detection:** Maturin can auto-detect `bin` bindings when there is only a binary
target and no pyo3/cdylib targets.
However, explicit configuration is recommended.

### 2. How Ruff Does It

**Repository:** [astral-sh/ruff](https://github.com/astral-sh/ruff)

Ruff is an extremely fast Python linter/formatter written in Rust, distributed as a
Python package on PyPI. It is the closest comparable project to flowmark-rs in terms of
architecture: a pure Rust CLI binary distributed via PyPI.

#### Ruff’s Configuration

**`pyproject.toml`:**
```toml
[build-system]
requires = ["maturin>=1.9,<2.0"]
build-backend = "maturin"

[project]
name = "ruff"
version = "0.15.4"
requires-python = ">=3.7"

[tool.maturin]
bindings = "bin"
manifest-path = "crates/ruff/Cargo.toml"
module-name = "ruff"
python-source = "python"
strip = true
```

Key settings:
- **`bindings = "bin"`** — standalone binary distribution
- **`manifest-path`** — points to the specific crate producing the binary (ruff uses a
  Cargo workspace)
- **`python-source = "python"`** — location of the Python wrapper package
- **`strip = true`** — strips debug symbols to reduce binary size

#### Ruff’s Python Wrapper

Ruff ships a thin Python wrapper package (`python/ruff/`) with three files:

1. **`__init__.py`** — exports `find_ruff_bin()` for programmatic use
2. **`__main__.py`** — enables `python -m ruff` by exec-ing the binary
   - Unix: `os.execvp()` replaces the Python process entirely (zero overhead)
   - Windows: `subprocess.run()` (because execvp behaves differently on Windows)
3. **`_find_ruff.py`** — sophisticated binary locator that searches multiple install
   locations (virtualenvs, system installs, `--prefix`, `--target`, user scheme)

**Important:** Ruff does NOT use a “wrapper package” pattern with platform-specific
sub-packages (e.g., `ruff-x86_64-linux`). Each wheel is a single self-contained `ruff`
package, platform-tagged by maturin.
pip selects the correct wheel based on the platform tag.

#### Ruff’s CI/CD

Ruff builds **17 platform-specific wheel targets + 1 sdist = 18 distributions** per
release.

The build pipeline uses:
- **`PyO3/maturin-action@e83996d129638aa358a18fbd1dfb82f0b0fb5d3b`**
  (**v1.51.0**) with **`maturin-version: v1.14.1`** (pinned)
- **`cargo-dist`** for release orchestration (but with `build-local-artifacts = false` —
  cargo-dist doesn’t build the actual binaries)
- **`uv publish`** for PyPI upload with OIDC trusted publishing

Build flags: `maturin build --release --locked --out dist --compatibility pypi`

**Platform targets:**

| Category | Targets |
| --- | --- |
| macOS | `x86_64-apple-darwin`, `aarch64-apple-darwin` |
| Windows | `x86_64-pc-windows-msvc`, `i686-pc-windows-msvc`, `aarch64-pc-windows-msvc` |
| Linux glibc | `x86_64-unknown-linux-gnu`, `i686-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `armv7-unknown-linux-gnueabihf`, `s390x-unknown-linux-gnu`, `powerpc64le-unknown-linux-gnu`, `riscv64gc-unknown-linux-gnu` |
| Linux musl | `x86_64-unknown-linux-musl`, `i686-unknown-linux-musl`, `aarch64-unknown-linux-musl`, `armv7-unknown-linux-musleabihf` |
| Linux misc | `arm-unknown-linux-musleabihf` (ARMv6) |

**Manylinux versions used:**
- Most glibc targets: `manylinux_2_17`
- RISC-V: `manylinux_2_31`
- All musl targets: `musllinux_1_2`

#### Ruff’s Versioning

The version is manually kept in sync between `pyproject.toml` and `Cargo.toml` using
Ruff’s [`tool.rooster` configuration](https://github.com/astral-sh/ruff/blob/main/pyproject.toml),
which lists the files updated together during a version bump.
There is no automated derivation of one from the other at build time.

### 3. How uv Does It

**Repository:** [astral-sh/uv](https://github.com/astral-sh/uv)

uv uses virtually the same approach as ruff (both are from Astral):

#### uv’s Configuration

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[tool.maturin]
bindings = "bin"
manifest-path = "crates/uv/Cargo.toml"
module-name = "uv"
python-source = "python"
strip = true
```

#### uv’s Python Wrapper

Nearly identical to ruff’s, with added sophistication:
- Detects the current virtualenv and passes it via `VIRTUAL_ENV` env var
- Passes the parent Python interpreter path via `UV_INTERNAL__PARENT_INTERPRETER`
- On Unix, uses `os.execvpe()` to replace the Python process entirely
- On Windows, uses `subprocess.run()` with `KeyboardInterrupt` handling

#### uv’s CI/CD

Also builds **17+ platform targets** using `maturin-action` + `cargo-dist` for
orchestration. Publishes with `uv publish` and PyPI trusted publishing.

**Notable extras:**
- **Wheel content verification** — a CI script opens each `.whl` file and asserts the
  exact expected file list
- **Dual distribution** — ships both `uv` (full binary) and `uv-build` (minimal-size
  profile) as separate PyPI packages
- **SBOMs** — each wheel includes a CycloneDX SBOM
- **Build attestations** — GitHub Attestations for supply chain security

### 4. Python Wheel Platform Tags

Python wheels use platform tags to indicate compatibility.
The wheel filename format is:
`{distribution}-{version}(-{build tag})-{python tag}-{abi tag}-{platform tag}.whl`

For binary-only distributions (`bindings = "bin"`), the relevant tags are:

| Platform | Tag Example | Notes |
| --- | --- | --- |
| Linux glibc x86_64 | `manylinux_2_17_x86_64` | glibc 2.17+ (CentOS 7+) |
| Linux glibc aarch64 | `manylinux_2_17_aarch64` | glibc 2.17+ |
| Linux musl x86_64 | `musllinux_1_2_x86_64` | Alpine Linux etc. |
| Linux musl aarch64 | `musllinux_1_2_aarch64` | Alpine Linux etc. |
| macOS x86_64 | `macosx_10_12_x86_64` | macOS 10.12+ |
| macOS ARM64 | `macosx_11_0_arm64` | macOS 11+ (Apple Silicon) |
| Windows x86_64 | `win_amd64` | 64-bit Windows |
| Windows x86 | `win32` | 32-bit Windows |
| Windows ARM64 | `win_arm64` | Windows on ARM |

**Manylinux evolution:**
- PEP 513: `manylinux1` (CentOS 5, glibc 2.5) — obsolete
- PEP 571: `manylinux2010` (CentOS 6, glibc 2.12) — obsolete
- PEP 599: `manylinux2014` (CentOS 7, glibc 2.17) — current standard
- PEP 600: `manylinux_x_y` (generic, future-proof) — e.g., `manylinux_2_17`

**Key constraint:** The Rust compiler since version 1.64 requires at least glibc 2.17,
so the minimum manylinux version is `2_17` (manylinux2014). This is what ruff and uv
both use for most targets.

### 5. Maturin-Action for CI/CD

[`PyO3/maturin-action`](https://github.com/PyO3/maturin-action) is a GitHub Action that
installs and runs maturin with built-in cross-compilation support.

**Key inputs:**

| Input | Purpose |
| --- | --- |
| `command` | maturin subcommand (`build`, `publish`, `sdist`) |
| `args` | Additional maturin arguments |
| `maturin-version` | Version to install (default: `latest`) |
| `manylinux` | Linux platform tag compatibility (default: `auto`) |
| `target` | Rust target triple |
| `container` | Custom Docker image for Linux builds |
| `sccache` | Enable compilation caching |
| `before-script-linux` | Pre-build script for Linux containers |

**Cross-compilation containers:** For non-native Linux architectures, maturin-action
automatically selects appropriate Docker images:
- x86_64 manylinux_2_17: `quay.io/pypa/manylinux2014_x86_64`
- aarch64 manylinux_2_17: `ghcr.io/rust-cross/manylinux2014-cross:aarch64`
- x86_64 musllinux: host build (no container needed)
- aarch64 musllinux: `ghcr.io/rust-cross/manylinux2014-cross:aarch64`

**Best practices from ruff/uv:**
- Pin the maturin-action version (to the latest `PyO3/maturin-action` release or a commit hash)
- Pin the maturin-version to the latest `maturin` release (1.13.3 as of May 2026; the
  `v1.11.5` pins surveyed below are a Feb 2026 snapshot of ruff/uv)
- Use `--locked` for reproducible builds
- Use `--compatibility pypi` for PyPI-compatible platform tags
- Test the installed wheel on each platform (at minimum `flowmark --help`)

### 6. PyPI Trusted Publishing (OIDC)

PyPI trusted publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions
workflows with PyPI, eliminating the need for long-lived API tokens.

**Setup steps:**

1. **Create or claim the PyPI project:** Register `flowmark-rs` on
   [pypi.org](https://pypi.org).
   For new projects, you can set up a “pending” trusted publisher before the first
   publish.

2. **Configure trusted publisher on PyPI:** Navigate to
   `https://pypi.org/manage/project/flowmark-rs/settings/publishing/` and add:
   - Repository owner: `jlevy`
   - Repository name: `flowmark-rs`
   - Workflow name: e.g., `pypi.yml` (or whatever the publish workflow is named)
   - Environment: `release` (optional but recommended)

3. **Workflow requirements:**
   - `permissions: id-token: write` — mandatory for OIDC token exchange
   - An `environment: release` declaration (recommended)
   - Publish with `uv publish --trusted-publishing always` or
     `pypa/gh-action-pypi-publish@release/v1`

**How it works:** During the publish step, GitHub exchanges an OIDC token with PyPI.
PyPI validates the owner/repo/workflow tuple against the trusted publisher configuration
and grants a short-lived publishing token automatically.

### 7. Patterns from simple-modern-uv

**Repository:** [jlevy/simple-modern-uv](https://github.com/jlevy/simple-modern-uv)

This is a Copier template for modern Python projects.
While it’s designed for pure Python (not Rust binaries), several patterns are directly
reusable:

**Reusable patterns:**
- **OIDC trusted publishing** — `id-token: write` +
  `uv publish --trusted-publishing always`
- **Workflow structure** — trigger on GitHub Release published event, checkout with
  `fetch-depth: 0`, build, publish
- **`astral-sh/setup-uv@v8`** — standard action for installing uv in CI
- **Dynamic versioning from Git tags** — using `uv-dynamic-versioning` plugin (for pure
  Python; for Rust, maturin reads from `Cargo.toml`)
- **Test-before-publish** — runs full test suite before uploading to PyPI

**What would need to change for Rust binary wheels:**
- Build backend: `hatchling` → `maturin`
- Build step: `uv build` → `maturin build --release`
- Need a cross-platform build matrix (not just Ubuntu)
- Need artifact collection from matrix jobs before publish

### 8. Other Projects Using This Pattern

| Project | Bindings | Build Tool | Platform Count | Distribution |
| --- | --- | --- | --- | --- |
| **ruff** | `bin` | maturin | 17 | Single `ruff` package |
| **uv** | `bin` | maturin | 17+ | Two packages: `uv`, `uv-build` |
| **maturin** | `bin` + `pyo3` | maturin (self-hosted) | ~10 | Single `maturin` package |
| **pydantic-core** | `pyo3` | maturin | ~15 | Library extension (not CLI) |
| **tokenizers** | `pyo3` | maturin | ~12 | Library extension |
| **polars** | `pyo3` | maturin | ~10 | Library extension |
| **tpchgen-cli** | `bin` | maturin | ~5 | Single package |
| **celq** | `bin` | maturin + cargo-zigbuild | ~6 | Single package |

**Key observation:** For standalone CLI binaries, the universal approach is `maturin`
with `bindings = "bin"`. No major project uses a different tool.
The only variation is the number of platform targets.

### 9. Manylinux vs Musl for Linux Wheels

There are two approaches for Linux wheel compatibility:

**Option A: manylinux (glibc)** — Used by ruff, uv, maturin
- Targets: `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`
- Tags: `manylinux_2_17_x86_64`, `manylinux_2_17_aarch64`
- Built inside manylinux Docker containers for compatibility
- Works on virtually all Linux distros with glibc 2.17+ (CentOS 7+, Ubuntu 14.04+,
  Debian 8+)
- Does NOT work on Alpine or other musl-based distros

**Option B: musllinux (musl)** — Used by ruff, uv additionally
- Targets: `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`
- Tags: `musllinux_1_2_x86_64`, `musllinux_1_2_aarch64`
- Built with musl-tools or inside musl cross-compilation containers
- Works on Alpine and other musl-based distros
- Also works on glibc distros (since musl binaries are statically linked)

**Note about flowmark-rs’s existing approach:** The current `release.yml` builds
`x86_64-unknown-linux-musl` and `aarch64-unknown-linux-musl` for GitHub Releases using
musl for static linking.
For PyPI, we should build **both** manylinux (glibc) and musllinux wheels to maximize
compatibility, following ruff’s example.
However, for a simpler initial approach, just manylinux wheels would cover the vast
majority of users.

### 10. Cargo.toml Binary Names and PyPI Package Names

An important consideration: the Cargo.toml currently defines two binary targets:

```toml
[[bin]]
name = "flowmark"
path = "src/main.rs"

[[bin]]
name = "flowmark-rs"
path = "src/main.rs"
```

For the PyPI package:
- **Package name:** `flowmark-rs` (matches the GitHub repo and avoids conflict with the
  Python `flowmark` package)
- **Binary name:** Both `flowmark` and `flowmark-rs` binaries should be included in the
  wheel, so users can invoke either
- Maturin can be told which binary to package via `manifest-path` or by specifying the
  binary name

### 11. Versioning Strategy

There are two approaches to keeping version numbers in sync:

**Approach A: Manual sync** (ruff, uv)
- Keep the version in both `pyproject.toml` and `Cargo.toml`
- Use a tool like rooster to bump all files simultaneously
- Simple, explicit, well-tested

**Approach B: Dynamic version from Cargo.toml** (issue #36 suggestion)
- Set `dynamic = ["version"]` in `pyproject.toml`
- Maturin reads the version from `Cargo.toml` automatically
- Avoids version drift
- This is the approach recommended in issue #36 and documented in maturin’s docs

**Recommendation for flowmark-rs:** Use Approach B (dynamic version from Cargo.toml).
This is simpler for a single-crate project and avoids the risk of version drift.
Ruff and uv use Approach A because they are Cargo workspaces with complex versioning
needs.

### 12. Flowmark-rs’s Existing Release Infrastructure

The current release setup already covers:

| Channel | Status | Workflow |
| --- | --- | --- |
| GitHub Releases (binaries) | Active | `release.yml` |
| crates.io (source + binary) | Active | `publish.yml` |
| Homebrew tap | Active | Manual (submodule) |
| PyPI | **Not yet** | Needs new workflow |

The existing `release.yml` builds 6 targets:
- `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`
- `x86_64-apple-darwin`, `aarch64-apple-darwin`
- `x86_64-pc-windows-msvc`, `aarch64-pc-windows-msvc`

For PyPI, we need to build **wheels** (not archives).
This requires a separate build step using maturin, which can coexist with the existing
release workflow.

## Comparison Matrix

### Approach Comparison for Adding PyPI Distribution

| Criterion | A: Extend release.yml | B: Separate pypi.yml | C: Shared workflow, two jobs |
| --- | --- | --- | --- |
| Complexity | Medium (adds to existing) | Low (independent) | Medium |
| Separation of concerns | Poor | Excellent | Good |
| Trigger flexibility | Coupled to tag push | Can be release event or tag | Flexible |
| Failure isolation | PyPI failure could affect GH Release | Fully isolated | Partially isolated |
| Wheel targets | Uses existing matrix | Fresh matrix, manylinux-optimized | Fresh matrix |
| Maintenance | One workflow to maintain | Two workflows, clear purpose | One workflow, more complex |

### Platform Coverage: Minimum vs Comprehensive

| Criterion | Minimum (5 targets) | Standard (7 targets) | Comprehensive (17+ targets) |
| --- | --- | --- | --- |
| Linux glibc x86_64 | Yes | Yes | Yes |
| Linux glibc aarch64 | Yes | Yes | Yes |
| macOS x86_64 | Yes | Yes | Yes |
| macOS aarch64 | Yes | Yes | Yes |
| Windows x86_64 | Yes | Yes | Yes |
| Linux musl x86_64 | No | Yes | Yes |
| Linux musl aarch64 | No | Yes | Yes |
| Windows i686 | No | No | Yes |
| Windows aarch64 | No | No | Yes |
| Linux i686 | No | No | Yes |
| Linux armv7 | No | No | Yes |
| Linux s390x, ppc64, riscv64 | No | No | Yes |
| Coverage | ~95% of users | ~99% of users | ~99.9% of users |
| Build time | ~10 min | ~15 min | ~30 min |
| Complexity | Low | Low-Medium | High |

## Options Considered

### Option A: Extend Existing `release.yml`

**Description:** Add maturin wheel-building jobs to the existing release workflow that
already builds binary archives.

**Pros:**
- Single workflow manages all release artifacts
- Can reuse the existing target matrix

**Cons:**
- Mixes archive and wheel builds (different tools, different containers)
- Harder to debug failures
- Different manylinux requirements (GNU vs musl targets)
- release.yml is already complex

### Option B: Separate `pypi.yml` Workflow (Recommended)

**Description:** Create a new `pypi.yml` workflow dedicated to building wheels and
publishing to PyPI. Triggered by the GitHub Release `published` event (same as
`publish.yml` for crates.io).

**Pros:**
- Clean separation of concerns
- Can use maturin-action’s Docker containers naturally
- Easy to test independently
- Follows the simple-modern-uv pattern of “release event → build → publish”
- Failure in PyPI publishing doesn’t affect GitHub Releases or crates.io

**Cons:**
- One more workflow file to maintain
- Builds the project again (doesn’t reuse existing binaries from release.yml)

### Option C: Combined Maturin + Archive Workflow

**Description:** Replace the current release.yml entirely with a maturin-based workflow
that produces both wheels and binary archives.

**Pros:**
- Single source of truth for all binary builds
- Maturin can output both wheels and archives

**Cons:**
- Major rework of existing tested workflow
- Higher risk of breaking existing release flow
- Maturin archives may not match current naming convention

### Eliminated Options

- **cargo-zigbuild approach:** Uses Zig’s linker for cross-compilation instead of Docker
  containers. While interesting for local development, maturin-action’s Docker approach
  is more battle-tested and used by ruff/uv.
  Eliminated because maturin-action already handles this well.

- **Platform-specific sub-packages** (e.g., `flowmark-rs-x86_64-linux`): Used by some
  npm-distributed Rust CLIs but NOT used by any major PyPI-distributed Rust CLI. Ruff
  and uv both ship single platform-tagged packages.
  Eliminated because it adds unnecessary complexity.

## Recommendations

### 1. Use Maturin with `bindings = "bin"` (Unanimous)

This is the universal standard.
Every major Rust CLI distributed via PyPI uses this approach.

### 2. Create a Separate `pypi.yml` Workflow (Option B)

Add a new `.github/workflows/pypi.yml` triggered by the GitHub Release `published`
event. This keeps concerns separated and allows the existing `release.yml` (binary
archives) and `publish.yml` (crates.io) to continue working unchanged.

### 3. Start with Standard Coverage (7 targets)

Build wheels for the platforms that match our existing release targets, plus manylinux
glibc variants:

| Target | Platform Tag | Runner | manylinux |
| --- | --- | --- | --- |
| `x86_64-unknown-linux-gnu` | `manylinux_2_17_x86_64` | `ubuntu-latest` | `2_17` |
| `aarch64-unknown-linux-gnu` | `manylinux_2_17_aarch64` | `ubuntu-latest` | `2_17` |
| `x86_64-unknown-linux-musl` | `musllinux_1_2_x86_64` | `ubuntu-latest` | N/A |
| `aarch64-unknown-linux-musl` | `musllinux_1_2_aarch64` | `ubuntu-latest` | N/A |
| `x86_64-apple-darwin` | `macosx_10_12_x86_64` | `macos-13` | N/A |
| `aarch64-apple-darwin` | `macosx_11_0_arm64` | `macos-14` | N/A |
| `x86_64-pc-windows-msvc` | `win_amd64` | `windows-latest` | N/A |

The musl targets are optional for the initial release — they primarily serve Alpine
Linux users. A 5-target version (glibc + macOS + Windows) would cover ~95% of users.

### 4. Add a Minimal Python Wrapper

Following ruff and uv’s pattern, include a small Python wrapper at `python/flowmark_rs/`
(or in a subdirectory) with:
- `__init__.py` — exports `find_flowmark_rs_bin()`
- `__main__.py` — enables `python -m flowmark_rs`
- `_find_bin.py` — locates the binary

This is optional for basic functionality (maturin handles placing the binary on PATH),
but it enables `python -m flowmark_rs` and programmatic discovery.

### 5. Use Dynamic Versioning from Cargo.toml

Set `dynamic = ["version"]` in `pyproject.toml` and let maturin read the version from
`Cargo.toml`. This avoids maintaining version numbers in two places.

### 6. Use PyPI Trusted Publishing

Set up OIDC trusted publishing on PyPI for the `flowmark-rs` project, linked to the
`pypi.yml` workflow.
Publish using `uv publish --trusted-publishing always`.

### 7. Recommended File Changes

**New files:**

1. **`pyproject.toml`** (repo root) — maturin build configuration
2. **`.github/workflows/pypi.yml`** — wheel build + publish workflow
3. **`python/flowmark_rs/__init__.py`** — Python wrapper (optional)
4. **`python/flowmark_rs/__main__.py`** — `python -m flowmark_rs` support (optional)
5. **`python/flowmark_rs/_find_bin.py`** — Binary locator (optional)

**Important:** The repo root already has a `python/` directory with
`flowmark-dev-tools`. The new `pyproject.toml` for the PyPI package should be at the
repo root (where `Cargo.toml` already lives), and maturin will handle the rest.
The `python/` directory already used for dev tools would need to be separate from the
maturin `python-source` path.

### 8. Proposed Workflow Structure

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-linux-x86_64:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: PyO3/maturin-action@v1
        with:
          command: build
          args: --release --locked --out dist
          target: x86_64-unknown-linux-gnu
          manylinux: "2_17"
      - uses: actions/upload-artifact@v7
        with:
          name: wheels-linux-x86_64
          path: dist/*.whl

  # ... similar jobs for other targets ...

  build-sdist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: PyO3/maturin-action@v1
        with:
          command: sdist
          args: --out dist
      - uses: actions/upload-artifact@v7
        with:
          name: wheels-sdist
          path: dist/*.tar.gz

  publish:
    needs: [build-linux-x86_64, ..., build-sdist]
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write
    steps:
      - uses: astral-sh/setup-uv@v8
      - uses: actions/download-artifact@v8
        with:
          pattern: wheels-*
          merge-multiple: true
          path: wheels/
      - run: uv publish --trusted-publishing always wheels/*
```

### 9. Key Considerations for flowmark-rs

1. **Package name conflict:** The Python `flowmark` package already exists on PyPI (the
   Python version). Using `flowmark-rs` as the PyPI package name avoids conflict and
   makes the Rust implementation explicit.
   Users would run `uvx flowmark-rs` (not `uvx flowmark`).

2. **Binary names in the wheel:** The wheel should include both `flowmark` and
   `flowmark-rs` binaries (both are defined in `Cargo.toml`). This way, after
   `pip install flowmark-rs`, both commands work.
   However, this needs testing — maturin may need configuration to include both
   binaries.

3. **Existing `python/pyproject.toml`:** The current `python/pyproject.toml` is for
   `flowmark-dev-tools`, a development-only package.
   It uses `hatchling` as its build backend and is marked `Private :: Do Not Upload`.
   The new root-level `pyproject.toml` for maturin is completely separate.

4. **`python-source` configuration:** Since `python/` already contains
   `flowmark-dev-tools`, the Python wrapper for the PyPI package should go in a
   different location, or maturin’s `python-source` should be carefully configured.
   One option: use `python-source = "py"` and put the wrapper in `py/flowmark_rs/`.

5. **sdist (source distribution):** Including an sdist allows users to build from source
   as a fallback. This requires a Rust toolchain on the user’s machine, but it’s standard
   practice and provides a safety net for unsupported platforms.

## Implementation Checklist

### Phase 1: Configuration (Day 1)

- [ ] Create `pyproject.toml` at repo root with maturin configuration
- [ ] Create Python wrapper package (optional, can defer)
- [ ] Test locally: `maturin build --release` and `maturin develop --release`
- [ ] Verify `flowmark-rs --help` works after `maturin develop`

### Phase 2: CI Workflow (Day 1-2)

- [ ] Create `.github/workflows/pypi.yml` with build matrix
- [ ] Start with 5 targets (linux-gnu-x86_64, linux-gnu-aarch64, macos-x86_64,
  macos-aarch64, windows-x86_64)
- [ ] Test with a dry run (build without publishing)
- [ ] Add musl targets if desired

### Phase 3: PyPI Setup (Day 2)

- [ ] Register `flowmark-rs` on PyPI (or set up pending trusted publisher)
- [ ] Configure trusted publisher on PyPI
- [ ] Test with TestPyPI first (`uv publish --index-url https://test.pypi.org/legacy/`)
- [ ] First real publish via creating a GitHub Release

### Phase 4: Verification (Day 2-3)

- [ ] Verify `pip install flowmark-rs` works on all platforms
- [ ] Verify `uvx flowmark-rs --help` works
- [ ] Verify `uv tool install flowmark-rs` works
- [ ] Update README with `uvx` / `pip install` instructions

### Phase 5: Polish (Future)

- [ ] Add Python wrapper for `python -m flowmark_rs`
- [ ] Add musl targets for Alpine support
- [ ] Add wheel content verification script (as uv does)
- [ ] Consider Windows ARM64 target
- [ ] Consider i686 targets for 32-bit support

## Methodology

This research was conducted by:

1. **Reading GitHub issue #36** in full, which provided a detailed proposal
2. **Cloning and examining three repositories:**
   - `astral-sh/ruff` — pyproject.toml, maturin config, all CI workflows, Python wrapper
     code
   - `astral-sh/uv` — pyproject.toml, maturin config, all CI workflows, Python wrapper
     code, wheel verification scripts
   - `jlevy/simple-modern-uv` — Copier template, CI workflows, publishing workflow
3. **Web research on:**
   - Maturin documentation (bindings, distribution, CI generation)
   - PyO3/maturin-action documentation and configuration
   - PyPI trusted publishing (OIDC) setup
   - Python wheel platform tag specifications (PEP 513, 571, 599, 600, 656)
   - Blog posts from practitioners (tpchgen-cli, celq)
4. **Reviewing the existing flowmark-rs infrastructure:** Cargo.toml, all three CI
   workflows, docs/publishing.md, the build-publishing spec

## References

### Official Documentation

- [Maturin User Guide](https://www.maturin.rs/) — full documentation
- [Maturin `bin` Bindings](https://www.maturin.rs/bindings) — binary-only distribution
- [Maturin Distribution Guide](https://www.maturin.rs/distribution.html) — manylinux,
  cross-compilation
- [PyO3/maturin-action](https://github.com/PyO3/maturin-action) — GitHub Actions for
  cross-platform builds
- [PyPI Trusted Publishers Docs](https://docs.pypi.org/trusted-publishers/) — OIDC setup
- [Python Packaging: Platform Compatibility Tags](https://packaging.python.org/specifications/platform-compatibility-tags/)

### Real-World Examples

- [Ruff’s pyproject.toml](https://github.com/astral-sh/ruff/blob/main/pyproject.toml) —
  primary reference (same pattern)
- [Ruff’s build-binaries.yml](https://github.com/astral-sh/ruff/blob/main/.github/workflows/build-binaries.yml)
  — comprehensive 17-target build
- [uv’s pyproject.toml](https://github.com/astral-sh/uv/blob/main/pyproject.toml) —
  another primary reference
- [uv’s build-release-binaries.yml](https://github.com/astral-sh/uv/blob/main/.github/workflows/build-release-binaries.yml)
  — comprehensive build with testing
- [simple-modern-uv](https://github.com/jlevy/simple-modern-uv) — template for PyPI
  publishing workflow patterns

### PEPs (Platform Tags)

- [PEP 513 — manylinux1](https://peps.python.org/pep-0513/)
- [PEP 600 — Future manylinux](https://peps.python.org/pep-0600/)
- [PEP 656 — musllinux](https://peps.python.org/pep-0656/)

### Community Resources

- [tpchgen: Distributing a Rust Binary via Python Using Maturin](https://kevinjqliu.github.io/blog/posts/tpchgen/index.html)
- [I packaged my Rust CLI to too many places](https://ivaniscoding.github.io/posts/rustpackaging1/)
- [GitHub: pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
  — official PyPI publish action

### Existing flowmark-rs Infrastructure

- [Issue #36](https://github.com/jlevy/flowmark-rs/issues/36) — the detailed proposal
- [Build-Publishing Spec](https://github.com/jlevy/flowmark-rs/blob/main/docs/project/specs/done/plan-2026-02-17-build-publishing.md) —
  existing release infrastructure
- [Publishing guide](https://github.com/jlevy/flowmark-rs/blob/main/docs/publishing.md) —
  current publishing guide
