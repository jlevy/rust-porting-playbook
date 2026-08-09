---
type: is
id: is-01kzkt9ahcyrcebwyayjnyy1j4
title: "PR #22 review S3: add contrastive Rust antipattern examples"
kind: bug
status: in_progress
priority: 3
version: 2
labels: []
dependencies: []
parent_id: is-01kzkt85s5tkgk66em33mvcbts
created_at: 2026-08-09T17:49:16.202Z
updated_at: 2026-08-09T17:49:46.842Z
---
PR #22 review S3. Files: guidelines/rust-rules.md:34-43,100-103,180-193; guidelines/rust-filesystem-rules.md:132-158. Add focused BAD/GOOD examples for clone-to-silence-borrowing, discarded fallible results, lock-held-across-await, and filter_map(Result::ok).
