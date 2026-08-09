# Project Specifications

This is the stable lifecycle index for project implementation plans. Individual plan
files are records of decisions and delivery work, not primary user guidance.

## Active Plans

| Plan | Tracking bead | State |
| --- | --- | --- |
| [TypeScript-to-Rust porting path](active/plan-2026-03-04-typescript-to-rust-porting-path.md) | `rpp-pk9g` | Draft core path |
| [qmd AI application port](active/plan-2026-03-04-qmd-ai-application-porting-path.md) | `rpp-ur4d` | Draft; blocked on the core path |
| [knip TypeScript-to-Rust port](active/plan-2026-03-04-knip-typescript-to-rust-port.md) | `rpp-la67` | Draft application exemplar |

## Completed Plans

| Plan | Delivery | Durable outputs |
| --- | --- | --- |
| [Reusable Rust guideline reorganization](done/plan-2026-08-08-rust-guideline-reorganization.md) | [PR #22](https://github.com/jlevy/rust-porting-playbook/pull/22) | [Rust guideline index](../../../guidelines/README.md) and [reuse review](../../reviews/rust-guideline-reuse-review-2026-08-08.md) |

## Lifecycle

- Keep currently executable plans in `active/` while their implementation beads are
  open.
- Move an implementation-complete, superseded, or intentionally abandoned plan to
  `done/` in the same change that records its outcome.
- Link maintained guidance and durable reviews from repository navigation. Link this
  index, rather than an individual plan, when readers need project-planning history.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
