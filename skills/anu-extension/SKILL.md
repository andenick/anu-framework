---
name: anu-extension
version: "3.5"
description: Framework for maximally faithful data series extension with live API data. Extension methodology is defined here; implementation lives in Anu Replicator P## processing scripts. v3.5 integrates with the central `DIVERGENCE_REGISTER.json` (via `_shared/divergences.py`) so extension-time divergences are visible to anu-review D13 alongside ingestion and manual-adjustment divergences. EPRs are authored per-series by the agent (no batch automation — each EPR documents a substantive methodology decision).
when-to-use: User needs to extend historical data series with modern API data from FRED, BEA, BLS, or other sources; scaffold a cohort of EPRs in batch; or log an extension-phase divergence to the project register.
search-hints: extension extend series api fred bea bls modern data update batch epr cohort divergence splice
argument-hint: [action] [series_id]
allowed-tools: Read, Write, Grep, Glob, LS, WebSearch, Shell
requires: anu-ingestion, anu-research
part-of: Anu Framework v11.0
---

# Anu Extension Standard v3.5: Maximum Faithfulness Data Extension Framework

A rigorous framework for extending economic data series with complete fidelity to original construction methodology. Every extension must be traceable, documented, and validated.

---

## Core Philosophy

The Anu Extension Standard ensures that extended data is **EXACTLY** what would have been produced if the original methodology were applied to new data. This requires:

1. **Complete Understanding** - Know exactly what data was used originally
2. **Methodology Fidelity** - Apply identical transformations
3. **Source Verification** - Confirm data sources match
4. **Transition Validation** - Verify seamless connection at splice points
5. **External Replicability** - All data MUST come from public APIs (FRED, BEA, etc.) that any researcher can access. NEVER reference internal databases, proprietary tools, or non-public data sources. Every data point must be traceable to a public URL.

---

## Outputs

This skill produces five concrete artifacts. Every extension session yields these — vague "extended data file" is not a valid artifact label.

| # | Artifact | Path | Format | Mandatory fields / contents | Downstream consumer |
|---|---|---|---|---|---|
| 1 | **EPR — Extension Provenance Record** | `{Project}/Technical/docs/series/S###_EPR.md` | Markdown | Series ID, Original Range, Extension Range, API/Source, Concept Match Justification, Splice Method, Splice Year, Faithfulness Assessment, Known Divergences, Reference Values. Full spec in `docs/DATA_PROVENANCE_STANDARDS.md`. A **No-Extension EPR** documents a deliberate non-extension decision. | `anu-review` (D6 scoring), methodology PDF generator |
| 2 | **EXTENSION_LOG.json** | `{Project}/Technical/ANU_REPLICATOR/data/final-data/logs/EXTENSION_LOG.json` | JSON | Per-series object keyed by `S###`: `{api, api_series_id, splice_year, splice_method, faithfulness, run_timestamp, source_url, divergence_ids}`. | `anu-ledger` (artifact coverage), `anu-publish` (scrub check) |
| 3 | **Updated `series_registry.json` extension block** | `{Project}/Technical/series_registry.json` (canonical) and `{Project}/Technical/ANU_REPLICATOR/config/series_registry.json` (mirror) | JSON | Per-series `extension` object: `{api, api_series_id, splice_year, splice_method, units_match, reference_values}`. Must be `null` for non-extendable series (cross-sectional, theoretical, derived). | Replicator P## scripts, validation suite |
| 4 | **Extended subseries data** | `{Project}/Technical/ANU_REPLICATOR/data/raw-data/api/` and `data/final-data/chopped/` | JSON cache + CSV columns | Cached API response (one file per fetch); the extended subseries appear as `S###-EXT`, `S###-COMBINED`, and where applicable `S###-F` columns in the chopped CSV. | `anu-chopped`, `anu-extenbook`, `anu-visualize` |
| 5 | **Divergence Register entries** | `{Project}/Technical/docs/DIVERGENCE_REGISTER.json` | JSON | Per-divergence: `{adr_id, series_id, category, description, impact, resolution_status, resolution_date}`. Created when a methodology divergence is discovered during extension. | `anu-review` (D6 + D13), human decision log |

