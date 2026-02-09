---
created_at: 2026-02-09T00:28:22.132Z
dependencies: []
id: is-01kgzws97nwhmxk5af63hjvfnf
kind: bug
labels: []
parent_id: is-01kgzsz6e4fe510fgy92fzysnf
priority: 0
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 1.8 Fix comrak CowStr type name — wrong library
type: is
updated_at: 2026-02-09T00:28:22.132Z
version: 1
---
CowStr belongs to pulldown-cmark not comrak. Correct version history: Vec<u8> pre-0.4, String 0.4-0.44, Cow<'static,str> 0.45+. Fix in: guidelines/python-to-rust-porting-rules.md L243-245
