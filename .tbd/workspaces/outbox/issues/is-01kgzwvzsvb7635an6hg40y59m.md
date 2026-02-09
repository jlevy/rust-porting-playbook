---
close_reason: "Fixed: parallelism patterns mapping added"
closed_at: 2026-02-09T00:55:17.146Z
created_at: 2026-02-09T00:29:50.778Z
dependencies: []
id: is-01kgzwvzsvb7635an6hg40y59m
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 4.7 Add parallelism patterns mapping table
type: is
updated_at: 2026-02-09T01:18:11.814Z
version: 5
---
multiprocessing.Pool.map→rayon par_iter, threading.Thread→std::thread::spawn, concurrent.futures→rayon/tokio. Fix in: reference/python-to-rust-mapping-reference.md new section
