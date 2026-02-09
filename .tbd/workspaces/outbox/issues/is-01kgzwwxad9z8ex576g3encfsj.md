---
created_at: 2026-02-09T00:30:21.004Z
dependencies: []
id: is-01kgzwwxad9z8ex576g3encfsj
kind: task
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 5.2 Fix for/else mapping — show idiomatic iterator solution
type: is
updated_at: 2026-02-09T00:30:21.004Z
version: 1
---
'Use flag variable' is un-idiomatic. Add: if let Some(item) = iter.find(|x| cond(x)). Fix in: reference/python-to-rust-mapping-reference.md L109
