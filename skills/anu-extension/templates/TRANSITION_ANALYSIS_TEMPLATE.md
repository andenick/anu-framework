# [Series ID]: [Series Name] - Transition Analysis Report

## Overview

| Property | Value |
|----------|-------|
| Series ID | [S###] |
| Series Name | [Name] |
| Analysis Date | [YYYY-MM-DD] |
| Analyst | [Agent/Model] |
| Original Period | [YYYY-YYYY] |
| Extension Period | [YYYY-YYYY] |
| Transition Point | [YYYY] |

---

## Overlap Period Definition

### Period Details

| Field | Value |
|-------|-------|
| Overlap Start Year | [YYYY] |
| Overlap End Year | [YYYY] |
| Overlap Duration | [N] years |
| Original Observations | [Count] |
| Extension Observations | [Count] |

### Overlap Data

| Year | Original Value | Extension Value | Difference | % Difference |
|------|---------------|-----------------|------------|--------------|
| [YYYY] | [Value] | [Value] | [Diff] | [%] |
| [YYYY] | [Value] | [Value] | [Diff] | [%] |
| [YYYY] | [Value] | [Value] | [Diff] | [%] |

---

## Transition Metrics

### Metric 1: Connection Ratio

**Definition**: Ratio of extension value to original value at the transition point.

**Formula**:
```
Connection Ratio = Extension_Value(transition_year) / Original_Value(transition_year)
```

**Calculation**:
```
Extension Value at [YYYY]: [Value]
Original Value at [YYYY]: [Value]
Connection Ratio: [Value]
```

**Thresholds**:
| Range | Status |
|-------|--------|
| 0.97 - 1.03 | PASS |
| 0.95 - 1.05 | WARN |
| Outside 0.95-1.05 | FAIL |

**Result**: [PASS / WARN / FAIL]

---

### Metric 2: Growth Rate Continuity

**Definition**: Difference in growth rates between original and extension at transition.

**Formula**:
```
Growth Rate Continuity = |Extension_Growth_Rate - Original_Growth_Rate|
```

**Calculation**:
```
Original Growth Rate (YYYY to YYYY+1): [Value]%
Extension Growth Rate (YYYY to YYYY+1): [Value]%
Absolute Difference: [Value]%
```

**Thresholds**:
| Range | Status |
|-------|--------|
| < 3% | PASS |
| 3-5% | WARN |
| > 5% | FAIL |

**Result**: [PASS / WARN / FAIL]

---

### Metric 3: Trend Alignment

**Definition**: Correlation between original and extension series in the overlap period.

**Formula**:
```
Trend Alignment = Pearson Correlation(Original_Overlap, Extension_Overlap)
```

**Calculation**:
```
Overlap Period: [YYYY] to [YYYY]
Correlation: [Value]
```

**Thresholds**:
| Range | Status |
|-------|--------|
| > 0.98 | PASS |
| 0.95 - 0.98 | WARN |
| < 0.95 | FAIL |

**Result**: [PASS / WARN / FAIL]

---

### Metric 4: Level Difference

**Definition**: Average percentage difference between series in overlap period.

**Formula**:
```
Level Difference = Mean(|Extension - Original| / Original × 100)
```

**Calculation**:
```
Average Level Difference: [Value]%
Maximum Level Difference: [Value]%
Minimum Level Difference: [Value]%
```

**Thresholds**:
| Range | Status |
|-------|--------|
| < 1% | PASS |
| 1-3% | WARN |
| > 3% | FAIL |

**Result**: [PASS / WARN / FAIL]

---

## Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Connection Ratio | [Value] | 0.95 - 1.05 | [PASS/WARN/FAIL] |
| Growth Rate Continuity | [Value]% | < 5% | [PASS/WARN/FAIL] |
| Trend Alignment | [Value] | > 0.95 | [PASS/WARN/FAIL] |
| Level Difference | [Value]% | < 3% | [PASS/WARN/FAIL] |

---

## Splice Method

### Method Used

- [ ] **Direct Level Match** - Extension values used directly (no adjustment)
- [ ] **Growth Rate Splice** - Extension growth rates applied to original levels
- [ ] **Ratio Adjustment** - Adjustment factor applied for continuity
- [ ] **Retropolation** - Extension pattern applied backward
- [ ] **Other**: [Describe]

### Splice Formula

**If adjustment applied**:
```
[Mathematical formula for splice adjustment]
```

**Adjustment Factor**: [Value if applicable]

### Justification

[Explain why this splice method was chosen and why it is faithful to the original methodology]

---

## Visualization

### Transition Plot Description

**Plot Reference**: [Path to saved visualization or inline description]

**Plot Elements**:
- Original series: [Description of line style, color]
- Extension series: [Description]
- Overlap period: [How highlighted]
- Transition point: [How marked]

### Visual Assessment

[Describe what the transition plot shows:
- Is the transition smooth?
- Are there visible discontinuities?
- Do the series align well in the overlap?
- Any concerning patterns?]

---

## Transition Classification

### Overall Status

Based on metric results:

- [ ] **SEAMLESS** - All metrics PASS, smooth transition
- [ ] **ACCEPTABLE** - Minor WARN flags, documented and justified
- [ ] **PROBLEMATIC** - FAIL flags present, requires review
- [ ] **FAILED** - Critical failures, cannot proceed

### Classification Justification

[Provide detailed explanation of the classification:
- Which metrics passed/failed?
- Why is this classification appropriate?
- What are the implications for data quality?
- Are there any caveats for users of this data?]

---

## Root Cause Analysis (if WARN or FAIL)

### Identified Causes

| Issue | Cause | Evidence |
|-------|-------|----------|
| [Metric issue] | [Root cause] | [Supporting evidence] |

### Potential Sources of Discontinuity

- [ ] Methodology change in source data
- [ ] Definition change (what's included)
- [ ] Base year change
- [ ] Classification change
- [ ] Coverage change
- [ ] Seasonal adjustment difference
- [ ] Revision timing difference
- [ ] Data error in original or extension
- [ ] Other: [Describe]

### Mitigation Applied

[Describe any adjustments or documentation added to address issues]

---

## Recommendations

### For Data Users

[Provide guidance for users of this extended series:
- Are there periods to treat with caution?
- Should certain analyses avoid the transition period?
- What is the confidence level in the extension?]

### For Future Extensions

[Document lessons learned:
- What would improve future extensions?
- Are there better sources available?
- Should methodology be revisited?]

---

## Technical Details

### Data Sources

| Source | File/API | Accessed |
|--------|----------|----------|
| Original | [Source] | [Date] |
| Extension | [Source] | [Date] |

### Analysis Script

**Script**: [Path to analysis script or inline code reference]

**Key Functions Used**:
- [Function name]: [Purpose]

### Reproducibility

[Document how to reproduce this analysis:
- Required files
- Script to run
- Expected outputs]

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [YYYY-MM-DD] | [Agent] | Initial analysis |

---

*Generated following Anu Extension Standard v1.0*
*Transition Analysis Template*
