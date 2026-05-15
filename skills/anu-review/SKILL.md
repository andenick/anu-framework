---
name: anu-review
version: "4.1"
description: Systematic audit tool for reviewing data chapter/module quality across the Anu Framework skills. 12 weighted dimensions (Research, Ingestion, Extension, Replicator, Chopped, Extenbook, Viz Quality, Documentation, ...) plus 2 gates — D13 Data Authenticity and D14 Outward-Facing Intelligibility. Use when auditing data construction projects.
when-to-use: User wants to audit data quality, review a chapter for completeness, or run the 14-dimension quality assessment
search-hints: review audit quality dimensions score completeness assessment data chapter D14 intelligibility
argument-hint: [chapter] or [action] [target]
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: none
part-of: Anu Framework v11.0
---

# Anu Review Standard v4.1: Integration Quality Audit Framework

A systematic audit tool for reviewing how well data chapters/modules are integrated into a data construction project. Part of the Anu Framework of tools.

---

## Quick Reference

### Purpose

The Anu Review validates compliance with the current Anu Framework v11.0 skills, including:
- **Anu Ingestion v3.0** - Data provenance, absorption, and series decomposition
- **Anu Extension v3.4** - Maximum faithfulness data extension
- **Anu Visualize v5.0** - Visualization application integration (R Shiny + Plotly / Plotly Dash)
- **Anu Publish / Anu Drive / Anu Archive** - the three external distribution channels audited by D14

### When to Use This Skill

Apply the Anu Review when:
- Completing a chapter integration
- Auditing existing data construction work
- Comparing implementation quality across chapters
- Identifying gaps in documentation or code
- Preparing for project milestones or handoffs

---

## Commands

```
/anu-review [chapter]           # Review single chapter (e.g., /anu-review 2)
/anu-review full [project]      # Review entire project
/anu-review compare [ch1] [ch2] # Compare two chapters
/anu-review gaps [chapter]      # Show only gaps
/anu-review score [chapter]     # Show only score
/anu-review checklist [chapter] # Show checklist with pass/fail
```

---

## Review Dimensions

The Anu Review evaluates **12 weighted dimensions** (D1–D12, summing to 100%) plus **2 gates** (D13, D14) that are scored 0–100 and reported alongside the weighted score but not folded into it.

### Weighted dimensions (D1–D12, sum = 100%)

| Dim | Weight | Description |
|-----|--------|-------------|
| D1 KB Completeness | 6% | Knowledge Base extraction quality and coverage |
| D2 Absorption Quality | 5% | Absorbed database coverage and accuracy |
| D3 Research Coverage | 8% | S###_research.json exists and is comprehensive for all series |
| D4 Decomposition Coverage | 9% | S###_DECOMPOSITION.md exists for all series |
| D5 DPR Completeness | 10% | Data Provenance Records quality |
| D6 EPR Completeness | 8% | Extension Provenance Records quality |
| D7 Chopped Validation | 9% | Anu Chopped CSV format compliance (dash notation, Row 1 metadata) |
| D8 Replicator Scripts | 12% | L## and P## scripts exist, run, produce correct output |
| D9 Extenbook Quality | 6% | 4-sheet structure, year formatting, registry-driven colors |
| D10 Viz Integration & Quality | 8% | Data artifacts + 10-point app quality checklist (charts render, no errors, metadata exposition, extension traces, validation passes) |
| D11 Test Coverage | 7% | Automated validation tests passing |
| D12 Documentation | 12% | DPRs, EPRs, decompositions, guides, README completeness |

### Gates (D13, D14 — scored 0–100, reported separately)

| Gate | Description |
|------|-------------|
| D13 Data Authenticity | No synthetic / placeholder / approximated / frozen data in any series |
| D14 Outward-Facing Intelligibility | Externally-distributed artifacts use public names, not internal jargon |

