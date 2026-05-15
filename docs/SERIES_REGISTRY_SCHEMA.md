# Anu Framework `series_registry.json` Schema Specification

**Schema version**: 2.0.0
**Spec version**: 1.0 (May 2026)
**Authoritative JSON Schema**: [`../schemas/series_registry.schema.json`](../schemas/series_registry.schema.json)
**Reference implementation**: `Projects/the reference project/Technical/series_registry.json`

---

## Overview

The `series_registry.json` is the single source of truth for every Anu Framework data project. It is produced by `/anu-ingestion` during Stage 2 of the Anu Pipeline and consumed by every downstream stage and artifact: the L## loaders, the P## processors, Anu Chopped CSVs, Anu Extenbooks, the visualization layer (Shiny/Dash), the Anu Replicator, the Anu Ledger, and the Anu Drive distribution package. Every value that reaches an end user must be traceable through this file.

Until now the registry's shape has been described only informally in `anu-ingestion/SKILL.md` (lines ~80-220) and learned by reading the the reference project reference implementation. This document gives the contract a formal name and a machine-readable JSON Schema (Draft 2020-12) so that loaders can validate registries on read, CI can gate registry edits, and new projects can scaffold conformant registries from day one. The schema is intentionally permissive in places (`additionalProperties: true` on most objects) so existing projects continue to parse; required fields and enums are enforced strictly where the contract is settled.

Conventions: series IDs follow the prefix scheme declared in the registry's `prefix_scheme` block. **Canonical prefixes are `D` (Data Series, primary) and `AD` (Additional Data Series).** The single-letter `D` and two-letter `AD` were chosen to avoid collision with `anu-architecture`'s eight `anu-architecture` phase prefixes (S/L/P/V/M/A/O/E). Project-optional extensions are documented per-project in `MIGRATION/PREFIX_SCHEME.md` if used. Validating regex: `^(D|AD|<project_ext>)\d{3,4}(-[A-Z]|-EXT|-COMBINED)?$`. `anu-doctor` P12 validates conformance. Figure IDs use the compact `Fig{C}.{N}` form with optional letter suffix (`Fig2.4A`). Source ref IDs are uppercase identifiers (`BEA_1966_LTEG`). Years are integers; periods are `[start, end]` integer pairs. Examples below illustrate the schema; substitute your project's prefix scheme as appropriate.

---

## Top-Level Structure

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | string | yes | Registry schema version. Currently `"2.0.0"`. |
| `project` | string | yes | Short project code (used for internal references; not the public-facing slug). |
| `prefix_scheme` | object | yes (v11.0+) | Declares which prefixes the project uses. Canonical: `{"primary": "D", "additional": "AD"}`. Projects may add a third prefix documented in `MIGRATION/PREFIX_SCHEME.md` if their data genuinely requires it (should be rare). |
| `notation` | string | no | Documentation string describing the series-ID notation in use. |
| `generated` | string (date) | no | ISO date `YYYY-MM-DD` the registry was generated. |
| `architecture` | string | no | Free-text framework version label, e.g., `"Anu Framework v11.0"`. |
| `drive_config` | object | no (recommended) | Distribution metadata consumed by `/anu-drive`. If absent, `anu-drive` synthesizes from top-level fields; explicit `drive_config` is preferred. |
| `series` | object | yes | Map of series ID -> series object. Property names MUST match the project's declared `prefix_scheme` (canonical: `^(D\d{3}\|AD\d{3,4})(-[A-Z]\|-EXT\|-COMBINED)?$`). |
| `figures` | object | no | Map of figure ID -> figure spec. Property names MUST match `^Fig\d+\.\d+[A-Z]?$`. |
| `sources` | object | no | Map of source ref_id -> source descriptor. Property names MUST be uppercase identifiers. |

Top-level skeleton:

```json
{
  "version": "2.0.0",
  "project": "<project-code>",
  "prefix_scheme": {
    "primary": "D",
    "additional": "AD"
  },
  "notation": "{PREFIX}{NNN}-{LETTER} with R:{YYYY} for reindexed display",
  "generated": "2026-MM-DD",
  "drive_config": { "...": "..." },
  "series":   { "D001": { "...": "..." }, "AD1001": { "...": "..." } },
  "figures":  { "Fig2.1": { "...": "..." } },
  "sources":  { "BEA_1966_LTEG": { "...": "..." } },
  "architecture": "Anu Framework v11.0"
}
```

