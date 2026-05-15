# Anu Framework v11.0 — Complete Architecture Overview

**Version**: 11.0
**Date**: May 15, 2026
**Location**: `docs/ANU_FRAMEWORK_OVERVIEW.md`

> **Changelog 2026-05-15 (Session 34).** Framework v10.0 → v11.0. The 21-commit Shaikh-Tonak (RMWND) rebuild surfaced 12 friction points (codified in [`ANU_FRAMEWORK_IMPROVEMENTS_RFC.md`](ANU_FRAMEWORK_IMPROVEMENTS_RFC.md)) plus a meta-workflow ([`ANU_REBUILD_META_SKILL.md`](ANU_REBUILD_META_SKILL.md)). v11.0 adds two new skills — **anu-scaffold** (generates L01/P02/V03 stubs from registry entries; eliminates ad-hoc generators) and **anu-rebuild** (6-wave salvage-and-port meta-workflow). Ten existing skills version-bumped, and `anu-data` (AnuData Architecture) was renamed to `anu-architecture` (Anu Architecture) for framework-name consistency: anu-research (2.0→2.1, +port), anu-ingestion (4.0→4.1, +migrate-scheme/batch-create-dpr/status-enum), anu-extension (3.4→3.5, +batch-create-epr/central-DIVERGENCE_REGISTER), anu-replicator (3.0→3.1, +lib/ layout), anu-architecture (2.0→2.1 + renamed, +BEA/BLS/FRED cache schemas), anu-pipeline (3.1→3.2, +run.py template), anu-publish (1.1→1.2, +audit.py), anu-doctor (1.0→1.1, +check_project.py with 10 P##-checks). Shared infrastructure: new `_shared/divergences.py` for cross-skill DIVERGENCE_REGISTER writes.
>
> **Changelog 2026-05-14 (Session 32).** Framework integration sweep: `anu-pipeline` v3.0 → v3.1 (Stage 8 split into sibling channels 8a Publish / 8b Drive / 8c Archive; `anu-docs` added as a floating skill; 14 → 17 skills); `anu-review` v4.0 → v4.1 (D14 Outward-Facing Intelligibility formalized as a gate; D1–D12 weighted, D13/D14 gates). New [`SKILL_VERSION_MATRIX.md`](SKILL_VERSION_MATRIX.md) as the authoritative per-skill version table; the skill table above corrected to match actual `SKILL.md` frontmatter.
>
> **Changelog 2026-05-14 (Session 30-31).** New skill **#17 Anu Archive** (`anu-archive/SKILL.md` + `generate_archive_package.py`) — the audit-grade transparency distribution channel, sibling to Anu Publish (GitHub) and Anu Drive (Google Drive). **Anu Drive** gains an executable generator (`generate_drive_package.py`, v1.0 → v1.1). The three external distribution channels are now formally defined as siblings.
>
> **Changelog 2026-05-13.** All skill `SKILL.md` headers unified to `part-of: Anu Framework v10.0` (previously a mix of v8.0 and v9.0). New canonical reference documents added: [`ANU_FRAMEWORK_GLOSSARY.md`](ANU_FRAMEWORK_GLOSSARY.md), [`SERIES_REGISTRY_SCHEMA.md`](SERIES_REGISTRY_SCHEMA.md) (with sibling [`schemas/series_registry.schema.json`](../schemas/series_registry.schema.json)), [`DATA_PROVENANCE_STANDARDS.md`](DATA_PROVENANCE_STANDARDS.md). `anu-extension` SKILL.md tightened to enumerate concrete artifacts (v3.3 → v3.4). New review dimension D14 (Outward-Facing Intelligibility) introduced in the CD2 session-28 review and folded into future `anu-review` runs.

---

## What is the Anu Framework?

The Anu Framework is a **20-skill framework for agent-driven data construction, empirical research, and reproducible publication** that produces outputs reproducible without agents. It covers the full lifecycle: researching source materials, ingesting and structuring data, extending series with modern APIs, producing machine-readable and human-readable outputs, building standalone replication packages, visualizing results interactively, auditing quality, tracking data provenance, orchestrating multi-agent workflows, conducting original econometric research via the Anu Architecture, distributing consumer-facing data packages, scaffolding code from registry entries, and rebuilding predecessor projects into Anu-Framework-native form.

---

## 20 Skills

| # | Skill | Version | Location | Purpose |
|---|-------|---------|----------|---------|
| 1 | **Anu Research** | v2.1 | `anu-research/SKILL.md` | Mine every quote, reference, and methodology note for each series; v2.1 adds `port` sub-command for predecessor JSONs |
| 2 | **Anu Ingestion** | v4.1 | `anu-ingestion/SKILL.md` | KB construction, import, absorption, decomposition, provenance; v4.1 adds migrate-scheme, batch-create-dpr, status-taxonomy enum |
| 3 | **Anu Extension** | v3.5 | `anu-extension/SKILL.md` | Faithful data extension methodology with API data; v3.5 adds batch-create-epr + central DIVERGENCE_REGISTER integration |
| 4 | **Anu Chopped** | v2.0 | `anu-chopped/SKILL.md` | Machine-readable CSV format (Row 1 metadata, Row 2 IDs, Row 3+ data) |
| 5 | **Anu Extenbook** | v3.2 | `anu-extenbook/SKILL.md` | Human-readable Excel with 4 sheets (Data, Provenance, Research, Construction) |
| 6 | **Anu Replicator** | v3.1 | `anu-replicator/SKILL.md` | Self-contained L##/P##/V##/M## reproduction package; v3.1 prescribes `lib/` shared-helpers layout |
| 7 | **Anu Visualize** | v5.0 | `anu-visualize/SKILL.md` | Interactive visualization (R Shiny + Plotly / Plotly Dash) |
| 8 | **Anu Review** | v4.1 | `anu-review/SKILL.md` | 12 weighted dimensions + 2 gates (D13 Authenticity, D14 Outward-Facing Intelligibility) |
| 9 | **Anu Pipeline** | v3.2 | `anu-pipeline/SKILL.md` | Master orchestrator — sequences all 19 other skills through 8 stages; v3.2 ships `templates/run.py.j2` |
| 10 | **Anu Variant** | v1.4 | `anu-variant/SKILL.md` | Methodology variant tracking with canonical IDs (VPRs) |
| 11 | **Anu Ledger** | v2.2 | `anu-ledger/SKILL.md` | Artifact inventory and coverage tracking |
| 12 | **Anu Adequacy** | v1.2 | `anu-adequacy/SKILL.md` | Post-research statistical adequacy gate |
| 13 | **Anu Architecture** | v2.1 | `anu-architecture/SKILL.md` | Anu Architecture (formerly AnuData Architecture); v2.1 documents BEA/BLS/FRED cache schemas (DataValue, UNIT_MULT, observation-list) |
| 14 | **Anu Publish** | v1.2 | `anu-publish/SKILL.md` | Stage 8a — GitHub replication channel; v1.2 ships `audit.py` (pre-publication scrub) |
| 15 | **Anu Drive** | v1.1 | `anu-drive/SKILL.md` | Stage 8b — Google Drive consumer channel: master data file, codebook, methodology PDF |
| 16 | **Anu Docs** | v1.0 | `anu-docs/SKILL.md` | Per-series documentation: 3-tier quality system (Thin/Adequate/Enriched), scoring rubric, enrichment workflow |
| 17 | **Anu Archive** | v1.0 | `anu-archive/SKILL.md` | Stage 8c — audit-grade transparency channel: provenance trail + manifest + checksums |
| 18 | **Anu Doctor** | v1.2 | `anu-doctor/SKILL.md` | Framework + project self-audit; v1.1 ships `check_project.py` (10 P##-checks); v1.2 adds D13/D14/D15 consistency checks |
| 19 | **Anu Scaffold** | v1.0 | `anu-scaffold/SKILL.md` | NEW — generates L01/P02/V03 stubs from registry entries; eliminates ad-hoc generator scripts |
| 20 | **Anu Rebuild** | v1.0 | `anu-rebuild/SKILL.md` | NEW — 6-wave salvage-and-port meta-workflow for predecessor projects |

All skills are located under `skills/`. The authoritative per-skill version, stage, and `requires:` matrix is [`SKILL_VERSION_MATRIX.md`](SKILL_VERSION_MATRIX.md). `anu-doctor` enforces that the matrix, this table, and every skill's frontmatter stay in agreement.

### The three external distribution channels

Skills 14, 15, and 17 are siblings — they consume the same upstream outputs and serve three distinct audiences:

- **Anu Publish (GitHub)** — researchers who `git clone` and run the pipeline. Lean: code + data + minimal docs + CI.
- **Anu Drive (Google Drive)** — scholars who open files and never run code. Friendly: master workbook + codebook + methodology PDF + per-series workbooks.
- **Anu Archive (comprehensive)** — peer reviewers, journal data editors, future-proof archival. Everything: code + data + full provenance trail + validation + decisions + reviews + ledger + glossary, with a machine-readable manifest and SHA-256 checksums.

---

## Reference implementation

**CD2** (`Projects/CD2/`) — the replication and extension of every empirical data series in Anwar Shaikh's *Capitalism: Competition, Conflict, Crises* (2016) — is the framework's reference implementation. It is the most complete Anu Framework project: it exercises all 18 skills, ships all three external distribution channels (GitHub repo, Drive package, comprehensive Archive), and was the project that drove the framework to v10.0. New Anu Framework projects should use CD2 as the known-good example to copy — its `Technical/` layout, its `series_registry.json` shape, its per-series DPR/EPR/decomposition docs, and its `anu-review` history are all canonical patterns.

---

## Architecture

### Data Flow

```
                    Anu Architecture (format standard)
                    ==================================

KB/HDARP Extractions
        |
        v
  Stage 1: [Anu Research]    -->  S###_research.json
        |
        v
  Stage 2: [Anu Adequacy]   -->  ADEQUACY_REPORT.json [GATE]
        |
        v
  Stage 3: [Anu Ingestion]  -->  series_registry.json, DPRs, Decompositions
        |
        v
  Stage 4: [Anu Extension]  -->  Extension methodology, EPRs
        |
        v
  Stage 5: [Anu Replicator] -->  L##/P##/V##/M## package
    Loading (L##)  -->  data/raw-data/
    Processing (P##) --> data/final-data/
    Validation (V##) --> VALIDATION_REPORT.json
    Manual (M##)   --> ADJUSTMENT_MANIFEST.json
        |
        +---> Stage 6: [Anu Chopped]    -->  Validated CSVs
        +---> Stage 6: [Anu Extenbook]  -->  4-sheet Excel workbooks
        |
        v
  Stage 7: [Anu Visualize]  -->  Interactive app + figure exports
        |
        v
  Stage 8a: [Anu Publish]   -->  Scrubbed, validated public release (GitHub) [OPTIONAL]
  Stage 8b: [Anu Drive]     -->  Consumer Google Drive package (master file + extenbooks + methodology PDF) [OPTIONAL]

  FLOATING:  [Anu Review]   -->  Quality audit at ANY stage
  FLOATING:  [Anu Docs]    -->  Per-series documentation (T1/T2/T3 tiers)
  FLOATING:  [Anu Variant]  -->  Methodology variant tracking
  INFRA:     [Anu Ledger]   -->  Artifact inventory (after each stage)
  INFRA:     [Anu Pipeline] -->  Orchestrates all of the above
```

### Data Integrity Constraints (MANDATORY)

**No Synthetic Data**: No skill in the Anu Framework may generate synthetic, estimated, or placeholder data. Every value in every output must trace to: an HDARP extraction, an API response, a published table, or a digitized figure. If data is unavailable, the series status is `data_unavailable` and the CSV is empty or absent. The pipeline handles missing series gracefully — it never needs fake data to proceed.

**No Proxies**: Extensions must use the EXACT same data source the original author used. CPI is not PPI. Earnings is not compensation. Yield is not total return. If the exact source is discontinued or proprietary, the substitution must be documented with a Concept Match Justification and flagged as `"proxy": true` in the registry.

**No Lazy Splices on Formulas**: If the original author computed a formula (r=NOS/K, P*=D/(r-g)), the extension must compute the same formula with extended component data. Growth-rate splice is only valid for directly-observed time series.

**Unit Documentation**: Every series must have documented units. Every formula combining series must include dimensional analysis.

**Content Type Classification**: Every series must be classified as `time_series`, `cross_sectional`, `theoretical`, or `derived`. Extensions only apply to time_series.

These constraints were formalized from lessons learned in the CD2 Shaikh (2016) replication, where 21% of initial extensions used wrong-concept proxies that were caught only in post-hoc audit. See `Projects/CD2/Technical/docs/SKEPTICAL_EXTENSION_REVIEW.md` for the full case study.

### Single Source of Truth: series_registry.json

Every output format reads from `series_registry.json`:

| Output | What It Reads |
|--------|--------------|
| Chopped CSV Row 1 | `subseries[id].source` + `units` + transform info |
| Chopped CSV Row 2 | Subseries keys as column IDs |
| Extenbook headers | `subseries[id].name` + `[R:YYYY]` for reindexed |
| Extenbook Research sheet | `S###_research.json` entries |
| Dash app trace colors | `subseries[id].color` |
| Dash app labels | `subseries[id].name` + period |
| Console reporter | `construction` steps as tree |
| DPR documents | All registry fields |

---

## Series ID Specification v2.0

| Pattern | Meaning | Example |
|---------|---------|---------|
| `S{NNN}` | Base series | `S001` |
| `S{NNN}-{LETTER}` | Subseries | `S001-A` |
| `S{NNN}-EXT` | API extension data | `S001-EXT` |
| `S{NNN}-COMBINED` | Final spliced series | `S001-COMBINED` |

Display notation for reindexed subseries: `S001-B [R:1958]`

See `docs/SERIES_ID_SPECIFICATION.md` for full details.

---

## Replicator Two-Phase Architecture

### Phase 1: Loading (L## scripts)

- `L00_load_all_data.py` orchestrates all loading scripts
- Each `L{NN}_load_{name}.py` loads one series
- Reads from `data/user-inputs/` (read-only)
- Writes to `data/raw-data/` (API responses + parsed CSVs)

### Phase 2: Processing (P## scripts)

- `P00_process_all_data.py` orchestrates all processing scripts
- Each `P{NN}_process_{name}.py` constructs, extends, and validates one series
- Reads from `data/user-inputs/` + `data/raw-data/`
- Writes to `data/final-data/` (series CSVs, Chopped, Extenbooks, reports)

### Master Orchestrator

`python replicate.py` runs L00 then P00 with detailed console output.

---

## How to Apply the Anu Framework to a New Project

1. `/anu-pipeline init [chapter]` — Initialize pipeline state
2. `/anu-research mine-chapter [chapter]` — Mine KB for all series (Stage 1)
3. `/anu-adequacy [chapter]` — Verify data source readiness (Stage 2, gate)
4. `/anu-ingestion create-registry [chapter]` — Build series_registry.json (Stage 3)
5. `/anu-ingestion decompose [series_id]` — For each series
6. `/anu-extension [chapter]` — Define extension methodology (Stage 4)
7. `/anu-replicator init [project]` — Scaffold Replicator package (Stage 5)
8. Create L##, P##, V##, M## scripts for each series
9. `python replicate.py` — Run end-to-end
10. `/anu-review [chapter]` — Audit quality (floating — run at any stage)
11. `/anu-visualize init` — Create Dash app (Stage 7)
12. `/anu-publish audit [project]` — Prepare for publication (Stage 8, optional)
13. Target Review score >= 85% before publication

---

## Reference Implementation

**CD2** (Capitalism Data v2) is the reference implementation, replicating data from Anwar Shaikh's *Capitalism: Competition, Conflict, Crises* (2016). Chapter 2 is the first fully implemented module.

---

*Anu Framework v11.0 — Data Construction, Empirical Research, and Reproducible Publication*
*Location: docs/ANU_FRAMEWORK_OVERVIEW.md*

**v9.0 Changes** (May 2026):
- Added anu-drive (skill #15) — consumer-facing Google Drive distribution package
- Pipeline Stage 8 split into 8a (Publish/GitHub) and 8b (Drive/Google Drive)
- Framework now covers full distribution lifecycle: GitHub (technical) + Google Drive (consumer)

**v8.0 Changes** (May 2026):
- Rebranded from "Anu Suite" to "Anu Framework"
- Added anu-publish (skill #14) — publication pipeline
- Reordered pipeline: Research → Adequacy → Ingestion (adequacy is post-research)
- Anu Review is now floating (can run at any stage)
- AnuData Architecture (renamed Anu Architecture in v11.0) documented as underlying format standard
- All 14 skills standardized: consistent frontmatter, part-of fields
- Data integrity constraints strengthened: no placeholders, approximations, or freezes

**v7.0 Changes** (May 2026):
- Added anu-data (AnuData Architecture v2.0, formerly NickyData; later renamed anu-architecture in v11.0)
- Renamed anu-shiny to anu-visualize
- Removed anu-standard-v2-archived