**Sync requirement.** When `series_registry.json` is updated, the canonical copy at `{Project}/Technical/series_registry.json` and the replicator mirror at `{Project}/Technical/ANU_REPLICATOR/config/series_registry.json` must remain identical. The `anu-extension` skill is responsible for keeping both in sync at the end of every session.

**Pre-publication.** Before `anu-publish` ships, every series with `extension` ≠ `null` MUST have a corresponding EPR file. `anu-ledger` enforces this with a `missing_epr` action item.

See `docs/DATA_PROVENANCE_STANDARDS.md` for full EPR field definitions, Concept Match Justification guidance (with positive and negative examples), and the No-Extension EPR pattern.

---

## Ten Principles of Extension Faithfulness

1. **UNDERSTAND BEFORE EXTENDING** - Read all source documentation (HDARP extracts)
2. **DOCUMENT AGENT REASONING** - Write detailed explanation of understanding
3. **SOURCE MATCH VERIFICATION** - Confirm original and extension sources are identical
4. **METHODOLOGY COMPARISON** - Quote old vs new methodology documentation
5. **BOOK CONTEXT INTEGRATION** - Include source quotes from chapters and appendices
6. **TRANSFORMATION REPLICATION** - Apply exact same transformations
7. **TRANSITION ANALYSIS** - Validate splice points with statistical tests
8. **VINTAGE TRACKING** - Record all data vintage dates
9. **QUOTE EVERYTHING** - Include actual quotes from all documentation
10. **FAIL ON UNCERTAINTY** - Stop if methodology unclear, do not guess. Stop if data is unavailable, do not fabricate.
11. **NO SYNTHETIC PLACEHOLDERS** - Never generate fake annual data from summary statistics. If a paper reports "mean = X, range Y-Z" but doesn't publish annual values, the series status is `data_unavailable` until real data is obtained. Acceptable alternatives: digitize from published figures, fetch from statistical agency APIs, or request from authors. `np.random` in a data construction script is always wrong.

---

## Prerequisites

Before using this skill, ensure:

1. **Anu Ingestion Documentation Exists**
   - DPR file for the series (`S###_DPR.md`)
   - Series registered in `series_registry.json`

2. **HDARP Extractions Available**
   - Book chapters and appendices (full text)
   - Original methodology PDFs (BEA, BLS, etc.)
   - Current methodology PDFs
   - All source quotes must come from HDARP extractions
   - **NO DIRECT PDF READING** - All content via HDARP

3. **Transition Analysis Capability**
   - Access to `transition_analysis.py` or equivalent
   - Historical baseline data for comparison

4. **Adequacy L3 Check**: Extension sources should match those identified in `ADEQUACY_REPORT.json` Layer 3 (Data Availability). If the adequacy report flagged missing API sources, extension may be blocked for those series.

---

## Commands

### Planning Commands

```
/anu-extension plan [series_id]
```
Create comprehensive extension plan for a series. Outputs:
- Prerequisite checklist
- Source identification
- Methodology comparison plan
- Transformation replication plan
- Validation test plan

```
/anu-extension understand [series_id]
```
Document agent's understanding of the series. Outputs:
- What the data represents
- Original source documentation
- How it was constructed
- What figures use this data
- Relevant book quotes

### Research Commands

```
/anu-extension compare-methodology [series_id]
```
Compare original vs current methodology. Outputs:
- Old methodology quotes (from HDARP extractions)
- Current methodology quotes (from HDARP extractions)
- Web research findings on methodology changes
- Impact assessment

```
/anu-extension book-context [series_id]
```
Extract all relevant book context. Outputs:
- Chapter references with quotes
- Appendix references with quotes
- Variable definitions
- Formulas
- Figure usage

### Execution Commands

```
/anu-extension extend [series_id]
```
Execute the extension with full documentation. Outputs:
- Extended data file
- TRANSFORMATION_LOG entries
- Intermediate validation results

```
/anu-extension transition-analysis [series_id]
```
Run transition analysis at splice points. Outputs:
- Overlap period metrics
- Connection ratio
- Growth rate continuity
- Trend alignment
- Transition visualization reference

### Validation Commands

