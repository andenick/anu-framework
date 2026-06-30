---
name: anu-build
version: "1.3"
description: Master orchestrator that drives every Anu Framework skill through a methodical 9-stage pipeline (Stage 0 Inventory through Stage 8 Distribution) with computed construction order, mandatory gates, and a 4-file documentation cascade. Replaces anu-rebuild and anu-pipeline. Canonical CLI implementation at `tools/anu_build.py` (project-agnostic, `--project <path>`).
when-to-use: Build, rebuild, or resume any Anu Framework data-construction project
search-hints: build pipeline orchestrate rebuild resume stage gate cascade
argument-hint: [command] [options]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
requires: anu-research, anu-adequacy, anu-ingestion, anu-extension, anu-replicator, anu-chopped, anu-extenbook, anu-visualize, anu-review, anu-docs, anu-variant, anu-ledger, anu-architecture, anu-publish, anu-drive, anu-archive, anu-doctor, anu-scaffold
part-of: Anu Framework v12.2
---

# Anu Build v1.3

Master orchestrator for the Anu Framework. Drives every skill through a methodical 9-stage pipeline with computed construction order, mandatory acceptance gates, and a 4-file documentation cascade that enables reliable multi-agent handoffs.

**Replaces**: `anu-rebuild` (mode=rebuild) and `anu-pipeline` (all modes).

---

## Stage Position

**Orchestrator** — calls all 18 other active skills in computed order.

---

## Execution Modes

| Mode | When | Stage 0 behavior |
|------|------|-------------------|
| `fresh` | No predecessor project | Generate manifest from user-provided scope |
| `rebuild` | Predecessor project provided | Absorb salvage, create crosswalk, generate registry skeleton |
| `resume` | Partially-complete project | Read existing state files, re-derive manifest, resume at highest incomplete stage |

---

## Canonical Stage Sequence

This is the single source of truth for stage numbering across the entire framework.

```
Stage 0:  INVENTORY       -> anu-build native (mode detection, salvage, registry, topo sort, manifest)
Stage 1:  RESEARCH         -> anu-research (mine KB for every series)
Stage 2:  ADEQUACY         -> anu-adequacy (post-research readiness gate) [GATE: score >= 80]
Stage 3:  INGESTION        -> anu-ingestion (registry finalized, DPRs, FPRs, decompositions)
Stage 4:  EXTENSION        -> anu-extension (EPRs, divergence register)
Stage 5:  REPLICATION      -> anu-scaffold + anu-replicator (L01/P02/V03 per series in topo order)
Stage 6:  OUTPUT           -> anu-chopped + anu-extenbook (machine-readable + human-readable)
Stage 7:  VISUALIZATION    -> anu-visualize (interactive app + figure export)
Stage 8:  DISTRIBUTION     -> three sibling channels:
  Stage 8a: PUBLISH        -> anu-publish (GitHub replication repo)
  Stage 8b: DRIVE          -> anu-drive (Google Drive consumer package)
  Stage 8c: ARCHIVE        -> anu-archive (audit-grade transparency package)

FLOATING (invoke at any stage):
  anu-review               -> Quality audit (14 dimensions + D13/D14 gates)
  anu-docs                 -> Per-series documentation (T1/T2/T3 tiers)
  anu-variant              -> Methodology variant tracking

INFRASTRUCTURE (auto-invoked by anu-build after every stage advance):
  anu-ledger               -> Artifact inventory regeneration
  anu-doctor               -> Framework + project consistency audit
  anu-architecture         -> Format standard (invoked at Stage 0 only)
```

---

## Documentation Cascade

The cascade is four append/regenerate files (STEP_LOG, BUILD_NARRATIVE, ANU_BUILD_MANIFEST, SUBSERIES_PLAN); the table below also lists the three related state files (registry, ledger, pipeline-state) for completeness:

| File | Owner | Mutability | Purpose |
|------|-------|------------|---------|
| `Technical/series_registry.json` | anu-ingestion | Read-only after Stage 3 | The contract: every series, subseries, construction step |
| `Technical/ANU_LEDGER.json` | anu-ledger | Regenerated after every step | Per-series artifact + stage state |
| `Technical/PIPELINE_STATE.json` | anu-build | Updated at stage boundaries | Top-level orchestration state |
| `Technical/Build/STEP_LOG.jsonl` | anu-build | Append-only | Event stream: one line per executed step |
| `Technical/Build/BUILD_NARRATIVE.md` | anu-build | Append-only | Human/LLM-readable chronological narrative |
| `Technical/Build/ANU_BUILD_MANIFEST.json` | anu-build | Written once at Stage 0 | Master execution plan with cohorts and gates |
| `Technical/Build/SUBSERIES_PLAN.json` | anu-build | Written at Stage 0, updated on registry changes | Topo-sorted construction graph |

### Reading Order for a Resuming Agent

1. `Projects/<name>/README.md` — orientation
2. `Technical/Build/BUILD_NARRATIVE.md` — last 5 entries (what happened recently)
3. `Technical/PIPELINE_STATE.json` — where are we
4. `Technical/Build/ANU_BUILD_MANIFEST.json` — what's the full plan
5. `Technical/ANU_LEDGER.json` — per-series state
6. `Technical/Build/SUBSERIES_PLAN.json` — what's the next concrete step
7. `Technical/series_registry.json` — only when needed for a specific series
8. `Technical/Build/STEP_LOG.jsonl` — only when debugging or reconstructing

---

## Canonical Project Directory Layout

All paths relative to the project's `Technical/` root. This layout is the standard for all Anu Framework projects.

```
Technical/
  series_registry.json              # THE contract (single source of truth)
  ANU_LEDGER.json                   # Per-series artifact inventory
  PIPELINE_STATE.json               # Stage-level orchestration state
  Build/
    BUILD_NARRATIVE.md              # Human/LLM-readable chronological narrative
    STEP_LOG.jsonl                  # Append-only event stream
    ANU_BUILD_MANIFEST.json         # Master execution plan (Stage 0)
    SUBSERIES_PLAN.json             # Topo-sorted construction graph
  research/                         # Stage 1 (anu-research)
    {sid}_research.json
  docs/
    series/
      {sid}_DPR.md                  # Stage 3 (anu-ingestion)
      {sid}_EPR.md                  # Stage 4 (anu-extension)
      {sid}_DECOMPOSITION.md        # Stage 3 (anu-ingestion)
      Fig{C}.{N}_FPR.md            # Stage 3 (anu-ingestion)
    chapters/
      CH{N}_ADEQUACY_REPORT.json   # Stage 2 (anu-adequacy)
  code/
    L01_loaders/
      L01_{sid}_*.py                # Stage 5 (anu-scaffold + agent)
      shared_*_loader.py            # Shared utilities (exempt from LPV triad)
    P02_processors/
      P02_{sid}_*.py                # Stage 5
    V03_validators/
      V03_{sid}_*.py                # Stage 5
  chopped/
    {sid}.csv                       # Stage 6 (anu-chopped)
  viz/
    config/
      app_config.json               # App configuration
      viz_style.json                # Theming/styling
    data/
      catalogs/
        DEFINITIVE_SERIES_CATALOG.json
        SUBSERIES_METADATA.json     # Canonical name (replaces SUBSOURCE_METADATA)
        FIGURE_SERIES_LINKAGE.json
        DATA_MANIFEST.json
    shiny/                          # Stage 7 (R variant)
      R/
        config.R, data_loader.R, chart_builder.R,
        helpers.R, validate_data.R, logger.R
      global.R, app.R
      tests/, logs/, docs/
    dash/                           # Stage 7 (Python variant)
      app.py, data_loader.py, chart_builder.py,
      validate_data.py, logger.py
      tests/, logs/, docs/
    check_quality.py                # Quality checklist runner (project-provided, e.g. one per project)
    cascade.py                      # Documentation cascade writer (ships with anu-build)
```

### Relative Path Convention

