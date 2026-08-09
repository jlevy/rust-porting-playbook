---
type: is
id: is-01kzj900apxtz3eq7mpkz5xv69
title: Harden the README bootstrap against open-time repository risk
kind: task
status: closed
priority: 1
version: 2
labels:
  - documentation
  - supply-chain
dependencies: []
parent_id: is-01kzj7wjwrv2swn2r4ebapcqgk
created_at: 2026-08-09T03:27:50.613Z
updated_at: 2026-08-09T03:59:50.568Z
closed_at: 2026-08-09T03:59:50.568Z
close_reason: Implemented the reviewed install/load/open-time policy, explicit cache disable, CODEOWNERS and all-text Unicode gate, pre-open bootstrap, wheel-only execution, and deterministic 14-day lock-artifact check; targeted and full Python 3.14 validation pass.
---
Add a concise pre-open inspection and fixed-commit recording step to the Quick Start so copied bootstrap instructions do not treat freshly cloned submodules or their agent configuration as automatically trusted.