### `drive_config`

Consumed only by `/anu-drive`. Schema:

| Field | Type | Required | Description |
|---|---|---|---|
| `project_title` | string | yes | Full title used in cover sheets and folder names. |
| `drive_version` | string | no | Drive-package version (e.g., `"1.0"`). |
| `author` | object | yes | `{first_name, last_name}`. |
| `institution` | string | no | Author institution. |
| `email` | string | no | Contact email. |
| `original_work` | object | no | `{author, title, year, publisher}` describing the original work being replicated. |
| `repo_url` | string | no | GitHub URL for the matching publication. |
| `license` | string | no | License string, e.g., `"MIT (Code) + CC-BY-4.0 (Data)"`. |

---

## Series Object

Every entry under `series` is one base series. The required fields are `name`, `chapter`, `figures`, `subseries`, and `validation`. The series must also identify its data origin via at least one of `source_file`, `source_series`, or `source_columns`.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Human-readable name. |
| `chapter` | integer | yes | Chapter number in the underlying work. |
| `figures` | array of string | yes | Figure IDs that depend on this series. May be empty for tier-2 input tables. |
| `tier` | integer (1 or 2) | no | Two-tier classification (see Tiers below). Absent or `1` for analytical series; `2` for raw input tables. |
| `source_file` | string | conditional | Path to source CSV under the Chopped root. |
| `source_series` | string or array | conditional | Parent series ID(s) for composite series. |
| `source_columns` | object | conditional | Map of logical role -> parent subseries column ID. |
| `year_range` | `[int, int]` | no | Series lifetime. |
| `data_type` | string | no | Content classification (see Enums). |
| `content_type` | string | no | Alias used by anu-framework rules. |
| `units` | string | no | Series-level units (often deferred to subseries). |
| `description` | string | no | One-line description. |
| `subseries_note` | string | no | Free-text used when `subseries` is empty (typical for wide tier-2 tables). |
| `subseries` | object | yes | Map of subseries ID -> subseries object. May be empty for wide tier-2 tables. |
| `construction` | array | no | Ordered construction steps. |
| `construction_steps` | array | no | Legacy/free-text variant. |
| `extension` | object or null | no | Modern-API extension config, or `null` if none. |
| `validation` | object | yes | Reference values and expected ranges. |
| `concurrent_series` | object | no | Numerator/denominator components for ratio series. |
| `proxy` | boolean | no | True if extension uses a proxy. Requires `proxy_justification`. |
| `proxy_justification` | string | conditional | Required when `proxy=true`. |
| `viz_column` / `shiny_column` | string | no | Visualization column name. |
| `source_refs` | array of string | no | Top-level `sources` keys. |
| `kb_references` | array of string | no | Knowledge Base anchors. |
| `decision_refs`, `assumption_refs` | array of string | no | Cross-references into research JSONs. |
| `index_axis` | string | no | For `cross_sectional` series: dimension name (e.g., `"industry"`). |
| `catalog_id` | string | no | Cross-reference to external catalog. |

Example series header (the reference project `S001`, lines 25-31):

```json
"S001": {
  "name": "US Industrial Production Index",
  "chapter": 2,
  "figures": ["Fig2.1"],
  "source_file": "ch02/Appendix2_IndustrialProduction.csv",
  "year_range": [1860, 2025],
  "data_type": "time_series"
}
```

### Tier patterns

Three patterns produce a valid series object:

1. **Tier-1 single-source analytical** — `source_file` + `construction` + optional `extension`. Example: `S001`.
2. **Tier-1 composite** — `source_series` (array of parent IDs) and/or `source_columns` instead of `source_file`. Example: `S027` (lines 3188-3300) reads from `S013` via `source_columns`.
3. **Tier-2 input table** — `"tier": 2`, `source_file`, minimal `construction` (`load` only), `subseries` often empty plus a `subseries_note`. Example: `S206` (line 1377).

---

## Subseries Object

Property keys under `subseries` must be valid subseries IDs (e.g., `S001-A`, `S001-EXT`, `S001-COMBINED`). Each subseries documents one column of source or derived data.

