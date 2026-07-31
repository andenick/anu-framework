---
name: anu-variant
version: "1.4"
description: Track methodology variants across data series, documenting alternative construction approaches and their implications
when-to-use: User needs to track different methodology choices, compare variant approaches, or document alternative data construction methods
search-hints: "variant methodology alternative approach construction comparison track"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
argument-hint: "[action] [series_id]"
requires: none
part-of: Anu Framework v12.2
---

# Anu Variant Standard v1.4

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Variant |
| Version | 1.4 |
| Part Of | Anu Framework v12.2 |
| Created | 2026-02-26 |
| Purpose | Track multiple methodological variants with unique IDs and full provenance |

---

## Stage Position

**Floating** — `anu-variant` is not a numbered pipeline stage; it is invoked at any point in a build. In practice it runs alongside or after construction, because it operates on series that already have provenance records and computed outputs. (Earlier framework revisions described it as "post-pipeline".)

- **Upstream**: Complete pipeline (DPR/EPR, calculator scripts, Knowledge Base extractions)
- **Downstream**: Review (variant quality), research (methodology comparisons)
- **Adequacy Relevance**: Variants require the same L1/L3 sources as the base series plus additional methodology papers
- **Key Handoff**: `VARIANT_REGISTRY.json`; variant VPRs; comparison CSVs

---

## Purpose

Define a protocol for **tracking multiple methodological variants** of the same economic aggregate. Each variant receives a unique, machine-parseable ID and a complete Variant Provenance Record (VPR) documenting its methodology, parameters, data sources, and benchmarks.

### Key Differentiators

| Aspect | Before Anu Variant | After Anu Variant |
|--------|---------------------|-------------------|
| Variant Identity | Ad-hoc names ("tonak version", "moos approach") | **Canonical IDs**: `V-SW01-AS2`, `V-SW01-TON`, `V-SW01-MOO` |
| Parameter Tracking | Embedded in code comments | **Structured VPR** with parameter tables and justifications |
| Cross-Variant Comparison | Manual, inconsistent | **Standardized comparison protocol** with correlation matrices |
| Data Vintage Awareness | Implicit | **Explicit vintage tagging** and download logs |
| Registry | None | **Central JSON catalog** per project, indexed across workspace |
| Validation | Scattered print statements | **Benchmark tables** with pass/fail status per variant |

---

## When to Use

Use the Anu Variant Standard when:

- Calculating the same aggregate using different methodological choices (e.g., NSW with/without indirect taxes)
- Tracking sensitivity to vintage data (same method, different data releases)
- Validating against published benchmarks from different authors
- Comparing results across multiple profit rate, exploitation, or wage formulations
- Documenting why a particular variant was chosen as baseline

---

## Inputs

Prerequisites — everything that must already exist before a variant can be created:

1. **Anu Standard DPR/EPR Exists**: Underlying series documented via Anu Standard or Anu Extension
2. **Calculator Script**: Python script with a `VariantConfig` pattern (or equivalent parameterization)
3. **KB Extractions**: Methodology sources extracted for each variant author
4. **Output Data**: At least one computed CSV for the variant

Further inputs are consumed once tracking is under way:

| Input | Source | Required |
|-------|--------|----------|
| `Technical/VARIANT_REGISTRY.json` | Created by Step 1, read by every later step | After init |
| Published benchmark values | The variant author's own publication | Yes, for Step 6 validation |
| Vintage data (ALFRED / BEA NIPA Archives / Philadelphia Fed RTDSM) | External archives | Optional (Step 8) |

---

## Workflow

> This skill **does ship** the scripts the steps below invoke, under
> `skills/anu-variant/scripts/`: `variant_registry.py`,
> `validate_variant.py`, `generate_comparison.py`, and
> `vintage_downloader.py`. Invoke them by their real path, e.g.
> `python $ANU_FRAMEWORK/skills/anu-variant/scripts/validate_variant.py`.
> Only `vintage_downloader.py` needs a third-party package (`requests`) and
> a `FRED_API_KEY`; the other three are stdlib-only. What each script must
> do is the contract this SKILL.md defines — a project may substitute its
> own implementation, but the shipped ones are the reference.

### Step 1: Initialize Variant Tracking

```bash
python variant_registry.py init --project "[project_name]" \
    --registry-path Technical/VARIANT_REGISTRY.json
```

### Step 2: Define Variant ID

Follow the Variant ID Convention (see below). Assign a unique ID:

```
V-{DOMAIN}{METRIC_NUM}-{METHOD_CODE}
```

