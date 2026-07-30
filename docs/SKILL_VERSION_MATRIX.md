# Anu Framework - Skill Version Matrix

**Framework version:** v12.2 (single source: the repo-root `VERSION` file)
**Purpose:** the single at-a-glance source of truth for which version of each
skill is current. Every `SKILL.md` frontmatter `version:` field is
authoritative; **this table is generated from those fields**.
`ANU_FRAMEWORK_OVERVIEW.md` must agree with this matrix. `anu-doctor` enforces
that agreement automatically (checks D03, D04, D05).

## The 21 shipped skills

The repository ships **21** `anu-*` skill directories. **19** are the current
pipeline set. **2** - `anu-pipeline` and `anu-rebuild` - were superseded by
`anu-build` in v12.0 but are **still shipped in full**: they are not redirect
stubs, they contain complete instructions, and `anu-ledger` still declares
`requires: anu-pipeline`. Prefer `anu-build`. See "Known inconsistency" below.

| # | Skill | Version | Status | Stage | `requires:` | Notes |
|---|---|---|---|---|---|---|
| 1 | anu-research | 2.1 | Current | 1 - RESEARCH | none | Mine KB for quotes, references, methodology per series |
| 2 | anu-adequacy | 1.2 | Current | 2 - ADEQUACY (gate) | anu-research | Post-research readiness gate (score >= 80 to advance) |
| 3 | anu-ingestion | 5.2 | Current | 3 - INGESTION | anu-research | Registry, DPRs, FPRs, decompositions, status taxonomy |
| 4 | anu-extension | 3.5 | Current | 4 - EXTENSION | anu-ingestion, anu-research | EPRs, divergence register, API integrations |
| 5 | anu-scaffold | 2.1 | Current | 5 - REPLICATION (sub) | anu-ingestion | Generate L01/P02/V03 stubs from registry entries |
| 6 | anu-replicator | 3.1 | Current | 5 - REPLICATION | anu-ingestion, anu-research, anu-extension | L01/P02/V03 reproduction package |
| 7 | anu-chopped | 2.0 | Current | 6a - OUTPUT | anu-replicator | Machine-readable CSV format |
| 8 | anu-extenbook | 3.2 | Current | 6b - OUTPUT | anu-ingestion, anu-research | Human-readable 4-sheet Excel workbooks |
| 9 | anu-visualize | 5.0 | Current | 7 - VISUALIZATION | anu-chopped, anu-replicator | Interactive visualization (Plotly Dash / R Shiny) |
| 10 | anu-publish | 2.1 | Current | 8a - DISTRIBUTION | anu-replicator, anu-chopped | GitHub replication channel |
| 11 | anu-drive | 1.1 | Current | 8b - DISTRIBUTION | anu-replicator, anu-chopped, anu-extenbook | Google Drive consumer channel |
| 12 | anu-archive | 1.0 | Current | 8c - DISTRIBUTION | anu-replicator, anu-publish, anu-drive | Audit-grade transparency channel |
| 13 | anu-review | 4.1 | Current | Floating | none | Quality audit (14 dimensions + D13/D14 gates) |
| 14 | anu-docs | 3.0 | Current | Floating | anu-research, anu-ingestion | Per-series documentation (T1/T2/T3 tiers) + the Anu Explainer |
| 15 | anu-variant | 1.4 | Current | Floating | none | Methodology variant tracking (VPRs) |
| 16 | anu-ledger | 2.2 | Current | Infrastructure | anu-pipeline, anu-ingestion | Artifact inventory + per-series stage tracking |
| 17 | anu-architecture | 2.1 | Current | Infrastructure | anu-ingestion, anu-replicator | Format standard; BEA/BLS/FRED cache schemas |
| 18 | anu-doctor | 2.3 | Current | Infrastructure | none | Framework (D01-D19) + project (P01-P39) self-audit |
| 19 | anu-build | 1.3 | Current | Orchestrator | anu-research, anu-adequacy, anu-ingestion, anu-extension, anu-replicator, anu-chopped, anu-extenbook, anu-visualize, anu-review, anu-docs, anu-variant, anu-ledger, anu-architecture, anu-publish, anu-drive, anu-archive, anu-doctor, anu-scaffold | Master orchestrator: 9-stage pipeline + 4-file cascade |
| 20 | anu-pipeline | 3.2 | Superseded | (was Orchestrator) | none | Superseded by anu-build; still ships full instructions |
| 21 | anu-rebuild | 1.1 | Superseded | (was Rebuild meta-skill) | anu-doctor, anu-ingestion, anu-publish, anu-pipeline, anu-scaffold | Superseded by anu-build (mode=rebuild); still ships full instructions |

All 21 declare `part-of: Anu Framework v12.2`.

## Known inconsistency - the superseded pair

Earlier revisions of this matrix and of `ANU_FRAMEWORK_OVERVIEW.md` described
`anu-pipeline` and `anu-rebuild` as "deprecated redirect stubs". They are not.
Measured on the shipped tree: `anu-pipeline/SKILL.md` is 291 lines with a
template and still calls itself the entry point for agents working on a data
construction project; `anu-rebuild/SKILL.md` is 539 lines with six templates;
neither mentions `anu-build`; and `anu-doctor` counts all 21 as active. The
framework therefore ships two competing orchestrators. This matrix now states
the shipped reality rather than the intent. Resolving it - either by reducing
the pair to real stubs or by re-admitting them as first-class skills - deletes
or promotes working instructions and is an open maintainer decision.

## Retired skill folders (deleted in v12.0)

| Skill folder | Deleted in | Superseded by |
|---|---|---|
| `anu-shiny-archived-20260509` | v12.0 | anu-visualize v5.0+ |
| `anu-standard-v2-removed-20260509` | v12.0 | anu-ingestion v4.0+ |

## The three external distribution channels

Skills 10, 11, 12 are siblings - same upstream inputs, three audiences:

| Channel | Skill | Audience | Generator script |
|---|---|---|---|
| GitHub replication repo | anu-publish | Developers (`git clone` + run) | `generate_publish_package.py` |
| Google Drive package | anu-drive | Scholars (open files, no code) | `generate_drive_package.py` |
| Comprehensive archive | anu-archive | Auditors (attached to GitHub Release), future-proof | `generate_archive_package.py` |

## How to keep this matrix true

1. When a skill's `SKILL.md` frontmatter `version:` changes, update this table
   and `ANU_FRAMEWORK_OVERVIEW.md` in the same commit. If the matrix lags by
   even one commit, `anu-doctor check_framework.py` fails D04/D05.
2. The frontmatter `version:` is authoritative - if any other reference
   disagrees, fix the reference, never the frontmatter.
3. The framework version lives in the repo-root `VERSION` file. Generated
   packages stamp that value; documentation footers must match it.
4. Run `python tools/check_framework.py` locally before pushing a version bump.
   **It does not currently exit 0** - see "Current self-audit state" in
   `README.md` for the failures that are known and open.
5. **Patch-version bumps (e.g. v2.2 -> v2.3) still require this propagation.**

---

*Maintained alongside `ANU_FRAMEWORK_OVERVIEW.md`. Part of the Anu Framework v12.2.*
