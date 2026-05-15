---
name: anu-pipeline
version: "3.2"
description: "Master orchestrator for Anu Framework data construction workflows. Sequences 19 skills through 8 stages with floating quality review. v3.2 ships a `templates/run.py.j2` generator that scaffolds a project-level `run.py` with `--validate-only`, `--from <stage>`, `--series <sid>`, and `--health` modes — replacing the ad-hoc orchestrator scripts every project was writing by hand. Tracks pipeline state, manages agent handoffs, enforces prerequisites and data integrity gates."
when-to-use: "User wants to run the full Anu Framework pipeline, check pipeline status, orchestrate multi-stage data construction, or scaffold a project-level run.py orchestrator."
search-hints: "pipeline orchestrate stages workflow status progress multi-agent data construction run.py orchestrator template scaffold"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[action] [chapter]"
requires: none
part-of: Anu Framework v11.0
---

# Anu Pipeline Standard v3.2

The master orchestrator for Anu Framework data construction workflows. Sequences 19 skills (was 17; v11.0 adds anu-scaffold and anu-rebuild) through 8 sequential stages plus floating skills, tracks state via `PIPELINE_STATE.json`, and enforces prerequisites and data integrity gates between stages. All packages follow the Anu Architecture format standard.

---

## Pipeline Stages

```
Stage 1:  RESEARCH       -> Anu Research (mine KB for every series)
Stage 2:  ADEQUACY       -> Anu Adequacy (post-research readiness gate) [GATE]
Stage 3:  INGESTION      -> Anu Ingestion (registry, decompose, provenance)
Stage 4:  EXTENSION      -> Anu Extension (define extension methodology)
Stage 5:  REPLICATION    -> Anu Replicator (build L##/P##/V##/M## package in Anu Architecture format)
Stage 6:  OUTPUT         -> Anu Chopped + Anu Extenbook (output formats)
Stage 7:  VISUALIZATION  -> Anu Visualize (interactive app + figure export)
Stage 8:  DISTRIBUTION   -> three sibling channels, any subset [OPTIONAL]
  Stage 8a: PUBLISH      -> Anu Publish (GitHub replication repo — git clone + run)
  Stage 8b: DRIVE        -> Anu Drive (Google Drive consumer package — open files, no code)
  Stage 8c: ARCHIVE      -> Anu Archive (audit-grade transparency package — full provenance + manifest)

FLOATING (invoke at any stage):
  Anu Review             -> Quality audit (14 dimensions, incl. D14) — run early and often
  Anu Docs               -> Per-series documentation (T1/T2/T3 tiers) — enrich at any stage
  Anu Variant            -> Methodology variant tracking — document alternatives as discovered

INFRASTRUCTURE (cross-cutting):
  Anu Ledger             -> Artifact inventory — regenerate after every stage advance
  Anu Architecture       -> The format standard all packages follow
```

### Stage 2 is a Gate

Adequacy runs AFTER Research because research reveals what's available; adequacy then checks whether what's available is sufficient. Pipeline cannot proceed to Ingestion unless adequacy is ADEQUATE (>=80) or EXEMPLARY (>=95).

### Data Integrity Gate (between every stage)

Before advancing to any stage, verify:
- No synthetic, placeholder, approximated, or frozen data in any output
- No `np.random` or fabricated values
- Every value traces to a published source or documented analytical method
- All series with missing data are marked `"status": "data_unavailable"` (not filled)

### Stage Dependencies

| Stage | Prerequisites | Outputs |
|-------|--------------|---------|
| 1. Research | KB exists, scope identified | S###_research.json per series |
| 2. Adequacy | Research complete | ADEQUACY_REPORT.json (gate) |
| 3. Ingestion | Adequacy ADEQUATE+ | series_registry.json, DPRs, decompositions |
| 4. Extension | Ingestion complete | Extension methodology, EPRs |
| 5. Replication | Ingestion + Extension | L##/P##/V##/M## scripts, all data outputs, VALIDATION_REPORT.json |
| 6. Output | Replication complete, V## pass | Chopped CSVs, Extenbook Excels |
| 7. Visualization | Output complete | Interactive app, figure exports, SUBSOURCE_METADATA.json |
| 8a. Publish | Review score >= 85% | GitHub repo: scrubbed code + data, README, LICENSE, CITATION.cff, CI |
| 8b. Drive | Review score >= 85% | Google Drive folder: master workbook, codebook, methodology PDF, per-series workbooks |
| 8c. Archive | Stages 8a + 8b complete | Comprehensive `.zip`: code + data + full provenance trail + MANIFEST.json + CHECKSUMS.txt |

---

## Pipeline State (PIPELINE_STATE.json)

Tracks completion of each stage per chapter:

```json
{
  "project": "[PROJECT]",
  "last_updated": "2026-03-08T15:00:00Z",
  "chapters": {
    "7": {
      "stage_0_adequacy": {
        "status": "complete",
        "completed_date": "2026-03-08",
        "adequacy_score": 92,
        "adequacy_rating": "ADEQUATE",
        "artifact": "Technical/docs/chapters/CH7_ADEQUACY_REPORT.json"
      },
      "stage_1_research": {
        "status": "complete",
        "completed_date": "2026-03-08",
        "series_completed": ["S034", "S035", "S036", "S037", "S038"],
        "artifacts": ["Technical/research/S034_research.json", "..."]
      },
      "stage_2_ingestion": {
        "status": "complete",
        "completed_date": "2026-03-08",
        "series_completed": ["S034", "S035", "S036", "S037", "S038"],
        "artifacts": ["Technical/series_registry.json", "Technical/docs/series/S034_DECOMPOSITION.md", "..."]
      },
      "stage_3_extension": {
        "status": "not_applicable",
        "note": "NAICS revisions prevent direct extension"
      },
      "stage_4_replication": {
        "status": "complete",
        "completed_date": "2026-03-08",
        "verification": {
          "clean_slate_run": true,
          "series_passed": 5,
          "series_failed": 0,
          "total_series": 5
        }
      },
      "stage_5_output": {
        "status": "complete",
        "completed_date": "2026-03-08",
        "verification": {
          "chopped_csvs": "5/5 generated",
          "extenbooks": "5/5 generated",
          "figure_csvs": "8 figure CSVs",
          "absorbed": "chapter_07_absorbed.csv"
        }
      },
      "stage_5b_viz_export": {
        "status": "pending",
        "note": "Figure CSVs generated. Dash integration not yet done."
      },
      "stage_6_viz_audit": {"status": "not_started"},
      "two_tier_structure": {
        "tier_1_composites": {
          "series": ["S034", "S035", "S036", "S037", "S038"],
          "status": "complete"
        },
        "tier_2_input_tables": {
          "series": ["S215", "S216", "S217"],
          "status": "registered"
        }
      }
    }
  }
}
```

---

## Chapter Implementation Workflow

The practical order for implementing a full chapter pipeline, refined from 4 completed chapters:

1. **KB Synthesis**: Read appendix/methodology sources. Create `Inputs/Robert/KB/ch##_topic.md` with equations, data sources, adjustments. Update `appendix_methodology_summary.json`.
2. **Research**: Batch-create all `S###_research.json` for the chapter's Tier 1 series, mining the KB and appendix files.
3. **Registry — Tier 2**: Register all raw input tables (Tier 2) in `series_registry.json` with `"tier": 2`, `source_file`, and column mappings.
4. **Decompositions**: Create `S###_DECOMPOSITION.md` for each Tier 1 series with sub-components, construction steps, and Mermaid diagram.
5. **Registry — Tier 1**: Register all Tier 1 composite series and figure entries in `series_registry.json`.
6. **Loading Scripts**: Create L## scripts for the chapter (one per Tier 2 input table). Run and verify parsed CSVs.
7. **Processing Scripts**: Create P## scripts for each Tier 1 series. Run and verify `_final.csv`, `_chopped.csv`, `_extenbook.xlsx` outputs.
8. **Documentation**: Create DPRs for Tier 1 series, EPRs where extensions are possible, FPRs for all figures.
9. **Absorption**: Run `absorb.py --chapter ##` to generate `chapter_##_absorbed.csv`.
10. **Figure CSVs**: Generate per-figure CSVs by copying chopped CSVs to `data/final-data/figures/`.
11. **Validation**: Regenerate the Ledger, verify health score, check for zero high-priority gaps.
12. **State Updates**: Update `PIPELINE_STATE.json`, `PROGRESS_LOG.md`, `.claude/instructions.md`.

Steps 1-5 can often be parallelized across multiple subagents. Steps 6-7 are sequential (loading must complete before processing).

---

## Skill-Stage Mapping

The Anu Framework consists of 17 skills mapped to pipeline stages:

| Stage | Skill | Creates | Feeds Into |
|-------|-------|---------|-----------|
| 1 | anu-research | S###_research.json | Adequacy, Ingestion, Extension, Extenbook |
| 2 | anu-adequacy | ADEQUACY_REPORT.json (gate) | Ingestion |
| 3 | anu-ingestion | series_registry.json, DPRs, FPRs, decompositions | Extension, Replicator, all output formats |
| 4 | anu-extension | EPRs, extension config in registry, EXTENSION_LOG.json | Replicator |
| 5 | anu-replicator | L##/P##/V##/M## scripts, all data | Output formats, Visualization |
| 6 | anu-chopped + anu-extenbook | Validated CSVs, Excel workbooks | Visualization, Review |
| 7 | anu-visualize | Interactive app, figure exports | Review, Distribution |
| 8a | anu-publish | GitHub repo: scrubbed code + data, CI | External release (developers) |
| 8b | anu-drive | Google Drive consumer package | External release (scholars) |
| 8c | anu-archive | Comprehensive audit `.zip` + MANIFEST + CHECKSUMS | External release (auditors), Zenodo |
| Float | anu-review | Quality audit reports (14 dimensions) | Remediation at any stage |
| Float | anu-docs | Per-series documentation (T1/T2/T3 tiers) | Review, Distribution |
| Float | anu-variant | Variant documentation (VPRs) | Review |
| Infra | anu-ledger | ANU_LEDGER.json | Review (regenerated after every stage) |
| Infra | anu-architecture | Anu Architecture format standard | All packages follow this |

The three Stage-8 channels (anu-publish, anu-drive, anu-archive) are **siblings** — they consume the same upstream outputs and serve three distinct audiences. A project may ship any subset; anu-archive is typically cut after 8a and 8b so it can mirror them.

Every skill has an **Anu Framework Context** section in its SKILL.md describing its pipeline position, upstream/downstream dependencies, and key handoffs.

## Agent Best Practices

### Lead + Teammate Pattern

- **Lead agent**: Manages pipeline state, assigns tasks, verifies prerequisites
- **Teammate agents**: Execute individual stages or series-level work

### Progressive Disclosure

Agents should not attempt to understand the entire project at once. The pipeline provides progressive disclosure:
1. Read `PIPELINE_STATE.json` to know current stage
2. Read the relevant SKILL.md for the current stage
3. Work on the specific series or task assigned
4. Update pipeline state when complete

### Verification at Every Stage

Before advancing to the next stage, verify:
- All required artifacts exist
- All series in the chapter are processed
- Quality checks pass (validation scripts, reference value checks)

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-pipeline status [chapter]` | Show pipeline state for a chapter |
| `/anu-pipeline advance [chapter]` | Advance to the next stage (with prerequisite check) |
| `/anu-pipeline run-stage [stage] [chapter]` | Execute a specific stage |
| `/anu-pipeline init [chapter]` | Initialize pipeline state for a chapter |
| `/anu-pipeline reset [stage] [chapter]` | Reset a stage to not_started |

---

## Integration with Anu Framework

The Pipeline skill references all other 19 skills and enforces their ordering. It is the entry point for agents working on a data construction project. All packages built through the pipeline conform to the Anu Architecture format standard.

---

## Version History

- **v1.0** (March 2026) — Initial release with 7 stages
- **v2.0** (April 2026) — Added Validation (V##) and Manual Adjustment (M##) stages. 10 stages total.
- **v3.0** (May 2026) — Major rewrite for Anu Framework v8.0:
  - Reordered: Research (Stage 1) → Adequacy (Stage 2) — research reveals what's available, then adequacy checks sufficiency
  - Anu Review is now FLOATING — can run at any stage, not locked to Stage 6
  - Added Stage 8: Publication (anu-publish) as optional final stage
  - AnuData Architecture documented as the underlying format standard (renamed to Anu Architecture in v11.0)
  - Consolidated V##/M## into Stage 5 (Replication) as sub-phases
  - Data integrity gate enforced between every stage transition
  - Updated to 14 skills (added the architecture skill [originally named "anu&#8209;data", renamed `anu-architecture` in v11.0], anu-publish, anu-visualize)
  - Removed project-specific references (CS extraction is a project pattern, not a pipeline stage)
- **v3.1** (May 2026) — Anu Framework v10.0 integration:
  - Stage 8 split into three sibling distribution channels: 8a Publish (GitHub), 8b Drive (Google Drive), 8c Archive (comprehensive audit `.zip`)
  - Added `anu-docs` as a FLOATING skill (per-series documentation, T1/T2/T3 tiers)
  - Updated to 17 skills (added anu-archive, anu-docs; anu-drive promoted to a named stage)
  - anu-review referenced as 14 dimensions (D14 Outward-Facing Intelligibility added)

---

## Template

- `templates/PIPELINE_STATE_TEMPLATE.json`

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `PIPELINE_STATE.json` |
| **Expects** | All stage artifacts as defined by each skill's Documentation Contract |
| **Must Update on Completion** | Update `PIPELINE_STATE.json` stage status. Regenerate Ledger (`/anu-ledger generate`) on every stage advance |

Before advancing to the next stage, validate that the current stage's Documentation Contract artifacts all exist. The Ledger's `series_inventory` provides this check automatically. Block advancement if mandatory artifacts are missing (agents may override with explicit justification).

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Multi-Agent Workflow Orchestrator*
