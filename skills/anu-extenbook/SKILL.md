---
name: anu-extenbook
version: "3.2"
description: Human-readable Excel workbook format with 4 sheets (Data, Provenance, Research, Construction). Registry-driven with correct year formatting, reindex markers, and color coding. Use when generating or auditing Extenbook Excel files.
when-to-use: User needs to create or audit 4-sheet Excel workbooks with Data, Provenance, Research, and Construction sheets
search-hints: extenbook excel workbook sheets data provenance research construction
argument-hint: [action] [series_id]
allowed-tools: Read, Write, Grep, Glob, LS, Shell
requires: anu-ingestion, anu-research
part-of: Anu Framework v12.2
---

# Anu Extenbook Standard v3.2

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Extenbook |
| Version | 3.2 |
| Part Of | Anu Framework v12.2 |
| Created | 2026-01-30 |
| Updated | 2026-03-07 |
| Purpose | Generate series-level Excel workbooks showing complete data construction |

---

## Stage Position

**Stage 6b — OUTPUT** (human-readable workbook format; `anu-chopped` is Stage 6a, the machine-readable format).

This follows the canonical stage sequence in `anu-build/SKILL.md`. The "Anu Framework Context" block further down this file still carries the older stage numbering that predates that sequence; where the two disagree, the canonical sequence governs.

---

## Purpose

Generate **series-level Excel workbooks** that expose every subcomponent, transformation, and provenance detail of a data series. Each workbook is a complete, self-contained visualization of data construction.

### Key Differentiators

| Aspect | Previous Extenbooks | Anu Extenbooks |
|--------|---------------------|----------------|
| Unit | Chapter or Figure | **Series** |
| Data Content | Limited or none | **All subcomponents visible** |
| Transformations | Described in text | **Visible as columns** |
| Splice Points | Documented | **Visible in data rows** |
| Provenance | Separate files | **Integrated Sheet 2** |

---

## When to Use

Use the Anu Extenbook skill when:

- After completing DPR/EPR for a series
- During chapter review to visualize all subcomponents
- For quality assurance and validation of extended data
- To provide reviewers with transparent data construction
- Complementing Anu Visualize Standard with spreadsheet visualization

---

## Prerequisites

Before generating an Anu Extenbook:

1. **DPR Exists**: Data Provenance Record for the series (`S###_DPR.md`)
2. **EPR Exists** (if extended): Extension Provenance Record (`S###_EPR.md`)
3. **Subsource Data**: Absorbed data available
4. **Series Registry**: Entry in `series_registry.json`

---

## Inputs

Everything the Extenbook writer reads. All paths are relative to the project's `Technical/` root unless stated otherwise.

| Input | Path / pattern | Required |
|-------|----------------|----------|
| Series registry | `series_registry.json` (subseries, `color`, construction array, units/period/name) | Yes — canonical source for the Provenance and Construction sheets |
| Research JSON | `research/S###_research.json` | Yes — populates the Research sheet |
| DPR | `docs/series/S###_DPR.md` | Yes (prerequisite 1) |
| EPR | `docs/series/S###_EPR.md` | Only for extended series (prerequisite 2) |
| Subsource data | Absorbed / parsed subsource values for the series | Yes (prerequisite 3) |
| Chopped source CSV | `Inputs/[ChoppedSource]/ch##/` | Yes — the Data sheet mirrors it, and Workflow Step 4 validates against it |

---

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Extenbook workbook | `Technical/ANU_REPLICATOR/data/final-data/extenbooks/` | 4-sheet `.xlsx` (Data, Provenance, Research, Construction) |

The workbook is the skill's only artifact — there is no log, index, or state file. Note that this SKILL.md records two file-name forms for it: the File Naming Convention section specifies `Anu_Extenbook_S###.xlsx`, while the Output Location listing shows `S###_extenbook.xlsx`. Both forms appear in framework documentation; treat the directory, not the exact stem, as the contract, and match whichever form the project's Replicator already writes.

---

## Commands

This skill ships **no executable**. It is a format standard: the workbook itself is written by the Replicator's `extenbook_writer.py` during P## processing. What this SKILL.md prescribes are agent-invoked actions, which are the four Workflow steps below.

| Action | What it does |
|--------|--------------|
| Verify prerequisites | Workflow Step 1 — confirm DPR/EPR and the registry entry exist |
| Generate | Workflow Step 2 — regenerate via the project's Replicator: `cd Technical/ANU_REPLICATOR` then `python replicate.py --series S###` |
| Review output | Workflow Step 3 — open the workbook and check subsource columns, splice highlighting, and the Provenance sheet |
| Validate against original | Workflow Step 4 — compare against the Chopped source CSV |

The only other command this skill names is the absorption re-run in Troubleshooting (`python scripts/utils/absorb.py --chapter ##`), which also belongs to the project's Replicator package, not to this skill.

---

## Workflow

### Step 1: Verify Prerequisites

- Check `Technical/docs/series/S###_DPR.md` exists
- Check `Technical/docs/series/S###_EPR.md` exists (for extendable series)
- Verify series entry in `series_registry.json`

### Step 2: Generate Extenbook