```
/anu-extension validate [series_id]
```
Run full validation suite. Outputs:
- Range validation results
- Cross-reference validation
- Automated test results
- Issue identification

```
/anu-extension certify [series_id]
```
Generate final certification. Outputs:
- Faithfulness score calculation
- EPR file generation
- EXTENSION_LOG.json entry
- DPR update with extension info

### Divergence Tracking Commands

```
/anu-extension log-divergence [series_id]
```
Document a methodology divergence discovered during extension. Outputs:
- New entry in DIVERGENCE_REGISTER.json
- ADR-### identifier assigned
- Linked to affected EPR files

```
/anu-extension list-divergences
```
Show all divergences in the project. Outputs:
- Summary of pending decisions
- Resolved divergences
- Statistics by category

```
/anu-extension resolve-divergence [ADR-###]
```
Record resolution decision for a divergence. Outputs:
- Updated DIVERGENCE_REGISTER.json
- Updated EPR files with resolution
- Decision documentation

---

## 10-Step Extension Workflow (with Divergence Tracking)

### Step 1: Prerequisite Check

Before any extension work:

- [ ] Verify DPR exists for series
- [ ] Verify HDARP extractions exist for book content
- [ ] Verify HDARP extractions exist for methodology PDFs
- [ ] If missing, document what is needed and STOP

**Output**: Prerequisite status report

### Step 2: Agent Understanding Document

Agent writes comprehensive explanation answering:

1. **What do I think this data is?**
   - Economic meaning and significance
   - How it fits in broader analysis

2. **What was the original data source?**
   - Exact source name, table, and line items
   - Time period covered
   - Units and frequency

3. **How was it constructed?**
   - Step-by-step transformation chain
   - Any splicing or adjustments

4. **What figures use this data?**
   - List all figures referencing this series
   - How series appears in each figure

5. **What does the source say about it?**
   - Relevant quotes from chapters
   - Relevant quotes from appendices

**Output**: Understanding statement in EPR file

### Step 3: Book Context Extraction

From HDARP book extractions, gather:

| Content | Source | Purpose |
|---------|--------|---------|
| Chapter quotes | `Inputs/Robert/KB/ch##_topic.md` | Context and interpretation |
| Appendix quotes | `Inputs/Robert/KB/ch18_appendices.md` | Methodology details |
| Variable definitions | `Inputs/Robert/KB/appendix_methodology_summary.json` | Exact formulas |
| Formulas | `series_registry.json` construction steps | Transformation specifications |
| Figure usage | `series_registry.json` figures field | Visual representation |

**Output**: Book Context section in EPR file

### Step 4: Original Methodology Documentation

From HDARP methodology extractions:

1. **Identify Original Vintage**
   - Find methodology documentation from original data period
   - Example: BEA 2011 vintage for the author's original data

2. **Extract Key Quotes**
   - Definition of series/table
   - Calculation methodology
   - Any special procedures

3. **Document Original Formulas**
   - Mathematical expressions
   - Variable definitions
   - Units and base years

**Source Location**: `Inputs/Robert/KB/` (project Knowledge Base files)

**Output**: Original Methodology section in EPR file

### Step 5: Current Methodology Research

1. **Read Current HDARP Methodology Extractions**
   - Find latest methodology documentation
   - Example: BEA 2024 methodology

2. **Web Search for Changes**
   - Search for comprehensive revisions
   - Search for methodology updates
   - Document findings with URLs and dates

3. **Compare Old vs New**
   - Create side-by-side comparison
   - Quote both old and new methodology
   - Assess impact: HIGH / MEDIUM / LOW / NONE

**Output**: Current Methodology and Methodology Comparison sections in EPR file

### Step 5.5: Divergence Check (NEW)

After completing methodology research, assess whether any divergences require logging:

1. **Identify Divergences**
   - Did the source agency change their methodology?
   - Are there coverage, classification, or definition changes?
   - Is there a discontinuity that cannot be explained?

2. **Assess Significance**
   - Quantify the impact if possible (level discontinuity, %)
   - Determine if it affects the theoretical analysis
   - Consider if the original author was aware of this

