---
name: anu-ingestion
version: "4.1"
description: Comprehensive data intake standard covering Knowledge Base construction, data import, absorption into a definitive internal format, series decomposition, and provenance documentation. v4.1 documents an agent-executed **migrate-scheme procedure** for cross-project ID remapping and codifies the standardized series-status taxonomy as a validated enum. DPRs are authored per-series by the agent (no batch automation — each DPR documents a substantive construction decision). Replaces anu-standard v2.2.
when-to-use: User needs to set up a data project, import raw data, build series_registry.json, decompose series, document provenance, migrate an ID scheme across an existing project, or scaffold a cohort of DPRs in one batch.
search-hints: ingestion import data series registry decompose provenance knowledge base dpr migrate scheme batch cohort taxonomy status enum
argument-hint: [action] [target]
allowed-tools: Read, Write, Grep, Glob, LS, Shell
requires: anu-research
part-of: Anu Framework v11.0
---

# Anu Ingestion Standard v4.1

The comprehensive data intake standard for the Anu Framework. Covers the full path from raw sources to a structured, documented, agent-ready data project. Replaces the former "Anu Standard" with expanded scope covering Knowledge Base construction, data absorption, and series decomposition.

---

## Seven Sub-Processes

1. **Knowledge Base Construction** — Build a searchable KB from HDARP extractions
2. **Data Import** — Bring raw data files into the project's `Inputs/` structure
3. **Data Absorption** — Transform diverse formats into a single definitive internal database
4. **Series Decomposition** — Document how each series is built from sub-components
5. **Provenance Documentation** — Create DPRs and FPRs for every series and figure
6. **Content Type Classification** — Classify data as tables, equations, figures, or body text
7. **Identity Systems** — Assign and manage series IDs per the Series ID Specification v2.0
8. **Source Authenticity Verification** — Before ingesting any data, verify it comes from an authentic source:
   - HDARP table extraction: acceptable (primary)
   - API response from official statistical agency: acceptable (primary)
   - Digitized from published figure: acceptable (secondary, document precision)
   - Computed from primary data using documented methodology: acceptable (derived)
   - Generated from summary statistics with random noise: **REJECTED**
   - Linear/log-linear trend estimated from reported range: **REJECTED**
   - Any `np.random` call in a data construction script: **REJECTED**

---

## Series ID Specification v2.1

### Canonical prefix scheme

The framework defines two canonical prefixes — `D` and `AD` — chosen to avoid collision with the eight `anu-architecture` phase prefixes (S/L/P/V/M/A/O/E). Every project declares them in `series_registry.json`'s top-level `prefix_scheme` block:

```json
"prefix_scheme": {
  "primary":    "D",
  "additional": "AD"
}
```

| Prefix | Meaning | Example |
|---|---|---|
| **`D`** | **Data Series** — series from the book or study being replicated | `D001`, `D042` |
| **`AD`** | **Additional Data Series** — everything else: series from other studies, derivative analytical series, comparison datasets, theoretical-construct series | `AD1001`, `AD2001` |

A single conceptual frame ("data series, some additional") with two prefixes. `anu-doctor` P12 validates conformance.

### Why not `S` for series?

Earlier versions used `S` and `ES`. Those collide with `anu-architecture`'s `S##` Setup-phase scripts (e.g., `S00_run_all.py`, `S01_install_packages.py`). The agent reading a project couldn't distinguish a series ID from a setup script at a glance. `D` is collision-free and reads as "Data" — the actual subject. `AD` extends naturally.

### Project-optional extensions

Projects may extend the scheme with additional prefixes when their data genuinely requires a third category — but this should be rare. If a project extends, the agent documents the extension in `MIGRATION/PREFIX_SCHEME.md` (template provided by `anu-rebuild`) with one-line justification per extension prefix. `anu-doctor` P12 validates that every series ID's prefix is either canonical (D, AD) or listed in the project's declared extension set.

### Format: `{PREFIX}{NNN}[-{LETTER}][_suffix]`

| Pattern | Meaning | Example |
|---------|---------|---------|
| `D{NNN}` | Primary data series | `D001` |
| `AD{NNNN}` | Additional data series (4-digit by convention) | `AD1001` |
| `{PREFIX}{NNN}-{LETTER}` | Subseries component | `D001-A`, `D001-B`, `AD1001-A` |
| `{PREFIX}{NNN}-EXT` | Extension data from modern API | `D001-EXT` |
| `{PREFIX}{NNN}-COMBINED` | Final spliced series | `D001-COMBINED` |

