---
type: is
id: is-01ksn2k47zqg62pgdttx5wysfs
title: Refresh current-comrak version claims in flowmark case study
kind: task
status: closed
priority: 2
version: 2
labels:
  - currency
dependencies: []
parent_id: is-01ksn2h8cx0bv38z2vkdnv4he0
created_at: 2026-05-27T15:59:29.535Z
updated_at: 2026-05-27T16:18:46.148Z
closed_at: 2026-05-27T16:18:46.147Z
close_reason: "Updated forward-looking comrak version claims 0.50+ -> 0.52+ (current May 2026) in library-choices, comrak-bug, migration-plan (x2), and mapping-reference. Reconciled the two divergent NodeValue::Text histories (porting-rules said String pre-0.45/Cow 0.45+; porting-guide said Vec<u8> 0.x/String 0.30+) to the canonical: Vec<u8> pre-0.4, String 0.4-0.44, Cow 0.45+. Historical 0.29 evaluation baseline preserved. Comrak-bug re-test against current still flagged as an open action in that doc."
---
Case studies keep comrak 0.29 as the historical evaluation baseline (correct, leave intact) but also make forward-looking 'current version' claims that are now stale. Current comrak is 0.52.0 (Apr 2026, MSRV 1.85).

Fix:
- Update the 'evolved to 0.30+ through 0.50+' phrasing in case-studies/flowmark/flowmark-port-library-choices.md:97, flowmark-port-migration-plan.md:173, flowmark-port-comrak-bug.md:27.
- Reconcile conflicting NodeValue::Text version-boundary claims: guidelines/python-to-rust-porting-rules.md:209 (String pre-0.45, Cow 0.45+) vs playbooks/python-to-rust-porting-guide.md:777 (Vec<u8> 0.x, String 0.30+). Verify the real history against comrak changelog and state it once, consistently.
- Re-test the comrak bug (flowmark-port-comrak-bug.md:28) against current comrak to see if the workaround can be dropped.
