# Supply Chain Audit Log

**Owner:** Joshua Levy

**Last updated:** 2026-08-08

This reverse-chronological log records repository supply-chain reviews and any
exceptions to [`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md).
Never include tokens, credentials, private hostnames, or raw environment dumps.

## 2026-08-08—Repository Refresh

### Context

| Item | Value |
| --- | --- |
| Date | 2026-08-08 |
| Auditor | Codex, acting for repository owner Joshua Levy |
| Host | macOS 26.5.2, Darwin arm64 |
| Toolchain | Node 24.13.0; npm 11.6.2; Python 3.13.7 default and 3.14.6 validation; local uv 0.11.28 |
| Global npm path | `~/.local/share/fnm/node-versions/v24.13.0/installation/lib/node_modules` |
| Active install protection | `NPM_CONFIG_IGNORE_SCRIPTS=true` |
| Policy mode | Balanced, 14-day cool-off; cutoff 2026-07-25 |

### Scope

- All tracked documentation, agent hooks, executable scripts, tests, CI workflows,
  Dependabot configuration, dependency pins, and research lockfile inventories.
- The Supply Chain Hardening guidebook at commit
  [`06c6e1e6`](https://github.com/jlevy/supply-chain-hardening/commit/06c6e1e6d6a00258728dd111a64dd197de2bd6f0).
- Candidate source and release changes for `get-tbd`, uv, GitHub CLI, Python,
  cargo-dist, maturin, `softprops/action-gh-release`, `actions/checkout`,
  `actions/setup-python`, and `astral-sh/setup-uv`.

Third-party repositories were cloned under the ignored `attic/` directory and reviewed
as data. No third-party code was executed before review.
The guidebook’s `audit_workspace.py` was read in full before its read-only Unicode,
`.pth`, persistence, and autostart checks were run.

### Commands Run

```sh
tbd setup --auto
tbd doctor
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/check_docs.py
UV_NO_BUILD=1 uv --no-config lock --check --script docs/project/research/data/extract_lockfile_inventory.py
python3 scripts/check_dependency_cooloff.py
python3 scripts/check_lockfile_inventories.py
git clone --filter=blob:none --no-checkout https://github.com/jlevy/supply-chain-hardening attic/supply-chain-hardening
git diff <old-tag>..<candidate-tag>
git ls-remote --tags <official-action-repository>
curl -fsSL <official-package-or-release-metadata-url>
```

The angle-bracket commands describe repeated read-only queries against each official
project; exact candidate versions and immutable results are recorded below.

### Raw Findings

| Surface | Finding | Cool-off verdict |
| --- | --- | --- |
| tbd | 0.4.2, published 2026-07-30; repository was on 0.4.0 | Exception required |
| `actions/checkout` | 7.0.1, released 2026-07-20 | Eligible |
| `actions/setup-python` | 7.0.0, released 2026-07-20 | Eligible |
| `astral-sh/setup-uv` | 9.0.0, released 2026-07-21 | Eligible |
| uv | 0.11.32, uploaded 2026-07-23 | Eligible |
| uv | Every reviewed 0.12.x release was newer than the cutoff | Deferred |
| GitHub CLI | 2.96.0, released 2026-07-02; prior installer used predictable `/tmp` paths | Eligible; security-motivated and harden extraction |
| PyYAML | 6.0.3 remains current and was already locked with hashes | Keep |
| CI cache | `setup-uv` could save a reusable cache from pull-request runs | Remove |
| Workspace safety | No CODEOWNERS coverage or hidden-Unicode validation | Add |
| Policy | Install-time rules existed; load-time and open-time rules were missing | Expand |
| Maintenance | `.gitignore` contained three identical `attic/` entries | Deduplicate |
| Workspace scan | No hidden Unicode, executable `.pth`, or host persistence; expected tracked tbd hooks reported as autostart | Review and test |
| OSV | No advisories returned for `get-tbd@0.4.2` or `PyYAML==6.0.3` | Clean at review time |
| Educational actions | `softprops/action-gh-release@v2` and older setup majors | Upgrade eligible live examples |
| Rust guidance | regex 1.12 and cargo-dist 0.31 currency text had drifted | Upgrade live guidance |
| Rust stable | 1.97.1 remained the eligible current stable patch | Refresh live version text |
| PyPI guidance | One maturin currency line lagged 1.14.1 | Correct |
| GitHub security | Dependabot security updates, secret scanning, and push protection enabled; no Dependabot alerts | Keep |
| Default branch | No ruleset or classic branch protection | Carry forward as `rpp-m7uy` |

The initial unit-test run also exposed 15 failures and 8 errors after the stock tbd
0.4.2 setup replaced repository-specific hook hardening.
That was a local integration regression, not evidence of a malicious package.
tbd doctor consequently reports the customized Codex hook file as stale even though its
anchoring and gh-before-tbd order are intentional and regression-tested; `rpp-gdrk`
tracks a supported upstream compatibility mechanism.

### Analysis and Verdict

#### Approved tbd 0.4.2 Exception

The repository owner explicitly requested that the project integration match the latest
globally installed tbd before any other work began.
That is human approval for one exact version, not a general cool-off bypass.
Registry metadata identifies the `get-tbd@0.4.2` artifact, its integrity digest, and a
GitHub Actions OIDC publisher; the official tag at commit
`d893da2807f655ca9b1987d40fa18a56a0e68d04` and source changes were reviewed.
The registry reports SHA-512 integrity
`1IAtf/2/BpFjYLWiXtWyFdWw275Hr2XK2Kl2W93JMcdDQWEieMqraQJomc1HLRLmisQPAbwdfBUc8CdBMU/QwA==`
and SHA-1 shasum `5a1f82b8cd5fdffa2776202d0689d1ca7ca04d0d`. The project pins 0.4.2 in
fallback commands and disables lifecycle scripts for those invocations.

**Verdict:** approved exception.
Preserve the repository’s hardened hooks instead of accepting the stock templates
verbatim.
Roll back to the prior reviewed 0.4.0 integration and restore the hardened hook
diff if validation or production use reveals a regression.

#### Eligible Routine Upgrades

The three action releases and uv 0.11.32 were at least 14 days old on the audit date.
Release notes and source diffs were reviewed, and workflow actions remain pinned to full
SHAs. uv 0.11.32 adds stricter `--locked`/`--check` handling for noncanonical lockfiles
in addition to maintenance fixes.

**Verdict:** upgrade.
Do not adopt uv 0.12 yet; track a re-evaluation after 2026-08-22.

#### GitHub CLI 2.96.0

Version 2.96.0 is outside the cool-off and fixes
[`GHSA-8cg3-r6g9-fpg2`](https://github.com/cli/cli/security/advisories/GHSA-8cg3-r6g9-fpg2),
a command-execution issue involving a malicious Codespace.
Official release checksums were recorded for Linux and macOS on amd64 and arm64.

**Verdict:** upgrade the checksum-verified fallback from 2.92.0 to 2.96.0 and move
download/extraction into a fresh private temporary directory.

#### CI and Workspace Controls

The validation workflow is small enough that a reusable uv cache has negligible value.
[setup-uv v9’s action metadata](https://github.com/astral-sh/setup-uv/blob/v9.0.0/action.yml)
defaults `enable-cache` to `auto` on hosted runners, so omission is not a safe disable;
setting it to `false` closes the pull-request cache-write path without a meaningful
performance tradeoff.
CODEOWNERS coverage and deterministic Unicode validation address open-time changes that
lockfiles cannot see.

**Verdict:** remove the cache and add both workspace controls.

### Actions Taken

| Action | Tracking |
| --- | --- |
| Refreshed tbd integration to 0.4.2 and restored hardened hook behavior | `rpp-6sg9`, `rpp-df39` |
| Upgraded eligible action, uv, and GitHub CLI pins | `rpp-70qs`, `rpp-v6hy` |
| Explicitly disabled setup-uv’s default PR cache writes | `rpp-x41r` |
| Added CODEOWNERS and hidden-Unicode validation | `rpp-eyb1` |
| Expanded the repository policy for load-time and open-time threats | `rpp-exbc` |
| Recorded this exception and audit | `rpp-l15w` |
| Added deterministic 14-day lock-artifact validation and wheel-only execution | `rpp-eiuy` |
| Refreshed current action, regex, cargo-dist, and maturin guidance | `rpp-qb33`, `rpp-2hmy`, `rpp-6ku0`, `rpp-sd3n` |
| Published the dated repository review and refreshed navigation | `rpp-fzwy`, `rpp-aofk` |

### Pending Actions

- [x] Complete full local validation and review the final diff (`rpp-rmxt`): 33 tests
  passed on Python 3.14.6; text/Markdown, lock, cool-off, provenance, syntax, policy,
  and diff checks passed.
- [ ] Re-evaluate uv 0.12 after its cool-off (`rpp-1gar`, deferred to 2026-08-22).
- [ ] Make the hardened Codex hook form semantically acceptable to tbd doctor
  (`rpp-gdrk`).

### Verdict (Summary)

No evidence of compromise was found.
One human-approved, exact-version cool-off exception was required for tbd 0.4.2.
Eligible maintenance and security upgrades are being applied; too-recent uv releases
remain deferred. The highest-impact control gaps were reusable cache writes from pull
requests and unprotected open-time configuration, both addressed by this refresh.
