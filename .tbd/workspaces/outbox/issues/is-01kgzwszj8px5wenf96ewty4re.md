---
created_at: 2026-02-09T00:28:44.999Z
dependencies: []
id: is-01kgzwszj8px5wenf96ewty4re
kind: task
labels: []
parent_id: is-01kgzsz6t5wsggwaxv3tqv5jc1
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 2.4 Add re.search and re.fullmatch regex mappings
type: is
updated_at: 2026-02-09T00:28:44.999Z
version: 1
---
Only re.match covered. Add re.search (no anchor needed), re.fullmatch (both ^/$). Also fix re.match→captures when groups used, fix find_iter return type. Fix in: guidelines/python-to-rust-porting-rules.md L183-196, reference/python-to-rust-mapping-reference.md L214+L217
