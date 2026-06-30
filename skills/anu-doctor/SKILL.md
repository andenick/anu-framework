---
name: anu-doctor
version: "2.3"
description: "Two-mode self-audit. **Framework mode** (`check_framework.py`): verifies the Anu Framework is internally consistent — skill versions match the matrix/overview, `requires:` resolves, `part-of:` matches current version, canonical docs exist, no archived skill references, generator scripts present. **Project mode** (`check_project.py`): verifies an individual data project is internally consistent — DPR coverage, L01/P02/V03 triad, registry alignment, chopped match, synthetic-data detection."
when-to-use: "After editing any SKILL.md, the framework overview, or the version matrix; before a framework release; OR after editing series_registry.json, code/ scripts, or research JSONs in a project; or when an agent reports a cross-reference that does not resolve"
search-hints: "doctor audit framework consistency version matrix requires cross-reference integrity self-check lint project registry triad coverage"
argument-hint: "[framework|project] [--fix]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
requires: none
part-of: Anu Framework v12.2
---

# Anu Doctor v2.3

Two-mode self-audit for framework and project consistency. "Entirely integrated across all skills" is not a state you reach once — it is a property you have to *keep*. Anu Doctor turns integration from a recurring manual cleanup into an invariant the framework enforces on itself.

**v2.3 (2026-05-19, evening)** added seven project-mode checks (P30-P36) following a comprehensive framework rebuild review session: rollup freshness (P30), DPR↔registry status sync (P31), V03↔registry reference-value match (P32, enforces registry-side `validation.reference_values`), no nested .git in Inputs/ (P33), orphan figures (P34), PROJECT_INDEX.md presence (P35), and the extension binary invariant (P36: subseries with -EXT iff `extension` block populated and complete; see `SERIES_REGISTRY_SCHEMA.md` § Extension Binary Invariant and `anu-extension/SKILL.md` § Binary State). Also: P04 is now format-aware (reads `chopped_format` from registry; see `anu-chopped/SKILL.md` § Format Selection) and the P02 LPV triad regex requires compact `L01_<sid>.py` naming (see `anu-replicator/SKILL.md` § Canonical Script Naming; descriptive `_load`/`_construct`/`_validate` suffixes are non-canonical). Historical context: see the framework rebuild review.

**v2.2 (2026-05-19)** added six project-mode checks (P24-P29) targeting integrity-of-state failures observed in a parallel-build review: stale ledgers (P24), exemplar-only ledgers (P25), hand-populated PIPELINE_STATE (P26), `anu_doctor_status: not_run` while stages are complete (P27), retroactive decision approvals (P28), and registry/chopped year_range drift (P29). See the framework rebuild review.

---

## Stage Position

**Infrastructure** — does not touch project data; audits the framework itself and individual project consistency. Auto-invoked by anu-build after every stage advance.

---

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| `skills/anu-*/SKILL.md` | All skill files | Yes (framework mode) |
| `docs/ANU_FRAMEWORK_OVERVIEW.md` | Framework docs | Yes (framework mode) |
| `docs/SKILL_VERSION_MATRIX.md` | Framework docs | Yes (framework mode) |
| `series_registry.json` | Project root | Yes (project mode) |
| Project code and doc directories | Project filesystem | Yes (project mode) |

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Console report | stdout | Per-check summary with PASS/FAIL/WARN |
| `FRAMEWORK_AUDIT.json` | Working directory (optional) | Machine-readable report (`--json` flag) |
| Auto-fixes | In-place edits | Only for D03 (part-of drift) and D12 (stale version strings) when `--fix` passed |

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-doctor` | Run framework checker, summarize results |
| `/anu-doctor --fix` | Run checker; auto-fix D03 and D12; re-run |
| `/anu-doctor --json` | Machine-readable JSON report |
| `/anu-doctor project --project <root>` | Run project checker on a data project |
| `/anu-doctor project --project <root> --json` | Project checker with JSON output |

### CLI

```bash
python check_framework.py            # run all D##-checks, report, exit non-zero on FAIL
python check_framework.py --json     # machine-readable report
python check_framework.py --fix      # auto-fix mechanically-fixable checks, re-run

