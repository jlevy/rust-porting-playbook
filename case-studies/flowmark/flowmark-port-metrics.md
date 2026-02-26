# Flowmark Metrics Source of Truth

Canonical metrics for the flowmark Python->Rust case study.

**Last updated:** 2026-02-26

**Scope note:** This file distinguishes:
- historical initial-port metrics (2025-11 baseline)
- current v2 metrics (latest synchronized state in this playbook)

## Current Metrics (v2, canonical)

| Metric | Value |
| --- | --- |
| Python app LOC | ~4,400 |
| Rust app LOC | ~6,000 |
| Rust/Python app ratio | ~1.36x |
| Python tests | 292 |
| Rust tests | 442 |
| Python test mapping | 292/292 mapped (100%) |
| Missing mapped Python tests | 0 |
| Workaround comments | 65 (`COMRAK-WORKAROUND`/`FIXME:`) |
| Performance improvement | 20-40x |

## Historical Baseline (initial port snapshot, 2025-11)

| Metric | Value |
| --- | --- |
| Python app LOC | ~2,000 |
| Rust app LOC | ~3,400 |
| Rust/Python app ratio | ~1.7x |
| Python test LOC | ~1,500 |
| Rust test LOC | ~2,900 |

## Usage Rules

- Use the **current metrics** table for top-level summaries and parity status.
- Keep historical values only when they are clearly labeled as baseline history.
- When updating values, update this file first, then propagate to README and case-study
  docs.

## Reproducibility and Evidence

When refreshing metrics, record evidence in a dated artifact note (for example
`case-studies/flowmark/metrics-evidence-YYYY-MM-DD.md`) including:

- Python repo commit hash used for measurement
- Rust repo commit hash used for measurement
- Commands run for LOC/test counts
- Output artifact paths (collected test list outputs, count outputs, or CI logs)

Recommended command pattern (adapt as needed per repo layout):

```bash
# Python app LOC (exclude tests)
rg --files -g '*.py' | rg -v '(^|/)(test|tests)/|(_test\\.py$)' | xargs wc -l

# Python test count
pytest --collect-only -q > artifacts/python-tests-collected.txt

# Rust app LOC
rg --files src -g '*.rs' | xargs wc -l

# Rust test count
cargo test -- --list > artifacts/rust-tests-listed.txt
```
