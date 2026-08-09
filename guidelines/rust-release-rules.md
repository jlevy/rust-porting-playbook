---
title: Rust Release Rules
description: Rules for reproducible Rust artifacts, least-privilege publishing, and multi-channel releases
author: Joshua Levy (github.com/jlevy) with LLM assistance
category: rust
---
# Rust Release Rules

Use these rules when a Rust project publishes crates, binaries, installers, packages, or
container images. A release is a supply-chain operation: it converts a reviewed commit
into artifacts users will execute and grants automation permission to publish them.

**Related:** [`rust-project-setup.md`](rust-project-setup.md),
[`rust-testing-rules.md`](rust-testing-rules.md),
[`SUPPLY-CHAIN-SECURITY.md`](../SUPPLY-CHAIN-SECURITY.md), and
`tbd guidelines supply-chain-hardening release-notes-guidelines`.

## Define One Release Identity

- Make a reviewed git commit the source of every artifact.
- Use one version and tag for all channels in the same release.
- State whether the tag or a manifest field is authoritative and derive other metadata
  from it.
- Refuse to publish when tag, package metadata, or generated version output disagree.
- Decide how prereleases, yanked releases, rebuilds, and MSRV changes are versioned.
- Never rebuild different bytes under an existing immutable version.

A tag-triggered workflow is a common design.
Manual dispatch may provide a dry-run, but publishing still needs an immutable commit
and an explicit release identity.

## Require a Clean Pre-Release Gate

Before creating or accepting a release tag, verify:

- formatting, lint, tests, documentation, and project-specific checks;
- supported feature combinations and platforms;
- the declared MSRV where applicable;
- dependency and license policy;
- package contents and excluded files;
- release notes for the exact commit range;
- version consistency;
- no uncommitted or unpushed release input.

The release workflow must repeat the checks that protect publishing.
A local command is convenience, not proof that the remote tag still names the same
state.

## Choose Automation Deliberately

Use a release generator such as cargo-dist when its generated artifact, installer,
platform, and permission model matches the project.
Use a custom workflow when the project needs unsupported channels or policy.

- Review generated workflows before committing them.
- Pin the generator and record the reviewed version.
- Regenerate through one documented command and review the diff.
- Keep project-specific publishing logic outside generated files where practical.
- Do not hand-roll an elaborate matrix merely because older projects did.
- Do not accept a generator’s default permissions or mutable action references without
  review.

Custom workflows should move branching, archive construction, and registry probes into
small testable programs rather than long inline shell blocks.

## Minimize Workflow Authority

