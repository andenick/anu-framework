---
name: anu-publish
version: "2.1"
description: "Publication pipeline that transforms internal Anu Framework projects into clean, publishable artifacts. Handles scrubbing (API keys, internal paths, framework-internal references via .publish_ignore; path/Arcanum leaks are FAIL-severity), packaging (data-only, data+pipeline, data+pipeline+viz, full, plus the web profile — the formal Anu→website export contract with parquet + data_dictionary + WEB_MANIFEST), validation (pre-publication gate P01-P15), and formatting (README, CITATION.cff, LICENSE). Ships generate_publish_package.py and audit.py."
when-to-use: "User wants to prepare a data project for public release, scrub sensitive data from a repo, validate a package for publication, or generate publication artifacts (CITATION.cff, LICENSE)"
search-hints: "publish release package scrub validate public repo github export citation license audit publish-ignore"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[audit|package|validate] [project] [profile]"
requires: anu-replicator, anu-chopped
part-of: Anu Framework v12.2
---

# Anu Publish v2.1

**Stage 8a — DISTRIBUTION (Publish)**

Transform an internal Anu Framework project into a clean, publishable artifact. Handles the full lifecycle from audit through export. One of three sibling distribution channels that consume the same upstream outputs and serve different audiences.

| Channel | Skill | Audience | What ships |
|---|---|---|---|
| **Publish (this skill)** | `anu-publish` | Developers who `git clone` and run the pipeline | Scrubbed code + data + CI, GitHub-ready |
| Drive | `anu-drive` | Scholars who open files, never run code | Master workbook, codebook, methodology PDF, per-series workbooks |
| Archive | `anu-archive` | Auditors, journal data editors (attached to GitHub Release) | Everything: code + data + full provenance trail + manifest + checksums |

A project may ship any subset. `anu-archive` typically runs last, mirroring the Publish repo into its `code/` directory and the Drive package into its `data/` directory.

**Core Principle**: Every published value must be reproducible. A researcher who clones the exported repo, installs dependencies, provides their own (free) API keys, and runs the pipeline must get the same results. No internal tools, private databases, or Arcanum infrastructure should be required. No placeholders, no approximations, no frozen values, no synthetic data.

## Stage Position

Stage 8a — DISTRIBUTION (Publish)

---

## Inputs

| Artifact | Path / Pattern | Required |
|----------|---------------|----------|
| Replicator package | `Technical/ANU_REPLICATOR/` | Yes |
| series_registry.json | `Technical/series_registry.json` | Yes |
| Chopped CSVs | `Technical/ANU_REPLICATOR/data/final-data/chopped/` | Yes |
| Extenbooks | `Technical/ANU_REPLICATOR/data/final-data/extenbooks/` | Yes (for `data+pipeline+viz` and `full` profiles) |
| Per-series provenance docs | `Technical/docs/series/*_DPR.md`, `*_EPR.md`, `*_DECOMPOSITION.md` | Yes (for `full` profile) |
| .publish_ignore | `{project_root}/.publish_ignore` | No |
| Visualization app | `Technical/ShinyApp/` or `Technical/ANU_VIZ/` | No (for `data+pipeline+viz` profile) |

## Outputs

| Artifact | Path / Pattern | Format |
|----------|---------------|--------|
| Export directory | `Outputs/{Project}_Publish_v{VERSION}/` | Directory tree |
| README.md | `{export}/README.md` | Markdown |
| CITATION.cff | `{export}/CITATION.cff` | YAML |
| LICENSE | `{export}/LICENSE` | Text |
| MANIFEST.json | `{export}/MANIFEST.json` | JSON (file list with SHA-256) |
| .gitignore | `{export}/.gitignore` | Text |
| PUBLISH_AUDIT.json | `{export}/PUBLISH_AUDIT.json` (with `--json`) | JSON |

## Generator Scripts

This skill ships two executables alongside this SKILL.md:

**`audit.py`** — canonical implementation of `/anu-publish audit`. Walks the project tree, applies `.publish_ignore` exclusion rules, greps every remaining text file for internal references. Exit non-zero on findings. Runs BEFORE `package` so agents identify leaks early.