Example: `V-SW01-AS2` for Net Social Wage, AS2 baseline method.

### Step 3: Register Variant

```bash
python variant_registry.py register \
    --id V-SW01-AS2 \
    --name "Net Social Wage - AS2 Baseline" \
    --domain SW --metric SW01 --method AS2 \
    --baseline true \
    --config '{"include_indirect_taxes": true, "defense_share": 0.40}'
```

### Step 4: Create VPR

Create a Variant Provenance Record from template:

```
Technical/docs/variants/V-SW01-AS2_VPR.md
```

Fill all sections: methodology, parameters, formulas, data sources, benchmarks.

### Step 5: Compute Variant

Run the calculator for this variant and record output paths:

```bash
python calculate_nsw.py --variant as2
```

### Step 6: Validate Against Benchmarks

```bash
python validate_variant.py --id V-SW01-AS2 --registry Technical/VARIANT_REGISTRY.json
```

### Step 7: Cross-Variant Comparison

```bash
python generate_comparison.py --registry Technical/VARIANT_REGISTRY.json \
    --metric SW01 --output Technical/ANU_REPLICATOR/data/final-data/nsw_variant_comparison.csv
```

### Step 8: Download Vintage Data (Optional)

```bash
python vintage_downloader.py --series GDP CPIAUCSL --vintage 2024Q4 \
    --output Technical/data/vintages/
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-variant init` | Initialize variant registry for a project |
| `/anu-variant register` | Register a new variant with ID and config |
| `/anu-variant create-vpr` | Create VPR from template for a variant |
| `/anu-variant compute` | Compute a single variant |
| `/anu-variant compute-all` | Compute all variants for a metric |
| `/anu-variant compare` | Generate cross-variant comparison |
| `/anu-variant validate` | Validate variant against benchmarks |
| `/anu-variant download-vintage` | Download and catalog vintage data |
| `/anu-variant list` | List all registered variants |
| `/anu-variant status` | Show status of all variants (computed, validated, etc.) |
| `/anu-variant audit` | Full compliance audit of variant documentation |

---

## Variant ID Specification

### Format: `V-{DOMAIN}{METRIC_NUM}-{METHOD_CODE}`

```
V          = Variant prefix (distinct from S###, T###, Fig#.#)
DOMAIN     = 2-letter domain code
METRIC_NUM = 2-digit metric number within domain
METHOD     = 2-3 character method abbreviation (uppercase letters and digits)
```

### Parsing Rule

```python
import re
VARIANT_ID_PATTERN = re.compile(r'^V-([A-Z]{2})(\d{2})-([A-Z0-9]{2,3})$')
# Group 1: domain, Group 2: metric number, Group 3: method code
```

### Domain Codes (Extensible)

| Code | Domain |
|------|--------|
| `SW` | Social Wage |
| `PR` | Profit Rate |
| `EX` | Exploitation |
| `WG` | Wages |
| `CA` | Capital |
| `MP` | Market Prices |
| `IO` | Input-Output |

### Examples (from Shaikh-Tonak project)

| Variant ID | Domain | Metric | Method | Description |
|-----------|--------|--------|--------|-------------|
| `V-SW01-AS2` | Social Wage | NSW | AS2 baseline | Current project baseline |
| `V-SW01-TON` | Social Wage | NSW | Tonak | Excludes indirect taxes |
| `V-SW01-MOO` | Social Wage | NSW | Moos | Military exclusions, NIPA tables |
| `V-PR01-SHT` | Profit Rate | General | Shaikh-Tonak | VA / KNC |
| `V-PR01-MOH` | Profit Rate | General | Mohun | Alternative method |
| `V-PR01-TSP` | Profit Rate | General | Tsoulfidis-Paitaridis | Alternative method |
| `V-EX01-BAS` | Exploitation | Rate of exploitation | Baseline | Book-compatible |
| `V-EX01-MOH` | Exploitation | Rate of exploitation | Mohun | Mohun variant |

### Vintage Suffix (Metadata Qualifier)

Not part of the canonical ID. Used in filenames and metadata:

```
V-SW01-AS2@2024Q4    — produced with 2024 Q4 vintage data
V-SW01-AS2@2011V     — produced with 2011 vintage NIPA data
```

---

## VARIANT_REGISTRY.json Schema

