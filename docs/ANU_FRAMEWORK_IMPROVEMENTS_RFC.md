# Anu Framework Improvements RFC — From RMWND Build Experience

**Status**: DRAFT — ready for maintainer review
**Author**: agent (rebuild conductor)
**Companion docs**: [`LESSONS_LEARNED_RMWND_2026.md`](LESSONS_LEARNED_RMWND_2026.md), [`ANU_REBUILD_META_SKILL.md`](ANU_REBUILD_META_SKILL.md)
**Framework version target**: v11.0 (proposed)
**Skill count target**: 20 (current 18 + `anu-scaffold` + `anu-rebuild`)

---

## Context

The 21-commit RMWND rebuild (May 2026, 64 series, 100% PASS) produced 17 one-off Python generator scripts and 6 shared utility modules. **Every generator is evidence of a framework gap; every utility is evidence of a missing standard.** This RFC enumerates 12 friction points and proposes concrete remediations. Each is grounded in actual rebuild artifacts at `Projects/RMWND/Technical/`.

Format per friction point: severity, affected skills, evidence (file:line), proposed change, code sketch (~10-20 LOC), acceptance criterion, related-to. Each remediation is implementable in ≤200 LOC.

---

## Friction 1 — Cross-project ID scheme migration

**Severity**: medium
**Affected skills**: `anu-ingestion` (v4.0 → v4.1)

### Evidence

- `MIGRATION/_build_registry.py` (76 lines) — regex remapper converting `T###` → `S###` and `N####` → `ES####` across the registry, including subseries IDs and `depends_on` references.
- `anu-ingestion/SKILL.md` documents only v1→v2 dash-notation migration (`S001A` → `S001-A`); no cross-project ID change support.
- Comment in `_build_registry.py`: "ID transform: T### -> S###, N#### -> ES####"

### Proposed change

Add `anu-ingestion migrate-scheme` command. Reads a CSV mapping `old_id,new_id` and walks the entire project artifact set, applying the mapping uniformly.

### Code sketch

```python
# anu-ingestion/migrate_scheme.py (new, ~80 LOC)
# CLI: anu-ingestion migrate-scheme --table mapping.csv [--dry-run]
#
# 1. Load mapping CSV
# 2. Build regex from old_ids (sorted by length descending to avoid prefix collision)
# 3. Walk:
#    - series_registry.json (keys, depends_on, subseries IDs, references)
#    - research/*.json (series_id field + content strings)
#    - docs/series/*.md (filename + frontmatter + body)
#    - chopped/*.csv (filename + Row 2 column IDs)
#    - code/{L01,P02,V03}/*.py (filename + content)
# 4. Apply sub. Write to MIGRATION/{date}_id_migration.log
# 5. --dry-run: report planned changes, write nothing
```

Frontmatter addition to `anu-ingestion/SKILL.md`:

```yaml
commands:
  migrate-scheme:
    args: --table <csv> [--dry-run]
    purpose: Apply a series-ID mapping uniformly across all project artifacts
```

### Acceptance

- Run `anu-ingestion migrate-scheme --table mapping.csv --dry-run` on RMWND with the T→S/N→ES table. Should report changes that match `_build_registry.py`'s output byte-for-byte.
- `anu-doctor` CLEAN after the framework edit.

### Related

- Friction 11 (`anu-rebuild` invokes this as part of Wave 0)
- Friction 6 (research JSON porting performs the same ID remapping inside JSON content)

---

## Friction 2 — Batch DPR/EPR/decomposition generation

**Severity**: HIGH (highest cost of any friction point)
**Affected skills**: `anu-ingestion` (v4.0 → v4.1), `anu-extension` (v3.4 → v3.5)

### Evidence

17 generator scripts in `MIGRATION/`:
- `_gen_dprs.py`, `_gen_remaining_dprs.py` (Ch5 DPRs)
- `_gen_ch6_docs.py`, `_gen_ch6_scripts.py` (Wave 2)
- `_gen_wave3_dprs.py`, `_gen_wave4_dprs.py`, `_gen_wave5_dprs.py`
- `_gen_sprint1/2/3/4_dprs.py`, `_gen_sprint1_scripts.py`
- `_gen_decomp_epr.py`

