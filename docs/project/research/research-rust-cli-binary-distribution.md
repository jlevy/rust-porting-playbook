---
title: "Research: Rust CLI Binary Distribution Practices"
status: complete
date: 2026-02-20
---
# Research: Rust CLI Binary Distribution Practices

## Motivation

When preparing a Rust CLI tool for public release with pre-built binaries, the main
question is: use cargo-dist, a custom GitHub Actions workflow, or something else?
This research surveys how 14 popular Rust CLI tools actually distribute their binaries
to inform that decision.

## Key Questions

1. What release mechanisms do popular Rust CLI tools use?
2. What specific versions of GitHub Actions, Rust toolchains, and cross-compilation
   tools do they use?
3. What target platforms do they build for?
4. How do they handle checksums, signing, and security?
5. How does Astral’s cargo-dist approach differ from everyone else’s custom workflows?
6. What should a modern, small-to-medium Rust CLI tool use?

## Findings

### Overview: Custom GitHub Actions Dominates

Of 14 major Rust CLI tools surveyed, **12 use fully custom GitHub Actions release
workflows**. Only Astral’s uv and ruff use cargo-dist — and they use it in a heavily
customized way (with maturin for Python wheel builds).

| Approach | Count | Tools |
| --- | --- | --- |
| Custom GHA workflow | 12 | ripgrep, bat, fd, delta, eza, starship, zoxide, just, jj, typst, mise, nushell |
| cargo-dist (customized + maturin) | 2 | uv, ruff |

* * *

### Tool-by-Tool Survey

#### 1. ripgrep (BurntSushi/ripgrep)

The template that many others copy.
Typst explicitly states its workflow is “based on ripgrep’s release action.”

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Tag push matching
`[0-9]+.[0-9]+.[0-9]+`

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v4` |
| `dtolnay/rust-toolchain` | `@master` |

**Rust toolchain:** `nightly` for primary platforms (x86_64 musl, macOS, Windows),
`stable` for cross-compiled ARM/i686/s390x Linux targets.
Not pinned — floats to latest.

**Build profile:** Custom `release-lto` profile with LTO enabled.
Builds with `--features pcre2` (`PCRE2_SYS_STATIC: 1`).

**Binary stripping:** Explicit — native `strip` on macOS, Docker-based strip via
cross-rs images on Linux (`aarch64-linux-gnu-strip`, etc.).

**Cross-compilation:** `cross` v0.2.5, downloaded as a prebuilt binary from GitHub
Releases.

**Targets (13):**

| Target | OS | Arch |
| --- | --- | --- |
| `x86_64-unknown-linux-musl` | Linux | x86_64 |
| `i686-unknown-linux-gnu` | Linux | i686 |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 |
| `armv7-unknown-linux-gnueabihf` | Linux | ARMv7 |
| `armv7-unknown-linux-musleabihf` | Linux | ARMv7 (musl) |
| `armv7-unknown-linux-musleabi` | Linux | ARMv7 (musl, soft-float) |
| `s390x-unknown-linux-gnu` | Linux | s390x |
| `x86_64-apple-darwin` | macOS | x86_64 |
| `aarch64-apple-darwin` | macOS | ARM64 |
| `x86_64-pc-windows-msvc` | Windows | x86_64 |
| `x86_64-pc-windows-gnu` | Windows | x86_64 (GNU) |
| `aarch64-pc-windows-msvc` | Windows | ARM64 |
| `i686-pc-windows-msvc` | Windows | i686 |

**Checksums:** SHA256 via `shasum -a 256` (Unix) and `certutil -hashfile` (Windows).

**Packaging:** `cargo-deb` for `.deb` packages (installed via `cargo install`).

**Shell completions/man pages:** Generated at runtime by running the built binary with
`--generate` flags. For cross-compiled targets, runs under QEMU emulation inside Docker.

**Release creation:** CLI-based via `gh release create --draft` + `gh release upload`
(not an action).

**Notable:** Three-job structure: `create-release` → `build-release` (matrix) →
`build-release-deb`. Uses `windows-11-arm` runner for aarch64 Windows.

* * *

#### 2. bat (sharkdp/bat)

**Release workflow:** `.github/workflows/CICD.yml` (combined CI/CD in one file)
**Trigger:** Runs on all pushes (master, tags, PRs); release behavior gated on tags
matching `v[0-9].*`

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v6` |
| `dtolnay/rust-toolchain` | `@stable` and `@master` |
| `taiki-e/install-action` | `@v2` |
| `softprops/action-gh-release` | `@v2` |
| `vedantmgoyal9/winget-releaser` | pinned SHA |

**Rust toolchain:** `stable` (floating).
MSRV tested separately via `cargo metadata` extraction.

**Cross-compilation:** `cross` installed via `taiki-e/install-action@v2` (not pinned to
a specific cross version — uses whatever `install-action` provides).

**Targets (13):**

| Target | OS | Arch |
| --- | --- | --- |
| `x86_64-unknown-linux-gnu` | Linux | x86_64 |
| `x86_64-unknown-linux-musl` | Linux | x86_64 (musl) |
| `i686-unknown-linux-gnu` | Linux | i686 |
| `i686-unknown-linux-musl` | Linux | i686 (musl) |
| `aarch64-unknown-linux-musl` | Linux | ARM64 (musl) |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 |
| `arm-unknown-linux-gnueabihf` | Linux | ARM |
| `arm-unknown-linux-musleabihf` | Linux | ARM (musl) |
| `x86_64-apple-darwin` | macOS | x86_64 |
| `aarch64-apple-darwin` | macOS | ARM64 |
| `x86_64-pc-windows-msvc` | Windows | x86_64 |
| `aarch64-pc-windows-msvc` | Windows | ARM64 |
| `i686-pc-windows-msvc` | Windows | i686 |

**Checksums:** None generated in the workflow.

**Runners:** `ubuntu-latest`, `macos-latest`, `macos-15-intel` (x86_64 macOS),
`windows-2025`, `windows-11-arm`.

**Packaging:** Manual `.deb` creation via `fakeroot dpkg-deb --build` (not cargo-deb).
Builds `.deb` for ALL Linux targets, not just x86_64. Naming:
`bat_${version}_${arch}.deb` or `bat-musl_${version}_${arch}.deb`. Auto-publishes to
Winget via `vedantmgoyal9/winget-releaser` (pinned SHA).

* * *

#### 3. fd-find (sharkdp/fd)

Same author and very similar structure to bat.

**Release workflow:** `.github/workflows/CICD.yml` **Trigger:** Tag push matching
`v[0-9]+.*`

**GitHub Actions versions:** Same as bat, except `softprops/action-gh-release` pinned to
commit SHA (`@a06a81a...` = v2.5.0).

**Rust toolchain:** `stable` (floating).

**Cross-compilation:** `cross` v0.2.5 (pinned, like ripgrep), downloaded via
`gh release download` (not install-action).

**Targets:** Same 13 as bat (but uses `ubuntu-24.04` pinned, `macos-14` pinned,
`windows-2022` pinned instead of `-latest`).

**Checksums:** None in workflow.

**Build attestation:** Uses `actions/attest-build-provenance@v3` for both tarballs and
`.deb` packages. Requires `id-token: write` permission.

**Security posture:** Most security-conscious of the three sharkdp tools: pins
third-party actions to commit SHAs, uses `persist-credentials: false` on all checkouts.

