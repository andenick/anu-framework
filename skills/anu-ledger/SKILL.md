---
name: anu-ledger
version: "2.2"
description: Auto-generated project manifest that inventories every artifact in an Anu Framework project. Agents read it on entry; the pipeline regenerates it after every stage. Use when orienting to a project, auditing documentation completeness, or before handoff.
when-to-use: User wants to check project health, generate artifact inventory, audit documentation completeness, or orient to an Anu project
search-hints: ledger manifest inventory artifacts health documentation audit orient project
argument-hint: [action] [chapter]
allowed-tools: Read, Write, Grep, Glob, LS, Shell
requires: anu-pipeline, anu-ingestion
part-of: Anu Framework v11.0
---

# Anu Ledger Standard v2.2

A living, auto-generated project manifest that tells agents exactly what exists, what is missing, and what needs attention. The Ledger is *not* prose documentation — it is a structured JSON file produced by a generator script that scans the project filesystem.

---

## Purpose

When an agent enters the workspace, it faces a key question: **what is the current state of this project?** The `.claude/instructions.md` explains *how* things work. The Ledger explains *where things stand right now*.

The Ledger answers:
- Which series have complete artifact sets (research, decomposition, DPR, scripts, outputs)?
- Which artifacts are missing or stale?
- What is the documentation coverage percentage per artifact type?
- What are the highest-priority gaps an agent should address?

---

## When to Use

| Situation | Action |
|-----------|--------|
| Entering a project | Read `ANU_LEDGER.json` after `.claude/instructions.md` |
| Completing a pipeline stage | Regenerate: `/anu-ledger generate` |
| Before `/handoff` | Regenerate to capture session work |
| Auditing a chapter | `/anu-ledger validate --chapter N` |
| Checking what's missing | `/anu-ledger gaps` |

---

## ANU_LEDGER.json Location

- **Canonical**: `Technical/ANU_LEDGER.json`
- **Mirror** (auto-generated during pipeline runs): `Technical/ANU_REPLICATOR/data/final-data/reports/ANU_LEDGER.json`

---

## Schema

The Ledger JSON has a fixed schema. All counts, series IDs, chapter numbers, and paths are project-specific — the schema defines the *structure*, not the values.

**Example (from the reference project project — adapt values for your project):**

```json
{
  "version": "1.0",
  "project": "[PROJECT_NAME]",
  "generated": "YYYY-MM-DDTHH:MM:SSZ",
  "generator": "ledger_generator.py v1.0",

  "project_summary": {
    "total_series": "<N>",
    "total_figures": "<N>",
    "chapters_active": ["<chapter_numbers>"],
    "documentation_health": "<0-100>",
    "last_pipeline_run": "YYYY-MM-DDTHH:MM:SSZ"
  },

  "chapters": {
    "<chapter_number>": {
      "series_count": "<N>",
      "pipeline_stage": "complete | in_progress | not_started",
      "review_score": "<0-100>",
      "artifact_coverage": {
        "research_json": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "decomposition": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "dpr": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "epr": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "loading_script": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "processing_script": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "reference_values": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "chopped_csv": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
        "extenbook": {"have": "<N>", "need": "<N>", "pct": "<0-100>"}
      }
    }
  },

  "series_inventory": {
    "S###": {
      "name": "<series_name>",
      "chapter": "<N>",
      "artifacts": {
        "research_json": {"exists": true, "path": "Technical/research/S###_research.json", "modified": "YYYY-MM-DD"},
        "decomposition": {"exists": true, "path": "Technical/docs/series/S###_DECOMPOSITION.md"},
        "dpr": {"exists": true, "path": "Technical/docs/series/S###_DPR.md"},
        "epr": {"exists": true, "path": "Technical/docs/series/S###_EPR.md"},
        "loading_script": {"exists": true, "path": "scripts/loading/L##_load_<name>.py"},
        "processing_script": {"exists": true, "path": "scripts/processing/P##_process_<name>.py"},
        "chopped_csv": {"exists": true, "path": "data/final-data/chopped/S###_chopped.csv"},
        "extenbook": {"exists": true, "path": "data/final-data/extenbooks/Anu_Extenbook_S###.xlsx"}
      },
      "has_extension": true,
      "complete": true
    }
  },

  "figures_inventory": {
    "Fig#.#": {
      "chapter": "<N>",
      "caption": "<figure caption>",
      "fpr_exists": false,
      "figure_csv_exists": true,
      "figure_csv_path": "data/final-data/figures/Fig#.#.csv",
      "columns": ["<col_names>"]
    }
  },

  "catalogs": [
    {"name": "series_registry.json", "path": "Technical/series_registry.json", "role": "canonical"}
  ],

  "stale_files": [
    {"path": "<file_path>", "reason": "<why stale>", "priority": "high | medium | low"}
  ],

  "coverage": {
    "research_json": {"have": "<N>", "need": "<N>", "pct": "<0-100>"},
    "...": "one entry per artifact type"
  },

  "action_items": [
    {"priority": "high | medium | low", "type": "missing_artifact | stale_file", "description": "<what to fix>"}
  ]
}
```

