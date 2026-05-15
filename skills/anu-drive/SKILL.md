---
name: anu-drive
version: "1.1"
description: "Consumer-facing Google Drive distribution package. Generates a shareable folder with master data file (all final series), individual Extenbooks, LaTeX-compiled methodology PDF with clickable per-series documentation, and plain-text README. Designed for non-technical scholars who need constructed data without GitHub or command-line access."
when-to-use: "User wants to share constructed data with a scholar via Google Drive, create a consumer-friendly data package, generate a methodology PDF documenting all series, or produce a single shareable folder from Anu Framework outputs"
search-hints: "drive share google folder package consumer scholar distribution methodology pdf extenbook"
argument-hint: "[generate|validate|update] [project_path]"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: anu-replicator, anu-chopped, anu-extenbook
part-of: Anu Framework v11.0
---

# Anu Drive Standard v1.1

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Drive |
| Version | 1.1 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-12 |
| Updated | 2026-05-14 — added the `generate_drive_package.py` generator script |
| Purpose | Generate a self-contained, consumer-facing data distribution folder for sharing via Google Drive |

---

## Generator script

This skill ships an executable generator at `generate_drive_package.py`
(alongside this SKILL.md). It is the canonical implementation of the
`/anu-drive generate` command.

```bash
python generate_drive_package.py <project_root> [--version X.Y]
```

It reads `{project}/Technical/series_registry.json`, pulls every
`*_final.csv` from `{project}/Technical/ANU_REPLICATOR/data/final-data/series/`
and every `*_extenbook.xlsx` from `.../extenbooks/`, and writes a complete
package to `{project}/Outputs/{PROJECT}_Drive_v{VERSION}/`:

- master CSV + XLSX (time-series content only — cross-sectional series are
  excluded from the year-indexed sheet but still ship as workbooks)
- 16-column codebook CSV
- per-series Excel workbooks under `Series/`, renamed to descriptive
  snake_case
- the newest methodology PDF found in `Technical/` or a prior Drive package
- `README.txt` and `CITATION.txt` rendered from `drive_config`
- the `README_codebook_columns.md` and `README_per_series_excel_format.md`
  explainer files carried forward from the prior package

It is **idempotent** — re-running on an unchanged registry produces an
identical package. It prints a currency note listing any registry series
that lack a final CSV and were therefore not shipped.

---

## Purpose

Generate a **single shareable folder** that a non-technical scholar can open in Google Drive and immediately understand, browse, and use all constructed data — without touching a command line, cloning a repo, or installing any software.

### The Distribution Gap

| Channel | Audience | Barrier |
|---------|----------|---------|
| GitHub Replication Package (anu-publish) | Technical researchers | Requires Git, Python, API keys |
| Consumer Website (anu-visualize) | General public | Requires deployment infrastructure |
| **Google Drive Package (anu-drive)** | **Scholars, collaborators, reviewers** | **None — just open the folder** |

Anu Drive fills the middle ground: richer than a data dump, simpler than a replication package.

### Sibling channels

Anu Drive is **Stage 8b** — one of three sibling distribution channels. Anu Publish (8a) targets developers on GitHub; Anu Archive (8c) bundles the comprehensive audit-grade package for reviewers and Zenodo. A project may ship any subset; `anu-archive` mirrors this Drive package into its `data/` directory. See `anu-pipeline/SKILL.md` for the Stage 8a/8b/8c map.

### Design Principles

1. **Zero-setup**: A scholar receives a Google Drive link and can start working immediately
2. **Self-documenting**: The methodology PDF explains every series without external references
3. **Machine-readable**: The master CSV can be imported into R, Python, Stata, or Excel with one command
4. **Explorable**: Curious scholars can drill into individual Extenbooks to see full construction
5. **Programmatic**: Everything is generated from `series_registry.json` — no manual assembly
6. **Scrubbed**: No API keys, no absolute paths, no internal Arcanum references

---

## Folder Structure

```
{ProjectName}_Drive_v{VERSION}/
│
├── README.txt                                        # Plain-text guide (NOT markdown)
├── CITATION.txt                                      # How to cite this data (formatted + BibTeX)
├── {ProjectName}_All_Series_v{VERSION}.xlsx          # Master data workbook
├── {ProjectName}_All_Series_v{VERSION}.csv           # Machine-readable duplicate of Sheet 1
├── {ProjectName}_Codebook_v{VERSION}.csv             # Formal data dictionary (one row per series)
├── {ProjectName}_Methodology_v{VERSION}.pdf          # LaTeX-compiled methodology document
│
├── Series/                                           # Individual Extenbooks (one per series)
│   ├── S001_{descriptor}.xlsx
│   ├── S002_{descriptor}.xlsx
│   ├── S003_{descriptor}.xlsx
│   └── ...
│
└── Supplementary/                                    # (optional) Non-time-series data
    ├── {descriptor}_cross_section.xlsx
    ├── {descriptor}_io_table.xlsx
    └── ...
```

### Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| Root folder | `{ProjectName}_Drive_v{VERSION}` | `MyProject_Drive_v1.0` |
| Master workbook | `{ProjectName}_All_Series_v{VERSION}.xlsx` | `CD2_All_Series_v1.0.xlsx` |
| Master CSV | `{ProjectName}_All_Series_v{VERSION}.csv` | `CD2_All_Series_v1.0.csv` |
| Codebook | `{ProjectName}_Codebook_v{VERSION}.csv` | `CD2_Codebook_v1.0.csv` |
| Methodology PDF | `{ProjectName}_Methodology_v{VERSION}.pdf` | `CD2_Methodology_v1.0.pdf` |
| Citation file | `CITATION.txt` (fixed name) | `CITATION.txt` |
| Extenbook file | `S{NNN}_{snake_case_name}.xlsx` | `S001_industrial_production.xlsx` |
| Supplementary file | `{snake_case_descriptor}.xlsx` | `input_output_table_1947.xlsx` |