Each is a thin template-filler over registry data. The `anu-ingestion create-dpr [series_id]` command is per-series; no batch mode.

### Proposed change

Add `anu-ingestion batch-create-{dpr,epr,decomposition}` commands with `--cohort` parameter. Use Jinja-style templates that the agent post-edits.

### Code sketch

```python
# anu-ingestion/templates/dpr_default.md.j2 (new)
"""
# {{sid}} — {{name}}

**Chapter**: {{chapter}}. **Status**: {{status}}.
**Source**: `data/source/{{source_path}}`, column `{{source_column}}`.
**Period**: {{period_start}}–{{period_end}}. **Units**: {{units}}.

## Definition
{{ narrative_placeholder }}  <!-- agent fills in -->

## Reference values
{% for year, value in benchmarks.items() %}
- {{year}}: {{value}}
{% endfor %}

## Provenance
- L01: `code/L01_loaders/L01_{{sid}}_{{slug}}.py`
- P02: `code/P02_processors/P02_{{sid}}_{{slug}}.py`
- V03: `code/V03_validators/V03_{{sid}}_{{slug}}.py`
"""

# anu-ingestion/batch_create_dpr.py (new, ~100 LOC)
# CLI: anu-ingestion batch-create-dpr --cohort wave_1_ch5 [--template default|pending_stub]
#
# 1. Read series_registry.json
# 2. Filter to cohort (chapter, wave, or explicit list)
# 3. For each series: render template with registry fields
# 4. Mark each DPR with `status: draft_from_template` in YAML frontmatter
# 5. Write to docs/series/{sid}_DPR.md
```

### Acceptance

- Run `anu-ingestion batch-create-dpr --cohort wave_1_ch5` on RMWND. Output should match (modulo my hand-edits) the existing `docs/series/S5*_DPR.md` files generated by my `_gen_dprs.py`.
- Replacing my 12 of 17 generators with this one command should be byte-equivalent to within ±5%.

### Related