python check_project.py --project <project_root>    # run all P##-checks
python check_project.py --project <root> --json     # machine-readable report
```

---

## Framework Mode Checks (D##)

The skill ships an executable checker at `check_framework.py` (alongside this SKILL.md). It runs the following checks against `skills/` and `docs/`:

| # | Check | Severity |
|---|---|---|
| D01 | Every `anu-*/SKILL.md` has a parseable YAML frontmatter with `name`, `version`, `part-of` | FAIL |
| D02 | The `name:` field matches the skill's directory name | FAIL |
| D03 | Every `part-of:` equals the current framework version (read from `ANU_FRAMEWORK_OVERVIEW.md`) | FAIL |
| D04 | Every skill's frontmatter `version:` matches its row in `SKILL_VERSION_MATRIX.md` | FAIL |
| D05 | Every skill's frontmatter `version:` matches its row in `ANU_FRAMEWORK_OVERVIEW.md`'s skill table | FAIL |
| D06 | `SKILL_VERSION_MATRIX.md` and `ANU_FRAMEWORK_OVERVIEW.md` agree on skill count and per-skill version | FAIL |
| D07 | Every `requires:` entry names a skill directory that exists and is not archived/removed | FAIL |
| D08 | No active skill body references an archived/removed skill by name without an "archived"/"superseded" qualifier | WARN |
| D09 | Every canonical doc cross-referenced from a SKILL.md exists on disk | FAIL |
| D10 | Generator-script claims resolve: hard-claims FAIL if missing; command-style WARN if absent; project-provided mentions not flagged | FAIL / WARN |
| D11 | The `anu-pipeline` stage map names only skills that exist | FAIL |
| D12 | No stale framework-version string (`Anu Framework v1.x` … `v11.x`) appears outside a Version History / changelog block | WARN |
| D13 | The body headline `# Anu <Name> ... vN.N` matches the frontmatter `version:` | FAIL |
| D14 | Every `SKILL.md` ships an evolution-log section (`## Version History`, `## Changelog`, or `## Skill Evolution Log`) | WARN |
| D15 | The `requires:`-graph across all skills is acyclic | FAIL |
| D16 | Every active `SKILL.md` has all 11 v12.0-template sections (Stage Position, Inputs, Outputs, Commands, Acceptance Gates, Documentation Cascade Writes, Integration with Anu Framework, Anti-Patterns, Data Repository Integration, Version History, Canonical References) | FAIL |
| D17 | `docs/schemas/skill_graph.json` exists, parses as JSON, and covers every active skill | FAIL |
| D18 | `docs/schemas/anu_build_manifest.schema.json` exists and parses as JSON | FAIL |
| D19 | Each active skill's `Stage Position` tag agrees with anu-build's canonical stage table | WARN |

Each run prints a per-check summary and exits non-zero if any FAIL-severity check fails. (Deprecated redirect stubs are skipped by D04/D05/D13/D16/D19.)

---

## Project Mode Checks (P##)

P##-checks verify that an individual data project is internally consistent:

