---
name: anu-ingestion
version: "5.2"
description: "Comprehensive data intake standard covering Knowledge Base construction, data import, absorption into a definitive internal format, series decomposition, provenance documentation, content type classification, identity systems, and source authenticity verification. Includes agent-executed migrate-scheme procedure for cross-project ID remapping (incl. the AS/ES→XS recipe), Series ID Spec v2.2 (D/XS canonical, xs_class sectioning), publish/triage/display_name registry fields, and the standardized series-status taxonomy. DPRs are authored per-series by the agent. Stage 3 of the Anu Framework pipeline; writes STEP_LOG, NARRATIVE, and LEDGER patches on every action."
when-to-use: "User needs to set up a data project, import raw data, build series_registry.json, decompose series, document provenance, migrate an ID scheme across an existing project, or scaffold a cohort of DPRs."
search-hints: "ingestion import data series registry decompose provenance knowledge base dpr migrate scheme batch cohort taxonomy status enum absorption"
argument-hint: "[action] [target]"
allowed-tools: Read, Write, Grep, Glob, Bash
requires: anu-research
part-of: Anu Framework v12.2
---

# Anu Ingestion v5.2

**Stage 3 — INGESTION**

The comprehensive data intake standard for the Anu Framework. Covers the full path from raw sources to a structured, documented, agent-ready data project through eight sub-processes: Knowledge Base Construction, Data Import, Data Absorption, Series Decomposition, Provenance Documentation, Content Type Classification, Identity Systems, and Source Authenticity Verification. Replaces the former "Anu Standard."

## Required-at-scaffold contracts

Every series scaffolded by anu-ingestion MUST carry these registry-side fields at creation time. anu-doctor P-checks fail in production if they're missing:

| Contract | Field | Enforcement |
|----------|-------|-------------|
| Validation parity (Decision 0002) | `validation.reference_values` (object or array) + `validation.tolerance` (number, default 0.01) | P32 (FAIL): V03 hardcoded benchmarks must match registry values |
| Extension binary state (Decision 0003) | `extension` is **object-when-extended** OR **explicitly `null`**, never absent | P36 (FAIL): subseries with `-EXT` iff `extension` block populated and complete |
| Status taxonomy (Decision 0003 corollary) | `series.status` must be a value from the **Status Taxonomy** table below (the single canonical enum, enforced by `anu-doctor` P06's `VALID_STATUS_RE`) | P31 (FAIL): status matches extension state + DPR claim |
| Chopped format (Decision 0005) | Top-level `chopped_format: "wide"|"long"` declared on the registry root (default `"wide"` if absent) | P04 (format-aware): chopped CSV layout matches declaration |

Optional supplementary field: `validation.round_trip_against` may name a book workbook the validator round-trips against, but it does **not** substitute for `validation.reference_values`. See `SERIES_REGISTRY_SCHEMA.md` § Validation Object for full schema.

## Stage Position

Stage 3 — INGESTION

---

## Inputs

| Artifact | Path / Pattern | Required |
|----------|---------------|----------|
| Research JSONs | `Technical/research/S###_research.json` | Yes |
| KB chapter files | `knowledge_base/ch##_topic.md` | Yes |
| KB methodology summary | `knowledge_base/appendix_methodology_summary.json` | Yes |
| Adequacy report | `Technical/docs/chapters/CH{N}_ADEQUACY_REPORT.json` | Recommended |
| Raw data files | `Inputs/` (flat structure) | Yes |
| API data cache | `Inputs/API/[SOURCE]/` | If extending |
| Knowledge Base extractions | `knowledge_base/` | Yes |
| Crosswalk CSV (migration only) | `MIGRATION/crosswalk.csv` | Migration only |

## Outputs

| Artifact | Path / Pattern | Format |
|----------|---------------|--------|
| Series registry | `Technical/series_registry.json` | JSON |
| Series decompositions | `Technical/docs/series/S###_DECOMPOSITION.md` | Markdown |
| Data Provenance Records | `Technical/docs/series/S###_DPR.md` | Markdown |
| Figure Provenance Records | `Technical/docs/series/Fig#.#_FPR.md` | Markdown |
| KB index | `KB_INDEX.md` | Markdown |
| KB manifest | `KB_MANIFEST.json` | JSON |
| Absorption report | `Technical/absorbed/ABSORPTION_REPORT.md` | Markdown |
| Absorbed database | `Technical/absorbed/chapter_##_absorbed.csv` | CSV (5-column long format) |
| Per-chapter KB file | `knowledge_base/ch##_topic.md` | Markdown |
| Methodology summary | `knowledge_base/appendix_methodology_summary.json` | JSON |
| Migration scheme log (migration only) | `MIGRATION/MIGRATE_SCHEME_LOG.md` | Markdown |

### Series ID Specification v2.2

The framework defines two canonical prefixes — `D` and `XS` — chosen to avoid collision with the eight `anu-architecture` phase prefixes (S/L/P/V/M/A/O/E).

```json
"prefix_scheme": {
  "primary": "D",
  "extra":   "XS"
}
```

| Prefix | Meaning | Example |
|---|---|---|
| **`D`** | **Data Series** — series from the book or study being replicated | `D001`, `D042` |
| **`XS`** | **Extra Series** — everything else: book-appendix series, series from other studies, derivative analytical series, comparison datasets, theoretical-construct series | `XS001`, `XS1001` |

Every `XS` entry MUST carry two classification fields in the registry (they drive website sectioning and publish ordering — XS sections always render after all primary series):

| Field | Values | Purpose |
|---|---|---|
| `xs_class` | `"appendix"` \| `"external_study"` | Whether the series is an appendix of the main book/study, or attributable to another study |
| `xs_attribution` | string | The appendix reference (e.g., `"Shaikh 2016, Appendix 6.8"`) or the study citation it comes from |

Projects may extend the scheme with additional prefixes when genuinely required — document in `MIGRATION/PREFIX_SCHEME.md` with one-line justification per extension prefix. `anu-doctor` P12 validates that every series ID's prefix is either canonical (D, XS) or listed in the project's declared extension set. The common project-specific primary alias is `S` (Study Series). **`AS` ("Analytical/Additional Series"), `ES` ("External Study Series"), and the pre-v2.2 canonical `AD` are LEGACY prefixes** — they are no longer valid aliases, `anu-doctor` rejects them, and existing projects migrate via the AS/ES→XS recipe in the migrate-scheme procedure below.

#### ID Format: `{PREFIX}{NNN}[-{LETTER}][_suffix]`

| Pattern | Meaning | Example |
|---------|---------|---------|
| `D{NNN}` | Primary data series | `D001` |
| `XS{NNN}` / `XS{NNNN}` | Extra series (digit count preserved from any legacy ID) | `XS003`, `XS1001` |
| `{PREFIX}{NNN}-{LETTER}` | Subseries component | `D001-A`, `XS1001-A` |
| `{PREFIX}{NNN}-EXT` | Extension data from modern API | `D001-EXT` |
| `{PREFIX}{NNN}-COMBINED` | Final spliced series | `D001-COMBINED` |

#### Reindexing Display Notation

Column IDs in CSVs stay clean (`S001-B`). Display names for Extenbooks and Dash legends include reindex markers: `S001-B [R:1958]` meaning "reindexed to 1958=100".

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

#### Vintage Tracking

Vintages are tracked in `LOAD_LOG.json`, not in the series ID:
- API files named with date: `FRED_INDPRO_20260307.json`
- Registry records `"last_pulled": "2026-03-07T14:30:00Z"`
- For ALFRED historical vintages: `"vintage_policy": "specific"`, `"alfred_date": "2016-01-01"`

#### Migration from v1.0

`S001A` becomes `S001-A`, `S001_EXT` becomes `S001-EXT`, `S001_COMBINED` becomes `S001-COMBINED`.

### The series_registry.json

The **single source of truth** for all series metadata. Located at `Technical/series_registry.json` in the project and `config/series_registry.json` in the Replicator. Every downstream output reads from this file.

#### Required Fields Per Series

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Internal series name |
| `display_name` | string | **Public-facing, human-readable name** — propagated identically to website display, download filenames, zip internals, data dictionaries, the data repository/API, and GitHub (see `ANU_NAMING_STANDARD.md`). Sentence-case prose; no codes, no `clean_tax_panel`-style identifiers. |
| `chapter` | int | Chapter number |
| `figures` | array | Figure references (e.g., `["Fig2.1"]`) |
| `subseries` | object | Map of subseries ID to subseries config — **each subseries MUST carry its own `label` (human-readable) and `units`**; a parent series may only declare a single `units` value if all subseries share it (no `mixed_*` unit strings — see `UNITS_VALIDATION_STANDARD.md`) |
| `validation` | object | Reference values and expected ranges |
| `publish` | bool | Whether the series is included in public outputs (web export, downloads, API). Culled/broken/signal-less series set `false`. |
| `triage` | object | `{"verdict": "publish"\|"fix"\|"cull", "reason": "...", "date": "YYYY-MM-DD"}` — every series must have a triage verdict before the publish stage; no `fix` verdicts may remain open at publish time |

`XS`-prefixed series additionally require `xs_class` and `xs_attribution` (see Series ID Specification v2.2).

Plus one of the source patterns below, depending on series type.

#### Status Taxonomy

The `status` field tracks each series through the data pipeline. Each status implies a minimum set of required artifacts that `anu-doctor` enforces.

| Status | Meaning | Required Artifacts | EPR Required? |
|---|---|---|---|
| `data_unavailable` | No data exists for this series | DPR only | No |
| `data_available` | Raw data identified, not yet loaded | DPR | No |
| `loaded` | L01 loader exists and runs | DPR, L01 | No |
| `book_period_validated` | V03 validator passes for book period | DPR, L01, P02, V03 | No |
| `book_period_partial:{reason}` | Partial book data (e.g., `1948_1961`) | DPR, L01, P02, V03 | No |
| `validated_book_and_extension` | Book + extension data validated | DPR, EPR, L01, P02, V03 | **Yes** |
| `validated_book_and_extension_partial` | Extension exists but incomplete | DPR, EPR, L01, P02, V03 | **Yes** |
| `study_complete` | External/additional series fully validated, no temporal extension needed | DPR, EPR, L01, P02, V03 | **Yes** (documents why no extension) |
| `benchmark_only_matrix_derived` | Calculated from matrix/benchmark data | DPR, P02, V03 | No |
| `extension_methodology_documented` | EPR written but extension not yet run | DPR, EPR | No |
| `pending:{dependency}` | Blocked on upstream series | DPR | No |

The `study_complete` status resolves false-positive EPR warnings for series that are fully validated but have no temporal extension (e.g., cross-study comparisons, external study replications). It requires an EPR that documents why no extension is needed, but does NOT imply `-EXT`/`-COMBINED` subseries exist.

#### Series Type Patterns

**Input Table Series (Tier 2)**: Raw data tables loaded directly from Chopped CSVs.

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Path to Chopped CSV |
| `tier` | Yes | `2` |
| `loading_script` | Yes | L## script ID |

**Single-Source Analytical Series (Tier 1)**: Built from one Chopped CSV through reindexing, splicing, and extension.

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Path to Chopped CSV |
| `construction` | Yes | Array of step objects with `op`, `input`, `output`, `formula` |
| `extension` | Optional | API extension config (null if no extension) |

**Multi-Source Composite Series (Tier 1)**: Derived from other series via computation.

| Field | Required | Description |
|-------|----------|-------------|
| `source_series` | Yes | Array of source series IDs |
| `construction_steps` | Yes | Array of string descriptions of construction steps |
| `extension` | Optional | API extension config (null if no extension) |

#### Concurrent Series (CS) for Ratio/Rate Series

When a series is a ratio or rate, the `concurrent_series` block defines level-data components enabling the "Show Components" view in the visualization app.

| Field | Required | Description |
|-------|----------|-------------|
| `concurrent_series` | Optional | Object mapping CS IDs to component definitions |
| `CS{NNN}-N` | Per component | Numerator component: name, source_table, source_column, component_type, units |
| `CS{NNN}-D` | Per component | Denominator component: same fields as numerator |
| `CS{NNN}-N2`, `-D2` | Optional | Additional components for multi-part ratios |

CS numbering runs parallel to S### numbering. The CS number matches the parent S### number. Processing scripts extract CS columns into `data_dict` and `chopped_writer` includes them in the chopped CSV.

#### Required Fields Per Subseries

| Field | Type | Criticality | Description |
|-------|------|-------------|-------------|
| `name` | string | CRITICAL | Descriptive name. Without it, viz trace labels degrade to raw column IDs. |
| `source` | string | Required | Original data source (null if derived) |
| `period` | array | CRITICAL | `[start_year, end_year]`. Without it, viz trace labels show "?-?" and date filtering breaks. |
| `units` | string | CRITICAL | Unit description. Without it, axis labels and metadata are incomplete. |
| `is_reindexed` | bool | Required | Whether this is a reindexed version of another subseries |
| `derived_from` | string | Required | Parent subseries ID if derived (null otherwise) |
| `transform` | object | Required | Transform specification if derived (null otherwise) |
| `color` | string | Recommended | Hex color for visualization |

**CRITICAL fields** are required for correct visualization. Missing CRITICAL fields cause degraded trace labels in the viz app.

#### Registry Completeness Validation

After creating or updating `series_registry.json`:
1. Every subseries MUST have non-null `name`, `period` (as `[start, end]`), and `units`
2. Every derived subseries MUST have `derived_from` pointing to a valid sibling subseries ID
3. Every subseries with `transform` MUST have `transform.type` set
4. Missing CRITICAL fields should be flagged as blockers for the viz export stage

#### SourceReference System (v2.0)

Top-level `sources` block with per-subseries `source_refs` fields for full provenance tracing.

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

Per-subseries `source_refs` arrays link to the `sources` block, enabling the provenance index to build lineage chains: `by_source`, `by_api`, and `by_series`.

#### Optional Fields

| Field | Type | Level | Description |
|-------|------|-------|-------------|
| `viz_column` | string | series or subseries | Semantic column name for visualization export. The Replicator's visualization export phase uses this to rename columns. Only subseries/series with a `viz_column` are included in the visualization export. |
| `source_refs` | array | subseries | References to top-level `sources` block entries (v2.0) |

### Absorbed Database Format

```csv
series_id,subseries_id,year,value,source_file
S034,S034-A,1987,0.1523,S034_chopped.csv
S034,S034-A,1988,0.1487,S034_chopped.csv
```

The 5-column long format is the implemented standard. Each row is one observation for one subseries in one year.

### Two-Tier Architecture

**Tier 1: Composite Analytical Series** — Full pipeline artifacts required: Research JSON, Decomposition, DPR, EPR (if extensible), Loading script (L##), Processing script (P##), Chopped CSV, Extenbook, Figure CSV. Registry pattern: Uses `source_series` or `source_file` with `construction` steps. No `tier` field or `"tier": 1`.

**Tier 2: Raw Input Tables** — Minimal artifacts: Loading script (L##) and registry entry with `"tier": 2`. Decomposition, DPR, EPR, processing script are not required (redundant for raw inputs). Registry pattern: Uses `source_file`, has `"tier": 2`, subseries map raw column IDs to names.

The Anu Ledger (v1.1+) is Tier-aware: Tier 2 series are not penalized for missing DPRs, decompositions, or processing scripts in the documentation health score.

### Eight Sub-Processes

#### 1. Knowledge Base Construction

Build a searchable KB from source materials. Two distinct activities:
1. **PDF Extraction** (mechanical): a PDF extraction pipeline extracts raw text from PDFs
2. **KB Synthesis** (analytical): An agent reads raw extractions and creates structured, searchable markdown per chapter

KB Synthesis outputs: per-chapter KB file (`knowledge_base/ch##_topic.md`), methodology summary (`appendix_methodology_summary.json`), `KB_INDEX.md`.

Steps: Identify source materials → Run PDF extraction if needed → Read extractions → Synthesize KB markdown → Update methodology summary → Update KB index.

#### 2. Data Import

Bring raw data files into `Inputs/` following the mandatory 3-folder pattern:
- `Inputs/` is FLAT — preserve user organization, no type-based subdirectories
- API data in `Inputs/API/[SOURCE]/` — all API data must be from public, externally replicable sources
- Knowledge Base imports in `knowledge_base/`
- Read-only originals — never modify files in `Inputs/`

#### 3. Data Absorption

Transform diverse input formats into a single definitive internal database — the "Absorbed Database" — in the 5-column long CSV format.

#### 4. Series Decomposition

Document how each series is built from sub-components. Requires `S###_research.json` to exist. Produces `Technical/docs/series/S###_DECOMPOSITION.md` containing: sub-component table, construction steps, research references, modern API equivalent, construction diagram (Mermaid flowchart).

Template: `templates/SERIES_DECOMPOSITION_TEMPLATE.md`

#### 5. Provenance Documentation

**Data Provenance Record (DPR)**: One per series — Quick Reference, Context, Subsources with API mapping, Year-Source Matrix, Transformation chain, Validation results, Known issues. DPRs are authored per-series by the agent; batch automation was considered and rejected because DPRs are content-heavy documents that benefit from per-series authoring.

**Figure Provenance Record (FPR)**: One per figure — data-to-figure mapping.

Templates: `templates/DPR_TEMPLATE.md`, `templates/FPR_TEMPLATE.md`

#### 6. Content Type Classification

| Type | Format | Example |
|------|--------|---------|
| Tables | CSV | Data tables from appendices |
| Equations | LaTeX | Mathematical formulas |
| Figures | Markdown + image | Charts and diagrams |
| Body text | Markdown | Narrative descriptions |

#### 7. Identity Systems

| Pattern | Domain | Example |
|---------|--------|---------|
| `D{NNN}` / `AD{NNNN}` | Data series | D001, AD1001 |
| `{PREFIX}{NNN}-{LETTER}` | Subseries | D001-A |
| `Fig{C}.{N}` | Figures (no space) | Fig2.1 |
| `T{NNN}` | Tables | T001 |
| `V-{DOM}{NN}-{MTH}` | Variants | V-PR01-SHT |

Figure IDs must be consistent across `series_registry.json`, research JSONs, DPRs, FPRs, and decomposition files. Always use the compact form without spaces.

#### 8. Source Authenticity Verification

Before ingesting any data, verify it comes from an authentic source:

| Source Type | Status |
|-------------|--------|
| KB table extraction | Acceptable (primary) |
| API response from official statistical agency | Acceptable (primary) |
| Digitized from published figure | Acceptable (secondary, document precision) |
| Computed from primary data using documented methodology | Acceptable (derived) |
| Generated from summary statistics with random noise | **REJECTED** |
| Linear/log-linear trend estimated from reported range | **REJECTED** |
| Any `np.random` call in a data construction script | **REJECTED** |

### migrate-scheme Procedure (agent-executed, no script)

When the agent is migrating an existing project from one prefix scheme to another, the agent runs this procedure manually. No automation script — the agent decides each edit.

**Input**: `MIGRATION/crosswalk.csv` — agent-decided mapping `old_id, new_id, name, status, notes`. Only rows with `status: confirmed` are acted on.

For each confirmed `(old_id, new_id)` pair:

1. Rewrite `Technical/series_registry.json`: any key `old_id` → `new_id`; any string content referencing `old_id` → `new_id`
2. Rewrite `research/<old_id>_research.json`: rename file; find-and-replace inside
3. Rewrite `docs/series/<old_id>_DPR.md` + `_EPR.md` + `_DECOMPOSITION.md`: rename + find-and-replace
4. Rewrite `Technical/chopped/<old_id>.csv`: rename; rewrite column headers (Row 2 of 3-row Chopped format)
5. Rewrite `Technical/extenbooks/<old_id>.xlsx`: rename file
6. Rewrite `Technical/code/L01_<old_id>.py`, `P02_<old_id>.py`, `V03_<old_id>.py`: rename + edit content
7. Scan for stragglers: `grep -rn "<old_id>"` across the project

After all confirmed pairs: run `anu-doctor project` — P14 (crosswalk completeness) should PASS. Log in `MIGRATION/MIGRATE_SCHEME_LOG.md`.

Cross-project ID migration looks mechanical but isn't: series may be renamed and split, old IDs may appear as legitimate historical references, and the agent must distinguish these cases. A script would be either too aggressive or too conservative.

#### AS/ES → XS recipe (Series ID Spec v2.2 migration)

For projects carrying legacy `AS`/`ES` prefixes (e.g., predecessor replication projects), the crosswalk is a pure prefix swap with digit counts preserved — `AS003 → XS003`, `ES2301 → XS2301` (3-digit AS and 4-digit ES occupy disjoint ranges, so no collisions). Beyond the standard 7 steps above:

8. Add `xs_class` + `xs_attribution` to every migrated entry (classify appendix-of-main-book vs attributable-to-other-study from existing `book_table`/provenance fields; agent-reviewed, never inferred blindly)
9. Rewrite `subseries_id` values inside chopped CSVs (`AS003-A → XS003-A`), not just filenames
10. Update `prefix_scheme` in the registry to `{"primary": "S" (or "D"), "extra": "XS"}`
11. Ship the crosswalk as `MIGRATION/crosswalk.csv` in the publish bundle (the public correspondence table); legacy IDs get **no public aliases**
12. Regenerate (do not rename) extenbooks and any viz caches downstream

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

## Acceptance Gates

### Per-Series Gates

| Gate | Criteria |
|------|----------|
| Research prerequisite | `S###_research.json` exists for every Tier 1 series |
| Registry completeness | All subseries have non-null `name`, `period`, `units` |
| Decomposition exists | `S###_DECOMPOSITION.md` exists for every Tier 1 series |
| DPR exists | `S###_DPR.md` exists for every Tier 1 series |
| Source authenticity | No synthetic/fabricated data in any construction script |
| ID consistency | Figure IDs match across registry, research, DPR, FPR, decomposition |

### Five Core Principles (invariants)

1. **EXPLICIT PARSING** — Never rely on implicit defaults when loading data
2. **VALIDATE ON LOAD** — Every data structure must be validated immediately after loading
3. **FAIL LOUDLY** — Never fall through to silent defaults; throw diagnostic errors
4. **DOCUMENT EVERYTHING** — Every series, figure, and transformation must have provenance
5. **TEST DATA PATHS** — Every data-to-output mapping must have automated tests

### Migration Gates

- P14 (crosswalk completeness) passes after migrate-scheme
- Every `old_id` from confirmed crosswalk rows no longer appears in current-state artifacts (ignoring `Inputs/Salvaged/`, `MIGRATION/`, and Version History blocks)
- Every `new_id` from confirmed rows appears in the registry

## Documentation Cascade Writes

| Cascade File | Trigger | Content Written |
|-------------|---------|-----------------|
| `STEP_LOG.jsonl` | Every action (init, import, absorb, decompose, create-dpr, create-fpr, create-registry, validate, migrate-ids) | `{action, target, timestamp, status, artifacts_created}` |
| `NARRATIVE.md` | Every action | Human-readable summary of what was ingested/created and construction decisions made |
| `ANU_LEDGER.json` | Stage 3 completion for a series/cohort | Patch: `ingestion_coverage` updated; registry/DPR/decomposition counts refreshed |

Must also update on completion: Regenerate Ledger (`/anu-ledger generate`). If `ANU_CHOPPED_CATALOG.json` exists, regenerate it (`/anu-chopped catalog`).

## Integration with Anu Framework

| Skill | Relationship | Artifact Flow |
|-------|-------------|---------------|
| **Anu Research** (Stage 1) | Upstream — research.json must exist before decomposition | `S###_research.json` → decomposition references, DPR citations |
| **Anu Adequacy** (Stage 2) | Upstream — adequacy gates ingestion (recommended) | `ADEQUACY_REPORT.json` → prerequisite check |
| **Anu Extension** (Stage 4) | Downstream — registry and DPRs are prerequisites | `series_registry.json`, `S###_DPR.md` → extension config, EPR context |
| **Anu Replicator** | Consumer — registry and absorbed data feed Replicator | `series_registry.json` → `data/user-inputs/`, `config/` |
| **Anu Chopped** | Consumer — Chopped CSVs validated during import | IDs use v2.0 notation |
| **Anu Extenbook** | Consumer — registry fields populate sheets | `series_registry.json` → Extenbook data |
| **Anu Review** | Scorer — D4 DPR Completeness and Decomposition Coverage | `S###_DPR.md`, `S###_DECOMPOSITION.md` → D4 score |
| **Anu Build** | Orchestrator — Ingestion is Stage 3 | Stage gate checked before Stage 4 |
| **Anu Ledger** | Coverage tracker — Tier-aware scoring | Registry, DPRs, decompositions → health score |

### Pipeline Context

- **Pipeline Stage**: 3 (INGESTION)
- **Upstream**: Stage 1 Research, Stage 2 Adequacy
- **Downstream**: Stage 4 Extension, Stage 5 Replication
- **Key Handoff**: Creates `series_registry.json` consumed by Extension, Replicator, Chopped, Extenbook, Visualize, Ledger

### Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.
- [`DATA_PROVENANCE_STANDARDS.md`](../../../docs/DATA_PROVENANCE_STANDARDS.md) — DPR / EPR / FPR / VPR record specs.

## Data Repository Integration

Anu projects ingest data from **the canonical data repository** via the static-checkout pattern. Each L## loader that consumes a data-repository source MUST:

1. Read from `ProjectX/inputs/data-repository/[SOURCE]/`, never from `<data-repository>/DATA/` directly.
2. Verify the checkout's `PROVENANCE.md` exists and validates (use the shared helper in `anu-replicator/lib/data/data_loader.py` once it lands; see the data-repository revamp Phase 5).
3. Record the `data_source_id`, `data_repo_version`, and PROVENANCE hash in the DPR (Data Provenance Record) for that series.

If the source you need is NOT in the data repository yet, the answer is to **add it to the data repository** (see `docs/DATA_REPOSITORY_INTEGRATION.md` §6 "Adding a new data-repository source"), not to ingest it project-locally.

**Anti-patterns** (anu-doctor will flag):
- Custom API client in the project that duplicates a data-repository collector
- Hardcoded paths into `<data-repository>/DATA/...` (bypasses PROVENANCE)
- Reading another project's `inputs/data-repository/` checkout instead of maintaining your own

Canonical reference: `<data-repository>/docs/DATA_CHECKOUT_CONTRACT.md`.

## Anti-Patterns

| # | DO NOT | Consequence |
|---|--------|-------------|
| 1 | Rely on implicit defaults when loading data | Silent data corruption; downstream artifacts inherit bad values |
| 2 | Fall through to silent defaults on error | Hides problems; agents proceed with incomplete data |
| 3 | Generate data from summary statistics with `np.random` | Violates data authenticity; produces fabricated series |
| 4 | Estimate trends from reported range endpoints | Not real data; cannot be validated against original |
| 5 | Modify files in `Inputs/` | Breaks read-only originals invariant; corrupts provenance |
| 6 | Use internal databases as intermediaries for public API data | Breaks external replicability; other researchers can't reproduce |
| 7 | Create multi-sheet Excel files for ad-hoc analysis | Ad-hoc analysis Excel is one-sheet-per-file; the canonical anu-extenbook 4-sheet workbook (Decision 0001) is the standard for series workbooks and is exempt |
| 8 | Use Figure IDs with spaces (e.g., `Fig 2.1` instead of `Fig2.1`) | Breaks cross-file ID consistency |
| 9 | Skip decomposition for Tier 1 series | Agents can't understand construction; downstream outputs lack context |
| 10 | Batch-automate DPR creation | DPRs are content-heavy; batch templating produces shells that hide construction decisions |
| 11 | Start ingestion without research JSONs | Decompositions and DPRs depend on research findings |
| 12 | Leave subseries with null `name`, `period`, or `units` | Causes degraded trace labels and broken date filtering in visualization |

## Version History

- **v2.2** (archived) — Former "Anu Standard"
- **v3.0** (March 2026) — Renamed to Anu Ingestion; expanded to 7 sub-processes
- **v3.1** (March 2026) — Added Two-Tier Architecture and Series Type Patterns; fixed absorbed database format to 5-column standard; added KB synthesis vs PDF extraction distinction; standardized Figure ID format (no spaces)
- **v3.2** (March 2026) — Added CRITICAL criticality level for subseries fields (name, period, units); added Registry Completeness Validation requirements for viz export
- **v3.3** (March 2026) — Generalized: replaced project-specific chapter references with descriptive type names; labeled series examples; genericized path patterns
- **v3.4** (March 2026) — Added Concurrent Series (CS) specification for ratio/rate series
- **v3.5** (March 2026) — Minor refinements
- **v4.0** (April 2026) — Registry schema v2.0: added top-level `sources` block with SourceReference entries, per-subseries `source_refs` arrays, provenance index support
- **v4.1** (May 2026) — Documented agent-executed migrate-scheme procedure for cross-project ID remapping. Codified series-status taxonomy as validated enum. Canonical prefix scheme switched to `{D: primary, AD: additional}` (Series ID Spec v2.1). Batch-create-dpr rejected: DPRs benefit from per-series authoring.
- **v5.0** (May 2026) — Rewritten to Anu Framework v12.0 common template. Added Stage Position (Stage 3 — INGESTION), machine-listed Inputs/Outputs tables, Acceptance Gates (including Five Core Principles as invariants), Documentation Cascade Writes (STEP_LOG + NARRATIVE + LEDGER), Anti-Patterns table. Renumbered pipeline stage to Stage 3. All substantive content preserved including Series ID Spec v2.1, registry schema, eight sub-processes, Two-Tier Architecture, and migrate-scheme procedure.
- **v5.1** (May 2026) — Added Status Taxonomy table with artifact requirements and EPR flags. Added `study_complete` status for fully-validated series with no temporal extension. Documented project-specific prefix extensions (S/ES/AS convention). Cross-references SERIES_REGISTRY_SCHEMA.md v2.1.0.
- **v5.2** (June 2026) — Series ID Specification v2.2: canonical prefixes now `{D: primary, XS: extra}`; `AS`/`ES`/`AD` declared LEGACY and rejected by anu-doctor. New mandatory XS classification fields (`xs_class`, `xs_attribution`) driving website sectioning. New mandatory registry fields: `display_name` (public naming, per ANU_NAMING_STANDARD), `publish`, `triage`; per-subseries `label` + `units` required, `mixed_*` unit strings banned (per UNITS_VALIDATION_STANDARD). Added AS/ES→XS migration recipe (steps 8–12) to migrate-scheme.

---

*Part of the Anu Framework v12.0 — Comprehensive Data Construction Framework*
*Replaces: Anu Standard v2.2*
