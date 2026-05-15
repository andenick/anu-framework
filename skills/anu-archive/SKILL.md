---
name: anu-archive
version: "1.0"
description: "Audit-grade transparency package. Bundles the complete provenance trail of an Anu Framework project — code, data, per-series and per-figure provenance records, knowledge-base extractions, validation logs, decision log, ledger, review history, methodology, and glossary — into a single versioned archive with a machine-readable manifest and SHA-256 checksums, suitable for Zenodo deposit or comprehensive distribution to peer reviewers and journal data editors."
when-to-use: "User wants to produce a comprehensive, audit-grade replication archive; deposit a project on Zenodo for a citable DOI; give a peer reviewer or journal data editor everything needed to verify every value and every methodological decision; or create a future-proof snapshot of a completed data project"
search-hints: "archive zenodo deposit audit transparency provenance manifest checksum comprehensive replication package reviewer"
argument-hint: "[generate|validate] [project_path]"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: anu-replicator, anu-publish, anu-drive
part-of: Anu Framework v11.0
---

# Anu Archive Standard v1.0

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Archive |
| Version | 1.0 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-14 |
| Purpose | Bundle the complete, audit-grade provenance trail of a project into one versioned, checksummed archive |

---

## Purpose

Anu Archive is the **third external distribution channel** of the Anu Framework, and the one that carries the framework's mandate of *foolproof replication with unbelievable context and detail*.

### The three external channels

| Channel | Skill | Audience | Carries |
|---|---|---|---|
| GitHub replication repo | `anu-publish` | Researchers who `git clone` and run the pipeline | Lean: code + data + minimal docs + CI |
| Google Drive package | `anu-drive` | Scholars who open files, never run code | Friendly: master workbook + codebook + methodology PDF + per-series workbooks |
| **Comprehensive archive** | **`anu-archive`** | **Peer reviewers, journal data editors, replication auditors, future-proof archival** | **Everything: code + data + full provenance trail + validation + decisions + reviews + ledger + glossary** |

`anu-publish` keeps the public repo lean — loading every provenance record into it would bloat a `git clone && run` use case that does not need them. `anu-drive` keeps the consumer package friendly — a scholar should not have to wade through hundreds of markdown files. `anu-archive` is the deliberate home for the full trail: a single artifact from which an outside auditor can verify *every* claim and re-derive *every* value without ever reaching into the project's live internal workspace.

### Design principles

1. **Self-contained.** The archive resolves every reference internally. No path leads back to the internal workspace.
2. **Checksummed.** Every file has a SHA-256 entry in `CHECKSUMS.txt`; the `MANIFEST.json` is the machine-readable inventory.
3. **Categorized.** Every artifact is tagged by category (code, data, provenance, validation, decisions, reviews, methodology, reference) so an auditor can navigate by concern.
4. **Reproducible.** The archive contains the `anu-publish` code subset and the `anu-drive` data subset, so the pipeline can be re-run from inside the archive.
5. **Citable.** Designed for Zenodo deposit — the archive's `README.md` and `MANIFEST.json` carry the citation metadata a DOI registration needs.
6. **Unvarnished.** Unlike the public-facing channels, internal vocabulary is *preserved* inside provenance records. An auditor needs the real trail — including which knowledge-base extraction supported which decomposition decision. Scrubbing is limited to secrets and absolute machine paths only.

---

## Folder structure

```
{ProjectName}_Archive_v{VERSION}/
│
├── README.md                      # Archive entry point — what this is, how to navigate, how to cite
├── MANIFEST.json                  # Machine-readable inventory: every file with size, sha256, category, source
├── CHECKSUMS.txt                  # SHA-256 of every file (sha256sum -c compatible)
│
├── code/                          # Mirror of the anu-publish GitHub repo
│   └── ...                        #   replicate.py, lib/, loading/, processing/, validation/, config/, etc.
│
├── data/                          # Mirror of the anu-drive consumer package
│   ├── master/                    #   master XLSX + CSV + codebook
│   ├── series/                    #   per-series Excel workbooks
│   └── methodology.pdf            #   compiled methodology document
│
├── provenance/
│   ├── series/                    # Per-series DPR + EPR + decomposition (one set per series)
│   ├── figures/                   # Per-figure FPR
│   ├── knowledge_base/            # KB extractions — the source-text trail
│   └── registry.json              # The canonical series registry (single source of truth)
│
├── validation/                    # Full validation logs + per-run validation reports
│
├── decisions/                     # DECISION_LOG + ASSUMPTIONS — every methodological choice with rationale
│
├── reviews/                       # anu-review history — every quality audit conducted on the project
│
├── reference/
│   ├── ledger.json                # Anu Ledger snapshot — artifact-level coverage inventory
│   ├── glossary.md                # Project + framework glossary
│   └── pipeline_state.json        # Per-chapter pipeline stage status
│
└── (the archive is also distributed as {ProjectName}_Archive_v{VERSION}.zip)
```

