# Data Provenance Standards v1.0

**Version:** 1.0
**Date:** 2026-05-13
**Location:** `docs/DATA_PROVENANCE_STANDARDS.md`
**Purpose:** Single canonical spec for the three provenance-record types used across all Anu Framework projects.

> Three record types document the origin, transformation, and replication of every series, extension, and figure in an Anu Framework project. DPR records the construction; EPR records the extension; FPR records how series become figures. A fourth, the VPR, lives under `anu-variant` and is summarized at the end of this document.

---

## Conventions

- **File location.** Series-level records live under `{Project}/Technical/docs/series/`. Figure records live under `{Project}/Technical/docs/figures/`.
- **Naming.** `S###_DPR.md`, `S###_EPR.md`, `Fig{N.M}_FPR.md`. Examples (from the reference project): `S001_DPR.md`, `S038_EPR.md`, `Fig10.1_FPR.md`.
- **Format.** Markdown with a leading H1 and a Quick Reference table.
- **Authoring.** DPRs are written by `anu-ingestion`. EPRs are written by `anu-extension`. FPRs are written by `anu-ingestion` or `anu-visualize` when a figure is registered.
- **Linkage.** Every DPR links to its decomposition and research JSON. Every EPR links back to its DPR. Every FPR links to the DPRs of the series it visualizes.
- **External disclosure.** Internal records may use internal vocabulary; when content from any record is rendered in an external artifact (methodology PDF, codebook, Drive package README), it must be translated to public names. See [External Disclosure Policy](#external-disclosure-policy).

---

## DPR — Data Provenance Record

**Purpose.** Documents the construction of a single series from its original published sources through to the final replicated values. The DPR answers: *where did this series come from, what was done to it, and how do I verify the result?*

### File-naming convention
`{Project}/Technical/docs/series/S###_DPR.md` — one file per series.

### Mandatory fields

| Field | Type | Description |
|---|---|---|
| Series ID | string | Canonical `S###` identifier |
| Series Name | string | Plain-language name as it appears in the book and in figures |
| Chapter | int | Chapter number in the source publication |
| Figures | array | Figure IDs the series feeds (e.g., `Fig 2.1`, `Fig 10.1`) |
| Year Range | string | Original range from the publication, and extended range if applicable |
| Source Citation | array | Each underlying source with full bibliographic citation |
| Source URL | array | Public URL for each source |
| Units | string | Final series units (e.g., `Index 1958=100`, `percent`, `ratio`) |
| Construction Methodology | prose | Step-by-step transformation chain (load → reindex → splice → final) |
| Reference Values | table | At least 3 (year, expected value, tolerance) for V01 validation |
| Subsource Breakdown | table | One row per subseries (S###-A, S###-B, …) with source, period, base, role |
| Year-Source Matrix | table | Which subseries covers which years |
| Research File | path | Pointer to `Technical/research/S###_research.json` |
| Decomposition | path | Pointer to `Technical/docs/series/S###_DECOMPOSITION.md` |
| Last Updated | date | ISO date of last meaningful edit |

### Optional fields
- **Splice Points** — explicit year, method (`growth_rate` or `direct`), and pre/post overlap correlation.
- **Known Issues** — documented divergences, missing years, classification changes.
- **Verbatim Source Text** — direct quote from the publication's appendix or methodology section.

### Worked example (compressed from `the reference project/Technical/docs/series/S001_DPR.md`)

```markdown
# Data Provenance Record: S001 — US Industrial Production Index

## Quick Reference
| Field | Value |
|-------|-------|
| Series ID | S001 |
| Name | US Industrial Production Index |
| Chapter | 2 |
| Figures | Fig 2.1 |
| Year Range | 1860–2010 (Shaikh); 1860–2025 (extended) |
| Units | Index 1958=100 |

## Subsources
| Subsource ID | Source | Period | Base/Units | Role |
| S001-A | BEA Long-Term Economic Growth, Table A15 | 1860–1918 | 1913=100 | Primary, early |
| S001-B | S001-A reindexed | 1860–1918 | 1958=100 | Derived |
| S001-C | Federal Reserve G.17 Industrial Production Index | 1919–2010 | 2017=100 | Primary, late |
| S001-D | S001-C reindexed at 1919 | 1919–2010 | matches S001-B | Derived |
| S001 | splice(S001-B, S001-D) at 1919 | 1860–2010 | 1958=100 | Final |

## Reference Values
| Year | Expected | Tolerance |
| 1929 | 8.7 | 1% |
| 1958 | 100.0 | 0.5% |
| 2010 | 93.1 | 1% |
```

### Validation rules
- The DPR is **complete** when every row in the subsource table has a non-empty `Source` and `Period`.
- The DPR is **verifiable** when its reference-value table has ≥ 3 entries and at least one falls in the original book's period (not just the extension period).
- The DPR is **enriched** (T3) when it includes a Verbatim Source Text excerpt and a Year-Source Matrix.

---

## EPR — Extension Provenance Record

**Purpose.** Documents the methodology and provenance for extending a series beyond its original publication range. The EPR answers: *how was this series extended, why is the chosen API faithful to the original source, and what divergences should the reader know about?*

A **No-Extension EPR** documents the deliberate decision to leave a series at its original range. It is written when extension is theoretically possible but methodologically inappropriate.

### File-naming convention
`{Project}/Technical/docs/series/S###_EPR.md` — written only for series with `extension.status` ≠ `null`.

### Mandatory fields

| Field | Type | Description |
|---|---|---|
| Series ID | string | Canonical `S###` |
| Original Range | `[start, end]` | Range covered by the original source |
| Extension Range | `[start, end]` or "NOT EXTENDED" | Range added by the extension |
| Extension API/Source | string | The exact public source (e.g., `FRED INDPRO`, `BEA NIPA Table 1.14`) |
| Concept Match Justification | prose | Why the API series measures the same concept as the original |
| Splice Method | enum | `growth_rate`, `direct`, or `composite` |
| Splice Year | int | Year at which old and new series are joined |
| Faithfulness Assessment | enum + prose | `high` / `medium` / `low` plus rationale |
| Known Divergences | table | Each divergence: scope, magnitude, mitigation |
| Reference Values | table | At least 2 values from the extended range |

### Optional fields
- **Splice Quality Metrics** — overlap correlation, discontinuity (σ), pre/post growth-rate comparison.
- **Verbatim Source Text** — quote from the publication's appendix describing the original construction.
- **Alternatives Investigated** — when present, a table of API/source candidates considered and rejected.

### Concept Match Justification — what it is and how to write it

**Definition.** A short argument that the extension API measures the *same underlying economic concept* as the original source, not merely a correlated proxy.

**Positive example.** *"FRED INDPRO is the same underlying Federal Reserve G.17 Industrial Production series Shaikh used. The data and methodology are unchanged; only the host platform differs. Concept match is exact."*

**Negative example (what NOT to do).** *"BLS earnings used as proxy for compensation because both are wage-related."* — earnings exclude employer-paid benefits and payroll taxes; compensation includes them. The concepts diverge by ~20 % in level. This would be a wrong-concept proxy and must be flagged in the `series_registry.json` with `"proxy": true` and a `"proxy_justification": "..."` field per the Anu Framework rule (no-proxy mandatory).

### No-Extension EPR worked example (compressed from `the reference project/Technical/docs/series/S038_EPR.md`)

```markdown
# Extension Provenance Record: S038

## Quick Reference
| Series ID | S038 |
| Series Name | OECD Industry IROP Deviations (PPP-adjusted) |
| Original Range | 1988–2003 |
| Extension Status | NOT EXTENDED |

## Non-Extension Decision

### Why No Extension
S038 relies on two data sources no longer available in compatible form:

1. **OECD STAN (2003 edition):** Industry classification changed from ISIC Rev.3 to ISIC Rev.4. Direct continuation introduces classification noise.
2. **PWT 6.2 PPP exchange rates:** PWT 10.01 uses revised methodology (expenditure-side vs output-side); PPP values differ materially.

### Alternatives Investigated
| Alternative | Why Rejected |
| OECD STAN 2025 + PWT 10.01 | ISIC and PPP methodology changes create discontinuities |
| EU KLEMS | EU-only; Shaikh's analysis spans USA, Japan, Canada, Australia, Korea |

### Decision Record
Per Anu Extension Standard Principle 10 (FAIL ON UNCERTAINTY): when no faithful extension is possible, the series is frozen rather than extended with degraded methodology.
```

### Validation rules
- An EPR is **complete** when Concept Match Justification, Splice Method, and Splice Year are all populated (or the EPR is a No-Extension EPR with a Decision Record).
- An EPR is **verifiable** when Reference Values from the extended range exist and are testable against V01.
- Every series with `extension` ≠ `null` in `series_registry.json` MUST have an EPR. Missing EPRs are flagged by `anu-ledger`.

---

## FPR — Figure Provenance Record

**Purpose.** Documents the mapping between a book's figure and the constructed data that produces it. The FPR answers: *which series feed this figure, where in the chopped CSV are they, and how do I redraw the chart faithfully?*

### File-naming convention
`{Project}/Technical/docs/figures/Fig{N.M}_FPR.md` — one file per figure registered in `series_registry.json#figures`.

### Mandatory fields

| Field | Type | Description |
|---|---|---|
| Figure ID | string | Canonical `Fig{N.M}` (e.g., `Fig2.1`, `Fig10.1`) |
| Chapter | int | Source-publication chapter |
| Page | int | Page in the source publication |
| Caption | string | Verbatim caption from the publication |
| Type | enum | `time_series`, `scatter`, `bar`, `composite`, `cross_sectional` |
| Constituent Series | array | Series IDs feeding this figure |
| Period | string | Year range shown in the figure |
| Replicator Output | path | Path to the figure CSV under `data/final-data/figures/` |
| Data Columns | table | One row per plotted column: name, source series, subseries, label, units |
| Axes | table | X and Y axis labels, scales, ranges |
| Data Sources | array | Public sources used (cited by public name) |

### Optional fields
- **Theoretical Significance** — short prose: what the figure argues, how the data supports the argument. Cited from the publication.
- **Verbatim Caption Text** — direct quote.
- **Cross-References** — DPR/EPR paths for constituent series, and any companion figures.

### Worked example (compressed from `the reference project/Technical/docs/figures/Fig10.1_FPR.md`)

```markdown
# Figure Provenance Record: Fig10.1 — Bank vs Private IROP

## Quick Reference
| Figure ID | Fig10.1 |
| Chapter | 10 |
| Page | 462 |
| Caption | Incremental Rates of Profit: Banks vs All Private Industries |
| Type | time_series |
| Series | S050 |
| Period | 1988–2005 |
| Replicator Output | data/final-data/figures/Fig10.1.csv |

## Data Columns
| Column | Series | Subseries | Label | Units |
| year | S050 | — | Year | — |
| bank_irop | S050 | S050-A | Banking industry IROP | Rate (decimal) |
| private_irop | S050 | S050-B | All-private industry average IROP | Rate (decimal) |

## Data Sources
- BEA GDP-by-Industry tables (NAICS): https://apps.bea.gov/iTable/
- BEA Wealth Tables 3.1ES, 3.4ES, 3.7ES, 3.8ES

## Cross-References
- DPR: Technical/docs/series/S050_DPR.md
```

### Validation rules
- An FPR is **complete** when every plotted column has a non-empty Source Series and Subseries (or `—` if direct from registry).
- An FPR is **publishable** when its `Data Sources` block cites every public source by its public name with a URL.
- Every figure listed in any series' `figures` array in `series_registry.json` MUST have an FPR. Missing FPRs are flagged by `anu-ledger`.

---

## VPR — Variant Provenance Record (brief)

The Variant Provenance Record lives under the `anu-variant` skill and tracks alternative calculation methodologies for series where the publication itself presents multiple variants (e.g., conventional vs Marxian profit rates, gross vs net IROP).

A VPR captures: variant ID, parent series ID, canonical methodology, divergence from parent, implications for downstream figures, decision rationale for choosing the canonical version.

VPRs are stored under `{Project}/Technical/docs/variants/V###_VPR.md`. See `anu-variant/SKILL.md` for the full spec.

---

## External Disclosure Policy

The user's rule for outward-facing artifacts:

> External-facing packages refer to content by its public name. Quote the book directly. Cite public data by its public source (FRED, BEA, BLS, OECD). The PDF-extraction step may be honestly disclosed as the method by which book text and tables were captured, with the caveat that extraction errors are possible. All other workspace-internal nomenclature is scrubbed at the packaging boundary.

**How DPR / EPR / FPR honor this rule:**

- **Internally** (in `Technical/docs/series/`, `Technical/docs/figures/`), records may use internal vocabulary: `KB`, extraction-pipeline names, project codenames, internal infrastructure references, internal-only acronyms. This is the working language of the agent team.
- **At the packaging boundary** (when content from a DPR/EPR/FPR is rendered into a methodology PDF, codebook, README, or Drive package), all internal terms must be translated:
  - "KB" → "the book" or "the publication"
  - extraction-pipeline names → may be retained as "PDF extraction" with the caveat *"text and tables were extracted from the source PDF via a multi-engine extraction protocol; extraction errors are possible and are flagged in the per-series documentation"*
  - internal infrastructure names / project codenames → removed entirely; replaced with the underlying public source
  - "Chopped CSV" → "the machine-readable data file"
  - "Extenbook" → "the Excel workbook"
  - "S###-A", "S###-EXT" notation → retained but explained at first use with a Series ID legend
- This translation happens in `anu-publish` and `anu-drive` skills, which scrub at the packaging step.

---

## Cross-references

- [[ANU_FRAMEWORK_GLOSSARY]] — canonical term definitions, including DPR / EPR / FPR / VPR entries.
- [[SERIES_REGISTRY_SCHEMA]] — JSON Schema for the registry that drives all three record types.
- [[SERIES_ID_SPECIFICATION]] — canonical series-ID notation (`S###`, `-A`, `-EXT`, etc.).
- [[ANU_FRAMEWORK_OVERVIEW]] — the 16-skill framework these records support.
- `anu-ingestion/SKILL.md` — the skill that produces DPRs and FPRs.
- `anu-extension/SKILL.md` — the skill that produces EPRs.
- `anu-review/SKILL.md` — the audit framework that validates D5 (DPR coverage), D6 (EPR coverage), and figure mapping.

---

*Part of Anu Framework v10.0. First published 2026-05-13.*
