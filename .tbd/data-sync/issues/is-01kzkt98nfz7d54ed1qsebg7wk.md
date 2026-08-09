---
type: is
id: is-01kzkt98nfz7d54ed1qsebg7wk
title: "PR #22 review R7: remove obvious low-signal Rust rules"
kind: bug
status: in_progress
priority: 3
version: 2
labels: []
dependencies: []
parent_id: is-01kzkt85s5tkgk66em33mvcbts
created_at: 2026-08-09T17:49:14.286Z
updated_at: 2026-08-09T17:49:45.056Z
---
PR #22 review R7. Files: guidelines/rust-rules.md:68,197-205; guidelines/rust-cli-rules.md:40-52. Cut baseline advice or retain only the non-obvious failure mode, such as related booleans masking state and omitted-vs-defaulted arguments.
