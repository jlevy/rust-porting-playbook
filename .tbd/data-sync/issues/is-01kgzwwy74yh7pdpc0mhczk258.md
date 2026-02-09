---
close_reason: "Fixed: derive guidance added for ported structs"
closed_at: 2026-02-09T00:55:30.315Z
created_at: 2026-02-09T00:30:21.922Z
dependencies: []
id: is-01kgzwwy74yh7pdpc0mhczk258
kind: task
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: closed
title: 5.4 Add derive guidance for ported structs
type: is
updated_at: 2026-02-09T01:18:11.859Z
version: 5
---
dataclasses→struct+derive but which derives? Minimum: Debug,Clone,PartialEq. Fix in: guidelines/python-to-rust-porting-rules.md L145
