# Anu Framework v12.2 — Complete Architecture Overview

**Version**: 12.2
**Date**: June 10, 2026
**Location**: `Council/Druck/docs/ANU_FRAMEWORK_OVERVIEW.md`

> **Changelog 2026-06-10 (v12.2).** Framework v12.1 → v12.2 — the **web-readiness release** (triggered by the Heterodata platform overhaul). (1) **Series ID Spec v2.2** (anu-ingestion v5.2): canonical prefixes now `{D: primary, XS: extra}`; legacy `AS`/`ES`/`AD` rejected by anu-doctor P12; XS entries carry `xs_class` (`appendix` | `external_study`) + `xs_attribution`, which drive website sectioning (XS sections render after all primary series, split appendix vs other-study). New mandatory registry fields: `display_name`, `publish`, `triage`; per-subseries `label`+`units`, `mixed_*` units banned. (2) **anu-publish v2.1**: P10/P11 scrub gates promoted WARN→FAIL (workspace paths had shipped to the public web); new `web` packaging profile — the formal Anu→website export contract (publish-filtered registry + chopped CSV + parquet + generated `data_dictionary.csv` + explainers + scrubbed DPRs + `WEB_MANIFEST.json`; downloads contract CSV+parquet only); new gates P13 (dictionary), P14 (units), P15 (no unpublished series). (3) **anu-docs v3.0**: the **Anu Explainer** — web-facing per-series artifact with fixed five-section template and hard Web-Format Rules (no file paths, no wide tables, KB-anchored quotes); DPR repositioned as downloadable full-provenance "agent context"; DOC11/DOC12 gates. (4) New canonical standards under `docs/standards/`: SITE_SPEC_PROTOCOL, SITE_BUILD_ORCHESTRATION, STUDY_PAGE_STANDARD, ANU_NAMING_STANDARD, EDUCATIONAL_DISCLAIMER_STANDARD, UNITS_VALIDATION_STANDARD, PANEL_CONSTRUCTION_RUBRIC. (5) Canonical **"Two namespaces"** section added below — series-ID prefixes vs pipeline-stage prefixes are different vocabularies; site explainers must copy from it.
>
> **Changelog 2026-05-24 (v12.1).** Framework v12.0 → v12.1. Decision-doc folder reactivated for *new* canonical decisions (the 0001–0006 set remains archived/integrated into specs). Two new decisions added: **Decision 0007** — canonical verbatim-quote schema for research JSONs (records inside `entries[]` with `entry_type == "verbatim_quote"`; top-level `verbatim_quotes[]` and inline-legacy fields deprecated) — migrated across all 64 RMWND research JSONs in v1.1 Phase 1; and **Decision 0008** — `validation.reference_values` is year-keyed scalars only, non-year statistics split into a new companion field `validation.derived_statistics` (registry schema v2.3.0+). New framework-level capabilities promoted from RMWND v1.1 + v1.2: `anu-doctor` standard scripts now ship at `Council/Druck/anu/check_framework.py` and `check_project.py` as canonical wrappers (no longer per-project authoring); `extension_year_range` field convention codified (per RMWND P29 fix — separate from `year_range` so book-period min/max stays stable when extension data is added); `artifacts.derived_no_l01` exemption flag for derived series that legitimately have no L01 loader (per RMWND P23 fix); stock-form primary support for rate-of-profit series (`DIV-012` pattern — `construction: "stock_form"` allowed where the source measured a stock rather than a flow). check_framework continues to PASS on 21 active skill folders (19 + 2 redirect stubs). No skill-version bumps required — v12.1 is a spec/decisions-layer release.
>
> **Changelog 2026-05-16 (v12.0).** Framework v11.0 → v12.0. Major consolidation: `anu-rebuild` + `anu-pipeline` merged into **anu-build** — a single master orchestrator with 9 stages (0 INVENTORY through 8 DISTRIBUTION), computed construction order via topological sort, mandatory acceptance gates, and a 4-file documentation cascade (STEP_LOG.jsonl, BUILD_NARRATIVE.md, ANU_BUILD_MANIFEST.json, SUBSERIES_PLAN.json). All 18 active SKILL.md files rewritten to a common 11-section template enforced by new anu-doctor D16 check. Two archived skill folders (`anu-shiny-archived-20260509`, `anu-standard-v2-removed-20260509`) deleted. anu-doctor extended with D16–D19 (framework) and P15–P20 (project) checks. New canonical docs: `ANU_BUILD_PROTOCOL.md`, `SKILL_DEPENDENCY_GRAPH.md`, `ANU_AUDIT_REPORT_20260516.md`, plus 5 JSON schemas. LEDGER and PIPELINE_STATE schemas extended to v12.0. Skill count: 20 → 19 (net: −anu-rebuild −anu-pipeline +anu-build = −1). All 18 active stage/floating/infrastructure skills version-bumped. Deprecated skills retained as redirect stubs.
>
> **Changelog 2026-05-15 (v11.0).** Framework v10.0 → v11.0. Two new skills: anu-scaffold and anu-rebuild. Ten existing skills version-bumped. `anu-data` renamed to `anu-architecture`.
>
> **Changelog 2026-05-14 (v10.0).** Integration sweep: anu-pipeline v3.1, anu-review v4.1, new SKILL_VERSION_MATRIX.md.

