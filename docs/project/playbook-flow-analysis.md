# Playbook Flow Analysis

A visual map of the Rust Porting Playbook's process flow, decision gates, resource
dependencies, and document relationships.

## 1. Process Flow: The 8-Phase Porting Lifecycle

These diagrams show the end-to-end process, including decision gates that block
progression and feedback loops that send you back to earlier phases.

### Preliminaries (Phases 0-1)

```mermaid
flowchart TD
    START([Start: Python Project]) --> P1

    subgraph P1["Phase 1: Assess"]
        P1_1[Measure codebase<br/>LOC, modules, entry points]
        P1_2[Inventory dependencies<br/>with risk ratings]
        P1_3[Measure test coverage]
        P1_4[Identify ambiguous behavior<br/>write clarifying tests]
        P1_1 --> P1_2 --> P1_3 --> P1_4
    end

    P1_4 --> G1{Gate: Ready to port?}
    G1 -->|"Coverage >=80%<br/>All deps have Rust equivalents<br/>Scope understood"| READY([Proceed to Phase 2 ▶])
    G1 -->|"Coverage gaps"| P0A(["⟲ Phase 0: Enhance test coverage<br/>(repeat gate when done)"])
    G1 -->|"Missing Rust<br/>equivalents"| P0B(["⟲ Phase 0: Research alternatives<br/>(repeat gate when done)"])

    style P0A fill:#efebe9,stroke:#795548
    style P0B fill:#efebe9,stroke:#795548
    style P1 fill:#e8f4f8,stroke:#2196F3
    style G1 fill:#fff9c4,stroke:#FFC107
```

### Porting (Phases 2-8)

