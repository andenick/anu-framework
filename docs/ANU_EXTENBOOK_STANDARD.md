# Anu Extenbook Standard v1.0

## Series-Level Data Construction Visualization

---

## Overview

The Anu Extenbook Standard defines a rigorous framework for generating **series-level Excel workbooks** that expose every subcomponent, transformation, and provenance detail of a data series.

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Created | 2026-01-30 |
| Part Of | Anu Framework v10.0 |
| Complements | Anu Ingestion, Anu Extension, Anu Review, Anu Visualize |

> **Note**: This is a summary doc. The `anu-extenbook` skill is at v3.2 — see `SKILL_VERSION_MATRIX.md` and `anu-extenbook/SKILL.md` for the authoritative current spec. "Anu Standard" was superseded by `anu-ingestion`; "Anu Shiny" was superseded by `anu-visualize`.

---

## Purpose

An Anu Extenbook is a **complete, self-contained visualization** of data construction for a single data series. Unlike the previous extenbook formats (chapter-level or figure-level), Anu Extenbooks are:

1. **Series-Level**: One workbook per S### series
2. **Subcomponent-Visible**: Every subsource shown as a separate column
3. **Transformation-Transparent**: All calculations laid out plain
4. **Splice-Point-Highlighted**: Visual indicators at transition years
5. **Provenance-Integrated**: Complete DPR/EPR documentation in Sheet 2

---

## Workbook Structure

```
Anu_Extenbook_S###.xlsx
├── Sheet 1: "Data" - All subcomponents laid out plain
└── Sheet 2: "Provenance" - Complete DPR/EPR documentation
```

### Sheet 1: Data

**Purpose**: Show all raw data subcomponents and transformations in a format similar to Shaikh Chopped, but for ONE series only.

#### Row Structure

| Row | Content |
|-----|---------|
| 0 | Metadata Row - Column-specific source citations |
| 1 | Header Row - Subsource IDs and descriptions |
| 2+ | Data Rows - Year-indexed values |

#### Column Structure

