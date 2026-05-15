---
name: anu-chopped
version: "2.0"
description: Machine-readable CSV output format with structured metadata. Validates and generates Anu Chopped CSVs with Row 1 metadata, Row 2 column IDs, and Row 3+ data. Includes subsource metadata generation for visualization. Use when creating, validating, or reading Chopped data files.
when-to-use: User needs to generate, validate, or read machine-readable CSV output files from data construction
search-hints: chopped csv output machine readable data format metadata validate
argument-hint: [action] [target]
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: anu-replicator
part-of: Anu Framework v11.0
---

# Anu Chopped Standard v2.0

The machine-readable CSV format for the Anu Framework. Formalizes the 3-row structure (metadata, headers, data) as a universal standard for data construction projects.

---

## Format Specification

### Row Structure

| Row | Content | Description |
|-----|---------|-------------|
| **Row 1** | Metadata | Source descriptions, units, and methodology notes per column |
| **Row 2** | Column IDs | Series and subseries identifiers (e.g., `S001-A`, `S001-B`) |
| **Row 3+** | Data | Numeric values with Year in the first column |

### Column Layout (left to right)

```
Year | S###-A (raw subsource 1) | S###-B (transform/reindex) | ... | S### (final series) | S###-EXT (raw API extension) | S###-F (re-indexed extension) | S###-COMBINED (spliced)
```

### Column ID Notation (v2.0)

