# [DATASET_ID]: [Dataset Name] - Data Provenance Record

## Anu Standard Compliance: v2.2

---

## Quick Reference

| Property | Value |
|----------|-------|
| Dataset ID | [DATASET_ID] |
| Type | time_series / derived |
| Time Period | [START_YEAR]-[END_YEAR] |
| Frequency | annual / quarterly / monthly / daily |
| Source Count | [#] |
| Base Year | [YEAR or N/A] |
| Units | [units] |
| Validation Status | PENDING |
| Last Updated | [YYYY-MM-DD] |

---

## Context

> "[Optional: Quote from source author about this data or its significance]"
> — [Author], [Source], p. [page]

[Brief description of what this dataset represents and why it matters for the project.]

---

## Subsources

| ID | Source | Period | API/URL | Quality | Notes |
|----|--------|--------|---------|---------|-------|
| [ID]A | [Source Name] | [YYYY-YYYY] | [URL or API] | [quality_category] | [notes] |
| [ID]B | [Source Name] | [YYYY-YYYY] | [URL or API] | [quality_category] | [notes] |

### Quality Categories
- `official_statistics` - Government/central bank data (HIGH reliability)
- `academic_research` - Peer-reviewed sources (HIGH reliability)
- `institutional` - IMF, World Bank, etc. (HIGH reliability)
- `historical_reconstruction` - Reconstructed from archives (MEDIUM reliability)
- `calculated` - Derived from formulas (VARIES)
- `estimated` - Third-party estimates (MEDIUM reliability)

---

## Subsource API Mapping (v2.2)

### Complete Subsource Inventory

| Subsource ID | Source Name | Type | API Endpoint | Period | Transform | File/Cache |
|--------------|-------------|------|--------------|--------|-----------|------------|
| [ID]A | [Source] | historical | None | [YYYY-YYYY] | None | [chopped table path] |
| [ID]B | [Source] | shaikh_original | None | [YYYY-YYYY] | None | [baseline file] |
| [ID]C | [Source] | fred | FRED:[SERIES] | [YYYY-YYYY] | [transform] | [cache path] |
| [ID]D | [Source] | bea_nipa | BEA:NIPA:[TABLE] | [YYYY-YYYY] | [transform] | [cache path] |

### Subsource Types
- `historical` - From `Inputs/ShaikhChoppedTables/` Excel files
- `shaikh_original` - From Shaikh's original absorbed data
- `fred` - FRED API (Federal Reserve Economic Data)
- `bea_nipa` - BEA NIPA tables
- `bea_fixed_assets` - BEA Fixed Assets tables
- `bea_gdp_industry` - BEA GDP by Industry tables
- `calculated` - Derived from other series

### API Configuration

| API | Key Source | Status |
|-----|------------|--------|
| FRED | Project: `Technical/ANU_REPLICATOR/config/api_keys.env` | [ACTIVE/MISSING/N/A] |
| BEA | Project: `Technical/ANU_REPLICATOR/config/api_keys.env` | [ACTIVE/MISSING/N/A] |

---

## Year-Source Matrix (v2.2)

### Data Attribution by Year

| Year Range | Subsource | Source | API | Data Origin |
|------------|-----------|--------|-----|-------------|
| [YYYY-YYYY] | [ID]A | [Source] | None | Chopped table: [filename] |
| [YYYY-YYYY] | [ID]B | [Source] | None | Shaikh original baseline |
| [YYYY-YYYY] | [ID]C | [Source] | [API:ID] | Live API fetch |

### Splice Points

| Year | Before Source | After Source | Method | Status |
|------|---------------|--------------|--------|--------|
| [YYYY] | [ID]A | [ID]B | [growth_rate/level_match] | [VALIDATED/PENDING] |

### Data Provenance Tree

```
Series [ID] Construction:
├── [YYYY-YYYY]: [Subsource A] from [Source]
│   └── File: [path/to/source]
├── [YYYY-YYYY]: [Subsource B] from [Source]
│   └── Shaikh baseline data
└── [YYYY-YYYY]: [Subsource C] from [Source]
    └── API: [ENDPOINT]
```

---

## Extension Script (v2.2)

| Field | Value |
|-------|-------|
| Script Location | `Technical/scripts/series_extensions/extend_[ID].py` |
| Script Status | [EXISTS/MISSING] |
| Last Run | [YYYY-MM-DD HH:MM:SS UTC or N/A] |
| Run Result | [SUCCESS/FAILED/N/A] |

---

## Transformation Chain

| Step | Operation | Input | Output | Script | Transform ID |
|------|-----------|-------|--------|--------|--------------|
| 1 | [operation] | [input] | [output] | [script.py] | T### |
| 2 | [operation] | [input] | [output] | [script.py] | T### |

### Transformation Details

#### T###: [Operation Name]

**Formula**: 
```
[Mathematical formula or pseudocode]
```

**Parameters**:
- [param1]: [value]
- [param2]: [value]

**Notes**: [Any important notes about this transformation]

---

## Validation Record

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Value Range | [min-max] | [actual range] | PASS/FAIL |
| Year Coverage | [start-end] | [actual coverage] | PASS/FAIL |
| Missing Values | [expected %] | [actual %] | PASS/FAIL |
| Cross-reference | [reference] | [matches?] | PASS/FAIL |

### Validation Notes

[Any notes about validation results, edge cases, or known discrepancies]

---

## Known Issues

- [ ] **[Issue 1]**: [Description and impact]
- [ ] **[Issue 2]**: [Description and impact]

---

## Appendix References

| Appendix | Title | Tables | Relevance |
|----------|-------|--------|-----------|
| App X.Y | [Title from source book] | [Table IDs] | [How this appendix informs series construction] |

### Key Appendix Variables
- **[Variable Name]**: [Formula/definition from appendix]
- **[Variable Name]**: [Formula/definition from appendix]

### Appendix Methodology Notes
[Key methodology points from appendix that inform series construction]

---

## Data Revision History

| Source | Revision | Date | Impact | Series Affected |
|--------|----------|------|--------|-----------------|
| BEA | [Comprehensive/Annual] | [YYYY] | [HIGH/MEDIUM/LOW] | [Series IDs] |
| BLS | [Methodology Update] | [YYYY] | [HIGH/MEDIUM/LOW] | [Series IDs] |

### Original Data Vintage
- **Shaikh Data Vintage**: [YYYY]
- **Current Data Vintage**: [YYYY]

### Extension Implications
[Document how revisions affect data extensions and methodology updates]

### Methodology URLs
- [Source 1]: [URL to methodology documentation]
- [Source 2]: [URL to methodology documentation]

---

## Related Content

- **Figures**: [List of figures using this dataset]
- **Derived Series**: [List of series derived from this one]
- **Module**: [Module/chapter this belongs to]
- **Appendices**: [List of appendices informing this series]

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| [YYYY-MM-DD] | 1.0 | Initial creation |

---

*Data Provenance Record following Anu Standard v2.0*