**Snake-case conversion rule**: Take the series `name` field from `series_registry.json`, lowercase it, replace spaces and hyphens with underscores, strip parentheses and special characters, truncate to 50 characters. Examples:

| Registry Name | Filename |
|--------------|----------|
| US Industrial Production Index | `S001_us_industrial_production_index.xlsx` |
| Corporate Rate of Profit (r) | `S013_corporate_rate_of_profit.xlsx` |
| Wage Share of Net Value Added | `S026_wage_share_of_net_value_added.xlsx` |

### Version Numbering

The Drive package version is set explicitly by the user or read from the project configuration:

| Source | Priority | Example |
|--------|----------|---------|
| CLI argument `--version X.Y` | 1 (highest) | `--version 2.1` |
| `series_registry.json` field `"drive_version"` | 2 | `"drive_version": "1.0"` |
| Date-based fallback | 3 (lowest) | `2026-05-12` |

Increment the version whenever the underlying data changes (new `replicate.py` run, series added/removed, corrections applied).

---

## Component 1: Master Data File

The master data file is the entry point for scholars who want to **use the data immediately** without understanding the construction process.

### Sheet 1: All Time Series

This is the "one sheet with everything" — a consumer-facing Chopped format containing only final series values.

**Structure**:

| Row | Content | Description |
|-----|---------|-------------|
| **Row 1** | Human-readable series names | e.g., "US Industrial Production Index (1860-2025)" |
| **Row 2** | Series IDs | e.g., `S001`, `S002`, `S003` |
| **Row 3** | Units | e.g., "Index 1958=100", "Percent", "Billions USD" |
| **Row 4+** | Data | Year in Column A, series values in subsequent columns |

**Column layout** (left to right):

```
Year | S001 | S002 | S003 | ... | S0NN
```

**What to include**: Only the FINAL constructed series — no subseries (`S001-A`), no intermediates (`S001-EXT`), no concurrent components (`CS001-N`). The user sees clean, ready-to-use data.

**What to exclude**: Series with `"status": "data_unavailable"` in the registry.

**Column ordering**: By series ID (S001, S002, S003, ...) which typically corresponds to chapter order in the source work.

**Formatting**:

| Element | Format |
|---------|--------|
| Row 1 (names) | Bold, #4472C4 background, white text, text wrap |
| Row 2 (IDs) | Bold, #D9E2F3 background |
| Row 3 (units) | Italic, #F2F2F2 background |
| Year column | Integer format (no commas, no decimals) |
| Data cells | Number format matching units (2 decimal places for indices/rates, 0 for integers, 1 for percentages) |
| Empty cells | Leave blank (no "N/A", no ".", no 0) |
| Freeze panes | Freeze at Row 4, Column B (headers + year always visible) |
| Column width | Auto-fit to content, minimum 12 |

### Sheet 2+: Non-Time-Series Data (Optional)

For data that cannot be represented as Year x Series columns:

| Content Type | Sheet Treatment |
|-------------|-----------------|
| Input-output matrices | One sheet per matrix, named by year: "IO Table 1947" |
| Cross-sectional data | One sheet per cross-section: "Industry Profit Rates 1997" |
| Country panels | One sheet per variable with country columns |
| Theoretical calculations | One sheet per derivation |

Each additional sheet follows the same formatting conventions (Row 1 = descriptors, Row 2 = IDs, Row 3 = units, Row 4+ = data) adapted to the content structure.

### CSV Duplicate

The CSV file contains **only Sheet 1** (All Time Series) in standard Anu Chopped format:

- Row 1: Series names (metadata)
- Row 2: Series IDs (column headers)
- Row 3: Units
- Row 4+: Data

This allows direct import into R (`read.csv`), Python (`pd.read_csv`), or Stata (`import delimited`) with minimal configuration. The user skips Row 1 and Row 3 to get a clean header + data frame.

---

## Component 2: Series Library

The Series/ folder contains **one Extenbook per series**, allowing scholars to drill into the full construction of any individual series.

### What Goes In

Copy every Extenbook from the Replicator's output:

```
Source: Technical/ANU_REPLICATOR/data/final-data/extenbooks/S{NNN}_extenbook.xlsx
Destination: {Drive}/Series/S{NNN}_{descriptor}.xlsx
```

### Renaming Rule

| Source Filename | Drive Filename |
|-----------------|----------------|
| `S001_extenbook.xlsx` | `S001_industrial_production.xlsx` |
| `S013_extenbook.xlsx` | `S013_corporate_rate_of_profit.xlsx` |

The descriptor is derived from the registry's `name` field using the snake-case conversion rule above.

### What Scholars See

Each Extenbook retains its full 4-sheet structure:

| Sheet | What It Shows the Scholar |
|-------|---------------------------|
| **Data** | All subsource columns, transformations, and the final series — the full construction visible in one spreadsheet |
| **Provenance** | Where every data point came from — sources, APIs, quality ratings, citations |
| **Research** | Original author's quotes and methodology notes that guided the construction |
| **Construction** | Step-by-step build log: load → rebase → splice → extend |

### Scrubbing

Before copying, verify that no Extenbook contains:
- Absolute paths (D:/, C:/, /home/)
- API keys or tokens
- Internal Arcanum references (Robin, Council, freenic)

The Provenance sheet's "References" section (Rows 87-95) may contain internal paths — these should be stripped or replaced with relative references within the Drive package.

---

## Component 3: Methodology PDF

The methodology PDF is the intellectual heart of the Drive package. It provides a **complete, hyperlinked documentation** of every series so that a scholar can click from the Table of Contents to any series and understand exactly what it measures, where the data came from, and how it was constructed.

### Document Structure

