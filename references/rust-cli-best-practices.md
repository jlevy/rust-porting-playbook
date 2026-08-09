---
title: Rust CLI Best Practices Map
description: Navigation map for the standalone Rust guideline suite and supporting research
---
# Rust CLI Best Practices Map

Rust best practices are organized as focused guidelines so each topic can be loaded and
maintained independently.

| Need | Guideline |
| --- | --- |
| Language, ownership, APIs, errors, unsafe, async | [`rust-rules.md`](../guidelines/rust-rules.md) |
| Cargo, packages, lint, CI, dependencies | [`rust-project-setup.md`](../guidelines/rust-project-setup.md) |
| CLI architecture, streams, exits, terminal behavior | [`rust-cli-rules.md`](../guidelines/rust-cli-rules.md) |
| Filesystem safety and mutation | [`rust-filesystem-rules.md`](../guidelines/rust-filesystem-rules.md) |
| Tests, fixtures, properties, platforms | [`rust-testing-rules.md`](../guidelines/rust-testing-rules.md) |
| Artifacts, channels, and publishing | [`rust-release-rules.md`](../guidelines/rust-release-rules.md) |
| Comprehensive code review | [`rust-code-review-rules.md`](../guidelines/rust-code-review-rules.md) |

For source-language parity, mappings, and synchronization, use the separate porting
guidelines and playbooks.

## 6.4 Release CI Workflow

See [`rust-release-rules.md`](../guidelines/rust-release-rules.md) for the maintained
release CI rules. Detailed, date-sensitive evidence remains in
[`research-rust-cli-binary-distribution.md`](../docs/project/research/research-rust-cli-binary-distribution.md).

## 6.5 Multi-Channel Distribution

See
[Choose Channels by Audience](../guidelines/rust-release-rules.md#choose-channels-by-audience)
for current decision guidance and
[`research-rust-cli-pypi-distribution.md`](../docs/project/research/research-rust-cli-pypi-distribution.md)
for the detailed PyPI/maturin investigation.

## 7.3 Parity Drift Detection for Ports

See [`cross-language-test-mapping.md`](cross-language-test-mapping.md) and
[`test-coverage-for-porting.md`](../guidelines/test-coverage-for-porting.md).

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
