---
close_reason: "Review complete: 4 CRITICAL (dict->HashMap insertion order, assert->debug_assert strips checks, ~=1.4 version mapping wrong, ==1.4.* mapping wrong), 16 IMPORTANT (int precision, frozenset misleading, match on String, str.find byte offset, re.match conflates bool/match, re.findall wrong type, Callable missing 3 traits, dunder methods absent, generators absent, context managers absent, dataclasses absent, enum.Enum absent, async absent, parallelism absent), 12 SUGGESTION, 10 NIT"
closed_at: 2026-02-08T19:59:00.699Z
created_at: 2026-02-08T19:36:18.066Z
dependencies: []
id: is-01kgzc2fwkzjac4aaekdf6n4f9
kind: task
labels: []
parent_id: is-01kgzc0ztxrrfganr2h863rhky
priority: 2
status: closed
title: Review reference/python-to-rust-mapping-reference.md
type: is
updated_at: 2026-02-09T01:18:11.416Z
version: 7
---
Exhaustive review of type/construct mappings: primitives, collections, control flow, error handling, functions/closures, mutability, decorators, modules, type hints. Verify every Python→Rust mapping for correctness. Check code examples compile.
