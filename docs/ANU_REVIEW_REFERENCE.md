# Anu Review Reference Documentation

**Version:** 2.0
**Status:** Active
**Last Updated:** March 2026
**Part of:** Anu Framework v10.0 (18 skills)

> **Note**: This reference doc covers the v2.0 12-dimension model. The `anu-review` skill is now at v4.1 and adds two PASS/FAIL gates: D13 (Data Authenticity) and D14 (Outward-Facing Intelligibility). See `SKILL_VERSION_MATRIX.md` and `anu-review/SKILL.md` for the authoritative current spec. References below to "Anu Standard" mean `anu-ingestion`; "Anu Shiny" means `anu-visualize`.

---

## Table of Contents

1. [Overview](#overview)
2. [Purpose and Philosophy](#purpose-and-philosophy)
3. [Review Dimensions](#review-dimensions)
4. [Scoring Methodology](#scoring-methodology)
5. [Checklists](#checklists)
6. [Commands](#commands)
7. [Templates](#templates)
8. [Validation Scripts](#validation-scripts)
9. [Integration with Anu Framework](#integration-with-anu-suite)
10. [Example Review](#example-review)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Anu Review is a systematic audit tool for reviewing how well data chapters/modules are integrated into a data construction project. It provides:

- **Quantitative assessment** of integration completeness
- **Qualitative analysis** of documentation quality
- **Gap identification** with prioritized action items
- **Certification levels** for tracking project maturity

### Key Features

- 12 weighted review dimensions + D0 pre-pipeline gate (skill v4.1 adds D13/D14 gates)
- Automated validation via Python scripts
- Standardized report templates
- Full integration with all 18 Anu Framework skills

---

## Purpose and Philosophy

### Why Anu Review?

Data construction projects involve multiple interconnected components:
- Source data and transformations
- Documentation (DPRs, EPRs)
- Code (data loaders, chart builders)
- Tests and validation
- Catalog entries

The Anu Review ensures all these components are properly connected and documented.

### Design Principles

1. **Measurable** - Every dimension has quantifiable scoring
2. **Actionable** - Reports include specific remediation steps
3. **Reproducible** - Same review produces same results
4. **Incremental** - Can review single chapters or entire projects
5. **Integrated** - Works with Anu Standard and Anu Extension

### Alignment with Data Quality Standards

The Anu Review incorporates best practices from:
- **FAIRER principles** - Findability, Accessibility, Interoperability, Reusability, Ethics, Reproducibility
- **ISO 8000** - Data quality management
- **DAMA DMBOK** - Data governance frameworks

---

## Review Dimensions

### Dimension Overview

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|------------------|
| D0 | Pre-Pipeline Adequacy | Gate | Was KB/data readiness verified before construction? (Anu Adequacy) |
| D1 | KB Completeness | 6% | Knowledge Base text pages, tables, equations, external papers |
| D2 | Absorption Quality | 5% | Absorbed CSV completeness, zero missing values, format compliance |
| D3 | Research Coverage | 8% | Research JSONs per series, KB refs validated, external scholarship |
| D4 | Decomposition Coverage | 9% | DECOMPOSITION.md per series with Mermaid diagrams and construction steps |
| D5 | DPR Completeness | 10% | Data Provenance Records with validation records resolved |
| D6 | EPR Completeness | 8% | Extension Provenance Records with faithfulness scores |
| D7 | Chopped Validation | 9% | Chopped CSVs pass format validator, dash-notation, metadata |
| D8 | Replicator Scripts | 12% | L##/P## scripts with docstrings, REPLICATOR_README, end-to-end verified |
| D9 | Extenbook Quality | 6% | XLSX files with 4 sheets (Data, Provenance, Research, Construction) |
| D10 | Viz Integration | 8% | ShinyApp data, series catalog, figure browser, methodology toggles |
| D11 | Test Coverage | 7% | Test files, artifact assertions, benchmark validation, cross-chapter checks |
| D12 | Documentation | 12% | FPRs, chapter investigations, ledger, comparison reviews, migration logs |

### Dimension D0: Pre-Pipeline Adequacy (Gate — unweighted)

**What it checks:**
- `CH{N}_ADEQUACY_REPORT.json` exists for the chapter
- Overall adequacy rating is ADEQUATE or higher
- All 5 layers (Source Text, Series Definition, Data Availability, Construction Logic, Validation Data) scored

**Scoring:** PASS/FAIL gate. Does not contribute to the weighted percentage score. Reported as context in the review report header.

**Why unweighted:** Adequacy is a precondition assessed before construction, not a quality dimension of the built artifacts. D1-D12 measure what was built; D0 measures whether readiness was verified before building. A chapter can score 100% on D1-D12 without D0 if the agent happened to have sufficient information — but D0 ensures this is verified systematically rather than by luck.

**In review reports:** Add a row above D1:
```
| D0 | Pre-Pipeline Adequacy | Gate | PASS (92/100) | Adequacy verified 2026-03-22 |
```

### Dimension D1: KB Completeness (6%)

**What it checks:**
- Knowledge Base text pages cover the chapter's page range
- Tables extracted from book appendices (CSV format)
- Equations extracted (TEX/TXT format)
- External papers integrated via PDF extraction (organized by theme)
- EXTERNAL_PAPERS_INDEX.md exists with paper-to-series mapping

**Scoring:**
```
KB Score = weighted average of (page coverage 40%, tables 25%, equations 15%, external papers 20%)
```

### Dimension D2: Absorption Quality (5%)

**What it checks:**
- `chapter_NN_absorbed.csv` exists in long format
- Zero missing values in absorbed data
- Absorption report (`chapter_NN_absorbed_REPORT.md`) documents column mappings
- All series for the chapter are present in the absorbed CSV

**Scoring:**
```
Absorption Score = (file exists 30%) + (zero missing 30%) + (report exists 20%) + (all series present 20%)
```

### Dimension D3: Research Coverage (8%)

**What it checks:**
- S###_research.json exists for every series in the chapter
- `kb_sources_searched` entries are valid paths (no broken references)
- External scholarship linked (Mohun, Moos, Tonak, etc.)
- `adequacy_refs` field present (v1.3+)
- Methodology summary is substantive

**Scoring:**
```
Research Score = (JSONs exist / expected) × completeness multiplier
```

### Dimension D4: Decomposition Coverage (9%)

**What it checks:**
- S###_DECOMPOSITION.md exists for every series
- Contains Mermaid flow diagram
- Has Quick Reference table and Construction Steps
- Terminal nodes map to identified data sources

**Scoring:**
```
Decomposition Score = (files exist / expected) × (sections complete / required sections)
```

### Dimension D5: DPR Completeness (10%)

**What it checks:**
- S###_DPR.md exists for every series
- Follows Anu Standard v2.0 template (Context, Subsources, Transformation Chain, Validation Record, Known Issues)
- Validation records are resolved (not PENDING)
- Source quotes included

**Scoring:**
```
DPR Score = (complete DPRs / total series) × 100%
PENDING validations reduce the score proportionally.
```

### Dimension D6: EPR Completeness (8%)

**What it checks:**
- S###_EPR.md exists for every extendable series
- Faithfulness score present and justified
- Transition analysis documented
- Certification status assigned

**Scoring:**
```
EPR Score = (complete EPRs / extendable series) × 100%
Series that are book-period-only are excluded from the denominator.
```

### Dimension D7: Chopped Validation (9%)

**What it checks:**
- S###_chopped.csv exists for every series
- Row 1: pipe-separated metadata
- Row 2: dash-notation column IDs matching S###-[SUBSERIES] pattern
- Row 3+: numeric data
- Cross-check against series_registry.json subseries definitions
- SUBSOURCE_METADATA.json has entries for each column

**Scoring:**
```
Chopped Score = (passing CSVs / total CSVs) × 100%
Automated validator (validate_chopped.py) preferred.
```

### Dimension D8: Replicator Scripts (12%)

**What it checks:**
- Loading scripts (L##) exist for all data sources
- Processing scripts (P##) exist for all Tier 1 series
- Scripts have docstrings and error handling
- REPLICATOR_README.md documents the pipeline
- `replicate.py` orchestrator runs end-to-end without errors

**Scoring:**
```
Replicator Score = (scripts exist 40%) + (docstrings 15%) + (README 15%) + (end-to-end run 30%)
```

### Dimension D9: Extenbook Quality (6%)

**What it checks:**
- S###_extenbook.xlsx exists for every series
- Has 4 sheets: Data, Provenance, Research, Construction
- Research sheet populated from research JSON
- Data sheet contains full period range

**Scoring:**
```
Extenbook Score = (files exist / expected) × (sheets complete / 4)
```

### Dimension D10: Viz Integration (8%)

**What it checks:**
- ShinyApp has chapter data CSV
- series_catalog.json has entries for chapter series
- Figure browser tab functional (if applicable)
- Methodology toggle on key charts (if applicable)
- SUBSOURCE_METADATA.json integrated

**10-point viz quality checklist:**
1. Chapter CSV exists in ShinyApp/data/
2. Series catalog entries present
3. Figure-column mapping defined
4. Interactive plotly charts render
5. Methodology comparison available
6. Extension period visible
7. Subsource metadata connected
8. Dual-axis support (if needed)
9. Data validation panel functional
10. Author quotes accessible

**Scoring:**
```
Viz Score = (checklist items passing / 10) × 100%
```

### Dimension D11: Test Coverage (7%)

**What it checks:**
- test_chapter_NN.R exists
- Artifact existence tests (DPRs, EPRs, chopped CSVs)
- Data range checks (year coverage, no NAs)
- Benchmark validation against published values
- Cross-chapter consistency checks (if applicable)
- test_artifacts.R with project-wide assertions

**Scoring:**
```
Test Score = (test sections present / required) × 100%
```

### Dimension D12: Documentation (12%)

**What it checks:**
- FPRs (Figure Provenance Records) for all figures
- Chapter investigation document
- REPLICATOR_README.md
- ANU_LEDGER.json entry
- PIPELINE_STATE.json entry
- Cross-study comparisons (if applicable)
- MIGRATION_LOG, EXTERNAL_PAPERS_INDEX (if applicable)

**Scoring:**
```
Documentation Score = (artifacts present / expected) × completeness multiplier
```

---

## Scoring Methodology

### Integration Score Formula (v2.0)

```
Overall Score =
  (D1_KB × 0.06) +
  (D2_Absorption × 0.05) +
  (D3_Research × 0.08) +
  (D4_Decomposition × 0.09) +
  (D5_DPR × 0.10) +
  (D6_EPR × 0.08) +
  (D7_Chopped × 0.09) +
  (D8_Replicator × 0.12) +
  (D9_Extenbook × 0.06) +
  (D10_Viz × 0.08) +
  (D11_Tests × 0.07) +
  (D12_Docs × 0.12)
  = 100% total weight
```

D0 (Pre-Pipeline Adequacy) is reported separately as a PASS/FAIL gate and does not contribute to the weighted score.

### Certification Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| **EXEMPLARY** | ≥95% | Reference implementation. Exceeds all standards. Can be used as template for other chapters. |
| **COMPLETE** | 85-94% | Fully integrated. Meets all core requirements. Ready for production use. |
| **ADEQUATE** | 70-84% | Functional with documented gaps. Acceptable for development but should be improved. |
| **INCOMPLETE** | <70% | Requires attention. Should not be used in production until gaps are addressed. |

### Score Interpretation

**95-100% (EXEMPLARY)**
- All DPRs complete with thorough documentation
- All EPRs have faithfulness assessments
- Data files fully validated
- Comprehensive test coverage
- Excellent knowledge base integration

**85-94% (COMPLETE)**
- Core DPRs complete
- Extended series have EPRs
- Data files exist and are mapped
- Good test coverage
- Adequate documentation

**70-84% (ADEQUATE)**
- Most DPRs exist but may have gaps
- Some EPRs missing or incomplete
- Data files exist
- Basic test coverage
- Documentation needs improvement

**<70% (INCOMPLETE)**
- Missing DPRs
- Missing EPRs for extended series
- Data file issues
- Insufficient test coverage
- Documentation gaps

---

## Checklists

### DPR Checklist

```markdown
## DPR: [SERIES_ID]

### File
- [ ] DPR file exists at `docs/series/[SERIES_ID]_DPR.md`

### Quick Reference
- [ ] Series ID present
- [ ] Title present
- [ ] Type specified
- [ ] Year range documented
- [ ] Quality category assigned

### Context
- [ ] Shaikh quotes included
- [ ] Theoretical significance explained
- [ ] Figure reference present

### Subsources
- [ ] All subsources listed
- [ ] Quality categories assigned
- [ ] Source links provided

### Transformation Chain
- [ ] All transformations documented
- [ ] T[XXX] identifiers used
- [ ] Input → Output mappings clear

### Validation
- [ ] Validation record present
- [ ] Date documented
- [ ] Status recorded
```

### EPR Checklist

```markdown
## EPR: [SERIES_ID]

### File
- [ ] EPR file exists at `docs/series/[SERIES_ID]_EPR.md`

### Understanding
- [ ] Agent understanding statement present
- [ ] Series purpose documented
- [ ] Extension rationale explained

### Context
- [ ] Book quotes included
- [ ] Original methodology documented
- [ ] Current methodology documented

### Methodology Changes
- [ ] Changes assessment present
- [ ] Sources compared
- [ ] Definitions checked

### Transition Analysis
- [ ] Transition metrics calculated
- [ ] Overlap period analyzed
- [ ] Connection ratio documented

### Certification
- [ ] Faithfulness score calculated
- [ ] Certification status assigned
- [ ] Notes documented (if applicable)
```

---

## Commands

### Basic Usage

```bash
/anu-review 2                    # Review Chapter 2
/anu-review 17                   # Review Chapter 17
```

### Advanced Usage

```bash
/anu-review full Capitalism Data # Review entire project
/anu-review compare 2 5          # Compare Chapters 2 and 5
/anu-review gaps 2               # Show only gaps for Chapter 2
/anu-review score 2              # Show only score for Chapter 2
/anu-review checklist 2          # Show checklist for Chapter 2
```

### Output Options

- **Default**: Full review report
- **gaps**: Gap analysis only
- **score**: Score summary only
- **checklist**: Pass/fail checklist

---

## Templates

### Location

```
skills/anu-review/templates/
├── REVIEW_REPORT_TEMPLATE.md
├── CHECKLIST_TEMPLATE.md
└── GAP_ANALYSIS_TEMPLATE.md
```

### REVIEW_REPORT_TEMPLATE.md

Complete review report including:
- Quick reference table
- Dimension scores
- Dimension details
- Gap analysis
- Action items
- Series inventory

### CHECKLIST_TEMPLATE.md

Pass/fail checklist organized by dimension with:
- Checkbox items for each requirement
- Series-level status tracking
- Summary section

### GAP_ANALYSIS_TEMPLATE.md

Detailed gap analysis including:
- Gap classification (Critical/Moderate/Minor)
- Remediation steps
- Effort estimates
- Dependency mapping
- Score projections

---

## Validation Scripts

### Location

```
skills/anu-review/scripts/
├── run_review.py         # Main orchestrator
├── validate_dpr.py       # DPR validation
├── validate_epr.py       # EPR validation
└── generate_report.py    # Report generator
```

### run_review.py

Main orchestrator that:
1. Accepts chapter ID and project path
2. Runs all validation modules
3. Calculates dimension scores
4. Generates report output

**Usage:**
```bash
python run_review.py 2 --project /path/to/project --series S001 S002 S003
```

### validate_dpr.py

DPR validation module that:
1. Checks file existence
2. Parses required sections
3. Validates content completeness
4. Returns structured results

### validate_epr.py

EPR validation module that:
1. Checks file existence for extended series
2. Validates faithfulness assessment
3. Checks transition analysis
4. Returns structured results

### generate_report.py

Report generator that:
1. Takes validation results
2. Populates templates
3. Generates markdown output
4. Supports multiple output formats

---

## Integration with Anu Framework

The Anu Review is a **floating** skill — it can run at any stage of the Anu Pipeline, not just at the end. It validates artifacts produced by all upstream skills:

| Dimension | Validates Output Of |
|-----------|-------------------|
| D0 | Anu Adequacy (Stage 0) |
| D1 | Anu Ingestion — KB Construction (Stage 2) |
| D2 | Anu Ingestion — Absorption (Stage 2) |
| D3 | Anu Research (Stage 1) |
| D4 | Anu Ingestion — Decomposition (Stage 2) |
| D5 | Anu Ingestion — DPR Documentation (Stage 2) |
| D6 | Anu Extension (Stage 3) |
| D7 | Anu Chopped (Stage 5) |
| D8 | Anu Replicator (Stage 4) |
| D9 | Anu Extenbook (Stage 5) |
| D10 | Anu Visualize (Stage 7) |
| D11 | Cross-cutting (tests for all stages) |
| D12 | Cross-cutting (documentation across all stages) |

### Recommended Workflow

1. **Run Adequacy Check** (Stage 0)
   ```
   /anu-adequacy check [chapter]
   ```

2. **Complete Pipeline** (Stages 1-5b)
   ```
   /anu-pipeline run-stage [stage] [chapter]
   ```

3. **Run Review** (Stage 6)
   ```
   /anu-review [chapter]
   ```

4. **Address Gaps** — fix critical issues, re-run review

5. **Target Certification** — COMPLETE (85%+) or EXEMPLARY (95%+)

---

## Example Review

### Chapter 2 Review

```
=============================================================
                 ANU REVIEW REPORT: Chapter 2
=============================================================

Quick Reference:
  Chapter:           2
  Title:             Turbulent Macro Dynamics
  Series:            S001-S018 (18 total)
  Integration Score: 85%
  Status:            COMPLETE

Dimension Scores:
  DPR Completeness:        100% (18/18 DPRs exist)
  EPR Completeness:        67%  (12/18 extended, 6 conceptual)
  Data File Integrity:     90%  (extended CSV has gaps)
  Series Mapping:          100% (18/18 mapped)
  Chart Builder:           80%  (generic builders used)
  Test Coverage:           100% (comprehensive tests)
  Catalog Consistency:     100% (all figures correct)
  Knowledge Base:          70%  (partial documentation)

Gaps Identified:
  1. Extended CSV incomplete: S008, S011-S018 missing
  2. S016 marked needs_source = TRUE
  3. No specialized chart builders for profit rate series
  4. Limited web research documentation

Action Items:
  [HIGH] Complete extended CSV with missing series
  [MED]  Investigate S016 source data
  [LOW]  Consider specialized builders for S013-S015
  [LOW]  Add web research to DPRs

=============================================================
```

---

## Best Practices

### Review Frequency

- **After completion**: Run review after each chapter integration
- **Before milestones**: Run full project review before major releases
- **Regular audits**: Periodic reviews to catch drift

### Addressing Gaps

1. **Critical first**: Always fix critical gaps before moderate
2. **Dependencies**: Check gap dependencies before fixing
3. **Verify fixes**: Re-run review after addressing gaps
4. **Document decisions**: Record why gaps were accepted (if any)

### Maintaining Quality

- **Continuous improvement**: Target higher certification levels over time
- **Cross-chapter consistency**: Use exemplary chapters as templates
- **Knowledge sharing**: Document lessons learned

### Common Pitfalls

1. **Skipping EPRs**: Extended series MUST have EPRs
2. **Generic tests**: Tests should cover Shaikh findings
3. **Incomplete catalogs**: All figures need full metadata
4. **Missing quotes**: DPRs should include actual book quotes

---

## Troubleshooting

### Low DPR Score

**Symptoms**: DPR Completeness < 70%

**Causes**:
- Missing DPR files
- Incomplete sections
- Missing source quotes

**Solutions**:
- Run `/anu-ingestion` for missing series
- Add Quick Reference tables
- Extract quotes from source materials

### Low EPR Score

**Symptoms**: EPR Completeness < 70%

**Causes**:
- Missing EPR files for extended series
- Incomplete faithfulness assessment
- Missing transition analysis

**Solutions**:
- Identify which series are extended
- Run `/anu-extension` for each
- Complete transition analysis

### Low Mapping Score

**Symptoms**: Series Mapping < 70%

**Causes**:
- Missing series in CH[X]_SERIES_MAPPING
- Incomplete mapping fields
- Wrong data_patterns

**Solutions**:
- Review data_loader.R
- Add all series to mapping
- Verify patterns match CSV columns

### Low Test Score

**Symptoms**: Test Coverage < 70%

**Causes**:
- Missing test file
- Incomplete test sections
- No thematic tests

**Solutions**:
- Create test_chapter_XX.R
- Add required test sections
- Test Shaikh findings

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial release with 8 dimensions |
| 2.0 | March 2026 | Expanded to 12 weighted dimensions + D0 gate. Added KB Completeness (D1), Absorption Quality (D2), Research Coverage (D3), Decomposition Coverage (D4), Chopped Validation (D7), Extenbook Quality (D9), Viz Integration (D10). Integrated with full Anu Framework v5.0 (12 skills). |

---

## References

- [Anu Framework Overview](ANU_FRAMEWORK_OVERVIEW.md)
- [Skill Version Matrix](SKILL_VERSION_MATRIX.md)
- [Anu Extension Standard](ANU_EXTENSION_STANDARD.md)
- [SKILL.md](../skills/anu-review/SKILL.md)

---

*Anu Review reference (v2.0 model) | Part of the Anu Framework v10.0*
