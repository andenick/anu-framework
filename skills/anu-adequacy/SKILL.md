---
name: anu-adequacy
version: "1.2"
description: "Post-research readiness gate that validates whether data sources, series definitions, and construction logic are sufficient to proceed to ingestion. Runs after Anu Research (Stage 2)."
when-to-use: "User wants to check if a chapter is ready for pipeline processing, or validate Knowledge Base sufficiency after research"
search-hints: "adequacy readiness gate validate knowledge base sufficient ready post-research"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[action] [chapter]"
requires: anu-research
part-of: Anu Framework v12.2
---

# Anu Adequacy Standard v1.2

A pre-pipeline readiness check that validates whether the Knowledge Base, series definitions, data sources, construction logic, and validation data are sufficient to construct all series in a chapter with full traceability. Produces an `ADEQUACY_REPORT.json` artifact that gates entry to Stage 1 (Research).

---

## Stage Position

**Stage 2 — ADEQUACY** in the canonical stage sequence maintained by `anu-build`: it runs after Stage 1 (Research) and gates entry to Stage 3 (Ingestion).

> **Legacy numbering note.** Sections further down this file (When to Use, Anu Framework Context, Integration with Anu Framework) were written before the framework-wide stage renumbering and still label this skill "Pipeline Stage 0 / before Research", with the state key `stage_0_adequacy`. Those labels are preserved verbatim because the state key they name is still what projects write. The canonical stage number is the one above.

---

## Purpose

Before constructing any data series, an agent must verify that sufficient information exists to:
1. Understand what the original author did (source text)
2. Define every series and subseries (registry completeness)
3. Obtain all raw data inputs (data source availability)
4. Trace every transformation from input to output (construction logic)
5. Verify the result against published values (validation data)

Without this check, agents discover missing information mid-pipeline, producing artifacts with gaps that compound through downstream stages.

---

## When to Use

Run Anu Adequacy **before** Anu Research (Pipeline Stage 0):

- When starting a new chapter in an existing project
- When starting a new data construction project
- When significant new KB material has been added
- When reviewing whether a project is ready for pipeline execution
- As a periodic health check during long-running construction projects

---

## Prerequisites

1. **Knowledge Base exists**: Some form of KB (Knowledge Base extractions, page-level text, appendix files) is available
2. **Chapter scope identified**: The chapter number, expected series list, and associated figures are known (from a Chapter Investigation or similar scoping document)
3. **Project structure initialized**: The framework-standard directory structure exists (Inputs/, Technical/)

---

## Five Adequacy Layers

### Layer 1: Source Text Completeness

**Question**: Do we have all book pages, appendix pages, and methodology text needed to understand every series?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Chapter narrative pages | Glob KB for page files covering the chapter's page range | >=95% of chapter page range has KB entries |
| Appendix/methodology pages | Glob KB for appendix pages referenced by the chapter | All referenced appendix pages present |
| Tables extracted | Cross-check expected data tables against KB tables/ directory | All referenced tables have CSV or structured extraction |
| Equations extracted | Cross-check key formulas against KB equations/ directory | All key equations have TEX/TXT extraction |
| Footnotes/endnotes | Verify methodology footnotes are findable in KB text | >=90% of cited footnotes locatable |

**How to assess**: Determine the chapter's page range from the book's table of contents or chapter investigation document. Glob `Technical/Knowledge_Base/text/` for `page_NNN_*.md` files. Count coverage. Check `Technical/Knowledge_Base/tables/` and `Technical/Knowledge_Base/equations/` for referenced items.

**Layer score**: Weighted average of check pass rates (pages 40%, tables 25%, equations 15%, appendix 10%, footnotes 10%).

### Layer 2: Series Definition Completeness

**Question**: Is every series fully defined with subseries, construction steps, and dependencies?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Series inventory complete | Count registry entries vs. expected from chapter investigation | 100% of expected series registered |
| Subseries defined | Each registry entry has non-empty `subseries` array | No empty subseries |
| Construction documented | Each series has construction steps or decomposition reference | All have construction logic |
| Dependencies explicit | Cross-references and upstream dependencies listed | No orphan references |
| ID convention consistent | All IDs follow S### or T### pattern | No conflicts or gaps |

**How to assess**: Read `series_registry.json` (if it exists) or the chapter investigation document. Count expected vs. registered series. Verify each has subseries definitions and construction metadata.

**Note**: If the project has not yet created `series_registry.json`, score based on whether the chapter investigation or scoping document defines all expected series. The registry will be created during Ingestion (Stage 2).

**Layer score**: Binary checks — each either passes (100%) or fails (0%). Average across all checks.

### Layer 3: Data Source Availability

