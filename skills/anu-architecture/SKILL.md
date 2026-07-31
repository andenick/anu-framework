---
name: anu-architecture
version: "2.1"
description: "Anu Architecture v2.1: Standardized framework for bespoke econometric data construction and analysis projects. Scaffolds folder structure, creates orchestrators, manages 8-phase script pipelines (S/L/P/V/M/A/O/E). v2.1 documents canonical cache schemas for BEA NIPA, BLS, and FRED responses (DataValue comma-stripping, UNIT_MULT exponent application, observation-list flattening) so projects sharing data sources can reuse cache readers via anu-replicator's `lib/data/` layout."
when-to-use: "User needs to set up a new data analysis/econometric project, run a research pipeline, scaffold an Anu Architecture workspace, check Anu Architecture project status, or parse a cached BEA/BLS/FRED API response with the canonical schema."
search-hints: "anu-architecture architecture anudata data econometrics panel analysis pipeline scaffold init research cache bea bls fred schema reader"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[init|status|run|checklist] [project_path]"
requires: anu-ingestion, anu-replicator
part-of: Anu Framework v12.2
---

# Anu Architecture v2.1

*Lineage: predecessor architecture v1.1 -> AnuData Architecture v2.0 (May 2026) -> Anu Architecture v2.1 (May 2026 — renamed for framework-name consistency).*

## Stage Position

**Infrastructure** — not a numbered pipeline stage. Anu Architecture is the format standard for a project's own research workspace (`Technical/AnuArchitecture/`). The orchestrator invokes it at project setup; the 8-phase pipeline it defines then runs on its own master orchestrator, independently of the framework's numbered stages.

## Description

Anu Architecture is a standardized, self-contained architecture for bespoke econometric data construction and analysis projects. It lives inside a project's `Technical/AnuArchitecture/` folder and provides a unified, chronological, self-documenting framework where every script, dataset, output, and decision is tracked in a single contained structure.

### Core Principles

1. **Containment**: Everything in one folder. Zip it and hand it to a reviewer.
2. **Chronological Legibility**: Numbered scripts run in a defined order. Anyone can reconstruct the pipeline.
3. **Separation of Concerns**: Raw data is never modified. Manual adjustments are clearly delineated from programmatic processing.
4. **Reproducibility Without Agents**: The entire pipeline runs via a single master orchestrator (e.g., `Rscript run.R` or `python run.py`) without AI agent intervention.
5. **Audit Trail**: Every transformation, parameter choice, and model run is logged in structured JSON.
6. **Exploration Preservation**: Exploratory work feeds `data/scratch/` (ephemeral); conclusions go to DECISION_LOG.md. E## scripts are never deleted — they are the permanent record of the research process.
7. **No Synthetic Data**: Every value in every CSV must come from a real, documented source. If data is unavailable, the series is `data_unavailable` — never filled with trends, noise, or estimates. Missing data is a gap to be resolved, not a hole to be papered over. `np.random` in a data construction script is always wrong.
8. **Public Reproducibility**: Every L## script must either call a public API or include a comment with the public download URL. No private data paths (private data repositories, internal databases) in the pipeline. If data comes from a non-API source, the L## header must include a `PUBLIC SOURCE:` line with the URL where anyone can obtain this data. Learned from the reference implementation: had to retroactively strip all private data references from 40+ scripts.
9. **Source Specification Before Code**: Before writing any L## or P## script, produce a Source Specification listing: variable name, source agency, table/series ID, units, frequency, URL, and date range. This is the contract the code must fulfill. Learned from the reference implementation: building extensions first then checking the Knowledge Base produced a 21% error rate.
10. **No Proxies Without Justification**: If the exact source is unavailable, document why and what proxy is used. Proxies must be flagged in project_registry.json with `"proxy": true` and a justification. CPI is not PPI. Earnings is not compensation. Yield is not total return. Every concept substitution degrades faithfulness.

## When to Use

- **Original econometric research**: Panel econometrics, time-series analysis, empirical testing
- **Long-running research projects**: Multi-test empirical studies with robustness requirements
- **Complex data construction**: Multi-source panel building, cross-dataset linking
- **Any project requiring**: Reproducibility, audit trail, validation, manual adjustment tracking

**NOT for**: Replicating published data series (use Anu Replicator for that — see Relationship section).

## Relationship to Anu Framework

Anu Architecture is a **first-class skill within the Anu Framework**, complementing Anu Replicator:

| | Anu Replicator | Anu Architecture |
|---|---|---|
| **Purpose** | Replicate published data series (e.g., Shaikh 2016 appendices) | Original econometric research and empirical analysis |
| **Phases** | L## + P## + V## + M## (4 phases) | S## + L## + P## + V## + M## + A## + O## + E## (8 phases) |
| **Central config** | `series_registry.json` | `project_registry.json` |
| **Language** | Python only | Any (R, Python, Stata, Mixed — user-configured) |
| **Validation** | Reference value checks inside P## | Dedicated V## phase with standardized checklist |
| **Analysis** | Not applicable (replication only) | Full econometric estimation, robustness, diagnostics |
| **Home** | `Technical/ANU_REPLICATOR/` | `Technical/AnuArchitecture/` |

A project can have **both** `Technical/ANU_REPLICATOR/` and `Technical/AnuArchitecture/`. They share the L##/P## naming convention and auto-discovery pattern but serve different purposes.

Anu Architecture **borrows** from Anu Replicator:
- L##/P## naming and glob-based auto-discovery (XX00 orchestrators)
- `paths.R`/`paths.py` centralized path management
- LOAD_LOG.json / PROCESS_LOG.json audit trails
- Result dict pattern (status, outputs, validation)
- Config-driven pipeline (registry JSON as single source of truth)

