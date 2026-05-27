---
type: is
id: is-01ksn2k588xne1yzymfza7n7t6
title: Reconcile internal contradictions in flowmark migration plan
kind: task
status: closed
priority: 3
version: 2
labels:
  - consistency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:30.567Z
updated_at: 2026-05-27T16:21:45.774Z
closed_at: 2026-05-27T16:21:45.773Z
close_reason: "Added dated note at migration-plan §8.2 clarifying the illustrative CI's 'submodules: recursive' is superseded by the chosen hybrid copy+CI-clone strategy (§2.2). Confirmed the workspace-vs-single contradiction already has a dated note (~256-260) and the color-eyre-vs-anyhow code uses an existing cross-reference to §13 (~3147); left those as-is since they're already disambiguated."
---
Net-new contradictions in case-studies/flowmark/flowmark-port-migration-plan.md (not covered by the Feb 2026 review):
- Submodule vs hybrid: CI YAML uses 'submodules: recursive' (~line 2131) but Section 2.2 (~426-649) and decision log D2 recommend against submodules in favor of hybrid copy+CI.
- Workspace vs single package: workspace layout shown (~262-337) while D2 and the doc conclude single-package; the 'for reference' workspace can confuse readers.
- color-eyre vs anyhow: Section 13 recommends color-eyre but code examples (~1006,1043) use anyhow::Result; acknowledged at ~3147 but examples not updated.
Add clear dated notes or align the examples so readers are not misled.