```
METHODOLOGY PDF
├── Title Page
├── Abstract / Introduction                    (1-2 pages)
├── Table of Contents                          (clickable hyperlinks)
├── Chapter 1: Data Overview                   (2-4 pages)
│   ├── 1.1 Project Description
│   ├── 1.2 Source Work
│   ├── 1.3 Coverage Summary
│   └── 1.4 Series Summary Table
├── Chapter 2: Series Documentation            (2-4 pages per series)
│   ├── S001 — {Name}
│   │   ├── Definition & Purpose
│   │   ├── Source Data
│   │   ├── Construction Process
│   │   ├── Extension (if applicable)
│   │   └── Output Summary
│   ├── S002 — {Name}
│   │   └── ...
│   └── S0NN — {Name}
│       └── ...
├── Appendix A: Data Sources                   (2-5 pages)
├── Appendix B: File Manifest                  (1-2 pages)
├── Appendix C: Using This Data                (2-3 pages)
│   ├── C.1 Opening in Excel / Google Sheets
│   ├── C.2 Importing into R
│   ├── C.3 Importing into Python
│   ├── C.4 Importing into Stata
│   └── C.5 Understanding the Extenbooks
└── Appendix D: Version History                (1 page)
```

### Title Page

```latex
\begin{titlepage}
\centering
{\Huge\bfseries {PROJECT TITLE} \\[0.5cm]}
{\Large Data Documentation \& Methodology \\[1cm]}
{\large Version {VERSION} \\[0.3cm]}
{\large {DATE} \\[2cm]}
{\Large {AUTHOR(S)} \\[0.3cm]}
{\large {INSTITUTION} \\[0.5cm]}
{\normalsize {EMAIL} \\[3cm]}
{\normalsize Based on: \emph{{ORIGINAL WORK TITLE}} \\
by {ORIGINAL AUTHOR} ({ORIGINAL YEAR}) \\[0.5cm]}
{\normalsize {PUBLISHER}}
\end{titlepage}
```

### Abstract / Introduction

One to two pages covering:

1. **What this is**: "This package contains [N] constructed economic data series covering [YEAR_START] to [YEAR_END]..."
2. **What original work**: "The data replicates and extends the empirical appendices of [Author]'s [Title] ([Year])..."
3. **What data sources**: "Original data is drawn from [Source1], [Source2], ... and extended to the present using [API1], [API2]..."
4. **What the goal is**: "The purpose is to make [Author]'s empirical work reproducible and extensible..."
5. **How to use this package**: Brief pointer to the three components (master file, series folder, this PDF)

### Chapter 1: Data Overview

**Section 1.1 — Project Description**: 1-2 paragraphs on the project's purpose and scope.

**Section 1.2 — Source Work**: Citation and brief description of the original work being replicated.

**Section 1.3 — Coverage Summary**: Table summarizing temporal and geographic scope:

| Dimension | Value |
|-----------|-------|
| Time Coverage | {YEAR_START} – {YEAR_END} |
| Geographic Scope | {SCOPE} |
| Total Series | {N_SERIES} |
| Extended to Present | {N_EXTENDED} of {N_SERIES} |
| Data Sources | {N_SOURCES} unique sources |
| API Extensions | {API_LIST} |

**Section 1.4 — Series Summary Table**: A master reference table (auto-generated from registry):

| ID | Name | Chapter | Period | Units | Extended | Source |
|----|------|---------|--------|-------|----------|--------|
| S001 | Industrial Production | 2 | 1860-2025 | Index 1958=100 | Yes (FRED) | BEA, FRB |
| S002 | Real GDP | 2 | 1929-2025 | Billions 2017$ | Yes (BEA) | BEA NIPA |
| ... | ... | ... | ... | ... | ... | ... |

This table is the entry point. A scholar reads this, identifies the series they need (say S065), clicks the hyperlink, and jumps directly to that series' documentation section.

### Chapter 2: Series Documentation (Per-Series Sections)

Each series gets its own `\section` with a standardized five-part structure. **Every section is auto-generated from `series_registry.json`** — no manual writing.

#### 2.X.1 — Definition & Purpose

```latex
\subsection{Definition \& Purpose}
\textbf{{SERIES_NAME}} measures {DEFINITION}.

{THEORETICAL_CONTEXT — from S###_research.json, one or two key author quotes
explaining why this series matters to the argument.}
```

Source fields: `name`, `description` from registry; `quotes` from `S###_research.json`.

#### 2.X.2 — Source Data

A table of all input subsources:

| Subsource | Source | Period | Units | Quality |
|-----------|--------|--------|-------|---------|
| S001-A | BEA Long-Term Economic Growth Table A15 | 1860-1959 | Index | Official Statistics |
| S001-B | FRB G.17 Industrial Production | 1919-2010 | Index | Official Statistics |
| S001-C | FRED INDPRO | 2011-2025 | Index 2017=100 | Official Statistics |

Source fields: `subseries` array from registry — each entry's `source`, `period`, `units`, `quality`.

#### 2.X.3 — Construction Process

Numbered steps derived from the registry's `construction` array:

> 1. **Load** S001-A from BEA LTEG Table A15 (1860-1959)
> 2. **Load** S001-B from FRB G.17 (1919-2010)
> 3. **Reindex** S001-A to base year 1958 = 100, producing S001-A-R
> 4. **Splice** S001-A-R and S001-B at 1919 using growth rate method, producing S001-BASE
> 5. **Extend** S001-BASE with FRED INDPRO from 2011, splice at 2010 using growth rate method

Each step maps to one entry in the `construction` array:
- `load` → "**Load** {id} from {source} ({period})"
- `reindex` → "**Reindex** {input} to base year {base_year} = {base_value}, producing {output}"
- `reindex_to_match` → "**Reindex** {input} to match {match_to} at {at_year}, producing {output}"
- `splice` → "**Splice** {inputs} at {at_year} using {method} method, producing {output}"
- `calculate` → "**Calculate** {output} = {formula}"
- `ratio` → "**Compute ratio** {output} = {numerator} / {denominator}"

