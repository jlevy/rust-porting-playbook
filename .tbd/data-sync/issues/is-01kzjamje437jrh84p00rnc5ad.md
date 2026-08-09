---
type: is
id: is-01kzjamje437jrh84p00rnc5ad
title: Make hardened Codex hooks compatible with tbd doctor
kind: task
status: open
priority: 2
version: 1
labels:
  - tbd
  - automation
  - supply-chain
dependencies: []
parent_id: is-01kzj7wjwrv2swn2r4ebapcqgk
created_at: 2026-08-09T03:56:33.091Z
updated_at: 2026-08-09T03:56:33.091Z
---
tbd 0.4.2 doctor flags .codex/hooks.json as stale because this repository intentionally anchors every command through git rev-parse and runs the pinned gh bootstrap before tbd prime. Re-running stock setup would regress tested behavior. Add a supported customization/semantic-equivalence mechanism upstream or teach doctor to accept this hardened form; until then preserve the reviewed hooks and treat the single doctor integration warning as expected.
