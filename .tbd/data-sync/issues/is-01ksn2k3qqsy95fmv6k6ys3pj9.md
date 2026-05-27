---
type: is
id: is-01ksn2k3qqsy95fmv6k6ys3pj9
title: Reconcile color-eyre vs anyhow guidance and fix stale maintenance claims
kind: task
status: open
priority: 2
version: 1
labels:
  - consistency
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:29.015Z
updated_at: 2026-05-27T15:59:29.015Z
---
Error-handling guidance is split and partly stale. color-eyre 0.6.5 was released March 2026, so 'last published 2023 / maintenance-only' is now inaccurate.

Fix:
- Resolve the split: guidelines/rust-general-rules.md:98-106 says prefer anyhow (color-eyre maintenance-only), but guidelines/rust-project-setup.md:64 and playbooks/python-to-rust-playbook.md:598 default to color-eyre, and the flowmark migration plan recommends color-eyre. Pick one canonical recommendation and make all docs agree.
- references/rust-cli-app-patterns.md:232 says color-eyre 'last published 2023' — correct to reflect 0.6.5 (2026).
- references/python-to-rust-mapping-reference.md:1054 lists color-eyre quality 'Excellent' with no caveat — align with whatever the canonical recommendation becomes.
