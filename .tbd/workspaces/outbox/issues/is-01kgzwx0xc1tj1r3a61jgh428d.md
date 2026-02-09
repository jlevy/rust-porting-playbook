---
close_reason: "Fixed: approx crate added for pytest.approx mapping"
closed_at: 2026-02-09T00:55:36.616Z
created_at: 2026-02-09T00:30:24.683Z
dependencies: []
id: is-01kgzwx0xc1tj1r3a61jgh428d
kind: task
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 5.10 Add pytest.approx → approx crate mapping
type: is
updated_at: 2026-02-09T01:18:11.899Z
version: 5
---
Manual abs() < epsilon is error-prone near zero. Add approx crate assert_relative_eq!. Fix in: reference/python-to-rust-mapping-reference.md L297