- Friction 8 (`anu-scaffold` generates code scaffolds the same way DPRs are batch-generated)
- Friction 11 (`anu-rebuild` per-cohort step #3 uses this)

---

## Friction 3 — Divergence tracking outside Extension

**Severity**: medium (low operational cost, high silent-misleading risk)
**Affected skills**: `anu-ingestion`, `anu-replicator`, `anu-extension` (cross-skill)

### Evidence

- `MIGRATION/divergences_from_ST2.md` — 31-line markdown documenting one ingestion-phase divergence (S507 surplus ratio: NIPA proxy → book-faithful e/(1+e)).
- `anu-extension/SKILL.md` mentions `DIVERGENCE_REGISTER.json` (lines 325-332) but scopes it to extension-phase decisions only.
- The S507 divergence was an *ingestion-phase* judgment call — no skill home.

### Proposed change

Hoist `DIVERGENCE_REGISTER.json` to a top-level project artifact (`{project_root}/DIVERGENCE_REGISTER.json`). Add a `register_divergence()` helper invokable from any skill. Add a `category` enum: `{ingestion, extension, manual_adjustment, scaffolding, scrub}`.

### Code sketch

```python
# skills/_shared/divergences.py (new — shared by all skills)
import json
from datetime import datetime, timezone
from pathlib import Path

def register_divergence(
    project_root: Path,
    series_id: str,
    skill: str,                # 'anu-ingestion', 'anu-extension', etc.
    category: str,             # see enum above
    predecessor_value: str,    # e.g. "0.5698 from T509_surplus_ratio NIPA proxy"
    new_value: str,            # e.g. "0.6296 from algebraic identity e/(1+e)"
    rationale: str,
) -> None:
    path = project_root / "DIVERGENCE_REGISTER.json"
    register = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"divergences": []}
    register["divergences"].append({
        "series_id": series_id,
        "skill": skill,
        "category": category,
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "predecessor_value": predecessor_value,
        "new_value": new_value,
        "rationale": rationale,
    })
    path.write_text(json.dumps(register, indent=2), encoding="utf-8")
```

Update `anu-extension/SKILL.md`, `anu-ingestion/SKILL.md`, `anu-replicator/SKILL.md` to reference the shared helper and the top-level register.

### Acceptance

- Convert `MIGRATION/divergences_from_ST2.md` into a `DIVERGENCE_REGISTER.json` entry via `register_divergence()`. Result is machine-queryable.
- `anu-review` can read the register and reflect counts in `D13_data_authenticity` reporting.

### Related

- Friction 11 (`anu-rebuild` requires divergences be logged here, not in ad-hoc markdown)

---

## Friction 4 — Pre-publication scrub auditing

**Severity**: medium-high
**Affected skills**: `anu-publish` (v1.1 → v1.2)

### Evidence

- `code/S00_setup/S06_publish_scrub_audit.py` (120 lines) — walks tree, applies `.publish_ignore`, greps for `D:/Arcanum`, `Council/`, `<framework>`, `Robin`, `<decision-ref>` patterns. Excludes false-positive files (the audit script itself, chapter REVIEW reports).
- First run on RMWND: 152 findings (mostly `<decision-ref>` inherited from ST2). After scrub: 0 findings on 653 files.
- `anu-publish/SKILL.md` lists `audit` as a command (line 90, argument-hint `[audit|package|validate]`) but ships only `generate_publish_package.py` which scrubs *during* generation. There is no documented pre-generation audit.

### Proposed change

Ship `anu-publish/audit.py` adapted from my `S06_publish_scrub_audit.py`. Document the scrub pattern set in `anu-publish/SKILL.md`. Formalize `.publish_ignore` as a standard with documented syntax.

### Code sketch

```python
# anu-publish/audit.py (new, ~120 LOC — direct port of S06)
SCRUB_PATTERNS = [
    re.compile(r"D:[/\\]Arcanum"),
    re.compile(r"/Council/|\\Council\\"),
    re.compile(r"\bDruck\b"),
    re.compile(r"\bRobin/|\bRobin\\"),       # tool name, not first-name "Robin"
    re.compile(r"DEC-[A-Z0-9]+"),            # internal decision codes
]

# CLI: anu-publish audit [--strict] [--report json|text]
# Exit non-zero if findings (unless --strict false and only WARN-level patterns).

# .publish_ignore syntax (formalized):
#   - one pattern per line; '#' = comment; blank lines ignored
#   - patterns ending in '/' match directories (and subtree)
#   - patterns use fnmatch glob style
#   - patterns relative to project root
```

Add `.publish_ignore` template to skill: ship a default that excludes `MIGRATION/`, runtime JSON files, internal coordination docs.

### Acceptance

- Run `anu-publish audit` on RMWND. Output identical to my S06 final run: `CLEAN — 653 files, zero internal references.`
- Documentation in `anu-publish/SKILL.md` lists every pattern with rationale.

### Related

- Friction 11 (`anu-rebuild` Wave 6 invokes `anu-publish audit` as a gate)

---

## Friction 5 — Framework for shared code helpers

**Severity**: medium
**Affected skills**: `anu-replicator` (v3.0 → v3.1)

### Evidence

- `code/utils/series.py` (180 LOC) — `BookColumnLoader` dataclass, `BenchmarkValidator` dataclass, `cross_source_e2_check()` helper, `TOLERANCES` constants table.
- `code/utils/bea_cache.py` (60 LOC) — BEA NIPA cache reader with comma-stripping and unit conversion.
- `code/utils/io_matrix.py` (80 LOC) — Leontief matrix loader + summary statistics.
- `code/utils/fred_cache.py` (30 LOC) — FRED JSON observation parser.
- `code/utils/paths.py`, `code/utils/io.py` — project paths + IO helpers.
- `anu-replicator/SKILL.md` mentions `lib/` once but doesn't structure it.

### Proposed change

Add a "Shared helpers" section to `anu-replicator/SKILL.md` prescribing:

```
lib/
├── data/        # source-specific readers (book_table, bea_cache, fred_cache, bls_cache)
├── transforms/  # splice, reindex, aggregate
├── validation/  # tolerance classes, benchmark validators, identity checks
└── io.py        # canonical write_series_csv, write_validation_result, paths
```

Ship reference implementations as templates: `anu-replicator/templates/lib/{data,transforms,validation}/`.

### Code sketch

```python
# anu-replicator/templates/lib/data/book_table.py (extracted from RMWND code/utils/io.py)
def read_book_table(path: Path) -> pd.DataFrame:
    """Read a digitized book-table CSV.
    Handles three header conventions:
    1. Leading # comment row (Ch5 tables H.1, E.2, 5.7, E.3)
    2. Multi-row title headers ending in a column row starting with 'year'
    3. No header preamble
    """
    # (current logic from RMWND code/utils/io.py:read_book_table)
```

### Acceptance

- `anu-replicator init` creates a project with `lib/` pre-populated from templates.
- A future rebuild does not need to write `series.py` / `bea_cache.py` / `io_matrix.py` from scratch.

### Related

- Friction 10 (BEA cache pattern lives here)
- Friction 8 (`anu-scaffold` emits L01/P02/V03 that import from `lib/`)

---

## Friction 6 — Research JSON porting from predecessor

**Severity**: medium
**Affected skills**: `anu-research` (v2.0 → v2.1)

### Evidence

- `MIGRATION/_port_research.py` — walked ST2's `research/*.json`, ran ID regex transform, marked `ported_from` + `port_date`. Ported 58 of 64 series's research JSONs in one pass.
- `anu-research/SKILL.md` assumes de-novo synthesis from KB extractions (HDARP outputs). No port command.

### Proposed change

Add `anu-research port` command.

### Code sketch

```python
# anu-research/port.py (new, ~60 LOC adapted from _port_research.py)
# CLI: anu-research port --from <predecessor_research_dir> --id-map mapping.csv
#                       [--mark-as-draft]
#
# 1. For each {sid}_research.json in predecessor:
# 2. Apply id-map (T### → S###, etc.)
# 3. Add ported_from + port_date metadata
# 4. Validate against current schema (v2.0)
# 5. Write to {target}/research/{new_sid}_research.json
# 6. Report which fields needed schema upgrade
```

### Acceptance

- Running `anu-research port` on ST2's research dir reproduces my 58 ported JSONs byte-equivalent to the current state.
- The new files have `ported_from` field for traceability.

### Related

- Friction 1 (uses the same ID mapping)
- Friction 11 (anu-rebuild Wave 0 step)

---

## Friction 7 — Standardized series-status taxonomy

**Severity**: medium (low ops, high maintenance hazard)
**Affected skills**: `anu-ingestion` (schema change → v4.1)

### Evidence

Status values I created ad-hoc across the rebuild:

| Status | First use | Purpose |
|---|---|---|
| `data_unavailable` | framework standard | no data, won't fabricate |
| `data_available` | framework standard | raw source on disk |
| `book_period_validated` | Wave 1 | book-period P02+V03 pass |
| `book_period_partial_1948_1961` | Wave 1 (S508/S509/S515/S516) | partial book period coverage |
| `pending_capital_stock_data` | Wave 1 (S510/S513/S514) | needs K\* |
| `pending_data_assembly` | Wave 4 | external study data not assembled |
| `pending_data_sourcing` | Wave 3 | needs broader sourcing effort |
| `validated_book_and_extension` | Sprint 1 (S607) | both periods PASS |
| `validated_book_and_extension_partial` | Sprint 2 (S514) | extension partial coverage |
| `benchmark_only_matrix_derived` | Sprint 4 (S701-S703) | IO-matrix-benchmark-year-only |

There is no canonical enumeration; `anu-doctor` cannot validate.

### Proposed change

Enumerate allowed status values in `anu-ingestion/SKILL.md` schema spec. Add JSON schema validation. Document the semantics.

### Code sketch

```yaml
# anu-ingestion/SKILL.md schema additions (v4.1)
status:
  type: enum
  values:
    # Lifecycle
    - data_unavailable           # no values; status documented
    - data_available             # raw source on disk, not yet loaded
    - loaded                     # L01 written, intermediate CSV exists
    - validated                  # P02 + V03 PASS for the canonical period
    # Period qualifiers (suffixes; combine with above as 'validated:<scope>')
    - validated:book_period      # 1948-1989 only
    - validated:extension        # post-book only
    - validated:book_and_extension      # full spliced range
    # Pending (require explicit dependency)
    - pending:<dependency_token> # e.g. 'pending:K_star', 'pending:NIPA_loader'
    # Partial (require explicit reason)
    - partial:<reason>           # e.g. 'partial:14_year_coverage_only'
```

JSON schema enforcement in `series_registry.json`:

```json
"status": {
  "type": "string",
  "pattern": "^(data_unavailable|data_available|loaded|validated(:[a-z_]+)?|pending:[a-z_]+|partial:[a-z_]+)$"
}
```

### Acceptance

- `anu-doctor project` validates every registry status against the schema.
- Migrating my 10 ad-hoc statuses to the new enum is one-time mechanical work documented in a `MIGRATION/status_taxonomy.md`.

### Related

- Friction 12 (`anu-doctor project` enforces this)

---

## Friction 8 — NEW SKILL: `anu-scaffold` (code generation from registry)

**Severity**: high (eliminates 3+ of my generators alone)
**Affected skills**: NEW `anu-scaffold` v1.0; integrates with `anu-replicator`, `anu-ingestion`

### Evidence

- `MIGRATION/_gen_ch6_scripts.py` (170 LOC) — generated 27 scripts for Ch6 (9 series × 3 each)
- `MIGRATION/_gen_wave4_scripts.py` (220 LOC) — generated 30 scripts for 10 external-study series
- `MIGRATION/_gen_sprint1_scripts.py` (300 LOC) — generated scripts for Sprint 1 series

All three follow the same pattern: read registry entry, fill template, write three files per series.

### Proposed change

Spin up `anu-scaffold` as a focused skill that generates L01/P02/V03 stubs.

### Code sketch

```yaml
# skills/anu-scaffold/SKILL.md (new)
---
name: anu-scaffold
version: "1.0"
description: "Generate L##/P##/V## script stubs from series_registry.json entries."
when-to-use: "User has a populated registry entry and needs the boilerplate code trio scaffolded; or wants to batch-scaffold a cohort."
requires: anu-ingestion
part-of: Anu Framework v11.0
allowed-tools: Read, Write, Glob
---
```

Templates (3 included with skill):

```python
# anu-scaffold/templates/L01_direct_column.py.j2
"""L01_{{sid}} — Load {{name}} from {{source_file}} column `{{source_column}}`."""
from utils.paths import {{source_dir}}
from utils.series import BookColumnLoader

LOADER = BookColumnLoader(
    series_id     = "{{sid}}",
    subseries_id  = "{{sid}}-A",
    source_file   = {{source_dir}} / "{{source_file}}",
    source_column = "{{source_column}}",
    units         = "{{units}}",
    unit_scale    = {{unit_scale}},
)

def run():
    df = LOADER.load()
    # … (same shape as my RMWND loaders)
```

CLI:

```bash
anu-scaffold generate --series S617 --template direct_column
anu-scaffold generate --cohort wave_1_ch5 --template auto
anu-scaffold generate --all-pending  # scaffold every series with status=loaded
```

Template auto-selection from registry entry's `content_type` and `construction`:
- `time_series` with `op: load` only → `direct_column` template
- `derived` (no L01) → `derived_processor` template
- `benchmark_only` with matrix construction → `matrix_summary` template

### Acceptance

- Running `anu-scaffold generate --cohort wave_2_ch6` on a fresh project should produce the 27 Ch6 scripts I generated via `_gen_ch6_scripts.py`, byte-equivalent modulo cosmetic whitespace.
- Skill registers as `requires: anu-ingestion` (registry-driven).
- `anu-doctor` framework matrix updated to 19 skills.

### Related

- Friction 2 (analogous batch generation for DPRs)
- Friction 5 (scaffolded code imports `lib/series.py`, `lib/bea_cache.py`)
- Friction 11 (`anu-rebuild` per-cohort step #5)

---

## Friction 9 — Generic `run.py` orchestrator

**Severity**: medium
**Affected skills**: `anu-pipeline` (v3.1 → v3.2)

### Evidence

- ST2 has `Inputs/ST2/Technical/AnuData/run.py` (~200 LOC) — discovery + orchestration of S/L/P/V/M/A/O/E phases.
- I never wrote one; used ad-hoc PowerShell `foreach` loops the whole rebuild.
- `anu-pipeline/SKILL.md` describes Stage 0-8 but doesn't ship a `run.py`.

### Proposed change

`anu-pipeline init` scaffolds a project-local `run.py` from a Jinja template that the user can extend. The template handles dynamic discovery (so a new L01 added later just shows up).

### Code sketch

```python
# anu-pipeline/templates/run.py.j2 (new, ~150 LOC)
"""Pipeline orchestrator — discovers and runs all S##/L##/P##/V## scripts."""
import argparse, importlib.util, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PHASES = ["S00_setup", "L01_loaders", "P02_processors", "V03_validators",
          "M04_manual", "A05_analysis", "O06_output"]

def discover(phase_dir: Path):
    for script in sorted(phase_dir.glob("*.py")):
        if script.name.startswith("_") or script.stem == "__init__":
            continue
        yield script

def run_phase(phase: str, filter_re=None):
    for script in discover(ROOT / "code" / phase):
        if filter_re and not filter_re.search(script.stem): continue
        spec = importlib.util.spec_from_file_location(script.stem, script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "run"): mod.run()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--validate-only", action="store_true")
    p.add_argument("--from", dest="start_phase", default=None)
    p.add_argument("--series", default=None)
    p.add_argument("--health", action="store_true")
    args = p.parse_args()

    if args.health:    # run S01–S05 + anu-doctor project equivalent
        run_phase("S00_setup")
        sys.exit(0)
    if args.validate_only:
        run_phase("V03_validators", filter_re=re.compile(args.series) if args.series else None)
        sys.exit(0)
    # full pipeline
    started = False
    for phase in PHASES:
        if args.start_phase and not started and phase != args.start_phase: continue
        started = True
        run_phase(phase, filter_re=re.compile(args.series) if args.series else None)
```

### Acceptance

- `anu-pipeline init` in a new project creates `run.py`. Running `python run.py --validate-only` on RMWND post-scaffold should reproduce the 64 PASS result.

### Related

- Friction 11 (anu-rebuild Wave 0 scaffold step invokes this)

---

## Friction 10 — Cached-API loader pattern

**Severity**: medium
**Affected skills**: `anu-architecture` (v2.0 → v2.1; also renamed from `anu-data`), `anu-replicator` (v3.0 → v3.1)

### Evidence

- `code/utils/bea_cache.py` (60 LOC) — `_parse_datavalue()` strips commas, `load_bea_line(table, lineno)`, `load_bea_line_summed(table, [lines])`.
- `code/utils/fred_cache.py` (30 LOC) — parses FRED JSON observations into annual averages.
- ST2 had a similar pattern but undocumented; I rediscovered it.

### Proposed change

Ship cache-reader modules as part of `anu-architecture` v2.1 templates (under `lib/data/`). Document the cache schema each agency uses.

### Code sketch

```python
# anu-architecture/templates/lib/data/bea_cache.py (new — direct port of RMWND code/utils/bea_cache.py)
"""Read BEA cached CSV/JSON responses.

BEA's NIPA-style CSVs have columns:
  TableName, SeriesCode, LineNumber, LineDescription, TimePeriod (year),
  METRIC_NAME, CL_UNIT, UNIT_MULT, DataValue (string with commas), NoteRef

DataValue strings include thousands separators ('126,977'); strip before float().
UNIT_MULT=6 means data is in millions × 10^6; divide by 1000 for billions.
"""
def _parse_datavalue(v) -> float: ...
def load_bea_line(table_csv: str, line_number: int) -> pd.DataFrame: ...
def load_bea_line_summed(table_csv: str, line_numbers: list[int]) -> pd.DataFrame: ...

# Sibling: bls_cache.py, fred_cache.py with documented schemas per agency
```

`anu-architecture/SKILL.md` adds a "Cache schemas" section linking each module to its docs.

### Acceptance

- A future BEA-using project can `from lib.data.bea_cache import load_bea_line` immediately.
- `anu-replicator init` includes these templates if the project declares BEA/BLS/FRED usage.

### Related

- Friction 5 (these are the data/ section of the prescribed lib/ layout)

---

## Friction 11 — NEW SKILL: `anu-rebuild` (predecessor-to-rebuild meta-workflow)

**Severity**: high (eliminates the entire ad-hoc planning step)
**Affected skills**: NEW `anu-rebuild` v1.0

### Evidence

- The 21-commit RMWND rebuild was structured as 6 waves + 4 sprints — a cadence I invented mid-build (documented retroactively in `docs/ROADMAP.md` and `docs/IMPLEMENTATION_PLAN.md`).
- No framework skill currently spans the "rebuild from predecessor" use case.
- ~2 hours of upfront planning + ~10 hours of iterating on the cadence over the build.

### Proposed change

Full skill specification lives in [`ANU_REBUILD_META_SKILL.md`](ANU_REBUILD_META_SKILL.md). Summary:

- 6-wave workflow: Foundation → per-cohort implementation → Distribution → Polish
- Sub-commands: `salvage`, `crosswalk`, `scaffold`, `wave-execute`, `closeout`
- Cross-cutting policies: `Inputs/Salvaged/` is read-only, crosswalk maintained for one release cycle, all divergences logged in `DIVERGENCE_REGISTER.json`, status field discipline
- Anti-patterns documented (don't copy predecessor outputs as starting point; don't skip per-wave review; don't fabricate pending data)
- When-NOT-to-use cases (no predecessor → use `anu-pipeline` directly; small series count → skip overhead)

### Acceptance

- See Deliverable 3 acceptance section
- Skill registers as `requires: anu-doctor, anu-ingestion, anu-publish, anu-pipeline`
- `anu-doctor` framework matrix updated to 20 skills

### Related

- All other friction points compose into `anu-rebuild`'s 6-wave workflow

---

## Friction 12 — Project-level consistency checks in `anu-doctor`

**Severity**: medium
**Affected skills**: `anu-doctor` (v1.0 → v1.1)

### Evidence

- `anu-doctor/check_framework.py` checks framework self-consistency (skill versions, requires-graph, generator scripts present).
- No mode that checks PROJECT consistency.
- My `code/S00_setup/S02_generate_ledger.py` does informal coverage tracking (artifacts per series) but doesn't *validate* alignment between artifacts.

### Proposed change

Add `anu-doctor project` mode with a new `check_project.py` sibling to `check_framework.py`.

### Code sketch

```python
# anu-doctor/check_project.py (new, ~150 LOC)
"""Project-level consistency audit. Run from a project root."""

CHECKS = {
    "P01_dpr_coverage":              # every registry entry has docs/series/{sid}_DPR.md
    "P02_lpv_triad":                 # every L01 has a matching P02 and V03 (or documented derived)
    "P03_research_registry_align":   # every research JSON's series_id matches a registry entry
    "P04_chopped_subseries_match":   # chopped CSV Row 2 IDs match the registry's subseries declarations
    "P05_no_stale_refs":             # no scripts reference a renamed/deleted series
    "P06_status_taxonomy":           # every status matches the standardized enum (Friction 7)
    "P07_validation_artifacts":      # every series has data/intermediate/validation/{sid}.json
    "P08_provenance_chain":          # provenance index resolves end-to-end for every series
    "P09_no_synthetic_markers":      # no series has status: synthetic / estimated_from_benchmarks
    "P10_divergences_logged":        # divergences from predecessor appear in DIVERGENCE_REGISTER.json
}

# CLI: anu-doctor project [--strict] [--check P01,P02,...]
# Exit 0 if CLEAN; non-zero with per-check FAIL list otherwise.
```

### Acceptance

- Running `anu-doctor project` on RMWND post-Wave-6 should report all 10 checks CLEAN.
- Adding a stale reference (renaming `S501` → `S5001` in one place but not others) should cause P05 to FAIL.

### Related

- Friction 7 (P06 enforces the status taxonomy)
- Friction 3 (P10 enforces the divergence register usage)
- Friction 11 (`anu-rebuild` Wave N+2 "Polish" runs this)

---

## Cross-friction synthesis

The 12 friction points cluster into three meta-themes:

1. **Batch operations** (Friction 1, 2, 6, 8) — the framework's per-series granularity is correct for quality but expensive at scale. Each remediation adds a `--cohort` mode or porter/migrator.
2. **Cross-skill coordination** (Friction 3, 4, 7, 12) — the framework's strict skill boundaries left coordination patterns (divergences, scrub audit, status taxonomy, project-wide checks) homeless. Each remediation hoists a shared mechanism to a recognized location.
3. **Project-scoped workflows** (Friction 5, 9, 10, 11) — the framework documents the *skills* but not how to *use them at project scale*. Each remediation adds templates, orchestrators, or meta-skills.

The two new skills proposed (`anu-scaffold`, `anu-rebuild`) together solve meta-themes 1 and 3 respectively. The remaining enhancements solve meta-theme 2 within existing skills.

---

## Implementation phasing

This RFC ends with the proposed changes specified. Actual implementation follows in separate sessions:

- **Phase A** — Enhancements to existing skills (Friction 1, 2, 3, 4, 5, 6, 7, 10, 12). Each is a focused PR to the relevant `SKILL.md` plus its sibling Python files. Total: ~9 PRs.
- **Phase B** — `anu-scaffold` new skill scaffolding (Friction 8). Includes 3 templates (direct-column, derived, matrix-summary).
- **Phase C** — `anu-rebuild` new skill scaffolding (Friction 11). See Deliverable 3 for the full spec.
- **Phase D** — Framework integration: bump to v11.0, update `ANU_FRAMEWORK_OVERVIEW.md` to 20 skills, update `SKILL_VERSION_MATRIX.md`, run `anu-doctor` until CLEAN.
- **Phase E** — Validation: apply enhanced framework to a new rebuild target (e.g., porting another economic data project) and measure session count vs. RMWND baseline of 12-15 sessions. Target: 7-10 sessions.

---

## Open questions for maintainer review

1. **Framework version**: v11.0 (with 2 new skills + breaking schema change) or v10.5 (minor)? Recommendation: **v11.0** — the status taxonomy is a breaking schema change.
2. **`.publish_ignore` vs `.anu-publish-ignore`**: shorter wins for now (matches `.gitignore` convention).
3. **`anu-rebuild` vs `anu-port`**: `anu-rebuild` emphasizes from-scratch rewriting, which matches the actual workflow.
4. **Should `anu-scaffold` ship with the three templates baked in, or as a generic engine with project-supplied templates?** Recommendation: **ship the three baseline templates** (direct-column / derived / matrix-summary); allow project override.
5. **Order of implementation**: highest-leverage friction points first (2, 8, 11) or in skill-version order (1, 2, 3 → 4 → 5 → 6 → 7)? Recommendation: **leverage order**, since batch DPR generation and `anu-scaffold` and `anu-rebuild` together absorb ~70% of the cost.

---

## Verification

After implementation phases A-E:

- `anu-doctor` CLEAN across all 20 skills, no version mismatches.
- `anu-doctor project` runs against RMWND and reports CLEAN.
- The next rebuild measured against this baseline: target ≥30% session-count reduction.
- The 17 generator scripts in `MIGRATION/` should be obsolete — each one absorbed by a skill enhancement or new-skill command.
- A maintainer reading any single friction point above can implement the proposed change in ≤200 LOC.

---

*This RFC is paired with [`LESSONS_LEARNED_RMWND_2026.md`](LESSONS_LEARNED_RMWND_2026.md) (narrative + cost analysis) and [`ANU_REBUILD_META_SKILL.md`](ANU_REBUILD_META_SKILL.md) (full spec for the proposed `anu-rebuild` skill).*
