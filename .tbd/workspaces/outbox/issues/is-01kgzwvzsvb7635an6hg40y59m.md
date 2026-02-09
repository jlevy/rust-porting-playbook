---
created_at: 2026-02-09T00:29:50.778Z
dependencies: []
id: is-01kgzwvzsvb7635an6hg40y59m
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 4.7 Add parallelism patterns mapping table
type: is
updated_at: 2026-02-09T00:29:50.778Z
version: 1
---
multiprocessing.Pool.map→rayon par_iter, threading.Thread→std::thread::spawn, concurrent.futures→rayon/tokio. Fix in: reference/python-to-rust-mapping-reference.md new section