---

## Artifact Types Tracked

The Ledger checks for the following artifacts per series. **Tier-aware scoring** (v1.1+): Tier 2 series (raw input tables) are only checked for loading scripts and registry entries. They are not penalized for missing DPRs, decompositions, processing scripts, or extenbooks.

### Tier 1 Series (Composite Analytical)

| Artifact | Expected Path Pattern | Required? |
|----------|-----------------------|-----------|
| Research JSON | `Technical/research/S###_research.json` | Yes (Stage 1) |
| Decomposition | `Technical/docs/series/S###_DECOMPOSITION.md` | Yes (Stage 2) |
| DPR | `Technical/docs/series/S###_DPR.md` | Yes (Stage 2) |
| EPR | `Technical/docs/series/S###_EPR.md` | Only if extended |
| Loading script | `scripts/loading/L##_*.py` | Yes (Stage 4) |
| Processing script | `scripts/processing/P##_*.py` | Yes (Stage 4) |
| Reference values | `validation/reference_values/S###_reference.json` | Recommended |
| Validation scripts | `scripts/validation/V##_*.py` | Yes (Stage 4c) |
| Manual adjustment scripts | `scripts/manual/M##_*.py` | If adjustments needed |
| Exploration scripts | `scripts/exploration/E##_*.py` | Optional (never deleted) |
| Chopped CSV | `data/final-data/chopped/S###_*.csv` | Yes (Stage 5) |
| Extenbook | `data/final-data/extenbooks/*S###*.xlsx` | Yes (Stage 5) |

### Tier 2 Series (Raw Input Tables)

| Artifact | Expected Path Pattern | Required? |
|----------|-----------------------|-----------|
| Loading script | `scripts/loading/L##_*.py` | Yes |
| Registry entry | `series_registry.json` with `"tier": 2` | Yes |

Per figure:

| Artifact | Expected Path Pattern | Required? |
|----------|-----------------------|-----------|
| FPR | `Technical/docs/figures/Fig#.#_FPR.md` | Recommended |
| Figure CSV | `data/final-data/figures/Fig#.#.csv` | Yes (Stage 5b) |

### Project-Level Artifacts (v2.2+)

| Artifact | Expected Path | Required? |
|----------|---------------|-----------|
| DECISION_LOG.md | `docs/DECISION_LOG.md` | Yes (if decisions made) |
| ASSUMPTIONS.md | `docs/ASSUMPTIONS.md` | Yes (if assumptions documented) |
| provenance_index.json | `provenance/provenance_index.json` | Recommended |
| VALIDATION_REPORT.json | `data/final-data/VALIDATION_REPORT.json` | Yes (Stage 4c) |
| ADJUSTMENT_MANIFEST.json | `config/ADJUSTMENT_MANIFEST.json` | If M## scripts exist |

---

## Documentation Health Score

Computed as a weighted average of artifact coverage:

```
Health = (research × 15% + decomposition × 10% + dpr × 15% + epr × 10%
          + scripts × 15% + reference_values × 10% + outputs × 15% + fpr × 10%)
```

Where each term is the coverage percentage for that artifact type (0-100). The weights reflect the relative importance of each artifact type to agent comprehension and pipeline correctness.

**Tier-aware adjustment**: Tier 2 series are excluded from the denominator for artifact types they are exempt from (decomposition, DPR, EPR, processing script, extenbook). This prevents Tier 2 tables from artificially deflating the health score. The `series_inventory` shows a `tier` field for each series so agents can distinguish Tier 1 from Tier 2.

| Score | Rating |
|-------|--------|
| >= 90 | GREEN — project well-documented |
| >= 70 | YELLOW — functional with gaps |
| < 70 | RED — significant documentation gaps |

---

## The Documentation Contract Pattern

Every Anu Framework skill defines a **Documentation Contract** specifying:

1. **Creates**: What artifacts this skill produces
2. **Expects**: What artifacts must exist before this skill runs
3. **Must Update on Completion**: What documentation/state files this skill must update when it finishes work

The Ledger validates these contracts by checking that each completed stage's expected artifacts actually exist.

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-ledger generate` | Regenerate `ANU_LEDGER.json` from current filesystem state |
| `/anu-ledger generate --chapter N` | Scope generation to a single chapter |
| `/anu-ledger status` | Print summary: health score, coverage, top action items |
| `/anu-ledger validate` | Check for gaps; exit with error if mandatory artifacts missing |
| `/anu-ledger gaps` | List all missing artifacts sorted by priority |

### Generator Script

The Ledger is produced by `Technical/ANU_REPLICATOR/scripts/utils/ledger_generator.py`:

```bash
cd Technical/ANU_REPLICATOR
python scripts/utils/ledger_generator.py                    # Generate ledger
python scripts/utils/ledger_generator.py --validate         # Validate only (exit code 1 if gaps)
python scripts/utils/ledger_generator.py --chapter 2        # Scope to one chapter
python scripts/utils/ledger_generator.py --report           # Print human-readable report
```

The generator can also be invoked via `replicate.py --ledger`.

---

## Agent Orientation Protocol

When entering a project that uses the Anu Framework:

1. Read `.claude/instructions.md` — understand workflow and rules
2. Read `Technical/ANU_LEDGER.json` — understand current state
3. Read `Technical/PIPELINE_STATE.json` — understand stage progress
4. Read the latest `Technical/Handoffs/HANDOFF_*.md` — understand last session's work
5. Begin work on highest-priority action items from the Ledger

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Pipeline** | Ledger regenerated on `anu-pipeline advance`; pipeline state feeds into Ledger |
| **Anu Ingestion** | Registry feeds Ledger's series list; Ledger validates ingestion artifacts |
| **Anu Review** | D12 Documentation dimension uses Ledger coverage percentages |
| **Anu Research** | Ledger tracks research.json existence per series |
| **Anu Extension** | Ledger tracks EPR existence for extended series |
| **Anu Replicator** | `replicate.py --ledger` regenerates after pipeline runs |
| **Anu Chopped** | Chopped catalog freshness tracked in Ledger catalogs section |
| **Anu Publish / Anu Drive / Anu Archive** | Cutting a distribution package is a shipped-artifact event — regenerate the Ledger afterward so its `distribution` section records the package name, version, channel (publish / drive / archive), and timestamp |

### Distribution events

When any Stage-8 channel ships a package, regenerate the Ledger so it records the event under a `distribution` block:

```json
"distribution": {
  "publish":  {"version": "1.0.0", "shipped": "2026-05-14", "target": "github.com/..."},
  "drive":    {"version": "1.3",   "shipped": "2026-05-14", "package": "CD2_Drive_v1.3"},
  "archive":  {"version": "1.0",   "shipped": "2026-05-14", "package": "CD2_Archive_v1.0"}
}
```

This gives any agent entering the project an immediate view of what has been shipped, in which version, to which channel — without scanning `Outputs/`.

---

## Anu Framework Context

- **Pipeline Stage**: Cross-cutting (regenerated after every stage advance)
- **Upstream**: All stages (reads PIPELINE_STATE.json, series_registry.json)
- **Downstream**: Anu Review (D12 uses Ledger for coverage data)
- **Adequacy Relevance**: Should track ADEQUACY_REPORT.json as a project artifact in the artifact inventory
- **Key Handoff**: ANU_LEDGER.json is the master artifact inventory consumed by Review

## Version History

- **v1.0** (March 2026) - Initial release
- **v1.1** (March 2026) - Documented tier-aware scoring for Tier 2 series; split artifact types table into Tier 1 and Tier 2; added tier-aware health score adjustment
- **v2.0** (March 2026) - Generalized: replaced the reference project-specific schema example with generic placeholders; removed stale project-specific notes
- **v2.1** (March 2026) - Minor refinements
- **v2.2** (April 2026) - Added tracking for v6.0 artifacts: V## validation scripts, M## manual adjustment scripts, E## exploration scripts, DECISION_LOG.md, ASSUMPTIONS.md, provenance_index.json, VALIDATION_REPORT.json, ADJUSTMENT_MANIFEST.json

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `ANU_LEDGER.json` |
| **Expects** | `series_registry.json`, `PIPELINE_STATE.json` |
| **Must Update** | Regenerate Ledger after any pipeline stage completion, before `/handoff` |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Project Documentation Manifest*