**Question**: Can we actually obtain the raw data needed to construct each series?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Book-period data present | Check absorbed CSV or Inputs/ for original digitized data | All book-period values accessible |
| API endpoints identified | For each extendable series, BEA/FRED/BLS table IDs documented | All extension sources identified |
| API data fetchable | Test API calls or verify cached data in Inputs/ | >=90% of API sources return data |
| External benchmarks located | Check Inputs/ExternalSources/ for validation datasets | Benchmarks for >=80% of key series |
| Structural breaks cataloged | Known methodology changes documented with bridge strategy | All breaks identified |

**How to assess**: Check `Inputs/` for source data files. If a `data_coverage_matrix.csv` exists, read it. For API sources, check if table IDs are documented in research JSONs or registry entries. Check `Inputs/ExternalSources/` for benchmark datasets.

**Layer score**: Weighted (book-period 30%, API identified 25%, API fetchable 20%, benchmarks 15%, breaks 10%).

### Layer 4: Construction Logic Verifiability

**Question**: Can we trace every output value back to its inputs through documented transformations?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Decompositions exist | Glob for S###_DECOMPOSITION.md or T###_DECOMPOSITION.md | 100% of series have decompositions |
| Flow diagrams present | Check each decomposition has a Mermaid diagram | All have flow diagrams |
| Input chain complete | Verify terminal nodes in diagrams map to Layer 3 sources | No dangling inputs |
| Formulas documented | Key calculations (e.g., NSW = B_w + G_w - T_w) present | All derived series have explicit formulas |

**How to assess**: Glob `Technical/docs/series/` for decomposition files. Read each and verify Mermaid blocks exist. Cross-check terminal nodes against data sources identified in Layer 3.

**Note**: If decompositions don't exist yet (pre-Ingestion), assess from the chapter investigation and KB methodology descriptions. The question is: "Could an agent write the decomposition from available information?"

**Layer score**: Weighted (decompositions 40%, diagrams 20%, chain complete 25%, formulas 15%).

### Layer 5: Validation Data Sufficiency

**Question**: How will we know if our replication is correct?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Figures mapped to series | Each figure in scope has associated series IDs | All figures mapped |
| Published values accessible | Author's original data in KB or absorbed CSV | Book-period benchmarks available |
| External validation sources | Independent estimates identified | >=1 external source per key series |
| Tolerance thresholds defined | Acceptable deviation documented | Thresholds set for key series |
| Cross-chapter constraints | Inter-series rules documented | Consistency rules defined |

**How to assess**: Check `FIGURE_SERIES_CATALOG.json` for figure-to-series mappings. Check absorbed CSVs for benchmark data. Check `Inputs/ExternalSources/` for independent validation datasets. Review chapter investigation for tolerance discussions.

**Layer score**: Weighted (figures 20%, published values 30%, external sources 25%, tolerances 15%, constraints 10%).

### Layer 6: Data Authenticity Readiness

**Question**: Will the planned data construction use only real data, or are synthetic placeholders planned?

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| No synthetic series planned | Review series_registry.json status fields | No series has `"status": "synthetic"` |
| KB tables extracted | Verify all annual data tables in KB are parsed to CSV | 100% of available annual tables extracted |
| Data gaps documented | Review GAP_REGISTER for data availability | Each gap has an acquisition plan (API, digitize, request) |

**If any series would require synthetic data**: BLOCKED. The agent must acquire real data before proceeding.

**How to assess**: Grep series_registry.json for `synthetic` or `estimated_from_benchmarks`. Grep P## scripts for `np.random`. Check that every gap in the GAP_REGISTER has a resolution plan that doesn't involve fabrication.

**Layer score**: Binary — PASS (no synthetic planned) or BLOCKED (synthetic required).

---

## Output Format

**File**: `Technical/docs/chapters/CH{N}_ADEQUACY_REPORT.json`

