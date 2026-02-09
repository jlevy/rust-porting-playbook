---
close_reason: "Fixed: dataclasses → struct-with-derives mapping added"
closed_at: 2026-02-09T00:55:15.886Z
created_at: 2026-02-09T00:29:49.452Z
dependencies: []
id: is-01kgzwvygdfg3vkbk419k8r9yp
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 4.4 Add dataclasses → struct-with-derives mapping
type: is
updated_at: 2026-02-09T00:55:59.816Z
version: 3
---
@dataclass→#[derive(Debug,Clone,PartialEq)], frozen=True→no &mut self, order=True→PartialOrd+Ord. Fix in: reference/python-to-rust-mapping-reference.md new section
