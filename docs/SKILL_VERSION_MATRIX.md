# Anu Framework — Skill Version Matrix

**Framework version:** v11.0
**Last verified:** 2026-05-15 (Session 34 — anu-scaffold and anu-rebuild added; ten skills version-bumped; verified by `anu-doctor/check_framework.py`)
**Purpose:** the single at-a-glance source of truth for which version of each skill is current. Every `SKILL.md` frontmatter `version:` field is authoritative; this table mirrors them. `ANU_FRAMEWORK_OVERVIEW.md` should agree with this matrix. `anu-doctor` enforces that agreement automatically.

## The 20 active skills

| # | Skill | Version | Stage | `requires:` | Notes |
|---|---|---|---|---|---|
| 1 | anu-research | 2.1 | 1 | none | Mine KB for quotes, references, methodology; v2.1 adds `port` sub-command |
| 2 | anu-adequacy | 1.2 | 2 (gate) | none | Post-research readiness gate |
| 3 | anu-ingestion | 4.1 | 3 | anu-research | Registry, DPRs, FPRs, decompositions; v4.1 adds migrate-scheme, batch-create-dpr, status-taxonomy enum |
| 4 | anu-extension | 3.5 | 4 | anu-ingestion, anu-research | EPRs, EXTENSION_LOG.json; v3.5 adds batch-create-epr + central DIVERGENCE_REGISTER integration |
| 5 | anu-replicator | 3.1 | 5 | anu-ingestion, anu-research, anu-extension | L##/P##/V##/M## package; v3.1 prescribes lib/ shared-helpers layout |
| 6 | anu-chopped | 2.0 | 6 | none | Machine-readable CSV format |
| 7 | anu-extenbook | 3.2 | 6 | none | 4-sheet Excel workbooks |
| 8 | anu-visualize | 5.0 | 7 | none | R Shiny + Plotly / Plotly Dash |
| 9 | anu-publish | 1.2 | 8a | anu-replicator, anu-chopped | GitHub replication channel; v1.2 ships `audit.py` (pre-publication scrub) and `generate_publish_package.py` |
| 10 | anu-drive | 1.1 | 8b | anu-replicator, anu-chopped, anu-extenbook | Google Drive consumer channel; ships `generate_drive_package.py` |
| 11 | anu-archive | 1.0 | 8c | anu-replicator, anu-publish, anu-drive | Audit-grade comprehensive channel; ships `generate_archive_package.py` |
| 12 | anu-review | 4.1 | floating | none | 12 weighted dimensions + 2 gates (D13, D14) |
| 13 | anu-docs | 1.0 | floating | none | Per-series documentation (T1/T2/T3 tiers) |
| 14 | anu-variant | 1.4 | floating | none | Methodology variant tracking (VPRs) |
| 15 | anu-pipeline | 3.2 | orchestrator | none | Sequences all 19 other skills; v3.2 ships `templates/run.py.j2` |
| 16 | anu-ledger | 2.2 | infrastructure | none | Artifact inventory; regenerate after every stage |
| 17 | anu-architecture | 2.1 | infrastructure | anu-ingestion, anu-replicator | Anu Architecture (formerly AnuData Architecture); v2.1 documents BEA/BLS/FRED cache schemas |
| 18 | anu-doctor | 1.2 | infrastructure | none | Framework + project self-audit; v1.1 ships `check_project.py`; v1.2 adds D13/D14/D15 consistency checks |
| 19 | anu-scaffold | 1.0 | infrastructure | anu-ingestion | NEW — generates L01/P02/V03 stubs from registry entries |
| 20 | anu-rebuild | 1.1 | meta-workflow | anu-doctor, anu-ingestion, anu-publish, anu-pipeline, anu-scaffold | NEW — 6-wave salvage-and-port runbook for predecessor projects; v1.1 reframed as agent-executable runbook with no fictional scripts |

All 20 declare `part-of: Anu Framework v11.0`.

## Archived skills (not counted in the 20)

| Skill folder | Status | Superseded by |
|---|---|---|
| `anu-shiny-archived-20260509` | archived | anu-visualize v5.0 |
| `anu-standard-v2-removed-20260509` | removed | anu-ingestion v4.0 |

## The three external distribution channels

Skills 9, 10, 11 are siblings — same upstream inputs, three audiences:

| Channel | Skill | Audience | Generator script |
|---|---|---|---|
| GitHub replication repo | anu-publish | Developers (`git clone` + run) | `generate_publish_package.py` |
| Google Drive package | anu-drive | Scholars (open files, no code) | `generate_drive_package.py` |
| Comprehensive archive | anu-archive | Auditors, Zenodo, future-proof | `generate_archive_package.py` |

## How to keep this matrix true

1. When a skill's `SKILL.md` frontmatter `version:` changes, update this table and the `ANU_FRAMEWORK_OVERVIEW.md` skill table in the same commit.
2. The frontmatter `version:` is authoritative — if the body headline (`# Anu X Standard vN.N`) disagrees with the frontmatter, fix the body.
3. A framework self-audit (`anu-doctor`, planned) will eventually enforce this automatically.

---

*Maintained alongside `ANU_FRAMEWORK_OVERVIEW.md`. Part of the Anu Framework v11.0.*