```json
{
  "project": "[PROJECT_ID]",
  "chapter": 5,
  "assessment_date": "2026-03-22",
  "assessor": "agent",
  "version": "1.0",
  "overall_adequacy": "ADEQUATE",
  "overall_score": 92,
  "layers": {
    "L1_source_text": {
      "score": 95,
      "status": "PASS",
      "checks": {
        "chapter_pages": {
          "expected": 56,
          "found": 53,
          "pct": 94.6,
          "status": "PASS",
          "detail": "Pages 95-150; missing page_097, page_098, page_142"
        },
        "appendix_pages": {
          "expected": 12,
          "found": 12,
          "pct": 100.0,
          "status": "PASS"
        },
        "tables_extracted": {
          "expected": 5,
          "found": 5,
          "pct": 100.0,
          "status": "PASS",
          "detail": "page_310_table_E2.csv is primary"
        },
        "equations_extracted": {
          "expected": 4,
          "found": 4,
          "pct": 100.0,
          "status": "PASS"
        },
        "footnotes_captured": {
          "expected": 18,
          "found": 16,
          "pct": 88.9,
          "status": "PASS"
        }
      },
      "gaps": ["page_097 and page_098 not in KB"]
    },
    "L2_series_definition": {
      "score": 100,
      "status": "PASS",
      "checks": {},
      "gaps": []
    },
    "L3_data_availability": {
      "score": 85,
      "status": "PASS",
      "checks": {},
      "gaps": ["BEA SIC-era tables pre-1997 not available via API"]
    },
    "L4_construction_logic": {
      "score": 95,
      "status": "PASS",
      "checks": {},
      "gaps": []
    },
    "L5_validation_data": {
      "score": 88,
      "status": "PASS",
      "checks": {},
      "gaps": ["No external validation for intermediate accounts T507-T510"]
    }
  },
  "blocking_gaps": [],
  "non_blocking_gaps": [
    "BEA SIC-era API gap affects extension only",
    "T507-T510 lack external validation (book-period intermediates)"
  ],
  "recommendation": "PROCEED - all blocking requirements met",
  "remediation_checklist": []
}
```

### Overall Score Calculation

```
overall_score = (L1 * 0.25) + (L2 * 0.20) + (L3 * 0.25) + (L4 * 0.15) + (L5 * 0.15)
```

Weights reflect pipeline impact: source text and data availability are most critical.

### Adequacy Thresholds

| Rating | Score | Pipeline Gate |
|--------|-------|---------------|
| EXEMPLARY | >=95 | PROCEED |
| ADEQUATE | 80-94 | PROCEED (gaps documented) |
| INSUFFICIENT | 60-79 | REMEDIATE FIRST |
| BLOCKED | <60 | CANNOT PROCEED |

**Gate rule**: Any layer scoring below 60 makes the overall rating BLOCKED regardless of the weighted average. Any layer scoring below 70 caps the overall rating at INSUFFICIENT.

---

## Remediation Guidance

When gaps are found, the adequacy report includes a `remediation_checklist`:

| Gap Type | Remediation |
|----------|-------------|
| Missing KB pages | Run a PDF extraction or manual transcription for missing page range |
| Missing tables | Extract tables from book PDF using table extraction |
| Missing equations | Manually transcribe equations from book into TEX format |
| Undefined series | Create chapter investigation document defining all series |
| Missing API source IDs | Research BEA/FRED/BLS table catalogs for equivalent modern tables |
| No benchmark data | Search literature for independent estimates; check ExternalSources/ |
| Structural break undocumented | Research methodology changes; document bridge strategy |
| Missing decomposition source info | Mine KB more thoroughly; may need additional page extractions |

---

## Anu Framework Context

- **Pipeline Stage**: 0 (ADEQUACY — pre-pipeline gate)
- **Upstream**: KB exists (Knowledge Base extractions, data imports)
- **Downstream**: Stage 1 Research (gated), all subsequent stages
- **Adequacy Relevance**: IS the adequacy check — produces the ADEQUACY_REPORT.json that flows through all stages
- **Key Handoff**: ADEQUACY_REPORT.json consumed by Research (adequacy_refs), Review (D0), Pipeline (stage_0_adequacy)

## Integration with Anu Framework

### As Pipeline Stage 0

Anu Adequacy runs as Stage 0 before Research. The pipeline state tracks it:

```json
{
  "stage_0_adequacy": {
    "status": "complete",
    "completed_date": "2026-03-22",
    "adequacy_score": 92,
    "adequacy_rating": "ADEQUATE",
    "artifact": "Technical/docs/chapters/CH5_ADEQUACY_REPORT.json"
  }
}
```

### As Anu Research Prerequisite

Anu Research (v1.3+) checks for the adequacy report before starting:
- If ADEQUATE or better: proceed with research
- If INSUFFICIENT: warn agent, suggest remediation
- If BLOCKED: refuse to start research

### As Anu Review D0