| Field | Type | Required | Criticality | Description |
|---|---|---|---|---|
| `name` | string | yes | CRITICAL | Descriptive name. Empty/null breaks viz trace labels. |
| `source` | string or null | yes | required | Original source citation; `null` if derived. |
| `period` | `[int, int]` | yes | CRITICAL | Year range. |
| `units` | string | yes | CRITICAL | Units, e.g., `"Index 1958=100"`. |
| `is_reindexed` | boolean | yes | required | Whether this is a reindexed version of another subseries. |
| `derived_from` | string or null | recommended | required | Parent subseries ID or `"A+B"` notation. |
| `transform` | object or null | recommended | required | Transform spec when derived. |
| `color` | string | recommended | recommended | Hex color for plotting. |
| `api` | string or null | no | optional | API source name if applicable. |
| `loading_script` | string | conditional | required when raw | `L##` script ID. |
| `processing_script` | string | conditional | required when derived | `P##` script ID. |
| `is_extension` | boolean | no | optional | True for the `-EXT` subseries. |
| `reindex_base_year` | integer or null | no | optional | Base year when `is_reindexed=true`. |
| `source_refs` | array of string | no | optional | Top-level `sources` keys. |
| `viz_column` / `shiny_column` | string | no | optional | Per-subseries viz column name. |
| `confidence` | enum | no | optional | `"high" | "medium" | "low"`. |
| `note` | string | no | optional | Free-text note (e.g., "intentionally skipped"). |

CRITICAL fields are required for correct visualization. Anu Chopped v1.2 emits warnings when any are missing.

Example subseries (the reference project `S001-B`, lines 57-79):

```json
"S001-B": {
  "name": "S001-A reindexed to 1958=100",
  "source": null,
  "period": [1860, 1918],
  "units": "Index 1958=100",
  "api": null,
  "is_reindexed": true,
  "reindex_base_year": 1958,
  "derived_from": "S001-A",
  "transform": {
    "type": "reindex",
    "input": "S001-A",
    "base_year": 1958,
    "formula": "S001-B[t] = S001-A[t] * (100 / S001-A[1958])"
  },
  "color": "#1f77b4",
  "processing_script": "P01",
  "source_refs": [],
  "confidence": "high"
}
```

### Subseries `transform` block

Required when `derived_from` is non-null. The `type` field carries one of:

| `type` | Required parameters | Meaning |
|---|---|---|
| `reindex` | `input`, `base_year`, `formula` | Rebase to `base_year` = 100. |
| `reindex_to_match` | `input`, `match_to`, `at_year`, `formula` | Scale `input` so it equals `match_to` at `at_year`. |
| `splice` | `inputs`, `at_year`, `formula` | Combine two subseries at a join year. |
| `calculated` | `inputs`, `formula` | General computation; documentation in `formula`. |
| `ratio` | `formula` | Ratio of two inputs. |
| `complement` | `formula` | Algebraic complement, e.g., `1 - x`. |
| `fitted_curve` | `formula` | Fitted analytical curve. |
| `annual_average` | `input`, `frequency` | Aggregate sub-annual to annual. |
| `deflate` | `input`, `deflator`, `base_year` | Real-deflation transform. |

---

## Construction Steps

`construction` is an ordered array of step objects executed by the P## processor. Each step has an integer `step` ordinal and a string `op`. Required additional parameters vary by `op`.

Generic shape:

```json
{ "step": 1, "op": "load", "subseries": ["S001-A"], "desc": "Load BEA LTEG TA15 data" }
```

### `op: "load"`
Load a source CSV column or columns into a subseries.

| Field | Required | Notes |
|---|---|---|
| `subseries` | yes | Array of subseries IDs to load. |
| `desc` | recommended | Human-readable summary. |
| `source` | no | Override `source_file` for this step. |

### `op: "reindex"`
Rebase a subseries to a new base year.

| Field | Required | Notes |
|---|---|---|
| `input` | yes | Source subseries ID. |
| `output` | yes | Output subseries ID. |
| `base_year` | yes | Year to set = 100. |

### `op: "reindex_to_match"`
Scale one subseries to equal another at a chosen year.

| Field | Required | Notes |
|---|---|---|
| `input` | yes | Subseries to be rescaled. |
| `match_to` | yes | Subseries whose level to match. |
| `at_year` | yes | Year at which the two should equal. |
| `output` | yes | Output subseries ID. |