---

## What is the Anu Framework?

The Anu Framework is a **19-active-skill framework (plus 2 deprecated redirect stubs = 21 skill folders) for agent-driven data construction, empirical research, and reproducible publication** that produces outputs reproducible without agents. It covers the full lifecycle from research through distribution, orchestrated by `anu-build` — a master skill that drives every other skill through a methodical 9-stage pipeline with computed construction order, mandatory gates, and a documentation cascade that enables reliable multi-agent handoffs.

---

## 19 Active Skills

| # | Skill | Version | Stage | Location | Purpose |
|---|-------|---------|-------|----------|---------|
| 1 | **Anu Research** | v3.0 | Stage 1 | `anu-research/SKILL.md` | Mine KB for quotes, references, methodology per series |
| 2 | **Anu Adequacy** | v2.0 | Stage 2 (gate) | `anu-adequacy/SKILL.md` | Post-research statistical readiness gate |
| 3 | **Anu Ingestion** | v5.2 | Stage 3 | `anu-ingestion/SKILL.md` | Registry, DPRs, FPRs, decompositions, status taxonomy, Series ID Spec v2.2 (D/XS) |
| 4 | **Anu Extension** | v4.0 | Stage 4 | `anu-extension/SKILL.md` | Extension methodology, EPRs, divergence register |
| 5 | **Anu Scaffold** | v2.1 | Stage 5 (sub) | `anu-scaffold/SKILL.md` | Generate L01/P02/V03 stubs from registry entries |
| 6 | **Anu Replicator** | v4.0 | Stage 5 | `anu-replicator/SKILL.md` | L01/P02/V03 reproduction package |
| 7 | **Anu Chopped** | v3.0 | Stage 6a | `anu-chopped/SKILL.md` | Machine-readable CSV format |
| 8 | **Anu Extenbook** | v4.0 | Stage 6b | `anu-extenbook/SKILL.md` | Human-readable 4-sheet Excel workbooks |
| 9 | **Anu Visualize** | v6.1 | Stage 7 | `anu-visualize/SKILL.md` | Interactive visualization (Plotly Dash / R Shiny) |
| 10 | **Anu Publish** | v2.1 | Stage 8a | `anu-publish/SKILL.md` | GitHub replication channel + `web` export contract (P01–P15 gate) |
| 11 | **Anu Drive** | v2.0 | Stage 8b | `anu-drive/SKILL.md` | Google Drive consumer channel |
| 12 | **Anu Archive** | v2.0 | Stage 8c | `anu-archive/SKILL.md` | Audit-grade transparency channel |
| 13 | **Anu Review** | v5.0 | Floating | `anu-review/SKILL.md` | Quality audit (14 dimensions + D13/D14 gates) |
| 14 | **Anu Docs** | v3.0 | Floating | `anu-docs/SKILL.md` | Per-series documentation (T1/T2/T3 tiers) + the Anu Explainer (web-facing) |
| 15 | **Anu Variant** | v2.0 | Floating | `anu-variant/SKILL.md` | Methodology variant tracking (VPRs) |
| 16 | **Anu Ledger** | v3.0 | Infrastructure | `anu-ledger/SKILL.md` | Artifact inventory + per-series stage tracking |
| 17 | **Anu Architecture** | v3.0 | Infrastructure | `anu-architecture/SKILL.md` | Format standard (BEA/BLS/FRED cache schemas) |
| 18 | **Anu Doctor** | v2.3 | Infrastructure | `anu-doctor/SKILL.md` | Framework (D01–D15) + project (P01–P36) self-audit |
| 19 | **Anu Build** | v1.3 | Orchestrator | `anu-build/SKILL.md` | **NEW** — Master orchestrator: 9-stage pipeline + cascade |