### Reindexing Display Notation

Column IDs in CSVs stay clean (`S001-B`). Display names for Extenbooks and Dash legends include reindex markers: `S001-B [R:1958]` meaning "reindexed to 1958=100".

The `series_registry.json` records reindexing metadata:

```json
{
  "S001-B": {
    "is_reindexed": true,
    "reindex_base_year": 1958,
    "derived_from": "S001-A",
    "transform": {
      "type": "reindex",
      "input": "S001-A",
      "base_year": 1958,
      "formula": "S001-B[t] = S001-A[t] * (100 / S001-A[1958])"
    }
  }
}
```

### Vintage Tracking

Vintages are tracked in `LOAD_LOG.json`, not in the series ID:

- API files named with date: `FRED_INDPRO_20260307.json`
- Registry records `"last_pulled": "2026-03-07T14:30:00Z"`
- For ALFRED historical vintages: `"vintage_policy": "specific"`, `"alfred_date": "2016-01-01"`

### Migration from v1.0

`S001A` becomes `S001-A`, `S001_EXT` becomes `S001-EXT`, `S001_COMBINED` becomes `S001-COMBINED`.

---

## The series_registry.json

The **single source of truth** for all series metadata. Located at `Technical/series_registry.json` in the project and `config/series_registry.json` in the Replicator.

Every downstream output (Chopped, Extenbook, Dash app, Replicator console, DPRs, EPRs) reads from this file. See the plan document for the full schema specification.

### Required Fields Per Series

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable series name |
| `chapter` | int | Chapter number |
| `figures` | array | Figure references (e.g., `["Fig2.1"]`) |
| `subseries` | object | Map of subseries ID to subseries config |
| `validation` | object | Reference values and expected ranges |

Plus one of the source patterns below, depending on series type.

### Series Type Patterns

The registry supports three series patterns. The `source_file` vs `source_series` field determines which pattern applies.

**Input Table Series (Tier 2)**: Raw data tables loaded directly from Chopped CSVs. No construction or processing — just a loading script.

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Path to Chopped CSV (e.g., `ch##/Appendix##_tablename.csv`) |
| `tier` | Yes | `2` |
| `loading_script` | Yes | L## script ID |

**Single-Source Analytical Series (Tier 1)**: Built from one Chopped CSV through reindexing, splicing, and extension.

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Path to Chopped CSV |
| `construction` | Yes | Array of step objects with `op`, `input`, `output`, `formula` |
| `extension` | Optional | API extension config (null if no extension) |

**Multi-Source Composite Series (Tier 1)**: Derived from other series (often Tier 2 inputs) via computation.

| Field | Required | Description |
|-------|----------|-------------|
| `source_series` | Yes | Array of source series IDs (e.g., `["S217"]`) |
| `construction_steps` | Yes | Array of string descriptions of construction steps |
| `extension` | Optional | API extension config (null if no extension) |

### Concurrent Series (CS) for Ratio/Rate Series

When a series is a **ratio or rate** (e.g., profit rate = Numerator / Denominator), the `concurrent_series` block in `series_registry.json` defines the level-data components. This enables the "Show Components" view in the visualization app.

| Field | Required | Description |
|-------|----------|-------------|
| `concurrent_series` | Optional | Object mapping CS IDs to component definitions |
| `CS{NNN}-N` | Per component | Numerator component: name, source_table, source_column, component_type, units |
| `CS{NNN}-D` | Per component | Denominator component: same fields as numerator |
| `CS{NNN}-N2`, `-D2` | Optional | Additional components for multi-part ratios |

CS numbering runs parallel to S### numbering. The CS number matches the parent S### number (e.g., S026 has CS026-N, CS026-D). Processing scripts extract CS columns into `data_dict` and `chopped_writer` includes them in the chopped CSV.

### Required Fields Per Subseries

| Field | Type | Criticality | Description |
|-------|------|-------------|-------------|
| `name` | string | CRITICAL | Descriptive name. Without it, viz trace labels degrade to raw column IDs. |
| `source` | string | Required | Original data source (null if derived) |
| `period` | array | CRITICAL | `[start_year, end_year]`. Without it, viz trace labels show "?-?" and date filtering breaks. |
| `units` | string | CRITICAL | Unit description (e.g., "Index 1958=100"). Without it, axis labels and metadata are incomplete. |
| `is_reindexed` | bool | Required | Whether this is a reindexed version of another subseries |
| `derived_from` | string | Required | Parent subseries ID if derived (null otherwise) |
| `transform` | object | Required | Transform specification if derived (null otherwise) |
| `color` | string | Recommended | Hex color for visualization |