```mermaid
flowchart TD
    BEGIN([Phase 1 gate passed ✓]) --> P2

    subgraph P2["Phase 2: Research & Library Evaluation"]
        P2_fast{Low-dependency<br/>project?}
        P2_fast -->|Yes| P2_quick[Map to standard equivalents<br/>regex, serde_json, clap]
        P2_fast -->|No| P2_1[Evaluate 2-3 candidates<br/>per high-risk dep]
        P2_1 --> P2_2[Create feature matrices]
        P2_2 --> P2_3[Run proof-of-concept<br/>with real inputs]
        P2_3 --> P2_4[Count and categorize diffs]
        P2_4 --> P2_5[Document decisions<br/>rationale + fallback plans]
        P2_quick --> P2_5
        P2_5 --> P2_6[Optional: best-practices<br/>survey for app type]
    end

    P2 --> P3

    subgraph P3["Phase 3: Plan"]
        P3_1[Define architecture<br/>single crate vs workspace]
        P3_2[Create feature parity matrix]
        P3_3[Plan module porting order<br/>leaf → integration → CLI]
        P3_4[Define acceptance criteria]
        P3_5[Budget effort<br/>35-50% for workarounds]
        P3_1 --> P3_2 --> P3_3 --> P3_4 --> P3_5
    end

    P3 --> P4

    subgraph P4["Phase 4: Set Up"]
        P4_1["cargo init project-rs"]
        P4_2[Configure Cargo.toml<br/>edition, MSRV, lints]
        P4_3[Add Python source<br/>as git submodule]
        P4_4[Set up test fixtures<br/>input/ and expected/]
        P4_5[Set up CI<br/>7+ parallel jobs]
        P4_6[Track version correspondence<br/>in package.metadata]
        P4_1 --> P4_2 --> P4_3 --> P4_4 --> P4_5 --> P4_6
    end

    P4 --> P5

    subgraph P5["Phase 5: Port the Code"]
        P5_loop["For each module (leaf → root):"]
        P5_1[Port tests first]
        P5_2[Implement until tests pass]
        P5_3[Add traceability comments]
        P5_4[Run cross-validation]
        P5_5[Update parity tracking spec]
        P5_loop --> P5_1 --> P5_2 --> P5_3 --> P5_4 --> P5_5
        P5_5 -->|Next module| P5_loop
    end

    P5 --> P6

    subgraph P6["Phase 6: Handle Library Differences"]
        P6_1[Cross-validate all fixtures]
        P6_2[Categorize every diff:<br/>porting bug / library diff /<br/>Python bug / improvement]
        P6_3{Diff category?}
        P6_1 --> P6_2 --> P6_3
        P6_3 -->|Porting bug| P6_fix[Fix immediately]
        P6_3 -->|Library diff| P6_workaround[Try: post-process →<br/>pre-process → accept →<br/>vendor → switch lib]
        P6_3 -->|Python bug| P6_decide[Replicate for parity<br/>or fix in Rust?]
        P6_3 -->|Improvement| P6_doc[Document and accept]
        P6_fix --> P6_track
        P6_workaround --> P6_track
        P6_decide --> P6_track
        P6_doc --> P6_track
        P6_track[Track all with<br/>HACK:/FIXME: comments]
    end

    P6_track --> G6{"More than 3 unfixable diffs<br/>or core feature broken?"}
    G6 -->|"No, or past 50%"| P7
    G6 -->|"Yes, early enough"| G6_ret(["⟲ Return to Phase 2:<br/>re-evaluate library choices"])

    subgraph P7["Phase 7: Finalize & Validate"]
        P7_1[Cross-validation gate:<br/>all fixtures pass]
        P7_2[CLI parity check<br/>flags, exit codes, I/O]
        P7_3[All CI jobs passing]
        P7_4[Documentation:<br/>README, CHANGELOG, --version]
        P7_5[Release configuration<br/>release.toml, CI workflow]
        P7_6[Multi-channel distribution<br/>crates.io, PyPI, Homebrew]
        P7_1 --> P7_2 --> P7_3 --> P7_4 --> P7_5 --> P7_6
    end

    P7 --> DONE([Port Complete ✓])
    DONE --> P8

    subgraph P8["Phase 8: Ongoing Synchronization"]
        P8_mode{Release mode?}
        P8_mode -->|"Mode A: Rust-only<br/>stabilization"| P8_A[Internal cleanups,<br/>docs, parity fixes<br/>same Python baseline]
        P8_mode -->|"Mode B: Upstream<br/>sync release"| P8_B1[Update git submodule<br/>to new Python version]
        P8_B1 --> P8_B2[Regenerate expected<br/>test fixtures]
        P8_B2 --> P8_B3[Cross-validate,<br/>categorize changes]
        P8_B3 --> P8_B4[Port changes to Rust]
        P8_B4 --> P8_B5[Update version<br/>correspondence]
        P8_A --> P8_done[Release]
        P8_B5 --> P8_done
        P8_done -->|Next cycle| P8_mode
    end

    style G6_ret fill:#efebe9,stroke:#795548
    style P2 fill:#e8f4f8,stroke:#2196F3
    style P3 fill:#e8f4f8,stroke:#2196F3
    style P4 fill:#e8f4f8,stroke:#2196F3
    style P5 fill:#fff3e0,stroke:#FF9800
    style P6 fill:#fff3e0,stroke:#FF9800
    style P7 fill:#e8f5e9,stroke:#4CAF50
    style P8 fill:#f3e5f5,stroke:#9C27B0
    style G6 fill:#fff9c4,stroke:#FFC107
```

**Phase color key:**
- Tan (Phase 0 / loop-back nodes): Remediation — repeat gate until conditions met
- Blue (Phases 1-4): Planning and preparation — ~25% of effort
- Orange (Phases 5-6): Implementation and fixing — ~65% of effort
- Green (Phase 7): Validation and release — ~10% of effort
- Purple (Phase 8): Ongoing maintenance

**Decision gates** (yellow diamonds) are blocking — you cannot proceed without
satisfying their conditions.

---

## 2. Resource Dependency Map

This diagram groups the 34 documents by function and maps them to lifecycle
stages. Solid arrows show primary usage; dotted arrows show secondary usage
(only some docs in the group apply). For exact per-document phase mappings,
see the inventory table in Section 8.

