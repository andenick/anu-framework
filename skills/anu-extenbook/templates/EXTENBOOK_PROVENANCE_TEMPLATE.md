# Anu Extenbook Provenance Sheet Template

## Sheet 2: Provenance

This template defines the structure for the Provenance sheet in an Anu Extenbook.

---

## Overall Structure

The Provenance sheet uses a two-column key-value layout with section headers.

| Column A | Column B-G |
|----------|------------|
| Field Name | Value(s) |

**Column Widths**:
- Column A: 25 (field names)
- Columns B-G: 20 each (values)

---

## Section 1: Series Overview (Rows 1-4)

| Row | Column A | Column B | Column C | Column D | Column E | Column F |
|-----|----------|----------|----------|----------|----------|----------|
| 1 | **SERIES OVERVIEW** | | | | | |
| 2 | Series ID | S### | Title | [Series Title] | | |
| 3 | Chapter | ## | Figures | Fig#.#, Fig#.# | | |
| 4 | Period | YYYY-YYYY | Extension Status | [EXTENDED/HISTORICAL/NOT_APPLICABLE] | | |

**Styling**:
- Row 1: Bold, #4472C4 background, white text (section header)
- Rows 2-4: Normal, alternating #F2F2F2 background

---

## Section 2: Theoretical Context (Rows 6-12)