#### 2.X.4 — Extension (Conditional)

Only included if the series has an `extension` block in the registry:

> **Extension Source**: FRED INDPRO (Federal Reserve Economic Data, Industrial Production Index)
> **Splice Year**: 2010
> **Splice Method**: Growth rate
> **Modern Coverage**: 2011-2025
> **Registration**: Free at https://fred.stlouisfed.org/

If no extension: this subsection is replaced with a single line: "*This series uses only historical data and has not been extended.*"

#### 2.X.5 — Output Summary

| Property | Value |
|----------|-------|
| Final Series ID | S001 |
| Period | 1860-2025 |
| Units | Index 1958=100 |
| Observations | 166 |
| Master File Column | Column B |
| Extenbook File | `Series/S001_industrial_production.xlsx` |

### Appendix A: Data Sources

Complete bibliography of all unique data sources used across all series, sorted alphabetically:

> **Bureau of Economic Analysis (BEA)**
> - NIPA Tables: https://www.bea.gov/data/national-accounts
> - Long-Term Economic Growth: [Citation]
> - Used in: S001, S002, S015, S026
>
> **Bureau of Labor Statistics (BLS)**
> - Current Employment Statistics: https://www.bls.gov/ces/
> - Used in: S003, S045
>
> **Federal Reserve Economic Data (FRED)**
> - Registration: https://fred.stlouisfed.org/ (free)
> - Series used: INDPRO (S001), GDP (S002), ...

### Appendix B: File Manifest

Complete listing of every file in the Drive package:

| File | Description | Size |
|------|-------------|------|
| `README.txt` | Package guide | — |
| `{Project}_All_Series_v{V}.xlsx` | All {N} final series in one workbook | — |
| `{Project}_All_Series_v{V}.csv` | Machine-readable CSV of time series | — |
| `{Project}_Methodology_v{V}.pdf` | This document | — |
| `Series/S001_{name}.xlsx` | {Series Name} — 4-sheet Extenbook | — |
| `Series/S002_{name}.xlsx` | {Series Name} — 4-sheet Extenbook | — |
| ... | ... | ... |

### Appendix C: Using This Data

Practical import instructions for common platforms:

**C.1 — Excel / Google Sheets**: Open `{Project}_All_Series.xlsx` directly. Row 1 = series names, Row 2 = series IDs, Row 3 = units, Row 4+ = data. Filter or copy columns as needed.

**C.2 — R**:
```r
library(readr)
data <- read_csv("{Project}_All_Series_v{V}.csv", skip = 2)
# skip = 2 skips the name and unit rows; Row 2 (IDs) becomes headers
```

**C.3 — Python**:
```python
import pandas as pd
data = pd.read_csv("{Project}_All_Series_v{V}.csv", header=1, skiprows=[2])
# header=1 uses Row 2 (IDs) as column names; skiprows=[2] skips units row
```

**C.4 — Stata**:
```stata
import delimited "{Project}_All_Series_v{V}.csv", rowrange(4:) varnames(2) clear
```

**C.5 — Understanding the Extenbooks**: Each file in `Series/` is an Excel workbook with four sheets. The Data sheet shows all raw inputs and transformations. The Provenance sheet documents sources. The Research sheet captures original author methodology. The Construction sheet logs the step-by-step build.

### Appendix D: Version History

| Version | Date | Changes |
|---------|------|---------|
| {VERSION} | {DATE} | {DESCRIPTION} |

---

## Component 4: README.txt

A plain-text file (NOT Markdown) that renders correctly in Google Drive preview, Notepad, and any text viewer.

### Template

```
================================================================
  {PROJECT TITLE}
  Data Package — Version {VERSION}
  {DATE}
================================================================

WHAT IS THIS?
-------------
This folder contains {N_SERIES} constructed economic data
series covering {YEAR_START} to {YEAR_END}, based on the
empirical work in:

  {ORIGINAL_AUTHOR}, "{ORIGINAL_TITLE}" ({ORIGINAL_YEAR})
  {PUBLISHER}

The data has been replicated from the original source
material and extended to the present using publicly
available government statistical APIs.


HOW TO USE THIS DATA
--------------------

  1. QUICK START — All data in one file:
     Open "{ProjectName}_All_Series_v{VERSION}.xlsx"
     Row 1 = Series names
     Row 2 = Series IDs (S001, S002, ...)
     Row 3 = Units
     Row 4+ = Data (Year in first column)

  2. DEEP DIVE — Construction of any series:
     Open the "Series/" folder.
     Each file is one data series showing every input,
     transformation, and the final constructed values.

  3. FULL METHODOLOGY:
     Open "{ProjectName}_Methodology_v{VERSION}.pdf"
     Clickable Table of Contents links to every series.

  4. PROGRAMMATIC USE (R, Python, Stata):
     Import "{ProjectName}_All_Series_v{VERSION}.csv"
     See Appendix C of the Methodology PDF for code.

  5. VARIABLE REFERENCE:
     Open "{ProjectName}_Codebook_v{VERSION}.csv"
     One row per series: ID, name, units, coverage, source.

  6. CITING THIS DATA:
     See CITATION.txt for formatted citation and BibTeX.


CONTENTS
--------
{ProjectName}_All_Series_v{VERSION}.xlsx   All series (Excel)
{ProjectName}_All_Series_v{VERSION}.csv    All series (CSV)
{ProjectName}_Codebook_v{VERSION}.csv      Data dictionary
{ProjectName}_Methodology_v{VERSION}.pdf   Full methodology
CITATION.txt                               How to cite this data
Series/                                    Individual series
  S001_{name}.xlsx                           {Series 1 Name}
  S002_{name}.xlsx                           {Series 2 Name}
  ...
README.txt                                 This file


CONTACT
-------
{AUTHOR_NAME}
{INSTITUTION}
{EMAIL}


LICENSE
-------
{LICENSE_TEXT}

================================================================
```

