---
type: is
id: is-01ksn2kjmf5p2pq7xcf4f9dp36
title: Unify SIGPIPE handling guidance across CLI docs
kind: task
status: closed
priority: 3
version: 2
labels:
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:44.271Z
updated_at: 2026-05-27T16:22:41.412Z
closed_at: 2026-05-27T16:22:41.411Z
close_reason: "Cross-linked the two SIGPIPE approaches (sigpipe crate in rust-cli-best-practices vs raw libc::signal in rust-cli-app-patterns) and noted they are equivalent — crate avoids an unsafe block, direct call avoids a dependency. Fixed anchor to #sigpipe-handling. cli-porting guideline already presents the libc reset as Option 1 internally, consistent with this."
---
Two different SIGPIPE approaches are recommended without cross-reference: references/rust-cli-best-practices.md:275 recommends the 'sigpipe = 0.1' crate, while references/rust-cli-app-patterns.md:497-499 (with libc = 0.2 at line 506) and guidelines/python-to-rust-cli-porting.md:175 use a raw libc::signal call. Pick one primary recommendation, present the other as an alternative, and cross-link so readers do not see conflicting advice.
