---
name: anu-replicator
version: "3.1"
description: Self-contained, versioned replication package with four-phase architecture (Loading L## + Processing P## + Validation V## + Manual Adjustment M##). v3.1 prescribes a `lib/` shared-helpers layout (`lib/data/`, `lib/transforms/`, `lib/validation/`, `lib/io/`) so cross-series patterns (BookColumnLoader, BenchmarkValidator, cached-API readers, IO matrix utilities) live in one canonical place rather than being re-implemented per series. A single orchestrator script reproduces all data series without agent intervention; includes hash audit trail and exploration scripts.
when-to-use: User needs to build or run a self-contained replication package, create reproducible data pipelines, bundle data construction code, or organize shared helpers across L##/P##/V## scripts.
search-hints: replicator reproduce package loading processing script bundle reproducible lib helpers shared utilities loader validator cache
argument-hint: [action] [target]
allowed-tools: Read, Write, Grep, Glob, LS, Shell
requires: anu-ingestion, anu-research, anu-extension
part-of: Anu Framework v11.0
---

# Anu Replicator Standard v3.1

A **versioned, self-contained replication package** with a four-phase architecture (Loading, Processing, Validation, Manual Adjustment). No agent is needed to run the replicator — a researcher clones the package, sets API keys, runs `python replicate.py`, and gets complete, validated output with a full SHA-256 hash audit trail.

---

## Design Philosophy

1. **Self-contained**: All inputs, code, and configuration in one package
2. **Four-phase**: Loading (L##), Processing (P##), Validation (V##), and Manual Adjustment (M##) are cleanly separated
3. **Numbered scripts**: Execution order is explicit via L##, P##, V##, and M## numbering
4. **Registry-driven**: `series_registry.json` is the single source of truth
5. **Dynamic paths**: All paths resolved via `pathlib`, no hardcoded paths
6. **Detailed reporting**: Every series prints construction tree, validation status, and coverage
7. **Graceful degradation**: Missing API keys skip affected series, never crash the whole run
8. **No synthetic data**: Every value must come from a real source. If data is unavailable, the series is marked `data_unavailable` — never filled with estimated trends, random noise, or interpolated placeholders. Missing data is missing, not fabricated.

---

## Public Distribution Requirements

When a replicator package is intended for public release (GitHub, journal submission):

### Data Acquisition Priority

L## scripts acquire data in this priority order:
1. **PUBLIC API** (FRED, BEA, BLS, World Bank) — always try first
2. **DOWNLOADED FILE** — if API unavailable (document exact URL)
3. **HDARP EXTRACTION** — last resort (methodology text from book PDF)

### L## Script Docstring Standard

Every loading script must include:
```python
"""
L##: [Series Name]
Phase: Loading
Source: [Institution]
Series/Table: [Identifier]
Public URL: [Direct link]
API: [Name] (free key: [registration URL])
Fallback: [Manual download instructions]
Original Data: http://www.anwarshaikhecon.org/
"""
```

### README Requirements

Project README must include:
1. **Prerequisites**: Python version, `pip install -r requirements.txt`
2. **API Keys**: List all required keys with FREE registration links
3. **Quick Start**: `cp config/api_keys.env.example config/api_keys.env` → edit → `python replicate.py`
4. **Data Sources Table**: Institution, API, URL, series used
5. **License**: Data usage terms

### .gitignore (MANDATORY)

Must exclude: `api_keys.env`, `data/raw-data/api/`, `__pycache__/`

See `docs/GIT_PROTOCOL.md` for the full standard.

---

## Two-Phase Architecture

### Phase 1: Loading (L## scripts)

**Purpose**: Acquire all data — parse user-provided files and fetch API data.

**Input**: `data/user-inputs/` (read-only, human-provided)
**Output**: `data/raw-data/` (machine-fetched, never hand-edited)

Scripts in `scripts/loading/`:

| Script | Description |
|--------|-------------|
| `L00_load_all_data.py` | Orchestrator: discovers and runs all L## scripts in order |
| `L01_load_[name].py` | Loads a specific series (e.g., `L01_load_industrial_production.py` for S001) |
| `L02_load_[name].py` | Next series... |
| ... | One L## per series |

Each L## script:
1. Reads `series_registry.json` for its series config
2. Parses user-provided Chopped CSV from `data/user-inputs/chopped/`, validates, writes to `data/raw-data/parsed/S###_parsed.csv`
3. If API extension configured: fetches raw data, saves to `data/raw-data/api/{API}_{SERIES_ID}_{YYYYMMDD}.json`
4. If manual download required: checks `data/user-inputs/chopped/` for file, warns if missing
5. Returns `LoadResult(series_id, status, obs_count, vintage_date, output_files)`

`L00` writes `data/raw-data/LOAD_LOG.json`:

```json
{
  "run_date": "2026-03-07T14:30:00Z",
  "results": [
    {
      "series_id": "S001",
      "status": "SUCCESS",
      "chopped_parsed": "parsed/S001_parsed.csv",
      "api_file": "api/FRED_INDPRO_20260307.json",
      "vintage_date": "2026-03-07",
      "obs_count": 1272
    }
  ]
}
```

### Phase 2: Processing (P## scripts)

**Purpose**: Construct, extend, validate, and format all data series.

**Input**: `data/user-inputs/` + `data/raw-data/`
**Output**: `data/final-data/`

Scripts in `scripts/processing/`:

| Script | Description |
|--------|-------------|
| `P00_process_all_data.py` | Orchestrator: discovers and runs all P## scripts in order |
| `P01_process_[name].py` | Processes a specific series |
| ... | One P## per series |

Each P## script:
1. Reads `series_registry.json` for construction steps and transforms
2. Loads parsed data from `data/raw-data/parsed/`
3. Loads API data from `data/raw-data/api/`
4. Loads research notes from `data/user-inputs/research/S###_research.json`
5. Executes construction steps in order, verifying each transform against the registry formula
6. Extends with API data using configured splice method
7. **Adds extension columns to `data_dict`**: For every extended series, the P## script must add both `S###-EXT` (raw API data from splice year onward) and `S###-F` (re-indexed API data overlapping with the previous subsource at the splice point) to the `data_dict` before writing chopped CSVs. Formula: `S###-F[t] = prev_subsource[splice_year] * (API[t] / API[splice_year])`
8. Validates against reference values
9. Writes to `data/final-data/series/S###_final.csv`
10. Writes Anu Chopped CSV to `data/final-data/chopped/`
11. Writes Anu Extenbook Excel to `data/final-data/extenbooks/`
12. **Returns result dict including `data_dict`** — a mapping of subseries IDs to pandas Series. This is consumed by the Visualization Export phase.

`P00` writes `data/final-data/PROCESS_LOG.json` (with SHA-256 hashes and timing per series) and `REPLICATION_REPORT.md`.

#### `data_dict` Return Contract

Every P## script **must** include `result["data_dict"] = data_dict` before returning. The `data_dict` maps subseries IDs (e.g., `"S026-A"`) to their pandas Series objects. The Visualization Export phase depends on this to produce chapter-level CSVs with aliased column names.

**Extension column requirement**: For extended series, `data_dict` must include both `S###-EXT` (raw API data) and `S###-F` (re-indexed extension data) in addition to the original subsources. These columns are written into the chopped CSV and consumed by the Shiny app for extension trace visibility.

**Registry completeness requirement**: The `SUBSOURCE_METADATA.json` generated during viz export depends on every subseries in `series_registry.json` having non-null `period`, `units`, and `name` fields. Missing fields cause degraded visualization labels (e.g., "?-?" instead of "1860-2010"). Agents must validate registry completeness before running the viz export.

### Phase 3: Validation (V## scripts)

**Purpose**: Verify all processed data against reference values, range checks, continuity constraints, and hash integrity before producing final outputs.

**Input**: `data/final-data/` (P## outputs)
**Output**: `data/final-data/VALIDATION_REPORT.json`

Scripts in `scripts/validation/`:

| Script | Description |
|--------|-------------|
| `V00_validate_all.py` | Orchestrator: discovers and runs all V## scripts in order |
| `V01_reference_values.py` | Compare outputs against published reference values |
| `V02_range_checks.py` | Verify all values fall within expected bounds |
| `V03_continuity.py` | Check year-over-year continuity (no unexplained jumps) |
| `V04_completeness.py` | Verify no missing years or unexpected NaN gaps |
| `V05_cross_series.py` | Validate cross-series consistency constraints |
| `V06_splice_quality.py` | Assess splice point transition quality for extended series |
| `V07_extension_overlap.py` | Verify extension overlap period correlation |
| `V08_hash_integrity.py` | SHA-256 hash verification of all input and output files |

Each V## script returns a `ValidationResult(script_id, status, checks_passed, checks_failed, details)`. `V00` aggregates results into `VALIDATION_REPORT.json`.

### Phase 4: Manual Adjustment (M## scripts)

**Purpose**: Apply documented, justified manual adjustments to processed data when automated processing cannot fully replicate the original construction.

**Input**: `data/final-data/` (P## outputs, validated by V##)
**Output**: `data/final-data/` (adjusted files), `ADJUSTMENT_MANIFEST.json`

Scripts in `scripts/manual/`:

| Script | Description |
|--------|-------------|
| `M00_apply_all_adjustments.py` | Orchestrator: discovers and runs all M## scripts in order |
| `M01_adjust_[name].py` | Apply specific documented adjustment |
| ... | One M## per adjustment |

Every manual adjustment MUST be documented in `config/ADJUSTMENT_MANIFEST.json`:

```json
{
  "adjustments": [
    {
      "id": "M01",
      "series_affected": ["S001"],
      "description": "Correct splice discontinuity at 1947",
      "justification": "Original author applied manual correction per appendix note",
      "decision_ref": "<decision-ref>"
    }
  ]
}
```

### Phase 5: Exploration (E## scripts)

**Purpose**: Standalone exploration and analysis scripts that are never deleted. Used for ad-hoc investigation, sensitivity analysis, or alternative methodology exploration.

Scripts in `scripts/exploration/`:

| Script | Description |
|--------|-------------|
| `E01_explore_[topic].py` | Standalone exploration script |
| ... | Any number of E## scripts |

E## scripts are **not run by the orchestrator** (`replicate.py` does not call them). They are standalone, self-documenting scripts that agents or researchers run manually. They are preserved indefinitely as part of the research record.

### Phase 6: Visualization Export

**Purpose**: Produce downstream-ready output files (chapter CSVs, series catalog, per-figure CSVs) that visualization apps consume directly.

**Input**: Processing results (`data_dict` from each P## script) + `series_registry.json`
**Output**: `data/final-data/shiny/` and `data/final-data/figures/`

This phase runs automatically after Processing in `replicate.py`. It uses the `viz_column` alias from the registry to rename subseries IDs to semantic column names that visualization apps expect.

| Writer | Output | Description |
|--------|--------|-------------|
| `shiny_writer.py` | `shiny/chapter_NN.csv` | Wide CSV per chapter: Year + aliased columns |
| `shiny_writer.py` | `shiny/series_catalog.json` | Machine-readable series catalog for the viz app |
| `subsource_metadata_writer.py` | `shiny/SUBSOURCE_METADATA.json` | Per-column metadata + construction text for viz (see Anu Chopped v1.3) |
| `generate_shiny_subsources.py` | `shiny/SUBSOURCE_METADATA.json` | Per-subsource metadata with `is_extension: true` for extension columns; auto-copied to the project's visualization app catalogs directory |
| `figure_writer.py` | `figures/FigN.M.csv` | Per-figure CSV with transforms applied (HP filter, normal-capacity, etc.) |

#### Column Aliasing via `viz_column`

The registry supports a `viz_column` field (also called `shiny_column` in existing implementations) at two levels:

- **Series level** (for single-column composites): `series.S001.viz_column = "IndProd"`
- **Subseries level** (for multi-column figure series): `series.S026.subseries.S026-A.viz_column = "rcorp"`

The visualization export writer reads `data_dict`, looks up each subseries's `viz_column` alias, and writes the chapter CSV with those aliases as column headers. Only aliased columns are included — raw subseries IDs are omitted from the chapter CSV.

---

## Folder Structure

```
ANU_REPLICATOR_v2.0.0/
+-- README.md                           # Complete instructions
+-- VERSION                             # "2.0.0"
+-- requirements.txt                    # Pinned Python dependencies
+-- replicate.py                        # Master orchestrator (runs L00 then P00)
+--
+-- config/
|   +-- series_registry.json            # THE single source of truth
|   +-- api_config.json                 # API endpoints, rate limits
|   +-- api_keys.env.example            # Template for API keys
|   +-- validation_config.json          # Tolerance thresholds
+--
+-- data/
|   +-- user-inputs/                    # Human-provided, READ-ONLY during replication
|   |   +-- README.md
|   |   +-- chopped/                    # Original Chopped CSVs
|   |   +-- provenance/                 # DPRs, citations, methodology
|   |   +-- research/                   # S###_research.json files
|   |   +-- INPUT_MANIFEST.md
|   +-- raw-data/                       # L## output, never hand-edit
|   |   +-- README.md
|   |   +-- api/                        # Raw API responses (vintage-dated)
|   |   +-- parsed/                     # Parsed Chopped CSVs
|   |   +-- LOAD_LOG.json
|   +-- final-data/                     # P## output, the deliverables
|       +-- README.md
|       +-- series/                     # Individual series CSVs
|       +-- chopped/                    # Regenerated Chopped CSVs
|       +-- extenbooks/                 # Generated Extenbook Excel files
|       +-- combined/                   # Chapter-level databases
|       +-- shiny/                      # Visualization export (chapter CSVs + catalog + SUBSOURCE_METADATA.json)
|       +-- figures/                    # Per-figure CSVs with transforms applied
|       +-- reports/                    # REPLICATION_REPORT.md
|       +-- logs/                       # Timestamped logs
|       +-- PROCESS_LOG.json
+--
+-- scripts/
|   +-- loading/                        # L00..L##
|   +-- processing/                     # P00..P##
|   +-- validation/                     # V00..V08
|   +-- manual/                         # M00..M##
|   +-- exploration/                    # E## (standalone, never deleted)
+--
+-- lib/                                # Shared library
|   +-- paths.py                        # Dynamic path resolution (pathlib)
|   +-- config_loader.py               # Load and validate series_registry.json
|   +-- registry_reader.py             # Query helper functions
|   +-- fetchers/                       # API fetcher modules
|   +-- transforms/                     # reindex, splice, aggregate, validate, filters
|   +-- formats/                        # chopped_writer, extenbook_writer, shiny_writer, figure_writer
|   +-- reporting/                      # console_reporter, report_generator
+--
+-- validation/
|   +-- reference_values/               # S###_reference.json per series
|   +-- expected_checksums.json
|   +-- tolerance_config.json
+--
+-- provenance/
|   +-- provenance_index.json           # Provenance index (by_source, by_api, by_series with lineage chains)
+--
+-- docs/
    +-- DECISION_LOG.md                 # <decision-ref> format decision records
    +-- ASSUMPTIONS.md                  # ASM-D/M/R category assumption records
```

---

## Master Orchestrator (replicate.py)

```
python replicate.py                      # Full run: L00 → P00 → V00 → M00
python replicate.py --load-only          # Just loading phase
python replicate.py --process-only       # Just processing (assumes raw-data exists)
python replicate.py --validate-only      # Just validation (assumes final-data exists)
python replicate.py --skip-validation    # Run L00 → P00 → M00, skip V00
python replicate.py --skip-manual        # Run L00 → P00 → V00, skip M00
python replicate.py --manual-only        # Just manual adjustments (assumes validated data)
python replicate.py --full               # Full run including viz export and ledger
python replicate.py --provenance         # Generate/update provenance_index.json
python replicate.py --series S001 S002   # Specific series only
python replicate.py --chapter 2          # All series in chapter
python replicate.py --dry-run            # Verify inputs, don't fetch APIs
python replicate.py --report             # Generate report from existing outputs
```

### Console Output Format

The orchestrator prints a detailed banner, per-series construction trees, and a summary table. See the Anu Framework plan document for the full console output specification.

Key elements:
- API key status check at startup
- Input file verification
- Per-series: subsource tree, construction verification, extension fetch, validation, status
- Summary: SUCCESS / PARTIAL / NO EXTENSION / FAILED counts
- Output file listing

---

## Dynamic Filepath Handling (lib/paths.py)

All paths use `pathlib.Path` relative to the package root:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER_INPUTS = ROOT / "data" / "user-inputs"
RAW_DATA    = ROOT / "data" / "raw-data"
FINAL_DATA  = ROOT / "data" / "final-data"
CONFIG      = ROOT / "config"
REGISTRY    = CONFIG / "series_registry.json"

def ensure_dirs():
    for d in [RAW_DATA / "api", RAW_DATA / "parsed",
              FINAL_DATA / "series", FINAL_DATA / "chopped",
              FINAL_DATA / "extenbooks", FINAL_DATA / "combined",
              FINAL_DATA / "shiny", FINAL_DATA / "figures",
              FINAL_DATA / "reports", FINAL_DATA / "logs"]:
        d.mkdir(parents=True, exist_ok=True)
```

---

## Error Handling

| Situation | Behavior |
|-----------|----------|
| API timeout | Retry 3x with exponential backoff, then mark PARTIAL |
| API key missing | Skip API-dependent series, mark PARTIAL with reason |
| Input file missing | Mark series FAILED with exact expected path |
| Validation failure | Series completes but flagged with specific failing checks |
| Manual download needed | Check if file exists, warn if not |
| Extension doesn't reach present | Print WARNING with reason and how many years short |
| Unicode encoding error (Windows) | See Platform Encoding Safety below |

### Platform Encoding Safety

On Windows, the default console encoding is cp1252, which cannot display many Unicode characters. Agents must:

- Avoid Unicode symbols in `notes`, `steps`, and strings printed via `pprint()` — use `'-'` instead of `'\u2212'` (Unicode minus), `'lambda'` instead of `'\u03bb'`
- Use `encoding='utf-8'` when writing text files (CSVs, reports, logs)
- If a `UnicodeEncodeError` occurs during console output, the data files are usually fine — fix the offending string and re-run

---

## Cross-Chapter Dependencies

When a P## script needs data from another chapter (e.g., Ch10's P18 loads Ch7's S215 parsed data, Ch10's P25 loads Ch6's S105 final data), follow these rules:

1. **Use `load_parsed()`** with the dependency series ID — the function resolves the path regardless of which chapter the series belongs to
2. **Document dependencies** in the processing script's docstring: `"Depends on: S215 (Ch7), S105 (Ch6)"`
3. **Record in the registry** using the `source_series` field: `"source_series": ["S215", "S105"]`
4. **Pipeline ordering**: The loading phase for the dependency chapter must have run before the dependent chapter's processing phase. The pipeline should validate this.
5. **Cross-chapter dependencies do not require re-running the dependency chapter** — only the parsed CSVs need to exist in `data/raw-data/parsed/`

---

## Concurrent Series (CS) in Processing Scripts

When a series is a **ratio or rate**, its P## script must also extract the **level-data components** (numerator and denominator) as Concurrent Series (CS) columns. This is defined by the `concurrent_series` block in `series_registry.json`.

**Pattern for P## scripts:**

1. Define a `CS_COLUMN_MAP` dict alongside the standard `COLUMN_MAP`, mapping CS IDs (e.g., `CS026-N`) to their source table columns
2. After the standard extraction loop, iterate over `CS_COLUMN_MAP` and extract each component using the same combined/raw fallback logic
3. Add CS columns to `data_dict` — they will be included in the chopped CSV automatically by `chopped_writer`

**Example (P09 for S026):**
```python
CS_COLUMN_MAP = {
    "CS026-N":  {"table": "S208", "raw": "S208AE", "combined": "S208AE_COMBINED", "label": "Pcorp"},
    "CS026-D":  {"table": "S208", "raw": "S208AT", "combined": "S208AT_COMBINED", "label": "KNCcorp"},
}
```

CS columns are transparent to existing subsource views (filtered out by `is_component: true` flag) and only shown in the "Show Components" view mode.

---

## Registry Sync Protocol

The series registry exists in two locations:

| Location | Role | Read By |
|----------|------|---------|
| `Technical/series_registry.json` | **Canonical** — the single source of truth | Ledger generator, agents, documentation |
| `config/series_registry.json` | **Mirror** — copy inside the Replicator package | `config_loader.py` (with fallback to canonical) |

**Best practice**: Always modify `Technical/series_registry.json`. The Replicator's `lib/paths.py` resolves the canonical path, so `replicate.py` reads from it directly. The `config/` mirror exists for self-contained package distribution. After modifying the canonical registry, copy to `config/` to keep them in sync, or rely on the fallback path resolution.

---

## Agent Orientation

Every folder has a `README.md` explaining:
1. What this folder contains
2. What puts files here (which script, which phase)
3. What reads from here
4. Whether contents are human-provided or machine-generated
5. Whether contents should be edited by hand

---

## Naming Convention for Scripts

| Pattern | Phase | Example |
|---------|-------|---------|
| `L00_load_all_data.py` | Loading orchestrator | Always L00 |
| `L{NN}_load_{series_name}.py` | Loading script | `L01_load_industrial_production.py` |
| `P00_process_all_data.py` | Processing orchestrator | Always P00 |
| `P{NN}_process_{series_name}.py` | Processing script | `P01_process_industrial_production.py` |
| `V00_validate_all.py` | Validation orchestrator | Always V00 |
| `V{NN}_{check_name}.py` | Validation script | `V01_reference_values.py` |
| `M00_apply_all_adjustments.py` | Manual adjustment orchestrator | Always M00 |
| `M{NN}_adjust_{name}.py` | Manual adjustment script | `M01_adjust_splice_correction.py` |
| `E{NN}_explore_{topic}.py` | Exploration script (standalone) | `E01_explore_alternative_splice.py` |

Script names include the series name (not just the number) for human readability. The number determines execution order.

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-replicator init [project]` | Scaffold replicator package structure |
| `/anu-replicator bundle [chapter]` | Bundle user-inputs for a chapter |
| `/anu-replicator create-loader [series_id]` | Generate L## script for a series |
| `/anu-replicator create-processor [series_id]` | Generate P## script for a series |
| `/anu-replicator run` | Execute replicate.py |
| `/anu-replicator run --load-only` | Execute loading phase only |
| `/anu-replicator run --process-only` | Execute processing phase only |
| `/anu-replicator validate` | Verify package completeness |

---

## Templates

- `templates/L_SCRIPT_TEMPLATE.py` — Loading script template
- `templates/P_SCRIPT_TEMPLATE.py` — Processing script template
- `templates/ORCHESTRATOR_TEMPLATE.py` — Orchestrator script template
- `templates/REPLICATOR_README_TEMPLATE.md` — Package README template

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Research** | research.json files bundled in `data/user-inputs/research/` |
| **Anu Ingestion** | series_registry.json and DPRs bundled in `data/user-inputs/` |
| **Anu Extension** | Extension methodology defined by Extension skill, implemented in P## scripts |
| **Anu Chopped** | P## scripts write Chopped CSVs using `chopped_writer.py` |
| **Anu Extenbook** | P## scripts write Extenbook Excels using `extenbook_writer.py` |
| **Anu Visualize** | Viz export writes chapter CSVs, catalog, and `SUBSOURCE_METADATA.json` to `data/final-data/shiny/`; auto-copies to the project's visualization app catalogs directory; downstream R Shiny app reads from there |
| **Anu Figure** | Figure export writes per-figure CSVs with transforms to `data/final-data/figures/` |
| **Anu Review** | D8 Replicator Scripts dimension scores script existence and correctness |
| **Anu Pipeline** | Replicator is Stage 4 of the pipeline |

---

## Anu Framework Context

- **Pipeline Stage**: 4 (REPLICATION)
- **Upstream**: Stage 2 Ingestion, Stage 3 Extension
- **Downstream**: Stage 5 Output (Chopped, Extenbook), Stage 5b Viz Export
- **Adequacy Relevance**: L4 (Construction Logic) — replicator implements the logic L4 validated
- **Key Handoff**: Produces all data outputs consumed by Chopped (validation), Extenbook (generation), Shiny (visualization)

## Version History

- **v1.0** (January 2026) - Initial release
- **v2.0** (March 2026) - Two-phase architecture, visualization export phase, data_dict contract
- **v2.1** (March 2026) - Added cross-chapter dependencies, platform encoding safety, registry sync protocol; rewrote L/P script templates to match actual implementation patterns
- **v2.2** (March 2026) - Added SUBSOURCE_METADATA.json to Visualization Export phase; added registry completeness requirement for viz export
- **v2.3** (March 2026) - Added extension column requirement (S###-EXT + S###-F) in data_dict and chopped CSVs; added generate_shiny_subsources.py to Visualization Export; documented automatic copy to ShinyApp catalogs
- **v2.4** (March 2026) - Generalized: replaced project-specific catalog paths with configurable directory references
- **v2.5** (March 2026) - Added Concurrent Series (CS) processing pattern: CS_COLUMN_MAP convention, level-data extraction from Tier 2 tables, integration with chopped_writer
- **v2.6** (March 2026) - Minor refinements
- **v3.0** (April 2026) - Four-phase architecture (L→P→V→M): added V## validation scripts (V01-V08), M## manual adjustment scripts with ADJUSTMENT_MANIFEST.json, E## exploration scripts, SHA-256 hash audit trail in PROCESS_LOG, new CLI flags (--validate-only, --skip-validation, --full, --manual-only, --skip-manual, --provenance), provenance_index.json, DECISION_LOG.md, ASSUMPTIONS.md

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | L##, P##, V##, M## scripts, E## exploration scripts, all data outputs (Chopped CSVs, Extenbooks, final CSVs, chapter CSVs, figure CSVs, series catalog, SUBSOURCE_METADATA.json), VALIDATION_REPORT.json, ADJUSTMENT_MANIFEST.json, provenance_index.json, DECISION_LOG.md, ASSUMPTIONS.md |
| **Expects** | `series_registry.json`, `S###_research.json`, Chopped input CSVs in `data/user-inputs/chopped/` |
| **Must Update on Completion** | `LOAD_LOG.json` and `PROCESS_LOG.json` are auto-generated. Regenerate Ledger via `python replicate.py --ledger` or `/anu-ledger generate` |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Self-Contained Replication Package*