```bash
python audit.py                       # report findings (exit non-zero if any)
python audit.py --strict              # also fail on WARN-severity hits
python audit.py --report json         # machine-readable
python audit.py --project <path>      # audit a different project root
```

Scrub patterns (FAIL-severity): `D:/Arcanum`, `C:/Users`, `E:/Storage`, `/Council/`, `\bDruck\b`, `\bRobin/`, `\bandenick\b`. Scrub patterns (WARN-severity): `DEC-[A-Z0-9]+` (internal decision codes inherited from predecessors).

The `.publish_ignore` file at the project root excludes internal coordination artifacts (one fnmatch glob per line; trailing `/` marks directory subtrees). Default excludes typically include `MIGRATION/`, internal plan docs, and runtime JSON files.

**`generate_publish_package.py`** — canonical implementation of `/anu-publish package` and `/anu-publish validate`. Assembles the export, scrubs it, writes the manifest, runs the pre-publication gate in one pass.

```bash
python generate_publish_package.py <project_root> \
    [--profile data-only|data+pipeline|data+pipeline+viz|full|web] \
    [--version X.Y.Z] [--json]
```

It reads `{project}/Technical/series_registry.json` for `drive_config` metadata (project name, author, institution, license, original work, repo URL) and writes a clean GitHub export to `{project}/Outputs/{Project}_Publish_v{VERSION}/` (replacing any existing directory at that version). The `web` profile writes to `{project}/Outputs/{Project}_Web_v{VERSION}/` instead.

## Publication Profiles

| Profile | Includes | Use Case |
|---------|----------|----------|
| `data-only` | Final data (chopped CSVs, extenbooks), registry, docs, README, CITATION.cff, LICENSE, MANIFEST.json | Researchers who want the data |
| `data+pipeline` *(default)* | Above + replicator code: `loading/`, `processing/`, `lib/`, `config/`, `validation/`, `replicate.py`, `requirements.txt` | Researchers who want to reproduce |
| `data+pipeline+viz` | Above + the visualization app under `visualization/` | Full interactive experience |
| `full` | Above + per-series provenance docs (`docs/series/*_DPR.md`, `*_EPR.md`, `*_DECOMPOSITION.md`) | Maximum transparency |
| `web` | **Not a superset** — the formal Anu→website export contract consumed by vizsite-family `build_cache.py`: publish-filtered `series_registry.json`, `chopped/` CSVs, `parquet/` per-series files, generated `data_dictionary.csv`, `docs/explainers/*_EXPLAINER.md`, scrubbed `docs/series/*_DPR.md`, `MIGRATION/crosswalk.csv` (if present), `WEB_MANIFEST.json` | Websites + the future Robin API (single source of truth for public naming and downloads) |

### The `web` profile contract

- **Publish-filtered**: series with `publish: false` (triage culls) are excluded from the registry copy, data files, and docs — enforced by gate P15.
- **Downloads contract is CSV + parquet** (`downloads_contract` in WEB_MANIFEST.json); JSON is not a public download format.
- **`data_dictionary.csv` is generated from the registry** (one row per series and subseries: `series_id, subseries_id, display_name, label, units, period_start, period_end, source, construction_type, license, notes`) — never hand-written, so naming is identical across site display, downloads, zips, and API (`ANU_NAMING_STANDARD.md`).
- **`WEB_MANIFEST.json`** carries series counts (total + by prefix) that the site's `build_cache.py` asserts against — replacing hardcoded expected-count constants.
- Requires `pandas` + `pyarrow` for the parquet conversion.

## Phase 1: Audit (`/anu-publish audit`)

Scan the project and produce an `AUDIT_REPORT.md`:

### 1A. Secret Detection
- Grep all files for patterns: API keys, tokens, passwords, `.env` files with real values
- Check: `config/api_keys.env` — must NOT be in the export, `api_keys.env.example` MUST exist
- Flag any hardcoded API keys in scripts (e.g., `FRED_API_KEY = "abc123"`)

### 1B. Path Sanitization
- Grep for absolute paths (`D:/`, `C:/`, `/home/`, `\\`)
- Grep for Arcanum-specific references: `Robin`, `freenic`, `Council/`, `Arcanum`
- Grep for personal identifiers: email addresses, usernames
- All `lib/paths.py` references should be relative (via `Path(__file__).resolve().parent`)

