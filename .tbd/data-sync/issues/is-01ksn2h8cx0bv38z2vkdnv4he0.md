---
type: is
id: is-01ksn2h8cx0bv38z2vkdnv4he0
title: "May 2026 currency review: refresh libraries, tooling, and best practices"
kind: epic
status: closed
priority: 1
version: 14
labels:
  - review
  - currency
dependencies: []
child_order_hints:
  - is-01ksn2j8h9kqsnfayv2rpctqny
  - is-01ksn2j8s3er00ktz5rhtp6s9s
  - is-01ksn2j92bywfz6aarqp7nqtqb
  - is-01ksn2j9agaathq5sbd99429cv
  - is-01ksn2k3qqsy95fmv6k6ys3pj9
  - is-01ksn2k3zsq0nvy38swg36eckt
  - is-01ksn2k47zqg62pgdttx5wysfs
  - is-01ksn2k4g0v6cdhvxjh0tw08rr
  - is-01ksn2k4r3sbcj11amjmbtbmzj
  - is-01ksn2k502a1ndasf4jqxw9etc
  - is-01ksn2k588xne1yzymfza7n7t6
  - is-01ksn2kjmf5p2pq7xcf4f9dp36
created_at: 2026-05-27T15:58:28.252Z
updated_at: 2026-05-27T16:22:56.474Z
closed_at: 2026-05-27T16:22:56.474Z
close_reason: "All 12 child beads implemented and closed. Currency refresh complete: crate pins (regex/clap/tempfile/fs-err/thiserror), cargo-dist->dist 0.31, maturin guidance, GitHub Actions pins, color-eyre/anyhow reconciliation, serde_norway note, comrak 0.52 claims + Text history, performance ranges anchored to measured 20-40x, date markers, Rust 1.95 note, migration-plan submodule note, SIGPIPE cross-link. 14 commits on claude/focused-goodall-PdlKw."
---
Senior engineering currency review of the Rust Porting Playbook (May 2026). A prior comprehensive review landed Feb 2026 (see _meta/plans/done/plan-2026-02-08-playbook-review-fixes.md); this pass finds what has drifted since plus net-new consistency gaps.

Scope: prescriptive docs (guidelines/, references/, playbooks/) must be current; research docs (docs/project/research/) are point-in-time surveys whose 'latest stable' claims need refreshing; case studies (case-studies/flowmark/) are historical records — only their forward-looking 'current version' factual claims should be updated, not the historical decisions.

Verified current versions as of 2026-05-27: Rust stable 1.95.0; clap 4.6.1; regex 1.12.3; comrak 0.52.0; indicatif 0.18.4; maturin 1.13.3; cargo-dist→'dist' 0.31.0; color-eyre 0.6.5 (released Mar 2026); serde_norway now better-maintained than serde_yaml_ng; actions/checkout v6, setup-python v6, setup-uv v7.5.

Child issues track each theme. File-and-fix-later: this epic captures filing; fixes are separate.
