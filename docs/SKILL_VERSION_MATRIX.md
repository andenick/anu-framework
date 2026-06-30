# Anu Framework — Skill Version Matrix

**Framework version:** v12.1
**Last verified:** 2026-05-24 (v12.1 spec bump — Decisions 0007 + 0008 added, framework-level anu-doctor wrappers shipped at `tools/`, `extension_year_range` + `derived_no_l01` field conventions codified, stock-form primary supported; no skill-version bumps required; verified by `anu-doctor/check_framework.py` — 21/21 PASS across D01–D19)
**Purpose:** the single at-a-glance source of truth for which version of each skill is current. Every `SKILL.md` frontmatter `version:` field is authoritative; this table mirrors them. `ANU_FRAMEWORK_OVERVIEW.md` should agree with this matrix. `anu-doctor` enforces that agreement automatically (checks D04, D05, D06).

## The 19 active skills

| # | Skill | Version | Stage | `requires:` | Notes |
|---|---|---|---|---|---|
| 1 | anu-research | 3.0 | 1 — RESEARCH | none | Mine KB for quotes, references, methodology per series |
| 2 | anu-adequacy | 2.0 | 2 — ADEQUACY (gate) | anu-research | Post-research readiness gate (score >= 80 to advance) |
| 3 | anu-ingestion | 5.2 | 3 — INGESTION | anu-research | Registry, DPRs, FPRs, decompositions, status taxonomy |
| 4 | anu-extension | 4.0 | 4 — EXTENSION | anu-ingestion, anu-research | EPRs, divergence register, API integrations |
| 5 | anu-scaffold | 2.1 | 5 — REPLICATION (sub) | anu-ingestion | Generate L01/P02/V03 stubs from registry entries |
| 6 | anu-replicator | 4.0 | 5 — REPLICATION | anu-ingestion, anu-research, anu-extension | L01/P02/V03 reproduction package |
| 7 | anu-chopped | 3.0 | 6a — OUTPUT | anu-replicator | Machine-readable CSV format |
| 8 | anu-extenbook | 4.0 | 6b — OUTPUT | anu-ingestion, anu-research | Human-readable 4-sheet Excel workbooks |
| 9 | anu-visualize | 6.1 | 7 — VISUALIZATION | anu-chopped, anu-replicator | Interactive visualization (Plotly Dash / R Shiny) |
| 10 | anu-publish | 2.1 | 8a — DISTRIBUTION | anu-replicator, anu-chopped | GitHub replication channel |
| 11 | anu-drive | 2.0 | 8b — DISTRIBUTION | anu-replicator, anu-chopped, anu-extenbook | Google Drive consumer channel |
| 12 | anu-archive | 2.0 | 8c — DISTRIBUTION | anu-replicator, anu-publish, anu-drive | Audit-grade transparency channel |
| 13 | anu-review | 5.0 | Floating | none | Quality audit (14 dimensions + D13/D14 gates) |
| 14 | anu-docs | 3.0 | Floating | anu-research, anu-ingestion | Per-series documentation (T1/T2/T3 tiers) |
| 15 | anu-variant | 2.0 | Floating | none | Methodology variant tracking (VPRs) |
| 16 | anu-ledger | 3.0 | Infrastructure | anu-ingestion | Artifact inventory + per-series stage tracking |
| 17 | anu-architecture | 3.0 | Infrastructure | anu-ingestion, anu-replicator | Format standard; BEA/BLS/FRED cache schemas |
| 18 | anu-doctor | 2.3 | Infrastructure | none | Framework (D01–D15) + project (P01–P36) self-audit |
| 19 | anu-build | 1.3 | Orchestrator | all 18 above | Master orchestrator: 9-stage pipeline + 4-file cascade |

All 19 declare `part-of: Anu Framework v12.1` (deprecated redirect stubs also bumped to v12.1).

## Deprecated skills (redirect stubs, not counted in the 19)

| Skill | Last Active Version | Redirect To |
|---|---|---|
| anu-rebuild | 1.1 | anu-build (mode=rebuild) |
| anu-pipeline | 3.2 | anu-build |

## Retired skill folders (deleted in v12.0)

| Skill folder | Deleted in | Superseded by |
|---|---|---|
| `anu-shiny-archived-20260509` | v12.0 | anu-visualize v5.0+ |
| `anu-standard-v2-removed-20260509` | v12.0 | anu-ingestion v4.0+ |

## The three external distribution channels

Skills 10, 11, 12 are siblings — same upstream inputs, three audiences:

| Channel | Skill | Audience | Generator script |
|---|---|---|---|
| GitHub replication repo | anu-publish | Developers (`git clone` + run) | `generate_publish_package.py` |
| Google Drive package | anu-drive | Scholars (open files, no code) | `generate_drive_package.py` |
| Comprehensive archive | anu-archive | Auditors (attached to GitHub Release), future-proof | `generate_archive_package.py` |

## How to keep this matrix true

1. When a skill's `SKILL.md` frontmatter `version:` changes, update this table and `ANU_FRAMEWORK_OVERVIEW.md` in the same commit. Same-commit propagation is required; if the matrix lags by even one commit, `anu-doctor check_framework.py` will fail D04/D05 and CI blocks the merge.
2. The frontmatter `version:` is authoritative — if any other reference disagrees, fix the reference.
3. `anu-doctor` checks D04, D05, D06 enforce agreement automatically. Run `python tools/check_framework.py` locally before pushing a version bump; expect 0 failures, 0 warnings.
4. **Patch-version bumps (e.g. v2.2 → v2.3) still require this propagation.** Two drift incidents have been caught by D04/D05 this way (2026-05-19): skills moved ahead of matrix on five v6.0→v6.1 / v5.0→v5.1 / v2.0→v2.1 / v2.0→v2.2 / v1.0→v1.1 changes, then again on anu-doctor v2.2→v2.3.
5. The `Last verified:` line above must be updated to the date of the most recent successful `anu-doctor check_framework.py` run.

---

*Maintained alongside `ANU_FRAMEWORK_OVERVIEW.md`. Part of the Anu Framework v12.0.*