### 1C. Documentation Completeness
- README.md exists and has: Quick Start, Dependencies, Data Sources, License
- LICENSE file exists
- CITATION.cff exists (or will be generated)
- ASSUMPTIONS.md exists
- DECISION_LOG.md exists
- Per-series: decomposition + DPR for all series, EPR for all extended series

### 1D. Reproducibility Check
- `requirements.txt` lists all imports (cross-check against actual `import` statements)
- `python replicate.py --dry-run` succeeds
- All V## validation checks pass
- No `np.random` or synthetic data in any script

### 1E. Data Integrity
- No `data_unavailable` series shipped without documentation explaining why
- All chopped CSVs have valid metadata rows
- Hash integrity (V08) passes

## Phase 2: Package (`/anu-publish package`)

### 2A. Create Export Directory

```
{project_name}_export_{profile}_{date}/
```

### 2B. Copy Files per Profile

Based on selected profile, copy files from the internal project structure to the export directory. Apply scrubbing rules during copy:

| Source (Internal) | Destination (Export) | Scrub |
|-------------------|---------------------|-------|
| `Technical/ANU_REPLICATOR/` | Root of export | Remove `__pycache__/` |
| `config/api_keys.env` | EXCLUDED | Ship `api_keys.env.example` only |
| `data/raw-data/api/` | EXCLUDED | Regenerated by pipeline |
| All `.py` files | Same relative path | Scan for hardcoded paths/keys |

### 2C. Generate Publication Artifacts

If not already present, generate:
- **README.md** — from `PUBLICATION_README.template` + project metadata
- **LICENSE** — from `LICENSE.template` (default: MIT)
- **CITATION.cff** — from `CITATION.cff.template` + registry metadata
- **CHANGELOG.md** — from git log or PROGRESS_LOG.md
- **.gitignore** — standard exclusions

### 2D. Decouple from Arcanum

- Replace any remaining Arcanum path references with relative paths
- Remove `.claude/`, `.codex/`, `.cursor/` directories
- Remove HANDOFF_*.md files (internal workflow)
- Remove PROGRESS_LOG.md (replaced by CHANGELOG.md)

## Phase 3: Validate (`/anu-publish validate`)

Pre-publication gate — the `generate_publish_package.py` generator runs checks **P01-P15**. FAIL-severity checks must all pass; WARN-severity checks should be reviewed before release. The generator exits non-zero on any FAIL.

| Check | Severity | Description |
|-------|----------|-------------|
| P01_README_EXISTS | FAIL | README.md present at export root |
| P02_LICENSE_EXISTS | FAIL | LICENSE file present |
| P03_CITATION_PARSEABLE | FAIL | CITATION.cff present with `cff-version`, `title`, `authors` keys |
| P04_MANIFEST_VALID | FAIL | MANIFEST.json present and valid JSON |
| P05_DATA_PRESENT | FAIL | `data/` contains at least one CSV (`web`: `chopped/` CSVs + `parquet/` files) |
| P06_CODEBOOK_PRESENT | WARN | `data/codebook.csv` present (non-web profiles; `web` uses P13) |
| P07_ENTRY_POINT | FAIL (pipeline profiles) | `replicate.py` runnable entry point present |
| P08_REQUIREMENTS | FAIL (pipeline profiles) | `requirements.txt` present |
| P09_NO_SECRETS | FAIL | No API keys, tokens, or passwords in any text file |
| P10_NO_ABSOLUTE_PATHS | **FAIL** (v2.1; was WARN) | No `D:/`, `C:/`, `/home/`, `/Users/`, or UNC paths — workspace paths shipped to the public web while this was WARN |
| P11_NO_ARCANUM_REFS | **FAIL** (v2.1; was WARN) | No references to Arcanum, Council/Druck, freenic, Robin, andenick |
| P12_NO_BUILD_ARTIFACTS | FAIL | No `__pycache__/`, internal staging dirs (`inputs_bundled/`, `SalvagedInputs/`), or `api_keys.env`/`.env` leaked into the export |
| P13_DICTIONARY_PRESENT | FAIL (`web`) | `data_dictionary.csv` present — mandatory for every public dataset per `ANU_NAMING_STANDARD.md` |
| P14_UNITS_DECLARED | FAIL | Every published series + subseries declares units; `mixed_*` unit strings banned (declare per-subseries units — `UNITS_VALIDATION_STANDARD.md`) |
| P15_NO_UNPUBLISHED_SERIES | FAIL (`web`) | No `publish: false` series data files in the web export |