All skills are located under `Council/Druck/.claude/skills/`. The authoritative per-skill version matrix is [`SKILL_VERSION_MATRIX.md`](SKILL_VERSION_MATRIX.md). `anu-doctor` enforces that the matrix, this table, and every skill's frontmatter stay in agreement.

**Code is source of truth.** When framework executable code (`check_project.py`, `check_framework.py`, SKILL.md frontmatter `version:` fields, the schema validator) diverges from human-readable documentation, the code wins — docs get updated to match. anu-doctor's D-checks are the mechanical enforcement layer. There is no separate decision-log channel: decisions land directly in the canonical spec (`SERIES_REGISTRY_SCHEMA.md`, the affected `SKILL.md`, the framework rules file) with rationale in commit messages.

### Deprecated skills (redirect stubs)

| Skill | Former Version | Redirect |
|-------|---------------|----------|
| anu-rebuild | v1.1 | → `anu-build` (mode=rebuild) |
| anu-pipeline | v3.2 | → `anu-build` |

### Retired skill folders (deleted in v12.0)

- `anu-shiny-archived-20260509` — superseded by anu-visualize v5.0
- `anu-standard-v2-removed-20260509` — superseded by anu-ingestion v4.0

---

## Architecture

### Data Flow

```
                    Anu Architecture (format standard)
                    ==================================

KB/HDARP Extractions
        |
        v
  Stage 0: [Anu Build]        -->  ANU_BUILD_MANIFEST.json, SUBSERIES_PLAN.json
        |
        v
  Stage 1: [Anu Research]     -->  S###_research.json
        |
        v
  Stage 2: [Anu Adequacy]     -->  ADEQUACY_REPORT.json [GATE: score >= 80]
        |
        v
  Stage 3: [Anu Ingestion]    -->  series_registry.json, DPRs, Decompositions
        |
        v
  Stage 4: [Anu Extension]    -->  Extension methodology, EPRs
        |
        v
  Stage 5: [Anu Scaffold]     -->  L01/P02/V03 stubs
           [Anu Replicator]   -->  L01/P02/V03 package, VALIDATION_REPORT.json
        |
        +---> Stage 6a: [Anu Chopped]    -->  Validated CSVs
        +---> Stage 6b: [Anu Extenbook]  -->  4-sheet Excel workbooks
        |
        v
  Stage 7: [Anu Visualize]    -->  Interactive app + figure exports
        |
        v
  Stage 8a: [Anu Publish]     -->  GitHub replication repo
  Stage 8b: [Anu Drive]       -->  Google Drive consumer package
  Stage 8c: [Anu Archive]     -->  Audit-grade transparency package

  FLOATING:  [Anu Review]     -->  Quality audit at ANY stage
  FLOATING:  [Anu Docs]       -->  Per-series documentation (T1/T2/T3 tiers)
  FLOATING:  [Anu Variant]    -->  Methodology variant tracking

  INFRASTRUCTURE:
  [Anu Ledger]    -->  Artifact inventory (auto-regenerated after every step)
  [Anu Doctor]    -->  Framework + project consistency audit
  [Anu Build]     -->  Orchestrates all of the above via 4-file cascade
```

### Documentation Cascade (NEW in v12.0)

Every anu-build step produces exactly three writes:
1. **STEP_LOG.jsonl** — append-only event stream (one JSON line per action)
2. **ANU_LEDGER.json** — per-series artifact state (regenerated)
3. **BUILD_NARRATIVE.md** — chronological human/LLM-readable narrative (appended)

Plus at stage boundaries:
4. **PIPELINE_STATE.json** — top-level orchestration state (updated)

See [`ANU_BUILD_PROTOCOL.md`](ANU_BUILD_PROTOCOL.md) for the full multi-agent handoff specification.

### Data Integrity Constraints (MANDATORY)

