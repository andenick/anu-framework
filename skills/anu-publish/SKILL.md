---
name: anu-publish
version: "1.2"
description: "Publication pipeline that transforms internal Anu Framework projects into clean, publishable artifacts. Handles scrubbing (API keys, internal paths, framework-internal references via .publish_ignore), packaging (data-only, data+pipeline, data+pipeline+viz), validation (pre-publication gate), and formatting (README, CITATION.cff, LICENSE). Ships generate_publish_package.py and audit.py."
when-to-use: "User wants to prepare a data project for public release, scrub sensitive data from a repo, validate a package for publication, or generate publication artifacts (CITATION.cff, LICENSE)"
search-hints: "publish release package scrub validate public repo github export citation license audit publish-ignore"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[audit|package|validate] [project] [profile]"
requires: anu-replicator, anu-chopped
part-of: Anu Framework v11.0
---

# Anu Publish Standard v1.2

Transform an internal Anu Framework project into a clean, publishable artifact. Handles the full lifecycle from audit through export.

## Generator scripts

This skill ships two executables alongside this SKILL.md:

**`audit.py`** — canonical implementation of `/anu-publish audit`. Walks the project tree, applies `.publish_ignore` exclusion rules, greps every remaining text file for internal references. Exit non-zero on findings. Runs BEFORE `package` so agents identify leaks early.

```bash
python audit.py                       # report findings (exit non-zero if any)
python audit.py --strict              # also fail on WARN-severity hits
python audit.py --report json         # machine-readable
python audit.py --project <path>      # audit a different project root
```

Scrub patterns (FAIL-severity): `D:/Arcanum`, `/Council/`, `\bDruck\b`, `\bRobin/`. Scrub patterns (WARN-severity): `DEC-[A-Z0-9]+` (internal decision codes inherited from predecessors).

The `.publish_ignore` file at the project root excludes internal coordination artifacts (one fnmatch glob per line; trailing `/` marks directory subtrees). Default excludes typically include `MIGRATION/`, internal plan docs, and runtime JSON files.

**`generate_publish_package.py`** — canonical implementation of `/anu-publish package` and `/anu-publish validate`. Assembles the export, scrubs it, writes the manifest, runs the pre-publication gate in one pass.

```bash
python generate_publish_package.py <project_root> \
    [--profile data-only|data+pipeline|data+pipeline+viz|full] \
    [--version X.Y.Z] [--json]
```

It reads `{project}/Technical/series_registry.json` for `drive_config`
metadata (project name, author, institution, license, original work,
repo URL) and writes a clean GitHub export to
`{project}/Outputs/{Project}_Publish_v{VERSION}/` (replacing any existing
directory at that version).

**Profiles** — each is a superset of the previous one:

| Profile | Adds |
|---------|------|
| `data-only` | final-data CSVs + codebook + README + CITATION.cff + LICENSE + MANIFEST.json |
| `data+pipeline` *(default)* | + replicator code: `loading/`, `processing/`, `lib/`, `config/`, `validation/`, `replicate.py`, `requirements.txt` |
| `data+pipeline+viz` | + the visualization app under `visualization/` |
| `full` | + per-series provenance docs (`docs/series/*_DPR.md`, `*_EPR.md`, `*_DECOMPOSITION.md`) |

**What it does:**

- Copies the profile's artifacts, skipping `__pycache__/`, `.git/`,
  `.claude/`, `api_keys.env`, `.env`, and `PROGRESS_LOG.md`.
- Generates `README.md` (profile-accurate), `LICENSE` (project copy or a
  synthesized MIT license), `CITATION.cff` (project copy or rendered from
  `drive_config`), and a standard `.gitignore`.
- **Scrubs** every text file for secrets (API keys/tokens/passwords),
  absolute machine paths (`D:/`, `C:/`, `/home/`, `/Users/`, UNC), and
  internal Arcanum references — reporting every hit.
- Writes `MANIFEST.json` listing every file with size and SHA-256.
- Runs the **pre-publication gate P01-P12** (see Phase 3): required files,
  parseable CITATION.cff, valid MANIFEST, data present, runnable entry
  point, no secrets, no absolute paths, no Arcanum refs, no build
  artifacts. Secrets and missing required files are FAIL; absolute paths
  and Arcanum refs are WARN.
- With `--json`, writes `PUBLISH_AUDIT.json` with the full scrub +
  validation audit.
- Exits non-zero if any FAIL-severity check fails.

## Sibling channels

Anu Publish is **Stage 8a** — one of three sibling distribution channels that consume the same upstream outputs and serve different audiences:

| Channel | Skill | Audience | What ships |
|---|---|---|---|
| **Publish (this skill)** | `anu-publish` | Developers who `git clone` and run the pipeline | Scrubbed code + data + CI, GitHub-ready |
| Drive | `anu-drive` | Scholars who open files, never run code | Master workbook, codebook, methodology PDF, per-series workbooks |
| Archive | `anu-archive` | Auditors, journal data editors, Zenodo deposit | Everything: code + data + full provenance trail + manifest + checksums |

