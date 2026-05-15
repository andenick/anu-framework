# The Anu Extension Standard: Maximum Faithfulness Data Extension Framework

**Version**: 2.0
**Created**: January 28, 2026
**Updated**: March 7, 2026
**Skill Location**: `skills/anu-extension/SKILL.md`
**Part Of**: Anu Framework v10.0
**Builds On**: Anu Ingestion v4.0, Anu Research v2.0
**Note**: This is a summary doc. The `anu-extension` skill is at v3.4 — see `SKILL_VERSION_MATRIX.md` and `anu-extension/SKILL.md` for the authoritative current spec.

---

## Summary

The Anu Extension Standard defines the methodology for extending historical data series with modern API data while maintaining maximum faithfulness to the original construction methodology. In Anu Framework v4.0, the Extension Standard defines the *methodology*; the Anu Replicator implements it in P## processing scripts.

## Ten Principles of Extension Faithfulness

1. **Understand Before Extending** — Complete Anu Research mining before any extension work
2. **Same Source Priority** — Prefer the exact same data source used by the original author
3. **Methodology Fidelity** — Apply identical transformations (reindexing, splicing, aggregation)
4. **Document Divergence** — Record any methodology changes between original and extension
5. **Validate at Splice** — Ensure smooth transition at the splice point
6. **Preserve Units** — Extension data must be converted to match original units
7. **Track Vintages** — Record the exact vintage date of all API data pulled
8. **Reference Values** — Validate against known-good values from the original data
9. **Graceful Degradation** — If extension data doesn't reach the present, document the gap
10. **Reproducibility** — All extension logic must be executable without agent intervention

## Key Changes in v2.0

- Extension config now lives in `series_registry.json` under each series' `extension` field
- Per-series extension scripts replaced by Anu Replicator P## processing scripts
- Prerequisites: Anu Ingestion v3.0 (registry, DPRs) and Anu Research v1.0 (research.json)
- EPRs reference research.json entries for methodology comparison
- Series IDs use v2.0 dash notation (S001-EXT, not S001_EXT)
- Vintage tracking integrated with LOAD_LOG.json

## Full Specification

See `skills/anu-extension/SKILL.md` for the complete standard with templates, workflow, and validation rules.

## Templates

| Template | Location |
|----------|----------|
| EPR | `anu-extension/templates/EPR_TEMPLATE.md` |
| Transition Analysis | `anu-extension/templates/TRANSITION_ANALYSIS_TEMPLATE.md` |
| Methodology Comparison | `anu-extension/templates/METHODOLOGY_COMPARISON_TEMPLATE.md` |
| Extension Certification | `anu-extension/templates/EXTENSION_CERTIFICATION_TEMPLATE.md` |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-28 | Initial Anu Extension Standard |
| 1.1 | 2026-02-03 | API Data Integration: live pulls, per-series scripts, year-source attribution |
| 2.0 | 2026-03-07 | Anu Framework v4.0: Replicator integration, registry-driven config, Research prerequisite, dash notation |

---

*Part of the Anu Framework v10.0 — Maximum Faithfulness Data Extension*