Apply the project-wide CI controls in
[`rust-project-setup.md`](rust-project-setup.md#design-ci-as-independent-evidence).
Release workflows add these narrower authority rules:

- Grant `contents: write`, `packages: write`, or `id-token: write` only to the job that
  needs it.
- Use protected release environments when publication warrants an approval boundary.
- Prefer registry trusted publishing through OIDC to stored long-lived tokens.
- Keep build jobs unable to publish; pass reviewed artifacts to separate publish jobs.
- Do not run untrusted pull-request code in a context that has release credentials.

If a channel cannot use short-lived credentials, scope its token to one project, store
it in the narrowest environment, rotate it, and ensure forked code cannot access it.

## Apply Cool-Off and Source Review to Release Tooling

Release generators, GitHub Actions, cross-compilers, package builders, and upload tools
are executable dependencies.

- Apply the project’s cool-off period to new versions.
- Review source and release diffs before upgrading.
- Pin exact versions, action commits, container digests, and downloaded checksums.
- Disable package install scripts and source builds unless reviewed and required.
- Record a documented exception when a time-critical security fix cannot wait.
- Treat a changed build image or runner label as a release-input change.

See `tbd guidelines supply-chain-hardening` for the full installation and workspace
policy.

## Build Artifacts Once Per Target

Each matrix entry should have one declared target, toolchain, runner, and packaging
rule. Build the artifact once and promote those exact bytes through validation and
publishing.

- Use `--locked` and the committed dependency resolution.
- Build from the tagged commit, not a floating branch.
- Record the compiler, target, features, and relevant environment.
- Keep target-specific linker and native dependencies explicit.
- Use native runners when cross-compilation would prevent meaningful smoke tests.
- Fail all-or-nothing releases if a required target fails; do not silently publish a
  partial platform set.

Cross-compilation adds a compiler, linker, sysroot, and native-library trust boundary.
Use it when necessary, not merely to reduce matrix size.

## Package Predictably

Artifact names should include project, version, and target.
Archives should contain only the files users expect:

- the executable or library
- license files
- a concise readme or install note
- shell completions or man pages when supported

Apply these packaging rules:

- Use deterministic file ordering and normalized timestamps where reproducible archives
  are a goal.
- Generate SHA-256 checksums for downloadable artifacts.
- Emit an SBOM or embedded dependency metadata when the project policy requires it.
- Sign artifacts or attest provenance when consumers have a verification path; a
  signature nobody verifies is not a substitute for other controls.
- Test archive extraction on every supported host format.

## Smoke-Test the Packaged Artifact

Do not validate only `target/release/<binary>` and assume the archive, wheel, installer,
or package contains the same working program.

For each natively runnable artifact:

1. install or extract it in an empty temporary environment;
2. run `--version` and a representative command;
3. verify expected executable names and files;
4. check dynamic-library and runtime assumptions;
5. uninstall or discard the isolated environment.

For cross-compiled artifacts that cannot run on the builder, use a native validation job
or explicitly record the remaining evidence gap.

## Choose Channels by Audience

No distribution channel is universally primary.
Choose the smallest set that serves the actual users.

| Channel | Best fit | Key considerations |
| --- | --- | --- |
| crates.io | Rust developers and library consumers | source build, feature/API contract, trusted publishing |
| GitHub Releases | direct binary downloads and automation | checksums, platform naming, installer trust |
| OS package manager | users of that platform | independent review cadence, formula/manifest updates |
| PyPI wheel via maturin | Python users and Rust replacements for Python CLIs | wheel tags, Python packaging metadata, OIDC |
| container registry | services and deployment tooling | base image digest, SBOM, runtime user and capabilities |

Adding a channel creates a long-term compatibility and incident-response obligation.
Do not publish everywhere solely to maximize the number of install commands.

## Publish Rust Crates Safely

- Inspect `cargo package --list` and the packaged crate before publishing.
- Use `cargo publish --dry-run` as evidence, not as the only release test.
- Publish workspace crates in dependency order and make reruns idempotent.
- Use crates.io trusted publishing when available.
- Keep internal workspace packages marked `publish = false`.
- Run semver checks for libraries whose public API compatibility is promised.
- Remember that yanking prevents new resolution but does not erase downloaded source.

## Publish Binary Wheels Deliberately

Maturin `bindings = "bin"` can package a Rust executable as a Python wheel.
Use this when the existing or intended audience installs tools through Python packaging.

- Keep Cargo as the version source or validate exact version synchronization.
- Build the documented wheel-tag matrix, including the minimum supported libc and macOS
  versions.
- Include an sdist only when source builds are supported and tested.
- Smoke-test every native wheel’s installed console command.
- Publish through PyPI trusted publishing.
- Make repeated workflow runs detect already-published immutable versions without
  treating a conflicting artifact as success.

See
[`research-rust-cli-pypi-distribution.md`](../docs/project/research/research-rust-cli-pypi-distribution.md)
for detailed, date-sensitive evidence and examples.

## Coordinate Multiple Channels Without Rebuilding

A multi-channel release should have:

1. one plan job that validates the release identity and intended channels;
2. build jobs that produce target artifacts;
3. validation jobs that consume those artifacts;
4. channel jobs that publish the validated bytes;
5. an announcement job that runs only after required channels succeed.

- Make each channel independently retryable.
- Detect prior publication and distinguish an identical existing version from a
  conflict.
- Prevent concurrent releases of the same version.
- Report exactly which channels completed if the orchestration fails.
- Never print a global success message while a required channel is skipped or failed.

## Test Release Logic Outside the Workflow

Complex release logic should be testable without creating a tag or granting publish
credentials.

Good candidates for checked-in scripts include:

- tag and version parsing;
- release-plan resolution;
- archive naming and construction;
- package-content validation;
- registry existence checks;
- target-to-runner mapping;
- checksums and manifest generation;
- installed-artifact smoke tests.

Test success, malformed input, partial state, registry errors, and reruns.
The workflow should orchestrate these programs and pass structured outputs between jobs.

## Prepare for Release Incidents

Document who can:

- revoke or rotate publishing credentials;
- remove or quarantine compromised workflow access;
- yank a crate or remove a package version where the registry permits it;
- publish a fixed version and security notice;
- verify which commits and artifacts are affected.

Retain provenance, checksums, logs, and the exact release commit long enough to answer
those questions. Do not overwrite evidence during a rerun.

## Release Checklist

- [ ] One immutable commit and version identify the release.
- [ ] Local and remote pre-release gates pass.
- [ ] Release tools and actions are reviewed and immutably pinned.
- [ ] Build jobs have no publishing authority.
- [ ] Publishing uses least privilege and short-lived credentials where possible.
- [ ] Every required target produces a named, checksummed artifact.
- [ ] Packaged artifacts, not only build outputs, pass smoke tests.
- [ ] Channel selection matches documented audiences.
- [ ] Multi-channel reruns are idempotent and conflicts fail.
- [ ] Release notes describe the exact commit range.
- [ ] Incident and recovery actions are documented.

## Related Guidelines

- [`rust-project-setup.md`](rust-project-setup.md)
- [`rust-testing-rules.md`](rust-testing-rules.md)
- [`rust-cli-rules.md`](rust-cli-rules.md)
- [`SUPPLY-CHAIN-SECURITY.md`](../SUPPLY-CHAIN-SECURITY.md)
- `tbd guidelines supply-chain-hardening release-notes-guidelines`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
