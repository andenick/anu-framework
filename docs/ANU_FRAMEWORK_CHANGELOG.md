# Anu Framework — Changelog

The single chronological record of framework-level changes. Per-skill version history lives in each `SKILL.md`; this file records framework-wide events — skill additions, version unifications, new canonical docs, structural changes.

The authoritative current state is always [`ANU_FRAMEWORK_OVERVIEW.md`](ANU_FRAMEWORK_OVERVIEW.md) and [`SKILL_VERSION_MATRIX.md`](SKILL_VERSION_MATRIX.md). `anu-doctor` enforces that they agree with every skill's frontmatter.

---

## 2026-05-15 — v11.0: RMWND rebuild absorption

The 21-commit Shaikh-Tonak (RMWND) rebuild — a public-facing replication package taken from blank scaffold to 64/64 PASS with `git push` to GitHub — surfaced 12 friction points the framework had no answer for. v11.0 absorbs them. RFCs at [`LESSONS_LEARNED_RMWND_2026.md`](LESSONS_LEARNED_RMWND_2026.md), [`ANU_FRAMEWORK_IMPROVEMENTS_RFC.md`](ANU_FRAMEWORK_IMPROVEMENTS_RFC.md), [`ANU_REBUILD_META_SKILL.md`](ANU_REBUILD_META_SKILL.md).

### Skill renamed

- `anu-data` → **`anu-architecture`** ("AnuData Architecture" → "Anu Architecture"). The "AnuData" name created a parallel brand inside a framework whose every other skill is named `anu-*` — readers were learning two names for one unified system. Skill folder renamed; project-level default folder `Technical/AnuData/` → `Technical/AnuArchitecture/`; legacy `Technical/AnuData/` folders in existing projects remain valid and are recognized by tooling.

### Skills added (18 → 20)

- **#19 `anu-scaffold`** (v1.0) — generates `L01_loaders/`, `P02_processors/`, `V03_validators/` script stubs from `series_registry.json` entries. Auto-selects template (`direct_column`, `derived`, `matrix_summary`) from the registry's `content_type` and construction blocks. Replaces the 17 one-off generator scripts written by hand during the RMWND build.
- **#20 `anu-rebuild`** (v1.0) — 6-wave salvage-and-port meta-workflow for taking a predecessor project Anu-Framework-native. Wraps the cadence proven on RMWND (Foundation → per-cohort → Distribution → Polish) into a reusable skill. Sub-commands: `salvage`, `crosswalk`, `scaffold`, `wave-execute`, `closeout`.

### Skills changed

- `anu-research` v2.0 → **v2.1** — adds `port` sub-command that ingests a predecessor project's research JSONs and rewrites IDs against an external mapping table.
- `anu-ingestion` v4.0 → **v4.1** — adds `migrate-scheme` (cross-project ID remapping with a CSV mapping table) and `batch-create-dpr --cohort` (cohort-level DPR scaffolding from a template). Codifies the series-status taxonomy as an enum.
- `anu-extension` v3.4 → **v3.5** — adds `batch-create-epr --cohort` for cohort-level EPR scaffolding. Integrates with the central `DIVERGENCE_REGISTER.json` via the new shared helper.
- `anu-replicator` v3.0 → **v3.1** — prescribes a `lib/` shared-helpers layout (`lib/data/`, `lib/transforms/`, `lib/validation/`, `lib/io/`) so cross-series patterns (BookColumnLoader, BenchmarkValidator, cached-API readers, IO matrix utilities) live in one canonical place.
- `anu-data` v2.0 → **anu-architecture v2.1** — RENAMED from `anu-data` (AnuData Architecture) to `anu-architecture` (Anu Architecture) for framework-name consistency. Skill folder `anu-data/` → `anu-architecture/`; project-level folder default `Technical/AnuData/` → `Technical/AnuArchitecture/` (legacy `Technical/AnuData/` still recognized). v2.1 also documents canonical cache schemas for BEA NIPA (DataValue comma-stripping, UNIT_MULT exponent application), BLS, and FRED API responses.
- `anu-pipeline` v3.1 → **v3.2** — ships `templates/run.py.j2` that scaffolds a project-level `run.py` with `--validate-only`, `--from <stage>`, `--series <sid>`, and `--health` modes.
- `anu-publish` v1.1 → **v1.2** — ships `audit.py` (port of the RMWND `S06_publish_scrub_audit.py`). Formalizes `.publish_ignore` as a standard with documented FAIL/WARN scrub patterns.
- `anu-doctor` v1.0 → **v1.1** — adds project mode via `check_project.py`. Ten P##-checks (P01–P10) audit individual data projects for DPR coverage, L01/P02/V03 triad completeness, research-registry alignment, chopped subseries match, status-taxonomy enum compliance, synthetic-data detection, and divergence logging.
- All 20 skill `SKILL.md` headers updated to `part-of: Anu Framework v11.0`.