**D13 Data Authenticity Checklist**:
- [ ] No `np.random` calls in any L## or P## script
- [ ] No `"data_quality": "estimated_from_benchmarks"` in series_registry.json
- [ ] No `"status": "synthetic"` in series_registry.json
- [ ] Every CSV value traces to an identifiable source (KB extraction, API, published table)
- [ ] EPRs with faithfulness < 50% are flagged for data acquisition

Any synthetic series = automatic INCOMPLETE certification for the project.

**D14 Outward-Facing Intelligibility Checklist**:

D14 audits every artifact an external party actually receives — the GitHub repo (`anu-publish`), the Drive package (`anu-drive`), the comprehensive archive (`anu-archive`), the methodology PDF, the codebook, and any project README/CITATION. The rule: external surfaces refer to content by its **public name**.

- [ ] The project's short identifier (e.g. a codename) is expanded at first use or absent
- [ ] No internal infrastructure names leak (Council-member names, internal tool names, internal directory names)
- [ ] Public data sources are cited by their public name and URL (FRED, BEA, BLS, OECD — not internal import folders)
- [ ] Internal acronyms (DPR, EPR, FPR, KB, L##/P##/V##, tier labels, wave labels) are either defined inline or absent from external surfaces
- [ ] DARP / HDARP, where mentioned, are honestly disclosed as the extraction method with the caveat that extraction errors are possible
- [ ] Methodological abbreviations (IROP, HP-filter, NIPA, etc.) are defined in a Notation or Glossary section
- [ ] Series-ID notation (`S###`, `-A`, `-EXT`, `-COMBINED`) is explained at first use

Score D14: 100 minus deductions per unexplained internal term weighted by surface visibility (a README first-paragraph leak costs more than a deep-metadata leak). A score < 90 should block external distribution until remediated. See `docs/DATA_PROVENANCE_STANDARDS.md` (External Disclosure Policy) and `ANU_FRAMEWORK_GLOSSARY.md`.

---

## Mandatory Source Material Reading (CRITICAL)

**Before scoring ANY dimension**, the reviewer MUST:

1. **Read the original source material** via the Knowledge Base (`Inputs/Robert/KB/`). Every chapter has HDARP-extracted text from the author's book. Read the methodology sections, appendix descriptions, and figure captions.

2. **Cross-check data values** against the author's published figures and tables. Do not rely solely on automated validation — V01 reference value checks cover a sample of points, not every value.

3. **Verify unit conventions**. The author may use decimal (0.09 = 9%) while extensions use percent (9.0). Index bases may differ (2005=100 vs 2017=100). Growth rates vs levels. Always compare a few hand-computed values.

4. **Verify extension methodology matches the author's construction**. Read how the author built each series (what agency, what table, what formula), then confirm the extension uses the same agency, table, and formula. If the extension uses a different source, it must be documented as a proxy with justification.

5. **Check for scale mismatches at splice points**. Compare the last Shaikh value with the first extension value. A relative difference >50% for non-volatile series, or a sign change, requires investigation.

**Why this matters**: In the reference project, automated validation (V01: 383/383 PASS) missed an 88x unit mismatch (S069) and a 5340x scale mismatch (S087) that were only caught by reading the actual data against the book. Source material reading is not optional.

---

## Scoring Methodology

### Integration Score Calculation (v2.0)

```
Integration Score = Sum of (Dimension_Score × Weight) for D1–D12   (weights sum to 100%)
```

D13 (Data Authenticity) and D14 (Outward-Facing Intelligibility) are **gates**, not weighted dimensions: each is scored 0–100 and reported alongside the Integration Score. D13 failing (any synthetic series) forces INCOMPLETE certification regardless of the weighted score. D14 below 90 blocks external distribution but does not change the chapter's Integration Score — it is reported as a separate project-level number so reviews remain comparable across framework versions.

Uses the weights defined in the dimensions table above. When `ANU_LEDGER.json` exists, the D12 Documentation dimension can reference the Ledger's `coverage` percentages directly.

### Certification Levels

| Level | Score | Description |
|-------|-------|-------------|
| **EXEMPLARY** | ≥95% | Reference implementation, exceeds all standards |
| **COMPLETE** | ≥85% | Fully integrated, meets all core requirements |
| **ADEQUATE** | ≥70% | Functional with documented gaps |
| **INCOMPLETE** | <70% | Requires attention before production use |

---

## Dimension Checklists

All checklists reference the Anu Framework v11.0 artifact structure. Tier 2 series (raw input tables) are exempt from D4, D5, D6, and are scored only on loading script existence.

### D0. v6.0 Artifacts (unweighted gate check)

The following v6.0 artifacts are checked as a gate condition. Absence does not reduce the weighted score but is reported prominently:

- [ ] **Validation phase completeness**: `VALIDATION_REPORT.json` exists with V01-V08 results; no FAIL status on critical checks (V01 reference values, V04 completeness, V08 hash integrity)
- [ ] **Decision log presence**: `DECISION_LOG.md` exists with <decision-ref> format entries for any non-trivial methodological decisions
- [ ] **Assumptions documentation**: `ASSUMPTIONS.md` exists with ASM-D (data), ASM-M (methodological), ASM-R (replication) categories documented
- [ ] **Provenance index quality**: `provenance_index.json` exists with `by_source`, `by_api`, and `by_series` sections; all series in scope have lineage chains
- [ ] **Manual adjustment manifest**: If M## scripts exist, `ADJUSTMENT_MANIFEST.json` documents all adjustments with justifications and decision references

### D1. KB Completeness (6%)

- [ ] KB synthesis file exists for the chapter (`Inputs/Robert/KB/ch##_topic.md`)
- [ ] Theoretical framework section present with key equations
- [ ] Data sources and methods documented with appendix references
- [ ] Key quotes from the book extracted and cited
- [ ] Adjustments and methodology notes captured
- [ ] `appendix_methodology_summary.json` updated with chapter entry

**Scoring**: `(Checklist items passed / 6) × 100`

### D2. Absorption Quality (5%)

- [ ] Absorbed database exists (`Technical/absorbed/chapter_##_absorbed.csv`)
- [ ] Long-format with columns: `series_id`, `subseries_id`, `year`, `value`, `source_file`
- [ ] All Tier 1 series in the chapter are represented
- [ ] Row count is reasonable (no empty series, no duplicate rows)
- [ ] Absorption report exists (`Technical/absorbed/chapter_##_absorbed_REPORT.md`)

**Scoring**: `(Checklist items passed / 5) × 100`

### D3. Research Coverage (8%)

For each Tier 1 series in the chapter:

- [ ] `Technical/research/S###_research.json` exists
- [ ] At least one `methodology_description` entry present
- [ ] All original data sources have `source_citation` entries
- [ ] All figures referencing this series have `figure_context` entries
- [ ] `methodology_summary` accurately describes the construction
- [ ] `citations` array has full bibliographic info for every source
- [ ] `cross_references` lists related series

**Scoring**: `(Series with complete research / Total Tier 1 series) × 100`

### D4. Decomposition Coverage (9%)

For each Tier 1 series in the chapter:

- [ ] `Technical/docs/series/S###_DECOMPOSITION.md` exists
- [ ] Quick Reference table complete (series ID, chapter, figures, sources, year range)
- [ ] Sub-component table lists all subseries with source, period, units
- [ ] Construction steps are specific and ordered
- [ ] Construction diagram (Mermaid flowchart) present
- [ ] Source methodology section documents formulas and adjustments

**Scoring**: `(Series with complete decomposition / Total Tier 1 series) × 100`

### D5. DPR Completeness (10%)

For each Tier 1 series in the chapter:

- [ ] `Technical/docs/series/S###_DPR.md` exists
- [ ] Quick Reference table complete
- [ ] Subsources table with source, period, units
- [ ] Year-Source Matrix present
- [ ] Core formula documented
- [ ] Data sources listed (primary and adjustments)
- [ ] Validation notes from pipeline run
- [ ] Related series cross-referenced

**Scoring**: `(Series with complete DPR / Total Tier 1 series) × 100`

### D6. EPR Completeness (8%)

For each Tier 1 series with extension potential:

- [ ] `Technical/docs/series/S###_EPR.md` exists
- [ ] Extension methodology documented (API sources, splice approach)
- [ ] Data sources for extension identified with URLs/endpoints
- [ ] Validation notes (splice quality, correlation checks)
- [ ] If no extension possible, documented as `"extension": null` in registry with reason

**Scoring**: `(Series with EPR / Series needing EPR) × 100`. Series with no extension get full marks.

### D7. Chopped Validation (9%)

For each Tier 1 series in the chapter:

- [ ] `data/final-data/chopped/S###_chopped.csv` exists
- [ ] Row 1 contains metadata strings (auto-generated from registry)
- [ ] Row 2 contains column IDs using dash notation (`S###-A`, not `S###A`)
- [ ] Year column is first column
- [ ] All data cells are numeric or empty
- [ ] No duplicate column IDs
- [ ] `SUBSOURCE_METADATA.json` exists and every column ID in this Chopped CSV has a matching entry (V10)

**Scoring**: `(Series with valid Chopped CSV / Total Tier 1 series) × 100`

### D8. Replicator Scripts (12%)

For each series in the chapter (both Tier 1 and Tier 2):

- [ ] Loading script exists (`scripts/loading/L##_load_*.py`)
- [ ] Loading script runs without error and produces `S###_parsed.csv`

For each Tier 1 series:

- [ ] Processing script exists (`scripts/processing/P##_process_*.py`)
- [ ] Processing script runs without error
- [ ] Processing script produces `S###_final.csv`, `S###_chopped.csv`, `S###_extenbook.xlsx`
- [ ] Processing script returns `data_dict` with subseries mapped to pandas Series
- [ ] Cross-chapter dependencies documented in docstring (if any)

**Scoring**: `(Scripts passing / Scripts required) × 100`

### D9. Extenbook Quality (6%)

For each Tier 1 series in the chapter:

- [ ] `data/final-data/extenbooks/S###_extenbook.xlsx` exists
- [ ] Contains 4 sheets: Data, Provenance, Research, Construction
- [ ] Year column formatted as integers (not decimals)
- [ ] Column headers use reindex notation where applicable (`S###-B [R:1958]`)
- [ ] All subseries present as columns in Data sheet

**Scoring**: `(Series with valid Extenbook / Total Tier 1 series) × 100`

### D10. Viz Integration & Quality (8%)

**D10a. Data Artifacts (40% of D10)**

- [ ] Figure CSVs exist in `data/final-data/figures/` for all chapter figures
- [ ] Chapter CSV exists in `data/final-data/shiny/chapter_NN.csv` (if viz export run)
- [ ] `series_catalog.json` includes entries for all chapter series
- [ ] Column names use `viz_column` aliases from registry
- [ ] Per-figure CSVs contain correct columns and year ranges
- [ ] `SUBSOURCE_METADATA.json` exists in `data/final-data/shiny/` with entries for all chopped columns
- [ ] `construction_text` is non-empty for all Tier 1 series in `SUBSOURCE_METADATA.json`
- [ ] All subsource entries have non-null `period_start`, `period_end`, `source_name`, and `role`

**D10b. Application Quality Checklist (60% of D10)**

- [ ] **Q1: All charts render** — No "Error building chart" messages for any series in the chapter
- [ ] **Q2: No R console errors** — No `$operator is invalid for atomic vectors` or `missing value where TRUE/FALSE needed` in server logs
- [ ] **Q3: Methodology panels populate** — Figure number, page reference, and construction narrative display correctly
- [ ] **Q4: Author quotes display** — With page numbers, no rendering errors, topic tags visible (if project uses quotes)
- [ ] **Q5: Extension data visible** — Extension subsources appear as separate chart traces (not collapsed into the final series). Every extended series must have subsources with `is_extension: true` in the project's `SUBSOURCE_METADATA.json`. Chopped CSVs must contain both `-EXT` (raw) and `-F` (re-indexed) columns for extended series.
- [ ] **Q5b: Component data visible** — For ratio/rate series with `concurrent_series` in the registry, verify: (a) CS columns exist in the chopped CSV, (b) CS entries exist in `SUBSOURCE_METADATA.json` with `is_component: true` and valid `component_type` ("numerator" or "denominator"), (c) "Show Components" mode renders in the viz app with dual Y-axis (rate on left, level-data on right). Series that are not ratios/rates (indices, levels, averages, deviations) are exempt.
- [ ] **Q6: Year ranges correct** — Chart X-axis matches actual data extent; no aggressive truncation from metadata year ranges
- [ ] **Q7: Trace labels descriptive** — Legend labels describe what the data is (e.g., "Unemployment Rate (FRED UNRATE)"), not just the source identifier
- [ ] **Q8: Data tables complete** — Data tab shows full dataset; CSV download produces all columns and rows
- [ ] **Q9: Metadata validation passes** — `validate_metadata_completeness.py` reports 0 errors for this chapter's series
- [ ] **Q10: Startup validation** — `validate_app_data()` reports 0 errors related to this chapter's data

**D10c. Chart-Readiness Validation (bonus, adds up to 10% to D10)**

- [ ] Every empirical figure has a data resolution path (column map, chopped CSV, or hdarp_variables match)
- [ ] `hdarp_variables` in HDARP_SERIES_LINKAGE.json match actual `series_name` values in chapter CSVs
- [ ] `figure_column_map.json` entries exist for all figures using extended chapter data (supports flat JSON format)
- [ ] `figure_column_map.json` entries include extension column names (`S###-EXT`, `S###-F`) for extended series figures
- [ ] Year-range filtering does not clip data when metadata range predates available data
- [ ] `isTRUE()`/`!is.na()` guards present on all `if()` conditions using values from JSON metadata

**Scoring**: `(D10a score × 0.35 + D10b score × 0.55 + D10c score × 0.10)` where each sub-score = `(items passed / items total) × 100`

### D11. Test Coverage (7%)

- [ ] Processing scripts include validation checks against `validation.expected_range`
- [ ] Reference values exist in registry for key series (where available)
- [ ] Pipeline run log shows 0 failures for chapter series
- [ ] Overlap correlations documented for extended series (where applicable)
- [ ] Edge cases handled (missing years, NaN values)

**Scoring**: `(Validation checks passing / Total checks) × 100`

### D12. Documentation (12%)

When `ANU_LEDGER.json` exists, use its `coverage` percentages directly. Otherwise:

- [ ] All Tier 1 series have research JSON, decomposition, DPR
- [ ] All extended series have EPR
- [ ] All figures have FPR (`Technical/docs/figures/Fig#.#_FPR.md`)
- [ ] `series_registry.json` entries complete for all series
- [ ] `PIPELINE_STATE.json` updated with current stage status
- [ ] `PROGRESS_LOG.md` has session entries for the chapter work
- [ ] `.claude/instructions.md` Current Status section reflects chapter completion

**Scoring**: Average of Ledger coverage percentages, or `(Docs present / Docs required) × 100`

---

## Review Process

### Step 1: Gather Information

1. Read `series_registry.json` to identify all series and figures for the chapter
2. Classify series into Tier 1 (composite) and Tier 2 (input tables) based on `tier` field or presence of processing scripts
3. Read `ANU_LEDGER.json` for artifact coverage data
4. Read `PIPELINE_STATE.json` for stage completion status
5. Identify which series have extensions vs no extension

### Step 2: Run Dimension Checks

For each of the 12 dimensions:
1. Execute checklist items against the filesystem
2. Record pass/fail for each item
3. Calculate dimension score as a percentage
4. Note specific gaps with file paths

### Step 3: Calculate Overall Score

1. Apply v2.0 dimension weights (D1: 6%, D2: 5%, ... D12: 12%)
2. Sum weighted scores
3. Determine certification level (EXEMPLARY/COMPLETE/ADEQUATE/INCOMPLETE)

### Step 4: Generate Report

1. Populate REVIEW_REPORT template with dimension scores
2. List all gaps in GAP_ANALYSIS sorted by priority
3. Generate action items: HIGH (missing scripts/data), MEDIUM (missing docs), LOW (polish)
4. Compare to previous review score if available in PIPELINE_STATE

---

## Output Templates

### Review Report

See `templates/REVIEW_REPORT_TEMPLATE.md`

### Checklist

See `templates/CHECKLIST_TEMPLATE.md`

### Gap Analysis

See `templates/GAP_ANALYSIS_TEMPLATE.md`

---

## Integration with Other Anu Tools

The Anu Review complements:

- **`/anu-ingestion`** - Creates DPR/FPR documentation, series decompositions
- **`/anu-extension`** - Creates EPR documentation, defines extension methodology
- **`/anu-visualize`** - Defines visualization requirements (R Shiny + Plotly)
- **`/anu-ledger`** - Provides artifact coverage data for D12 Documentation scoring

### Recommended Workflow

1. Complete chapter integration work
2. Run `/anu-review [chapter]` to assess
3. Address gaps identified in report
4. Re-run review until COMPLETE or EXEMPLARY

---

## Example Review Output

```
=============================================================
                 ANU REVIEW REPORT: Chapter 7
=============================================================

Quick Reference:
  Chapter:           7
  Title:             The Theory of Real Competition
  Tier 1 Series:     S034-S038 (5 composites)
  Tier 2 Series:     S215-S217 (3 input tables)
  Figures:           8 (3 Salter + 5 time-series)
  Integration Score: 92%
  Status:            COMPLETE

Dimension Scores:
  D1  KB Completeness:       100%  ch07_real_competition.md
  D2  Absorption Quality:    100%  chapter_07_absorbed.csv (180 rows)
  D3  Research Coverage:     100%  5/5 research JSONs
  D4  Decomposition Coverage:100%  5/5 decompositions
  D5  DPR Completeness:      100%  5/5 DPRs
  D6  EPR Completeness:      N/A   No extensions (NAICS revisions)
  D7  Chopped Validation:    100%  5/5 valid Chopped CSVs
  D8  Replicator Scripts:    100%  L19-L21, P13-P17
  D9  Extenbook Quality:     100%  5/5 Extenbooks
  D10 Viz Integration:        60%  Figure CSVs present, Dash not integrated
  D11 Test Coverage:          80%  Validation ranges checked, no reference values
  D12 Documentation:          93%  Per ANU_LEDGER.json coverage

Gaps Identified:
  1. Viz app not yet rendering Ch7 figures (D10)
  2. No reference values for validation (D11)
  3. FPR for Fig7.10-7.12 could include Salter methodology detail

Action Items:
  [MED]  Integrate Ch7 data into ANU_VIZ Dash app
  [LOW]  Add reference values if Shaikh published specific figures
  [LOW]  Enhance Salter FPRs with cross-sectional methodology

=============================================================
```

---

## File Locations (Example: the reference project Project)

> **Note**: The paths below are from the the reference project project. Other projects will have the same structure under their own `Technical/` directory.

| Content | Location |
|---------|----------|
| DPR/EPR files | `Technical/docs/series/S###_DPR.md`, `S###_EPR.md` |
| Research JSONs | `Technical/research/S###_research.json` |
| Decompositions | `Technical/docs/series/S###_DECOMPOSITION.md` |
| Series registry | `Technical/series_registry.json` |
| Anu Ledger | `Technical/ANU_LEDGER.json` |
| Pipeline state | `Technical/PIPELINE_STATE.json` |
| Replicator scripts | `Technical/ANU_REPLICATOR/scripts/loading/`, `scripts/processing/` |
| Chapter CSVs | `Technical/ANU_REPLICATOR/data/final-data/shiny/chapter_NN.csv` |
| Figure CSVs | `Technical/ANU_REPLICATOR/data/final-data/figures/FigN.M.csv` |
| Extenbooks | `Technical/ANU_REPLICATOR/data/final-data/extenbooks/` |

---

## Integration with Anu Framework

| Skill | Reviewed Dimension |
|-------|-------------------|
| **Anu Research** | D3 Research Coverage |
| **Anu Ingestion** | D1, D2, D4, D5 |
| **Anu Extension** | D6 |
| **Anu Chopped** | D7 |
| **Anu Replicator** | D8 |
| **Anu Extenbook** | D9 |
| **Anu Visualize** | D10 |
| **Anu Pipeline** | Pipeline stage tracking |

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | Review reports (REVIEW_REPORT, GAP_ANALYSIS, CHECKLIST), `PIPELINE_STATE.json` anu_review section |
| **Expects** | `ANU_LEDGER.json` (for D12 coverage data), all artifacts from completed stages |
| **Must Update on Completion** | Update `PIPELINE_STATE.json` with review score and certification level |

The D12 Documentation dimension should reference the Ledger's `coverage` percentages when available, rather than manually counting artifacts.

---

## Anu Framework Context

- **Pipeline Stage**: 6 (AUDIT)
- **Upstream**: All prior stages must be complete
- **Downstream**: None (terminal stage) — outputs inform remediation cycle
- **Adequacy Relevance**: D0 gate validates that Stage 0 was run; D1-D12 audit built artifacts
- **Key Handoff**: Review reports, certification levels, gap analysis inform remediation

## Version History

- **v1.0** (January 2026) - Initial release (9 dimensions)
- **v1.1** (February 2026) - Added API Configuration dimension
- **v2.0** (March 2026) - 12 dimensions; added Research Coverage, Decomposition Coverage, Replicator Scripts; reweighted all dimensions
- **v3.0** (March 2026) - Full checklist rewrite: replaced 9 legacy R Shiny dimensions with 12 Anu Framework v6.0 dimensions; tier-aware scoring; updated review process to registry-driven workflow
- **v3.1** (March 2026) - Added D7-V10 (SUBSOURCE_METADATA.json column coverage); added D10 checks for SUBSOURCE_METADATA.json existence, construction_text completeness, and subsource field quality
- **v3.2** (March 2026) - Expanded D10 into D10a (Data Artifacts) and D10b (Application Quality Checklist) with 10-point viz quality assessment covering chart rendering, error-free operation, metadata exposition, extension visibility, and programmatic validation
- **v3.3** (March 2026) - Added D10c (Chart-Readiness Validation) with checks for data resolution paths, hdarp_variables matching, figure_column_map coverage, year-range safety, and NA guard requirements
- **v3.4** (March 2026) - Updated Q5 with extension column verification (both -EXT and -F columns in chopped CSVs); added D10c check for extension columns in figure_column_map.json; documented flat JSON support for figure_column_map
- **v3.5** (March 2026) - Generalized: labeled the reference project file locations as example; fixed Plotly Dash references to R Shiny + Plotly
- **v3.6** (March 2026) - Added Q5b (Component data visible) for ratio/rate series with Concurrent Series (CS) architecture: checks CS columns in chopped CSV, `is_component` entries in SUBSOURCE_METADATA, and "Show Components" dual-axis rendering
- **v3.7** (March 2026) - Minor refinements
- **v4.0** (April 2026) - Added D0 v6.0 gate check: validation phase completeness (V01-V08), decision log presence (<decision-ref>), assumptions documentation (ASM-D/M/R), provenance index quality (by_source/by_api/by_series), manual adjustment manifest verification
- **v4.1** (May 2026) - Formalized **D14 Outward-Facing Intelligibility** as a gate (introduced ad-hoc in the the reference project Session 28-30 reviews): audits externally-distributed artifacts for undefined internal jargon across the three distribution channels (anu-publish, anu-drive, anu-archive). Clarified that D1–D12 are the weighted dimensions (sum 100%) and D13/D14 are gates scored separately. Refreshed skill cross-references to Anu Framework v10.0.

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.
- [`DATA_PROVENANCE_STANDARDS.md`](../../docs/DATA_PROVENANCE_STANDARDS.md) — DPR / EPR / FPR / VPR record specs.

---

*Part of the Anu Framework v11.0 — Integration Quality Audit Framework*