**Packaging:** Manual `.deb` via external `scripts/create-deb.sh` with
`fakeroot dpkg-deb --build`. Auto-publishes to Winget (v2, pinned SHA).

* * *

#### 4. delta (dandavison/delta)

**Release workflow:** `.github/workflows/cd.yml` **Trigger:** Tag push matching
`[0-9]+.[0-9]+.[0-9]+`

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v3` |
| `dtolnay/rust-toolchain` | `@stable` |
| `taiki-e/install-action` | `@v2` |
| `softprops/action-gh-release` | `@v1` |
| `vedantmgoyal2009/winget-releaser` | `@v2` |

**Rust toolchain:** `stable` (floating).

**Cross-compilation:** `cross` via `taiki-e/install-action@v2`, conditionally used when
`use-cross: true`.

**Targets (7):** `aarch64-apple-darwin`, `x86_64-pc-windows-msvc`,
`x86_64-unknown-linux-gnu`, `x86_64-unknown-linux-musl`, `i686-unknown-linux-gnu`,
`arm-unknown-linux-gnueabihf`, `aarch64-unknown-linux-gnu`

**Checksums:** None.
Packaging via custom `./etc/ci/before_deploy.sh` script.

**Notable:** Sets `MACOSX_DEPLOYMENT_TARGET: 10.7` for broad macOS compatibility.
Publishes to crates.io and Winget as separate jobs.

* * *

#### 5. eza (eza-community/eza)

**Release mechanism:** `justfile` recipes + `gh release create` (no release workflow
YAML).

**Cross-compilation:** Uses `cross` directly from justfile recipes.

**Targets:** Linux x86_64 (GNU+musl), aarch64, ARM; Windows x86_64. Builds three
variants: standard (with libgit2), `no_libgit`, and `static`.

**Checksums:** MD5 + SHA256 checksums generated.

**Notable:** Uses `convco` for conventional-commit-based versioning.
Most manual approach of all tools surveyed.

* * *

#### 6. starship (starship/starship)

The most sophisticated custom workflow.
Includes MSI, PKG, and code signing.

**Release workflow:** `.github/workflows/release.yml` **Trigger:** `release-please`
creates the release, then the workflow builds artifacts.

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `googleapis/release-please-action` | `@v4` |
| `actions/checkout` | `@v6` |
| `dtolnay/rust-toolchain` | `@master` |
| `taiki-e/install-action` | `@cross` |
| `signpath/github-action-submit-signing-request` | `@v2` |
| `actions/setup-node` | `@v6` |
| `softprops/action-gh-release` | `@v2` |
| `rust-lang/crates-io-auth-action` | `@v1` |
| `mislav/bump-homebrew-formula-action` | `@v3.6` |

**Rust toolchain:** `stable` via `dtolnay/rust-toolchain`.

**Cross-compilation:** `cross` via `taiki-e/install-action@cross` for Linux targets.
macOS and Windows use native `cargo build --target`.

**Targets (11):**

| Target | OS | Arch |
| --- | --- | --- |
| `x86_64-unknown-linux-gnu` | Linux | x86_64 |
| `x86_64-unknown-linux-musl` | Linux | x86_64 (musl) |
| `i686-unknown-linux-musl` | Linux | i686 (musl) |
| `aarch64-unknown-linux-musl` | Linux | ARM64 (musl) |
| `arm-unknown-linux-musleabihf` | Linux | ARM (musl) |
| `x86_64-unknown-freebsd` | FreeBSD | x86_64 |
| `x86_64-apple-darwin` | macOS | x86_64 |
| `aarch64-apple-darwin` | macOS | ARM64 |
| `x86_64-pc-windows-msvc` | Windows | x86_64 |
| `i686-pc-windows-msvc` | Windows | i686 |
| `aarch64-pc-windows-msvc` | Windows | ARM64 |

**Checksums:** SHA256 via `openssl dgst -sha256 -r`.

**Signing:** Windows binaries signed via SignPath
(`signpath/github-action-submit-signing-request@v2`).

**Packaging:**
- MSI: `cargo-wix` **v0.3.8** (`cargo install --version 0.3.8 cargo-wix`) with custom
  `install/windows/main.wxs`. MSIs signed via SignPath.
- macOS PKG: Custom `build_and_notarize.sh` with Apple notarization via
  `xcrun notarytool`. Both x86_64 and aarch64 `.pkg` files built and notarized.
- Shell installer: `curl -sS https://starship.rs/install.sh | sh`
- Chocolatey: Updated via `install/windows/choco/update.ps1`
- Winget: Updated via `wingetcreate.exe` with MSI and ZIP URLs

**Version management:** `release-please-action@v4` with `release-type: rust`. Runs on
every push to `master`. The `release_please` job outputs `release_created` (boolean) and
`tag_name`. All build/sign/upload jobs are gated on
`release_please.outputs.release_created == 'true'`. Release starts as draft, set to
non-draft after all artifacts are uploaded.

**Publishing:** Auto-publishes to crates.io (`rust-lang/crates-io-auth-action@v1` with
OIDC trusted publishing), Homebrew (`mislav/bump-homebrew-formula-action@v3.6`), Winget,
and Chocolatey.

**Environment:** `MACOSX_DEPLOYMENT_TARGET: 10.7`, `CARGO_INCREMENTAL: 0`,
`CARGO_NET_RETRY: 10`. Windows targets set `RUSTFLAGS: -C target-feature=+crt-static`.

* * *

#### 7. zoxide (ajeetdsouza/zoxide)

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Push to `main` and
manual dispatch.

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v6` |
| `SebRollen/toml-action` | `@v1.2.0` |
| `actions-rs/toolchain` | `@v1` |
| `Swatinem/rust-cache` | `@v2.8.2` |
| `actions-rs/cargo` | `@v1` |
| `actions-rs/install` | `@v0.1` |
| `softprops/action-gh-release` | `@v2` |

**Rust toolchain:** `stable` (floating) with `minimal` profile.

**Cross-compilation:** `cross` from specific commit (`cross-rs/cross.git` rev
`e281947ca900da425e4ecea7483cfde646c8a1ea`).

**Targets (11):** `x86_64-unknown-linux-musl`, `arm-unknown-linux-musleabihf`,
`armv7-unknown-linux-musleabihf`, `aarch64-unknown-linux-musl`,
`i686-unknown-linux-musl`, `aarch64-linux-android`, `armv7-linux-androideabi`,
`x86_64-apple-darwin`, `aarch64-apple-darwin`, `x86_64-pc-windows-msvc`,
`aarch64-pc-windows-msvc`

**Checksums:** None in the workflow.

**Packaging:** `cargo-deb` with `--no-build --no-strip` flags.

**Notable:** Builds for Android targets.
Uses `actions-rs/toolchain@v1` (older, now deprecated in favor of
`dtolnay/rust-toolchain`). Installs cross from a pinned git revision rather than a
release version.

* * *

#### 8. just (casey/just)

**Release workflow:** `.github/workflows/release.yaml` **Trigger:** Tag push matching
`*`

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v6` |
| `softprops/action-gh-release` | `@v2.5.0` |
| `Swatinem/rust-cache` | `@v2` |
| `peaceiris/actions-gh-pages` | `@v4` |

**Rust toolchain:** Default (not pinned — uses whatever is on the runner).

