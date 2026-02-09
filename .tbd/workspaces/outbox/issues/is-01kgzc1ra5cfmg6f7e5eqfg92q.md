---
close_reason: "Review complete: 2 CRITICAL (format!() advice misleading for hot paths, claims Edition 2024 focus but omits all edition-specific changes), 8 IMPORTANT (MSRV policy overstated, impl Into<String> missing ownership context, LineBreakMode::None shadows Option::None, missing Arc<Mutex> anti-pattern, error handling misleading, Cow/arena explanations insufficient), 9 SUGGESTION, 6 NIT"
closed_at: 2026-02-08T19:58:30.883Z
created_at: 2026-02-08T19:35:53.924Z
dependencies: []
id: is-01kgzc1ra5cfmg6f7e5eqfg92q
kind: task
labels: []
parent_id: is-01kgzc0ztxrrfganr2h863rhky
priority: 2
status: closed
title: Review guidelines/rust-general-rules.md
type: is
updated_at: 2026-02-09T00:31:03.535Z
version: 4
---
Review Edition 2024 patterns, ownership/borrowing advice, error handling (thiserror/anyhow), string handling, regex patterns, code organization, anti-patterns, testing, performance. Fact-check version requirements and API details.