### `op: "splice"`
Join two subseries at a year.

| Field | Required | Notes |
|---|---|---|
| `inputs` | yes | `[before_subseries, after_subseries]`. |
| `at_year` | yes | Join year. |
| `output` | yes | Output subseries ID. |
| `method` | no | E.g., `"use_second_from_splice_year"`. |

### `op: "calculate"`
General-purpose calculation step. `formula` lives in the `transform` block of the output subseries.

| Field | Required | Notes |
|---|---|---|
| `inputs` | yes | Input subseries IDs. |
| `output` | yes | Output subseries ID. |
| `desc` | recommended | What is computed. |

### `op: "rescale"`
Apply a linear/scalar rescaling. Same shape as `calculate`.

### `op: "extract"`
Used by composite series (`source_series`-pattern) to pull specific columns from a parent series.

| Field | Required | Notes |
|---|---|---|
| `input` | yes | Parent series ID (e.g., `"S013"`). |
| `columns` | yes | Array of parent subseries IDs to extract. |

### `op: "extend"`
Marker step indicating that extension columns are merged in (typically when `extension.pre_computed=true`). Documented via `desc`.

### `op: "verify"`
Run reference-value checks defined in `validation`. No parameters.

### `op: "transpose"`
Reshape a wide cross-sectional table into long format. No parameters required.

### `op: "output"`
Terminal step that writes a final artifact.

| Field | Required | Notes |
|---|---|---|
| `output` | yes | Output filename. |

### `op: "normal_capacity"`
Capacity-adjusted derivation used in figure-level transforms (see the reference project `Fig6.5/6.6`).

### `op: "aggregate"`, `op: "combine"`
Reserved for future aggregation/combination semantics. Use `calculate` until a project requires distinguishing them.

A multi-step `construction` example (the reference project `S001`, lines 125-167):

```json
"construction": [
  { "step": 1, "op": "load", "subseries": ["S001-A"], "desc": "Load BEA LTEG TA15" },
  { "step": 2, "op": "reindex", "input": "S001-A", "output": "S001-B", "base_year": 1958 },
  { "step": 3, "op": "load", "subseries": ["S001-C"], "desc": "Load FRB G-17 (1919-2010)" },
  { "step": 4, "op": "reindex_to_match", "input": "S001-C", "match_to": "S001-B", "at_year": 1919, "output": "S001-D" },
  { "step": 5, "op": "splice", "inputs": ["S001-B", "S001-D"], "at_year": 1919, "output": "S001",
    "method": "use_second_from_splice_year" }
]
```

---

## Extension Object

The `extension` block on a series declares how the original series is carried forward using a modern API. `/anu-extension` consumes it to produce the EPR (Extension Provenance Record) at `Technical/docs/series/S###_EPR.md`. Set to `null` when no extension is planned.

| Field | Type | Required | Description |
|---|---|---|---|
| `api` | string | yes | API/agency identifier (`FRED`, `BEA`, `BLS`, `MeasuringWorth`, `OECD`, `IMF`, ...). |
| `api_series_id` | string | yes if scripted | Native API series identifier. |
| `frequency` | enum | yes if scripted | `annual` \| `quarterly` \| `monthly` \| `daily` \| `weekly`. |
| `aggregation` | enum or null | yes | `annual_average` \| `annual_sum` \| `end_of_period` \| `start_of_period` \| `null`. |
| `splice_year` | integer | yes | Year at which extension takes over. |
| `splice_method` | enum | yes | `growth_rate` \| `direct` \| `level` \| `ratio`. |
| `output_subseries` | string | yes | Subseries ID for the extension (matches `^S\d{3}-EXT$`). |
| `combined_subseries` | string | yes | Subseries ID for the spliced output (matches `^S\d{3}-COMBINED$`). |
| `reindexed_subseries` | string | no | Optional reindex-to-match subseries ID. |
| `vintage_policy` | enum | yes | `latest` \| `specific` \| `alfred`. |
| `alfred_date` | string (date) | conditional | Required when `vintage_policy="alfred"`. |
| `last_pulled` | string (date) | recommended | ISO date of last successful pull. |
| `manual_download` | boolean | no | True if extension data is fetched by hand. |
| `pre_computed` | boolean | no | True if extension is pre-merged into source CSV upstream. |
| `tables` | array | no | Agency table IDs when `pre_computed=true`. |
| `note` | string | no | Free-text rationale. |
| `provenance` | object | yes | EPR provenance block (see below). |