**Cross-compilation:** Direct linker flags, no `cross` tool:
- ARM: `--codegen linker=arm-linux-gnueabihf-gcc`
- AArch64: `--codegen linker=aarch64-linux-gnu-gcc`
- LoongArch64: `--codegen linker=loongarch64-linux-gnu-gcc-14`
- Dependencies installed via `apt-get` (e.g., `gcc-aarch64-linux-gnu`)

**Targets (9):** `aarch64-apple-darwin`, `x86_64-apple-darwin`,
`aarch64-pc-windows-msvc`, `x86_64-pc-windows-msvc`, `aarch64-unknown-linux-musl`,
`x86_64-unknown-linux-musl`, `arm-unknown-linux-musleabihf`,
`armv7-unknown-linux-musleabihf`, `loongarch64-unknown-linux-musl`

**Checksums:** Post-hoc approach: a separate `checksum` job runs after `package`,
downloads ALL release artifacts via `gh release download`, then generates a single
unified `SHA256SUMS` file with `shasum -a 256 * > ../SHA256SUMS` and uploads it back to
the release.

**Notable:** All Linux targets use musl (static linking).
All targets use `--codegen target-feature=+crt-static`. Generates manpages via
`./target/debug/just --man`. Deploys mdbook docs (`mdbook@0.4.52` +
`mdbook-linkcheck@0.7.7`) to GitHub Pages.
Detects prerelease via semver regex.
Global `RUSTFLAGS: --deny warnings`.

* * *

#### 9. jj / jujutsu (jj-vcs/jj)

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Published release
event.

**GitHub Actions versions (ALL pinned to full SHAs):**

| Action | SHA | Version |
| --- | --- | --- |
| `actions/checkout` | `de0fac2e4...` | v6.0.2 |
| `dtolnay/rust-toolchain` | `e97e2d8cc...` | master (not tagged) |
| `actions/upload-release-asset` | `e8f9f06c4...` | v1.0.2 (archived) |
| `actions/setup-python` | `a309ff8b4...` | v6.2.0 |
| `astral-sh/setup-uv` | `eac588ad8...` | v0.5.1 |

**Rust toolchain:** `stable`.

**Cross-compilation:** Minimal — uses native runners for each architecture where
possible:
- `ubuntu-24.04` for x86_64 Linux
- `ubuntu-24.04-arm` for aarch64 Linux (ARM runner)
- `macos-15` for both x86_64 and aarch64 macOS (ARM runner, x86_64 built via `--target`
  — this is a trivial cross-compile on macOS, not requiring `cross` or Docker)
- `windows-2022` for x86_64 Windows
- `windows-11-arm` for aarch64 Windows (ARM runner)

This is distinctive: jj avoids Docker-based cross-compilation entirely by using GitHub’s
native ARM runners for Linux and Windows, and macOS’s built-in cross-build support for
the x86_64 macOS target.

**Targets (6):** `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`,
`x86_64-apple-darwin`, `aarch64-apple-darwin`, `x86_64-pc-windows-msvc`,
`aarch64-pc-windows-msvc`

**Checksums:** None in the workflow.

**Security:** `persist-credentials: false` on most checkout steps.
`permissions: read-all` at top level, `contents: write` only on jobs that need it.

**Notable:** All action versions pinned to full SHAs (best security practice).
Uses `astral-sh/setup-uv@v0.5.1` for Python/docs tooling.
Docs built with `uv run mkdocs`. Fewest targets (6) of all tools surveyed — focuses on
the most common platforms only.

* * *

#### 10. typst (typst/typst)

Explicitly based on ripgrep’s release workflow.

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Tag push matching
`v[0-9]+.*`

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | pinned SHA (`@8e8c483db...`) |
| `dtolnay/rust-toolchain` | pinned SHA (`@f941e41d0...`) → Rust 1.91.0 |
| `actions/upload-artifact` | pinned SHA (`@b7c566a77...`) |
| `ncipollo/release-action` | pinned SHA (`@2c591bcc8...`) → v1.14.0 |

**Rust toolchain:** Pinned to **Rust 1.91.0** (via dtolnay SHA).

**Cross-compilation:** `cross` installed from `cross-rs` GitHub repo at specific commit
SHA `085092ca`. Used for Linux targets marked `cross: true`.

**Targets (8):** `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`,
`armv7-unknown-linux-musleabi`, `riscv64gc-unknown-linux-gnu`, `x86_64-apple-darwin`,
`aarch64-apple-darwin`, `x86_64-pc-windows-msvc`, `aarch64-pc-windows-msvc`

**Checksums:** None in the workflow.

**Archive format:** `.tar.xz` for Unix (xz compression, not gzip), `.zip` for Windows.

**Dual-mode trigger:** On `workflow_dispatch`, artifacts uploaded via
`actions/upload-artifact` with 3-day retention (for testing).
On `release: published`, artifacts uploaded to the GitHub Release via
`ncipollo/release-action`.

**Cross features:** Cross builds use `--features self-update,vendor-openssl`. Native
builds use `--features self-update`.

**Notable:** Pins ALL action versions to full SHAs (not `@v4` tags).
Pins Rust to an exact version (1.91.0). Most security-conscious pinning approach.
Packages binaries with README, LICENSE, and NOTICE files.

* * *

#### 11. uv (astral-sh/uv) — cargo-dist

The most sophisticated distribution of any tool surveyed.
Uses cargo-dist as orchestrator with maturin for Python wheel builds.

**Release workflow:** `.github/workflows/release.yml` (auto-generated by cargo-dist)
**Trigger:** `workflow_dispatch` with tag input (default: `"dry-run"`) — not tag push

**cargo-dist version:** **0.30.2**

**Maturin version:** **v1.11.5** via `PyO3/maturin-action@v1.50.0`
(`b1bd829e37fef14c63f19162034228a2f3dc1021`)

**dist-workspace.toml configuration (key sections):**

```toml
[dist]
cargo-dist-version = "0.30.2"
ci = "github"
installers = ["shell", "powershell"]
dist = false                          # cargo-dist does NOT build binaries
build-local-artifacts = false         # custom build jobs replace cargo-dist builds
local-artifacts-jobs = ["./build-release-binaries", "./build-docker"]
publish-jobs = ["./publish-pypi", "./publish-crates"]
post-announce-jobs = ["./publish-docs", "./publish-versions"]
dispatch-releases = true              # manual workflow_dispatch, not tag push
github-release = "announce"           # release created in announce phase
github-attestations = true
github-attestations-phase = "announce"
github-attestations-filters = ["*.json", "*.sh", "*.ps1", "*.zip", "*.tar.gz"]
auto-includes = false
create-release = true
pr-run-mode = "skip"                  # no release workflow on PRs
install-updater = false
install-path = ["$XDG_BIN_HOME/", "$XDG_DATA_HOME/../bin", "~/.local/bin"]

[dist.github-custom-runners]
global = "depot-ubuntu-latest-4"      # Depot runners for speed

[dist.min-glibc-version]
aarch64-unknown-linux-gnu = "2.28"
riscv64gc-unknown-linux-gnu = "2.31"
"*" = "2.17"

[dist.github-action-commits]          # cargo-dist pins actions via this section
"actions/checkout" = "11bd71901..."                  # v4
"actions/upload-artifact" = "6027e3dd..."             # v4.6.2
"actions/download-artifact" = "d3f86a10..."           # v4.3.0
"actions/attest-build-provenance" = "00014ed6..."     # v3.1.0

[dist.binaries]
"*" = ["uv", "uvx"]
aarch64-pc-windows-msvc = ["uv", "uvx", "uvw"]       # uvw = Windows GUI binary
i686-pc-windows-msvc = ["uv", "uvx", "uvw"]
x86_64-pc-windows-msvc = ["uv", "uvx", "uvw"]
```