```mermaid
flowchart LR
    subgraph core["Core References (All Phases)"]
        PB_CORE[["★ python-to-rust-playbook.md<br/>port-checklist-initial-template.md"]]
    end

    subgraph playbooks["Playbooks"]
        PB_TEST[["python-to-rust-test-coverage-playbook.md"]]
        PB_PORT[["python-to-rust-mapping-reference.md<br/>python-to-rust-porting-guide.md<br/>cross-language-test-mapping.md"]]
        PB_INFRA[["rust-cli-best-practices.md<br/>rust-code-review-checklist.md"]]
        PB_SYNC[["python-to-rust-sync-release-workflow.md<br/>auto-sync-agent-prompt-template.md<br/>port-checklist-update-template.md"]]
    end

    subgraph guidelines["Guidelines"]
        G_TEST_DOC[["test-coverage-for-porting.md"]]
        G_SETUP_DOC[["rust-project-setup.md"]]
        G_IMPL[["python-to-rust-porting-rules.md<br/>rust-general-rules.md<br/>rust-cli-app-patterns.md<br/>python-to-rust-cli-porting.md<br/>porting-principles-and-antipatterns.md<br/>filesystem-heavy-cli-porting.md"]]
    end

    subgraph evidence["Research & Case Study"]
        CS_PLAN_EV[["flowmark-port-analysis.md<br/>flowmark-port-decision-log.md<br/>flowmark-port-library-choices.md"]]
        CS_VAL_EV[["flowmark-port-cross-validation.md<br/>flowmark-port-metrics.md"]]
        R_DIST[["research-rust-cli-binary-distribution.md<br/>research-rust-cli-pypi-distribution.md"]]
    end

    PREP["Phases 1-4<br/>Preparation"]
    IMPL_PH["Phases 5-6<br/>Implementation"]
    VAL_PH["Phase 7<br/>Validation"]
    SYNC_PH["Phase 8<br/>Sync"]

    %% Primary connections (solid)
    PB_TEST --> PREP
    G_TEST_DOC --> PREP
    G_SETUP_DOC --> PREP
    CS_PLAN_EV --> PREP

    PB_PORT --> IMPL_PH
    G_IMPL --> IMPL_PH

    PB_INFRA --> VAL_PH
    CS_VAL_EV --> VAL_PH
    R_DIST --> VAL_PH

    PB_SYNC --> SYNC_PH

    %% Secondary connections (dotted)
    PB_INFRA -.-> PREP
    PB_PORT -.-> VAL_PH
    G_IMPL -.-> PREP

    style PB_CORE fill:#e0f2f1,stroke:#00897B
    style PB_TEST fill:#e0f2f1,stroke:#00897B
    style PB_PORT fill:#e0f2f1,stroke:#00897B
    style PB_INFRA fill:#e0f2f1,stroke:#00897B
    style PB_SYNC fill:#e0f2f1,stroke:#00897B
    style G_TEST_DOC fill:#e0f2f1,stroke:#00897B
    style G_SETUP_DOC fill:#e0f2f1,stroke:#00897B
    style G_IMPL fill:#e0f2f1,stroke:#00897B
    style CS_PLAN_EV fill:#e0f2f1,stroke:#00897B
    style CS_VAL_EV fill:#e0f2f1,stroke:#00897B
    style R_DIST fill:#e0f2f1,stroke:#00897B
    style PREP fill:#e8f4f8,stroke:#2196F3
    style IMPL_PH fill:#fff3e0,stroke:#FF9800
    style VAL_PH fill:#e8f5e9,stroke:#4CAF50
    style SYNC_PH fill:#f3e5f5,stroke:#9C27B0
    style core fill:#f5f5f5,stroke:#9E9E9E
    style playbooks fill:#f5f5f5,stroke:#9E9E9E
    style guidelines fill:#f5f5f5,stroke:#9E9E9E
    style evidence fill:#f5f5f5,stroke:#9E9E9E
```

---

## 3. Document Relationship Map

This shows how documents reference each other — the internal link structure
of the playbook itself.