Anu Review (v3.7+) includes D0 as an unweighted gate check:
- Reports whether adequacy was checked and the score
- Does not affect the 12-dimension weighted score
- Provides context for understanding dimension scores

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-adequacy check [chapter]` | Run full adequacy assessment for a chapter |
| `/anu-adequacy layer [N] [chapter]` | Run a single layer check (1-5) |
| `/anu-adequacy remediate [chapter]` | Generate remediation checklist from existing report |
| `/anu-adequacy status [chapter]` | Show current adequacy status |

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `Technical/docs/chapters/CH{N}_ADEQUACY_REPORT.json` |
| **Expects** | KB directory, chapter investigation or series list |
| **Must Update** | `PIPELINE_STATE.json` stage_0_adequacy on completion |
| **Gates** | Stage 1 (Research) requires ADEQUATE or higher |

---

## Inputs

Every input below is one this SKILL.md's layer checks already read. Nothing is required to exist at a fixed path — a layer scores what it can find and records the rest as a gap.

| Input | Where it is read from | Used by |
|-------|----------------------|---------|
| Knowledge Base page extractions | `Technical/Knowledge_Base/text/page_NNN_*.md` | Layer 1 |
| Knowledge Base tables + equations | `Technical/Knowledge_Base/tables/`, `Technical/Knowledge_Base/equations/` | Layer 1, Layer 6 |
| Chapter scope (page range, expected series, figures) | Chapter investigation or equivalent scoping document | Layers 1, 2, 5 |
| `series_registry.json` | `Technical/series_registry.json` (may not exist yet — see the Layer 2 note) | Layers 2, 6 |
| Source data and cached API pulls | `Inputs/` | Layer 3 |
| `data_coverage_matrix.csv` | `Inputs/` (when the project maintains one) | Layer 3 |
| External benchmark datasets | `Inputs/ExternalSources/` | Layers 3, 5 |
| Decomposition documents | `Technical/docs/series/*_DECOMPOSITION.md` | Layer 4 |
| Figure-to-series mapping | `FIGURE_SERIES_CATALOG.json` | Layer 5 |
| GAP_REGISTER | The project's gap register | Layer 6 |
| P## processing scripts | The project's replicator code tree (grepped for `np.random`) | Layer 6 |

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| `CH{N}_ADEQUACY_REPORT.json` | `Technical/docs/chapters/` | The layer-by-layer assessment: per-layer scores, per-check counts, gaps, `overall_score`, `overall_adequacy`, `blocking_gaps`, `non_blocking_gaps`, `recommendation` |
| `remediation_checklist` | Inside the same report | Populated from the Remediation Guidance table when gaps are found; also what `/anu-adequacy remediate` re-derives |
| `stage_0_adequacy` block | `PIPELINE_STATE.json` | Status, completion date, score, rating, and the path to the report — written on completion per the Documentation Contract |

This skill writes no data files, no code, and no series artifacts. Its only product is the assessment and the pipeline-state update it triggers.

---

## Acceptance Gates

The report itself is the gate. Its verdict is computed, not asserted:

| Rating | Score | Pipeline gate |
|--------|-------|---------------|
| EXEMPLARY | >=95 | PROCEED |
| ADEQUATE | 80–94 | PROCEED (gaps documented) |
| INSUFFICIENT | 60–79 | REMEDIATE FIRST |
| BLOCKED | <60 | CANNOT PROCEED |

Three overrides sit on top of the weighted average:

1. **Any layer below 60 → BLOCKED**, regardless of the weighted average.
2. **Any layer below 70 → capped at INSUFFICIENT**, regardless of the weighted average.
3. **Layer 6 is binary.** If any series would require synthetic data, the outcome is BLOCKED and real data must be acquired before proceeding — there is no partial credit.

Downstream consumers enforce the verdict: Anu Research proceeds on ADEQUATE or better, warns on INSUFFICIENT, and refuses to start on BLOCKED. Anu Review reads the report as its unweighted D0 gate check.

---

## Anti-Patterns

| Anti-pattern | Why it's wrong | Do this instead |
|---|---|---|
| Averaging past a failing layer | A weighted mean can hide a layer at 40 | Apply the layer floors: <60 is BLOCKED, <70 caps at INSUFFICIENT |
| Proceeding to Research on a BLOCKED report | The gate exists precisely to stop this | Remediate first; Anu Research refuses to start on BLOCKED |
| Planning to fill a gap with synthetic or estimated values | Layer 6 exists to catch this before it enters the pipeline | Give every gap an acquisition plan (API, digitize, request) |
| Scoring a layer from impression rather than evidence | Every layer specifies a concrete "How to assess" procedure | Glob the KB, read the registry, check `Inputs/` — then score |
| Treating a missing `series_registry.json` as an automatic Layer 2 zero | The registry is created at Ingestion, downstream of this gate | Score Layer 2 from the chapter investigation or scoping document, per the Layer 2 note |
| Treating missing decompositions as an automatic Layer 4 zero | Decompositions are also written downstream | Ask the Layer 4 question: could an agent write the decomposition from what exists today? |
| Writing the report and stopping | The gate is only observable to the pipeline through state | Update `PIPELINE_STATE.json` `stage_0_adequacy` on completion |

---

## Version History

- **v1.0** (March 2026) - Initial release. 5-layer assessment framework. Learned from predecessor-project and reference-implementation gap analysis.
- **v1.1** (March 2026) - Added Anu Framework Context section; integrated with full suite awareness
- **v1.2** (April 2026) - Version bump for Anu Framework v11.0 alignment; noted validation phase integration

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v12.2 - Pre-Pipeline Readiness Gate*
