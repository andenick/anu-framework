# [SERIES_ID]: [Series Name] - Extension Provenance Record

## Quick Reference

| Property | Value |
|----------|-------|
| Series ID | [S###] |
| Series Name | [Full name] |
| Original Period | [YYYY-YYYY] |
| Extension Period | [YYYY-YYYY] |
| Original Source | [Source name] |
| Extension Source | [API/Source] |
| Transition Status | [SEAMLESS/ACCEPTABLE/PROBLEMATIC/FAILED] |
| Faithfulness Score | [0-100]% |
| Certification | [CERTIFIED/CERTIFIED WITH NOTES/NOT CERTIFIED] |
| Extension Date | [YYYY-MM-DD] |
| Certifying Agent | [Agent/Model] |

---

## Agent Understanding Statement

**REQUIRED**: Before any extension work, the agent must document their complete understanding of this series.

### What is this data?

[Provide a detailed description of the series and its economic meaning. Explain what this data measures, why it matters, and how it fits into broader economic analysis.]

### What was the original data source?

[Document the exact sources used in the original construction. Include:
- Source name (e.g., "BEA NIPA Table 1.14")
- Specific line items or series codes
- Time period in original source
- Units and frequency
- Any notes about source selection]

### What methodology was originally applied?

[Describe the step-by-step transformation chain used to construct the original series:
1. Raw data extraction
2. Any adjustments or corrections
3. Calculations or formulas applied
4. Splicing with other sources (if any)
5. Final transformations]

### What source will be used for extension?

[Document the source for extension data:
- API endpoint or data source
- Specific series/table identifiers
- Expected update frequency
- Any differences from original source]

### Have there been methodology updates?

**Answer**: [YES / NO]

[If YES, provide detailed explanation:
- What changed
- When it changed
- How it affects this series
- Impact assessment]

---

## Book Context

### Chapter References

| Chapter | Page | Quote | Relevance |
|---------|------|-------|-----------|
| [Ch#] | [Page] | "[Exact quote from the book]" | [How this informs the extension] |
| [Ch#] | [Page] | "[Another quote]" | [Relevance] |

**HDARP Source**: `Knowledge_Base/HDARP_v3.3_Campaign/Body_Text/ch##_*.md`

### Appendix References

| Appendix | Section | Quote | Formula |
|----------|---------|-------|---------|
| [App X.Y] | [Section title] | "[Exact quote from appendix]" | [Formula if applicable] |
| [App X.Y] | [Section] | "[Quote about methodology]" | [Formula] |

**HDARP Source**: `Knowledge_Base/HDARP_v4.0_Figure_Metadata/Chapter_18_Appendices/appendix_*.json`

### Figure Usage

| Figure | Caption | Series Role |
|--------|---------|-------------|
| [Fig X.Y] | [Full caption] | [How series appears: axis, line, component] |
| [Fig X.Y] | [Caption] | [Role in figure] |

**HDARP Source**: `ShinyApp/data/ShaikhAbsorbed/hdarp_v4/ch##_figures.json`

### Variable Definitions from Book

| Variable | Definition | Formula | Source |
|----------|------------|---------|--------|
| [Symbol] | [What it represents] | [Mathematical formula] | [Appendix X.Y] |

---

## Original Methodology Documentation

### Source: [Original Methodology PDF Title]

**Document**: [Full title, e.g., "BEA NIPA Methodology, September 2011"]
**HDARP Location**: `Knowledge_Base/HDARP_Methodology_Sources_2025.12.22/DOC_###/`
**Vintage Date**: [YYYY-MM]

#### Key Methodology Quotes

> "[Quote 1 from original methodology documentation that explains how this data was constructed]"
> 
> — [Source Document], p. [Page]

> "[Quote 2 explaining calculation methods or definitions]"
> 
> — [Source Document], p. [Page]

> "[Quote 3 about any special procedures or adjustments]"
> 
> — [Source Document], p. [Page]

#### Original Formulas

| Variable | Formula | Units | Source |
|----------|---------|-------|--------|
| [Var] | [Mathematical formula] | [Units] | [Document, Page] |

#### Original Data Tables Referenced

| Table | Title | Lines Used | Period |
|-------|-------|------------|--------|
| [Table ID] | [Title] | [Specific lines] | [YYYY-YYYY] |

---

## Current Methodology Documentation

### Source: [Current Methodology PDF Title]

**Document**: [Full title, e.g., "BEA NIPA Handbook Chapter 13, 2024"]
**HDARP Location**: `Knowledge_Base/HDARP_Methodology_Sources_2025.12.22/DOC_###/`
**Vintage Date**: [YYYY-MM]

#### Key Methodology Quotes

> "[Quote 1 from current methodology documentation]"
> 
> — [Source Document], p. [Page]

> "[Quote 2 explaining current calculation methods]"
> 
> — [Source Document], p. [Page]

#### Current Formulas

| Variable | Formula | Units | Source |
|----------|---------|-------|--------|
| [Var] | [Mathematical formula] | [Units] | [Document, Page] |

### Methodology Changes Assessment

| Aspect | Original (Vintage: YYYY) | Current (Vintage: YYYY) | Impact |
|--------|--------------------------|-------------------------|--------|
| Definition | [Original definition] | [Current definition] | [HIGH/MEDIUM/LOW/NONE] |
| Calculation | [Original method] | [Current method] | [Impact] |
| Coverage | [Original coverage] | [Current coverage] | [Impact] |
| Base Year | [Original base] | [Current base] | [Impact] |
| Classification | [Original system] | [Current system] | [Impact] |

**Overall Methodology Match**: [YES - Identical / YES - Minor differences / NO - Significant changes]

---

## Web Research Findings

### Search Queries Performed

1. "[Search query 1]" - [Date performed]
2. "[Search query 2]" - [Date]
3. "[Query about revisions]" - [Date]

### Key Findings

| Source | Date | Finding | Implication for Extension |
|--------|------|---------|---------------------------|
| [URL] | [Date] | [What was found] | [How this affects extension] |
| [URL] | [Date] | [Finding about revisions] | [Impact] |

### Methodology Revision History

| Revision Name | Year | Source | Impact on This Series |
|---------------|------|--------|----------------------|
| [e.g., "BEA Comprehensive Revision"] | [YYYY] | [URL or document] | [Description of impact] |
| [Revision] | [Year] | [Source] | [Impact] |

---

## Divergences (Anu Divergence Register)

### Divergences Affecting This Series

| ADR ID | Title | Category | Status |
|--------|-------|----------|--------|
| [ADR-###] | [Title] | [Category] | [pending_decision/accepted/adjusted/flagged/rejected] |

### Divergence Details

**[ADR-###]: [Title]**

- **Category**: [source_methodology_change / coverage_change / classification_change / base_year_change / discontinuity / definition_change]
- **Impact**: [Quantified impact if available]
- **Status**: [Current status]
- **Description**: [Brief description of the divergence]

### Resolution Status

- [ ] No divergences identified
- [ ] Divergences logged, pending researcher decision
- [ ] All divergences resolved

**Note**: If divergences exist, this EPR has status "CERTIFIED WITH NOTES" until resolved.

---

## API Configuration (v1.1)

### API Keys Used

| API | Key Source | Status |
|-----|------------|--------|
| FRED | Project: `Technical/ANU_REPLICATOR/config/api_keys.env` | [ACTIVE/MISSING] |
| BEA | Project: `Technical/ANU_REPLICATOR/config/api_keys.env` | [ACTIVE/MISSING] |

**Key Verification**: All API keys loaded from project-local config. No hardcoded keys.

### Fetcher Configuration

| Component | Version | Location |
|-----------|---------|----------|
| UnifiedDataFetcher | 1.0 | `Technical/scripts/tools/unified_fetcher.py` |
| FREDFetcher | 1.0 | `Technical/scripts/tools/fred_fetcher.py` |
| BEAFetcher | 1.0 | `Technical/scripts/tools/bea_fetcher.py` |

### Extension Script

| Field | Value |
|-------|-------|
| Script Location | `Technical/scripts/series_extensions/extend_[S###].py` |
| Script Version | [Version] |
| Last Run | [YYYY-MM-DD HH:MM:SS UTC] |
| Run Status | [SUCCESS/FAILED] |

---

## Subsource API Mapping

### Complete Subsource Inventory

| Subsource ID | Source Name | Type | API Endpoint | Period | Transform | Notes |
|--------------|-------------|------|--------------|--------|-----------|-------|
| [S###]A | [Source] | historical | None | [YYYY-YYYY] | None | From chopped table |
| [S###]B | [Source] | shaikh_original | None | [YYYY-YYYY] | None | Baseline data |
| [S###]C | [Source] | fred | FRED:[SERIES] | [YYYY-YYYY] | [Transform] | Live API |
| [S###]D | [Source] | bea_nipa | BEA:NIPA:[TABLE] | [YYYY-YYYY] | [Transform] | Live API |

### Subsource Types

- `historical`: From `Inputs/ShaikhChoppedTables/` Excel files
- `shaikh_original`: From Shaikh's original data (pre-2012)
- `fred`: FRED API (Federal Reserve Economic Data)
- `bea_nipa`: BEA NIPA tables
- `bea_fixed_assets`: BEA Fixed Assets tables
- `bea_gdp_industry`: BEA GDP by Industry tables
- `calculated`: Derived from other series

---

## Year-Source Matrix

### Data Attribution by Year

| Year Range | Subsource | Source | API | Data Origin |
|------------|-----------|--------|-----|-------------|
| [YYYY-YYYY] | [S###]A | [Source] | None | Chopped table: [filename] |
| [YYYY-YYYY] | [S###]B | [Source] | None | Shaikh original baseline |
| [YYYY-YYYY] | [S###]C | [Source] | [API:ID] | Live API fetch: [timestamp] |

### Splice Points

| Year | Before Source | After Source | Method | Validation |
|------|---------------|--------------|--------|------------|
| [YYYY] | [S###]A | [S###]B | [growth_rate/level_match] | [PASS/WARN/FAIL] |
| [YYYY] | [S###]B | [S###]C | [Method] | [Status] |

### Data Provenance Summary

```
Series [S###] Construction:
├── [YYYY-YYYY]: [Subsource A] from [Source]
│   └── File: [path/to/chopped/table.xlsx]
├── [YYYY-YYYY]: [Subsource B] from [Source]  
│   └── Shaikh baseline data
└── [YYYY-YYYY]: [Subsource C] from [Source]
    └── API: [ENDPOINT] fetched [TIMESTAMP]
```

---

## Live Pull Log

### API Fetch History

| Fetch ID | Timestamp | API | Endpoint | Status | Rows | Vintage |
|----------|-----------|-----|----------|--------|------|---------|
| FETCH001 | [ISO 8601] | FRED | [SERIES] | [OK/ERROR] | [N] | [YYYY-MM-DD] |
| FETCH002 | [ISO 8601] | BEA | [TABLE] | [Status] | [N] | [Vintage] |

### Response Verification

| Fetch ID | Response Hash (SHA256) | Cached | Cache Path |
|----------|------------------------|--------|------------|
| FETCH001 | [First 16 chars]... | YES/NO | [Path] |

### Data Quality Checks

| Check | Result | Notes |
|-------|--------|-------|
| Expected year range present | [PASS/FAIL] | [Notes] |
| No missing values in range | [PASS/FAIL] | [Notes] |
| Values within expected bounds | [PASS/FAIL] | [Notes] |
| Consistent with previous fetch | [PASS/FAIL/N/A] | [Notes] |

---

## Original Data Construction

### Original Subsources

| Subsource ID | Source | Period | Units | Frequency | Quality | Notes |
|--------------|--------|--------|-------|-----------|---------|-------|
| [S###]A | [Source name] | [YYYY-YYYY] | [Units] | [Annual/Quarterly/Monthly] | [HIGH/MEDIUM/LOW] | [Notes] |
| [S###]B | [Source name] | [YYYY-YYYY] | [Units] | [Frequency] | [Quality] | [Notes] |

### Original Transformations

| Step | Transform ID | Operation | Formula | Input | Output |
|------|--------------|-----------|---------|-------|--------|
| 1 | T### | [Operation type] | [Formula] | [Input data] | [Output data] |
| 2 | T### | [Operation] | [Formula] | [Input] | [Output] |
| 3 | T### | [Operation] | [Formula] | [Input] | [Output] |

### Shaikh's Construction Notes

> "[Exact quote from appendix about how this series was constructed]"
> 
> — Appendix [X.Y], p. [Page]

> "[Additional construction notes if available]"
> 
> — [Source]

---

## Extension Construction

### Extension Subsources

| Subsource ID | Source | Period | API/URL | Units | Frequency | Notes |
|--------------|--------|--------|---------|-------|-----------|-------|
| [S###]C | [Source] | [YYYY-YYYY] | [API endpoint] | [Units] | [Frequency] | [Notes] |

### Data Fetch Details

| Field | Value |
|-------|-------|
| API Endpoint | [Full URL or API call] |
| Download Timestamp | [YYYY-MM-DD HH:MM:SS UTC] |
| Data Vintage | [YYYY-MM-DD] |
| Raw File Location | [Path to raw downloaded file] |

### Extension Transformations

| Step | Transform ID | Operation | Formula | Input | Output | Faithful? |
|------|--------------|-----------|---------|-------|--------|-----------|
| 1 | T### | [Operation] | [Formula] | [Input] | [Output] | [YES/NO + reason] |
| 2 | T### | [Operation] | [Formula] | [Input] | [Output] | [YES/NO + reason] |

### Transformation Justification

**Step 1**: [Detailed explanation of why this transformation is faithful to the original methodology]

**Step 2**: [Justification for this step]

**Overall**: [Summary of how extension transformations replicate original construction]

---

## Transition Analysis

### Overlap Period

| Field | Value |
|-------|-------|
| Overlap Start | [YYYY] |
| Overlap End | [YYYY] |
| Duration | [N] years |
| Original Values in Overlap | [Count] observations |
| Extension Values in Overlap | [Count] observations |

### Transition Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Connection Ratio | [Value] | 0.95 - 1.05 | [PASS/WARN/FAIL] |
| Growth Rate Continuity | [Value]% | < 5% | [PASS/WARN/FAIL] |
| Level Difference | [Value]% | < 3% | [PASS/WARN/FAIL] |
| Trend Alignment (Correlation) | [Value] | > 0.95 | [PASS/WARN/FAIL] |

### Metric Calculations

**Connection Ratio**:
```
Extension_Value(overlap_start) / Original_Value(overlap_start) = [Value]
```

**Growth Rate Continuity**:
```
|Extension_Growth_Rate - Original_Growth_Rate| at transition = [Value]%
```

### Splice Method Used

- [ ] Direct Level Match - Extension values match original levels exactly
- [ ] Growth Rate Splice - Extension applied using growth rates
- [ ] Ratio Adjustment - Adjustment factor applied to maintain continuity
- [ ] Other: [Describe method]

**Splice Formula Applied**:
```
[Mathematical formula for splice, if applicable]
```

### Transition Visualization

**Chart Reference**: [Path to transition plot image or reference]

**Description**: [Brief description of what the transition visualization shows]

### Transition Assessment

**Status**: [SEAMLESS / ACCEPTABLE / PROBLEMATIC / FAILED]

**Detailed Assessment**:
[Provide thorough explanation of transition quality:
- How well do the series connect?
- Any visible discontinuities?
- Are growth rates consistent?
- Any concerns or caveats?]

---

## Validation Results

### Range Validation

| Period | Actual Min | Actual Max | Expected Min | Expected Max | Status |
|--------|------------|------------|--------------|--------------|--------|
| Original | [Value] | [Value] | [Value] | [Value] | [PASS/FAIL] |
| Extension | [Value] | [Value] | [Value] | [Value] | [PASS/FAIL] |
| Combined | [Value] | [Value] | [Value] | [Value] | [PASS/FAIL] |

### Cross-Reference Validation

| Reference Series | Expected Correlation | Actual Correlation | Status |
|------------------|---------------------|-------------------|--------|
| [Series ID] | [Value] | [Value] | [PASS/FAIL] |
| [Series ID] | [Value] | [Value] | [PASS/FAIL] |

### Automated Test Results

| Test Name | Result | Notes |
|-----------|--------|-------|
| Value range check | [PASS/FAIL] | [Notes] |
| Missing value check | [PASS/FAIL] | [Notes] |
| Monotonicity check (if applicable) | [PASS/FAIL] | [Notes] |
| Growth rate bounds | [PASS/FAIL] | [Notes] |
| Cross-reference correlation | [PASS/FAIL] | [Notes] |

### Documentation Completeness

| Section | Status |
|---------|--------|
| Agent Understanding | [COMPLETE/INCOMPLETE] |
| Book Context | [COMPLETE/INCOMPLETE] |
| Original Methodology | [COMPLETE/INCOMPLETE] |
| Current Methodology | [COMPLETE/INCOMPLETE] |
| Methodology Comparison | [COMPLETE/INCOMPLETE] |
| Transformation Chain | [COMPLETE/INCOMPLETE] |
| Transition Analysis | [COMPLETE/INCOMPLETE] |
| Validation Results | [COMPLETE/INCOMPLETE] |

---

## Extension Certification

### Faithfulness Score: [0-100]%

**Calculation**:

| Component | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Methodology Match | 30% | [0-100]% | [Value]% |
| Source Match | 20% | [0-100]% | [Value]% |
| Transformation Replication | 20% | [0-100]% | [Value]% |
| Transition Quality | 20% | [0-100]% | [Value]% |
| Documentation Completeness | 10% | [0-100]% | [Value]% |
| **Total** | **100%** | | **[Total]%** |

### Scoring Criteria

**Methodology Match (30%)**:
- 100%: Identical methodology, no changes
- 75-99%: Minor changes, well documented
- 50-74%: Moderate changes, may affect comparability
- <50%: Significant methodology differences

**Source Match (20%)**:
- 100%: Same source, same table, same lines
- 75-99%: Same source, minor differences
- 50-74%: Different table or source with equivalent coverage
- <50%: Substantially different source

**Transformation Replication (20%)**:
- 100%: All transformations exactly replicated
- 75-99%: Minor variations, mathematically equivalent
- 50-74%: Some transformations approximated
- <50%: Cannot replicate key transformations

**Transition Quality (20%)**:
- 100%: SEAMLESS - All metrics pass
- 75-99%: ACCEPTABLE - Minor deviations
- 50-74%: PROBLEMATIC - Significant deviations documented
- <50%: FAILED - Cannot establish valid connection

**Documentation Completeness (10%)**:
- 100%: All sections complete with quotes
- 75-99%: Most sections complete
- 50-74%: Key sections missing
- <50%: Inadequate documentation

### Certification Status

- [ ] **CERTIFIED** - Maximally faithful extension (Score >= 90%)
- [ ] **CERTIFIED WITH NOTES** - Faithful with documented deviations (Score >= 75%)
- [ ] **NOT CERTIFIED** - Significant methodology differences (Score < 75%)

### Certification Notes

[Document any deviations, caveats, or important notes about this extension]

### Certifying Agent

| Field | Value |
|-------|-------|
| Agent | [Model name / Agent ID] |
| Date | [YYYY-MM-DD] |
| Session | [Session ID if available] |
| Anu Extension Version | 1.0 |

---

## Related Documentation

### Associated Files

| File | Location | Purpose |
|------|----------|---------|
| DPR | [Path to S###_DPR.md] | Original series documentation |
| Raw Data | [Path to raw download] | Unprocessed extension data |
| Extended Data | [Path to extended CSV] | Final extended series |
| Transition Plot | [Path to visualization] | Transition analysis chart |

### TRANSFORMATION_LOG Entries

| Transform ID | Description | Logged |
|--------------|-------------|--------|
| T### | [Description] | [YES/NO] |
| T### | [Description] | [YES/NO] |

### EXTENSION_LOG Entry

```json
{
  "extension_id": "[EXT###]",
  "series_id": "[S###]",
  "timestamp": "[YYYY-MM-DDTHH:MM:SSZ]",
  "faithfulness_score": [Score],
  "certification": "[Status]"
}
```

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [YYYY-MM-DD] | [Agent] | Initial extension |
| | | | |

---

*Generated following Anu Extension Standard v1.0*
*Extension Provenance Record Template*
