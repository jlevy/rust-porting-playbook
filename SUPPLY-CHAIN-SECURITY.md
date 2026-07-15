# Supply-Chain Security

This repository follows a 14-day cool-off for new dependency releases unless a human
approves and records a specific exception.

## Repository Rules

- Pin executable GitHub Actions to full commit SHAs and include the corresponding
  release tag in a comment.
- Pin Python dependencies exactly and commit hash-bearing lockfiles.
- Use locked or frozen installs in CI.
- Do not use unversioned `npx`, `uvx`, `cargo install`, `curl | sh`, or equivalent
  zero-install execution in repository automation.
- Disable package lifecycle scripts by default when using Node package managers.
- Review dependency and lockfile diffs as code changes.

The lockfile inventory utility is a standalone PEP 723 script.
Its only runtime dependency, PyYAML, is pinned in the script and in the adjacent
`*.py.lock` file. CI uses `uv --no-config ... --locked` so local resolver configuration
cannot change that environment.
CI downloads the tbd and qmd source lockfiles only from full-commit GitHub URLs,
verifies their recorded SHA-256 digests, and byte-compares every regenerated inventory
artifact with the committed research data.

GitHub Actions in this repository are pinned to immutable SHAs.
Version comments are for maintainers and dependency-update tooling; execution never
relies on a floating major-version tag.
Dependabot checks those pins weekly and applies the same 14-day cool-off before opening
normal version-update pull requests.
Security updates are exempt so known vulnerabilities can be remediated promptly.

For the broader threat model and ecosystem-specific controls, see the
[Supply Chain Hardening guidebook](https://github.com/jlevy/supply-chain-hardening).
