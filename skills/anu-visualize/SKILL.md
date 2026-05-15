---
name: anu-visualize
version: "5.0"
description: Interactive visualization standard supporting R Shiny + Plotly and Plotly Dash. Registry-driven multi-source charts with chopped data, methodology panels, author quotes, extension data, dual-axis support, L00/P00 data pipeline, and data validation. Use when building, configuring, or reviewing data visualization apps.
when-to-use: User needs to build interactive visualizations, create Plotly Dash charts, or configure R Shiny data apps
search-hints: visualize plotly visualization chart interactive dashboard app data plot shiny dash
argument-hint: [action] [target]
allowed-tools: Read, Write, Grep, Glob, LS, Shell
requires: anu-chopped, anu-replicator
part-of: Anu Framework v11.0
---

# Anu Visualize Standard v5.0

*Renamed from Anu Shiny v4.3. Supports both R Shiny + Plotly and Plotly Dash frameworks.*

Interactive visualization for data construction projects. The app is registry-driven: all trace labels, colors, metadata panels, and construction details come from canonical JSON files (series catalog, subsource metadata, series linkage, and optionally project-specific files like author quotes).

---

## Supported Frameworks

| Framework | Language | Use Case | Example |
|-----------|----------|----------|---------|
| **R Shiny + Plotly** | R | Full-featured data exploration with methodology panels | CD2 ShinyApp |
| **Plotly Dash** | Python | Lightweight visualization, Python-native projects | CD2 ANU_VIZ |

The standard is framework-agnostic — the same canonical JSON files, data pipeline, and quality checklist apply regardless of framework choice.

---

## Application Structure

```
Technical/ShinyApp/                    # (R Shiny variant)
+-- app.R                              # Main Shiny app (UI + server logic)
+-- global.R                           # Global setup, library loads
+-- [PROJECT].Rproj                    # RStudio project file
+-- L00.py                             # Master data loader orchestrator
+-- P00.py                             # Master data processor orchestrator
+-- R/
|   +-- data_loader.R                  # Load all JSON/CSV data at startup
|   +-- chart_builder.R               # Plotly chart construction
|   +-- helpers.R                      # safe_field(), safe_str(), UI helpers
|   +-- validate_data.R               # Startup data integrity checks
|   +-- config.R                       # Path resolution ([PROJECT]_PATHS)
|   +-- data_loader_standards.R        # Loading standards/conventions
|   +-- logger.R                       # Structured logging
+-- scripts/
|   +-- loading/                       # Per-chapter loader scripts (L01-L##)
|   +-- processing/                    # Per-chapter processor scripts (P01-P##)
+-- config/
|   +-- app_config.json                # Color palettes, figure registries
+-- data/
|   +-- [SOURCE]/                      # Project-specific absorbed data
|       +-- catalogs/                  # Canonical JSON metadata files
|       +-- chapter_XX_extended.csv    # Wide-format chapter data
|       +-- DATA_MANIFEST.json         # SHA-256 manifest
+-- tests/                             # Validation scripts
+-- logs/                              # Runtime log files
+-- docs/                              # Series mapping documentation
```

---

## Canonical Data Files (Single Sources of Truth)

| File | Purpose | Key Fields |
|------|---------|------------|
| `DEFINITIVE_SERIES_CATALOG.json` | Master series metadata | series_id, name, chapter, figure_ids, time_period, extension_status, subsource_ids |
| `SUBSOURCE_METADATA.json` | Per-subsource metadata | subsource_id, column_name, source_name, source_text, source_url, period, role, is_construction_member, is_extension, parent_series |
| `HDARP_SERIES_LINKAGE.json` | Figure-to-series-to-data mapping | figure_id, chapter, page_number, full_caption, hdarp_variables, linked_series, data_columns, axis specs, year_range |
| `[PROJECT]_QUOTES_MASTER.json` | Author quotes organized by chapter/figure (optional) | quotes_by_chapter, page_number, text, topic_tags |
| `config/app_config.json` | App configuration | color_palettes, figure_column_map, figure_file_registry, figure_cross_chapter, figure_highlight_series |