| Column | Content | Color Code |
|--------|---------|------------|
| A | Year | White |
| B-N | Subsources (S###A, S###B, etc.) | Yellow (original) / Blue (extension) |
| O+ | Transformation columns (Rebased, Spliced) | Orange |
| Last | FINAL - Extended series | Green |

#### Example Layout

```
     A      B                      C                      D                      E
0  | Year | BEA LTEG Table A15    | FRB G.17             | FRED INDPRO          | FINAL: S001 Extended |
1  | Year | S001A: BEA (1860-1959)| S001B: FRB (1919-2010)| S001C: FRED (2011-2025)| S001_FINAL |
2  | 1860 | 2.3                   |                       |                       | 2.8        |
3  | 1861 | 2.5                   |                       |                       | 3.0        |
...
60 | 1919 | 15.2                  | 15.4                  |                       | 16.5       | <- Splice
...
151| 2010 |                       | 95.2                  | 95.3                  | 100.0      | <- Splice
152| 2011 |                       |                       | 96.1                  | 101.2      |
...
166| 2025 |                       |                       | 105.7                 | 111.2      |
```

#### Visual Indicators

| Indicator | Meaning |
|-----------|---------|
| Yellow row background | Splice year |
| Light yellow cells | Original Shaikh subsources |
| Light blue cells | API extension data |
| Light orange cells | Transformation columns |
| Light green cells | Final extended series |
| Gray cells | Out-of-range (NaN) |

### Sheet 2: Provenance

**Purpose**: Complete structured documentation extracted from DPR/EPR files.

#### Section Structure

| Section | Rows | Content |
|---------|------|---------|
| Series Overview | 1-4 | ID, Title, Chapter, Figures, Period, Status |
| Theoretical Context | 6-12 | Shaikh quotes, relevance, HDARP sources |
| Subsources | 14-25 | Table: ID, Source, Period, API, Quality |
| Transformation Chain | 27-40 | Table: Step, Operation, Formula, Input, Output |
| Extension Details | 42-55 | Sources, Splice Method, Transition Metrics |
| Faithfulness Certification | 57-65 | Component scores, Total, Status |
| Divergences | 67-75 | ADR entries affecting this series |
| References | 77-85 | File locations, generation timestamp |

---

## Color Coding Standard

| Element | Hex Color | RGB | Usage |
|---------|-----------|-----|-------|
| Header Row | #4472C4 | 68, 114, 196 | Column headers |
| Metadata Row | #D9E2F3 | 217, 226, 243 | Row 0 metadata |
| Subsource Original | #FFF2CC | 255, 242, 204 | Shaikh's subsources |
| Subsource Extension | #E6F2FF | 230, 242, 255 | API extension data |
| Transformation | #FCE4D6 | 252, 228, 214 | Intermediate calcs |
| Final Series | #E6FFE6 | 230, 255, 230 | Final output |
| Splice Row | #FFFF00 | 255, 255, 0 | Splice point highlight |
| NaN/Empty | #F2F2F2 | 242, 242, 242 | Inactive ranges |
| PASS | #E6FFE6 | 230, 255, 230 | Validation pass |
| FAIL | #FFE6E6 | 255, 230, 230 | Validation fail |

---

## File Naming Convention

```
Anu_Extenbook_S###.xlsx
```

**Examples**:
- `Anu_Extenbook_S001.xlsx` - US Industrial Production Index
- `Anu_Extenbook_S013.xlsx` - US Corporate Rate of Profit
- `Anu_Extenbook_S047.xlsx` - Market Prices vs Direct Prices

---

## Output Directory Structure

```
Projects/Capitalism Data/Outputs/Anu_Extenbooks/
├── Chapter_02/
│   ├── Anu_Extenbook_S001.xlsx
│   ├── Anu_Extenbook_S002.xlsx
│   └── ...
├── Chapter_09/
│   ├── Anu_Extenbook_S047.xlsx
│   └── ...
├── Chapter_16/
│   └── ...
└── SUMMARY/
    └── Anu_Extenbook_Master_Index.xlsx
```

---

## Prerequisites

Before generating an Anu Extenbook, ensure:

1. **DPR File Exists**: `docs/series/S###_DPR.md`
2. **EPR File Exists** (for extended series): `docs/series/S###_EPR.md`
3. **Subsource Catalog Entry**: In `catalogs/SERIES_SUBSOURCES.json`
4. **Series Catalog Entry**: In `catalogs/DEFINITIVE_SERIES_CATALOG.json`
5. **Shaikh Absorbed Data**: `data/ShaikhAbsorbed/chapter_##_data.csv`

---

## Generation Workflow

### Step 1: Verify Prerequisites

```bash
# Check DPR exists
ls docs/series/S###_DPR.md

# Check EPR exists (for extendable series)
ls docs/series/S###_EPR.md

# Verify subsource catalog entry
grep "S###" catalogs/SERIES_SUBSOURCES.json
```

### Step 2: Generate Extenbook

```bash
# Single series
python create_anu_extenbooks.py --series S001

# Entire chapter
python create_anu_extenbooks.py --chapter 2

# All chapters
python create_anu_extenbooks.py --all
```

### Step 3: Review Output

1. Open generated workbook
2. Verify Sheet 1 (Data):
   - All subsources appear as separate columns
   - Splice years highlighted in yellow
   - Final series values correct
3. Verify Sheet 2 (Provenance):
   - All sections complete
   - DPR/EPR information accurate
   - References correct

### Step 4: Validate Against Original

Compare with Shaikh Chopped source file:
```
Inputs/ShaikhChoppedTables/Appendix#_*.xlsx
```

---

## Relationship to Other Anu Components

### Anu Ingestion (formerly Anu Standard)

The Anu Extenbook **visualizes DPR documentation** in spreadsheet format:
- Subsources table from DPR → Sheet 2 Subsources section
- Transformation chain from DPR → Sheet 2 Transformation section
- Validation results from DPR → Sheet 2 Validation section

### Anu Extension Standard

The Anu Extenbook **visualizes EPR methodology**:
- Extension details → Sheet 2 Extension Details section
- Transition metrics → Sheet 2 Transition Metrics table
- Faithfulness score → Sheet 2 Certification section

### Anu Review

The Anu Extenbook **aids quality review**:
- Splice points visible in data for validation
- All subcomponents exposed for verification
- Complete documentation for audit trail

### Anu Visualize (formerly Anu Shiny)

The Anu Extenbook **complements interactive visualization**:
- Visualization app shows interactive charts
- Extenbook shows raw data construction
- Together provide complete transparency

---

## Key Differentiators from Previous Extenbooks

| Aspect | Chapter-Level Extenbooks | Figure-Level Extenbooks | Anu Extenbooks |
|--------|--------------------------|-------------------------|----------------|
| Unit | Chapter | Figure | **Series** |
| Sheets | 3 (Data, Metadata, Notes) | 5 (Overview, etc.) | **2 (Data, Provenance)** |
| Data Content | Multiple series | Metadata only | **All subcomponents** |
| Transformations | Described | Documented | **Visible in columns** |
| Splice Points | Mentioned | Referenced | **Highlighted rows** |
| Provenance | Separate files | Partial | **Fully integrated** |

---

## Validation Checklist

For each generated Anu Extenbook:

### Sheet 1: Data
- [ ] All subsources visible as separate columns
- [ ] Column colors follow standard (yellow/blue/orange/green)
- [ ] Splice years highlighted with yellow background
- [ ] NaN cells grayed out correctly
- [ ] Final series values match known data
- [ ] Freeze panes set correctly (B3)

### Sheet 2: Provenance
- [ ] Series Overview section complete
- [ ] Theoretical Context includes Shaikh quote
- [ ] Subsources table matches DPR
- [ ] Extension Details matches EPR (if applicable)
- [ ] Transition Metrics show PASS/FAIL correctly
- [ ] Faithfulness Score matches EPR
- [ ] References accurate

### Cross-Validation
- [ ] Subsource values match Shaikh Chopped original
- [ ] Splice years match EPR transition analysis
- [ ] Final series matches extended data files

---

## Troubleshooting

### Missing Subsource Data

**Error**: `Warning: No subsources found for S###`

**Solution**: 
1. Check `catalogs/SERIES_SUBSOURCES.json` for S###A, S###B entries
2. Run absorption script if needed: `python absorb_shaikh_chopped_v3.py`

### DPR/EPR Not Found

**Error**: `Warning: No DPR found for S###`

**Solution**:
1. Create DPR using Anu Standard skill
2. Create EPR using Anu Extension Standard skill (if extendable)

### Empty Chapter Data

**Error**: No data appears in Sheet 1

**Solution**:
1. Verify `data/ShaikhAbsorbed/chapter_##_data.csv` exists
2. Run absorption for that chapter

### Splice Point Mismatch

**Issue**: Splice years don't match EPR documentation

**Solution**:
1. Review EPR transition analysis
2. Update subsource period information
3. Regenerate extenbook

---

## Script Reference

### Main Script

**Location**: `Technical/scripts/create_anu_extenbooks.py`

### Key Functions

| Function | Purpose |
|----------|---------|
| `generate_series_extenbook(series_id)` | Create one extenbook |
| `create_data_sheet(ws, ...)` | Build Sheet 1 |
| `create_provenance_sheet(ws, ...)` | Build Sheet 2 |
| `generate_chapter_extenbooks(chapter)` | Generate all for chapter |
| `create_master_index(all_created)` | Create summary workbook |

### Command Line Usage

```bash
# Single series
python create_anu_extenbooks.py --series S001

# Single chapter
python create_anu_extenbooks.py --chapter 2

# All chapters
python create_anu_extenbooks.py --all
```

---

## Templates

Templates location: `skills/anu-extenbook/templates/`

| Template | Purpose |
|----------|---------|
| `EXTENBOOK_DATA_TEMPLATE.md` | Sheet 1 structure guide |
| `EXTENBOOK_PROVENANCE_TEMPLATE.md` | Sheet 2 structure guide |

---

## Integration with Arcanum Workflow

### In /readystart

When starting work on a chapter, Anu Extenbooks can be generated to review data construction before analysis.

### In /handoff

After completing work, generate Anu Extenbooks to document the final state of all extended series.

### In Anu Review

Reference Anu Extenbooks during chapter reviews to validate data construction.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-30 | Initial release |

---

## Related Documentation

| Document | Location |
|----------|----------|
| Skill Definition | `skills/anu-extenbook/SKILL.md` |
| Rules File | `.cursor/rules/anu-extenbook.md` |
| Data Template | `skills/anu-extenbook/templates/EXTENBOOK_DATA_TEMPLATE.md` |
| Provenance Template | `skills/anu-extenbook/templates/EXTENBOOK_PROVENANCE_TEMPLATE.md` |
| Generation Script | `Projects/Capitalism Data/Technical/scripts/create_anu_extenbooks.py` |

---

*Part of the Anu Framework - Data Construction Visualization*  
*Anu Extenbook Standard v1.0 - 2026-01-30*