Provenance sub-object (mandatory fields):

| Field | Description |
|---|---|
| `shaikh_source` | Original source citation in the underlying work. |
| `shaikh_appendix_ref` | Appendix/figure cross-reference. |
| `extension_source` | Modern source name. |
| `extension_url` | Modern source URL. |
| `conceptual_continuity` | Why the extension measures the same concept. |
| `vintage_note` | Notes about base-year/vintage differences. |

Example extension (the reference project `S001`, lines 169-189):

```json
"extension": {
  "api": "FRED",
  "api_series_id": "INDPRO",
  "frequency": "monthly",
  "aggregation": "annual_average",
  "splice_year": 2010,
  "splice_method": "growth_rate",
  "output_subseries": "S001-EXT",
  "combined_subseries": "S001-COMBINED",
  "vintage_policy": "latest",
  "last_pulled": "2026-05-04",
  "reindexed_subseries": "S001-F",
  "provenance": {
    "shaikh_source": "BEA (1966, table A15) + FRB G-17",
    "shaikh_appendix_ref": "Appendix 2.1, Fig 2.1",
    "extension_source": "FRED INDPRO",
    "extension_url": "https://fred.stlouisfed.org/series/INDPRO",
    "conceptual_continuity": "Same underlying FRB G.17 Industrial Production Index",
    "vintage_note": "FRED base 2017=100; growth-rate splice eliminates base dependency"
  }
}
```

EPR location convention: the EPR markdown is written to `Technical/docs/series/S###_EPR.md` and bundled into the Replicator at `data/user-inputs/EPR/`. The `provenance` block is the canonical input.

---

## Validation Object

Drives the post-construction validator and the anu-review D8 dimension.

| Field | Type | Required | Description |
|---|---|---|---|
| `reference_values` | object or array | yes | Year-keyed values for assertion checks. |
| `expected_range` | `[number, number]` | yes | Hard min/max bounds for the constructed series. |
| `tolerance` | number | no | Relative tolerance for `reference_values` (default 0.01 = 1%). |
| `target_end_year` | integer or null | no | Required end-year after extension. |
| `row_count` | object | no | For `cross_sectional` series: `{expected, tolerance}`. |
| `note` | string | no | Free-text. |

`reference_values` may take either of two forms:

**Object form** (used throughout the reference project for time-series):
```json
"reference_values": {
  "1860": 1.636761,
  "1924": 30.131291,
  "2026": 504.014601
}
```

**Array form** (also valid; useful for explicit per-row tolerance):
```json
"reference_values": [
  {"year": 1860, "expected": 1.636761, "tolerance": 0.01},
  {"year": 2026, "expected": 504.014601, "tolerance": 0.05}
]
```

Full example (the reference project `S001`, lines 190-210):

```json
"validation": {
  "reference_values": { "1860": 1.636761, "2026": 504.014601 },
  "expected_range": [0, 600],
  "target_end_year": 2025
}
```

---

## Concurrent Series (`concurrent_series`)

When a series is a ratio/rate (`r = N / D`), the `concurrent_series` block defines the level-data numerator(s) and denominator(s). Keys match `^CS\d{3}(-[A-Z][0-9]?)?$` and the CS number mirrors the parent series number (`S026` -> `CS026-N`, `CS026-D`).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Human-readable component name. |
| `source_table` | string | yes | Series ID of the source table (e.g., `"S208"`). |
| `source_column` | string | yes | Subseries column ID in that table. |
| `combined_column` | string | no | Spliced/extended column ID. |
| `component_type` | enum | yes | `"numerator"` or `"denominator"`. |
| `units` | string | yes | Component units. |
| `formula_role` | string | no | One-line description of the role in the parent formula. |

Multi-part ratios use suffixes `-N2`, `-D2`, etc. Example (the reference project `S026`, lines 3143-3180):

