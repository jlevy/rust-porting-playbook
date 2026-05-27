---
type: is
id: is-01ksn2k3zsq0nvy38swg36eckt
title: Evaluate serde_norway as successor to serde_yaml_ng
kind: task
status: open
priority: 2
version: 1
labels:
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:29.272Z
updated_at: 2026-05-27T15:59:29.272Z
---
Docs recommend serde_yaml_ng as the replacement for the archived serde_yaml. As of 2026, serde_yaml_ng still depends on the unmaintained unsafe-libyaml, while serde_norway (uses unsafe-libyaml-norway) is the more actively maintained fork.

Action: evaluate whether to switch the recommendation (or at least add a note) in references/python-to-rust-mapping-reference.md:1046, playbooks/python-to-rust-playbook.md:89, playbooks/python-to-rust-porting-guide.md:258, and case-studies/flowmark/flowmark-port-migration-plan.md:704. Confirm current maintenance/soundness status of both before deciding.