**How `build-local-artifacts = false` works:**

This is the key differentiator.
In standard cargo-dist, the release workflow auto-generates build jobs that run
`dist build --artifacts=local`. Astral disables this and substitutes custom reusable
workflows:

1. `local-artifacts-jobs = ["./build-release-binaries", "./build-docker"]` references
   `.github/workflows/build-release-binaries.yml`
2. The custom workflow uses **maturin** (not `cargo build`) to produce both Python
   wheels AND standalone binaries from the same compilation step
3. Artifacts uploaded with `artifacts-*` naming pattern so cargo-dist can find them
4. cargo-dist’s `build-global-artifacts` step then generates installers and checksums
   based on those artifacts

**GitHub Actions in release.yml (auto-generated):**

| Action | SHA | Version |
| --- | --- | --- |
| `actions/checkout` | `11bd71901...` | v4 |
| `actions/upload-artifact` | `6027e3dd1...` | v4.6.2 |
| `actions/download-artifact` | `d3f86a106...` | v4.3.0 |
| `actions/attest-build-provenance` | `00014ed6e...` | v3.1.0 |

**GitHub Actions in build-release-binaries.yml (hand-written):**

| Action | SHA | Version |
| --- | --- | --- |
| `actions/checkout` | `de0fac2e4...` | v6.0.2 |
| `PyO3/maturin-action` | `b1bd829e3...` | v1.50.0 |
| `actions/setup-python` | `a309ff8b4...` | v6.2.0 |
| `uraimo/run-on-arch-action` | `d94c13912...` | v3.0.1 |
| `astral-sh/setup-uv` | `eac588ad8...` | v7.3.0 |

**Pipeline structure:**
1. `plan` — `dist plan --output-format=json` (or `dist host --steps=create`)
2. `custom-build-binaries` + `custom-build-docker` — parallel builds via custom reusable
   workflows using maturin; uploads `artifacts-*` and `wheels-*`
3. `build-global-artifacts` — downloads all `artifacts-*`, runs
   `dist build --artifacts=global` to generate installers (`install.sh`, `install.ps1`),
   checksums, `dist-manifest.json`
4. `host` — `dist host --steps=upload --steps=release`
5. `custom-publish-pypi` / `custom-publish-crates` — PyPI and crates.io
6. `announce` — creates GitHub Release with attestations
7. `custom-publish-docs` / `custom-publish-versions` — post-announce

**Targets (18):** Both GNU and musl for Linux (including powerpc64, powerpc64le, s390x,
riscv64), macOS (x86_64 + ARM64), Windows (x86_64 + ARM64 + i686).

**Checksums:** SHA256, embedded directly in the installer scripts.

**Shell installer details:** The generated `uv-installer.sh`:
- Detects platform via `uname -s` / `uname -m`
- Downloads `.tar.gz` from GitHub Release
- Verifies SHA256 checksums (embedded in the script itself)
- Installs to XDG-compliant paths (`$XDG_BIN_HOME`, `$XDG_DATA_HOME/../bin`,
  `~/.local/bin`)
- Creates an `env` script and modifies shell RC files (`.bashrc`, `.zshrc`, `.profile`)

**Custom runners:** Depot (`depot-ubuntu-latest-4`, `depot-ubuntu-24.04-4`,
`depot-ubuntu-24.04-8`, `depot-macos-14`) for faster builds.

* * *

#### 12. ruff (astral-sh/ruff) — cargo-dist

Nearly identical architecture to uv.

**cargo-dist version:** **0.30.2** **Maturin version:** **v1.11.5** via
`PyO3/maturin-action@v1.50.0`

**dist-workspace.toml differences from uv:**

```toml
pr-run-mode = "plan"                   # runs dist plan on PRs (uv skips entirely)
local-artifacts-jobs = ["./build-binaries", "./build-docker", "./build-wasm"]
publish-jobs = ["./publish-pypi", "./publish-wasm"]
post-announce-jobs = ["./notify-dependents", "./publish-docs",
                      "./publish-playground", "./publish-versions"]
```

**GitHub Actions in release.yml (auto-generated, newer versions than uv):**

| Action | SHA | Version |
| --- | --- | --- |
| `actions/checkout` | `de0fac2e4...` | v6.0.2 |
| `actions/upload-artifact` | `b7c566a77...` | v6.0.0 |
| `actions/download-artifact` | `37930b1c2...` | v7.0.0 |
| `actions/attest-build-provenance` | `00014ed6e...` | v3.1.0 |

**Targets (18):** Identical to uv.

**Additional build outputs:** WASM builds published to npm for the Ruff playground.

**Notable:** ruff’s auto-generated `release.yml` uses newer action versions than uv’s
(v6 checkout, v6 upload, v7 download), because it was regenerated more recently.
Both projects’ hand-written custom build workflows use the same versions.

* * *

#### 13. mise (jdx/mise)

The broadest distribution strategy of any tool surveyed.

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Push to `mise` branch
(custom release flow).

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | pinned SHA |
| `taiki-e/install-action` | pinned SHA |
| `actions/cache` | pinned SHA |
| `nick-fields/retry` | pinned SHA |
| `apple-actions/import-codesign-certs` | pinned SHA → v5 |
| `Swatinem/rust-cache` | pinned SHA |
| `crazy-max/ghaction-import-gpg` | pinned SHA → v6 |

**Rust toolchain:** Not pinned (uses runner default).

**Cross-compilation:** `cross` via `taiki-e/install-action` for Linux ARM targets.

**Targets (10):** `x86_64-unknown-linux-gnu`, `x86_64-unknown-linux-musl`,
`aarch64-unknown-linux-gnu`, `aarch64-unknown-linux-musl`,
`armv7-unknown-linux-gnueabi`, `armv7-unknown-linux-musleabi`, `x86_64-apple-darwin`,
`aarch64-apple-darwin`, `x86_64-pc-windows-msvc`, `aarch64-pc-windows-msvc`

**Checksums and signing:**
- `minisign` for binary signing
- `zipsign` for Windows archive signing
- GPG signing via `crazy-max/ghaction-import-gpg@v6`
- Apple code signing via `apple-actions/import-codesign-certs@v5`

**Notable:**
- LLM-generated release notes (Claude via `ANTHROPIC_API_KEY`, fallback to `git-cliff`)
- npm wrapper: `@jdxcode/mise` with platform-specific sub-packages
- Publishes to: GitHub Releases, npm, Snap, Winget, Fedora COPR, Ubuntu PPA, Alpine, own
  CDN (mise.run)
- Shell installer: `curl https://mise.run | sh`
- Builds in tar.xz, tar.gz, and tar.zst formats

* * *

#### 14. nushell (nushell/nushell)

**Release workflow:** `.github/workflows/release.yml` **Trigger:** Semver git tags.

**GitHub Actions versions:**

| Action | Version |
| --- | --- |
| `actions/checkout` | `@v6` |
| `actions-rust-lang/setup-rust-toolchain` | `@v1.12.0` |
| `hustcer/setup-nu` | `@v3` |
| `softprops/action-gh-release` | `@v2.0.5` |

