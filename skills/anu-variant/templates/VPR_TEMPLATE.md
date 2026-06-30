# [VARIANT_ID]: [Variant Name] - Variant Provenance Record

## Quick Reference

| Property | Value |
|----------|-------|
| Variant ID | [V-XX##-YYY] |
| Metric | [Metric name, e.g., Net Social Wage] |
| Method | [Method name, e.g., AS2 Baseline] |
| Domain | [Domain name, e.g., Social Wage] |
| Is Baseline | [YES/NO] |
| Coverage | [YYYY-YYYY] |
| Book Period | [YYYY-YYYY] |
| Data Vintage | [e.g., 2024Q4] |
| Validation Status | [PASS/PARTIAL/FAIL/PENDING] |
| Last Computed | [YYYY-MM-DD] |

---

## Methodological Description

### What This Variant Computes

[Describe the aggregate this variant calculates and how it differs from other variants of the same metric.]

### Original Author / Source

| Field | Value |
|-------|-------|
| Author | [Author name] |
| Publication | [Full citation] |
| Year | [YYYY] |
| Key Innovation | [What distinguishes this method] |

### Key Quotes

> "[Exact quote from the original source describing the methodology]"
>
> — [Author], [Publication], p. [Page]

> "[Additional quote if available]"
>
> — [Source]

**KB Source**: `knowledge_base/[document_path]`

---

## Parameter Specification

### VariantConfig Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| [param_name] | [value] | [Why this value was chosen for this variant] |
| [param_name] | [value] | [Justification] |
| [param_name] | [value] | [Justification] |
| [param_name] | [value] | [Justification] |
| [param_name] | [value] | [Justification] |

### Implementation Reference

| Field | Value |
|-------|-------|
| Script | [Relative path to calculator script] |
| Class | [Python class name] |
| Instance | [Variable name, e.g., VARIANT_AS2] |
| Config Lines | [Line numbers in script] |

---

## Data Sources

### Primary NIPA Series

| Series Code | Description | Table | Line | Usage |
|-------------|-------------|-------|------|-------|
| [code] | [description] | [NIPA table ref] | [line #] | [E1/E2/T1/T2/LS/GDP] |
| [code] | [description] | [table] | [line] | [usage] |

### NIPA Tables Used

| Table | Title | Lines Used | Purpose |
|-------|-------|------------|---------|
| [table ref] | [title] | [line numbers] | [What these lines provide] |
| [table ref] | [title] | [lines] | [purpose] |

### Linked Anu Standard Series

| Series ID | Name | Relationship |
|-----------|------|-------------|
| [S###] | [Series name] | [How it relates to this variant] |

---

## Computation Formula

### Core Formula

```
[AGGREGATE] = [FORMULA]
```

Example:
```
NSW = (E1 + E2 * LS) - (T1 + T2 * LS)
```

### Component Decomposition

| Component | Formula | Description |
|-----------|---------|-------------|
| E1 | [formula] | [Direct labor benefits] |
| E2 | [formula] | [Mixed public goods] |
| T1 | [formula] | [Social insurance taxes] |
| T2 | [formula] | [Other taxes] |
| LS | [formula] | [Labor share] |

### Variant-Specific Adjustments

[Describe any adjustments unique to this variant, e.g., indirect tax exclusion, military exclusion.]

---

## Validation Against Published Benchmarks

### Benchmark Sources

| Source | Author | Year | Coverage | Notes |
|--------|--------|------|----------|-------|
| [Publication] | [Author] | [YYYY] | [YYYY-YYYY] | [Notes on benchmark] |

### Benchmark Comparison

| Year | This Variant | Benchmark | Difference | % Diff | Status |
|------|-------------|-----------|------------|--------|--------|
| [YYYY] | [value] | [value] | [diff] | [%] | [PASS/WARN/FAIL] |
| [YYYY] | [value] | [value] | [diff] | [%] | [status] |
| [YYYY] | [value] | [value] | [diff] | [%] | [status] |

### Correlation with Reference

| Metric | Value | Period | Status |
|--------|-------|--------|--------|
| Pearson r | [value] | [YYYY-YYYY] | [PASS/FAIL (threshold: 0.95)] |
| Mean Absolute Error | [value]B | [YYYY-YYYY] | [status] |
| Max Absolute Error | [value]B | [year] | [status] |

---

## Cross-Variant Comparison

### Compared Against

| Variant ID | Method | Relationship |
|-----------|--------|-------------|
| [V-XX##-YYY] | [Method name] | [baseline/alternative/replication] |
| [V-XX##-YYY] | [Method name] | [relationship] |

### Key Differences

| Aspect | This Variant | [Other Variant ID] | Impact |
|--------|-------------|-------------------|--------|
| [Parameter/Feature] | [This value] | [Other value] | [Quantified impact] |
| [Parameter/Feature] | [This value] | [Other value] | [Impact] |

### Comparison Results

| Year | This NSW | [Other] NSW | Difference | Sign Agreement |
|------|---------|------------|------------|----------------|
| [YYYY] | [value] | [value] | [diff] | [YES/NO] |

**Comparison CSV**: `[path to nsw_variant_comparison.csv]`

---

## Vintage Information

### Current Data Vintage

| Field | Value |
|-------|-------|
| Vintage Label | [e.g., 2024Q4] |
| NIPA Release | [BEA release date] |
| Download Date | [YYYY-MM-DD] |
| Flat File | [filename] |

### Historical Vintages Computed

| Vintage | Date Computed | NSW Range | Notes |
|---------|--------------|-----------|-------|
| [vintage label] | [date] | [min-max] | [notes] |

---

## Known Issues and Limitations

1. **[Issue]**: [Description of limitation and its impact on results]
2. **[Issue]**: [Description]

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [YYYY-MM-DD] | [Agent] | Initial VPR creation |
| | | | |

---

*Generated following Anu Variant Standard v1.0*
*Variant Provenance Record Template*