3. **Log if Necessary**
   - If divergence is significant (>5% impact or methodological break):
     - Create entry in `DIVERGENCE_REGISTER.json`
     - Assign ADR-### identifier
     - Document options for resolution
   - If minor (<5% impact, same core methodology):
     - Note in EPR but do not log as formal divergence

4. **Continue Extension**
   - Divergences do NOT block extension
   - Extensions proceed with "CERTIFIED WITH NOTES" status
   - Decisions are made at end of chapter/project

**Divergence Categories**:
- `source_methodology_change` - Agency changed calculation/collection
- `coverage_change` - What's included/excluded changed
- `classification_change` - Industry/sector classification updated
- `base_year_change` - Reference period shifted
- `discontinuity` - Data break with no documented cause
- `definition_change` - Conceptual change in what's measured

**Output**: Entry in DIVERGENCE_REGISTER.json (if applicable), note in EPR file

### Step 6: Transformation Replication Plan

1. **List All Original Transformations**
   - From DPR transformation chain
   - From appendix methodology
   - From TRANSFORMATION_LOG.json

2. **Identify Equivalent Current Operations**
   - Map each original transform to current equivalent
   - Note any that differ

3. **Flag Non-Replicable Items**
   - Document any transformations that cannot be exactly replicated
   - Explain why and propose alternatives

4. **Document Rationale**
   - Justify each transformation choice
   - Reference methodology documentation

**Output**: Transformation Replication Plan in EPR file

### Step 7: Extension Execution

1. **Fetch New Data**
   - Use documented API endpoints
   - Record download timestamp and vintage date
   - Save raw data file

2. **Apply Transformations**
   - Execute each transformation from plan
   - Log in TRANSFORMATION_LOG.json
   - Use Transform IDs: T101, T102, ... for extensions

3. **Intermediate Validation**
   - Check value ranges at each step
   - Verify units and base years
   - Document any issues

**Output**: Extended data file, TRANSFORMATION_LOG entries

### Step 8: Transition Analysis

Run comprehensive transition analysis:

1. **Calculate Overlap Period Metrics**
   ```
   Connection Ratio = Extension_Value(overlap_start) / Original_Value(overlap_start)
   Target: 0.95 - 1.05
   ```

2. **Growth Rate Continuity**
   ```
   Growth_Difference = |Extension_Growth - Original_Growth| at transition
   Target: < 5%
   ```

3. **Trend Alignment**
   ```
   Correlation of original and extension in overlap period
   Target: > 0.95
   ```

4. **Level Difference**
   ```
   Percent difference at transition point
   Target: < 3%
   ```

5. **Generate Transition Plot**
   - Original series
   - Extended series
   - Overlap period highlighted

**Classification**:
- SEAMLESS: All metrics pass
- ACCEPTABLE: Minor deviations, documented
- PROBLEMATIC: Significant deviations, requires review
- FAILED: Cannot proceed, methodology mismatch

**Output**: Transition Analysis section in EPR file

### Step 9: Validation Suite

1. **Range Validation**
   - Check min/max against expected bounds
   - Flag outliers

2. **Cross-Reference Validation**
   - Compare to related series
   - Check correlations match historical patterns

3. **Automated Tests**
   - Run test suite for series
   - Document all results

4. **Documentation Completeness**
   - All EPR sections filled
   - All quotes documented
   - All transformations logged

**Output**: Validation Results section in EPR file

### Step 10: Certification

1. **Calculate Faithfulness Score**
   ```
   Faithfulness Score = 
     (Methodology_Match × 30%) +
     (Source_Match × 20%) +
     (Transformation_Replication × 20%) +
     (Transition_Quality × 20%) +
     (Documentation_Completeness × 10%)
   ```

2. **Determine Certification Status**
   - CERTIFIED: Score >= 90%, all criteria met
   - CERTIFIED WITH NOTES: Score >= 75%, documented deviations
   - NOT CERTIFIED: Score < 75% or critical failures

3. **Generate EPR File**
   - Complete all sections
   - Include all quotes and references
   - Sign with agent info

4. **Update Extension Log**
   - Add entry to EXTENSION_LOG.json
   - Link to EPR file