**Rust toolchain:** Not pinned (dynamically set via `rust-toolchain.toml`).

**Cross-compilation:** No `cross` tool.
Uses native GitHub Actions runners for each platform.
Target set via `rust-toolchain.toml` modification:
`echo "targets = ['$TARGET']" >> rust-toolchain.toml`

**Targets (13):** `aarch64-apple-darwin`, `x86_64-apple-darwin`,
`x86_64-pc-windows-msvc`, `aarch64-pc-windows-msvc`, `x86_64-unknown-linux-gnu`,
`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu`, `aarch64-unknown-linux-musl`,
`armv7-unknown-linux-gnueabihf`, `armv7-unknown-linux-musleabihf`,
`riscv64gc-unknown-linux-gnu`, `loongarch64-unknown-linux-gnu`,
`loongarch64-unknown-linux-musl`

**Checksums:** `shasum -a 256 * > ../SHA256SUMS` on all artifacts.

**Packaging:** MSI via WiX Toolset 6
(`dotnet tool install --global wix --version 6.0.0`).

**Notable:** Installs Nushell itself (`hustcer/setup-nu@v3`) to run release packaging
scripts written in `.nu` files.
Uses `actions-rust-lang/setup-rust-toolchain@v1.12.0` instead of the more common
`dtolnay/rust-toolchain`.

* * *

## Comparative Analysis

### GitHub Actions Versions Used

| Action | Most Common Version | Tools Using It |
| --- | --- | --- |
| `actions/checkout` | `@v6` | bat, fd, starship, zoxide, just, nushell |
|  | `@v4` | ripgrep |
|  | pinned SHA | typst, jj, uv, ruff, mise |
| `dtolnay/rust-toolchain` | `@stable` | bat, fd, delta, starship, jj |
|  | `@master` | ripgrep, starship |
|  | pinned SHA → specific version | typst (1.91.0) |
| `actions-rust-lang/setup-rust-toolchain` | `@v1.12.0` | nushell |
| `taiki-e/install-action` | `@v2` | bat, fd, delta |
|  | `@cross` | starship |
|  | pinned SHA | mise |
| `softprops/action-gh-release` | `@v2` | bat, fd, starship, zoxide |
|  | `@v2.5.0` | just |
|  | `@v2.0.5` | nushell |
|  | `@v1` | delta |
| `ncipollo/release-action` | pinned SHA → v1.14.0 | typst |
| `Swatinem/rust-cache` | `@v2` | just, mise |

### Cross-Compilation Approaches

| Approach | Tools | Notes |
| --- | --- | --- |
| `cross` via `taiki-e/install-action` | bat, fd, delta, starship, mise | Most common. Version determined by install-action. |
| `cross` pinned version/SHA | ripgrep (v0.2.5), typst (SHA `085092ca`), zoxide (SHA `e281947c`) | More reproducible. |
| Direct linker flags via apt | just | No Docker containers needed. Uses `--codegen linker=...`. |
| Native ARM runners | jj | Uses ARM runners for ARM builds. macOS x86_64 built via `--target` on ARM runners. |
| `cargo --target` (no cross tool) | nushell | Cross-compiles from x86_64 for ARM/RISC-V via `cargo build --target`. No `cross` or Docker. |
| maturin (cargo-dist custom) | uv, ruff | Specific to Python wheel builds. |

### Rust Toolchain Pinning

| Strategy | Tools | Tradeoff |
| --- | --- | --- |
| `nightly` (floating) | ripgrep | Access to latest features; may break |
| `stable` (floating) | bat, fd, delta, starship, jj, zoxide | Safe default; minor version drift between releases |
| Exact version (pinned SHA) | typst (1.91.0) | Most reproducible; requires manual updates |
| Runner default (not specified) | just, mise, nushell | Simplest; least control |

### Target Platform Coverage

**Minimum viable set (all tools):**
- `x86_64-unknown-linux-musl` (or `-gnu`)
- `aarch64-unknown-linux-musl` (or `-gnu`)
- `x86_64-apple-darwin`
- `aarch64-apple-darwin`

**Common additions:**
- `x86_64-pc-windows-msvc` — included by 13 of 14 tools
- `aarch64-pc-windows-msvc` — included by 9 of 14 tools
- `armv7-unknown-linux-musleabihf` — included by 9 of 14 tools
- `i686` variants — included by ~7 tools

**Linux musl vs GNU:**
- 8 tools build musl-only for Linux (just, typst, jj, starship partially)
- 6 tools build both GNU and musl (bat, ripgrep, nushell, uv, ruff, mise)
- Musl-only is the simpler approach: static binaries that work everywhere

### GitHub Actions Runner OS Versions

Different tools use different runner strategies:

| Strategy | Tools | Notes |
| --- | --- | --- |
| `-latest` (floating) | ripgrep, bat, starship, just | Simplest. May break on OS upgrades. |
| Pinned OS version | fd (`ubuntu-24.04`, `macos-14`, `windows-2022`) | More reproducible. |
| Mixed | nushell, mise | `-latest` for some, pinned for others. |

**ARM runners:**
- `windows-11-arm` — used by ripgrep, bat, fd, just for `aarch64-pc-windows-msvc`
- Ubuntu ARM runners — used by jj for `aarch64-unknown-linux-musl` (no cross needed)
- `macos-latest` — now ARM64 (Apple Silicon) by default on GitHub Actions
- `macos-15-intel` — used by bat for `x86_64-apple-darwin` (Intel Mac)

### Checksum and Signing Practices

| Practice | Tools | Notes |
| --- | --- | --- |
| SHA256 checksums | ripgrep, just, nushell, starship, uv, ruff | Standard practice |
| No checksums | bat, fd, delta, typst, jj, zoxide | Surprisingly common |
| GitHub attestations | uv, ruff, fd | Cryptographic build provenance |
| Code signing (Windows) | starship (SignPath) | Only one tool |
| Binary signing (minisign/GPG) | mise | Most thorough |
| macOS notarization | starship | Only one tool |

### Shell Installer Patterns

| Tool | URL | Notes |
| --- | --- | --- |
| starship | `starship.rs/install.sh` | Own domain, most polished |
| zoxide | GitHub raw URL | Simple, in-repo script |
| just | `just.systems/install.sh` | Own domain |
| uv | `astral.sh/uv/install.sh` | cargo-dist generated |
| ruff | `astral.sh/ruff/install.sh` | cargo-dist generated |
| mise | `mise.run` | Own CDN |

### Package Manager Distribution

**Universal (all 14 tools):**
- GitHub Releases with prebuilt binaries
- Homebrew (`brew install`)
- `cargo install` (build from source)

**Common (8+ tools):**
- Winget
- Scoop
- Linux distro packages (Arch, Fedora, Debian/Ubuntu)

**Selective:**
- PyPI (uv, ruff only — via maturin wheels)
- npm (mise only — `@jdxcode/mise` with platform sub-packages)
- Snap (starship, bat, mise)
- Chocolatey (starship, delta)

* * *

## cargo-dist: Deep Dive

### What It Is

cargo-dist (renamed to just “dist” at v0.24.0, October 2024) is an opinionated release
automation tool for Rust projects.

**Latest stable version:** **v0.30.4** (February 16, 2026).

Recent release history:

| Version | Date | Notes |
| --- | --- | --- |
| v0.30.4 | 2026-02-16 | Bugfixes, dependency updates (CVE fix in brace-expansion) |
| v0.30.3 | 2025-12-15 | macOS codesign fix, sudo permission fix for shell installer |
| v0.30.2 | 2025-10-31 | Attestation customization (used by Astral) |
| v0.30.0 | 2025-09-07 | ZIP compression, installer enhancements, native ARM64 Linux runners |
| v0.26.0 | 2024-12-12 | CycloneDX SBOM support |
| v0.24.0 | 2024-10-28 | Renamed to “dist”, new config format (`dist-workspace.toml`) |

GitHub stats: ~1,900 stars, 133 forks (as of Feb 2026).

### What It Generates

Running `cargo dist init` creates:
- `dist-workspace.toml` — configuration file (preferred since v0.24.0; replaces
  `[workspace.metadata.dist]` in Cargo.toml)
- `.github/workflows/release.yml` — auto-generated GitHub Actions workflow

The generated workflow has **8 jobs** in a structured pipeline:
1. **plan** (ubuntu-22.04) — `dist plan` to compute build matrix, output
   `dist-manifest.json`
2. **build-local-artifacts** (matrix, per-platform) — compile binaries, create archives,
   generate attestations
3. **build-global-artifacts** (ubuntu-22.04) — create shell/PowerShell installers,
   Homebrew formula, npm packages, unified checksum file
4. **host** (ubuntu-22.04) — create GitHub Release (draft), upload all artifacts
5. **publish-homebrew-formula** — push formula to tap repo
6. **publish-npm** — publish npm packages (Node.js 20.x)
7. **custom-publish** — reusable workflows (e.g., cargo publish)
8. **announce** — mark release as non-draft after all publishing succeeds

### Installer Types Supported

5 installer types — notably, **no `.deb`, `.rpm`, Flatpak, Snap, AppImage, or macOS
`.pkg`**:

| Installer | Strategy | Platform | Description |
| --- | --- | --- | --- |
| **shell** | Fetching | Unix | `curl \| sh` — downloads + installs binary |
| **powershell** | Fetching | Windows | `irm \| iex` — downloads + installs binary |
| **homebrew** | Fetching | macOS/Linux | Formula pushed to configurable tap repo |
| **npm** | Fetching | Cross-platform | npm package wrapping native binaries |
| **msi** | Bundling | Windows | MSI installer with bundled binaries |

### Cross-Compilation Approach

cargo-dist does **not** include a built-in cross-compilation tool.
Cross-compilation support remains an open feature request (issue #74, opened Feb 2023,
still open as of Feb 2026). Instead, cargo-dist relies on:

- **macOS:** Native builds on macOS runners.
  Both x86_64 and aarch64 are “nearby-buildable” on macOS -- either architecture can
  build the other with just `rustup target add`.
- **Linux aarch64:** Since mid-2025, cargo-dist uses GitHub’s native ARM64 Linux runners
  (`ubuntu-24.04-arm`) for aarch64 targets, avoiding cross-compilation entirely.
- **Linux musl:** Supported via `musl-tools` on Ubuntu runners.
  The `min-glibc-version` config option exists for glibc-based targets.
- **Windows:** Native builds on Windows runners.
  aarch64-pc-windows-msvc is not in the supported targets list (see disadvantages).
- **User-configured cross-compilation:** Users can manually configure cross-compilation
  via `dependencies.apt` (to install cross-compiler packages like
  `gcc-aarch64-linux-gnu`) and `.cargo/config.toml` (to set linker paths).
  This works for simple cases but struggles with C library dependencies (OpenSSL,
  libudev, etc.).

The cargo-dist team evaluated `cross-rs`, `cargo-zigbuild`, and `cargo-xwin` as
potential solutions but has not integrated any of them.
The trend toward GitHub providing free native ARM64 runners (announced Jan 2025) has
reduced the urgency of cross-compilation support.

### Key Configuration Options

```toml
[dist]
cargo-dist-version = "0.30.4"      # Pins the cargo-dist version
ci = "github"                       # CI provider (GitHub Actions ONLY)
installers = ["shell", "homebrew"]  # Installer types to generate
targets = [...]                     # Build targets
publish-jobs = ["homebrew"]         # What to publish
tap = "owner/homebrew-tap"          # Homebrew tap repo
install-path = "CARGO_HOME"         # Where to install (~/.cargo/bin/)
pr-run-mode = "plan"                # What runs on PRs (skip/plan/upload)
checksum = "sha256"                 # sha256/sha512/sha3-256/blake2b/false
create-release = true               # Auto-create GitHub Release
source-tarball = false              # Skip source tarball
github-attestations = true          # Build provenance attestations (SLSA L2)
dispatch-releases = false           # workflow_dispatch vs tag push trigger
build-local-artifacts = true        # Use cargo-dist's builds (false = custom)
ssldotcom-windows-sign = "..."      # Windows code signing (SSL.com eSigner)
msvc-crt-static = true              # Static MSVC CRT (default)
```

### Advantages

1. **Zero YAML authoring** — the workflow is auto-generated and regenerated on updates
2. **Structured pipeline** — plan/build/host/publish/announce is well-organized
3. **Installer generation** — shell, PowerShell, Homebrew, npm, MSI
4. **cargo-binstall compatibility** — releases are automatically discoverable
5. **Checksums and attestations** — SHA256 + GitHub artifact attestations (SLSA L2)
6. **`dist plan` validation** — catch config errors on PRs before merging
7. **Upgradeable** — `cargo dist init` regenerates workflow for new versions
8. **CycloneDX SBOM** — software bill of materials generation (since v0.26.0)
9. **Windows code signing** — SSL.com eSigner integration (since v0.15.0)
10. **Custom job hooks** — 6 injection points: plan, local-artifacts, global-artifacts,
    host, publish, post-announce

### Disadvantages