---

## Component 5: Citation File

A plain-text citation file so scholars know exactly how to credit the data in their own work. Includes both a human-readable formatted citation (for copy-paste into a paper) and a BibTeX entry (for LaTeX users).

### Why Plain Text

| Format | Problem for Non-Technical Scholars |
|--------|-----------------------------------|
| `.cff` (Citation File Format) | Requires YAML parsing; scholars won't know what to do with it |
| `.bib` (BibTeX only) | Only useful for LaTeX users |
| `.ris` (Reference Manager) | Requires Zotero/Mendeley import |
| **`.txt` (plain text)** | **Opens in any text editor, readable immediately, copy-paste ready** |

### File Structure

CITATION.txt contains three blocks separated by dividers:

1. **Formatted citation** (APA-style) — copy-paste into a manuscript
2. **BibTeX entry** — copy-paste into a .bib file
3. **Original work citation** — credit the source being replicated

### Template

```
================================================================
  HOW TO CITE THIS DATA
================================================================

If you use this data in your research, please cite:

  {AUTHOR_LAST}, {AUTHOR_FIRST}. ({YEAR}).
  {PROJECT_TITLE} [Data set], Version {VERSION}.
  {INSTITUTION}.
  Based on: {ORIGINAL_AUTHOR}, "{ORIGINAL_TITLE}"
  ({ORIGINAL_YEAR}). {PUBLISHER}.


BIBTEX
------
@misc{{CITATION_KEY},
  author       = {{{AUTHOR_LAST}, {AUTHOR_FIRST}}},
  title        = {{{PROJECT_TITLE}}},
  year         = {{{YEAR}}},
  version      = {{{VERSION}}},
  note         = {{Data set. Based on {ORIGINAL_AUTHOR},
                  ``{ORIGINAL_TITLE}'' ({ORIGINAL_YEAR})}},
  institution  = {{{INSTITUTION}}},
  url          = {{{REPO_URL}}}
}


ORIGINAL WORK
-------------
This data replicates and extends the empirical content of:

  {ORIGINAL_AUTHOR}. ({ORIGINAL_YEAR}).
  {ORIGINAL_TITLE}.
  {PUBLISHER}.

Please also cite the original work when using this data.


================================================================
  {PROJECT_TITLE} -- Version {VERSION}
  Generated {DATE}
================================================================
```

### Field Mapping from Registry

| Template Field | Registry Source |
|---------------|----------------|
| `{AUTHOR_LAST}` | `series_registry.json` → `author.last_name` |
| `{AUTHOR_FIRST}` | `series_registry.json` → `author.first_name` |
| `{YEAR}` | Generation year (current year) |
| `{PROJECT_TITLE}` | `series_registry.json` → `project_title` |
| `{VERSION}` | Drive package version |
| `{INSTITUTION}` | `series_registry.json` → `institution` |
| `{ORIGINAL_AUTHOR}` | `series_registry.json` → `original_work.author` |
| `{ORIGINAL_TITLE}` | `series_registry.json` → `original_work.title` |
| `{ORIGINAL_YEAR}` | `series_registry.json` → `original_work.year` |
| `{PUBLISHER}` | `series_registry.json` → `original_work.publisher` |
| `{CITATION_KEY}` | Auto-generated: `{author_last}{year}_{project_slug}` (e.g., `beshara2026_cd2`) |
| `{REPO_URL}` | `series_registry.json` → `repo_url` (blank if unpublished) |

---

## Component 6: Codebook

A formal data dictionary in CSV format — one row per series — documenting every variable the scholar receives. This is standard practice in academic data sharing and what a journal data editor would expect alongside any dataset submission.

### Why CSV

The codebook is data-about-data. It should be machine-readable, importable into any tool, and inspectable without specialized software. CSV is the universal standard for codebooks in social science.

### What It Documents

The codebook describes the **final series** that the scholar receives in the master data file — not the internal subseries or construction intermediates. If a scholar opens the master Excel file and sees column `S013`, they can look up `S013` in the codebook to learn exactly what it is.

### Column Specification

| # | Column | Type | Description | Registry Source |
|---|--------|------|-------------|-----------------|
| 1 | `series_id` | string | Series identifier | Key in `series` dict (e.g., `S001`) |
| 2 | `name` | string | Human-readable series name | `series[id].name` |
| 3 | `definition` | string | What this series measures | `series[id].description` |
| 4 | `units` | string | Unit of measurement | `series[id].units` (e.g., "Index 1958=100", "Percent", "Billions USD") |
| 5 | `frequency` | string | Temporal frequency | `series[id].frequency` (typically "annual") |
| 6 | `coverage_start` | integer | First year of data | Min year with non-null value |
| 7 | `coverage_end` | integer | Last year of data | Max year with non-null value |
| 8 | `n_observations` | integer | Count of non-null values | Computed from data |
| 9 | `content_type` | string | Data classification | `series[id].content_type` (time_series, cross_sectional, etc.) |
| 10 | `chapter` | integer | Chapter in source work | `series[id].chapter` |
| 11 | `figures` | string | Figures replicated | `series[id].figures` (comma-separated, e.g., "Fig6.1, Fig6.3") |
| 12 | `source_primary` | string | Main historical data source | First subseries' `source` field |
| 13 | `source_extension` | string | API used for extension | `series[id].extension.api` + `series[id].extension.api_series_id` (e.g., "FRED INDPRO") or blank |
| 14 | `extended` | string | Whether extended to present | "Yes" if extension block exists, "No" otherwise |
| 15 | `splice_year` | integer/blank | Year where extension begins | `series[id].extension.splice_year` or blank |
| 16 | `notes` | string | Caveats, special handling | `series[id].notes` or blank |