5. **Update DPR**
   - Add extension information to original DPR
   - Cross-reference EPR file

**Output**: Complete EPR file, EXTENSION_LOG entry, updated DPR

---

## Output Files

### Extension Provenance Record (EPR)

File naming: `[SERIES_ID]_EPR.md`
Location: Same as DPR files (e.g., `docs/series/S001_EPR.md`)

Template: `templates/EPR_TEMPLATE.md`

### Extension Log

File: `EXTENSION_LOG.json`
Location: With TRANSFORMATION_LOG.json

Schema:
```json
{
  "anu_extension_version": "1.0",
  "project": "[Project Name]",
  "extensions": [
    {
      "extension_id": "EXT001",
      "series_id": "S001",
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
      "agent": "[model-name]",
      "session": "[session-id]",
      "original_period": "YYYY-YYYY",
      "extension_period": "YYYY-YYYY",
      "methodology_match": true,
      "transition_status": "SEAMLESS",
      "faithfulness_score": 98,
      "certification": "CERTIFIED",
      "epr_file": "path/to/EPR.md",
      "transform_ids": ["T101", "T102"],
      "validation_result": "PASS",
      "notes": ""
    }
  ]
}
```

---

## Integration with Other Standards

### With Anu Ingestion

- EPR files complement DPR files (both in `Technical/docs/series/`)
- Share series identity conventions (S### with dash notation)
- Extension config lives in `series_registry.json` under each series
- Reference same `series_registry.json` for all metadata

### With Knowledge Base

- All quotes sourced from KB files (`Inputs/Robert/KB/`)
- KB files are HDARP extractions synthesized into structured markdown
- Reference KB file paths in EPR methodology comparison sections

### With Transition Analysis

- Splice validation metrics computed in P## processing scripts
- Transition analysis documented in EPR file
- Overlap correlations recorded in registry `validation` block

---

## API Data Integration (v1.1)

The Anu Extension Standard supports live API data pulls for extending series with current data. This ensures reproducibility and automated updates.

### API Infrastructure

**Fetcher Utilities** (located in `Technical/scripts/tools/`):
- `fred_fetcher.py` - FRED API integration with caching
- `bea_fetcher.py` - BEA API integration with caching
- `unified_fetcher.py` - Routes requests to appropriate source

**API Key Management**:
- All keys stored in project-local config: `Technical/ANU_REPLICATOR/config/api_keys.env`
- Load via `api_config.py` - NEVER hardcode API keys
- Available keys: FRED_API_KEY, BEA_API_KEY
- NEVER use internal database tools (e.g., Robin) as intermediaries for API data

### Extension Implementation

In Anu Framework v11.0, extension logic is implemented inside **Anu Replicator P## processing scripts**, not in standalone extension scripts. The `series_registry.json` `extension` field defines the API source, splice method, and target end year. The P## script reads this config and executes the extension as part of the processing phase.

### Year-Source Attribution

Every data point must be attributed to its source. The Year-Source Matrix is documented in each series' DPR:

| Year Range | Subsource | Source Name | API Endpoint | Notes |
|------------|-----------|-------------|--------------|-------|
| `start`-`splice_year` | S{NNN}-A..D | Original subsources | None | From chopped table or author's data |
| `splice_year`-`end` | S{NNN}-EXT | API source (raw) | `API:SERIES_ID` | Raw API data in native units |
| `splice_year`-`end` | S{NNN}-F | API source (re-indexed) | `API:SERIES_ID` | Re-indexed to overlap previous subsource at splice year |

**Example (the reference project, S001 — US Industrial Production Index):**

| Year Range | Subsource | Source Name | API Endpoint | Notes |
|------------|-----------|-------------|--------------|-------|
| 1860-1918 | S001-A | Historical Statistics | None | From chopped table |
| 1919-2010 | S001-D | Original (reindexed) | None | Baseline data |
| 2011-2025 | S001-EXT | FRED (raw) | FRED:INDPRO | Raw API data in native units |
| 2011-2025 | S001-F | FRED (re-indexed) | FRED:INDPRO | Re-indexed to overlap S001-D at splice year |

### API Data Cache Location

All API-fetched data MUST be cached in the project's `Inputs/API/` directory:
- `Inputs/API/FRED/` - FRED API data (one CSV per series, e.g., `INDPRO.csv`)
- `Inputs/API/BEA/` - BEA API data
- NEVER use `<private data source>` or any internal database path for API data
- Cache files use format: `year,SERIES_ID` (CSV with annual averages)

### API Provenance Requirements

Every extension using API data must document:

1. **API Endpoint** - Full specification (e.g., "FRED:GDPC1", "BEA:FixedAssets:FAAt301ESI")
2. **Source URL** - Public webpage for the data (e.g., `https://fred.stlouisfed.org/series/GDPC1`)
3. **Fetch Timestamp** - When data was retrieved (ISO 8601)
4. **Data Vintage** - Publication date of the data
5. **Parameters** - Any transform parameters (e.g., frequency conversion)
6. **Response Hash** - SHA256 of raw response for verification

### Live Pull Workflow

1. **Load API Configuration**
   ```python
   from api_config import get_api_key
   from tools.unified_fetcher import UnifiedDataFetcher
   fetcher = UnifiedDataFetcher()
   ```

2. **Fetch Extension Data**
   ```python
   df = fetcher.get_series("FRED:INDPRO", start_year=2011, end_year=2025)
   ```

3. **Record Provenance**
   - Log fetch timestamp
   - Record data vintage
   - Store raw response in cache

4. **Apply Transformations**
   - Use same methodology as original
   - Document any deviations

5. **Splice with Baseline**
   - Apply documented splice method
   - Run transition analysis

### API Commands

```
/anu-extension generate-script [series_id]
```
Generate an extension script for a series. Outputs:
- `extend_S###.py` with complete configuration
- All subsources identified
- API endpoints configured
- Transformation chain defined

```
/anu-extension fetch-live [series_id]
```
Execute live API pull for a series. Outputs:
- Fresh data from configured APIs
- Updated cache files
- Fetch provenance log

```
/anu-extension validate-api [series_id]
```
Validate API configuration for a series. Checks:
- API keys available in project config (`api_keys.env`)
- Endpoints accessible
- Data format matches expected
- Year coverage is complete

```
/anu-extension run-script [series_id]
```
Execute the extension script for a series. Outputs:
- Reconstructed series from subsources
- Extended data with live API data
- Updated EPR file
- Transition analysis results

### Subsource Types

| Type | API | Source Location |
|------|-----|-----------------|
| `historical` | None | `Inputs/[ChoppedSource]/ch##/*.csv` |
| `original` | None | `data/raw-data/parsed/S###_parsed.csv` |
| `fred` | FRED:SERIES_ID | FRED API |
| `bea_nipa` | BEA:NIPA:TABLE | BEA API |
| `bea_fixed_assets` | BEA:FixedAssets:TABLE | BEA API |
| `bea_gdp_industry` | BEA:GDPbyIndustry:TABLE | BEA API |
| `calculated` | None | Derived from other series |
| `component` | None | Level-data input of a ratio/rate (CS columns) |

### Concurrent Series (CS) and Extensions

CS component columns (e.g., `CS026-N`, `CS026-D`) represent the level-data inputs of ratio/rate series. Important extension rules:

- **CS columns are NOT independently extended.** When extending a ratio series, extend the **ratio itself** (producing `S###-EXT` and `S###-F` columns), not the individual CS numerator/denominator components.
- CS components inherit their time range from the Tier 2 source tables. If a Tier 2 table is extended, the CS column will naturally pick up the extended data on the next P## processing run.
- CS columns have `is_component: true` in `SUBSOURCE_METADATA.json` and are excluded from standard extension views. They appear only in the "Show Components" view mode.
- When documenting extension methodology in EPRs, note that the extended ratio may diverge from the ratio of independently extended components due to vintage differences or methodology changes in the numerator/denominator.

### Integration with Series Registry

The `series_registry.json` maps project series IDs to API sources:

```json
{
  "S001": {
    "name": "Industrial Production Index",
    "source": "FRED",
    "series_id": "INDPRO",
    "transform": "annual_average"
  }
}
```

---

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `EXT_NO_DPR` | No DPR exists for series | Create DPR first using anu-ingestion |
| `EXT_NO_HDARP` | HDARP extractions missing | Run HDARP on required documents |
| `EXT_METHODOLOGY_MISMATCH` | Cannot match methodology | Document difference, seek review |
| `EXT_TRANSITION_FAILED` | Transition analysis failed | Investigate data quality, methodology |
| `EXT_VALIDATION_FAILED` | Validation tests failed | Review extension, fix issues |
| `EXT_UNCERTAINTY` | Methodology unclear | Stop, do not guess, seek clarification |

---

## Templates

Available in `templates/`:

| Template | Purpose |
|----------|---------|
| `EPR_TEMPLATE.md` | Extension Provenance Record |
| `TRANSITION_ANALYSIS_TEMPLATE.md` | Transition analysis report |
| `METHODOLOGY_COMPARISON_TEMPLATE.md` | Old vs new methodology |
| `EXTENSION_CERTIFICATION_TEMPLATE.md` | Final certification |
| `EXTENSION_SCRIPT_TEMPLATE.py` | Per-series extension script template |

---

## Reference Implementation

Use the project's own reference chapter (typically the first fully completed chapter) for reference. Key artifacts:
- `Technical/docs/series/S###_EPR.md` - EPR files
- `Technical/ANU_REPLICATOR/scripts/processing/P##_*.py` - Extension logic in processing scripts
- `series_registry.json` extension config per series

---

## v2.0 Changes: Replicator Integration

In Anu Framework v11.0, extension logic is **implemented inside Anu Replicator P## processing scripts**. This skill defines the *methodology* for faithful extension; the Replicator implements it in code.

Key changes:
- Extension config now lives in `series_registry.json` under each series' `extension` field
- Per-series extension scripts replaced by P## processing scripts
- Prerequisites updated: requires Anu Ingestion v3.0 and Anu Research v1.0
- EPRs reference research.json entries for methodology comparison
- Uses dash notation for series IDs (S001-EXT, not S001_EXT)
- **Dual extension columns**: Every extended series produces two columns in chopped CSVs:
  - `S###-EXT` (role: `extension_raw`) — raw API data in native units from the splice year onward
  - `S###-F` (role: `extension_reindexed`) — API data re-indexed to match the previous subsource at the splice point
  - Re-indexing formula: `S###-F[t] = prev_subsource[splice_year] * (API[t] / API[splice_year])`
- **Automatic subsource registration**: A project-specific generator script reads `series_registry.json` extension blocks and auto-generates `SUBSOURCE_METADATA.json` entries with `is_extension: true` for both `-EXT` and `-F` columns

## Visualization Requirements

Extension data MUST be visible in the Shiny/Plotly visualization app:

1. **Separate Trace**: Every extension subsource (where `is_extension == true`) must appear as its own chart trace, not silently merged into the final composite series.
2. **Distinct Labeling**: Extension traces must have descriptive labels showing the API source and time range (e.g., "FRED INDPRO Extension [2011–2025]").
3. **Extension View Mode**: The app's "Final Extension" view mode must filter to only extension subsources. If no extension subsources have `is_extension == true`, the view should display an informational message rather than silently showing all data.
4. **All Sources View**: The "All Sources" view must include extension traces alongside original subsources so users can see the complete construction.
5. **Splice Point Visibility**: Where an extension splices with original data, the overlap or transition should be visually apparent (both traces visible in the overlap period).

6. **Chart-Readiness**: Extension subsources must have entries in the project's `SUBSOURCE_METADATA.json` and corresponding columns in chopped CSVs so the visualization app's data resolution path can find and display them.
7. **Column Map Coverage**: When extension data is part of an extended chapter CSV, the corresponding `figure_column_map.json` entry must include the extension column names.
8. **Source URL Links**: Every extension subsource entry in `SUBSOURCE_METADATA.json` MUST include a `source_url` field linking to the public data source page (e.g., `https://fred.stlouisfed.org/series/INDPRO`). The visualization app renders these as clickable links so users can verify data at the source.

These requirements are validated by the Anu Review D10b quality checklist item Q5 (Extension data visible), D10c chart-readiness checks, and Q7 (Trace labels descriptive).

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Ingestion** | Prerequisite — registry and DPRs must exist |
| **Anu Research** | Prerequisite — research.json provides methodology context |
| **Anu Replicator** | P## scripts implement extension logic defined here |
| **Anu Chopped** | Extended series written to Chopped format |
| **Anu Extenbook** | Extension columns visible in Extenbook |
| **Anu Visualize** | Extension traces must be visible as separate chart traces (see Visualization Requirements) |
| **Anu Review** | D6 EPR Completeness dimension; D10b Q5 validates extension visibility |

## Anu Framework Context

- **Pipeline Stage**: 3 (EXTENSION)
- **Upstream**: Stage 2 Ingestion
- **Downstream**: Stage 4 Replication
- **Adequacy Relevance**: L3 (Data Availability) — extension requires the API/data sources L3 verified
- **Key Handoff**: Creates EPRs consumed by Extenbook, Review; updates series_registry.json extension config

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-28 | Initial Anu Extension Standard |
| 1.1 | 2026-02-03 | API Data Integration: live pulls, per-series scripts, year-source attribution |
| 2.0 | 2026-03-07 | Replicator integration, registry-driven config, Research prerequisite, dash notation |
| 2.1 | 2026-03-08 | Removed legacy paths (Knowledge_Base/, DEFINITIVE_SERIES_CATALOG.json, per-series extension scripts); updated KB paths to Inputs/Robert/KB/; fixed "Anu Standard" references to "Anu Ingestion" |
| 2.2 | 2026-03-12 | Added Visualization Requirements section: extension subsources must appear as separate chart traces; cross-referenced with Anu Review D10b Q5 and Anu Visualize quality checklist |
| 2.3 | 2026-03-12 | Added chart-readiness and column map coverage to visualization requirements; cross-referenced with Anu Review D10c |
| 2.4 | 2026-03-15 | Added dual extension column convention (S###-EXT raw + S###-F re-indexed), re-indexing formula, automatic subsource registration via generate_shiny_subsources.py, updated Year-Source Attribution table |
| 3.0 | 2026-03-15 | Generalized: replaced project-specific hardcoding with placeholders; added generic Year-Source template; renamed shaikh_original to original; labeled the reference project examples |
| 3.1 | 2026-03-15 | Added Concurrent Series (CS) extension rules: CS columns are NOT independently extended; component subsource type; CS/extension interaction documented |
| 3.2 | 2026-03-16 | External replicability: removed Robin references; API data cached in Inputs/API/FRED/; added source_url requirement for subsource metadata; added API Data Cache Location section |
| 3.3 | 2026-04-07 | Version bump for Anu Framework v11.0 alignment (format unchanged) |
| 3.4 | 2026-05-13 | Outputs section tightened to enumerate five concrete artifacts (EPR, EXTENSION_LOG.json, registry block, extended subseries, Divergence Register) |
| 3.5 | 2026-05-15 | Integrated with the central `DIVERGENCE_REGISTER.json` (via `_shared/divergences.py`) so extension-time divergences are visible to `anu-review` D13 alongside ingestion and manual-adjustment divergences. The `batch-create-epr` idea was considered and rejected: EPRs are content-heavy documents (each documents a methodology choice, splice rationale, and concept-match justification) that benefit from per-series authoring; batch templating would produce uniform-looking shells that hide the methodology decisions. |

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `S###_EPR.md`, `EXTENSION_LOG.json`, `DIVERGENCE_REGISTER.json` entries |
| **Expects** | `S###_DPR.md` (from anu-ingestion), `series_registry.json` with extension config, `S###_research.json` |
| **Must Update on Completion** | Update `series_registry.json` extension config if methodology changed. Regenerate Ledger (`/anu-ledger generate`) |

**Note**: The canonical source for all series metadata is `series_registry.json`. Extension config, subsource mapping, and splice methodology all live in the registry.

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.
- [`DATA_PROVENANCE_STANDARDS.md`](../../docs/DATA_PROVENANCE_STANDARDS.md) — DPR / EPR / FPR / VPR record specs.

---

*Part of the Anu Framework v11.0 — Maximum Faithfulness Data Extension*