```mermaid
flowchart TD
    README[["<b>README.md</b><br/>Entry point"]] --> MAIN
    README --> CHK_INIT
    README --> CHK_UPD
    README --> AUTO_SYNC
    README --> META

    MAIN[["<b>python-to-rust-playbook.md</b><br/>8-phase process"]]
    MAIN --> TEST_COV
    MAIN --> MAPPING
    MAIN --> CLI_BP
    MAIN --> TEST_MAP
    MAIN --> G_SETUP
    MAIN --> G_CLI
    MAIN --> SYNC_WF
    MAIN --> G_FS

    TEST_COV[["python-to-rust-test-coverage-playbook.md"]]
    MAPPING[["python-to-rust-mapping-reference.md"]]
    GUIDE[["python-to-rust-porting-guide.md"]]

    CLI_BP[["rust-cli-best-practices.md"]]
    CLI_BP --> R_BIN
    CLI_BP --> R_PYPI

    TEST_MAP[["cross-language-test-mapping.md"]]
    REVIEW[["rust-code-review-checklist.md"]]

    CHK_INIT[["port-checklist-initial-template.md"]]
    CHK_INIT --> MAIN
    CHK_INIT --> CS_INDEX

    CHK_UPD[["port-checklist-update-template.md"]]
    CHK_UPD --> SYNC_WF

    SYNC_WF[["python-to-rust-sync-release-workflow.md"]]
    AUTO_SYNC[["auto-sync-agent-prompt-template.md"]]
    AUTO_SYNC --> CHK_UPD
    AUTO_SYNC --> SYNC_WF

    G_SETUP[["rust-project-setup.md"]]
    G_CLI[["python-to-rust-cli-porting.md"]]
    G_PORT[["python-to-rust-porting-rules.md"]]
    G_RUST[["rust-general-rules.md"]]
    G_CLI_PAT[["rust-cli-app-patterns.md"]]
    G_TEST[["test-coverage-for-porting.md"]]
    G_PRINC[["porting-principles-and-antipatterns.md"]]
    G_FS[["filesystem-heavy-cli-porting.md"]]

    R_BIN[["research-rust-cli-binary-distribution.md"]]
    R_PYPI[["research-rust-cli-pypi-distribution.md"]]

    CS_INDEX[["<b>case-studies/flowmark/README.md</b>"]]
    CS_INDEX --> CS_ANALYSIS & CS_METRICS & CS_DECISIONS & CS_LIBS & CS_XVAL & CS_COMRAK & CS_WRAP & CS_PLAN

    CS_ANALYSIS[["flowmark-port-analysis.md"]]
    CS_METRICS[["flowmark-port-metrics.md"]]
    CS_DECISIONS[["flowmark-port-decision-log.md"]]
    CS_LIBS[["flowmark-port-library-choices.md"]]
    CS_XVAL[["flowmark-port-cross-validation.md"]]
    CS_COMRAK[["flowmark-port-comrak-bug.md"]]
    CS_WRAP[["flowmark-port-wrapping-solution.md"]]
    CS_PLAN[["flowmark-port-migration-plan.md"]]

    META[["<b>_meta/</b><br/>Meta-process"]]
    META --> OBS_TPL & TRIAGE_TPL & LOG
    OBS_TPL[["case-study-observations-template.md"]]
    TRIAGE_TPL[["case-study-improvement-triage-template.md"]]
    LOG[["playbook-improvement-log.md"]]

    style README fill:#e0f2f1,stroke:#00897B,stroke-width:3px
    style MAIN fill:#e0f2f1,stroke:#00897B,stroke-width:3px
    style CS_INDEX fill:#e0f2f1,stroke:#00897B,stroke-width:2px
    style META fill:#e0f2f1,stroke:#00897B,stroke-width:2px
```

---

## 4. Meta-Improvement Feedback Loop

The playbook is self-improving: each case study feeds observations back into the
playbook itself.