### JSON Loading Rules

ALL `fromJSON()` calls MUST use `simplifyVector = FALSE` and `simplifyDataFrame = FALSE` to prevent jsonlite from converting nested lists to atomic vectors.

### figure_column_map.json Loading

Supports two JSON formats:
- **Wrapped format**: `{ "figure_column_map": { "Fig2.1": [...], ... } }`
- **Flat format**: `{ "Fig2.1": [...], ... }`

Uses dual-path resolution, checking `[PROJECT]_PATHS$anu_visualize` first (ANU_REPLICATOR output), then `[PROJECT]_PATHS$catalogs` (app catalogs).

---

## Chart Types

### 1. Chopped Chart (`build_chopped_chart`)
Multi-source chart for series with subsource breakdowns. Each subsource gets its own trace with descriptive labels.

### 2. Time Series Chart (`build_time_series_chart`)
Standard time series from extended chapter CSVs. Supports single and multi-column figures.

### 3. Sector Overlay Chart
For figures with >10 series: semi-transparent gold traces with a bold white highlight series.

### 4. Scatter Chart (`build_scatter_chart`)
Log-log scatter plots with 45-degree reference lines.

### 5. Dual-Axis Support
Subsources are grouped by units. When two distinct unit types are detected, a secondary Y-axis is added.

---

## UI Panels

### Methodology Panel
Book figure reference, construction formula (LaTeX), HP filter lambda, source documents, construction narrative.

### Author Quotes Panel
Quotes from the project's quotes master JSON with page references.

### Extension Panel
Extension status, pull date, and API sources.

### Data Table
Interactive table with CSV download functionality.

### Series Browser
Browse all series by chapter with summary cards.

---

## View Modes

| Mode | Filter Logic | Shows |
|------|-------------|-------|
| Full View | Show composite + all segments | Default: everything |
| All Sources | All segment columns | Every subsource trace + composite overlay |
| Final Series | Composite column only | Single final series line |
| Author Construction | `is_construction_member == true` | Only author's original subsources |
| Final Extension | `is_extension == true` | Only extension data |
| Individual | Match by subsource ID | User-selected subsources |
| Show Components | `is_component == true` | Concurrent Series (CS) level-data inputs on dual Y-axis |

### Anti-Patterns (DO NOT)

- DO NOT check `api` field to determine if something is an extension — use `is_extension` boolean
- DO NOT use `source_name` string matching to categorize subsources
- DO NOT default to showing all subsources when a filter returns empty — show informational message
- DO NOT mix CS component columns with regular subsource columns in standard view modes

---

## Safe Field Access Pattern

All field accesses in UI rendering MUST use defensive helpers:

```r
safe_field(obj, "field_name", default = NULL)
safe_str(obj, "field_name", default = "")
```

All `renderUI` blocks MUST be wrapped in `tryCatch`.

---

## Data Validation (Startup)

The app runs `validate_app_data()` at startup:

1. **Structural checks**: All canonical JSON files exist and loaded
2. **Cross-reference integrity**: subsource parent_series exist in catalog
3. **Value sanity**: year ranges valid, chapters in range
4. **Chart readiness**: figures have data column mappings
5. **Manifest verification**: SHA-256 hash comparison

---

## Quality Checklist (Pre-Launch)

