---
created_at: 2026-02-09T00:30:24.231Z
dependencies: []
id: is-01kgzwx0f87jdja27f0qqr97rn
kind: bug
labels: []
parent_id: is-01kgzsz7yntqwrmm79pqdp2x46
priority: 2
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 5.9 Fix LineBreakMode::None shadowing Option::None
type: is
updated_at: 2026-02-09T00:30:24.231Z
version: 1
---
enum variant None shadows Option::None causing confusing errors. Rename to NoBreaks or Off. Fix in: guidelines/rust-general-rules.md L135