```mermaid
flowchart TD
    subgraph execute["Execute a Port"]
        SELECT[Select Python project<br/>500+ LOC, 80%+ coverage]
        FOLLOW[Follow 8-phase playbook<br/>end to end]
        OBSERVE[Record observations<br/>using template]
        SELECT --> FOLLOW --> OBSERVE
    end

    subgraph extract["Extract Improvements"]
        TRIAGE[Triage observations:<br/>FIX / ADD / CLARIFY /<br/>GENERALIZE / VALIDATE]
        PRIORITIZE[Prioritize by<br/>impact × severity]
        DRAFT[Draft specific<br/>playbook changes]
        TRIAGE --> PRIORITIZE --> DRAFT
    end

    subgraph integrate["Integrate"]
        REVIEW_HUMAN[Human review of<br/>proposed changes]
        IMPLEMENT[Agent implements<br/>changes to docs]
        VERIFY[Link-check and<br/>validate consistency]
        UPDATE_LOG[Update improvement log]
        REVIEW_HUMAN --> IMPLEMENT --> VERIFY --> UPDATE_LOG
    end

    OBSERVE --> TRIAGE
    DRAFT --> REVIEW_HUMAN
    UPDATE_LOG -->|"Next port uses<br/>improved playbook"| SELECT

    OBS_T[["case-study-observations-template.md"]] -.->|Template for| OBSERVE
    TRI_T[["case-study-improvement-triage-template.md"]] -.->|Template for| TRIAGE
    IMP_LOG[["playbook-improvement-log.md"]] -.->|Append to| UPDATE_LOG

    style execute fill:#e3f2fd,stroke:#1565C0
    style extract fill:#fff3e0,stroke:#E65100
    style integrate fill:#e8f5e9,stroke:#2E7D32
    style OBS_T fill:#e0f2f1,stroke:#00897B
    style TRI_T fill:#e0f2f1,stroke:#00897B
    style IMP_LOG fill:#e0f2f1,stroke:#00897B
```

---

## 5. Effort Distribution

Where time actually goes, based on the flowmark case study.

```
Phase 1: Assess          ██░░░░░░░░░░░░░░░░░░  5%
Phase 2: Research         ████░░░░░░░░░░░░░░░░ 10%
Phase 3: Plan             ██░░░░░░░░░░░░░░░░░░  5%
Phase 4: Set Up           ██░░░░░░░░░░░░░░░░░░  5%
Phase 5: Port             █████████████░░░░░░░░ 33%  ← Tests first, module by module
Phase 6: Library Fixes    ████████████░░░░░░░░░ 32%  ← Often single largest phase
Phase 7: Finalize         ████░░░░░░░░░░░░░░░░░ 10%

Preparation (1-4):  25%  ─┐
Implementation (5-6): 65%  ├─ Key insight: most effort is in
Validation (7):     10%  ─┘   implementation + library workarounds
```

---

## 6. Entry Points and Reading Order

Different users need different starting points. Here's a decision tree.

```mermaid
flowchart TD
    WHO{What are you doing?}

    WHO -->|"Starting a new<br/>Python→Rust port"| NEW
    WHO -->|"Syncing an existing<br/>port to new upstream"| SYNC
    WHO -->|"Setting up an AI agent<br/>for porting"| AGENT
    WHO -->|"Reviewing Rust<br/>port quality"| QA
    WHO -->|"Improving the<br/>playbook itself"| META_DOCS

    NEW[["<b>1.</b> README.md<br/><b>2.</b> python-to-rust-playbook.md<br/><b>3.</b> port-checklist-initial-template.md<br/><b>4.</b> case-studies/flowmark/"]]

    SYNC[["<b>1.</b> auto-sync-agent-prompt-template.md<br/><b>2.</b> port-checklist-update-template.md<br/><b>3.</b> python-to-rust-sync-release-workflow.md"]]

    AGENT[["<b>1.</b> python-to-rust-porting-rules.md<br/><b>2.</b> rust-project-setup.md<br/><b>3.</b> rust-general-rules.md<br/><b>4.</b> python-to-rust-cli-porting.md<br/><b>5.</b> porting-principles-and-antipatterns.md"]]

    QA[["<b>1.</b> rust-code-review-checklist.md<br/><b>2.</b> cross-language-test-mapping.md<br/><b>3.</b> flowmark-port-cross-validation.md"]]

    META_DOCS[["<b>1.</b> _meta/meta-improving-this-playbook.md<br/><b>2.</b> case-study-observations-template.md<br/><b>3.</b> playbook-improvement-log.md"]]

    style WHO fill:#fff9c4,stroke:#F9A825,stroke-width:2px
    style NEW fill:#e0f2f1,stroke:#00897B
    style SYNC fill:#e0f2f1,stroke:#00897B
    style AGENT fill:#e0f2f1,stroke:#00897B
    style QA fill:#e0f2f1,stroke:#00897B
    style META_DOCS fill:#e0f2f1,stroke:#00897B
```

---

## 7. Two-Mode Release Cycle (Phase 8 Detail)