- [ ] **Q1: All charts render** — No "Error building chart" messages
- [ ] **Q2: No console errors** — No `$operator is invalid` or runtime errors
- [ ] **Q3: Methodology panels populate** — Figure number, page, construction info visible
- [ ] **Q4: Author quotes display** — With page numbers, no rendering errors (if applicable)
- [ ] **Q5: Extension data visible** — Extension subsources appear as separate traces
- [ ] **Q6: Year ranges correct** — Chart X-axis matches data extent
- [ ] **Q7: Trace labels descriptive** — Labels show data description, not code names
- [ ] **Q8: Data tables complete** — Download CSV produces full data
- [ ] **Q9: Validation passes** — `validate_metadata_completeness.py` exits with code 0
- [ ] **Q10: Startup validation** — `validate_app_data()` reports 0 errors
- [ ] **Q11: Source URLs present** — Every extension subsource has a `source_url`
- [ ] **Q12: Source links clickable** — Subsource details panel renders clickable links

---

## Year Range Filtering Safety

1. Only apply when the metadata range overlaps with the actual data range
2. Only apply when the filter would keep <70% of rows
3. Never narrow data to a range that doesn't match available data

---

## Color Palettes

Colors are loaded from `config/app_config.json`:
- **Accent color**: GBA Purple `#543c8a`
- `sources`: BEA=#1f77b4, FRED=#2ca02c, MeasuringWorth=#ff7f0e, etc.
- `multi_series`: Gold, cyan, orange, green, red, purple cycle
- `subsource`: Extended 16-color palette for chopped charts
- `status`: verified=#28a745, partial=#ffc107, needs_review=#dc3545

---

## Data Pipeline (L00/P00)

- **`python L00.py`** — Runs all `scripts/loading/L##_ch*.py` loaders
- **`python P00.py`** — Runs all `scripts/processing/P##_ch*.py` processors
- Both support chapter filtering: `python P00.py ch05 ch07`
- Results logged to `data/logs/LOAD_LOG.json` and `data/logs/PROCESS_LOG.json`

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-visualize init [project]` | Scaffold visualization app structure |
| `/anu-visualize validate` | Run metadata completeness validation |
| `/anu-visualize check-quality` | Run quality checklist interactively |

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Chopped** | App loads chopped CSVs for detailed subseries data |
| **Anu Replicator** | Reads chapter CSVs and catalog from `data/final-data/shiny/` |
| **Anu Extension** | Extension subsources must appear as visible chart traces |
| **Anu Review** | D10 Viz Quality dimension scores app completeness |

---

## Anu Framework Context

- **Pipeline Stage**: 5b (VIZ EXPORT) + 6 (VIZ)
- **Upstream**: Stage 5 Output (Chopped CSVs, catalogs, SUBSOURCE_METADATA.json)
- **Downstream**: Stage 6 Review (D10 Viz Integration)
- **Adequacy Relevance**: L5 (Validation Data) — viz enables visual validation against published figures

## Version History

- **v1.0** (January 2026) — Initial R Shiny implementation (as "Anu Shiny")
- **v2.0** (March 2026) — Registry-driven design, multi-source charts
- **v3.0** (March 2026) — Quality checklist, safe field access, chart-readiness validation
- **v4.0** (March 2026) — Generalized: removed project-specific hardcoding, added Components view mode
- **v4.3** (April 2026) — Anu Framework v6.0 compatibility
- **v5.0** (May 2026) — Renamed from Anu Shiny to Anu Visualize. Added Plotly Dash as supported framework. Anu Framework v7.0 integration.

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | Visualization app, validated data views |
| **Expects** | Canonical JSON files, HDARP chapter files, chopped CSVs, chapter extended CSVs |
| **Must Validate** | All 12 quality checklist items before marking app as ready |

---

## Example: CD2 Project

| Placeholder | CD2 Value |
|-------------|-----------|
| `[PROJECT]` | `CD2` |
| `[SOURCE]` | `ShaikhAbsorbed` |
| `SUBSOURCE_METADATA.json` | `SHINY_SUBSOURCES.json` (116 subsources) |
| `[PROJECT]_QUOTES_MASTER.json` | `SHAIKH_QUOTES_MASTER.json` |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Interactive Visualization*
*Lineage: Anu Shiny v1.0-v4.3 -> Anu Visualize v5.0*