```json
{
  "anu_variant_version": "1.0",
  "project": "<project_name>",
  "generated": "<ISO 8601>",
  "total_variants": "<int>",
  "domain_registry": {
    "<DOMAIN_CODE>": {
      "name": "<domain_name>",
      "metrics": {
        "<METRIC_CODE>": {
          "name": "<metric_name>",
          "formula": "<summary formula>"
        }
      }
    }
  },
  "variants": {
    "<VARIANT_ID>": {
      "variant_id": "<str>",
      "domain": "<str>",
      "metric": "<str>",
      "method_code": "<str>",
      "name": "<str>",
      "method_name": "<str>",
      "description": "<str>",
      "is_baseline": "<bool>",
      "config_parameters": { },
      "source_series": { },
      "nipa_tables_used": [ ],
      "output_files": { },
      "coverage": { "start_year": 0, "end_year": 0 },
      "benchmark_values": { },
      "linked_series": [ ],
      "calculator_script": "<path>",
      "calculator_class": "<str>",
      "calculator_instance": "<str>",
      "vpr_file": "<path>",
      "created": "<ISO date>",
      "last_computed": "<ISO date>",
      "data_vintage": "<str>"
    }
  },
  "cross_variant_comparisons": [ ],
  "vintage_tracking": { }
}
```

---

## Variant Provenance Record (VPR)

Each variant gets a VPR document (`V-{ID}_VPR.md`) with:

1. **Quick Reference** — ID, metric, method, domain, baseline status, coverage, vintage, validation
2. **Methodological Description** — What this variant computes, original author, key quotes
3. **Parameter Specification** — VariantConfig fields with values and justifications
4. **Data Sources** — NIPA series, tables, linked Anu Standard series
5. **Computation Formula** — Core formula, component decomposition, implementation reference
6. **Validation Against Published Benchmarks** — Sources, comparison table, correlation
7. **Cross-Variant Comparison** — Comparison with other variants of same metric
8. **Vintage Information** — Data vintage, historical vintages computed
9. **Known Issues and Limitations**
10. **Changelog**

Template: `templates/VPR_TEMPLATE.md`

---

## Cross-Variant Comparison Protocol

### Standard CSV Format

```
year, V-SW01-AS2_nsw, V-SW01-AS2_nsw_gdp, V-SW01-TON_nsw, V-SW01-TON_nsw_gdp, ...
```

### Required Analyses

1. **Correlation Matrix** — Pairwise correlations across all variants for the same metric
2. **Sign-Change Analysis** — Years where variants disagree on sign of the aggregate
3. **Summary Statistics** — Mean, std, min, max per variant
4. **Level Divergence** — Max absolute and percentage difference between variants per year
5. **Trend Comparison** — Do all variants agree on direction of change year-over-year?

### Comparison Report

Template: `templates/VARIANT_COMPARISON_TEMPLATE.md`

---

## Vintage Integration

### Download Workflow

1. Identify target series and vintage date
2. Download from ALFRED / BEA NIPA Archives / Philadelphia Fed RTDSM
3. Catalog in `VINTAGE_DOWNLOAD_LOG.json`
4. Tag variant computation with vintage identifier

### Tagging Convention

```
data_vintage: "2024Q4"       — BEA 2024 Q4 release
data_vintage: "2011V"        — 2011 comprehensive revision vintage
data_vintage: "ALFRED:2023-01-15"  — ALFRED snapshot date
```

### Vintage Report

Template: `templates/VINTAGE_REPORT_TEMPLATE.md`

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| `VARIANT_REGISTRY.json` | `Technical/` | Master catalog of every variant, its config parameters, source series, output paths, benchmarks and vintage |
| `V-{DOMAIN}{NUM}-{METHOD}_VPR.md` | `Technical/docs/variants/` | Variant Provenance Record — the 10 sections listed above, from `templates/VPR_TEMPLATE.md` |
| `{metric}_variant_comparison.csv` | `Technical/ANU_REPLICATOR/data/final-data/` | Cross-variant comparison in the standard year-indexed column format |
| Comparison report | Project-chosen path | Correlation matrix, sign-change analysis, summary statistics, level divergence, trend comparison — from `templates/VARIANT_COMPARISON_TEMPLATE.md` |
| `VINTAGE_DOWNLOAD_LOG.json` | `Technical/data/vintages/` | Catalog of downloaded data vintages |
| Vintage report | Project-chosen path | From `templates/VINTAGE_REPORT_TEMPLATE.md` |

This skill does not write `series_registry.json` or any series data file; variant outputs live in their own registry and directories.

### Output Structure