All config files, data loaders, and framework utilities MUST resolve paths relative to the project root (`Technical/`), never using absolute paths. The standard pattern:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[N]  # Navigate to Technical/
REGISTRY_PATH = PROJECT_ROOT / "series_registry.json"
CHOPPED_DIR = PROJECT_ROOT / "chopped"
DOCS_DIR = PROJECT_ROOT / "docs" / "series"
CODE_DIR = PROJECT_ROOT / "code"
```

```r
# R equivalent
project_root <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."))
registry_path <- file.path(project_root, "series_registry.json")
```

---

## Sub-series Construction Protocol (Stage 5)

Construction order is computed, not authored. The algorithm:

1. Walk every `series.{id}.construction` step in `series_registry.json`
2. For each step with `inputs`, create edges from input subseries to output subseries
3. Build a DAG; detect cross-series edges
4. Run Kahn's topological sort to produce layers
5. Within each cohort, process layers 0 through N sequentially

For each series in each cohort, in topo order:
- For each sub-series in topo order (A, B, ..., COMBINED):
  - If `op: load`: invoke L01 via anu-replicator
  - If `op: derive`: invoke P02 with declared `inputs`
  - If `op: splice`: invoke P02 with declared `at_year`, `method`
  - V03 must PASS
  - Append STEP_LOG line, patch LEDGER, append NARRATIVE paragraph

---

## Acceptance Gates

Between every pair of adjacent stages:

1. All required artifacts present for every series in cohort
2. `anu-doctor` project mode (P01–P39) zero FAIL-severity failures
3. `anu-review` score for floating dimensions in scope >= 80
4. STEP_LOG closed, LEDGER regenerated, NARRATIVE appended, PIPELINE_STATE advanced
5. `Technical/Handoffs/HANDOFF_YYYYMMDD_HHMMSS.md` written (at session boundaries)

### Data Integrity Gate (between every stage)

- No synthetic, placeholder, approximated, or frozen data in any output
- No `np.random` or fabricated values
- Every value traces to a published source or documented analytical method
- All series with missing data marked `"status": "data_unavailable"` (not filled)

---

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| `series_registry.json` | anu-ingestion output | Yes |
| `Inputs/` directory | User-provided source material | Yes |
| Predecessor project root | User-provided (mode=rebuild only) | Conditional |
| `ANU_LEDGER.json` | anu-ledger (mode=resume) | Conditional |
| `PIPELINE_STATE.json` | Prior anu-build run (mode=resume) | Conditional |

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| `Technical/Build/ANU_BUILD_MANIFEST.json` | Build dir | Master execution plan |
| `Technical/Build/SUBSERIES_PLAN.json` | Build dir | Topo-sorted construction graph |
| `Technical/Build/STEP_LOG.jsonl` | Build dir | Event stream |
| `Technical/Build/BUILD_NARRATIVE.md` | Build dir | Chronological narrative |
| `Technical/PIPELINE_STATE.json` | Technical root | Updated orchestration state |
| `Technical/ANU_LEDGER.json` | Technical root | Updated per-series state |
| All skill outputs from Stages 1–8 | Various | Research JSONs, DPRs, EPRs, L01/P02/V03, chopped, extenbooks, viz, distribution |

---

## Commands

The canonical CLI is `python tools/anu_build.py --project <path> <subcommand>`. Projects may ship a thin local shim (e.g. `Technical/build.py`) that imports `anu_build.main(default_project=...)` so users in the project directory can omit `--project`. The full v1.0 verb set (init / plan / run-stage / run-to-completion / audit / handoff) is reserved for orchestrator extensions; the implemented v1.2 subcommands are:

| Command | CLI | Description |
|---------|-----|-------------|
| `/anu-build status` | `python anu_build.py --project <path> status` | Print stage/cohort/series progress |
| `/anu-build advance` | `python anu_build.py --project <path> advance` | Identify the next pipeline action (no execution) |
| `/anu-build validate` | `python anu_build.py --project <path> validate` | Read-only conformance check (wraps anu-doctor project mode) |
| `/anu-build chopped` | `python anu_build.py --project <path> chopped` | Regenerate Anu Chopped CSVs (delegates to `code/O06_output/O01_*`) |
| `/anu-build extenbooks` | `python anu_build.py --project <path> extenbooks` | Regenerate Anu Extenbook workbooks (delegates to `code/O06_output/O02_*`) |
| `/anu-build ledger` | `python anu_build.py --project <path> ledger` | Regenerate `ANU_LEDGER.json` (delegates to `code/S00_setup/S02_*` with inline fallback) |
| `/anu-build viz` | `python anu_build.py --project <path> viz` | Run `viz/check_quality.py` quality checker |
| `/anu-build review` | `python anu_build.py --project <path> review` | Summarise latest `Technical/Handoffs/ANU_REVIEW_*.md` |
| `/anu-build help` | `python anu_build.py help` | Print orchestrator help |

The CLI is also importable: `from anu_build import status, advance, validate, chopped, extenbooks, ledger, viz, review, main, BuildContext, resolve_context`. Each subcommand function takes a `BuildContext` and returns an int exit code.

---

## Stage-Transition Gates

| Gate | Condition |
|------|-----------|
| Stage 0 → 1 | Registry exists, manifest generated, SUBSERIES_PLAN computed, anu-doctor project CLEAN |
| Stage 1 → 2 | Research coverage 100% (all series have research JSONs) |
| Stage 2 → 3 | All adequacy reports score >= 80 |
| Stage 3 → 4 | All DPRs exist, registry finalized, decompositions complete |
| Stage 4 → 5 | EPRs exist for all extending series, divergence register present |
| Stage 5 → 6 | All L01/P02/V03 triads complete, VALIDATION_REPORT.json all PASS, zero scaffold_only |
| Stage 6 → 7 | All chopped CSVs + extenbooks present and validated |
| Stage 7 → 8 | Viz app launches, all series visible, D10 >= 80 |
| Stage 8 done | Publish/Drive/Archive bundles present, anu-review >= 85, D13/D14 >= 90 |

---

## Documentation Cascade Writes

| File | When written |
|------|-------------|
| STEP_LOG.jsonl | After every atomic action (series processed, artifact created, gate checked) |
| BUILD_NARRATIVE.md | After every STEP_LOG append (1-3 paragraph summary) |
| ANU_LEDGER.json | After every action that changes per-series state |
| PIPELINE_STATE.json | At stage boundaries and session boundaries |

---

## Integration with Anu Framework

| Upstream Skill | Input Artifact | This Skill Uses It For |
|----------------|----------------|------------------------|
| anu-research | `research/*.json` | Stage 1 gate check |
| anu-adequacy | `ADEQUACY_REPORT.json` | Stage 2 gate check |
| anu-ingestion | `series_registry.json`, DPRs | Stage 3 gate, construction graph |
| anu-extension | EPRs, `EXTENSION_LOG.json` | Stage 4 gate |
| anu-scaffold | L01/P02/V03 stubs | Stage 5 code generation |
| anu-replicator | Validation artifacts | Stage 5 gate |
| anu-chopped | Chopped CSVs | Stage 6 gate |
| anu-extenbook | Extenbook xlsx | Stage 6 gate |
| anu-visualize | Dash/Shiny app | Stage 7 gate |
| anu-publish | `Outputs/Publish/` | Stage 8a gate |
| anu-drive | `Outputs/Drive/` | Stage 8b gate |
| anu-archive | `Outputs/Archive/` | Stage 8c gate |
| anu-review | Review reports | Floating gate checks |
| anu-docs | Per-series docs + Anu Explainers (`docs/explainers/{SID}_EXPLAINER.md`, anu-docs v3.0) | Floating quality enrichment; explainers REQUIRED before Stage 8a `web`-profile publish (DOC11) |
| anu-variant | Variant registry | Floating methodology tracking |
| anu-ledger | `ANU_LEDGER.json` | Per-series state after every action |
| anu-doctor | P01–P39 results | Gate enforcement |
| anu-architecture | Format standard | Stage 0 validation |

---

## Anti-Patterns

- **DO NOT** skip gates — every stage boundary requires explicit gate passage
- **DO NOT** process series out of topo order — downstream series may depend on upstream outputs
- **DO NOT** fabricate data — any missing value must be `data_unavailable`, never synthetic
- **DO NOT** write STEP_LOG or NARRATIVE without the other — they are always written together
- **DO NOT** advance PIPELINE_STATE without regenerating the LEDGER first
- **DO NOT** modify `series_registry.json` after Stage 3 — it is frozen
- **DO NOT** copy from predecessor projects directly — use Inputs/Salvaged/ as the staging area
- **DO NOT** run stages out of order — the stage sequence is invariant

---

## Data Repository Integration

Stage 0 (Inventory) walks `inputs/data-repository/` and records every checkout. Stage 8 (Distribution) runs `/data-validate --strict` — pipeline fails if any data-repository checkout drift detected. Other stages do not modify data-repository checkouts.

## Version History

- **v1.0** (May 2026) — Initial release. Consolidates anu-rebuild v1.1 and anu-pipeline v3.2 into a single orchestrator. 9-stage pipeline with computed construction order. 4-file documentation cascade. LLM read-order protocol. Part of Anu Framework v12.0.
- **v1.1** (May 2026) — Added canonical project directory layout with all standard paths relative to `Technical/`. Added relative path convention requirement (no absolute paths). Documented `SUBSERIES_METADATA.json` as canonical name (replaces `SUBSOURCE_METADATA`). Added shared loader convention (`shared_*_loader.py` exempt from LPV triad).
- **v1.3** (June 2026) — Anu Framework v12.2 web-readiness release: registered the Anu Explainer (anu-docs v3.0) in the cascade — explainers are REQUIRED before a Stage 8a `web`-profile publish (DOC11 gate). Headline/matrix/overview version stamps re-synced.
- **v1.2** (May 2026) — Promoted a reference project's per-project `build.py` into a project-agnostic orchestrator at `tools/anu_build.py` taking `--project <path>`. Resolves all per-project paths from `<project>/Technical/`. Importable surface (`status`, `advance`, `validate`, `chopped`, `extenbooks`, `ledger`, `viz`, `review`, `main`, `BuildContext`, `resolve_context`). The reference project's `Technical/build.py` is now a thin shim that injects `default_project` so per-project UX is unchanged. Other Anu v12.0+ projects can adopt the same shim pattern (5 lines) or invoke `anu_build.py` directly.

---

## Canonical References

- [`ANU_FRAMEWORK_OVERVIEW.md`](../../../docs/ANU_FRAMEWORK_OVERVIEW.md) — framework architecture
- [`ANU_FRAMEWORK_GLOSSARY.md`](../../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary
- [`SERIES_REGISTRY_SCHEMA.md`](../../../docs/SERIES_REGISTRY_SCHEMA.md) — registry schema
- [`SKILL_DEPENDENCY_GRAPH.md`](../../../docs/SKILL_DEPENDENCY_GRAPH.md) — skill dependency DAG
- [`ANU_BUILD_PROTOCOL.md`](../../../docs/ANU_BUILD_PROTOCOL.md) — multi-agent handoff protocol
- [`schemas/anu_build_manifest.schema.json`](../../../docs/schemas/anu_build_manifest.schema.json)
- [`schemas/subseries_plan.schema.json`](../../../docs/schemas/subseries_plan.schema.json)
- [`schemas/ledger_v12.schema.json`](../../../docs/schemas/ledger_v12.schema.json)
- [`schemas/pipeline_state_v12.schema.json`](../../../docs/schemas/pipeline_state_v12.schema.json)

---

*Part of the Anu Framework v12.0 — Master Orchestrator*
*Lineage: anu-rebuild v1.1 + anu-pipeline v3.2 → anu-build v1.0*