- Subseries use dash notation: `S001-A`, `S001-B`, `S001-C`
- Extension (raw): `S001-EXT` — raw API data in native units from the splice year onward
- Extension (re-indexed): `S001-F` — API data re-indexed to overlap with the previous subsource at the splice point. Formula: `S###-F[t] = prev_subsource[splice_year] * (API[t] / API[splice_year])`
- Combined: `S001-COMBINED`
- Base series (author's final composite): `S001`
- Concurrent (component) numerator: `CS001-N` — level-data numerator input of a ratio/rate series
- Concurrent (component) denominator: `CS001-D` — level-data denominator input of a ratio/rate series
- Additional component suffixes: `CS001-N2`, `CS001-D2`, `CS001-N3`, `CS001-D3` for multi-ratio series

### Concurrent Series (CS) Columns

When a series is a ratio or rate (e.g., profit rate = NOS / Capital), the chopped CSV may include **Concurrent Series (CS)** columns that expose the level-data components (numerator and denominator). These columns:

- Use the `CS{NNN}-{suffix}` naming convention (e.g., `CS026-N`, `CS026-D`)
- Are defined in the `concurrent_series` block of `series_registry.json`
- Have corresponding `SUBSOURCE_METADATA` entries with `is_component: true` and `component_type: "numerator"|"denominator"`
- Live in the **same chopped CSV** as the rate series (not separate files)
- Have units (e.g., `$billions`) that differ from the rate series (e.g., `Rate (decimal)`)

| Validation Rule | ID | Description |
|-----------------|-----|-------------|
| CS column naming | V12 | CS columns must match `CS\d{3}-(N\d?|D\d?)` pattern |
| CS metadata | V13 | Each CS column must have a SUBSOURCE_METADATA entry with `is_component: true` |

### Row 1 Metadata Generation

Row 1 is **auto-generated from `series_registry.json`** by the Chopped writer. For each column:

- Non-derived subseries: `"{source}, {units}. {methodology_summary_excerpt}"`
- Derived/reindexed subseries: `"Derived from {derived_from}, {transform.type} to {units}. Formula: {transform.formula}"`
- Extension: `"{api} {api_series_id}, {units}. Source: {api_url}. Pulled via {script}. {aggregation_note}"`
- Combined: `"Spliced {base_series} ({base_period}) + {extension_source} (post-{splice_year}), re-indexed to {target_base} at splice year."`

---

## Validation Rules

| Rule | ID | Description |
|------|----|-------------|
| Row 1 exists | V1 | First row contains metadata strings |
| Row 2 exists | V2 | Second row contains column IDs |
| Year column | V3 | First column is "Year" (Row 2) or empty (Row 1) |
| ID format | V4 | All column IDs match `S\d{3}(-[A-Z]|-EXT|-F|-COMBINED)?` |
| Numeric data | V5 | All data cells (Row 3+) are numeric or empty |
| No duplicate IDs | V6 | No duplicate column IDs in Row 2 |
| Metadata count | V7 | Row 1 has same number of columns as Row 2 |
| Filename | V8 | Filename follows convention (warning only, not blocking) |
| Final series | V9 | At least one column has base series ID (S###) without suffix (warning for wide_table format) |
| Subsource metadata | V10 | Every column ID in this Chopped CSV has a matching entry in the project's `SUBSOURCE_METADATA.json` |
| Extension columns | V11 | Every extended series must have both `-EXT` (raw) and `-F` (re-indexed) columns in the chopped CSV |

---

## Subsource Metadata Generation

Every project that produces Chopped CSVs **MUST** also generate a `SUBSOURCE_METADATA.json` file that provides per-column metadata for downstream visualization. This file is **programmatically generated from `series_registry.json`** — never hand-written.

### Purpose

The visualization layer needs richer metadata than Row 1 descriptions alone. Without structured, registry-derived metadata, view mode filtering breaks (wrong subsources shown), trace labels degrade (unlabeled or mislabeled), and users cannot understand how series were constructed.

### Generator Script Pattern

A script (e.g., `generate_subsource_metadata.py`) reads `series_registry.json` and produces `SUBSOURCE_METADATA.json`:

```python
# Reads: config/series_registry.json
# Writes: data/final-data/shiny/SUBSOURCE_METADATA.json
# Also copies to: visualization app data directory
```

### Required Output Fields Per Column

| Field | Type | Description |
|-------|------|-------------|
| `subsource_id` | string | Compact ID without dash (e.g., `S001A`) |
| `column_name` | string | Chopped CSV column ID with dash (e.g., `S001-A`) |
| `source_name` | string | Human-readable source name |
| `source_text` | string | Full source citation text |
| `period_start` | int/null | First year of data coverage |
| `period_end` | int/null | Last year of data coverage |
| `units` | string/null | Unit description (e.g., "Index 1958=100") |
| `role` | string | One of: `original`, `reindex`, `reindex_to_match`, `splice`, `calculate`, `ratio`, `rescale`, `derived` |
| `is_derived` | bool | Whether this column is derived from another subseries |
| `derived_from` | string/null | Parent subseries ID if derived |
| `transform_type` | string/null | Transform type (reindex, splice, etc.) |
| `transform_detail` | string | Key-value pairs describing transform parameters |
| `is_construction_member` | bool | Whether this subsource participates in the author's construction steps |
| `is_extension` | bool | Whether this subsource is extension data (post-splice-year API data) |
| `parent_series` | string | Parent series ID (e.g., `S001`) |

### Required Output Fields Per Series (Construction Metadata)

| Field | Type | Description |
|-------|------|-------------|
| `series_id` | string | Series ID |
| `name` | string | Human-readable series name |
| `chapter` | int | Chapter number |
| `splice_year` | int/null | Year where extension data is spliced |
| `extension_api` | string/null | API used for extension (e.g., `FRED`) |
| `extension_series` | string/null | API series ID (e.g., `INDPRO`) |
| `extension_method` | string/null | Splice method used |
| `construction_text` | string | Human-readable narrative of how the series was constructed |

### Output JSON Structure

```json
{
  "generated_by": "generate_subsource_metadata.py",
  "source": "series_registry.json",
  "version": "1.0.0",
  "subsources": {
    "S001A": { "subsource_id": "S001A", "column_name": "S001-A", "..." : "..." },
    "S001B": { "..." : "..." }
  },
  "series_construction": {
    "S001": { "series_id": "S001", "construction_text": "...", "..." : "..." }
  }
}
```

### Deriving `is_construction_member`

A subseries has `is_construction_member = true` if it appears in any `construction` step for its parent series (as `input`, `output`, `match_to`, or in `inputs`/`subseries` arrays). This is determined by scanning the registry's `construction` array.

### Deriving `is_extension`

A subseries has `is_extension = true` if it corresponds to the post-splice-year segment of the final series. Two extension columns exist per extended series:

- **`S###-EXT`** (role: `extension_raw`) — Raw API data in native units from the splice year onward
- **`S###-F`** (role: `extension_reindexed`) — API data re-indexed to match the previous subsource at the splice point, using the formula: `S###-F[t] = prev_subsource[splice_year] * (API[t] / API[splice_year])`

Both columns allow visual verification that the extension faithfully continues the original series. The `-F` column should overlap visually with adjacent subsources at the splice point.

Extension subsource metadata is generated by a project-specific script that reads `series_registry.json` extension blocks (e.g., `generate_shiny_subsources.py` in the the reference project project, producing `SHINY_SUBSOURCES.json`). The general standard name for this output is `SUBSOURCE_METADATA.json`.

### Deriving `construction_text`

The generator builds a human-readable narrative by walking the `construction` steps and the `extension` config:

- `load` steps: "{id}: {source_name} ({period})"
- `reindex` steps: "{input} reindexed to {base_year}=100 -> {output}"
- `reindex_to_match` steps: "{input} reindexed to match {match_to} at {at_year} -> {output}"
- `splice` steps: "{input1} + {input2} spliced at {at_year} -> {output}"
- Extension: "Extended via {api} {series_id} ({method} at {splice_year})"

### Validation Against Chopped CSVs

The generator MUST validate that every column in every Chopped CSV has a corresponding entry in the output JSON. Missing entries indicate registry gaps that will cause unlabeled traces in the visualization.

---

## Catalog Format

`ANU_CHOPPED_CATALOG.json` — machine-readable catalog of all Chopped files:

```json
{
  "version": "2.0",
  "generated": "2026-03-07",
  "files": [
    {
      "filename": "Appendix2_IndustrialProduction.csv",
      "chapter": 2,
      "series_id": "S001",
      "subseries_ids": ["S001-A", "S001-B", "S001-C", "S001-D", "S001", "S001-EXT", "S001-COMBINED"],
      "year_range": [1860, 2025],
      "figures": ["Fig2.1"],
      "format": "time_series",
      "research_entry_count": 4,
      "extension_source": "FRED:INDPRO"
    }
  ]
}
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-chopped validate [file]` | Validate a single Chopped CSV |
| `/anu-chopped validate-all [directory]` | Validate all Chopped CSVs in a directory |
| `/anu-chopped generate [series_id]` | Generate Chopped CSV from registry + data |
| `/anu-chopped catalog [directory]` | Generate/update ANU_CHOPPED_CATALOG.json |
| `/anu-chopped migrate-ids [file]` | Migrate column IDs from v1.0 to v2.0 notation |

---

## Validation Script

`scripts/validate_chopped.py` — runs all validation rules, prints pass/fail per rule, returns exit code 0 if all pass.

```bash
python validate_chopped.py path/to/file.csv
python validate_chopped.py --dir path/to/chopped/ch02/
python validate_chopped.py --catalog path/to/ANU_CHOPPED_CATALOG.json
```

---

## Writer Library

`lib/formats/chopped_writer.py` in the Anu Replicator generates Chopped CSVs:

1. Reads `series_registry.json` for metadata and column IDs
2. Generates Row 1 from registry fields (auto-generated, not hand-written)
3. Generates Row 2 from subseries keys
4. Writes data rows from the processed series data

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Ingestion** | Chopped CSVs are validated during import; IDs use v2.0 notation |
| **Anu Replicator** | P## scripts write Chopped CSVs to `data/final-data/chopped/` |
| **Anu Extenbook** | Extenbook Data sheet mirrors Chopped structure with Excel formatting |
| **Anu Visualize** | R Shiny app loads Chopped CSVs for visualization; `SUBSOURCE_METADATA.json` (project-specific naming and generator) provides per-column metadata |
| **Anu Review** | D7 Chopped Validation dimension scores format compliance |

---

## Templates

- `templates/ANU_CHOPPED_CATALOG_TEMPLATE.json`

---

## Anu Framework Context

- **Pipeline Stage**: 5 (OUTPUT — validation)
- **Upstream**: Stage 4 Replication (produces Chopped CSVs)
- **Downstream**: Stage 5b Viz Export, Stage 6 Review
- **Adequacy Relevance**: L2 (Series Definition) — validates that chopped column IDs match registry subseries
- **Key Handoff**: Validated Chopped CSVs feed into Shiny data pipeline and Extenbook generation

## Version History

- **v1.0** (March 2026) - Initial release
- **v1.1** (March 2026) - Version bump for Anu Framework v6.0
- **v1.2** (March 2026) - Added Subsource Metadata Generation standard (V10), SUBSOURCE_METADATA.json specification, construction_text derivation
- **v1.3** (March 2026) - Added S###-F re-indexed extension column convention, V11 extension column validation rule, dual extension column requirement (-EXT + -F), subsource metadata generation standard, re-indexing formula documentation
- **v1.4** (March 2026) - Generalized: replaced the reference project-specific subsource metadata naming with generic pattern; clarified SUBSOURCE_METADATA.json as the standard name with project-specific variants
- **v1.5** (March 2026) - Added Concurrent Series (CS) column convention for ratio/rate series component data (CS{NNN}-N, CS{NNN}-D), V12/V13 validation rules
- **v2.0** (April 2026) - Version bump for Anu Framework v6.0 compatibility (format unchanged)

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `ANU_CHOPPED_CATALOG.json` (via `/anu-chopped catalog`), `SUBSOURCE_METADATA.json` (via generator script) |
| **Expects** | `series_registry.json` (for writer and metadata generator), Chopped CSVs to validate |
| **Must Update on Completion** | Regenerate catalog (`/anu-chopped catalog`) after new Chopped CSVs are written. Regenerate `SUBSOURCE_METADATA.json` after registry or chopped changes. Regenerate Ledger (`/anu-ledger generate`) |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Machine-Readable Data Format*