**CRITICAL fields** are required for correct visualization. The `SUBSOURCE_METADATA.json` generator (Anu Chopped v1.2) will produce null values for missing CRITICAL fields, causing degraded trace labels in the viz app. Agents MUST validate that all subseries have non-null `name`, `period`, and `units` before running the Visualization Export phase.

### Registry Completeness Validation

After creating or updating `series_registry.json`, validate subseries completeness:

1. Every subseries MUST have non-null `name`, `period` (as `[start, end]`), and `units`
2. Every derived subseries MUST have `derived_from` pointing to a valid sibling subseries ID
3. Every subseries with `transform` MUST have `transform.type` set
4. Missing CRITICAL fields should be flagged as blockers for the viz export stage (Anu Pipeline Stage 5b)

### SourceReference System (v2.0)

The registry v2.0 adds a top-level `sources` block and per-subseries `source_refs` fields, enabling full provenance tracing from any data point back to its original source.

#### Top-Level Sources Block

```json
{
  "sources": {
    "SRC-BEA-LTEG": {
      "name": "Bureau of Economic Analysis, Long Term Economic Growth",
      "type": "primary_source",
      "citation": "BEA, Long Term Economic Growth 1860-1970, Table A-15, p.185",
      "url": "https://www.bea.gov/...",
      "access_date": "2026-03-15"
    },
    "SRC-FRED-INDPRO": {
      "name": "FRED Industrial Production Index",
      "type": "api_source",
      "api": "FRED",
      "series_id": "INDPRO",
      "url": "https://fred.stlouisfed.org/series/INDPRO"
    }
  }
}
```

#### Per-Subseries source_refs

Each subseries entry can include a `source_refs` array linking to the `sources` block:

```json
{
  "S001-A": {
    "name": "Historical Statistics of the US",
    "source": "BEA LTEG Table A-15",
    "period": [1860, 1918],
    "units": "Index",
    "source_refs": ["SRC-BEA-LTEG"]
  }
}
```

The `source_refs` array enables the provenance index (`provenance_index.json`) to build lineage chains: `by_source` (which series use a given source), `by_api` (which series come from a given API), and `by_series` (which sources feed a given series).

### Optional Fields (Series and Subseries)

| Field | Type | Level | Description |
|-------|------|-------|-------------|
| `viz_column` | string | series or subseries | Semantic column name for visualization export (e.g., `"IndProd"`, `"rcorp"`). The Replicator's visualization export phase uses this to rename columns in chapter-level CSVs. Set at series level for single-column composites (Ch2-style), at subseries level for multi-column figure series (Ch6-style). Only subseries/series with a `viz_column` are included in the visualization export. |
| `source_refs` | array | subseries | References to top-level `sources` block entries (v2.0) |

---

## Sub-Process 1: Knowledge Base Construction

### Purpose

Build a searchable Knowledge Base from source materials. This involves two distinct activities:

1. **HDARP Extraction** (mechanical): Robert/HDARP extracts raw text from PDFs — body text, appendices, tables, equations. This produces raw extraction files.
2. **KB Synthesis** (analytical): An agent reads the raw extractions and creates a structured, searchable markdown document per chapter. This is the valuable agent work.

### KB Synthesis Outputs

- **Per-chapter KB file**: `Inputs/Robert/KB/ch##_topic.md` — Structured markdown synthesizing:
  - Theoretical framework and key equations
  - Data sources and methods (from appendices)
  - Adjustments, selection criteria, known limitations
  - Key quotes with page references
- **Methodology summary**: `Inputs/Robert/KB/appendix_methodology_summary.json` — Machine-readable index of data sources, limitations, and methodology per chapter
- `KB_INDEX.md` — Catalog of all KB content with paths and descriptions

### Steps

1. Identify source materials (book chapters, appendices, methodology PDFs)
2. If raw HDARP extractions do not exist, run HDARP (following an external KB-construction protocol)
3. Read all relevant extractions for the chapter
4. Synthesize into a structured KB markdown file (`Inputs/Robert/KB/ch##_topic.md`)
5. Update `appendix_methodology_summary.json` with new chapter entry
6. Update `KB_INDEX.md` listing all KB content

---

## Sub-Process 2: Data Import

### Purpose

