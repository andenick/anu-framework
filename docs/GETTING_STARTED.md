# Getting Started with the Anu Framework

**Version**: 1.0
**Date**: May 2026

This guide walks you through applying the Anu Framework to a new data construction project — from Knowledge Base extraction through publication. It is generic and project-agnostic.

---

## Prerequisites

- An project workspace with the standard layout (Inputs/, Technical/, Outputs/)
- Source materials (PDFs, datasets, API access) for the data you want to construct
- Python 3.10+ with pandas, numpy, openpyxl, requests

---

## Step 1: Set Up Your Project

```
mkdir -p Inputs Technical Outputs
```

Organize source materials in `Inputs/` (read-only — never modify originals). If you have PDFs that need extraction, use HDARP (`<KB construction>` → `<KB construction>`).

## Step 2: Initialize the Pipeline

```
/anu-pipeline init [project_name]
```

This creates `Technical/PIPELINE_STATE.json` to track your progress through the 8 stages.

## Step 3: Research (Stage 1)

```
/anu-research mine-chapter [scope]
```

For each data series you want to construct, the Research skill mines your Knowledge Base for every quote, footnote, methodology description, and data source reference. Output: `S###_research.json` per series.

## Step 4: Adequacy Check (Stage 2)

```
/anu-adequacy [scope]
```

Verifies that your research uncovered sufficient information to construct all planned series. This is a gate — the pipeline blocks if adequacy is below 80%.

## Step 5: Ingestion (Stage 3)

```
/anu-ingestion create-registry [scope]
/anu-ingestion decompose [series_id]
```

Build `series_registry.json` — the single source of truth for all series definitions, subseries, construction steps, and metadata. Create decomposition documents for each series.

## Step 6: Extension Planning (Stage 4)

```
/anu-extension [scope]
```

For time-series data that can be extended to the present using public APIs (FRED, BEA, World Bank, etc.), define the extension methodology. Every extension must use the exact same source the original author used — no proxies.

## Step 7: Build the Replicator (Stage 5)

```
/anu-replicator init [project_name]
```

This scaffolds the self-contained reproduction package following Anu Architecture:

```
Technical/ANU_REPLICATOR/
+-- replicate.py              # Master orchestrator
+-- config/series_registry.json
+-- scripts/loading/           # L## scripts
+-- scripts/processing/        # P## scripts
+-- scripts/validation/        # V## scripts
+-- scripts/manual/            # M## scripts
+-- lib/                       # Shared utilities
+-- data/                      # Input → raw → final
```

Write L## loading scripts (one per data source) and P## processing scripts (one per series). Run `python replicate.py` to execute the full pipeline.

## Step 8: Quality Review (Floating)

```
/anu-review [scope]
```

Run quality audits at any stage — not just at the end. Early reviews catch issues before they compound. The review scores 12+ dimensions including research completeness, registry quality, extension faithfulness, and documentation.

## Step 9: Output Formats (Stage 6)

The pipeline automatically produces:
- **Anu Chopped CSVs**: Machine-readable format (Row 1 metadata, Row 2 IDs, Row 3+ data)
- **Anu Extenbooks**: Human-readable 4-sheet Excel workbooks (Data, Provenance, Research, Construction)

## Step 10: Visualization (Stage 7)

```
/anu-visualize init
```

Build an interactive Plotly Dash app for exploring the constructed data. Registry-driven — all labels, colors, and metadata come from `series_registry.json`.

## Step 11: Publish (Stage 8, Optional)

```
/anu-publish audit [project]
/anu-publish package [project] data+pipeline
/anu-publish validate [export_dir]
```

Scrub API keys, remove internal paths, generate README/LICENSE/CITATION.cff, validate for public release.

---

## Core Principles

1. **Every value must be real.** No synthetic data, no placeholders, no approximations, no frozen values.
2. **The registry is the source of truth.** All outputs derive from `series_registry.json`.
3. **Research before code.** Understand the methodology before writing scripts.
4. **Self-contained packages.** Anyone can clone, install, and reproduce.
5. **Audit early and often.** Don't wait until the end to run anu-review.

---

## Reference Implementation

**CD2** (Capitalism Data v2) is the reference implementation — 113 series, 97 scripts, 71 extensions. See `Projects/CD2/` in the Arcanum workspace.

---

*Part of the Anu Framework v10.0*