---

## Inputs

The generator walks a project's `Technical/` tree and pulls:

| Archive location | Source in the project |
|---|---|
| `code/` | `Technical/reference-replicator/` (the `anu-publish` repo) — excluding `.git/`, `__pycache__/`, `data/cache/` |
| `data/master/`, `data/series/` | The most recent `Outputs/{Project}_Drive_v*/` package |
| `data/methodology.pdf` | The methodology PDF from the latest Drive package or `Technical/` |
| `provenance/series/` | `Technical/docs/series/*_DPR.md`, `*_EPR.md`, `*_DECOMPOSITION.md` |
| `provenance/figures/` | `Technical/docs/figures/*_FPR.md` |
| `provenance/knowledge_base/` | `Inputs/Robert/KB/*` (or the project's KB directory) |
| `provenance/registry.json` | `Technical/series_registry.json` |
| `validation/` | `Technical/ANU_REPLICATOR/data/final-data/logs/VALIDATION_LOG.json` + any validation reports |
| `decisions/` | `Technical/ANU_REPLICATOR/docs/DECISION_LOG.md`, `docs/ASSUMPTIONS.md` |
| `reviews/` | `Technical/Reviews/**` |
| `reference/ledger.json` | `Technical/ANU_LEDGER.json` |
| `reference/glossary.md` | `{Project}/GLOSSARY.md` (project-scoped) |
| `reference/pipeline_state.json` | `Technical/PIPELINE_STATE.json` |

---

## MANIFEST.json schema

```json
{
  "project": "the reference project",
  "archive_version": "1.0",
  "generated": "2026-05-14T00:00:00Z",
  "framework_version": "Anu Framework v11.0",
  "citation": {
    "title": "...",
    "authors": [{"family-names": "...", "given-names": "..."}],
    "original_work": {"author": "...", "title": "...", "year": 2016, "publisher": "..."},
    "license": "MIT (Code) + CC-BY-4.0 (Data)",
    "repository_code": "https://github.com/..."
  },
  "category_counts": {
    "code": 0, "data": 0, "provenance": 0, "validation": 0,
    "decisions": 0, "reviews": 0, "reference": 0
  },
  "file_count": 0,
  "total_bytes": 0,
  "files": [
    {
      "path": "provenance/series/S001_DPR.md",
      "size": 0,
      "sha256": "...",
      "category": "provenance",
      "source": "Technical/docs/series/S001_DPR.md"
    }
  ]
}
```

Every file in the archive (except `MANIFEST.json` and `CHECKSUMS.txt` themselves) has exactly one `files[]` entry. The `category` field is one of: `code`, `data`, `provenance`, `validation`, `decisions`, `reviews`, `reference`.

---

## Validation rules

`/anu-archive validate {archive_path}` checks:

| ID | Rule | Severity |
|---|---|---|
| A01 | `MANIFEST.json`, `CHECKSUMS.txt`, `README.md` present at root | FAIL |
| A02 | Every file on disk (except manifest/checksums) has a `MANIFEST.json` entry | FAIL |
| A03 | Every `MANIFEST.json` entry resolves to a file that exists on disk | FAIL |
| A04 | Every file's recomputed SHA-256 matches its `CHECKSUMS.txt` entry | FAIL |
| A05 | Every series in `provenance/registry.json` has a DPR in `provenance/series/` | FAIL |
| A06 | Every series with an `extension` block has an EPR in `provenance/series/` | FAIL |
| A07 | Every series in the registry has a decomposition in `provenance/series/` | WARN |
| A08 | Every figure referenced by any series has an FPR in `provenance/figures/` | WARN |
| A09 | No secrets — no API keys, tokens, or passwords in any text file | FAIL |
| A10 | No absolute machine paths (`D:/`, `C:/`, `/home/`, `\\`) in any text file | WARN |
| A11 | `code/` contains a runnable entry point (`replicate.py` or equivalent) | FAIL |
| A12 | `data/` contains the master workbook and at least one per-series workbook | FAIL |
| A13 | `reference/glossary.md` is present and non-empty | WARN |

A09 and A10 are the only scrubbing rules. Unlike `anu-publish`, internal vocabulary inside provenance records is **preserved** — an auditor needs the real trail.

---

## Generator script

This skill ships an executable generator at `generate_archive_package.py` (alongside this SKILL.md). It is the canonical implementation of `/anu-archive generate`.

```bash
python generate_archive_package.py <project_root> [--version X.Y] [--no-zip]
```

It walks the project tree per the Inputs table, copies each artifact into the right archive location, computes SHA-256 for every file, writes `MANIFEST.json` and `CHECKSUMS.txt`, renders `README.md` from the registry's `drive_config`, runs the A01–A13 validation rules, and (unless `--no-zip`) packages the result as `{ProjectName}_Archive_v{VERSION}.zip`. Output goes to `{project}/Outputs/{ProjectName}_Archive_v{VERSION}/`.

---

## Commands

| Command | Purpose |
|---|---|
| `/anu-archive generate [project_path]` | Build a complete archive package from project artifacts |
| `/anu-archive validate [archive_path]` | Run the A01–A13 validation rules against an existing archive |

---

## Integration with the Anu Framework

| Skill | Relationship |
|---|---|
| **anu-publish** | The archive's `code/` directory is a mirror of the `anu-publish` GitHub repo |
| **anu-drive** | The archive's `data/` directory is a mirror of the `anu-drive` consumer package |
| **anu-ingestion** | Source of the DPRs and decompositions bundled under `provenance/series/` |
| **anu-extension** | Source of the EPRs bundled under `provenance/series/` |
| **anu-review** | Source of the audit history bundled under `reviews/` |
| **anu-ledger** | Source of `reference/ledger.json` |

### Pipeline position

```
  Stage 8a: [Anu Publish]   -->  GitHub replication repo        [OPTIONAL]
  Stage 8b: [Anu Drive]     -->  Google Drive consumer package  [OPTIONAL]
  Stage 8c: [Anu Archive]   -->  Comprehensive audit archive    [OPTIONAL]  <- NEW
```

All three Stage-8 channels are siblings — they consume the same upstream outputs and serve different audiences. A project may ship any subset.

---

## Anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|---|---|---|
| Scrubbing internal vocabulary from provenance records | Auditors need the unvarnished trail | Preserve it; scrub only secrets and absolute paths |
| Omitting the validation logs | The archive must prove the data was checked | Always bundle `validation/` |
| Shipping without `CHECKSUMS.txt` | Future-proof archival requires integrity verification | Always compute and bundle checksums |
| Re-deriving artifacts instead of copying | The archive must reflect the project as-built | Copy from the canonical workspace verbatim |
| Including `.git/` or `__pycache__/` in `code/` | Bloat and irrelevant history | Exclude them in the generator |

---

## Documentation Contract

| Aspect | Detail |
|---|---|
| **Creates** | `{ProjectName}_Archive_v{VERSION}/` folder + `.zip` in `Outputs/` |
| **Expects** | A completed project: `series_registry.json`, an `anu-publish` repo, an `anu-drive` package, per-series provenance docs, validation logs, decision log, review history, ledger, glossary |
| **Must update on completion** | Regenerate the Anu Ledger to record the archive as a shipped artifact |

---

## Version History

- **v1.0** (May 2026) — Initial release. Defines the audit-grade transparency channel: bundles code, data, per-series and per-figure provenance records, knowledge-base extractions, validation logs, decision log, ledger, review history, methodology, and glossary into one versioned archive with a machine-readable `MANIFEST.json` and SHA-256 checksums. Ships `generate_archive_package.py`. Sibling to `anu-publish` (GitHub) and `anu-drive` (Drive).

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.
- [`DATA_PROVENANCE_STANDARDS.md`](../../docs/DATA_PROVENANCE_STANDARDS.md) — DPR / EPR / FPR / VPR record specs.

---

*Part of the Anu Framework v11.0 — Comprehensive Audit Archive.*