| # | Check | Severity |
|---|---|---|
| P01 | Every `series_registry.json` entry has a corresponding `S###_DPR.md` | FAIL |
| P02 | Every series has an L01 loader, P02 processor, AND V03 validator (the LPV triad). `shared_*_loader.py` files are exempt from triad matching. | FAIL |
| P03 | Research JSON subseries declarations match the registry's subseries list | FAIL |
| P04 | Chopped CSV Row 2 column IDs match the registry's subseries declarations. **Pipeline-stage-aware**: `-EXT`/`-COMBINED` subseries are exempt (WARN not FAIL) when extension stage (Stage 4) is incomplete per `PIPELINE_STATE.json`. | FAIL |
| P05 | No stale references to renamed/removed series in code or docs | WARN |
| P06 | `status:` field values come from the standardized enum (includes `study_complete`, `extension_methodology_documented`) | FAIL |
| P07 | Every series has either a validation artifact or a `data_unavailable` status | FAIL |
| P08 | Provenance chain is intact (DPR cites a source that L01 actually reads) | WARN |
| P09 | No synthetic-data heuristics in code (`np.random`, "estimated trend", "linear interpolation placeholder") | FAIL |
| P10 | Documented divergences are also logged in `DIVERGENCE_REGISTER.json` | WARN |
| P12 | Every series ID matches the registry's declared `prefix_scheme` (supports nested-dict prefix declarations) | FAIL |
| P13 | Declared `status` is consistent with artifacts that should exist (e.g. `status: loaded` => L01 exists; `study_complete` => EPR exists) | FAIL |
| P14 | In rebuild projects (`MIGRATION/crosswalk.csv` present): every crosswalk row with `status: confirmed` has been acted on | WARN |
| P15 | `Build/ANU_BUILD_MANIFEST.json` exists and has valid schema | WARN/FAIL |
| P16 | `SUBSERIES_PLAN.json` topo-sort is acyclic and covers every subseries | FAIL |
| P17 | `ANU_LEDGER.json` and `PIPELINE_STATE.json` schema versions match framework | WARN |
| P18 | Every entry in `STEP_LOG.jsonl` parses as valid JSON | FAIL |
| P19 | Every non-stub L01 has `loader=true` in the ledger | WARN |
| P20 | `BUILD_NARRATIVE.md` last timestamp approximates `STEP_LOG.jsonl` last timestamp | WARN |
| P21 | Every series entry has minimum required fields: `name`, `chapter` (>= 0), `status`, `units`, `content_type`, `subseries` | FAIL |
| P22 | Subseries IDs follow naming conventions: start with parent ID, `-EXT`/`-COMBINED` match extension block, no `-B`/`-EXT` conflict, CRITICAL fields present | WARN |
| P23 | Series-to-downstream artifact correspondence matrix: DPR, EPR (if applicable), L01, P02, V03, chopped CSV. Writes `SERIES_CORRESPONDENCE_MATRIX.json` | WARN |
| P24 | `ANU_LEDGER.generated` is fresh relative to the latest `STEP_LOG.jsonl` entry and `PIPELINE_STATE.last_updated` | WARN |
| P25 | `ANU_LEDGER` series-inventory size matches the registry series count (no exemplar-only ledgers) | FAIL |
| P26 | Every `PIPELINE_STATE` stage marked complete is backed by `STEP_LOG` entries for that stage (honours per-stage `verification_method: filesystem_inventory`) | FAIL |
| P27 | `framework_audit.anu_doctor_status` is not `not_run` when any stage beyond Stage 0 is complete | FAIL |
| P28 | Decision documents follow `NNNN_*.md` numbering and carry an approval timestamp; no retroactive approvals | WARN |
| P29 | Registry `year_range` matches the chopped CSV min/max year per series | WARN |
| P30 | Registry top-level `by_status` / `by_content_type` rollups match per-series data | WARN |
| P31 | Each DPR markdown `Status:` line matches the registry `series[sid].status` | WARN |
| P32 | V03 hardcoded reference values match registry `validation.reference_values` | FAIL |
| P33 | `Inputs/` contains no nested `.git` directories | WARN |
| P34 | Every top-level figure is referenced by at least one series | WARN |
| P35 | `PROJECT_INDEX.md` exists at the project root | WARN |
| P36 | Extension binary invariant: a series has `-EXT`/`-COMBINED` subseries iff its `extension` block is populated and complete | FAIL |
| P37 | Every `inputs/data-repository/[SOURCE]/` checkout has a valid `PROVENANCE.md` (schema + files present) | FAIL |
| P38 | Every `inputs/data-repository/` checkout's file SHA-256s match `PROVENANCE.md` (strict re-hash) | FAIL |
| P39 | No code hardcodes `<data-repository>/DATA/` paths (reads go through `inputs/data-repository/`) | WARN |

(There is no P11 — the number was skipped when project mode was first numbered.)

Project mode replaces ad-hoc per-project verification scripts.

---

## When to Run

- After editing any `SKILL.md` frontmatter (version bump, requires change)
- After editing `ANU_FRAMEWORK_OVERVIEW.md` or `SKILL_VERSION_MATRIX.md`
- After adding, renaming, archiving, or removing a skill
- Before any framework release or handoff
- As the gate at the end of a framework-integration session
- After editing `series_registry.json`, code/ scripts, or research JSONs in a project

---

## Examples

### Framework mode — clean run

```
$ python check_framework.py
============================================================
  Anu Doctor - Framework Self-Audit
============================================================
  framework version: v12.0
  active skills:     21

  D01  20/20  [PASS]
  D02  20/20  [PASS]
  ...
  D15  1/1    [PASS]

  Summary: 0 failures, 0 warnings
============================================================
```

### Framework mode — drift detected

```
  D13  19/20  [FAIL]
        - anu-chopped: headline v1.4 != frontmatter v2.0
  D04   1/20  [FAIL]
        - anu-chopped: matrix v2.0 disagrees with frontmatter v1.4

  Summary: 2 failures, 0 warnings
```

### Project mode — DPR coverage gap

```
$ python check_project.py --project /path/to/project
  P01  62/64  [FAIL]
        - S063 has no DPR file
        - S064 has no DPR file
```

### JSON output for CI

```
$ python check_framework.py --json
{
  "framework_version": "v12.0",
  "active_skills": 20,
  "results": [
    {"check": "D01", "skill": "anu-research", "severity": "FAIL", "ok": true, "detail": "..."},
    ...
  ],
  "summary": {"fails": 0, "warns": 0}
}
```

---

## Acceptance Gates

| Gate | Condition |
|------|-----------|
| Framework clean | Zero FAIL-severity checks in D01–D19 |
| Project clean | Zero FAIL-severity checks in P01–P39 |
| Auto-fix safe | Only D03 (part-of drift) and D12 (stale version strings) are auto-fixable |
| Release gate | Framework mode CLEAN required before any framework version bump |

---

## Documentation Cascade Writes

