---
name: anu-rebuild
version: "1.1"
description: "Agent-executable runbook for taking a predecessor data construction project and producing a fresh, Anu-Framework-native rebuild. Six waves: Foundation → per-cohort Construction → Distribution → Polish. The agent does the work, guided by this spec; the framework provides templates and validators, not automation. Derived from the RMWND/Shaikh-Tonak rebuild (May 2026, 64 series, 100% PASS, 21 commits)."
when-to-use: "Agent has been asked to refactor or rebuild an existing data project under the Anu Framework. Open this file and execute Waves 0..N+2 sequentially."
search-hints: "rebuild refactor port salvage predecessor migration crosswalk ground-up regenerate workflow waves"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "<predecessor_root> <target_root>"
requires: anu-doctor, anu-ingestion, anu-publish, anu-pipeline, anu-scaffold
part-of: Anu Framework v11.0
---

# Anu Rebuild Standard v1.1

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Rebuild |
| Version | 1.1 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-15 |
| Updated | 2026-05-15 |
| Purpose | Agent-executable runbook for predecessor-to-rebuild |
| Derived from | RMWND/Shaikh-Tonak rebuild (May 2026, 64 series, 100% PASS) |

---

## Purpose

This skill is a **runbook**, not a tool. An agent assigned to rebuild a predecessor data project opens this file, follows the six waves top-to-bottom, and produces an Anu-Framework-native implementation.

**The framework does not provide automation for the construction work.** There is no `anu-rebuild salvage` script that decides what to copy. There is no `anu-rebuild crosswalk` script that proposes the ID mapping. There is no `anu-rebuild scaffold` script that decides the project tree. The agent makes every decision; the framework provides:

- **This spec** (what to do, in what order, with what acceptance)
- **Templates** under `templates/` and in sibling skills (DPR, EPR, FPR, registry-entry stub, crosswalk CSV header, etc.)
- **Validators** (`anu-doctor`, `audit.py`, V## scripts) that check the agent's work after each wave

Why this design: automation that makes assumptions ages badly — a script that "salvages" picks the wrong files for some project; a script that "proposes" a crosswalk imposes an ID scheme. Agents reason about each case. The framework holds them to invariants via validators.

---

## When to invoke

The agent should follow this runbook when **all four** conditions hold:

1. A **predecessor project exists** with valuable data, methodology, and/or correspondence to salvage.
2. The **target is a new public-facing repository**, fully Anu-Framework-native, ready for distribution.
3. **Series count is ≥ 20** — below that, the per-wave structure is overhead.
4. The predecessor is **not already Anu-Framework-native at the current version**. If it is, the agent applies an ID-scheme migration in-place (see `anu-ingestion/SKILL.md` § migrate-scheme procedure).

---

## Inputs the agent decides

Before starting Wave 0, the agent confirms with the user:

| Input | Default | Notes |
|---|---|---|
| `predecessor_root` | (user-provided) | Filesystem path to the prior project. Read-only during the rebuild. |
| `target_root` | (user-provided) | Filesystem path for the new build. Becomes the working directory. |
| Prefix scheme | `{primary: "D", additional: "AD"}` | Canonical scheme. `D` = Data Series (primary, from the book/study). `AD` = Additional Data Series (everything else — other studies, derivative analytical, comparison datasets). Chosen to avoid collision with anu-architecture phase prefixes (S/L/P/V/M/A/O/E). Project may add a third prefix in `MIGRATION/PREFIX_SCHEME.md` if genuinely needed. |
| Cohort partition | Book chapters | Default: one cohort per book chapter. Override if the predecessor's data has a different natural grouping. |

---

# Wave 0 — Foundation

**Goal**: empty target tree + curated salvage + decided crosswalk + registry skeleton + `anu-doctor` framework CLEAN.

The agent does these steps in order. Each is concrete enough that a fresh agent reading this can execute without further guidance.

### Step 0.1 — Decide and document the prefix scheme

Open `MIGRATION/PREFIX_SCHEME.md` (create the file from `anu-rebuild/templates/PREFIX_SCHEME_TEMPLATE.md`). Document:

- `primary`: `D` (canonical — Data Series, from the book/study being replicated)
- `additional`: `AD` (canonical — Additional Data Series, everything else: other studies, derivative analytical series, comparison datasets)
- Any project-specific extensions, with one-line justification (should be rare)

**Why D/AD and not S/ES?** `S` collides with `anu-architecture`'s Setup-phase script prefix (`S00_run_all.py`); `D` is collision-free and reads as "Data." `AD` extends naturally.

The agent uses this document throughout the rebuild as the source of truth.

### Step 0.2 — Create the project tree

```bash
mkdir -p Technical/{code,data,docs,schemas} \
         Inputs/Salvaged \
         MIGRATION \
         Outputs \
         research \
         docs/series \
         docs/figures
mkdir -p Technical/code/{S00_setup,L01_loaders,P02_processors,V03_validators,M04_manual,O06_output,E_exploration}
mkdir -p Technical/data/{raw,intermediate,final,user-inputs,source}
touch .gitignore .publish_ignore
```

The agent adapts paths to project conventions; the structure above is the RMWND-proven default.

### Step 0.3 — Salvage from the predecessor

Walk `<predecessor_root>`. For each artifact, decide: **copy to `Inputs/Salvaged/<predecessor-name>/`** or **skip**.

Copy:
- `Technical/series_registry.json` (or equivalent — `project_registry.json`, manifest file)
- `research/*.json` (if the predecessor has per-series research dossiers)
- `docs/series/*_DPR.md`, `*_EPR.md`, `*_DECOMPOSITION.md`
- `data/final/` chopped CSVs (as reference benchmarks — re-derive, don't ship)
- Correspondence, methodology notes, decision logs the predecessor maintained

Skip:
- `data/raw/` (regenerable from public sources)
- Build artifacts, caches, `__pycache__/`
- Anything under `.git/`
- Predecessor-internal infrastructure (internal monitoring tools, organizational-private directories, internal-only data acquisition platforms — substitute the predecessor's equivalents)

After copying, write a `.read_only` sentinel file at `Inputs/Salvaged/.read_only`. **Nothing in the rebuild ever writes back to this directory.** If salvaged artifacts need amendment, the agent copies them to their new location and edits the copy.

Log the salvage decisions in `MIGRATION/SALVAGE_LOG.md` (template: `anu-rebuild/templates/SALVAGE_LOG_TEMPLATE.md`).

### Step 0.4 — Decide the crosswalk

Open the predecessor's series registry. For each old series ID, the agent decides:

- **Map to a new ID** under the new prefix scheme (e.g., `T001 → S001`, `N1001 → ES1001`)
- **Drop** (predecessor had a series that doesn't survive the rebuild — note why)
- **Defer** (decision needs more research; come back later)

Write decisions to `MIGRATION/crosswalk.csv` using `anu-rebuild/templates/CROSSWALK_TEMPLATE.csv` as the header. Columns: `old_id, new_id, name, status, notes`.

**Status enum** for crosswalk rows:
- `proposed` — mapping decided, awaiting user review
- `confirmed` — user has signed off
- `dropped` — predecessor series not carried forward (notes column explains why)
- `deferred` — decision deferred

Show the crosswalk to the user before continuing. The agent's first-pass crosswalk is a *proposal*, not a final mapping.

### Step 0.5 — Build the registry skeleton

Write `Technical/series_registry.json` using `anu-rebuild/templates/REGISTRY_SKELETON_TEMPLATE.json`. Populate:

- Top-level metadata: `project`, `project_title`, `author`, `original_work`, `book`, `prefix_scheme`, `core_period`, `extension_period`
- `drive_config` block (title, author, year, publisher, institution, license) — required by `anu-drive`
- `series: {}` — populated in per-cohort waves, but each confirmed-crosswalk new_id gets a stub entry with `status: pending`
- `figures: {}` — same treatment

Don't try to fill in construction details yet. That's per-cohort work.

### Step 0.6 — Initialize git + first commit

```bash
git init -b main
git add -A
git commit -m "Wave 0: scaffold + salvaged inputs + initial crosswalk"
```

### Step 0.7 — Validate Wave 0

```bash
# Framework still consistent
python <framework>/skills/anu-doctor/check_framework.py

# Project state check — expect some FAILs (no DPRs, no L01/P02/V03 yet);
# the ones that MUST pass at this stage:
python <framework>/skills/anu-doctor/check_project.py --project .
```

**Acceptance criteria** (each must be true before declaring Wave 0 complete):

- [ ] `MIGRATION/PREFIX_SCHEME.md` exists and documents the scheme
- [ ] Project tree exists (verify with `ls`)
- [ ] `Inputs/Salvaged/` populated; `.read_only` sentinel present; `Inputs/<predecessor>/` untouched
- [ ] `MIGRATION/SALVAGE_LOG.md` accounts for every artifact copy/skip decision
- [ ] `MIGRATION/crosswalk.csv` populated with at least `proposed` status for every predecessor series
- [ ] `Technical/series_registry.json` has top-level metadata, `prefix_scheme`, `drive_config`, and series stubs
- [ ] `anu-doctor` framework: 0 FAIL / 0 WARN
- [ ] `anu-doctor` project: P06 (status taxonomy), P09 (no synthetic data), P10 (divergences logged), P12 (prefix scheme conformance) all PASS. P01/P02 will FAIL until per-cohort waves — that's expected.
- [ ] Initial commit made

---

# Waves 1..N — Per-cohort Construction

Each cohort is a logical group of series the agent builds in one wave. Default: one cohort per book chapter. For RMWND-style projects, ~13 cohorts.

For each cohort, the agent executes the following steps. Estimated 1 focused session per cohort (≤ 8 series for a medium book, scaling to 12-15 for big chapters).

### Step W.1 — Mine or port research

Two paths per series:

**Path A: Port from predecessor**

If the predecessor has a `<old_id>_research.json` that's accurate, the agent:
1. Reads `MIGRATION/crosswalk.csv` to find the `new_id`
2. Copies `Inputs/Salvaged/<predecessor>/research/<old_id>_research.json` to `research/<new_id>_research.json`
3. Rewrites SID references inside the JSON (find-and-replace `old_id` → `new_id`)
4. Adds `"ported_from": "<old_id>"` and `"ported_at": "<iso-date>"` to the JSON metadata
5. Reviews the content — is it still accurate? Does it need re-mining for missed quotes/methodology?
6. Logs the port decision in `MIGRATION/PORTING_LOG.md` (template provided)

**Path B: Mine fresh from the KB**

If no usable predecessor research exists (or the predecessor's research is too sparse), the agent follows `anu-research/SKILL.md` for fresh KB mining.

Same outcome either way: `research/<new_id>_research.json` exists, follows the schema in `anu-research/SKILL.md`, and is accurate for the series.

### Step W.2 — Adequacy gate

Follow `anu-adequacy/SKILL.md` to produce `docs/chapters/CH<N>_ADEQUACY_REPORT.json`. Score the cohort across the 5 layers. Required: ≥ 80 (ADEQUATE).

If < 80: the cohort isn't ready for ingestion. Either re-mine more research (Step W.1) or surface gaps to the user and defer the cohort.

### Step W.3 — Build DPRs

For each series in the cohort, the agent authors `docs/series/<new_id>_DPR.md` from `anu-ingestion/templates/DPR_TEMPLATE.md` (template), populating with:
- Source agency, URL, publication
- Period, units, frequency
- Construction methodology from the research JSON
- Reference values from the book (these become V## benchmarks later)

**Don't batch this.** Each DPR is a substantive document. Authoring each one forces the agent to actually understand the series.

### Step W.4 — Decompose

For each composite series, author `docs/series/<new_id>_DECOMPOSITION.md` from `anu-ingestion/templates/DECOMPOSITION_TEMPLATE.md`. Document subsources, splices, formulas.

### Step W.5 — Register

Update `Technical/series_registry.json`: replace the cohort's series stubs with full entries (subseries, units, period, content_type, status: `data_available`, etc.). Use the schema in `docs/SERIES_REGISTRY_SCHEMA.md`.

### Step W.6 — Extension methodology (extendable series only)

For series that extend beyond the book period, author `docs/series/<new_id>_EPR.md` from `anu-extension/templates/EPR_TEMPLATE.md`. Document the API source, splice methodology, concept-match justification.

Update `series_registry.json` extension block per series.

### Step W.7 — Generate code stubs

Use `anu-scaffold` to render L01/P02/V03 script stubs:

```bash
python <framework>/skills/anu-scaffold/generate.py --cohort <cohort_name>
```

This is the **only** mechanical generator the agent invokes during construction. It renders templated stubs with `# TODO:` markers. The agent fills the TODOs in.

### Step W.8 — Implement construction logic

For each L01_<sid>.py, P02_<sid>.py, V03_<sid>.py stub:

1. Read the DPR (source) and EPR (extension methodology, if any)
2. Implement L01: fetch from the documented public source
3. Implement P02: transform per the documented construction methodology
4. Implement V03: validate against reference values from the DPR

If shared helpers exist or are needed, place them in `Technical/code/lib/{data,transforms,validation,io}/` per `anu-replicator/SKILL.md` v3.1.

### Step W.9 — Run + validate

```bash
python run.py --series <each-in-cohort> --validate-only
```

Iterate until every series in the cohort PASSes V03 against its reference values. If a series fails reference-value match: investigate. Could be wrong methodology, wrong reference value, predecessor bug. Document the resolution in `DIVERGENCE_REGISTER.json` (via `_shared/divergences.py`).

### Step W.10 — Output formats

```bash
# Chopped CSVs (machine-readable)
follow anu-chopped/SKILL.md procedure

# Extenbooks (human-readable Excel)
follow anu-extenbook/SKILL.md procedure
```

### Step W.11 — Review gate

Follow `anu-review/SKILL.md` to audit the cohort. Required: score ≥ 85% scope-adjusted; D13 (data authenticity) and D14 (outward intelligibility) both GREEN.

If < 85% or D13/D14 RED: the cohort isn't ready for closeout. Address findings, re-review.

### Step W.12 — Closeout commit

```bash
python <framework>/skills/anu-doctor/check_project.py --project .   # must be CLEAN for the cohort scope
git add -A
git commit -m "Wave <N>: <cohort_name> closeout — <count> series PASS, review <score>%"
```

**Acceptance per cohort**:

- [ ] Every series in the cohort has: research JSON, DPR, decomposition (if composite), EPR (if extendable), registry entry with `validated_book_and_extension` or `book_period_validated` status, L01/P02/V03 scripts, V03 PASS against benchmarks
- [ ] `anu-review` ≥ 85% with D13 + D14 GREEN
- [ ] `anu-doctor project` CLEAN for the cohort's series
- [ ] Closeout commit with descriptive message

---

# Wave N+1 — Distribution

When all cohorts are complete:

### Step D.1 — Pre-publication scrub audit

```bash
python <framework>/skills/anu-publish/audit.py --project . --strict
```

Must report CLEAN. Iterate until zero internal-reference leaks. Common findings: hardcoded local paths, internal codenames in comments, decision-log references that mention internal tooling.

### Step D.2 — Whole-project review

Follow `anu-review/SKILL.md` for a whole-project audit. ≥ 85% with D13 + D14 GREEN required.

### Step D.3 — Generate three distribution channels

```bash
python <framework>/skills/anu-publish/generate_publish_package.py .   # GitHub-ready
python <framework>/skills/anu-drive/generate_drive_package.py .       # Drive bundle
python <framework>/skills/anu-archive/generate_archive_package.py .   # Audit archive
```

Each writes to `Outputs/`. Audit each before declaring done:

```bash
python <framework>/skills/anu-publish/audit.py --project Outputs/<bundle>/ --strict
```

### Step D.4 — Push to GitHub

```bash
cd Outputs/<project>_Publish_v1.0/
git init -b main && git add -A && git commit -m "Initial public release v1.0"
gh repo create andenick/<descriptive-slug> --public --source=. --remote=origin --push
git tag v1.0.0 && git push --tags
```

**Folder name discipline**: the slug must be descriptive (`measuring-wealth-of-nations-replication`), not a codename (`RSCD`, `the reference project`). Codename-shaped folder names get flagged by the audit.

### Step D.5 — Drive folder upload

Copy `Outputs/<project>_Drive_v1.0/` to the shared cloud folder (e.g., `E:\Storage\Cloud Drive\Shared\Heterodata\`). Cloud sync propagates.

### Step D.6 — Archive

`Outputs/<project>_Archive_v1.0.zip` stays on local disk. Verify SHA-256 checksums.

**Acceptance**:

- [ ] `anu-publish audit --strict` CLEAN at project root and on each output bundle
- [ ] Three Outputs/ directories exist + the archive zip
- [ ] GitHub repo live, tagged v1.0.0, CI green
- [ ] Drive folder copied to cloud share with descriptive slug name
- [ ] `anu-doctor project` CLEAN at the whole-project level

---

# Wave N+2 — Polish

Final pass after distribution.

### Step P.1 — Project-mode self-audit

```bash
python <framework>/skills/anu-doctor/check_project.py --project . --json
```

Resolve any remaining FAILs. WARNs are documented in a `KNOWN_ISSUES.md` if accepted-with-explanation.

### Step P.2 — Log framework friction

While the rebuild is fresh, the agent opens `MIGRATION/FRAMEWORK_FRICTIONS.md` (template provided) and lists every place the framework was less than perfect: missing templates, ambiguous specs, gaps in validation, unclear errors. This becomes input for the next framework revision (v11.1).

### Step P.3 — Final commit

```bash
git add -A && git commit -m "Wave N+2: polish — anu-doctor CLEAN, friction log captured"
git push
```

**Acceptance**:

- [ ] `anu-doctor project` 0 FAIL (WARNs allowed if documented in `KNOWN_ISSUES.md`)
- [ ] `MIGRATION/FRAMEWORK_FRICTIONS.md` populated with concrete friction points for v11.1
- [ ] Final commit pushed

---

## Cross-cutting policies

### `Inputs/Salvaged/` is read-only

Once Wave 0 completes, nothing else writes to `Inputs/Salvaged/`. If salvaged content needs amendment, copy it to its new location first. The `.read_only` sentinel marks this contract.

### Crosswalk is the source of truth during the rebuild

`MIGRATION/crosswalk.csv` is referenced for every porting decision. After v1.0 release, it freezes as a historical doc.

### Divergences logged centrally

Every divergence from the predecessor — ingestion, extension, manual adjustment, scrub — is logged via `_shared/divergences.py`'s `register_divergence()` helper into top-level `DIVERGENCE_REGISTER.json`. No silent rewrites. This is mechanical (a small function call), not automated decision-making.

### Status field discipline

Every registry entry declares a status from the enum in `anu-ingestion/SKILL.md` v4.1. Pending series carry explicit dependency tokens (`pending:<dep>`). `anu-doctor` P06 validates.

### No synthetic data, ever

Every value in every CSV traces to a real source. If unavailable, the series carries explicit `NaN` and `status: data_unavailable`. `anu-review` D13 gates the cohort closeout.

### Per-wave closeout commits

Each wave ends with a commit listing every series gained and validation status. Git log is the progress report.

### Folder naming convention

Public output folders use descriptive slugs (`measuring-wealth-of-nations-replication`), not codenames (`RSCD`, `the reference project`). Audit flags codename-shaped names.

---

## Anti-patterns

### Do not copy predecessor outputs as starting point

The predecessor's `data/final/*.csv` are reference benchmarks at most. Re-derive every value from documented sources.

**Real RMWND example**: ST2's `T507.csv` carried a NIPA-proxy surplus ratio of 0.5698 at 1948. The book identity S/Y = e/(1+e) yields 0.6296. RMWND's S507 was re-derived; the divergence was caught and logged.

### Do not skip per-wave review

The `anu-review` gate is the framework's quality enforcement. Skipping pushes defects downstream.

### Do not fabricate "pending" data

Pending series carry explicit `NaN` and `status: pending:<dependency>`. Never fill with synthetic averages, interpolations, or estimates.

### Do not let the crosswalk drift

After Wave 0 approval, every current-state artifact uses new IDs. The crosswalk + salvaged read-only inputs are the only places predecessor IDs may appear.

### Do not write scripts that automate construction decisions

If the agent finds itself wanting to write a `_apply_crosswalk_to_chopped.py` script, the agent has the wrong frame. Use Edit + Grep — the agent decides each case. The exception is `anu-scaffold`'s template rendering, which is pure boilerplate substitution with no decision-making.

### Do not invent fictional commands

Every command in this runbook is either a generic file-system operation (`mkdir`, `cp`, `git`), a validator (`anu-doctor`, `audit.py`, V## scripts), or a distribution generator (`generate_drive_package.py` etc.). There is no `anu-rebuild salvage` command. If a step in this spec requires a decision, the agent makes it.

---

## When NOT to use

| Scenario | Use instead |
|---|---|
| No predecessor; fresh project from a book | Follow `anu-pipeline/SKILL.md` directly, starting from `anu-research` |
| Predecessor already at current Anu Framework version | Apply ID-scheme migration via `anu-ingestion/SKILL.md` § migrate-scheme procedure |
| Series count < 20 | Per-series invocation of existing skills; the wave structure is overhead |
| Predecessor data unsalvageable | Treat as fresh project; the salvage step is no-op |

---

## Generalization beyond economic data

The RMWND build was economic data (Marxian aggregates). The workflow generalizes to any domain meeting the four invocation conditions.

| Domain | Predecessor | Salvage candidates | Per-cohort partition |
|---|---|---|---|
| Capital markets | ETL pipeline + analyst spreadsheets | Cleaned tick data, methodology, correspondence | by asset class |
| Sectoral employment | BLS CES historical notebook | Bridge tables, classification mappings | by NAICS sector |
| Environmental accounts | EPA + Eurostat compiled datasets | Concordance tables, satellite-data docs | by pollutant / by country |
| Heterodox replication | Author's R or Stata code | Author correspondence, classification spreadsheets | by chapter / by paper |

The 6-wave cadence applies unchanged. Only per-cohort partition varies.

---

## Integration with Anu Framework

| Skill | Where in the runbook |
|---|---|
| `anu-doctor` (required) | Wave 0 Step 0.7; Wave W.12 (per cohort); Wave N+2 Step P.1 |
| `anu-ingestion` (required) | Wave W.3 (DPRs), W.4 (decompositions), W.5 (registry); see `anu-ingestion/SKILL.md` § migrate-scheme for ID-only rebuilds |
| `anu-publish` (required) | Wave N+1 Steps D.1, D.3, D.4 |
| `anu-pipeline` (required) | The 8-stage skill orchestration is what each per-cohort wave invokes internally |
| `anu-scaffold` (required) | Wave W.7 — the only construction-time mechanical generator |
| `anu-research` | Wave W.1 (mine or port) |
| `anu-adequacy` | Wave W.2 (gate) |
| `anu-extension` | Wave W.6 (extendable series) |
| `anu-chopped`, `anu-extenbook` | Wave W.10 |
| `anu-review` | Wave W.11 (per cohort); Wave N+1 Step D.2 |
| `anu-drive`, `anu-archive` | Wave N+1 Step D.3 |

---

## Documentation Contract

| Aspect | Detail |
|---|---|
| **Creates** | `Inputs/Salvaged/`, `MIGRATION/{crosswalk.csv, SALVAGE_LOG.md, PORTING_LOG.md, PREFIX_SCHEME.md, FRAMEWORK_FRICTIONS.md}`, registry skeleton, project tree, `DIVERGENCE_REGISTER.json` |
| **Expects** | Predecessor read access, target writable directory, prefix scheme decision (default {S, ES}) |
| **Reads** | Predecessor `series_registry.json`, `research/`, `docs/series/`, `data/final/`; framework templates |
| **Updates** | `DIVERGENCE_REGISTER.json` as divergences are logged; per-wave closeout commits |

---

## Verification

The rebuild is correctly executed when:

1. `anu-doctor project` is CLEAN at Wave N+2
2. `anu-publish audit --strict` is CLEAN
3. Every divergence from the predecessor is logged in `DIVERGENCE_REGISTER.json`
4. The empirical findings of the predecessor (the book) are reproduced
5. The public release passes external review without manual scrubbing iterations
6. The next agent reading the rebuild project's git log can reconstruct the build history wave-by-wave

---

## Version History

- **v1.1** (May 2026) — Reframed as agent-executable runbook. Removed all fictional script commands (`anu-rebuild salvage|crosswalk|scaffold|wave-execute|closeout`). The agent makes decisions; the framework provides templates and validators. Added concrete acceptance criteria per step. Added explicit cross-cutting policy on folder naming (descriptive slugs, not codenames). Documented `D`/`AD` as canonical prefix scheme — Data Series (primary) and Additional Data Series — chosen to avoid collision with anu-architecture's eight phase prefixes (S/L/P/V/M/A/O/E). Project may extend with a third prefix if genuinely needed.
- **v1.0** (May 2026) — Initial release. 6-wave workflow + cross-cutting policies + anti-patterns. Derived from RMWND/Shaikh-Tonak rebuild (64 series, 100% PASS, 21 commits).

---

## Canonical references

- [`LESSONS_LEARNED_RMWND_2026.md`](../../docs/LESSONS_LEARNED_RMWND_2026.md) — experience report this runbook is derived from
- [`ANU_FRAMEWORK_IMPROVEMENTS_RFC.md`](../../docs/ANU_FRAMEWORK_IMPROVEMENTS_RFC.md) — the 12 friction-point remediations
- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary

---

*Part of the Anu Framework v11.0 — Agent-Executable Rebuild Runbook.*
