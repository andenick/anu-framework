# [ADR-###]: [Divergence Title] - Anu Divergence Record

## Quick Reference

| Property | Value |
|----------|-------|
| Divergence ID | ADR-### |
| Title | [Short descriptive title] |
| Category | [source_methodology_change / coverage_change / classification_change / base_year_change / discontinuity / definition_change] |
| Series Affected | [S###, S###, ...] |
| Figures Affected | [Fig#.#, ...] |
| Chapter(s) | [#, #, ...] |
| Discovery Date | [YYYY-MM-DD] |
| Discovered By | [Agent/Model] |
| Status | [pending_decision / accepted / adjusted / flagged / rejected] |

---

## Discovery Context

### When Discovered

[Describe when and during what process this divergence was discovered]

### How Discovered

[Describe how this divergence was identified - methodology comparison, transition analysis, etc.]

### Source Documentation

| Document | Location | Relevant Section |
|----------|----------|------------------|
| [Original methodology doc] | [HDARP path] | [Section/page] |
| [Current methodology doc] | [HDARP path] | [Section/page] |

---

## Nature of the Divergence

### Description

[Detailed description of what changed between original and current methodology]

### Original Methodology

> "[Quote from original methodology documentation]"
> 
> — [Source, Page]

[Explanation of how data was calculated/collected in the original period]

### Current Methodology

> "[Quote from current methodology documentation]"
> 
> — [Source, Page]

[Explanation of how data is calculated/collected currently]

### Key Difference

[Concise statement of the specific methodological difference]

---

## Impact Assessment

### Quantified Impact

| Metric | Value |
|--------|-------|
| Level Discontinuity | [X.XX percentage points or %] |
| Direction | [Extension higher/lower than historical] |
| Affected Period | [YYYY-YYYY] |
| Transition Year | [YYYY] |

### Impact on Analysis

[How does this divergence affect the economic interpretation or analysis using this series?]

### Shaikh Context

[What did Shaikh say about this data? Does the book's analysis depend on the original methodology?]

> "[Relevant quote from Shaikh about this data or methodology]"
> 
> — Shaikh (2016), Chapter [#], p. [###]

---

## Resolution Options

### Option 1: Accept As-Is

**Description**: Accept the divergence with documentation. Extension proceeds using current methodology.

**Pros**:
- [Advantage]
- [Advantage]

**Cons**:
- [Disadvantage]
- [Disadvantage]

**Implementation**: No adjustment needed. Document in EPR with clear warning.

---

### Option 2: [Alternative Approach]

**Description**: [Describe the adjustment or alternative]

**Pros**:
- [Advantage]

**Cons**:
- [Disadvantage]

**Implementation**: [Steps to implement this option]

---

### Option 3: [Another Alternative]

**Description**: [Describe another option if applicable]

**Pros**:
- [Advantage]

**Cons**:
- [Disadvantage]

**Implementation**: [Steps to implement]

---

## Researcher Decision

### Status: [PENDING / RESOLVED]

### Decision

- [ ] **Accept as-is** - Proceed with documented divergence
- [ ] **Adjust** - Apply specific adjustment (specify below)
- [ ] **Flag** - Warn users but no adjustment
- [ ] **Reject** - Cannot extend this series faithfully
- [ ] **Other** - Custom resolution (specify below)

### Decision Rationale

[Researcher's explanation of why this decision was made]

### Decision Date

[YYYY-MM-DD]

### Decision By

[Researcher name or identifier]

---

## Resolution Applied

### Adjustment Details (if applicable)

[Describe any adjustment applied]

### Updated EPR Files

| File | Update Applied |
|------|----------------|
| [S###_EPR.md] | [What was updated] |

### User Warnings

[Text to include in documentation warning users of this divergence]

---

## Related Documentation

### EPR Files

- [S###_EPR.md](path/to/EPR)

### EXTENSION_LOG Entry

```json
{
  "extension_id": "EXT###",
  "divergence_refs": ["ADR-###"]
}
```

### Web Research

| Source | Date | Finding |
|--------|------|---------|
| [URL] | [Date] | [Relevant finding] |

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [YYYY-MM-DD] | [Agent] | Initial divergence record |
| | | | |

---

*Generated following Anu Extension Standard v1.0*
*Anu Divergence Record Template*
