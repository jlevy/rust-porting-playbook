---
created_at: 2026-02-09T00:29:50.351Z
dependencies: []
id: is-01kgzwvzcgd2qpxk7z1f9z7fww
kind: task
labels: []
parent_id: is-01kgzsz7jk8g5jb0vde9jd762w
priority: 1
spec_path: docs/project/specs/active/plan-2026-02-08-playbook-review-fixes.md
status: open
title: 4.6 Add async patterns mapping table
type: is
updated_at: 2026-02-09T00:29:50.351Z
version: 1
---
async def→async fn, await→.await, asyncio.run→#[tokio::main], asyncio.gather→tokio::join!, asyncio.sleep→tokio::time::sleep. Fix in: reference/python-to-rust-mapping-reference.md new section