Bring raw data files into the project's `Inputs/` structure following the standard 3-folder pattern.

### Rules

- `Inputs/` is FLAT — preserve user organization, no type-based subdirectories
- API data goes in `Inputs/API/[SOURCE]/` (e.g., `Inputs/API/FRED/`, `Inputs/API/BEA/`) — all API data must be from public, externally replicable sources
- Robert imports go in `Inputs/Robert/` for HDARP content
- Read-only originals only — never modify files in `Inputs/`
- NEVER use internal databases as intermediaries for public API data

---

## Sub-Process 3: Data Absorption

### Purpose

Transform diverse input formats (Chopped CSVs, Excel files, API responses) into a single definitive internal database — the "Absorbed Database."

### Output

- Absorbed database CSV in long format: `Technical/absorbed/chapter_##_absorbed.csv`
- `ABSORPTION_REPORT.md` documenting the absorption process

### Absorbed Database Format

```csv
series_id,subseries_id,year,value,source_file
S034,S034-A,1987,0.1523,S034_chopped.csv
S034,S034-A,1988,0.1487,S034_chopped.csv
```

The 5-column long format is the implemented standard. Each row is one observation for one subseries in one year.

---

## Sub-Process 4: Series Decomposition

### Purpose

Document how each series is built from sub-components. This is the deep analytical work that ensures agents understand the construction before they code anything.

### Prerequisites

- Anu Research `S###_research.json` must exist for the series

5. **Adequacy Check recommended**: If `ADEQUACY_REPORT.json` exists for the chapter, verify it is ADEQUATE before starting ingestion. If absent, proceed but warn.

### Output

`Technical/docs/series/S###_DECOMPOSITION.md` for each series, containing:

1. **Sub-component table**: Every column, its source, coverage, units, and transform
2. **Construction steps**: Step-by-step formulas from the `series_registry.json`
3. **Research references**: Links to specific entries in `S###_research.json`
4. **Modern API equivalent**: What API series extends this data
5. **Construction diagram**: Mermaid flowchart showing data flow

### Template

`templates/SERIES_DECOMPOSITION_TEMPLATE.md`

---

## Sub-Process 5: Provenance Documentation

### Data Provenance Record (DPR)

One DPR per series documenting:
- Quick Reference (series ID, chapter, figures, coverage)
- Context (research entry references)
- Subsources with API mapping and quality categories
- Year-Source Matrix
- Transformation chain (from series_registry.json)
- Validation results
- Known issues

### Figure Provenance Record (FPR)

One FPR per figure documenting data-to-figure mapping.

### Templates

- `templates/DPR_TEMPLATE.md`
- `templates/FPR_TEMPLATE.md` (inherited from anu-standard, the archived predecessor skill)

---

## Sub-Process 6: Content Type Classification

Classify all extracted content:

| Type | Format | Example |
|------|--------|---------|
| Tables | CSV | Data tables from appendices |
| Equations | LaTeX | Mathematical formulas |
| Figures | Markdown + image | Charts and diagrams |
| Body text | Markdown | Narrative descriptions |

---

## Sub-Process 7: Identity Systems

Manage all identifiers:

| Pattern | Domain | Example |
|---------|--------|---------|
| `S{NNN}` | Data series | S001 |
| `S{NNN}-{LETTER}` | Subseries | S001-A |
| `Fig{C}.{N}` | Figures | Fig2.1 (no space — never `Fig 2.1`) |
| `T{NNN}` | Tables | T001 |
| `V-{DOM}{NN}-{MTH}` | Variants | V-PR01-SHT |

Figure IDs must be consistent across `series_registry.json`, research JSONs, DPRs, FPRs, and decomposition files. Always use the compact form without spaces.

---

## Two-Tier Architecture

Data construction projects distinguish between raw input tables and computed analytical series:

### Tier 1: Composite Analytical Series