Mature ports alternate between two release modes. This prevents coupling
Rust improvements with upstream sync risk.

```mermaid
flowchart TD
    TRIGGER{Trigger?}

    TRIGGER -->|"Rust improvements<br/>ready to ship"| MODE_A
    TRIGGER -->|"New Python<br/>version released"| MODE_B

    subgraph MODE_A["Mode A: Rust-Only Stabilization"]
        A1[Internal cleanups, docs,<br/>build/release hardening]
        A2[Parity fixes that don't<br/>change Python baseline]
        A3[Same python_source.version<br/>in Cargo.toml]
        A4[Release Rust version bump]
        A1 --> A2 --> A3 --> A4
    end

    subgraph MODE_B["Mode B: Upstream Sync Release"]
        B1["Update submodule to<br/>new Python version"]
        B2["Regenerate test fixtures"]
        B3["Cross-validate, categorize<br/>bug fix / feature / refactor"]
        B4["Port each change to Rust"]
        B5["Update python_source.version"]
        B6["Release with new baseline"]
        B1 --> B2 --> B3 --> B4 --> B5 --> B6
    end

    A4 -->|"Next cycle"| TRIGGER
    B6 -->|"Next cycle"| TRIGGER

    style MODE_A fill:#e8f5e9,stroke:#2E7D32
    style MODE_B fill:#e3f2fd,stroke:#1565C0
    style TRIGGER fill:#fff9c4,stroke:#F9A825
```

---

## 8. Complete Document Inventory

| # | Document | Layer | Primary phases | Purpose |
|---|----------|-------|----------------|---------|
| 1 | `python-to-rust-playbook.md` | Playbook | All | Canonical 8-phase process |
| 2 | `python-to-rust-mapping-reference.md` | Playbook | 2, 5 | Type and API mappings |
| 3 | `python-to-rust-porting-guide.md` | Playbook | 5, 6 | Deep methodology and pitfalls |
| 4 | `rust-cli-best-practices.md` | Playbook | 4, 7 | CI, linting, releases, distribution |
| 5 | `rust-code-review-checklist.md` | Playbook | 7 | 150+ quality checks |
| 6 | `cross-language-test-mapping.md` | Playbook | 5, 6, 7 | YAML test traceability + CI gates |
| 7 | `python-to-rust-test-coverage-playbook.md` | Playbook | 1 (Phase 0) | Pre-port test enhancement |
| 8 | `port-checklist-initial-template.md` | Playbook | 1-7 | Copy-and-fill execution checklist |
| 9 | `port-checklist-update-template.md` | Playbook | 8 | Sync execution checklist |
| 10 | `python-to-rust-sync-release-workflow.md` | Playbook | 8 | Mode A / Mode B release patterns |
| 11 | `auto-sync-agent-prompt-template.md` | Playbook | 8 | Copy-paste prompt for sync agent |
| 12 | `python-to-rust-porting-rules.md` | Guideline | 5 | Core rules for agent context |
| 13 | `python-to-rust-cli-porting.md` | Guideline | 5, 7 | CLI-specific porting patterns |
| 14 | `rust-general-rules.md` | Guideline | 5 | Edition 2024+ best practices |
| 15 | `rust-cli-app-patterns.md` | Guideline | 5 | CLI patterns (clap, errors, testing) |
| 16 | `rust-project-setup.md` | Guideline | 4 | Cargo.toml, CI, release automation |
| 17 | `test-coverage-for-porting.md` | Guideline | 1 | Test strategy for agent context |
| 18 | `porting-principles-and-antipatterns.md` | Guideline | 5, 6 | 8 non-negotiable principles |
| 19 | `filesystem-heavy-cli-porting.md` | Guideline | 2, 5 | Path, symlink, encoding patterns |
| 20 | `research-rust-cli-binary-distribution.md` | Research | 7 | Survey of 14 Rust CLI tools |
| 21 | `research-rust-cli-pypi-distribution.md` | Research | 7 | maturin / PyPI distribution |
| 22-29 | `case-studies/flowmark/*` | Case Study | 2, 3, 6, 7 | Real-world port evidence |
| 30-34 | `_meta/*` | Meta | — | Self-improvement framework |