```
Project/Technical/
├── VARIANT_REGISTRY.json             # Master variant registry
├── docs/
│   └── variants/
│       ├── V-{DOMAIN}{NUM}-{METHOD}_VPR.md  # Per-variant provenance records
│       └── ...
├── data/
│   └── vintages/
│       └── VINTAGE_DOWNLOAD_LOG.json # Vintage download catalog
└── ANU_REPLICATOR/data/final-data/
    ├── {metric}_variant_comparison.csv  # Cross-variant comparison
    └── ...
```

---

## Integration with Anu Framework

| Component | Relationship |
|-----------|-------------|
| Anu Standard | VPR references DPR series IDs; variant registry links to series catalog |
| Anu Extension | VPR can reference EPR for extended variants; vintage tracking extends series coverage |
| Anu Extenbook | Extenbooks can be generated per-variant showing different methodological choices |
| Anu Review | Review protocol validates variant completeness; audit command checks all VPRs |

---

## Validation Checklist

For each registered variant:

- [ ] Variant ID follows `V-{DOMAIN}{METRIC}-{METHOD}` pattern
- [ ] Registry entry exists in `VARIANT_REGISTRY.json`
- [ ] VPR file exists and all sections are complete
- [ ] Config parameters match calculator script
- [ ] Output CSV files exist at registered paths
- [ ] Benchmark values documented with sources
- [ ] Cross-variant comparison includes this variant
- [ ] Calculator script and class linkage is valid
- [ ] Data vintage is recorded
- [ ] Exactly one variant per metric marked as baseline

---

## Acceptance Gates

A variant is accepted — i.e. may be cited, compared, or chosen as baseline — only when every item of the Validation Checklist above passes. Restated as gates:

| Gate | Condition |
|------|-----------|
| Identity | The ID matches `V-{DOMAIN}{METRIC}-{METHOD}` and parses under `VARIANT_ID_PATTERN`; a registry entry exists in `VARIANT_REGISTRY.json` |
| Documentation | The VPR file exists and all ten of its sections are complete |
| Code linkage | Config parameters match the calculator script; the calculator script and class linkage resolve |
| Data | Output CSV files exist at the registered paths, and the recorded data vintage is present |
| Validation | Benchmark values are documented with their sources, and the variant has been validated against them |
| Comparison | The cross-variant comparison for this metric includes this variant |
| Baseline discipline | Exactly one variant per metric is marked as baseline |

`anu-variant` publishes no pass/fail score of its own; the gate is the checklist, and `anu-review`'s audit command checks that every registered variant has a complete VPR.

---

## Anti-Patterns

- **DO NOT** name variants ad hoc ("the Tonak version", "the other approach"). Every variant gets a canonical, machine-parseable ID.
- **DO NOT** leave methodological parameters only in code comments — they belong in the VPR parameter table, with a justification per parameter.
- **DO NOT** mark more than one variant per metric as baseline, and do not leave a metric with no baseline.
- **DO NOT** compare or splice variants computed from different data vintages without recording the vintage on each — vintage is a metadata qualifier, never part of the canonical ID.
- **DO NOT** register a variant with no benchmark values or no output data; an unvalidated entry in the registry misrepresents the variant's status.
- **DO NOT** scatter validation results in print statements — benchmark tables with per-variant pass/fail status are the record.

---

## Anu Framework Context

- **Pipeline Stage**: Floating (see Stage Position above); operates on completed series
- **Upstream**: Complete pipeline (DPR/EPR, calculator scripts, Knowledge Base extractions)
- **Downstream**: Review (variant quality), research (methodology comparisons)
- **Adequacy Relevance**: Variants require the same L1/L3 sources as the base series plus additional methodology papers
- **Key Handoff**: VARIANT_REGISTRY.json; variant VPRs; comparison CSVs

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `VARIANT_REGISTRY.json`, `V-{DOM}{NN}-{MTH}_VPR.md`, variant comparison CSVs, `VINTAGE_DOWNLOAD_LOG.json` |
| **Expects** | `S###_DPR.md` or `S###_EPR.md`, calculator scripts, Knowledge Base extractions |
| **Must Update on Completion** | Update `VARIANT_REGISTRY.json` with new variant entries |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-26 | Initial release |
| 1.1 | 2026-03-08 | Fixed legacy paths (Technical/catalogs/ -> Technical/, Technical/ShinyApp/data/ -> ANU_REPLICATOR/data/final-data/) |
| 1.2 | 2026-03-15 | Generalized: replaced hardcoded project name with placeholder; labeled variant ID examples as project-specific; genericized file tree |
| 1.4 | 2026-04-07 | Version bump for Anu Framework v6.0 compatibility (format unchanged) |

---

## Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v12.2 - Multi-Methodology Tracking Framework*
