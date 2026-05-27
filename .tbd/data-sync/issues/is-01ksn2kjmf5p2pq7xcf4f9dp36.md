---
type: is
id: is-01ksn2kjmf5p2pq7xcf4f9dp36
title: Unify SIGPIPE handling guidance across CLI docs
kind: task
status: open
priority: 3
version: 1
labels:
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:44.271Z
updated_at: 2026-05-27T15:59:44.271Z
---
Two different SIGPIPE approaches are recommended without cross-reference: references/rust-cli-best-practices.md:275 recommends the 'sigpipe = 0.1' crate, while references/rust-cli-app-patterns.md:497-499 (with libc = 0.2 at line 506) and guidelines/python-to-rust-cli-porting.md:175 use a raw libc::signal call. Pick one primary recommendation, present the other as an alternative, and cross-link so readers do not see conflicting advice.