Full pipeline artifacts required:
- Research JSON, Decomposition, DPR, EPR (if extensible)
- Loading script (L##), Processing script (P##)
- Chopped CSV, Extenbook, Figure CSV

**Registry pattern**: Uses `source_series` (array of input series IDs) or `source_file` with `construction` steps. No `tier` field or `"tier": 1`.

**Examples (the reference project)**: S034 (average ROP from S217 industry data), S001 (spliced industrial production index)

### Tier 2: Raw Input Tables

Minimal artifacts — only loading script and registry entry:
- Loading script (L##) that parses the chopped CSV
- Registry entry with `"tier": 2` and subseries mapping the raw columns

**Not required**: Decomposition, DPR, EPR, processing script, extenbook. These would be redundant since Tier 2 tables are just raw inputs.

**Registry pattern**: Uses `source_file`, has `"tier": 2`, subseries map raw column IDs to names.

**Examples (the reference project)**: S217 (ropdataUSind with 64 columns), S013 (BEA NIPA Table 6.8.II-7 with 47 columns)

### Ledger Implications

The Anu Ledger (v1.1+) is Tier-aware: Tier 2 series are not penalized for missing DPRs, decompositions, or processing scripts in the documentation health score.

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-ingestion init [project]` | Initialize project with Inputs/Technical/Outputs structure |
| `/anu-ingestion import [source]` | Import data files into Inputs/ |
| `/anu-ingestion absorb [chapter]` | Create absorbed database for a chapter |
| `/anu-ingestion decompose [series_id]` | Create series decomposition document |
| `/anu-ingestion create-dpr [series_id]` | Create DPR from template |
| `/anu-ingestion create-fpr [figure_id]` | Create FPR from template |
| `/anu-ingestion create-registry [chapter]` | Create series_registry.json for a chapter |
| `/anu-ingestion validate [target]` | Validate ingestion completeness |
| `/anu-ingestion migrate-ids` | Migrate series IDs from v1.0 to v2.0 notation |

---

## Five Core Principles (inherited from Anu Standard)

1. **EXPLICIT PARSING** — Never rely on implicit defaults when loading data
2. **VALIDATE ON LOAD** — Every data structure must be validated immediately after loading
3. **FAIL LOUDLY** — Never fall through to silent defaults; throw diagnostic errors
4. **DOCUMENT EVERYTHING** — Every series, figure, and transformation must have provenance
5. **TEST DATA PATHS** — Every data-to-output mapping must have automated tests

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Research** | Prerequisite — research.json must exist before decomposition |
| **Anu Extension** | Ingestion outputs (registry, DPRs) are prerequisites for extension |
| **Anu Replicator** | Registry and absorbed data feed into Replicator's data/user-inputs/ |
| **Anu Chopped** | Chopped CSVs are validated during import; IDs use v2.0 notation |
| **Anu Extenbook** | Registry fields populate Extenbook sheets |
| **Anu Review** | D4 DPR Completeness and D4 Decomposition Coverage scored |
| **Anu Pipeline** | Ingestion is Stage 2 (after Research) |

---

## Anu Framework Context

- **Pipeline Stage**: 2 (INGESTION)
- **Upstream**: Stage 0 Adequacy, Stage 1 Research
- **Downstream**: Stage 3 Extension, Stage 4 Replication
- **Adequacy Relevance**: L2 (Series Definition) — ingestion creates the series_registry.json that L2 validates
- **Key Handoff**: Creates series_registry.json consumed by Extension, Replicator, Chopped, Extenbook, Shiny, Ledger

---

## migrate-scheme procedure (agent-executed, no script)

When the agent is rebuilding a predecessor under a new ID scheme (`anu-rebuild` Wave 0 step 0.4 and Wave W.* per-cohort applications), or migrating an existing Anu-native project from one prefix scheme to another, the agent runs this procedure manually. **No automation script — the agent decides each edit.**

### Inputs

- `MIGRATION/crosswalk.csv` — agent-decided mapping `old_id, new_id, name, status, notes`. Only rows with `status: confirmed` are acted on; `proposed`, `deferred`, and `dropped` rows are noise during the migration.

### Procedure

For each confirmed `(old_id, new_id)` pair in the crosswalk, the agent:

1. **Rewrites `Technical/series_registry.json`**: any key `old_id` becomes `new_id`. Any string content referencing `old_id` becomes `new_id`.
2. **Rewrites `research/<old_id>_research.json`**: rename file to `research/<new_id>_research.json`; find-and-replace `old_id` inside.
3. **Rewrites `docs/series/<old_id>_DPR.md`** + `_EPR.md` + `_DECOMPOSITION.md`: rename + find-and-replace.
4. **Rewrites `Technical/chopped/<old_id>.csv`**: rename file; rewrite column headers inside (Row 2 of the 3-row Chopped format).
5. **Rewrites `Technical/extenbooks/<old_id>.xlsx`**: rename file. (Workbook contents are SID-self-describing; if a sheet has the SID inline, edit it.)
6. **Rewrites `Technical/code/L01_<old_id>.py`**, `P02_<old_id>.py`, `V03_<old_id>.py`: rename + edit content (variable names, docstring, output paths).
7. **Scans for stragglers**: `grep -rn "<old_id>"` across the project. Any remaining hit is either a comment that should be updated or a legitimate historical reference that should be qualified.

The agent uses `Edit` + `Grep` tools, not a generator script. Each edit is conscious; nothing is mechanical.

### After all confirmed pairs are processed

Run `python <framework>/skills/anu-doctor/check_project.py --project .` — P14 (crosswalk completeness) should PASS. Specifically:
- Every `old_id` from a confirmed crosswalk row no longer appears in any current-state artifact (search ignores `Inputs/Salvaged/`, `MIGRATION/`, and `Version History` blocks)
- Every `new_id` from a confirmed row does appear in the registry

### Logging

Append a one-line summary to `MIGRATION/MIGRATE_SCHEME_LOG.md`:

```
2026-MM-DD — migrated <N> series under crosswalk vX.Y. Stragglers: <list> (resolved by …).
```

### Why no script

Cross-project ID migration looks mechanical but isn't:
- Some series get renamed *and* split into subseries
- Some old IDs map to a derivative concept under a new ID
- Some appearances of `<old_id>` are legitimate historical references (in commits, in changelogs, in `Inputs/Salvaged/`) that must be preserved
- The agent reading the predecessor's research can tell which is which; a regex can't

A script would either be too aggressive (breaks history) or too conservative (misses cases). The agent gets it right per-row.

---

## Version History

- **v2.2** (archived) - Former "Anu Standard"
- **v3.0** (March 2026) - Renamed to Anu Ingestion; expanded to 7 sub-processes
- **v3.1** (March 2026) - Added Two-Tier Architecture and Series Type Patterns; fixed absorbed database format to 5-column standard; added KB synthesis vs HDARP extraction distinction; standardized Figure ID format (no spaces)
- **v3.2** (March 2026) - Added CRITICAL criticality level for subseries fields (name, period, units); added Registry Completeness Validation requirements for viz export
- **v3.3** (March 2026) - Generalized: replaced the reference project-specific chapter references (Ch2-style, Ch6/7/10-style) with descriptive type names; labeled series examples; genericized path patterns
- **v3.4** (March 2026) - Added Concurrent Series (CS) specification for ratio/rate series: concurrent_series block, CS{NNN}-N/D naming convention, integration with processing scripts
- **v3.5** (March 2026) - Minor refinements
- **v4.0** (April 2026) - Registry schema v2.0: added top-level `sources` block with SourceReference entries (SRC-ID format), per-subseries `source_refs` arrays, provenance index support (by_source, by_api, by_series lineage chains)
- **v4.1** (May 2026) - Documented the agent-executed **migrate-scheme procedure** for cross-project ID remapping (registry + research JSONs + per-series docs + chopped CSVs) using a crosswalk CSV. No automation script — the agent runs find-and-replace passes guided by the crosswalk and validates with `anu-doctor project`. Codified the series-status taxonomy as a validated enum (`data_unavailable`, `data_available`, `loaded`, `book_period_validated`, `extension_methodology_documented`, `validated_book_and_extension`, `partial:<reason>`, `pending:<dependency>`). **Canonical prefix scheme switched to `{D: primary, AD: additional}`** (Series ID Spec v2.1) — earlier `S`/`ES` collided with `anu-architecture` `S##` Setup-phase script prefixes. The `batch-create-dpr` idea was considered and rejected: DPRs are content-heavy documents that benefit from per-series authoring; batch templating would produce uniform-looking shells that hide construction decisions.

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `series_registry.json`, `S###_DECOMPOSITION.md`, `S###_DPR.md`, `Fig#.#_FPR.md`, `KB_INDEX.md`, `KB_MANIFEST.json`, `ABSORPTION_REPORT.md` |
| **Expects** | `S###_research.json` (from anu-research) |
| **Must Update on Completion** | Regenerate Ledger (`/anu-ledger generate`). If `ANU_CHOPPED_CATALOG.json` exists, regenerate it (`/anu-chopped catalog`) |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.
- [`DATA_PROVENANCE_STANDARDS.md`](../../docs/DATA_PROVENANCE_STANDARDS.md) — DPR / EPR / FPR / VPR record specs.

---

*Part of the Anu Framework v11.0 — Comprehensive Data Construction Framework*
*Replaces: Anu Standard v2.2*