| Row | Column A | Column B-G (merged) |
|-----|----------|---------------------|
| 6 | **THEORETICAL CONTEXT** | |
| 7 | Shaikh Quote 1 | "[Quote from chapter/appendix]" — Shaikh (2016), p. ## |
| 8 | Shaikh Quote 2 | "[Additional quote if relevant]" — Shaikh (2016), p. ## |
| 9 | Relevance | [Description of series significance to Shaikh's argument] |
| 10 | Key Arguments | [Theoretical points this series supports] |
| 11 | HDARP Source | Knowledge_Base/HDARP_v3.3_Campaign/Body_Text/ch##_*.md |
| 12 | Appendix Reference | Appendix #.# — [Appendix title] |

**Styling**:
- Row 6: Section header style
- Rows 7-8: Wrap text, row height 60+
- Column B-G: Merged cells for quotes

---

## Section 3: Subsources (Rows 14-25)

| Row | Column A | Column B | Column C | Column D | Column E | Column F | Column G |
|-----|----------|----------|----------|----------|----------|----------|----------|
| 14 | **SUBSOURCES** | | | | | | |
| 15 | ID | Source | Period | Base Year | API/URL | Quality | Notes |
| 16 | S###A | [Source Name] | YYYY-YYYY | YYYY=100 | [URL if applicable] | official_statistics | [Notes] |
| 17 | S###B | [Source Name] | YYYY-YYYY | YYYY=100 | [URL if applicable] | official_statistics | [Notes] |
| 18 | S###C | [Source Name] | YYYY-YYYY | YYYY=100 | [API endpoint] | official_statistics | Extension source |
| ... | | | | | | | |

**Styling**:
- Row 14: Section header style
- Row 15: Table header (#4472C4 background)
- Rows 16+: Alternating background
- Original subsources: #FFF2CC background for ID column
- Extension subsources: #E6F2FF background for ID column

**Quality Categories**:
- official_statistics
- academic_research
- institutional
- historical_reconstruction
- calculated
- estimated

---

## Section 4: Transformation Chain (Rows 27-40)

| Row | Column A | Column B | Column C | Column D | Column E | Column F |
|-----|----------|----------|----------|----------|----------|----------|
| 27 | **TRANSFORMATION CHAIN** | | | | | |
| 28 | Step | Transform ID | Operation | Formula | Input | Output |
| 29 | 1 | T001 | load_historical | N/A | [Source file] | S###A_raw |
| 30 | 2 | T002 | load_modern | N/A | [API] | S###B_raw |
| 31 | 3 | T003 | rebase | value × (100/value[YYYY]) | S###A_raw | S###A_rebased |
| 32 | 4 | T004 | splice | growth_rate_splice(A, B, YYYY) | S###A, S###B | S###_spliced |
| 33 | 5 | T005 | extend | growth_rate_splice(orig, ext, YYYY) | S###_original, S###C | S###_extended |
| ... | | | | | | |

**Styling**:
- Row 27: Section header style
- Row 28: Table header
- Formula column: Monospace font (Consolas)

**Common Operations**:
- load_historical, load_modern, load_api
- rebase, reindex
- splice, growth_rate_splice, level_splice
- adjust, seasonally_adjust
- calculate, derive

---

## Section 5: Extension Details (Rows 42-55)

| Row | Column A | Column B | Column C | Column D |
|-----|----------|----------|----------|----------|
| 42 | **EXTENSION DETAILS** | | | |
| 43 | Original Source | [Source name and period] | | |
| 44 | Extension Source | [API/Source name] | Series ID | [e.g., FRED INDPRO] |
| 45 | Splice Year | YYYY | Splice Method | [growth_rate/level/ratio] |
| 46 | Overlap Period | YYYY-YYYY | Duration | # years |
| 47 | | | | |
| 48 | **Transition Metrics** | Value | Threshold | Status |
| 49 | Connection Ratio | #.### | 0.95-1.05 | PASS/FAIL |
| 50 | Growth Rate Continuity | #.##% | <5% | PASS/FAIL |
| 51 | Trend Alignment | #.### | >0.95 | PASS/FAIL |
| 52 | Level Difference | #.##% | <3% | PASS/FAIL |
| 53 | | | | |
| 54 | Transition Assessment | [SEAMLESS/ACCEPTABLE/PROBLEMATIC/FAILED] | | |
| 55 | Notes | [Explanation of any issues] | | |

**Styling**:
- Row 48: Sub-header style (#D9E2F3 background)
- Status column: Green for PASS, Red for FAIL
- Row 54: Bold

---

## Section 6: Validation (Rows 57-65)

| Row | Column A | Column B | Column C | Column D | Column E |
|-----|----------|----------|----------|----------|----------|
| 57 | **VALIDATION** | | | | |
| 58 | | Expected | Actual | Status | |
| 59 | Min Value | #.## | #.## | PASS/FAIL | |
| 60 | Max Value | #.## | #.## | PASS/FAIL | |
| 61 | Year Coverage | YYYY-YYYY | YYYY-YYYY | PASS/FAIL | |
| 62 | Missing Values | 0 | # | PASS/FAIL | |
| 63 | | | | | |
| 64 | Cross-Reference | Reference Series | Expected r | Actual r | Status |
| 65 | | S### | >0.## | 0.## | PASS/FAIL |

---

## Section 7: Faithfulness Certification (Rows 67-75)

| Row | Column A | Column B | Column C | Column D |
|-----|----------|----------|----------|----------|
| 67 | **FAITHFULNESS CERTIFICATION** | | | |
| 68 | Component | Weight | Score | Weighted |
| 69 | Methodology Match | 30% | ##% | ##.#% |
| 70 | Source Match | 20% | ##% | ##.#% |
| 71 | Transformation Replication | 20% | ##% | ##.#% |
| 72 | Transition Quality | 20% | ##% | ##.#% |
| 73 | Documentation Completeness | 10% | ##% | ##.#% |
| 74 | **TOTAL** | 100% | | **##%** |
| 75 | Certification Status | [CERTIFIED / CERTIFIED WITH NOTES / NOT CERTIFIED] | | |

**Styling**:
- Row 74: Bold, #E6FFE6 background for total
- Row 75: Large font for status
- CERTIFIED: Green background
- CERTIFIED WITH NOTES: Yellow background
- NOT CERTIFIED: Red background

---

## Section 8: Divergences (Rows 77-85)

| Row | Column A | Column B | Column C | Column D | Column E |
|-----|----------|----------|----------|----------|----------|
| 77 | **DIVERGENCES** | | | | |
| 78 | ADR ID | Title | Category | Impact | Status |
| 79 | ADR-### | [Divergence title] | [Category] | [Impact description] | [pending/accepted/rejected] |
| 80 | ADR-### | [Divergence title] | [Category] | [Impact description] | [pending/accepted/rejected] |
| ... | | | | | |
| 84 | | | | | |
| 85 | (none) | No divergences affecting this series | | | |

**Categories**:
- source_methodology_change
- coverage_change
- classification_change
- base_year_change
- discontinuity
- definition_change

---

## Section 9: References (Rows 87-95)

| Row | Column A | Column B-G (merged) |
|-----|----------|---------------------|
| 87 | **REFERENCES** | |
| 88 | DPR File | docs/series/S###_DPR.md |
| 89 | EPR File | docs/series/S###_EPR.md |
| 90 | Raw Data Location | Inputs/API/[SOURCE]/[file].csv |
| 91 | Extended Data Location | Outputs/Data/##_CHAPTER_NAME/S###_extended.csv |
| 92 | Shaikh Chopped Source | Inputs/ShaikhChoppedTables/Appendix#_[Name].xlsx |
| 93 | HDARP Chapter | Knowledge_Base/HDARP_v3.3_Campaign/Body_Text/ch##_*.md |
| 94 | HDARP Appendix | Knowledge_Base/HDARP_v4.0_Figure_Metadata/Chapter_18_Appendices/appendix_#_#.json |
| 95 | Extenbook Generated | YYYY-MM-DD HH:MM:SS |

---

## General Styling

### Section Headers

| Property | Value |
|----------|-------|
| Background | #4472C4 |
| Font | White, Bold, 12pt |
| Row Height | 25 |
| Merge | Columns A-G |

### Table Headers

| Property | Value |
|----------|-------|
| Background | #4472C4 |
| Font | White, Bold |
| Row Height | 20 |

### Data Rows

| Property | Value |
|----------|-------|
| Background | Alternating white / #F2F2F2 |
| Font | Normal, 10pt |
| Wrap Text | Yes for long content |

### Status Indicators

| Status | Background |
|--------|------------|
| PASS | #E6FFE6 (Light Green) |
| FAIL | #FFE6E6 (Light Red) |
| PENDING | #FFFFD6 (Light Yellow) |

---

## Print Settings

- Orientation: Landscape
- Fit to: 1 page wide
- Header: "Anu Extenbook: S### - Provenance"
- Footer: "Page &P of &N | Generated: [Date]"

---

*Template Version 1.0 - Anu Extenbook Standard*