**No Synthetic Data**: No skill may generate synthetic, estimated, or placeholder data. Every value must trace to a published source or documented analytical method. If data is unavailable, status is `data_unavailable` and the output is empty.

**No Proxies**: Extensions must use the EXACT same data source the original author used. Substitutions require a Concept Match Justification and `"proxy": true` flag.

**No Lazy Splices on Formulas**: If the original computed a formula, the extension must compute the same formula with extended components. Growth-rate splice is only valid for directly-observed time series.

**Content Type Classification**: Every series must be classified as `time_series`, `cross_sectional`, `theoretical`, or `derived`. Extensions only apply to `time_series`.

### Single Source of Truth: series_registry.json

Every output format reads from `series_registry.json`. See [`SERIES_REGISTRY_SCHEMA.md`](SERIES_REGISTRY_SCHEMA.md) for the schema specification.

### Two Namespaces (CANONICAL — site explainers copy from here)

The framework uses two **unrelated** letter-prefix vocabularies. Conflating them produces wrong public copy (it happened on live sites — a series-ID first letter was presented as a pipeline stage).

**1. Series-ID prefixes** identify *what a data series is* (Series ID Spec v2.2, anu-ingestion):

| Prefix | Meaning |
|---|---|
| `D` (project alias: `S`) | Primary series — from the book or study being replicated |
| `XS` | Extra series — book-appendix series (`xs_class: appendix`) or series from another study (`xs_class: external_study`) |

**2. Pipeline-script phase prefixes** identify *what a script does* (anu-architecture):

| Prefix | Meaning |
|---|---|
| `S##` | Setup |
| `L##` | Loading — fetch/read raw source data |
| `P##` | **Processing — and processing only** (construction, transformation) |
| `V##` | Validation — check outputs against benchmarks |
| `M##` | Manual adjustment (documented) |
| `A##` | Analysis |
| `O##` | Output |
| `E##` | Exploration |

A series ID's first letter says **nothing** about pipeline stages, and a script prefix says nothing about series classification. Public-facing "how this was built" copy must describe the pipeline using the script-phase table (counts derived from the replicator script inventory), and describe the catalog using the series-ID table — never by counting series IDs' first letters.

---

## Robin Integration (across all stages)

**Robin** (`Council/Robin/`) is Arcanum's canonical economic data repository. The Anu Framework consumes Robin as its primary external data source. Integration touches every stage:

| Stage | How it touches Robin |
|---|---|
| **Stage 1 — anu-research** | Research JSONs cite Robin sources by `robin_source_id` (matches `AUTHORITATIVE_COUNTS.json` keys). |
| **Stage 2 — anu-adequacy** | +1 score if cited source is in Robin and live; -1 if cited but absent from Robin and OPEN_APIS. |
| **Stage 2.5 — Data Acquisition from Robin** | Project creates `Inputs/Robin/[SOURCE]/` checkouts per `INPUTS_ROBIN_CONTRACT.md`. PROVENANCE.md records `robin_source_id`, version, file hashes. |
| **Stage 3 — anu-ingestion** | L## loaders import `lib/data/robin_loader.py`. Never read `Council/Robin/DATA/` directly. |
| **Stage 4 — anu-extension** | EPRs record Robin source + snapshot timestamp. Extension refreshes the checkout when Robin's canonical updates. |
| **Stage 5 — anu-replicator** | `lib/data/robin_loader.py` is the canonical helper. Hash-stamps every load against Robin version. |
| **Stage 6 — anu-chopped / anu-extenbook** | Output formats record `robin_source_id` in subsource metadata. |
| **Stage 7 — anu-review** | D13 Data Authenticity gate checks: every Robin-sourced series has valid PROVENANCE + non-drifting hashes. |
| **Stage 8 — anu-publish / anu-archive** | Published manifests include the `robin_version` pinned at construction time. |

**Canonical references**:
- `Council/Robin/AUTHORITATIVE_COUNTS.json` — the only valid count source
- `Council/Robin/docs/specs/INPUTS_ROBIN_CONTRACT.md` — checkout contract (PROVENANCE fields)
- `Council/Druck/docs/ROBIN_INTEGRATION_SPECIFICATION.md` — cross-workspace governance

**Anti-patterns** (anu-doctor flags):
- Project ingests data via custom API clients that duplicate Robin collectors
- Hardcoded paths into `Council/Robin/DATA/`
- Reading through another project's checkout instead of maintaining own
- Citing hand-curated record counts ("64.9M") instead of pointing at `AUTHORITATIVE_COUNTS.json`

