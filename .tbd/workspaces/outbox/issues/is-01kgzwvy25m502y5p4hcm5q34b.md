---
close_reason: "Fixed: context managers → RAII mapping with examples added"
closed_at: 2026-02-09T00:55:15.469Z
created_at: 2026-02-09T00:29:48.996Z
dependencies: []
id: is-01kgzwvy25m502y5p4hcm5q34b
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 4.3 Add context managers → RAII mapping with examples
type: is
updated_at: 2026-02-09T00:55:59.810Z
version: 3
---
with open→fs::read_to_string (RAII), with lock→let _guard=mutex.lock(), custom→impl Drop. Fix in: reference/python-to-rust-mapping-reference.md after L147
