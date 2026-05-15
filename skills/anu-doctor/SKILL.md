---
name: anu-doctor
version: "1.2"
description: "Two-mode self-audit. **Framework mode** (`check_framework.py`): the Anu Framework is internally consistent — every skill's declared version matches the version matrix and overview, every `requires:` resolves, every `part-of:` matches the current framework version, every cross-referenced canonical doc exists, no skill cites a removed/archived skill, every generator script a SKILL.md claims to ship is present. **Project mode** (`check_project.py`, new in v1.1): an individual data project is internally consistent — every registry entry has a DPR + L01/P02/V03 triad, research JSON subseries align with the registry, chopped CSV Row 2 matches subseries declarations, no stale references, divergences are logged. Run after any framework or project edit."
when-to-use: "After editing any SKILL.md, the framework overview, or the version matrix; before a framework release; OR after editing series_registry.json, code/ scripts, or research JSONs in a project; or when an agent reports a cross-reference that does not resolve"
search-hints: "doctor audit framework consistency version matrix requires cross-reference integrity self-check lint project registry triad coverage"
argument-hint: "[framework|project] [--fix]"
allowed-tools: Read, Write, Bash, Glob, Grep
requires: none
part-of: Anu Framework v11.0
---

# Anu Doctor Standard v1.2

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Doctor |
| Version | 1.2 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-14 |
| Updated | 2026-05-15 |
| Purpose | Verify the Anu Framework AND individual data projects are internally consistent and self-referentially correct |

---

## Purpose

"Entirely integrated across all skills" is not a state you reach once — it is a property you have to *keep*. The framework drifts back out of integration within a few sessions of normal editing: a skill version is bumped but the overview table is not; a `requires:` points to a renamed skill; a SKILL.md references a canonical doc that was moved.

Anu Doctor turns integration from a recurring manual cleanup into an invariant the framework enforces on itself. It is the framework's own test suite.

---

## What it checks

The skill ships an executable checker at `check_framework.py` (alongside this SKILL.md). It runs the following checks against `skills/` and `docs/`:

| # | Check | Severity |
|---|---|---|
| D01 | Every `anu-*/SKILL.md` has a parseable YAML frontmatter with `name`, `version`, `part-of` | FAIL |
| D02 | The `name:` field matches the skill's directory name | FAIL |
| D03 | Every `part-of:` equals the current framework version (read from `ANU_FRAMEWORK_OVERVIEW.md`) | FAIL |
| D04 | Every skill's frontmatter `version:` matches its row in `SKILL_VERSION_MATRIX.md` | FAIL |
| D05 | Every skill's frontmatter `version:` matches its row in `ANU_FRAMEWORK_OVERVIEW.md`'s skill table | FAIL |
| D06 | `SKILL_VERSION_MATRIX.md` and `ANU_FRAMEWORK_OVERVIEW.md` agree on the skill count and the per-skill version | FAIL |
| D07 | Every `requires:` entry names a skill directory that exists and is not archived/removed | FAIL |
| D08 | No active skill body references an archived/removed skill by name (e.g. `anu-standard`, `anu-shiny`) without an "archived"/"superseded" qualifier | WARN |
| D09 | Every canonical doc cross-referenced from a SKILL.md (`ANU_FRAMEWORK_GLOSSARY.md`, `SERIES_REGISTRY_SCHEMA.md`, `DATA_PROVENANCE_STANDARDS.md`, `SKILL_VERSION_MATRIX.md`, `ANU_FRAMEWORK_OVERVIEW.md`) exists on disk | FAIL |
| D10 | Generator-script claims resolve: a SKILL.md that *hard-claims* to ship a script ("ships an executable … at X") FAILs if X is missing; a script *presented as a command* (`python X.py …`) WARNs if absent; a mention qualified as project-provided ("e.g.", "project-specific") or inside a Version History block is not flagged | FAIL / WARN |
| D11 | The `anu-pipeline` stage map names only skills that exist | FAIL |
| D12 | No stale framework-version string (`Anu Framework v1.0` … `v10.0`) appears outside a Version History / changelog block | WARN |
| D13 | The body headline `# Anu <Name> ... vN.N` matches the frontmatter `version:` | FAIL |
| D14 | Every `SKILL.md` ships an evolution-log section (`## Version History`, `## Changelog`, or `## Skill Evolution Log`) | WARN |
| D15 | The `requires:`-graph across all skills is acyclic | FAIL |

Each run prints a per-check summary and exits non-zero if any FAIL-severity check fails.

---

## Commands

### Framework mode (default)

```bash
python check_framework.py            # run all D##-checks, report, exit non-zero on FAIL
python check_framework.py --json     # machine-readable report
```

`/anu-doctor` — run the framework checker and summarize.
`/anu-doctor --fix` — run the checker; for the mechanically-fixable checks (D03 part-of drift, D12 stale version strings in current-state lines) apply the fix and re-run. Structural failures (D06 disagreement, D07 broken requires) are reported, never auto-fixed — they need human judgment.

### Project mode (new in v1.1)

```bash
python check_project.py --project <project_root>    # run all P##-checks
python check_project.py --project <root> --json     # machine-readable report
```

`/anu-doctor project --project <root>` — run the project checker and summarize.

Ten P##-checks verify that an individual data project is internally consistent:

| # | Check | Severity |
|---|---|---|
| P01 | Every `series_registry.json` entry has a corresponding `S###_DPR.md` | FAIL |
| P02 | Every series has an L01 loader, P02 processor, AND V03 validator (the LPV triad) | FAIL |
| P03 | Research JSON subseries declarations match the registry's subseries list | FAIL |
| P04 | Chopped CSV Row 2 column IDs match the registry's subseries declarations | FAIL |
| P05 | No stale references to renamed/removed series in code or docs | WARN |
| P06 | `status:` field values come from the standardized enum (anu-ingestion v4.1 taxonomy) | FAIL |
| P07 | Every series has either a validation artifact or a `data_unavailable` status | FAIL |
| P08 | Provenance chain is intact (DPR cites a source that L01 actually reads) | WARN |
| P09 | No synthetic-data heuristics in code (`np.random`, "estimated trend", "linear interpolation placeholder") | FAIL |
| P10 | Documented divergences are also logged in `DIVERGENCE_REGISTER.json` | WARN |

Project mode replaces ad-hoc per-project verification scripts (the RMWND build wrote 4 of these by hand; see Friction Point 12 in `ANU_FRAMEWORK_IMPROVEMENTS_RFC.md`).

---

## When to run

- After editing any `SKILL.md` frontmatter (version bump, requires change).
- After editing `ANU_FRAMEWORK_OVERVIEW.md` or `SKILL_VERSION_MATRIX.md`.
- After adding, renaming, archiving, or removing a skill.
- Before any framework release or handoff.
- As the gate at the end of a framework-integration session.

---

## Integration with Anu Framework

| Skill | Relationship |
|---|---|
| All 18 skills | Anu Doctor audits every one of their `SKILL.md` files |
| anu-pipeline | D11 validates the orchestrator's stage map |
| anu-ledger | Sibling infrastructure skill — anu-ledger inventories *project* artifacts; anu-doctor inventories *framework* consistency |

Anu Doctor is **infrastructure**, not a pipeline stage. It does not touch project data — it audits the framework itself.

---

## Documentation Contract

| Aspect | Detail |
|---|---|
| **Creates** | A console report; optionally `FRAMEWORK_AUDIT.json` with `--json` |
| **Expects** | `skills/anu-*/SKILL.md`, `docs/ANU_FRAMEWORK_OVERVIEW.md`, `docs/SKILL_VERSION_MATRIX.md` |
| **Must update on completion** | Nothing — it is read-only unless `--fix` is passed |

---

## Examples

### Framework mode — clean run

```
$ python check_framework.py
============================================================
  Anu Doctor - Framework Self-Audit
============================================================
  framework version: v11.0
  active skills:     20

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

The same drift surfaces in both D04 and D13 because the matrix and frontmatter diverged from the body headline. Fix the source of truth (frontmatter), then re-run.

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
  "framework_version": "v11.0",
  "active_skills": 20,
  "results": [
    {"check": "D01", "skill": "anu-research", "severity": "FAIL", "ok": true, "detail": "..."},
    ...
  ],
  "summary": {"fails": 0, "warns": 0}
}
```

---

## Anti-patterns

| Anti-pattern | Why it's wrong |
|---|---|
| Editing a `SKILL.md` and not running anu-doctor before committing | Drift accumulates silently; the next session may rely on a broken cross-reference. CI catches it but local feedback is faster. |
| Using `--fix` to clear all warnings without investigation | `--fix` only auto-fixes the mechanically-fixable D03 (part-of drift) and D12 (stale version strings) cases. Other failures need human judgment. Running it without reading the report can mask a structural issue. |
| Bumping a skill's `version:` field without adding a Version History entry | D14 (WARN) catches missing evolution-log sections but not missing entries within them. Always log the change. |
| Renaming a skill folder without updating `ANU_FRAMEWORK_OVERVIEW.md` and `SKILL_VERSION_MATRIX.md` | D02 and D06 catch it, but only after the fact. Treat the matrix and overview as part of the rename. |
| Adding a `requires:` entry to introduce a dependency without confirming the dependency isn't cyclic | D15 catches cycles, but a cycle introduced by a long chain (A → B → C → A) is harder to back out of than one caught at edit time. |
| Skipping anu-doctor in CI on the assumption that local checks are enough | Local checks drift from CI. The framework's invariant only holds if `anu-doctor` runs on every PR. |

---

## Version History

- **v1.2** (May 2026) — Added three consistency checks: **D13** (body headline `# Anu <Name> ... vN.N` must match frontmatter `version:` — FAIL), **D14** (every `SKILL.md` must ship an evolution-log section — WARN), **D15** (`requires:`-graph across skills must be acyclic — FAIL). Refreshed D12's `STALE_VERSION_RE` to cover v1.0–v10.0 (previously v1.0–v9.0 only — the regex itself had gone stale on the v11.0 bump). Discovered and fixed during the v11.0 framework-consistency audit; eight skill body headlines were stale and 30+ "Anu Framework v10.0" footers had survived the v11.0 sweep because D12 didn't match v10.
- **v1.1** (May 2026) — Added project mode via `check_project.py`. Ten P##-checks (P01–P10) audit individual data projects for DPR coverage, L01/P02/V03 triad completeness, research-registry alignment, chopped subseries match, status-taxonomy enum compliance, synthetic-data detection, and divergence logging. Addresses Friction Point 12 from the RMWND-build improvements RFC.
- **v1.0** (May 2026) — Initial release. 12 checks (D01–D12) covering frontmatter validity, version consistency across the matrix/overview/frontmatter triangle, `requires:` integrity, archived-skill references, canonical-doc existence, generator-script existence, stage-map coherence, and stale-version-string detection.

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v11.0 — Framework + Project Self-Audit.*
