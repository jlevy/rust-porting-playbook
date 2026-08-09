---
type: is
id: is-01kzkt98nfz7d54ed1qsebg7wk
title: "PR #22 review R7: remove obvious low-signal Rust rules"
kind: bug
status: closed
priority: 3
version: 3
labels: []
dependencies: []
parent_id: is-01kzkt85s5tkgk66em33mvcbts
created_at: 2026-08-09T17:49:14.286Z
updated_at: 2026-08-09T18:08:27.804Z
closed_at: 2026-08-09T18:08:27.804Z
close_reason: "Addressed in 1d0ccd1; all local checks and PR #22 CI pass."
---
PR #22 review R7. Files: guidelines/rust-rules.md:68,197-205; guidelines/rust-cli-rules.md:40-52. Cut baseline advice or retain only the non-obvious failure mode, such as related booleans masking state and omitted-vs-defaulted arguments.