```json
"concurrent_series": {
  "CS026-N": {
    "name": "Corporate Profits (Pcorp)",
    "source_table": "S208",
    "source_column": "S208AE",
    "combined_column": "S208AE_COMBINED",
    "component_type": "numerator",
    "units": "$billions",
    "formula_role": "Numerator of rcorp = Pcorp / KNCcorp(-1)"
  },
  "CS026-D": { "...": "..." }
}
```

Processing scripts must extract CS columns into `data_dict` and Anu Chopped writers include them in the chopped CSV.

---

## Figures Block

The top-level `figures` map (keys `Fig{C}.{N}[A-Z]?`) describes each visualization's data binding.

| Field | Type | Required | Description |
|---|---|---|---|
| `chapter` | integer | yes | Chapter number. |
| `page` | integer | no | Page in the underlying work. |
| `caption` | string | yes | Figure caption. |
| `type` | enum | no | `time_series` \| `cross_sectional` \| `scatter` \| `scatter_plot` \| `bar_chart` \| `line_chart` \| `grouped_bar_chart` \| `distribution` \| `theoretical`. |
| `y_scale` | enum | no | `linear` \| `log` \| `logarithmic`. |
| `columns` | object | yes | Map of role -> `{series, subseries, label}`. |
| `axes` | object | no | `{x: {label, range}, y: {label, scale, range, format}}`. |
| `transforms` | array | no | Figure-level transforms (e.g., `normal_capacity`). |
| `source_file` | string | no | Override source CSV for cross-sectional figures. |

Example (the reference project `Fig2.1`, lines 12389-12415):

```json
"Fig2.1": {
  "chapter": 2,
  "page": 57,
  "caption": "US Industrial Production Index, 1860-2010",
  "type": "time_series",
  "y_scale": "log",
  "columns": {
    "IndProd": { "series": "S001", "label": "Industrial Production Index" }
  },
  "axes": {
    "x": { "label": "Year", "range": [1860, 2010] },
    "y": { "label": "Index", "scale": "logarithmic" }
  },
  "transforms": []
}
```

---

## Sources Block

The top-level `sources` map records every primary or secondary source cited by `source_refs` arrays elsewhere in the registry. Key must equal the entry's `ref_id`.

| Field | Type | Required | Description |
|---|---|---|---|
| `ref_id` | string | yes | Equal to map key. |
| `type` | enum | yes | `government_publication` \| `journal_article` \| `book` \| `database` \| `dataset` \| `working_paper` \| `press_release` \| `other`. |
| `author` | string | recommended | Author or institution. |
| `title` | string | recommended | Title. |
| `year` | integer or null | no | Publication year. |
| `publisher` | string | no | Publisher. |
| `note` | string | no | Pin-cite / table reference. |
| `url` | string | no | Canonical URL. |

Example (the reference project `BEA_1966_LTEG`, lines 15214-15223):

```json
"BEA_1966_LTEG": {
  "ref_id": "BEA_1966_LTEG",
  "type": "government_publication",
  "author": "Bureau of Economic Analysis",
  "title": "Long Term Economic Growth, 1860-1970",
  "note": "BEA LTEG 1860-1970, TA15 p.185",
  "year": 1966,
  "publisher": "U.S. Department of Commerce",
  "url": "https://fraser.stlouisfed.org/title/long-term-economic-growth-1860-1970-5494"
}
```

---

## Enumerations