---

## How to Build a New Project

```
/anu-build init --project <path> --mode fresh
/anu-build run-to-completion
```

Or step by step:
1. `/anu-build init --mode fresh` — Stage 0: generate manifest + construction plan
2. `/anu-build run-stage 1` — Research
3. `/anu-build run-stage 2` — Adequacy gate
4. `/anu-build run-stage 3` — Ingestion
5. `/anu-build run-stage 4` — Extension
6. `/anu-build run-stage 5` — Replication (L01/P02/V03 in topo order)
7. `/anu-build run-stage 6` — Output (chopped + extenbooks)
8. `/anu-build run-stage 7` — Visualization
9. `/anu-build run-stage 8` — Distribution (publish + drive + archive)

Run `/anu-build status` at any point to see progress. Run `/anu-build handoff` to close a session.

---

## Reference Implementations

- **CD2** (`Projects/CD2/`) — replication of Anwar Shaikh's *Capitalism: Competition, Conflict, Crises* (2016). Most complete project; exercises all skills. The v11.0 reference.
- **RMWND** (`Projects/RMWND/`) — replication of Shaikh & Tonak's *Measuring the Wealth of Nations* (1994). 64 series, first project built end-to-end on anu-build v12.0.

---

## Paper Target Ledger (Replication Contract Phase)

**Added 2026-05-27 by Study 12 Correia Definitive Wave 8 Agent 8D (additive).**

Empirical-paper replication projects under the Anu Framework — where Python
output must agree with a published paper's tables/figures and/or a canonical
Stata log — should adopt the **Paper Target Ledger Protocol**
([`protocols/PAPER_TARGET_LEDGER_PROTOCOL.md`](protocols/PAPER_TARGET_LEDGER_PROTOCOL.md))
during the contract-gate / W2.5-equivalent phase (roughly Stage 3 ingestion +
Stage 5 replicator, between data load and headline comparison).

The protocol codifies five documented "target is the bug" failure modes from
Study 12 (W4.6, W7.0, W7.1, W8A, W8B):

1. **Hand-typed transcription error** (W4.6 sign-flipped targets)
2. **Wrong Stata log block** (W7.0 rolling-window vs full-sample IRLS)
3. **Wrong paper table row** (W7.1 Baseline vs Richer Model)
4. **Misread-prior-conclusion** (W8A handoff inverted a FIX doc's verdict)
5. **Bar-chart visual-read** (W8B Figure IX bar-heights treated as precise)

Operational rule: **first 10 minutes on the target, not the code.** When Python
selectively disagrees with a target while other metrics match, the first
hypothesis is that the target is wrong. Reference implementation:
`Projects/Volcker/Technical/AnuData/studies/study_12_correia_definitive/code/lib/target_ledger.py`
(study-local; promotion to a shared framework module pending Druck approval).

Adoption is opt-in until the next framework-level review. Projects in the
"protocol does not apply" category (no canonical Stata source; first-of-its-kind
extraction with no published table; pipeline contract-gates) remain valid.

---

## Canonical References

- [`SKILL_VERSION_MATRIX.md`](SKILL_VERSION_MATRIX.md) — per-skill version table
- [`ANU_FRAMEWORK_GLOSSARY.md`](ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary
- [`SERIES_REGISTRY_SCHEMA.md`](SERIES_REGISTRY_SCHEMA.md) — registry schema
- [`SKILL_DEPENDENCY_GRAPH.md`](SKILL_DEPENDENCY_GRAPH.md) — skill dependency DAG
- [`ANU_BUILD_PROTOCOL.md`](ANU_BUILD_PROTOCOL.md) — multi-agent handoff protocol
- [`DATA_PROVENANCE_STANDARDS.md`](DATA_PROVENANCE_STANDARDS.md) — provenance chain spec
- [`protocols/PAPER_TARGET_LEDGER_PROTOCOL.md`](protocols/PAPER_TARGET_LEDGER_PROTOCOL.md) — paper-target ledger discipline for replication projects

---

*Anu Framework v12.1 — Data Construction, Empirical Research, and Reproducible Publication*
*Location: Council/Druck/docs/ANU_FRAMEWORK_OVERVIEW.md*
