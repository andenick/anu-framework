# Anu Framework — Open Source Specification

**Version**: 2.0
**Date**: 2026-06-10
**Status**: Shipped (describes the public `anu-framework` repository as released)

## What is the Anu Framework?

The Anu Framework is a **19-active-skill** framework (plus 2 deprecated redirect
stubs) for agent-driven data construction, empirical research, and reproducible
publication that produces outputs reproducible without agents. It covers the full
lifecycle from Knowledge Base extraction through interactive visualization and
quality auditing, orchestrated by `anu-build`.

## Public Repo Structure

```
anu-framework/
├── README.md                        # Framework overview (19 active skills, v12.2)
├── LICENSE                          # MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── docs/
│   ├── ANU_FRAMEWORK_OVERVIEW.md    # Complete architecture overview (v12.2)
│   ├── ANU_FRAMEWORK_GLOSSARY.md    # Canonical vocabulary
│   ├── SKILL_VERSION_MATRIX.md      # Per-skill version table
│   ├── SERIES_REGISTRY_SCHEMA.md    # Registry schema reference
│   ├── DATA_PROVENANCE_STANDARDS.md # DPR/EPR/FPR/VPR field specs
│   ├── GETTING_STARTED.md
│   └── … (standards, comparison, review reference, changelogs)
├── skills/
│   ├── anu-research/                # Stage 1 — mine KB for methodology
│   ├── anu-adequacy/                # Stage 2 — post-research readiness gate
│   ├── anu-ingestion/               # Stage 3 — registry, decomposition, provenance
│   ├── anu-extension/               # Stage 4 — maximum-faithfulness extension
│   ├── anu-scaffold/                # Stage 5 (sub) — generate L01/P02/V03 stubs
│   ├── anu-replicator/              # Stage 5 — L##/P##/V##/M## reproduction package
│   ├── anu-chopped/                 # Stage 6a — machine-readable CSV format
│   ├── anu-extenbook/               # Stage 6b — 4-sheet Excel workbooks
│   ├── anu-visualize/               # Stage 7 — R Shiny + Plotly Dash
│   ├── anu-publish/                 # Stage 8a — GitHub replication channel + web export
│   ├── anu-drive/                   # Stage 8b — Google Drive consumer package
│   ├── anu-archive/                 # Stage 8c — audit-grade transparency archive
│   ├── anu-review/                  # Floating — 14-dimension quality audit
│   ├── anu-docs/                    # Floating — per-series docs + Anu Explainer
│   ├── anu-variant/                 # Floating — methodology variant tracking
│   ├── anu-ledger/                  # Infra — artifact coverage tracking
│   ├── anu-architecture/            # Infra — 8-phase research format standard
│   ├── anu-doctor/                  # Infra — framework + project self-audit
│   ├── anu-build/                   # Orchestrator — 9-stage pipeline + cascade
│   ├── anu-pipeline/                # Deprecated stub → anu-build
│   └── anu-rebuild/                 # Deprecated stub → anu-build (mode=rebuild)
├── schemas/
│   └── series_registry.schema.json
├── tools/
│   ├── check_framework.py           # Clone-relative wrapper for anu-doctor
│   └── audit_publish.py
└── examples/
    └── mini-replication/            # Minimal worked example (INDPRO)
```

## Relationship to Anu Architecture Standalone

The Anu Framework imports Anu Architecture (formerly AnuData Architecture) as one
of its skills. Users can:
1. Use Anu Architecture standalone for original research (no Anu Framework needed) —
   available at [github.com/andenick/anu-architecture](https://github.com/andenick/anu-architecture).
2. Use the full Anu Framework for replication projects (anu-replicator + other skills).
3. Use both in the same project: Anu Replicator for published data replication, Anu
   Architecture for original empirical analysis.

## What Gets Stripped at the Publishing Boundary

Per the framework's own `anu-publish` scrub gates (P10/P11) and `anu-docs` DOC03,
the following are removed before any artifact crosses into outward-facing
distribution:

- Workspace-internal filesystem paths and directory structure
- Internal infrastructure / agent tooling names
- Extraction-pipeline chunking/processing internals (disclosable only as "PDF
  extraction via agent vision + OCR, errors possible")
- Private data-repository specifics
- Personal API keys and configurations
- Project-specific raw data files

## What Stays

- All active skill `SKILL.md` files (sanitized)
- Data integrity constraints (no synthetic data, no proxies, no lazy splices)
- Series ID Specification (current: v2.2 — canonical prefixes `D` primary / `XS` extra)
- Templates and scripts from skill directories
- Review reference and quality standards
- Pipeline stage documentation

## Reference Implementation

The reference implementation is a replication of Shaikh & Tonak's *Measuring the
Wealth of Nations* (1994) — 64 series, the first project built end-to-end on
`anu-build`. A sanitized minimal example ships at `examples/mini-replication/`.

---

*Originally drafted 2026-05-09 during the NickyData → AnuData Architecture
integration (AnuData → Anu Architecture rename 2026-05-15); updated 2026-06-10 to
describe the shipped v12.2 repository.*