### Format Rules

| Property | Value |
|----------|-------|
| Encoding | UTF-8 with BOM (for Excel auto-detection) |
| Delimiter | Comma |
| Quoting | Double-quote fields containing commas, quotes, or newlines |
| Header row | Column names exactly as specified above |
| Sort order | By `series_id` ascending (S001, S002, ...) |
| Empty values | Leave blank (no "N/A", no "NULL") |
| Line endings | CRLF (Windows compatibility) |

### Example

```csv
series_id,name,definition,units,frequency,coverage_start,coverage_end,n_observations,content_type,chapter,figures,source_primary,source_extension,extended,splice_year,notes
S001,US Industrial Production Index,Index of industrial output for the United States,Index 1958=100,annual,1860,2025,166,time_series,2,"Fig2.1",BEA Long-Term Economic Growth Table A15,FRED INDPRO,Yes,2010,
S002,Real GDP,Real gross domestic product,Billions 2017 USD,annual,1929,2025,97,time_series,2,"Fig2.3",BEA NIPA Table 1.1.6,BEA API,Yes,2022,
S013,Corporate Rate of Profit,Net operating surplus divided by net capital stock,Rate (decimal),annual,1929,2025,97,time_series,6,"Fig6.1, Fig6.3",BEA NIPA / BEA Fixed Assets,,No,,Computed as ratio NOS/K
```

### What NOT to Include

| Excluded Content | Reason |
|-----------------|--------|
| Subseries (S001-A, S001-B) | Internal construction detail — scholar only sees final series |
| Construction steps | Documented in methodology PDF and Extenbooks |
| API keys or URLs | Security — documented in methodology PDF Appendix A |
| Internal file paths | Scrubbing rule — no Arcanum references |

---

## Generation Process

### Prerequisites

Before generating a Drive package, verify:

1. `series_registry.json` exists and is populated
2. `replicate.py` has been run successfully (all L## and P## complete)
3. Extenbooks exist in `data/final-data/extenbooks/`
4. Chopped CSVs exist in `data/final-data/chopped/`
5. Validation (V##) has passed
6. `tectonic` is available for LaTeX compilation (at `tools/tectonic.exe`)

### Step-by-Step Generation

#### Step 1: Read Configuration

```python
# Read series_registry.json
registry = json.load(open("config/series_registry.json"))

# Determine project metadata
project_name = registry.get("project_name", "Project")
version = registry.get("drive_version", datetime.now().strftime("%Y-%m-%d"))
author = registry.get("author", "")
institution = registry.get("institution", "")
original_work = registry.get("original_work", {})
```

#### Step 2: Create Folder Structure

```python
drive_dir = f"Outputs/{project_name}_Drive_v{version}"
os.makedirs(f"{drive_dir}/Series", exist_ok=True)
os.makedirs(f"{drive_dir}/Supplementary", exist_ok=True)  # only if needed
```

**Output location**: The Drive folder is generated inside the project's `Outputs/` directory (standard).

#### Step 3: Generate Master Data File

```python
# Collect all final series
series_list = []
for sid, sconfig in registry["series"].items():
    if sconfig.get("status") == "data_unavailable":
        continue
    if sconfig.get("content_type") == "time_series":
        series_list.append(sid)

# Sort by series ID
series_list.sort()

# Build DataFrame: Year x final series values
# Read each series' final column from its Chopped CSV or final-data output
# Write to Sheet 1 of the Excel workbook
# Add Row 1 (names), Row 2 (IDs), Row 3 (units) as header rows
```

For non-time-series content (matrices, cross-sections):
```python
# Classify by content_type
cross_sectional = [s for s in registry["series"] if s["content_type"] == "cross_sectional"]
# Each gets its own sheet in the master workbook
```

#### Step 4: Copy and Rename Extenbooks

```python
for sid in series_list:
    src = f"data/final-data/extenbooks/{sid}_extenbook.xlsx"
    descriptor = snake_case(registry["series"][sid]["name"])
    dst = f"{drive_dir}/Series/{sid}_{descriptor}.xlsx"
    shutil.copy2(src, dst)
    # Scrub: verify no absolute paths or API keys in the file
```

#### Step 5: Generate LaTeX Methodology Document

```python
# Use the DRIVE_METHODOLOGY_TEMPLATE.tex as base
# For each series, generate a \section with:
#   - Definition from registry name + description
#   - Subsource table from registry subseries
#   - Construction steps from registry construction array
#   - Extension details from registry extension block
#   - Output summary

# Write to {drive_dir}/methodology.tex
```

#### Step 6: Compile PDF

```bash
# Using tectonic (available at tools/tectonic.exe)
tectonic methodology.tex -o {drive_dir}/
# Rename output
mv {drive_dir}/methodology.pdf {drive_dir}/{ProjectName}_Methodology_v{VERSION}.pdf
# Clean up .tex source (do NOT include in Drive folder)
rm {drive_dir}/methodology.tex
```

The .tex source file is NOT included in the Drive package — only the compiled PDF. The LaTeX source stays in `Technical/` for reproducibility.

#### Step 7: Generate CSV

```python
# Export Sheet 1 of the master workbook as CSV
# Encoding: UTF-8 with BOM (for Excel compatibility)
# Line endings: CRLF (for Windows compatibility)
```

#### Step 8: Generate README.txt

```python
# Fill the README template with project metadata
# List all files in the package (including CITATION.txt and CODEBOOK.csv)
# Write as plain ASCII text (no Unicode beyond basic Latin)
```

#### Step 9: Generate CITATION.txt

```python
# Fill the DRIVE_CITATION_TEMPLATE.txt with registry metadata
# Fields: author, project_title, version, institution, original_work.*
# Generate citation_key: "{author_last}{year}_{project_slug}"
# Write as plain ASCII text
```

#### Step 10: Generate CODEBOOK.csv

```python
# For each series in registry where status != "data_unavailable":
#   Read series metadata from registry
#   Compute coverage_start, coverage_end, n_observations from actual data
#   Derive source_primary from first subseries
#   Derive source_extension from extension block (if present)
#   Derive extended = "Yes"/"No" from extension block presence
# Sort by series_id ascending
# Write CSV with UTF-8 BOM encoding, CRLF line endings
# Header row uses exact column names from codebook specification
```

#### Step 11: Validate

Run all validation rules (see Validation section below).

#### Step 12: Remove Build Artifacts

```python
# Remove: .tex source, .aux, .log, .toc, .out files
# Remove: Supplementary/ folder if empty
# Final folder should contain ONLY the deliverables
```

---

## LaTeX Generation Rules

### Per-Series Section Generation

The LaTeX generator reads `series_registry.json` and produces one `\section` per series. The mapping from registry fields to LaTeX content:

#### Construction Step Rendering

| Registry Step Type | LaTeX Rendering |
|-------------------|-----------------|
| `load` | "**Load** {subseries_id} from {source_name} ({period_start}–{period_end})" |
| `reindex` | "**Reindex** {input} to base year {base_year} = {base_value}, producing {output}" |
| `reindex_to_match` | "**Reindex** {input} to match {match_to} at year {at_year}, producing {output}" |
| `splice` | "**Splice** {input_1} and {input_2} at {at_year} using {method} method, producing {output}" |
| `calculate` | "**Calculate** {output} using formula: ${formula}$" |
| `ratio` | "**Compute** {output} = {numerator} ÷ {denominator}" |
| `rescale` | "**Rescale** {input} by factor {factor}, producing {output}" |

#### Subsource Table Generation

For each series, generate a `tabular` environment with columns: Subsource ID, Source Name, Period, Units, Data Quality.

#### Extension Block Generation

If `extension` exists in the registry entry:
```latex
\paragraph{Extension to Present}
\begin{description}
  \item[Source] {api} — {api_series_id}
  \item[Splice Year] {splice_year}
  \item[Method] {method}
  \item[Modern Coverage] {splice_year+1}–{current_year}
  \item[Registration] Free at {api_url}
\end{description}
```

### LaTeX Packages Required

```latex
\usepackage[margin=1in]{geometry}        % Page margins
\usepackage[hidelinks]{hyperref}         % Clickable TOC and cross-references
\usepackage{booktabs}                    % Professional tables
\usepackage{longtable}                   % Multi-page tables
\usepackage{fancyhdr}                    % Headers/footers
\usepackage{titlesec}                    % Section formatting
\usepackage{enumitem}                    % List formatting
\usepackage{xcolor}                      % Color support
\usepackage{bookmark}                    % PDF bookmarks
\usepackage[T1]{fontenc}                 % Font encoding
\usepackage{lmodern}                     % Modern fonts
```

### PDF Features

| Feature | Implementation |
|---------|---------------|
| Clickable TOC | `\hyperref` + `\tableofcontents` |
| PDF bookmarks | `\bookmark` package — sidebar navigation in PDF viewers |
| Section links from summary table | `\hyperref[sec:S001]{S001}` links to `\label{sec:S001}` |
| Page numbers | Bottom center via `\fancyhf` |
| Header | "{Project Name} — Methodology" on left, "v{VERSION}" on right |

---

## Validation Rules

| Rule | ID | Description | Severity |
|------|----|-------------|----------|
| Folder structure | D01 | Root contains README.txt, CITATION.txt, CODEBOOK .csv, master .xlsx, master .csv, methodology .pdf, Series/ | FAIL |
| Master file completeness | D02 | Every series with `status != "data_unavailable"` and `content_type == "time_series"` is present in master file Sheet 1 | FAIL |
| Series library completeness | D03 | Every series in the master file has a corresponding Extenbook in Series/ | FAIL |
| Naming convention | D04 | All files follow the naming patterns defined above | WARN |
| Methodology PDF integrity | D05 | PDF opens, has TOC, has one section per series, has all four appendices | FAIL |
| README accuracy | D06 | README file listing matches actual folder contents | WARN |
| No secrets | D07 | No API keys, tokens, or passwords in any file (grep for common patterns) | FAIL |
| No absolute paths | D08 | No `D:/`, `C:/`, `/home/`, `\\` paths in any text file | FAIL |
| No Arcanum references | D09 | No "Robin", "Council", "Arcanum", "freenic" in any file | FAIL |
| CSV/XLSX consistency | D10 | CSV and XLSX Sheet 1 contain identical data (value-level check) | FAIL |
| Year formatting | D11 | Year column contains integers only (no 2,013.00 formatting) | FAIL |
| No empty series | D12 | No series column in the master file is entirely blank | WARN |
| Extenbook sheet count | D13 | Every Extenbook in Series/ has exactly 4 sheets | WARN |
| PDF page count | D14 | Methodology PDF has at least (N_series * 2 + 10) pages (sanity check) | WARN |
| Supplementary cleanup | D15 | Supplementary/ folder is absent if empty | WARN |
| Citation file | D16 | CITATION.txt exists, contains a formatted citation block and a BibTeX `@misc{` entry | FAIL |
| Codebook completeness | D17 | CODEBOOK CSV has exactly 16 columns with correct headers, one row per series in the master file, no series missing | FAIL |

### Running Validation

```bash
/anu-drive validate {drive_folder_path}
```

Output: `DRIVE_VALIDATION_REPORT.md` with PASS/WARN/FAIL per rule.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/anu-drive generate [project_path]` | Generate a complete Drive package from project outputs |
| `/anu-drive validate [drive_folder]` | Validate an existing Drive package against all rules |
| `/anu-drive update [drive_folder]` | Regenerate specific components (master file, PDF, or README) |
| `/anu-drive manifest [project_path]` | Preview what would be generated without creating files |

### Generate Options

| Flag | Description | Default |
|------|-------------|---------|
| `--version X.Y` | Set package version | From registry or date |
| `--no-csv` | Skip CSV generation (Excel only) | Include CSV |
| `--no-supplementary` | Skip non-time-series data | Include all |
| `--series S001,S002` | Generate for specific series only | All series |
| `--draft` | Skip PDF compilation (placeholder PDF) | Full compilation |

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Replicator** | Source of all constructed data and Extenbooks |
| **Anu Chopped** | Master CSV follows Chopped format conventions (adapted for consumer use) |
| **Anu Extenbook** | Individual series files are Extenbooks with standardized renaming |
| **Anu Publish** | Sibling distribution channel — anu-publish targets GitHub, anu-drive targets Google Drive |
| **Anu Review** | Drive package should only be generated after review score >= 85% |
| **Anu Ledger** | Drive generation is a ledger event — track what was shipped and when |
| **Anu Research** | research.json entries populate the methodology PDF's theoretical context |

### Pipeline Position

```
Stage 5: [Anu Replicator]  ──→  data/final-data/
    │
    ├──→ Stage 6: [Anu Chopped]     ──→  Validated CSVs
    ├──→ Stage 6: [Anu Extenbook]   ──→  4-sheet workbooks
    │
    ├──→ Stage 7: [Anu Visualize]   ──→  Interactive app
    │
    ├──→ Stage 8a: [Anu Publish]    ──→  GitHub release
    └──→ Stage 8b: [Anu Drive]      ──→  Google Drive folder   ← NEW
```

**Prerequisites**: Stages 5 + 6 must be complete (Replicator run, Chopped validated, Extenbooks generated).
**Recommended**: Anu Review score >= 85% before generating a Drive package for external sharing.

---

## Scrubbing Protocol

Before any Drive package is shared externally, the following must be verified:

### Automatic Scrubbing (during generation)

1. **Path sanitization**: Replace all absolute paths with relative references or remove entirely
2. **API key removal**: Strip any API keys found in Extenbook Provenance sheets
3. **Internal reference removal**: Remove references to internal organizational platforms, infrastructure directories, or project-specific tooling that won't exist for the recipient
4. **Agent references**: Remove Claude Code / agent workflow references from any metadata

### Manual Review Checklist

- [ ] Open each Extenbook Provenance sheet — verify no internal paths in References section
- [ ] Open master Excel — verify no hidden sheets, no comments with internal info
- [ ] Open methodology PDF — verify no internal tool references
- [ ] Open README.txt — verify contact info is correct and intended for external sharing

---

## Anu Framework Context

- **Pipeline Stage**: 8b (Distribution — Google Drive)
- **Upstream**: Stage 5 Replicator, Stage 6 Chopped + Extenbook
- **Downstream**: None (terminal output — the scholar receives this)
- **Adequacy Relevance**: N/A (all adequacy checks happen upstream)
- **Key Handoff**: The Drive folder IS the handoff — it leaves Arcanum and goes to the recipient

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Do This Instead |
|-------------|----------------|-----------------|
| Including raw API data | Clutters the package, may contain API keys | Only include final constructed series |
| Including .tex source | Non-technical users can't use LaTeX | Compile to PDF, keep .tex in Technical/ |
| Including Python scripts | This isn't a replication package | Use anu-publish for that channel |
| Manual Extenbook creation | Diverges from registry, will be stale | Always generate from Replicator output |
| Markdown README | Renders as plain text in many viewers | Use .txt with ASCII formatting |
| Version "latest" or no version | Recipients can't track which data they have | Always version explicitly |
| Including `data_unavailable` series | Confusing empty columns | Exclude entirely, note in methodology |
| Including agent handoff docs | Internal workflow artifacts | Strip all HANDOFF_*.md files |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-12 | Initial release — folder structure, master file spec, series library, methodology PDF, README template, validation rules, generation process, LaTeX specification |
| 1.1 | 2026-05-14 | Shipped `generate_drive_package.py` — canonical generator. Master XLSX has a single sheet ("All Time Series") holding time-series and derived series only; cross-sectional / theoretical / panel-indexed series are excluded from the master and ship only as individual per-series workbooks in `Series/`. Master CSV mirrors that sheet. Validation rules are advisory in v1.1; FAIL/WARN enforcement is on the v1.2 roadmap. |
| 1.1.1 | 2026-05-15 | Generator robustness: (a) falls back to `Technical/chopped/` + `Technical/extenbooks/` if the canonical `Technical/ANU_REPLICATOR/data/final-data/` layout is absent; (b) accepts `{SID}.csv` filenames if `{SID}_final.csv` glob is empty; (c) auto-detects Chopped 3-row CSV format vs standard 1-row header; (d) synthesizes a `drive_config` block from top-level registry fields (`author`, `original_work`, `book`) if absent, with `CC-BY-4.0` license default; (e) `registry["drive_config"]` is updated in-memory so downstream README/CITATION helpers see the synthesized values. Validated against the Shaikh-Tonak (RMWND) project layout. |

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `{ProjectName}_Drive_v{VERSION}/` folder in `Outputs/` |
| **Expects** | `series_registry.json`, Extenbooks in `data/final-data/extenbooks/`, Chopped CSVs, completed Replicator run |
| **Must Update on Completion** | Regenerate Ledger (`/anu-ledger generate`) to record Drive package as shipped artifact |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v11.0 — Consumer Distribution Package*
*v1.0 — May 2026*