A project may ship any subset. `anu-archive` typically runs last, mirroring the Publish repo into its `code/` directory and the Drive package into its `data/` directory. See `anu-pipeline/SKILL.md` for the Stage 8a/8b/8c map.

## Core Principle

**Every published value must be reproducible.** A researcher who clones the exported repo, installs dependencies, provides their own (free) API keys, and runs the pipeline must get the same results. No internal tools, private databases, or Arcanum infrastructure should be required.

No placeholders, no approximations, no frozen values, no synthetic data. Every value traces to a published source or documented analytical method.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/anu-publish audit [project]` | Scan project for publication readiness — flag secrets, internal paths, missing docs |
| `/anu-publish package [project] [profile]` | Generate a clean export directory in the selected profile |
| `/anu-publish validate [export_dir]` | Run pre-publication gate checks on an export |

---

## Publication Profiles

| Profile | Includes | Use Case |
|---------|----------|----------|
| `data-only` | Final data (chopped CSVs, extenbooks), registry, docs, README | Researchers who want the data |
| `data+pipeline` | Above + scripts (L##/P##/V##/M##), lib/, orchestrator, requirements.txt | Researchers who want to reproduce |
| `data+pipeline+viz` | Above + visualization app (Dash or Shiny) | Full interactive experience |
| `full` | Above + KB extractions, research JSONs, exploration scripts | Maximum transparency |

---

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

---

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

---

## Phase 3: Validate (`/anu-publish validate`)

Pre-publication gate — the `generate_publish_package.py` generator runs
checks **P01-P12**. FAIL-severity checks must all pass; WARN-severity
checks should be reviewed before release. The generator exits non-zero on
any FAIL.

| Check | Severity | Description |
|-------|----------|-------------|
| P01_README_EXISTS | FAIL | README.md present at export root |
| P02_LICENSE_EXISTS | FAIL | LICENSE file present |
| P03_CITATION_PARSEABLE | FAIL | CITATION.cff present with `cff-version`, `title`, `authors` keys |
| P04_MANIFEST_VALID | FAIL | MANIFEST.json present and valid JSON |
| P05_DATA_PRESENT | FAIL | `data/` contains at least one CSV |
| P06_CODEBOOK_PRESENT | WARN | `data/codebook.csv` present |
| P07_ENTRY_POINT | FAIL (pipeline profiles) | `replicate.py` runnable entry point present |
| P08_REQUIREMENTS | FAIL (pipeline profiles) | `requirements.txt` present |
| P09_NO_SECRETS | FAIL | No API keys, tokens, or passwords in any text file |
| P10_NO_ABSOLUTE_PATHS | WARN | No `D:/`, `C:/`, `/home/`, `/Users/`, or UNC paths |
| P11_NO_ARCANUM_REFS | WARN | No references to Arcanum, Council/Druck, freenic, Robin |
| P12_NO_BUILD_ARTIFACTS | FAIL | No `__pycache__/` or `api_keys.env`/`.env` leaked into the export |

Deeper checks that require executing the pipeline — `DRY_RUN_PASSES`
(`python replicate.py --dry-run` exits 0), `VALIDATION_PASSES` (all V##
checks pass), `REQUIREMENTS_COMPLETE` (imports cross-checked against
`requirements.txt`), and `NO_SYNTHETIC_DATA` (no `np.random` or
placeholders) — are run by the `/anu-publish audit` phase, not the static
package gate.

Output: console summary + `PUBLISH_AUDIT.json` (with `--json`) carrying
PASS/WARN/FAIL per check.

---

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

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Replicator** | Produces the package that anu-publish exports |
| **Anu Review** | Quality audit should pass before publishing |
| **Anu Ledger** | Artifact coverage should be complete before publishing |
| **Anu Architecture** | Anu Architecture is the format standard the export follows |
| **Anu Pipeline** | Publication is the final stage after all construction is complete |

---

## Anu Framework Context

- **Pipeline Position**: Floating — can run at any stage, but typically runs after anu-review confirms quality
- **Prerequisite**: anu-review score should be >= 85% before publishing
- **Output**: Clean export directory ready for `git init` + push

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-13 | Initial release — scrub rules, four packaging profiles, pre-publication validation gate, CITATION.cff and README templates |
| 1.1 | 2026-05-14 | Added the `generate_publish_package.py` executable generator; renumbered the validation gate as P01-P12 to mirror the generator's static checks |
| 1.2 | 2026-05-15 | Added `audit.py` as canonical pre-publication scrub implementation; formalized `.publish_ignore` exclusion manifest with documented FAIL/WARN scrub pattern set. Friction-Point-4 absorbed from RMWND build experience. |

---

*Part of the Anu Framework v11.0 — Publication Pipeline*
*v1.2 — May 2026*