Extenbooks are auto-generated by P## processing scripts via `extenbook_writer.py`. They can also be regenerated via:

```bash
cd Technical/ANU_REPLICATOR
python replicate.py --series S###
```

### Step 3: Review Output

Open generated file: `data/final-data/extenbooks/S###_extenbook.xlsx`

Verify:
- All subsources appear as separate columns
- Splice points highlighted
- Final series matches known values
- Provenance sheet is complete

### Step 4: Validate Against Original

Compare with Chopped CSV source in `Inputs/[ChoppedSource]/ch##/`

---

## Workbook Structure

### Sheet 1: Data

**Purpose**: Show all subcomponents and transformations laid out plain.

**Structure**:

| Row | Content |
|-----|---------|
| 0 | Metadata (column-specific source citations) |
| 1 | Headers (subsource IDs and descriptions) |
| 2+ | Data (year-indexed values) |

**Columns**:

| Column | Content | Color |
|--------|---------|-------|
| A | Year | White |
| B-N | Subsources (S###A, S###B, etc.) | Light Yellow (original) / Light Blue (extension) |
| O+ | Transformations (Rebased, Spliced) | Light Orange |
| Last | FINAL (extended series) | Light Green |

**Visual Indicators**:
- Splice years: Yellow row background
- Empty cells (NaN): Light gray
- Active ranges: Column-specific coloring

### Sheet 2: Provenance

**Purpose**: Complete DPR/EPR documentation in structured format.

**Sections**:

| Rows | Section | Content |
|------|---------|---------|
| 1-3 | Series Overview | ID, Title, Chapter, Figures, Period, Status |
| 5-12 | Theoretical Context | Author quotes, relevance |
| 14-25 | Subsources | Table with ID, Source, Period, API, Quality |
| 27-40 | Transformation Chain | Step, Operation, Formula, Input, Output |
| 42-55 | Extension Details | Sources, Splice Method, Transition Metrics |
| 57-65 | Validation | Range checks, correlations, test results |
| 67-75 | Certification | Faithfulness score, status, notes |
| 77-85 | Divergences | ADR entries affecting this series |
| 87-95 | References | DPR, EPR, data file locations |

---

## File Naming Convention

```
Anu_Extenbook_S###.xlsx
```

Examples:
- `Anu_Extenbook_S001.xlsx` - US Industrial Production Index
- `Anu_Extenbook_S013.xlsx` - US Corporate Rate of Profit
- `Anu_Extenbook_S047.xlsx` - Market Prices vs Direct Prices

---

## Output Location

Extenbooks are written to a flat directory inside the Replicator's final data output:

```
Technical/ANU_REPLICATOR/data/final-data/extenbooks/
├── S001_extenbook.xlsx
├── S002_extenbook.xlsx
├── S034_extenbook.xlsx
└── ...
```

---

## Color Coding Standard

| Element | Hex Color | Usage |
|---------|-----------|-------|
| Header Row | #4472C4 | Column headers (Row 1) |
| Metadata Row | #D9E2F3 | Row 0 metadata |
| Subsource Original | #FFF2CC | Author's original subsources |
| Subsource Extension | #E6F2FF | API extension data |
| Transformation | #FCE4D6 | Intermediate calculations |
| Final Series | #E6FFE6 | Final spliced series |
| Splice Row | #FFFF00 | Splice point highlight |
| NaN/Empty | #F2F2F2 | Inactive ranges |

---

## Integration with Anu Framework

| Component | Relationship |
|-----------|-------------|
| Anu Standard | Extenbook visualizes DPR documentation |
| Anu Extension Standard | Extenbook visualizes EPR methodology |
| Anu Review | Extenbook aids quality review |
| Anu Visualize Standard | Complements interactive visualization |

---

## Validation Checklist

For each generated Anu Extenbook:

- [ ] All subsources visible as separate columns
- [ ] Splice points clearly marked with yellow highlighting
- [ ] Final series matches known values from DPR/EPR
- [ ] Provenance sheet contains complete DPR/EPR information
- [ ] Color coding applied correctly per standard
- [ ] Links to source files accurate in references section
- [ ] Comparison with Chopped original validates accuracy

---

## Troubleshooting

### Missing Subsource Data

```
Error: Subsource S###A not found in absorbed database
```

**Solution**: Run absorption script for the chapter:
```bash
cd Technical/ANU_REPLICATOR
python scripts/utils/absorb.py --chapter ##
```

### DPR/EPR Not Found

```
Error: DPR file not found for S###
```

**Solution**: Create DPR first using Anu Ingestion skill.

### Splice Point Mismatch

If splice point values don't match between subsources:

1. Check transition analysis in EPR
2. Verify splice year is correct
3. Review rebasing methodology

---

## v2.0 Changes: 4-Sheet Structure

### Sheet Structure (v2.0)

| Sheet | Content | Source |
|-------|---------|--------|
| **Data** | Year column + all subseries columns with values | Chopped CSV data + registry metadata |
| **Provenance** | Source, period, units, transforms per subseries | `series_registry.json` fields |
| **Research** | One row per research entry: entry_id, type, location, quote, subseries | `S###_research.json` |
| **Construction** | Step-by-step construction from registry: step number, operation, inputs, outputs | `series_registry.json` construction array |

### Year Formatting Fix

Years MUST be formatted as integers (2013), not as decimals (2,013.00). The Extenbook writer enforces integer formatting on the Year column.

### Column Header Notation

For reindexed subseries, headers display: `S001-B [R:1958]` meaning "reindexed to 1958=100". Non-reindexed headers are plain: `S001-A`.

### Color Coding

Cell background colors match the `color` field from `series_registry.json` for each subseries. This ensures visual consistency between Extenbook and the Dash app.

### Registry-Driven Generation

The Extenbook writer (`lib/formats/extenbook_writer.py` in the Replicator) reads `series_registry.json` and `S###_research.json` to auto-generate all four sheets. No manual formatting required.

---

## Templates

Templates location: `skills/anu-extenbook/templates/`

- `EXTENBOOK_DATA_TEMPLATE.md` - Sheet 1 structure guide
- `EXTENBOOK_PROVENANCE_TEMPLATE.md` - Sheet 2 structure guide

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Ingestion** | Registry provides all metadata for Provenance and Construction sheets |
| **Anu Research** | research.json populates the Research sheet |
| **Anu Replicator** | P## scripts generate Extenbooks via `extenbook_writer.py` |
| **Anu Chopped** | Data sheet mirrors Chopped structure with Excel formatting |
| **Anu Review** | D9 Extenbook Quality dimension scores sheet structure and formatting |

---

## Acceptance Gates

A generated Extenbook is accepted when:

- [ ] All four prerequisites hold (DPR, EPR-if-extended, subsource data, registry entry)
- [ ] The workbook contains all four sheets: Data, Provenance, Research, Construction
- [ ] Every item in the Validation Checklist above passes
- [ ] The Year column is formatted as integers (`2013`, not `2,013.00`)
- [ ] Reindexed subseries headers carry the `[R:YYYY]` marker; non-reindexed headers are plain
- [ ] Cell background colors match the `color` field in `series_registry.json` and the Color Coding Standard above
- [ ] Workflow Step 4 comparison against the Chopped source CSV shows no value mismatch

There is no gate script; these are checked by the agent on generation and re-scored by `anu-review` dimension D9 (Extenbook Quality).

---

## Anti-Patterns

| # | DO NOT | Consequence |
|---|--------|-------------|
| 1 | Hand-edit a generated workbook to fix values or formatting | Generation is registry-driven; the next run silently overwrites the edit, and the workbook stops matching the registry |
| 2 | Fix a wrong value in the workbook instead of in `series_registry.json` | The registry is the canonical source; the Chopped CSV and the visualization app keep the wrong value |
| 3 | Generate an Extenbook before the DPR exists | The Provenance sheet has nothing to document; produces a shell that looks complete |
| 4 | Leave the Year column as decimals (`2,013.00`) | Years stop reading as years and break comparison against the Chopped source |
| 5 | Drop the `[R:YYYY]` marker from a reindexed subseries header | A reindexed column is indistinguishable from a raw one; readers mis-compare levels |
| 6 | Invent colors instead of using the registry `color` field and the Color Coding Standard | Breaks visual consistency between the Extenbook and the visualization app |
| 7 | Merge subsources into one column instead of showing each separately | Defeats the skill's whole purpose: every subcomponent must be visible |

---

## Anu Framework Context

- **Pipeline Stage**: 5 (OUTPUT — generation)
- **Upstream**: Stage 4 Replication, Anu Research (research JSONs), Anu Ingestion (DPRs)
- **Downstream**: Stage 6 Review (D9 Extenbook Quality)
- **Adequacy Relevance**: L1 (Source Text) — Extenbook Research sheet draws from KB sources validated by L1
- **Key Handoff**: Standalone deliverable; reviewed by Anu Review D9

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `Anu_Extenbook_S###.xlsx` (4-sheet workbook per series) |
| **Expects** | `S###_DPR.md`, `S###_research.json`, `series_registry.json` |
| **Must Update on Completion** | No additional updates — Extenbooks are auto-generated outputs |

**Note**: The canonical source for all series metadata is `series_registry.json`. Extenbook generation reads from the registry.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-30 | Initial release (2-sheet structure) |
| 2.0 | 2026-03-07 | 4-sheet structure (Research, Construction), year formatting fix, [R:YYYY] headers, registry-driven generation |
| 2.1 | 2026-03-08 | Removed legacy paths (DEFINITIVE_SERIES_CATALOG.json, create_anu_extenbooks.py, Outputs/Anu_Extenbooks/); updated to Replicator output paths; fixed troubleshooting references |
| 3.0 | 2026-03-15 | Generalized: removed project-specific hardcoding (Shaikh Absorbed, Shaikh Chopped, Shaikh quotes); replaced with generic terms |
| 3.2 | 2026-04-07 | Version bump for Anu Framework v6.0 compatibility (format unchanged) |

---

## Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — the formal `series_registry.json` schema.

---

*Part of the Anu Framework v12.2 — Human-Readable Data Workbook*