Deeper checks that require executing the pipeline — `DRY_RUN_PASSES` (`python replicate.py --dry-run` exits 0), `VALIDATION_PASSES` (all V## checks pass), `REQUIREMENTS_COMPLETE` (imports cross-checked against `requirements.txt`), and `NO_SYNTHETIC_DATA` (no `np.random` or placeholders) — are run by the `/anu-publish audit` phase, not the static package gate.

Output: console summary + `PUBLISH_AUDIT.json` (with `--json`) carrying PASS/WARN/FAIL per check.

## Templates

### CITATION.cff Template

```yaml
cff-version: 1.2.0
message: "If you use this data, please cite it as below."
title: "{project_title}"
version: "{version}"
date-released: "{date}"
authors:
  - family-names: "{author_last}"
    given-names: "{author_first}"
    orcid: "{orcid}"
    affiliation: "{institution}"
repository-code: "{repo_url}"
license: MIT
keywords:
  - economics
  - data-replication
  - reproducible-research
references:
  - type: book
    authors:
      - family-names: "{original_author_last}"
        given-names: "{original_author_first}"
    title: "{original_title}"
    year: "{original_year}"
    publisher:
      name: "{publisher}"
```

### Publication README Structure

```markdown
# {Project Title}

{One paragraph description}

## Quick Start

1. Clone: `git clone {repo_url}`
2. Install: `pip install -r requirements.txt`
3. API Keys: `cp config/api_keys.env.example config/api_keys.env`
4. Run: `python replicate.py`

## API Keys (Free Registration)

| API | Register | Required For |
|-----|----------|-------------|
| ... | ... | ... |

## Data Sources

| Source | Series | URL |
|--------|--------|-----|
| ... | ... | ... |

## Series Coverage

| Chapter | Series | Extended |
|---------|--------|----------|
| ... | ... | ... |

## Methodology

{Brief description of the replication approach}

## Citation

{BibTeX and plain text citation}

## License

{License text}
```

## Commands

| Command | Purpose |
|---------|---------|
| `/anu-publish audit [project]` | Scan project for publication readiness — flag secrets, internal paths, missing docs |
| `/anu-publish package [project] [profile]` | Generate a clean export directory in the selected profile |
| `/anu-publish validate [export_dir]` | Run pre-publication gate checks on an export |

## Acceptance Gates

| Gate | Criteria | Effect |
|------|----------|--------|
| PUBLISH-READY | All P01-P12 FAIL-severity checks pass, audit.py returns 0 | Package is ready for `git init` + push |
| WARN-CLEAN | All FAIL checks pass, all WARN checks also pass | Package is pristine — no caveats |
| NOT READY | Any FAIL-severity check fails | Package must not be published; fix blocking issues first |

## Documentation Cascade Writes

| Cascade File | Trigger | Content Written |
|-------------|---------|-----------------|
| `STEP_LOG.jsonl` | Every action (audit, package, validate) | `{action, project, profile, timestamp, gate_result, check_results}` |
| `NARRATIVE.md` | Every action | Human-readable summary of audit findings, scrub hits, and validation results |
| `ANU_LEDGER.json` | Stage 8a completion | Patch: `publish_coverage` updated; package marked as shipped with profile and version |
| `PIPELINE_STATE.json` | Package/validate completion | `stage_8a_publish` block updated with gate result, profile, version, artifact path |

## Integration with Anu Framework

| Skill | Relationship | Artifact Flow |
|-------|-------------|---------------|
| **Anu Replicator** (Stage 5) | Upstream — produces the package that anu-publish exports | `ANU_REPLICATOR/` → export root |
| **Anu Chopped** (Stage 6a) | Upstream — chopped CSVs included in all profiles | Chopped CSVs → `data/` in export |
| **Anu Review** | Quality gate — review score should be >= 85% before publishing | Review score → publish prerequisite |
| **Anu Ledger** | Coverage tracker — artifact coverage should be complete before publishing | Ledger → completeness check |
| **Anu Drive** (Stage 8b) | Sibling channel — Drive targets scholars, Publish targets developers | Independent outputs from same upstream |
| **Anu Archive** (Stage 8c) | Sibling channel — Archive mirrors the Publish repo into its `code/` directory | Publish export → Archive `code/` |
| **Anu Build** | Orchestrator — Publication is Stage 8a | Stage gate checked; `PIPELINE_STATE.json` updated |

### Pipeline Context

- **Pipeline Stage**: 8a (DISTRIBUTION — Publish)
- **Upstream**: Stage 5 Replicator, Stage 6 Chopped + Extenbook, Stage 7 Visualize (optional)
- **Downstream**: Stage 8c Archive (mirrors Publish into `code/`)
- **Prerequisite**: anu-review score should be >= 85% before publishing

## Anti-Patterns

| # | DO NOT | Consequence |
|---|--------|-------------|
| 1 | Ship `api_keys.env` or `.env` files with real values | Secret leak; always ship `.env.example` only |
| 2 | Leave absolute paths (`D:/Arcanum`, `C:/Users/...`) in exported code | Breaks on any other machine; use `pathlib` relative resolution |
| 3 | Include `__pycache__/`, `.git/`, `.claude/`, `.codex/` in the export | Bloat and internal artifacts; the generator excludes these automatically |
| 4 | Claim >80% completion without a passing P01-P12 gate | The gate is the objective measure; subjective estimates are unreliable |
| 5 | Skip the audit phase and go straight to packaging | Audit catches secrets and internal references before they reach the export |
| 6 | Include synthetic or placeholder data in the export | Every value must trace to a published source; `data_unavailable` series are excluded, not faked |
| 7 | Include HANDOFF_*.md or PROGRESS_LOG.md in the export | Internal workflow artifacts; replace with CHANGELOG.md |

## Robin Integration

Published manifests MUST pin the Robin version at construction time. Before packaging, run `python robin_loader.py validate <project>` — fail the pre-publication gate if any drift is detected.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-13 | Initial release — scrub rules, four packaging profiles, pre-publication validation gate, CITATION.cff and README templates |
| 1.1 | 2026-05-14 | Added the `generate_publish_package.py` executable generator; renumbered the validation gate as P01-P12 to mirror the generator's static checks |
| 1.2 | 2026-05-15 | Added `audit.py` as canonical pre-publication scrub implementation; formalized `.publish_ignore` exclusion manifest with documented FAIL/WARN scrub pattern set. Friction-Point-4 absorbed from RMWND build experience. |
| 2.0 | 2026-05-16 | Rewritten to Anu Framework v12.0 common template. Added Stage Position (Stage 8a — DISTRIBUTION Publish), machine-listed Inputs/Outputs tables, Acceptance Gates, Documentation Cascade Writes (STEP_LOG + NARRATIVE + LEDGER), Anti-Patterns table. All substantive content preserved including audit phases, packaging profiles, P01-P12 gate, and templates. |
| 2.1 | 2026-06-10 | Scrub hardening + the web export contract. **P10 (absolute paths) and P11 (Arcanum refs) promoted WARN→FAIL** (workspace paths had shipped to the public web under WARN). audit.py FAIL patterns extended (C:/Users, E:/Storage, andenick). P12 now also rejects internal staging dirs (`inputs_bundled/`, `SalvagedInputs/`). New **`web` packaging profile** — publish-filtered registry + chopped CSV + parquet + generated `data_dictionary.csv` + explainers + scrubbed DPRs + `WEB_MANIFEST.json` (downloads contract: CSV + parquet only). New gates: P13 DICTIONARY_PRESENT (web), P14 UNITS_DECLARED (no `mixed_*` units), P15 NO_UNPUBLISHED_SERIES (web). |

---

## Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v12.0 — Publication Pipeline*