1. **GitHub Actions only** — no GitLab, Gitea/Forgejo, or any other CI. Open feature
   request (issue #1781) with no timeline.
2. **Version coupling** — `cargo-dist-version` must match generated YAML. Forgetting to
   regenerate after upgrading causes build failures.
3. **Generated YAML is not meant to be hand-edited** — `dist init` overwrites changes.
   Must use config system or custom job hooks for customization.
4. **Debugging** — build matrix is computed dynamically by `dist plan` and passed as
   JSON. Debugging requires running `dist plan` locally to inspect output.
5. **Adoption** — only Astral (uv/ruff) among the 14 major tools surveyed.
   GitHub’s dependents page shows only 12 repos for the `cargo-dist` crate, though this
   metric is misleading: cargo-dist is a CLI tool, not a library dependency, so most
   users have `dist-workspace.toml` files rather than Cargo.toml dependencies.
   Actual usage is higher but hard to quantify precisely.
   Well-known but not ubiquitously adopted among high-profile projects.
6. **Breaking changes** — pre-1.0, has had breaking changes between versions
7. **Complexity for simple cases** — generated workflow for even a simple tool is ~300
   lines of YAML with complex conditional logic
8. **No `.deb`/`.rpm`/`.pkg`** — only 5 installer types.
   No Linux distro packages or macOS `.pkg`.
9. **No ARM64 Windows** — `aarch64-pc-windows-msvc` not yet in supported targets list
   despite Rust Tier 1 since 1.91
10. **Shell installer + Snap curl** — refuses to work with Snap-installed curl (Ubuntu
    default). Falls back to wget but may abort.
11. **Runner image dependencies** — Ubuntu 20.04 deprecation (April 2025) required
    regeneration. Future deprecations will require the same.

### How Astral Uses It Differently

Astral’s usage is non-standard in several critical ways:

1. **`build-local-artifacts = false`** — disables cargo-dist’s default binary builds
   entirely. `local-artifacts-jobs` substitutes custom reusable workflows.
2. **`dist = false`** — cargo-dist does not try to identify or build packages itself.
3. **Maturin replaces `cargo build`** — `PyO3/maturin-action@v1.50.0` produces both
   Python wheels AND standalone binaries in one compilation step.
4. **`dispatch-releases = true`** — manual `workflow_dispatch` with tag input (default:
   `"dry-run"`) instead of tag push.
   Enables testing the entire release pipeline.
5. **Custom CI runners** — Depot runners (`depot-ubuntu-latest-4`) instead of
   GitHub-hosted runners, for faster builds.
6. **XDG-compliant install paths** —
   `["$XDG_BIN_HOME/", "$XDG_DATA_HOME/../bin", "~/.local/bin"]` instead of cargo-dist’s
   default `$CARGO_HOME/bin`.
7. **`github-action-commits` section** — cargo-dist has a dedicated config section for
   pinning GitHub Actions to full SHAs, so the auto-generated workflow uses pinned
   versions.
8. **No updater** — `install-updater = false` disables cargo-dist’s self-update
   mechanism.

This means Astral uses cargo-dist primarily as a **release orchestrator** (plan → host →
announce), not as a build system.
The actual builds are done by maturin in custom workflows.
cargo-dist only generates the installers and manages the GitHub Release.

For a project that doesn’t need Python wheel distribution, Astral’s approach provides no
advantage over cargo-dist’s defaults or a custom workflow.
However, two features are noteworthy even for simpler projects:

- **`dispatch-releases = true`** — dry-run testing of the release pipeline is valuable
- **`github-action-commits`** — SHA pinning via config rather than manual YAML editing

* * *

## Patterns and Anti-Patterns

### What the Best Tools Do

1. **Pin action versions** — typst and jj pin to full SHAs (best practice).
   Most others use `@v4`/`@v6` tags (acceptable).
   Avoid `@master` (ripgrep does this).

2. **Use musl for Linux** — static binaries that work on any Linux.
   No GLIBC version issues.
   just, typst, jj, and starship use musl-only for Linux.

3. **Generate SHA256 checksums** — ripgrep, just, nushell, starship do this.
   Surprisingly, bat, fd, delta, typst, jj, and zoxide don’t.

4. **Include Windows** — 13 of 14 tools build for Windows.
   Even Unix-focused tools include at least `x86_64-pc-windows-msvc`.

5. **Keep it simple** — just uses direct linker flags instead of cross.
   jj and nushell use native runners.
   Simpler approaches are easier to debug.

### What to Avoid

1. **Deprecated actions** — zoxide uses `actions-rs/toolchain@v1` and
   `actions-rs/cargo@v1`, which are unmaintained.
   Use `dtolnay/rust-toolchain` instead.

2. **No checksums** — 6 of 14 tools skip checksums entirely.
   This is a security gap.

3. **Floating nightly** — ripgrep uses nightly without pinning.
   This can break unexpectedly.

4. **Over-engineering** — mise’s setup (minisign + GPG + zipsign + Apple signing + LLM
   release notes + own CDN + npm + Snap + COPR + PPA) is impressive but overkill for
   most projects.

* * *

## Recommended Approach

### For Small-to-Medium Pure-Rust CLI Tools

**Recommended: Custom GitHub Actions workflow modeled on
[casey/just](https://github.com/casey/just/blob/master/.github/workflows/release.yaml).**

just is the best template for a small-to-medium Rust CLI: pure Rust, single maintainer,
focused utility, all-musl Linux targets, Windows support, direct linker flags (no Docker
or `cross-rs`), and a clean three-job workflow (prerelease detection, matrix build,
unified checksums). The workflow is ~120 lines of straightforward YAML.

Other good templates depending on specific needs:
- **typst** — if you want all actions pinned to full SHAs and a specific Rust version
- **fd** — if you want GitHub build attestations (`actions/attest-build-provenance`)
- **jj** — if you want the simplest possible setup using native ARM runners for
  everything (no cross-compilation at all)

### When to Use cargo-dist Instead

cargo-dist is a reasonable choice when:
- **You want zero YAML authoring** and are willing to accept an opaque generated
  workflow in exchange for not writing any release CI yourself
- **You need auto-generated installers** — shell (`curl | sh`), PowerShell
  (`irm | iex`), Homebrew formula, npm packages, or MSI. Writing these from scratch is
  non-trivial.
- **You have no dedicated release engineer** and want a tool that handles the entire
  plan/build/host/publish/announce pipeline from a single TOML config
- **PR validation matters** — `dist plan` catches release config errors on PRs

cargo-dist is less suitable when:
- You need `aarch64-pc-windows-msvc` (not in cargo-dist’s supported targets list)
- You have C dependencies that need cross-compilation (cargo-dist’s cross-compilation
  support is limited; issue #74 is still open)
- You want to understand and own every line of your release workflow
- You’re concerned about version coupling (forgetting to regenerate YAML after bumping
  `cargo-dist-version` breaks the release)

### When to Use cross-rs

Use `cross` (via `taiki-e/install-action`) when:
- Your project has C dependencies (OpenSSL, libudev, etc.)
  that need cross-compiled system libraries
- You need to build for exotic targets (s390x, powerpc64, RISC-V) where native runners
  aren’t available
- You want Docker-based build isolation for reproducibility

For pure-Rust projects, `cross` adds Docker overhead without benefit.
just’s direct linker flags approach is simpler and faster.

* * *

## Best Practices for a Modern Rust CLI

Based on the practices of all 14 tools surveyed, here are the emerging best practices
for binary distribution of a small-to-medium Rust CLI tool.

### Target Platforms

Minimum recommended set based on surveyed tools:

| Target | Priority | Rationale |
| --- | --- | --- |
| `x86_64-unknown-linux-musl` | Required | Most common Linux servers/CI (static) |
| `aarch64-unknown-linux-musl` | Required | AWS Graviton, ARM servers |
| `x86_64-apple-darwin` | Required | Intel Macs (pre-2020) |
| `aarch64-apple-darwin` | Required | Apple Silicon (M1+) |
| `x86_64-pc-windows-msvc` | Recommended | 13/14 surveyed tools include Windows |
| `aarch64-pc-windows-msvc` | Optional | Windows ARM — growing, Rust Tier 1 since 1.91 |
| `armv7-unknown-linux-musleabihf` | Optional | Raspberry Pi, embedded — 9/14 tools |

**Why musl for Linux:** Static binaries work on any Linux distribution regardless of
glibc version. just, typst, and jj all use musl-only for Linux.
8 of 14 tools build musl-only or musl-primary for Linux.
The performance difference is negligible for most CLI tools.

### GitHub Actions Component Versions

Based on the most current practices across surveyed tools:

| Component | Recommended | Used By |
| --- | --- | --- |
| `actions/checkout` | `@v6` | bat, fd, starship, just, nushell |
| `dtolnay/rust-toolchain` | `@stable` | bat, fd, delta, starship, jj |
| `softprops/action-gh-release` | `@v2` | bat, fd, starship, zoxide |
| `Swatinem/rust-cache` | `@v2` | just, mise |

For maximum security, pin to full SHAs (as typst and jj do).
For maintainability, `@v6` tags are acceptable since Dependabot will update them.

### Cross-Compilation

| Approach | Used By | Tradeoffs |
| --- | --- | --- |
| `cross` via `taiki-e/install-action@v2` | bat, fd, delta, starship, mise | Most common. Docker-based, handles C deps. |
| `cross` pinned version/SHA | ripgrep, typst, zoxide | More reproducible. |
| Direct linker flags (`--codegen linker=...`) | just | Simpler, no Docker. Good for pure-Rust musl-only. |
| Native ARM runners | jj | No cross-compilation issues. Simplest for common targets. |
| `cargo --target` (no cross tool) | nushell | Pure-Rust cross-compile from x86_64. No Docker overhead. |

The trend is toward native ARM runners (GitHub made them free for public repos in Jan
2025), which avoids cross-compilation complexity entirely for the most common targets.

### Checksums and Security

| Practice | Adoption | Notes |
| --- | --- | --- |
| SHA256 checksums | 8/14 tools | Standard practice, should be considered baseline |
| GitHub attestations | 3/14 tools (uv, ruff, fd) | Free, provides cryptographic build provenance (SLSA) |
| Code signing (Windows) | 1/14 (starship via SignPath) | Needed for Winget/SmartScreen |
| Binary signing (minisign/GPG) | 1/14 (mise) | Strongest integrity guarantee |
| macOS notarization | 1/14 (starship) | Needed for macOS Gatekeeper |

### Installers

| Installer | Adoption | Notes |
| --- | --- | --- |
| GitHub Releases (tar.gz/zip) | 14/14 | Universal baseline |
| `cargo install` / `cargo binstall` | 14/14 | Automatic for any crate on crates.io |
| Shell installer (`curl \| sh`) | 6/14 | Common for widely-used tools |
| Homebrew tap | widespread | Not tracked in survey but standard for macOS |
| PowerShell installer | varies | Include if building for Windows |
| `.deb` packages | 4/14 (ripgrep, bat, fd, zoxide) | Via cargo-deb or manual dpkg-deb |
| Winget | 4/14 (bat, fd, delta, starship) | Auto-publish via winget-releaser action |

### Version Management

| Approach | Used By | Notes |
| --- | --- | --- |
| Manual tag push | ripgrep, bat, fd, delta, typst, jj | Simplest. Tag → release. |
| release-please | starship | Automated PR with version bump + changelog |
| release-plz | mise | Rust-specific alternative to release-please |
| Custom scripts | just, nushell | For specific needs |

Manual tag push is the most common and simplest approach.
release-please or release-plz add automation that becomes valuable as release cadence
increases.

* * *

## Summary Table

| Tool | Release System | GHA Checkout | Rust Toolchain | Cross Tool | Targets | Checksums | Windows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ripgrep | Custom GHA | @v4 | nightly | cross v0.2.5 | 13 | SHA256 | Yes (3) |
| bat | Custom GHA | @v6 | stable | cross (install-action) | 13 | None | Yes (3) |
| fd | Custom GHA | @v6 | stable | cross (install-action) | 13 | None | Yes (3) |
| delta | Custom GHA | @v3 | stable | cross (install-action) | 7 | None | Yes (1) |
| eza | justfile | — | — | cross | ~6 | MD5+SHA256 | Yes (1) |
| starship | Custom GHA + release-please | @v6 | stable | cross (install-action) | 11 | SHA256 | Yes (3) |
| zoxide | Custom GHA | @v6 | stable | cross (git SHA) | 11 | None | Yes (2) |
| just | Custom GHA | @v6 | default | linker flags | 9 | SHA256 | Yes (2) |
| jj | Custom GHA | SHA | stable | native runners + macOS cross | 6 | None | Yes (2) |
| typst | Custom GHA | SHA | 1.91.0 | cross (git SHA) | 8 | None | Yes (2) |
| uv | cargo-dist 0.30.2 | SHA | — | maturin | 18 | SHA256 | Yes (3) |
| ruff | cargo-dist 0.30.2 | SHA | — | maturin | 18 | SHA256 | Yes (3) |
| mise | Custom GHA | SHA | default | cross (install-action) | 10 | minisign | Yes (2) |
| nushell | Custom GHA | @v6 | default | cargo --target (no cross tool) | 13 | SHA256 | Yes (2) |

* * *

## Sources

### Tool Repositories and Workflows

- [ripgrep release.yml](https://github.com/BurntSushi/ripgrep/blob/master/.github/workflows/release.yml)
- [bat CICD.yml](https://github.com/sharkdp/bat/blob/master/.github/workflows/CICD.yml)
- [fd CICD.yml](https://github.com/sharkdp/fd/blob/master/.github/workflows/CICD.yml)
- [delta cd.yml](https://github.com/dandavison/delta/blob/main/.github/workflows/cd.yml)
- [eza justfile](https://github.com/eza-community/eza)
- [starship release.yml](https://github.com/starship/starship/blob/master/.github/workflows/release.yml)
- [zoxide release.yml](https://github.com/ajeetdsouza/zoxide/blob/main/.github/workflows/release.yml)
- [just release.yaml](https://github.com/casey/just/blob/master/.github/workflows/release.yaml)
- [jj release.yml](https://github.com/jj-vcs/jj/blob/main/.github/workflows/release.yml)
- [typst release.yml](https://github.com/typst/typst/blob/main/.github/workflows/release.yml)
- [uv release.yml](https://github.com/astral-sh/uv/blob/main/.github/workflows/release.yml)
- [uv dist-workspace.toml](https://github.com/astral-sh/uv/blob/main/dist-workspace.toml)
- [ruff dist-workspace.toml](https://github.com/astral-sh/ruff/blob/main/dist-workspace.toml)
- [mise release.yml](https://github.com/jdx/mise/blob/main/.github/workflows/release.yml)
- [nushell release.yml](https://github.com/nushell/nushell/blob/main/.github/workflows/release.yml)

### cargo-dist

- [cargo-dist documentation](https://axodotdev.github.io/cargo-dist/)
- [cargo-dist GitHub releases](https://github.com/axodotdev/cargo-dist/releases) —
  latest stable: v0.30.4 (Feb 2026)
- [cargo-dist configuration reference](https://axodotdev.github.io/cargo-dist/book/reference/config.html)
- [cargo-dist CHANGELOG](https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md)
- [cargo-dist cross-compilation issue #74](https://github.com/axodotdev/cargo-dist/issues/74)
  — open since Feb 2023
- [cargo-dist Platforms wiki](https://github.com/axodotdev/cargo-dist/wiki/Platforms) —
  last updated Mar 2023, partially outdated

### Background

- [Ruff build and release process (DeepWiki)](https://deepwiki.com/astral-sh/ruff/8.4-release-process)
- [Packaging Rust for npm (Orhun’s blog)](https://blog.orhun.dev/packaging-rust-for-npm/)
- [Release engineering blog post (axo.dev)](https://blog.axo.dev/2023/02/cargo-dist)
- [cargo-binstall](https://github.com/cargo-bins/cargo-binstall)
- [maturin documentation](https://www.maturin.rs/)
- [ripgrep release process (DeepWiki)](https://deepwiki.com/BurntSushi/ripgrep/3.4-release-process)
