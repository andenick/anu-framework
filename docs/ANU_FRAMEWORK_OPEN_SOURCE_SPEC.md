# Anu Framework — Open Source Specification

**Version**: 1.0
**Date**: 2026-05-09
**Status**: Planning

## What is the Anu Framework?

The Anu Framework is an 18-skill framework for agent-driven data construction and empirical research projects that produces outputs reproducible without agents. It covers the full lifecycle from Knowledge Base extraction through interactive visualization and quality auditing.

## Full Repo Structure

```
anu-suite/
├── README.md                        # Framework overview
├── LICENSE                          # MIT
├── docs/
│   ├── ARCHITECTURE.md              # Full suite architecture
│   ├── DATA_INTEGRITY.md            # No synthetic data, no proxies, no lazy splices
│   ├── SERIES_ID_SPEC.md            # S{NNN} notation v2.0
│   └── PIPELINE_STAGES.md           # 10-stage pipeline
├── skills/
│   ├── anu-research/                # Mine KB for methodology
│   ├── anu-ingestion/               # Registry, decomposition, provenance
│   ├── anu-extension/               # Maximum-faithfulness extension
│   ├── anu-replicator/              # L##/P## reproduction package
│   ├── anu-chopped/                 # Machine-readable CSV format
│   ├── anu-extenbook/               # 4-sheet Excel workbooks
│   ├── anu-visualize/               # R Shiny + Plotly Dash
│   ├── anu-review/                  # 12-dimension quality audit
│   ├── anu-pipeline/                # Multi-stage orchestrator
│   ├── anu-variant/                 # Methodology variant tracking
│   ├── anu-ledger/                  # Artifact coverage tracking
│   ├── anu-adequacy/                # Pre-pipeline readiness gate
│   └── anu-architecture/            # Anu Architecture (8-phase research pipeline; renamed from anu-data)
├── standards/
│   ├── ANU_EXTENSION_STANDARD.md
│   ├── ANU_EXTENBOOK_STANDARD.md
│   └── ANU_REVIEW_REFERENCE.md
├── examples/
│   └── minimal_example/                 # Sanitized the reference project example (1 chapter)
└── schema/
    ├── series_registry.schema.json
    └── project_registry.schema.json
```

## Relationship to Anu Architecture Standalone

The Anu Framework imports Anu Architecture (formerly AnuData Architecture) as one of its 20 skills. Users can:
1. Use Anu Architecture standalone for original research (no Anu Framework needed)
2. Use the full Anu Framework for replication projects (anu-replicator + other skills)
3. Use both in the same project: Anu Replicator for published data replication, Anu Architecture for original empirical analysis

## What Gets Stripped

- All Arcanum workspace paths and structure
- Council/Druck internal infrastructure
- HDARP chunking/processing details (reference only, not included)
- Robin data platform specifics
- Personal API keys and configurations
- Project-specific data files

## What Stays

- All 20 skill SKILL.md files (sanitized)
- Data integrity constraints (no synthetic data, no proxies, no lazy splices)
- Series ID Specification v2.0
- Templates and scripts from skill directories
- Review reference and quality standards
- Pipeline stage documentation

## Reference Implementation

the reference project (Capitalism Data v2) is the reference implementation, replicating 113 data series from Shaikh (2016). A sanitized single-chapter example will be included.

## Next Steps

1. Create repo after Anu Architecture standalone is published
2. Sanitize all SKILL.md files
3. Extract templates and scripts
4. Create the reference project minimal example
5. Write comprehensive README linking to Anu Architecture

---

*Created 2026-05-09 as part of the NickyData → AnuData Architecture integration; AnuData → Anu Architecture rename 2026-05-15*