### Infrastructure added

- **`_shared/`** package (not a skill) — cross-skill helpers. Ships `divergences.py` with `register_divergence(series_id, skill, category, predecessor_value, new_value, rationale)` so any skill can write to `<project>/DIVERGENCE_REGISTER.json`. Categories: ingestion, extension, manual_adjustment, scaffolding, scrub.

### Canonical docs added

- `LESSONS_LEARNED_RMWND_2026.md` — what worked, what hurt, build cost analysis, counterfactuals (~3000 words).
- `ANU_FRAMEWORK_IMPROVEMENTS_RFC.md` — 12 friction points with severity, evidence, proposed change, code sketch, acceptance criteria (~6000 words).
- `ANU_REBUILD_META_SKILL.md` — full SKILL.md spec for the new anu-rebuild skill (~2500 words).

---

## 2026-05-14 — v10.0 integration sweep (CD2 Sessions 30–35)

The framework was brought to full internal consistency over six working sessions driven by the CD2 reference project.

### Skills added
- **#17 `anu-archive`** (v1.0) — audit-grade transparency distribution channel; ships `generate_archive_package.py`.
- **#18 `anu-doctor`** (v1.0) — framework self-audit; ships `check_framework.py`. Checks D01–D12: version consistency across the frontmatter / matrix / overview triangle, `requires:` integrity, canonical-doc existence, generator-script existence, stage-map coherence, stale-version-string detection.

### Skills changed
- `anu-pipeline` v3.0 → **v3.1** — Stage 8 split into three sibling channels: 8a Publish, 8b Drive, 8c Archive. `anu-docs` added as a floating skill. Stage map updated to 18 skills.
- `anu-review` v4.0 → **v4.1** — D14 (Outward-Facing Intelligibility) formalized as a gate. Clarified D1–D12 as the weighted dimensions (sum 100 %) and D13/D14 as gates scored separately — fixing a pre-existing 110 %-sum bug.
- `anu-extension` v3.3 → **v3.4** — Outputs section tightened to enumerate five concrete artifacts (EPR, EXTENSION_LOG.json, registry block, extended subseries, Divergence Register).
- `anu-drive` v1.0 → **v1.1** — gained an executable generator, `generate_drive_package.py`.
- `anu-publish` v1.0 → **v1.1** — gained an executable generator, `generate_publish_package.py`; validation gate renumbered to P01–P12.
- All skill `SKILL.md` headers unified to `part-of: Anu Framework v10.0` (previously a mix of v6.0/v7.0/v8.0/v9.0).

### Canonical docs added
- `ANU_FRAMEWORK_GLOSSARY.md` — shared vocabulary (56 entries).
- `SERIES_REGISTRY_SCHEMA.md` + `schemas/series_registry.schema.json` — formal registry schema.
- `DATA_PROVENANCE_STANDARDS.md` — DPR / EPR / FPR / VPR record specs.
- `SKILL_VERSION_MATRIX.md` — the authoritative per-skill version / stage / `requires:` table.
- `ANU_FRAMEWORK_CHANGELOG.md` — this file.

### Structural changes
- The **three external distribution channels** (`anu-publish`, `anu-drive`, `anu-archive`) are now formally defined as siblings — same upstream inputs, three audiences. `anu-archive` mirrors the Publish repo and the Drive package and adds the full provenance trail.
- Every skill now carries a `## Canonical references` section linking the shared docs relevant to it.
- The `docs/` set was reconciled — obsolete docs (describing the removed `anu-standard` skill) moved to `docs/_Archive/`; stale current-state version strings corrected across the doc set.
- `anu-ledger` now records distribution events (a `distribution` block tracking which channel shipped which version when).

### Reference implementation
- **CD2** (`Projects/CD2/`) is designated the framework's reference implementation — the most complete Anu Framework project and the known-good example for new projects to copy. It exercises all 18 skills and all three distribution channels.

---

## Earlier history

Pre-v10.0 history is recorded in the individual skill `SKILL.md` Version History sections and in `ANU_FRAMEWORK_OVERVIEW.md`'s changelog block. Notable prior milestones:

- **v9.0** (May 2026) — `anu-publish` added as Stage 8.
- **v8.0** (May 2026) — `anu-pipeline` v3.0 rewrite: Research→Adequacy reorder, Review made floating.
- **v6.0** (April 2026) — Validation (V##) and Manual Adjustment (M##) stages added to the replicator.
- Earlier — the framework grew from the original `anu-standard` (now removed, superseded by `anu-ingestion`) and `anu-shiny` (now archived, superseded by `anu-visualize`).

---

*Maintained alongside `ANU_FRAMEWORK_OVERVIEW.md`. New framework-level events append a dated section at the top.*