Anu Architecture **adds**:
- Validation as a first-class phase (V##)
- Manual adjustment tracking with audit manifest (M##)
- Analysis/robustness/diagnostics (A## + V## post-analysis)
- Exploration preservation (E##)
- Intermediate data checkpoints (int-data/)
- Standardized pre/post-analysis checklist
- Language-agnostic design

### Legacy folder name

Projects scaffolded before the May 2026 rename used `Technical/AnuData/` rather than `Technical/AnuArchitecture/`. Both layouts are functionally identical; the framework does not force a migration. Tooling that walks a project tree should recognize either folder name.

---

## The Eight Prefixes

| Prefix | Name | Purpose | Reads From | Writes To |
|--------|------|---------|------------|-----------|
| **S##** | Setup | Package installation, workspace config, environment variables, API keys, path validation | (system) | `logs/setup/` |
| **L##** | Load | Load raw data from files AND APIs into standardized format. Handles caching, vintage tracking. Every L## must document: Public Source URL, API endpoint params, units, vintage date. | `data/user-inputs/` + external APIs + project `Inputs/` | `data/raw-data/` |
| **P##** | Process | Clean, transform, merge, reshape, construct analysis-ready datasets | `data/raw-data/` | `data/int-data/` + `data/final-data/` |
| **V##** | Validate | Data integrity, completeness, distributions, cross-checks. Also includes **model diagnostics** after analysis (Sargan, AR tests, Hausman, specification tests). | `data/final-data/` or `outputs/analysis/` | `logs/validation/` + `outputs/validation/` |
| **M##** | Manual Adjust | Documented, justified manual corrections with full audit trail. High standard of proof. Never modify `final-data/` — always write to `adjusted-final-data/`. | `data/final-data/` | `data/adjusted-final-data/` |
| **A##** | Analyze | Econometric estimation, statistical tests, model fitting. Includes **robustness** (specification curves, sensitivity, alternative estimators) and **comparison** (cross-model/cross-theory adjudication). | `data/final-data/` or `data/adjusted-final-data/` | `outputs/analysis/` |
| **O##** | Output | Publication-quality tables, figures, reports, LaTeX, PDF generation. Includes comparison outputs. **O## runs LAST after everything else.** | `outputs/analysis/` | `outputs/deliverables/` |
| **E##** | Explore | Standalone exploratory scripts. New data sources, methods, visualizations, prototypes. Outputs are **ephemeral** (go to `data/scratch/`). E## scripts are never deleted. | Any | `data/scratch/` |

## Running Order

```
S## -> L## -> P## (+ E## runs concurrently) -> V## -> M## -> A## -> V## (diagnostics) -> O## (LAST)
```

- **S##** runs first to ensure environment is ready
- **L##** loads all raw data
- **P##** processes data; **E##** exploration can run concurrently with P## (after L## completes)
- **V##** validates the processed data (first pass: data quality)
- **M##** applies any justified manual adjustments
- **A##** runs all analysis (estimation, robustness, comparison)
- **V##** runs again for model diagnostics (second pass: post-estimation checks)
- **O##** runs **LAST** — generates all final outputs after everything else is complete

## Script Conventions

- **XX00**: Orchestrator script — auto-discovers and runs XX01-XX99 via glob pattern `XX[0-9][0-9]_*.ext`
- **XX01-XX99**: Individual scripts, numbered to reflect execution order
- **Numbers mean execution order, nothing else.** No reserved ranges, no semantic sub-bands. If you need to insert between XX03 and XX04, renumber the phase and follow the Renumbering Protocol below.
- Every script must include a standard header block declaring Purpose, Inputs, Outputs, and Dependencies (see Script Header Standard below).
- Naming pattern: `XX##_descriptive_name.ext` (e.g., `L01_load_bls_employment.py`)
- File extension determined by project language config (`.R`, `.py`, `.do`, `.jl`)
- **Letter suffixes (A01b, P03b) are NOT allowed** — they are invisible to the orchestrator glob and break pipeline discovery. Renumber instead.
- **Only the 8 defined phase prefixes are valid**: S, L, P, V, M, A, O, E. Do not invent new prefixes (e.g., no "N##" for robustness — use A## instead).

## Script Header Standard

Every script (XX01+, not XX00 orchestrators) must begin with a header block:

```python
"""
P07: Construct Marxian Variables
================================
Phase:   Processing
Purpose: Compute lending rate, economy profit rate, and interest-profit
         spread for Marxian credit theory tests.

Inputs:
  - data/int-data/unified_panel.parquet  (from P04)
  - data/raw-data/fred_macro.parquet     (from L07)

Outputs:
  - data/int-data/unified_panel.parquet  (adds 3 columns)

Dependencies:
  - P04 must have run (unified_panel must exist)
  - L07 must have run (fred_macro must exist)

Studies: STUDY_04_COINTEGRATION
"""
```

Required fields: Script ID & title, Phase, Purpose, Inputs (with source script in parentheses), Outputs, Dependencies. Studies is optional (A## phase only).

The Dependencies field is the safety mechanism for renumbering — when you renumber P07 to P09, grep for "P07" in all script headers and update.

## Renumbering Protocol

When inserting, removing, or reordering scripts within a phase, complete ALL steps:

1. **Rename files** to new numbers. Example: inserting new P04 between P03 and P04 means rename P04->P05, P05->P06, ..., then create new P04.
2. **Update script headers** — In every renamed script, update the Script ID line. In ALL scripts in the phase, update Dependencies references to reflect new numbers.
3. **Update project_registry.json** — Search for old script IDs in `loading_scripts`, `processing_scripts`, `analysis_scripts` arrays. Update all references.
4. **Update CHECKLIST.md** — Update every `- [x] XX##: description` line that references a changed number.
5. **Update DECISION_LOG.md** — Search for old script IDs in DEC entries. Update references. Add a new DEC entry documenting the renumbering and why.
6. **Update VERSION_LOG.md** — Do NOT rewrite historical entries (they document what existed at that version). Add a note to the current version entry documenting the renumbering.
7. **Preserve logs** — LOAD_LOG.json, PROCESSING_LOG.json: do NOT rename references in old log entries. Old logs reflect what ran at the time. New pipeline runs will produce entries with new script IDs.
8. **Verify orchestrator** — Run `python run.py --dry-run` to confirm all scripts are discovered in the correct order.

---

## `/anu-architecture init` — Interactive Setup

When invoked, the skill interactively prompts the user for project configuration. **Language is NOT hardcoded** — the skill asks the user to specify their preferred language(s) for each new project.

### Interactive Prompts

```
/anu-architecture init

> Project name?
> Language? [R / Python / Stata / Mixed]
> Location? [Technical/AnuArchitecture] (default)
> How many studies/tests?
> Study names? (comma-separated)
> Data sources? (comma-separated)
> Include Shiny visualization? [y/N]
> Include automated tests? [y/N]
```

Use `AskUserQuestion` for each prompt to collect user input.

### What `/anu-architecture init` Creates

1. **Full folder structure** (see Folder Structure below)
2. **Master orchestrator** (`run.R`, `run.py`, or `run.do` per language choice)
3. **`project_registry.json`** with study stubs from user input
4. **All XX00 orchestrator scripts** (S00, L00, P00, V00, M00, A00, O00)
5. **`utils/paths.R`** (or `.py`) with all path constants
6. **`README.md`** with project overview and running instructions
7. **`DECISION_LOG.md`** (empty template with format guide)
8. **`CHECKLIST.md`** (auto-populated from study configuration)
9. **`docs/` templates**: METHODOLOGY.md, DATA_SOURCES.md, VARIABLE_CODEBOOK.md, ASSUMPTIONS.md
10. **L## stubs** for each data source specified
11. **A## stubs** for each study specified
12. **`.gitignore`** (ignore data/raw-data/, data/int-data/, data/scratch/, logs/)

---

## Folder Structure

```
Technical/AnuArchitecture/
|
+-- README.md                          # Project overview, running instructions
+-- run.R                              # Master orchestrator (language-specific)
+-- project_registry.json              # Single source of truth for study config
+-- DECISION_LOG.md                    # Structured record of all design decisions
+-- CHECKLIST.md                       # Auto-generated validation/analysis checklist
|
+-- code/                              # ALL scripts
|   +-- setup/          S##            # Package install, env config
|   +-- loading/        L##            # Data loading (files + APIs)
|   +-- processing/     P##            # Data transformation and construction
|   +-- validation/     V##            # Data validation + model diagnostics
|   +-- manual/         M##            # Manual adjustments + ADJUSTMENT_LOG.md
|   +-- analysis/       A##            # Estimation + robustness + comparison
|   +-- outputs/        O##            # Publication-quality outputs (RUNS LAST)
|   +-- exploration/    E##            # Standalone exploration (ephemeral outputs)
|
+-- data/                              # ALL data
|   +-- user-inputs/                   # Specifications, parameters, configs (YAML)
|   +-- raw-data/                      # L## output (never manually edited)
|   |   +-- LOAD_LOG.json
|   +-- int-data/                      # P## intermediate checkpoints
|   |   +-- PROCESSING_LOG.json
|   +-- final-data/                    # Analysis-ready datasets (P## output)
|   |   +-- DATA_DICTIONARY.md
|   +-- adjusted-final-data/           # M## output (clearly separate from final-data)
|   |   +-- ADJUSTMENT_MANIFEST.json
|   +-- scratch/                       # E## ephemeral outputs (cleared periodically)
|
+-- outputs/                           # ALL outputs (internal to Anu Architecture)
|   +-- validation/                    # V## outputs
|   +-- analysis/                      # A## outputs (organized by study/test)
|   +-- exploration/                   # E## summary outputs (optional, non-ephemeral)
|   +-- deliverables/                  # O## outputs (publication-ready)
|       +-- tables/
|       +-- figures/
|       +-- reports/
|       +-- OUTPUT_CATALOG.json
|
+-- utils/                             # Shared utility code (self-contained)
|   +-- paths.R                        # All path constants
|   +-- config_loader.R                # Load registries and YAML configs
|   +-- transforms/                    # Reusable transform functions
|   +-- estimators/                    # Econometric estimation wrappers
|   +-- diagnostics/                   # Post-estimation diagnostic functions
|   +-- io/                            # Data I/O utilities
|   +-- logging/                       # Audit trail utilities
|
+-- logs/                              # Execution and audit logs
|   +-- setup/
|   +-- validation/
|   +-- runs/                          # Timestamped run logs (JSON)
|
+-- shiny/                             # Interactive visualization (optional)
|
+-- tests/                             # Automated tests (optional)
|
+-- docs/                              # Study documentation
    +-- METHODOLOGY.md
    +-- DATA_SOURCES.md
    +-- VARIABLE_CODEBOOK.md
    +-- ASSUMPTIONS.md
```

---

## project_registry.json

Single source of truth for study configuration:

```json
{
  "version": "2.1.0",
  "project": "Project Name",
  "architecture": "Anu Architecture v2.1",
  "language": "R",
  "author": "Author Name",

  "studies": {
    "STUDY_01": {
      "name": "Study Name",
      "method": "Estimation method",
      "dependent_variable": "variable_name",
      "key_prediction": "description",
      "analysis_scripts": ["A01"],
      "status": "PENDING"
    }
  },

  "datasets": {
    "main_panel": {
      "description": "Dataset description",
      "loading_scripts": ["L01", "L02"],
      "processing_scripts": ["P01", "P02"],
      "format": "parquet"
    }
  }
}
```

---

## Data Flow

```
Project Inputs/ (read-only, standard project layout)
    | L## (loads, never modifies source)
data/raw-data/
    | P## (transforms)
data/int-data/ (intermediate checkpoints)
    | P## (final construction)
data/final-data/ (analysis-ready)
    | V## (validates)
    | M## (manual adjustments if needed)
data/adjusted-final-data/ (if adjustments applied)
    | A## (estimation + robustness)
outputs/analysis/ (results)
    | V## (model diagnostics)
    | O## (LAST -- formats for publication)
outputs/deliverables/ (tables, figures, reports)
    | manual promote
Project Outputs/YYYY.MM.DD Description/ (dated-output convention)
```

**Primary data format**: Apache Parquet (fast, compact, preserves types). CSV only for `data/user-inputs/` (human-editable) and final deliverables when CSV is the target format.

---

## Manual Adjustment Standards

Every M## adjustment requires **all five** of:

1. **Specific reason**: Why this adjustment is necessary (not "data looks wrong")
2. **Evidence**: Source documentation proving the adjustment is correct
3. **Original values**: Exact values before adjustment
4. **Adjusted values**: Exact values after adjustment
5. **Reversibility**: Can this be undone? How?

Adjustments are written to `data/adjusted-final-data/` — **never** to `final-data/`. The `ADJUSTMENT_MANIFEST.json` records every adjustment with all five fields. A## scripts must explicitly choose whether to read from `final-data/` or `adjusted-final-data/`.

---

## DECISION_LOG.md Format

Structured entries recording every design decision:

```markdown
## <DECISION-ID>: Decision Title (YYYY-MM-DD)

**Decision**: What was decided.

**Rationale**: Why this choice was made.

**Alternatives Considered**:
- Alternative 1 (rejected: reason)
- Alternative 2 (rejected: reason)

**Impact**: What this decision affects going forward.
```

---

## CHECKLIST.md

Auto-generated by `/anu-architecture init`, populated from the study configuration. Covers:

- **Pre-Analysis**: All S##, L##, P##, V## items checked
- **Analysis**: All A## studies estimated, diagnostics pass
- **Outputs**: All O## deliverables generated and cataloged

Agents and humans check items off as they complete them.

---

## Output Promotion

When deliverables are ready for the project's root `Outputs/` folder:
1. O## scripts generate publication-ready files to `outputs/deliverables/`
2. Manual copy to `Outputs/YYYY.MM.DD Description/` (dated-output convention)
3. Decision recorded in DECISION_LOG.md

---

## Master Orchestrator

The master orchestrator (`run.R`, `run.py`, or `run.do`) is the single entry point:

```
Rscript run.R                    # Full pipeline: S -> L -> P -> V -> M -> A -> V -> O
Rscript run.R --setup-only       # Just S##
Rscript run.R --load-only        # Just L##
Rscript run.R --from P           # Resume from processing phase
Rscript run.R --test A01         # Run specific script
Rscript run.R --dry-run          # Show what would execute
Rscript run.R --report           # Status report from last run
```

Each XX00 orchestrator auto-discovers scripts by glob pattern (e.g., `list.files("code/loading", pattern = "^L[0-9]{2}_.*\\.R$")`) and sources them in numeric order.

---

## Integration with Standard Project Layout

- Anu Architecture lives in `Technical/AnuArchitecture/` (inside the framework-standard project structure)
- Source data read from `Inputs/` (read-only, never modified)
- Published outputs promoted to `Outputs/` (dated-output convention)
- **Self-contained**: The entire Anu Architecture folder can be zipped and given to a reviewer

---

## `/anu-architecture status`

Check current state of an Anu Architecture project:
- Read `project_registry.json` for study definitions
- Read `CHECKLIST.md` for completion tracking
- Scan `code/` directories for script counts per phase
- Scan `data/` directories for data presence
- Scan `outputs/` for deliverable status
- Report: studies defined, scripts written, data loaded, analyses complete, outputs generated

---

## `/anu-architecture checklist`

Display the current CHECKLIST.md with completion status. Useful for agents picking up where a previous session left off.

---

## Public Reproducibility Requirements

### Data Acquisition Priority (MANDATORY for L## scripts)

Every L## loading script must acquire data using this priority order:

1. **PUBLIC API** — Always try first (FRED, BEA, BLS, World Bank, IMF). Requires user-provided API key from `config/api_keys.env`.
2. **DOWNLOADED FILE** — If API unavailable or key missing. Script must document the exact public URL for manual download.
3. **PDF EXTRACTION** — Last resort, for methodology text or historical data only available in the book PDF.

### L## Script Source Documentation (MANDATORY)

Every L## script header must include:
```
Source: [Institution Name]
Series/Table: [Specific identifier]
Public URL: [Direct link to data page]
Description: [What this data is]
Original Data: https://www.anwarshaikhecon.org/ (Shaikh's published appendix)
```

### API Key Management

- Store keys in `config/api_keys.env` (ALWAYS gitignored)
- Ship `config/api_keys.env.example` with placeholder values and FREE registration URLs
- L## scripts MUST gracefully degrade when keys are missing (warn, don't crash)
- README lists all required API keys with registration links

### No Private Data Sources

Data projects intended for public repositories must NEVER reference:
- Internal databases or private data repositories
- Proprietary APIs without public alternatives
- Files that exist only on the author's machine

Every value in the final output must be traceable to a publicly accessible source.

### .gitignore Requirements

Every public data project MUST exclude:
- `config/api_keys.env` (real API keys)
- `data/raw-data/api/` (cached responses — regenerated by pipeline)
- `__pycache__/`, `*.pyc`

The exclusion list above is the standard in full. (Earlier revisions pointed at a `docs/GIT_PROTOCOL.md`; that document was never written, and the pointer has been removed rather than left dangling.)

---

## Error Handling

- **Project not framework-standard** (missing Inputs/Technical/Outputs): Warn user, suggest running `/project-initialization` first
- **Data sources not found**: L## scripts should fail loudly with diagnostic errors (principle: FAIL LOUDLY from Anu Standard)
- **Missing packages**: S## scripts check for required packages and report what's missing
- **Anu Architecture already exists**: If `Technical/AnuArchitecture/` (or legacy `Technical/AnuData/`) already exists, report current state instead of overwriting

---

## Logging

Every script execution is logged to `logs/runs/` as structured JSON:

```json
{
  "run_id": "run_YYYY-MM-DDTHH-MM-SS",
  "script": "A01_test1_mean_reversion.R",
  "started": "ISO timestamp",
  "completed": "ISO timestamp",
  "status": "ok",
  "input_files": [{"path": "...", "hash": "sha256:..."}],
  "output_files": [{"path": "...", "hash": "sha256:..."}],
  "parameters": {},
  "key_results": {}
}
```

---

## Versioning

- **No CHANGELOG file** — git tags mark architecture milestones (e.g., `anu-architecture-v2.1`)
- DECISION_LOG.md tracks project-level decisions
- Git log is the changelog

---

## Evolutionary Versioning (Snake-Shedding Model)

For long-running research projects, Anu Architecture supports **evolutionary versioning** — discrete versions where each is a complete, self-contained state of the project.

### Version Numbering

```
v0.1  -- Planning (plan document, study definitions)
v0.2  -- Initialized (Anu Architecture scaffolded, environment validated)
v0.3  -- Data loaded (all L## complete, LOAD_LOG verified)
v0.4  -- Panel constructed (all P## complete, validation passed)
v0.5  -- Exploration complete (E## analysis done, specifications refined)
v1.0  -- FIRST COMPLETE PIPELINE (all studies estimated, scorecard produced)
v1.1+ -- Iterations (new data, revised specifications, additional KB entries)
v2.0  -- MAJOR REVISION (structural changes, new theories, new data sources)
```

### Archive Structure

```
Technical/AnuArchitecture/
+-- _archive/
|   +-- v0.1_YYYY-MM-DD/           # Planning snapshot
|   +-- v0.2_YYYY-MM-DD/           # Post-init snapshot
|   +-- ...
+-- _version_history/
    +-- VERSION_LOG.md              # What changed per version and why
    +-- MIGRATION_NOTES.md          # Technical notes for rebuilds
```

### When to Version Up

- **Only when the user explicitly requests it**
- After natural milestones (loading, validation, each study, synthesis)
- When incorporating significant new knowledge that changes specifications
- When a fundamental design decision changes

### Archive Process

1. Copy current state of `code/`, `data/`, `outputs/`, `logs/` to `_archive/vX.Y_DATE/`
2. Record what changed and why in `_version_history/VERSION_LOG.md`
3. Rebuild incorporating new knowledge from the previous version
4. **Never delete** old versions — they are the permanent record of evolution

---

## `/anu-architecture version [up|log|archive]`

Additional commands for evolutionary projects:

- **`/anu-architecture version up`**: Archive current state, increment version, update VERSION_LOG.md
- **`/anu-architecture version log`**: Display VERSION_LOG.md showing evolution history
- **`/anu-architecture version archive`**: List all archived versions with dates and descriptions

---

## Assumptions Register

For rigorous research projects, Anu Architecture projects should maintain an `ASSUMPTIONS.md` file tracking every assumption:

```markdown
## Data Assumptions
- ASM-D01: [Description] -- Source: [KB doc / paper / data inspection]

## Methodological Assumptions
- ASM-M01: [Description] -- Source: [methodology paper]

## Theoretical Assumptions
- ASM-T01: [Description] -- Source: [theory paper]
```

Every assumption should be revisited when versioning up.

---

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Interactive setup answers (project name, language, location, studies, data sources, Shiny y/N, tests y/N) | The user, via `AskUserQuestion` during `/anu-architecture init` | Yes, for `init` |
| `project_registry.json` | The scaffolded project (`Technical/AnuArchitecture/`) | Yes, for every command after `init` |
| Project `Inputs/` | The framework-standard project layout — read-only, never modified | Yes |
| Public APIs (FRED, BEA, BLS, World Bank, IMF) | External; keys supplied by the user in `config/api_keys.env` | Conditional (L## scripts) |
| Downloaded source files / book PDF | Acquisition priorities 2 and 3 when no public API exists | Conditional |
| `data/user-inputs/` specifications, parameters, configs (YAML) | Human-authored | Conditional |
| `CHECKLIST.md`, `DECISION_LOG.md`, `_version_history/VERSION_LOG.md` | The scaffolded project | Read by `status`, `checklist`, `version log` |

---

## Outputs

`/anu-architecture init` writes the scaffold; the generated pipeline writes everything else. All paths are relative to `Technical/AnuArchitecture/`.

| Output | Written by | Description |
|--------|-----------|-------------|
| The full folder structure | `init` | `code/`, `data/`, `outputs/`, `utils/`, `logs/`, `docs/`, optional `shiny/` and `tests/` |
| `run.R` / `run.py` / `run.do` | `init` | Master orchestrator for the chosen language |
| `project_registry.json` | `init` | Single source of truth for study configuration, with study stubs from the user's answers |
| XX00 orchestrator scripts (S00, L00, P00, V00, M00, A00, O00) | `init` | Glob-based auto-discovery entry points per phase |
| `utils/paths.R` (or `.py`) | `init` | Centralized path constants |
| `README.md`, `DECISION_LOG.md`, `CHECKLIST.md`, `.gitignore` | `init` | Project overview, decision record, auto-populated checklist, exclusions |
| `docs/METHODOLOGY.md`, `DATA_SOURCES.md`, `VARIABLE_CODEBOOK.md`, `ASSUMPTIONS.md` | `init` | Documentation templates |
| L## and A## stubs | `init` | One per declared data source and per declared study |
| `data/raw-data/` + `LOAD_LOG.json` | L## | Loaded raw data, never manually edited |
| `data/int-data/` + `PROCESSING_LOG.json`, `data/final-data/` + `DATA_DICTIONARY.md` | P## | Intermediate checkpoints and analysis-ready datasets |
| `logs/validation/`, `outputs/validation/` | V## | Data-quality pass and post-estimation diagnostics |
| `data/adjusted-final-data/` + `ADJUSTMENT_MANIFEST.json` | M## | Documented manual adjustments, kept separate from `final-data/` |
| `outputs/analysis/` | A## | Estimation, robustness, comparison results |
| `outputs/deliverables/` (`tables/`, `figures/`, `reports/`) + `OUTPUT_CATALOG.json` | O## | Publication-ready outputs, generated last |
| `data/scratch/` | E## | Ephemeral exploration output |
| `logs/runs/run_*.json` | Every script | Structured execution record with input/output file hashes |
| `_archive/vX.Y_DATE/` + `_version_history/VERSION_LOG.md`, `MIGRATION_NOTES.md` | `version up` / `version archive` | Snake-shedding version snapshots |

Deliverables reach the project's root `Outputs/YYYY.MM.DD Description/` only by the manual promotion step described under Output Promotion.

---

## Commands

**This skill ships no executable.** It is agent-invoked: the commands below are sub-commands the agent performs by reading this SKILL.md and writing files into the project. The only runnable artifact is the master orchestrator (`run.R` / `run.py` / `run.do`) that `init` generates *inside the project* — it is not part of this skill directory.

| Command | Description |
|---------|-------------|
| `/anu-architecture init` | Interactive scaffold — prompts for project name, language, location, studies, data sources, Shiny and tests; then creates the full structure listed under Outputs |
| `/anu-architecture status` | Read `project_registry.json` and `CHECKLIST.md`, scan `code/`, `data/`, `outputs/`, and report studies defined, scripts written, data loaded, analyses complete, outputs generated |
| `/anu-architecture checklist` | Display `CHECKLIST.md` with completion status, for an agent resuming someone else's session |
| `/anu-architecture run` | Listed in this skill's `argument-hint`. Execution is delegated to the project's generated master orchestrator; the invocation surface it exposes (`--setup-only`, `--load-only`, `--from P`, `--test A01`, `--dry-run`, `--report`) is specified under Master Orchestrator |
| `/anu-architecture version up` | Archive the current state, increment the version, update `VERSION_LOG.md` |
| `/anu-architecture version log` | Display `VERSION_LOG.md` |
| `/anu-architecture version archive` | List archived versions with dates and descriptions |

---

## Acceptance Gates

These are the conditions this standard treats as must-pass. They are enforced by review, not by a shipped checker.

| Gate | Condition |
|------|-----------|
| Scaffold complete | Full folder structure, master orchestrator, `project_registry.json`, all seven XX00 orchestrators, `paths` module, README, DECISION_LOG, CHECKLIST, docs templates, and `.gitignore` all present |
| Naming valid | Every script matches `XX##_descriptive_name.ext` using only the eight prefixes S/L/P/V/M/A/O/E. No letter suffixes — they are invisible to the orchestrator glob |
| Headers complete | Every XX01+ script carries the header block with Script ID & title, Phase, Purpose, Inputs (with source script), Outputs, Dependencies |
| Source specification before code | A Source Specification (variable, agency, table/series ID, units, frequency, URL, date range) exists before any L## or P## script is written |
| Public reproducibility | Every L## either calls a public API or carries a `PUBLIC SOURCE:` URL in its header; no private data paths anywhere in the pipeline |
| Secrets excluded | `config/api_keys.env` gitignored, `config/api_keys.env.example` shipped, L## degrades gracefully when a key is missing |
| No synthetic data | No value is trend-filled, noise-filled, or estimated to close a gap; unavailable series are `data_unavailable`; `np.random` is absent from construction scripts |
| Proxies declared | Any concept substitution is flagged `"proxy": true` in `project_registry.json` with a justification |
| Manual adjustments justified | Every M## adjustment records all five of reason, evidence, original values, adjusted values, reversibility in `ADJUSTMENT_MANIFEST.json`, and writes to `adjusted-final-data/` — never `final-data/` |
| Renumbering complete | All eight steps of the Renumbering Protocol done, ending with `--dry-run` confirming discovery order |
| Running order respected | S → L → P (E concurrent) → V → M → A → V (diagnostics) → O, with O## last |
| Containment | The `Technical/AnuArchitecture/` folder can be zipped and handed to a reviewer as-is |

---

## Anti-Patterns

| Anti-pattern | Why it's wrong | Do this instead |
|---|---|---|
| Letter-suffixed scripts (`A01b`, `P03b`) | Invisible to the orchestrator glob; the pipeline silently skips them | Renumber the phase and follow the Renumbering Protocol |
| Inventing a new phase prefix (e.g. `N##` for robustness) | Only the eight defined prefixes are discovered and ordered | Robustness is A## |
| Reading semantics into script numbers | Numbers mean execution order, nothing else — no reserved ranges | Encode meaning in the name and the header, not the number |
| Renaming files without updating headers, registry, checklist, and decision log | Dependencies references go stale and the pipeline breaks quietly | Complete all eight Renumbering Protocol steps, then `--dry-run` |
| M## writing into `data/final-data/` | Destroys the boundary between programmatic construction and manual correction | Write to `data/adjusted-final-data/` and record the adjustment |
| Deleting E## exploration scripts | They are the permanent record of the research process | Never delete them; their *outputs* are the ephemeral part |
| Rewriting historical `VERSION_LOG.md` entries or deleting archived versions | They document what existed at that version | Append to the current entry; keep every archive |
| Private data paths or proprietary-only sources in L## | The pipeline stops being reproducible by anyone else | Public API first, then a documented public download URL, then PDF extraction |
| Committing real API keys | Irreversible disclosure | Keep `config/api_keys.env` gitignored; ship only the `.example` |
| Filling a data gap with a trend, noise, or an estimate | Fabricated values propagate silently through every downstream phase | Mark the series `data_unavailable` and resolve the gap |
| Substituting a near-enough proxy silently | CPI is not PPI; earnings are not compensation; yield is not total return | Flag `"proxy": true` with a justification, or find the real source |
| Overwriting an existing `Technical/AnuArchitecture/` (or legacy `AnuData/`) on `init` | Destroys prior work | Report the current state instead |
| Running O## before analysis is final | Deliverables get built from stale results | O## runs last, always |

---

## Skill Evolution Log

This section tracks learnings from real-world usage of Anu Architecture to improve the architecture.

### Learning L001 (2026-04-05, Research Planning)

**Context**: First real-world application to an applied research project.

**Findings**:
1. The original skill lacked evolutionary versioning — critical for long-running research projects. Added snake-shedding model.
2. The original skill lacked an assumptions register — critical for long-running research projects where every claim must be defensible. Added ASSUMPTIONS.md.
3. The 8-phase pipeline maps well to the research workflow, but V## needs to be explicitly split into "data quality" (pre-analysis) and "model diagnostics" (post-analysis) passes.
4. E## exploration scripts are invaluable for building intuition before formal estimation. The "never delete" rule is essential.
5. Source attribution must be a first-class concern — every decision, variable construction, and method choice needs a citation trail.
6. The project_registry.json "studies" structure works well for organizing multiple tests within a single project.

**Actions Taken**: Updated skill with evolutionary versioning, assumptions register, version commands.

### Learning L002 (2026-05-09, Anu Framework Integration)

**Context**: Renamed from its predecessor to AnuData Architecture and integrated as a first-class Anu Framework skill.

**Rationale**: The predecessor architecture was architecturally parallel to the Anu Framework but treated as a separate system. Integration makes the full data construction lifecycle — from replication (anu-replicator) through original research — a unified framework. This also positions the architecture for open-source release as a standalone adoptable framework.

### Learning L003 (2026-05-15, Framework-Name Consistency)

**Context**: Renamed from AnuData Architecture to Anu Architecture as part of the v11.0 framework sweep.

**Rationale**: The "AnuData" name created a parallel brand inside the Anu Framework — readers had to learn two names ("Anu" and "AnuData") for what is in fact one unified system. The rename makes the skill's identity consistent with the rest of the framework (anu-*) and removes the impression that "Anu Architecture" is a sibling framework rather than a member skill. The skill folder `anu-data/` was renamed to `anu-architecture/`; the project-level folder default became `Technical/AnuArchitecture/`; existing projects with `Technical/AnuData/` are unaffected and remain valid.

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Anu Architecture v2.1 — Part of the Anu Framework v12.2*
*Lineage: predecessor architecture v1.0 (2026-04-05) -> v1.1 (2026-04-06) -> AnuData v2.0 (2026-05-09) -> Anu Architecture v2.1 (2026-05-15)*
*First application: an applied research project (2026-04-05)*