| Enum | Allowed values | Notes |
|---|---|---|
| `data_type` (series) | `time_series`, `cross_sectional`, `cross_sectional_panel`, `panel`, `quarterly`, `quarterly_annualised`, `mixed`, `placeholder`, `theoretical`, `derived` | Pipeline gating: only `time_series` flows through extension. |
| `content_type` (series, framework-rules alias) | `time_series`, `cross_sectional`, `theoretical`, `derived` | Recorded in `.claude/rules/anu-framework.md`. |
| `tier` | `1`, `2` | 1 = composite analytical; 2 = raw input table. |
| `confidence` (subseries) | `high`, `medium`, `low` | Used by anu-review D9. |
| `transform.type` | `reindex`, `reindex_to_match`, `splice`, `calculated`, `ratio`, `complement`, `fitted_curve`, `annual_average`, `deflate` | Some projects also use `combined`; emit `calculated` instead. |
| `construction[].op` | `load`, `reindex`, `reindex_to_match`, `splice`, `calculate`, `rescale`, `extract`, `extend`, `verify`, `transpose`, `output`, `normal_capacity`, `aggregate`, `combine` | `aggregate`/`combine` reserved; prefer `calculate`. |
| `extension.frequency` | `annual`, `quarterly`, `monthly`, `daily`, `weekly` | |
| `extension.aggregation` | `annual_average`, `annual_sum`, `end_of_period`, `start_of_period`, `null` | `null` when source is already annual. |
| `extension.splice_method` | `growth_rate`, `direct`, `level`, `ratio` | `growth_rate` is the default; only valid when the original was itself directly observed (see `anu-framework.md` "No Lazy Splices"). |
| `extension.vintage_policy` | `latest`, `specific`, `alfred` | |
| `concurrent_series_component.component_type` | `numerator`, `denominator` | |
| `figure.type` | `time_series`, `cross_sectional`, `scatter`, `scatter_plot`, `bar_chart`, `line_chart`, `grouped_bar_chart`, `distribution`, `theoretical` | |
| `figure.y_scale` | `linear`, `log`, `logarithmic` | `log` and `logarithmic` are accepted aliases. |
| `source.type` | `government_publication`, `journal_article`, `book`, `database`, `dataset`, `working_paper`, `press_release`, `other` | |

### Review-score / certification levels

The registry itself does not currently carry a per-series `review_score`. Quality scoring lives in the anu-review artifacts and the Anu Ledger. When future versions surface a certification field, the canonical levels are:

| Level | Meaning |
|---|---|
| `gold` | All 13 anu-review dimensions pass; KB-verified. |
| `silver` | D1-D8 pass; data authenticity verified; minor doc gaps. |
| `bronze` | Constructed and validated; documentation incomplete. |
| `provisional` | Constructed but unverified against source. |
| `data_unavailable` | No data; series marked as unavailable per anu-framework rule. |

---

## Required Cross-Field Invariants

Validators SHOULD enforce these beyond the JSON Schema:

1. Every subseries ID under `series[X].subseries` MUST start with the parent series ID and a dash, or equal the parent ID exactly (for the base output column).
2. Every `extension.output_subseries` MUST match `^{parent}-EXT$`; every `extension.combined_subseries` MUST match `^{parent}-COMBINED$`.
3. Every value in a `source_refs` array MUST be a key in the top-level `sources` block.
4. Every `figures[]` entry on a series MUST be a key in the top-level `figures` block (when `figures` is present).
5. When `proxy = true`, `proxy_justification` MUST be a non-empty string.
6. When `extension` is non-null, `data_type` MUST be `time_series` (extensions do not apply to cross-sectional or theoretical series).
7. When `derived_from` is non-null, `transform` MUST be non-null and `transform.type` MUST be set.
8. Every subseries MUST have non-null `name`, `period`, and `units` (CRITICAL fields). The Anu Chopped `SUBSOURCE_METADATA.json` generator emits warnings for any null.

---

## Version and Migration

| Schema version | Notable changes | Migration |
|---|---|---|
| `1.x` (deprecated) | `S001A` form, no `sources` block, no `concurrent_series`. | Run `/anu-ingestion migrate-ids` to rewrite series IDs to v2.0 dash notation. Hand-author a `sources` block from existing free-text citations. |
| `2.0.0` (current) | Top-level `sources` block with `SRC-*`-style ref IDs, per-subseries `source_refs`, `concurrent_series` for ratio series, `tier` field, `data_type` enum, `extension.provenance` sub-object. | Native. |

A future `2.1.0` is expected to add an explicit `review_score`/`certification` field at the series level, formalize `aggregate`/`combine` ops as distinct from `calculate`, and tighten `transform.type` to require either `input` or `inputs`.

---

## Validation

Validate any candidate registry against the JSON Schema at:

`schemas/series_registry.schema.json`

Reference command (Python):

```python
import json, jsonschema
schema   = json.load(open("schemas/series_registry.schema.json"))
registry = json.load(open("Projects/<proj>/Technical/series_registry.json"))
jsonschema.Draft202012Validator(schema).validate(registry)
```

The reference implementation `Projects/the reference project/Technical/series_registry.json` is the canonical sample-of-truth and is expected to validate cleanly. When this spec and the schema disagree with the the reference project registry, the registry wins until the next dated revision of this document.