| File | When written |
|------|-------------|
| `FRAMEWORK_AUDIT.json` | After `--json` runs (optional) |
| Auto-fixed SKILL.md files | After `--fix` for D03/D12 only |
| Console report | Every run (always) |

---

## Integration with Anu Framework

| Upstream Skill | Input Artifact | This Skill Uses It For |
|----------------|----------------|------------------------|
| **All 21 skill folders** | `SKILL.md` files | D01–D19 audit every skill's frontmatter and body |
| **Anu Build** | Stage advance events | Auto-invoked after every stage for P##-checks |
| **Anu Ledger** | Sibling | Ledger inventories *project* artifacts; Doctor inventories *framework* consistency |

---

## Anti-Patterns

- **DO NOT** edit a `SKILL.md` without running anu-doctor before committing — drift accumulates silently
- **DO NOT** use `--fix` to clear all warnings without investigation — it only auto-fixes D03 and D12; other failures need human judgment
- **DO NOT** bump a skill's `version:` field without adding a Version History entry — D14 catches missing sections but not missing entries
- **DO NOT** rename a skill folder without updating `ANU_FRAMEWORK_OVERVIEW.md` and `SKILL_VERSION_MATRIX.md` — D02 and D06 catch it post-hoc
- **DO NOT** add a `requires:` entry without confirming the dependency isn't cyclic — D15 catches cycles but they're harder to back out
- **DO NOT** skip anu-doctor in CI on the assumption that local checks are enough

---

## Version History

- **v1.0** (May 2026) — Initial release. 12 checks (D01–D12) covering frontmatter validity, version consistency, `requires:` integrity, archived-skill references, canonical-doc existence, generator-script existence, stage-map coherence, stale-version-string detection.
- **v1.1** (May 2026) — Added project mode via `check_project.py`. Ten P##-checks (P01–P10) audit individual data projects for DPR coverage, L01/P02/V03 triad completeness, research-registry alignment, chopped subseries match, status-taxonomy enum compliance, synthetic-data detection, and divergence logging.
- **v1.2** (May 2026) — Added D13 (headline vs frontmatter version match), D14 (evolution-log section required), D15 (requires-graph acyclic). Added P12 (prefix-scheme conformance), P13 (status-vs-artifacts consistency), P14 (crosswalk completeness for rebuild projects).
- **v2.0** (May 2026) — Rewritten to v12.0 common template. Added stage position, cascade writes, acceptance gates, anti-patterns sections. Updated `part-of` to Anu Framework v12.0. `requires:` remains `none`.
- **v2.1** (May 2026) — P04 now pipeline-stage-aware (extension subseries exempt when Stage 4 incomplete). P02 excludes `shared_*_loader.py` from triad matching. P06/P13 support `study_complete` and `extension_methodology_documented` statuses. New P21 (minimum required fields), P22 (subseries suffix convention), P23 (series-to-downstream correspondence matrix). P23 writes `SERIES_CORRESPONDENCE_MATRIX.json`.
- **v2.2** (May 2026) — Six project-mode checks P24–P29 (ledger freshness, ledger inventory completeness, STEP_LOG/PIPELINE_STATE consistency, anu-doctor-mandatory-before-advance, decision-log numbering, year-range integrity) from a parallel-build review.
- **v2.3** (May 2026) — Seven project-mode checks P30–P36 (rollup freshness, DPR↔registry status sync, V03↔registry reference values, no nested .git, orphan figures, PROJECT_INDEX presence, extension binary invariant) + three data-repository checks P37–P39, plus framework checks D16–D19 (v12.0 11-section template, skill-graph JSON, build-manifest schema, stage-tag agreement). P04 made format-aware; P02 triad requires compact naming.

---

## Data Repository Integration

`check_project.py` adds a data-repository compliance check:

1. **Enumerate** every `inputs/data-repository/[SOURCE]/` checkout in the project.
2. **For each checkout, verify**:
   - PROVENANCE.md exists
   - PROVENANCE.md has the required YAML frontmatter fields (see `<data-repository>/docs/DATA_CHECKOUT_CONTRACT.md`)
   - `canonical_path` resolves to an existing folder
   - Each file's recorded sha256 matches its current sha256
   - `expiry` is not in the past
3. **Cross-check the project**:
   - Grep project scripts for hardcoded `<data-repository>/DATA/` paths (anti-pattern — should read from `inputs/data-repository/`)
   - Detect projects bypassing the data repository via custom API clients (compare against the `<data-repository>/collectors/` collector names)

Outputs a data-repository compliance subscore in the project health report. Failures block `anu-build` Stage 8 (distribution).

Canonical reference: `docs/DATA_REPOSITORY_INTEGRATION.md`.

---

## Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v12.0 — Framework + Project Self-Audit*
