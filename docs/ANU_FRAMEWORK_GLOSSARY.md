# Anu Framework Glossary

**Version:** 1.0
**Date:** 2026-05-13
**Location:** `docs/ANU_FRAMEWORK_GLOSSARY.md`
**Tagline:** *Single source of canonical definitions for all Anu Framework terminology.*

---

## How to Use This Glossary

Every term used across the Anu Framework — agent skills, internal artifacts, outward-facing packages — is defined exactly once here. When a skill, doc, or review mentions a term, it should match this glossary's definition without restatement. Cross-references use `[[double-bracket]]` notation. Acronyms point to their expansions.

**Related canonical documents:**
- [`SERIES_ID_SPECIFICATION.md`](./SERIES_ID_SPECIFICATION.md) — canonical series identifier grammar
- [`ANU_FRAMEWORK_OVERVIEW.md`](./ANU_FRAMEWORK_OVERVIEW.md) — framework architecture and skill map
- [`DATA_PROVENANCE_STANDARDS.md`](./DATA_PROVENANCE_STANDARDS.md) — provenance record specifications (sister doc)

---

## 1. Framework & Architecture

### Anu Framework
**Definition:** A 20-skill, multi-stage data-construction framework for replicating published economic series and extending them with public-API data under strict faithfulness rules.
**Example:** a reference Shaikh-replication project is the reference project for Anu Framework v11.
**Related:** [[Anu Architecture]] [[Anu Replicator]] [[Anu Pipeline]]

### Anu Pipeline
**Definition:** The master orchestrator that sequences 19 Anu skills through 8 stages (Adequacy through Publish) with quality review gates between stages.
**Example:** Running `/anu-pipeline status` on the reference project reports which series are at which stage.
**Related:** [[Anu Framework]] [[Quality Gate]] [[Anu Ledger]]

### Anu Architecture
**Definition:** A self-contained, language-agnostic eight-phase (S/L/P/V/M/A/O/E) folder standard for original econometric research, distinct from replication-only Anu Replicator packages. Renamed from "AnuData Architecture" in v11.0 (May 2026).
**Example:** A panel-data study with R scripts lives in `Technical/AnuArchitecture/`, while a Shaikh replication lives in `Technical/ANU_REPLICATOR/`. Legacy projects use `Technical/AnuData/`.
**Related:** [[Anu Replicator]] [[Pipeline Script]] [[project_registry.json]]

### Anu Replicator
**Definition:** A versioned, self-contained Python replication package with four phases (L## / P## / V## / M##) reproducible without agent intervention via a single `replicate.py` orchestrator.
**Example:** `<project>/Technical/replicator/` reproduces all 40+ the reference project series end-to-end.
**Related:** [[Anu Architecture]] [[L## Loading]] [[P## Processing]]

### Pipeline Stage
**Definition:** One of eight ordered Anu Pipeline phases — Adequacy, Research, Ingestion, Extension, Replicator, Output, Distribution, Review — with prerequisites enforced between adjacent stages.
**Example:** a project chapter 2 passed Adequacy (D0) before any `S###_research.json` was written.
**Related:** [[Quality Gate]] [[Anu Pipeline]]

### Series Registry
**Full name:** `series_registry.json`
**Definition:** The single machine-readable source of truth for every series, subseries, transform, extension, and unit in an Anu project; all output formats read from it.
**Example:** a reference project's registry at `Technical/series_registry.json` registers S001 with four subseries and a FRED INDPRO extension.
**Related:** [[Series ID]] [[Subseries]] [[DPR]]

---

## 2. Series Notation

### Series ID
**Definition:** Canonical identifier matching `S\d{3}(-[A-Z]|-EXT|-F|-COMBINED)?` that uniquely names a series, subseries, or derived column within a project.
**Example:** `S001` (US Industrial Production Index), `S017` (GDP per Capita), `S026` (Rate of Profit).
**Related:** [[Subseries]] [[Series Registry]]

### S###
**Definition:** A base series — the author's final published composite for that conceptual variable, after all subsource splicing and reindexing.
**Example:** `S001` is the final 1860–2010 spliced Industrial Production Index at 1958=100.
**Related:** [[Series ID]] [[Splice point]]

### S###-A, -B, -C…
**Full name:** Lettered Subseries
**Definition:** A component subseries of a base series, lettered A, B, C in temporal or construction order; raw subsources alternate with derived/reindexed forms.
**Example:** `S001-A` is BEA LTEG raw data; `S001-B` is `S001-A` reindexed to 1958=100.
**Related:** [[Subseries]] [[Reindexing]]

### S###-EXT
**Definition:** Raw extension data pulled from a modern public API in the API's native units, covering years past the original series' splice year.
**Example:** `S001-EXT` is FRED INDPRO monthly data aggregated to annual averages, native 2017=100.
**Related:** [[S###-F]] [[Extension]] [[Splice point]]

### S###-F
**Definition:** Extension data reindexed at the splice year so it overlays the last subsource of the original series on the same scale.
**Example:** `S001-F[t] = S001-D[2010] * (INDPRO[t] / INDPRO[2010])` continues 1958=100 past 2010.
**Related:** [[S###-EXT]] [[S###-COMBINED]] [[Reindexing]]

### S###-COMBINED
**Definition:** The final spliced series joining the original (S###) through the splice year with the reindexed extension (S###-F) afterward — the column a downstream user typically consumes.
**Example:** `S001-COMBINED` runs 1860–2025: Shaikh's data through 2010, FRED extension after.
**Related:** [[S###-F]] [[Splice point]]

### Subseries
**Definition:** Any non-final column belonging to a base series — either a raw subsource pulled from a single document, or a transform of another subseries.
**Example:** S001 has four subseries (S001-A through S001-D) plus the final S001 splice.
**Related:** [[S###-A, -B, -C…]] [[Series Registry]]

### Concurrent Series
**Definition:** Level-data numerator and denominator columns published alongside a ratio/rate series so consumers can recompute or audit the ratio.
**Example:** `CS026-N` (Net Operating Surplus) and `CS026-D` (Capital Stock) are the components of S026 Rate of Profit.
**Related:** [[CS###-N]] [[CS###-D]] [[ROP]]

### CS###-N
**Definition:** Concurrent-series numerator: the level-data top of a ratio series, exposed in the same chopped CSV with `is_component: true` and `component_type: "numerator"`.
**Example:** `CS026-N` is the Net Operating Surplus level series feeding S026.
**Related:** [[Concurrent Series]] [[CS###-D]]

### CS###-D
**Definition:** Concurrent-series denominator: the level-data bottom of a ratio series, with multi-ratio variants suffixed `-D2`, `-D3` when needed.
**Example:** `CS026-D` is the Capital Stock level series feeding S026.
**Related:** [[Concurrent Series]] [[CS###-N]]

### Reindexing
**Definition:** Rescaling a series so a chosen base year equals 100, preserving the growth-rate structure but changing the level.
**Example:** `S001-B[t] = S001-A[t] * (100 / S001-A[1958])` rebases BEA from 1913=100 to 1958=100.
**Related:** [[S###-A, -B, -C…]] [[Splice point]]

### Splice point
**Definition:** The year at which two subsource series are joined; the later series is rescaled to match the earlier at that year so growth rates carry across.
**Example:** S001 splices S001-B and S001-D at 1919; S001-COMBINED splices to FRED INDPRO at 2010.
**Related:** [[Reindexing]] [[S###-COMBINED]]

---

## 3. Provenance Records

### DPR
**Full name:** Data Provenance Record
**Definition:** Per-series markdown document at `Technical/docs/series/S###_DPR.md` listing subsources, year-source matrix, transformation chain, validation checks, and research references.
**Example:** `S001_DPR.md` documents BEA LTEG + FRB G.17 sources, the 1919 splice, and the 1958=100 base.
**Related:** [[EPR]] [[Decomposition]] [[Series Registry]]

### EPR
**Full name:** Extension Provenance Record
**Definition:** Per-series markdown at `S###_EPR.md` recording the extension API, splice year, splice method, methodology comparison, transition analysis, and a faithfulness assessment.
**Example:** `S001_EPR.md` documents the FRED INDPRO growth-rate splice at 2010 with r≈0.998 overlap correlation.
**Related:** [[DPR]] [[Faithfulness]] [[Concept Match Justification]]

### FPR
**Full name:** Figure Provenance Record
**Definition:** Per-figure provenance document mapping a published book figure to the constructed series, subseries, and replication script that reproduce it.
**Example:** A the reference project FPR links Shaikh's Figure 2.1 to S001 plotted from `reference-replicator/data/chopped/S001.csv`.
**Related:** [[DPR]] [[Anu Ingestion]]

### VPR
**Full name:** Variant Provenance Record
**Definition:** Structured record per Anu Variant documenting one methodological alternative — parameters, data sources, benchmarks, and a canonical variant ID such as `V-SW01-AS2`.
**Example:** Tonak's social-wage variant and Moseley's variant of the same aggregate each get distinct VPRs with parameter tables.
**Related:** [[Divergence Register]] [[Anu Variant]]

---

## 4. Data Construction Concepts

### Concept Match Justification
**Definition:** Written argument in an EPR explaining why a substituted modern series measures the same conceptual quantity as the original, required whenever the exact original source is unavailable.
**Example:** Justifying use of FRED INDPRO for FRB G.17 (identical underlying series, same agency) needs minimal text; substituting CPI for PPI is not allowed.
**Related:** [[Faithfulness]] [[Proxy]]

### Construction Step
**Definition:** One numbered transformation in a DPR's Transformation Chain (extract, reindex, splice, deflate, ratio) — the human-readable counterpart of a `transform` block in the registry.
**Example:** Step 2 of S001: "Reindex S001-A to 1958=100 via `S001-B[t] = S001-A[t] × (100 / S001-A[1958])`".
**Related:** [[DPR]] [[Reindexing]]

### Content Type
**Definition:** Classification of every series as `time_series`, `cross_sectional`, `theoretical`, or `derived`; only `time_series` is eligible for API extension.
**Example:** S001 (Industrial Production) is `time_series`; an input-output table is `cross_sectional` and is not extended.
**Related:** [[Extension]] [[Series Registry]]

### Divergence Register
**Definition:** Section of an Anu Variant comparison documenting where two variants disagree numerically and methodologically, with correlation matrices and benchmark tables.
**Example:** The divergence register for Rate of Profit variants reports the year-by-year gap between Shaikh, Tonak, and Moseley estimates.
**Related:** [[VPR]] [[Anu Variant]]

### Faithfulness
**Definition:** Degree to which an extension reproduces what the original methodology would have produced if applied to new data; scored Low / Medium / High in the EPR.
**Example:** S001 faithfulness is High because FRED INDPRO is literally the same FRB G.17 series the author used.
**Related:** [[EPR]] [[Concept Match Justification]]

### Proxy
**Definition:** A substitute series used when the exact original source is unavailable; must be flagged `"proxy": true` in the registry with a proxy-justification field. Wrong-concept proxies (CPI for PPI) are prohibited.
**Example:** Twelve of 58 the reference project's extensions were retroactively flagged for proxy violations and remediated.
**Related:** [[Concept Match Justification]] [[Faithfulness]]

### Decomposition
**Definition:** Per-series blueprint at `S###_DECOMPOSITION.md` describing every construction step before any code is written; the contract that L## and P## scripts must fulfill.
**Example:** `S001_DECOMPOSITION.md` specifies the four subseries, the 1919 splice, and the 1958 reindex base.
**Related:** [[DPR]] [[Construction Step]]

---

## 5. Pipeline Scripts

### L## Loading
**Definition:** Numbered Python script that acquires one or more raw subsources — from a public API, downloaded file, or extracted Knowledge Base table — and writes to `data/raw-data/`. Never modifies data.
**Example:** `L01_industrial_production.py` fetches FRED INDPRO and reads the BEA LTEG TA15 CSV.
**Related:** [[P## Processing]] [[Anu Replicator]]

### P## Processing
**Definition:** Numbered Python script that transforms one or more L## outputs into the final series via reindexing, splicing, deflation, or ratio computation; verifies the transform formula against stored data.
**Example:** `P01_industrial_production.py` reindexes S001-A to S001-B, then splices into S001 at 1919.
**Related:** [[L## Loading]] [[Construction Step]]

### V## Validation
**Definition:** Anu Architecture phase script dedicated to validating intermediate data against benchmarks, reference values, and dimensional-consistency rules before analysis.
**Example:** `V01_unit_checks.py` confirms ratios are dimensionless and levels match published book values within tolerance.
**Related:** [[Anu Architecture]] [[Quality Gate]]

### M## Manual adjustment
**Definition:** Script that applies one explicit, audited manual correction (e.g., overriding a single bad observation) to processed data, with the rationale logged in the AUDIT_MANIFEST.
**Example:** `M01_fix_1933_outlier.py` replaces a misprinted value with the documented correction from the author's errata.
**Related:** [[V## Validation]] [[Anu Architecture]]

### E## Exploration
**Definition:** Anu Architecture phase script preserving exploratory work — diagnostic plots, scratch regressions, sensitivity scans — whose conclusions flow to DECISION_LOG.md but whose outputs stay ephemeral.
**Example:** `E03_check_break_1973.py` tests for a structural break before A## fits the final model.
**Related:** [[Anu Architecture]]

### S/L/P/V/M/A/O/E Phases
**Definition:** The eight Anu Architecture phases — Source-spec, Loading, Processing, Validation, Manual, Analysis, Output, Exploration — run via numbered scripts and orchestrated through `run.py` or `run.R`.
**Example:** A panel-econometrics study uses all eight; a pure replication uses only L/P/V/M.
**Related:** [[Anu Architecture]] [[Anu Replicator]]

---

## 6. Document Tiers

### T1 Thin
**Definition:** Anu Docs tier for the minimum-viable per-series doc, auto-generated from registry metadata with no Knowledge Base reading. Scores 25–35 points.
**Example:** A `S034.md` whose methodology field reads "Construction steps from registry" with empty `kb_sources_searched`.
**Related:** [[T2 Adequate]] [[T3 Enriched]] [[Anu Docs]]

### T2 Adequate
**Definition:** Functional per-series doc with real methodology composed from DPR, EPR, and appendix text; the agent researcher field is `"agent"`, not `"auto-generated"`. Scores 55–70.
**Example:** A doc that explains the splice-and-reindex chain in prose, listing institutional provenance.
**Related:** [[T1 Thin]] [[T3 Enriched]]

### T3 Enriched
**Definition:** Gold-standard per-series doc adding direct author quotes, theoretical context, and connection to the source work's broader argument. Scores 85–100.
**Example:** An S001 doc quoting Shaikh's Appendix 2.1 on industrial-production methodology with a "From the Book" section.
**Related:** [[T2 Adequate]] [[Knowledge Base]]

---

## 7. Quality Gates

### D0 Adequacy Gate
**Definition:** Pre-research readiness check (Anu Adequacy) verifying that Knowledge Base, series definitions, data sources, construction logic, and validation data are sufficient to proceed; emits `ADEQUACY_REPORT.json`.
**Example:** a project chapter 6 passed D0 only after KB pages 220–245 were re-extracted from the source PDF.
**Related:** [[Anu Adequacy]] [[Knowledge Base]]

### D13 Authenticity Gate
**Definition:** Anu Review dimension auditing that no synthetic, placeholder, estimated, or randomly generated data exists in any series; any failure forces an INCOMPLETE certification.
**Example:** A single `np.random` call in a P## script automatically fails D13 and blocks publication.
**Related:** [[Anu Review]] [[Faithfulness]]

### D14 Outward-Facing Intelligibility
**Definition:** Quality dimension scoring whether external-facing artifacts (README, methodology PDF, per-series docs) use only public terminology, with internal jargon scrubbed at the packaging boundary.
**Example:** A doc referencing "DPR S001" fails D14; the same doc rewritten as "data provenance for the Industrial Production series" passes.
**Related:** [[External Disclosure Policy]] [[Anu Publish]]

### Quality Gate
**Definition:** Any binary pass/fail check the Anu Pipeline enforces between stages; a failed gate blocks the next stage until remediated.
**Example:** D0, D13, D14, plus per-skill gates such as Chopped V1–V13 validation rules.
**Related:** [[D0 Adequacy Gate]] [[D13 Authenticity Gate]] [[D14 Outward-Facing Intelligibility]]

---

## 8. Output Formats

### Chopped CSV
**Definition:** Anu Framework machine-readable CSV with Row 1 = column metadata (source, units, methodology excerpt), Row 2 = column IDs (`S001-A`, `S001`, `S001-COMBINED`), Row 3+ = numeric data with Year first.
**Example:** `data/chopped/S001.csv` exposes all four subseries plus base and combined columns in one file.
**Related:** [[Anu Chopped]] [[Series Registry]]

### Extenbook
**Definition:** Per-series Excel workbook with four sheets — Data, Provenance, Research, Construction — auto-generated from the registry, DPR, EPR, and research JSON.
**Example:** `S001_Extenbook.xlsx` shows every subsource as a column with reindex markers and splice rows highlighted.
**Related:** [[Anu Extenbook]] [[DPR]] [[Series Registry]]

### Drive Package
**Definition:** Consumer-facing Google Drive folder (Anu Drive) bundling a master multi-sheet workbook, individual Extenbooks, a LaTeX-compiled methodology PDF, and a plain-text README — zero-setup for non-technical scholars.
**Example:** `CD2_Drive_v1.0/` hands a colleague all 40+ series without GitHub or Python.
**Related:** [[Replicator Package]] [[Extenbook]]

### Replicator Package
**Definition:** The self-contained Anu Replicator deliverable — `loading/`, `processing/`, `validation/`, `data/`, `lib/`, `replicate.py`, `requirements.txt`, README — that reproduces all series from public APIs with no agent assistance.
**Example:** `<project>/Technical/replicator/` is a reference project's registry.
**Related:** [[Anu Replicator]] [[L## Loading]] [[P## Processing]]

---

## 9. Extraction & Sources

### Knowledge Base
**Definition:** Searchable, agent-readable extraction of book chapters, appendices, methodology PDFs, and footnotes — the ground truth against which all construction must be verified.
**Example:** the project KB at `knowledge_base/` contains chapter pages and historical methodology PDFs from BEA, BLS, and FRB.
**Related:** [[PDF Extraction]] [[Anu Research]]

### PDF Extraction
**Definition:** The process of converting source PDFs (book chapters, appendices, methodology documents) into searchable, agent-readable text plus structured tables, equations, and figures, using agent vision and/or OCR. For files larger than ~10 pages or 1 MB this is done chunk-by-chunk; small born-digital PDFs can be read directly without OCR. Extraction errors are always possible, so the published source remains authoritative.
**Example:** A full book is extracted chapter-by-chapter to populate the project Knowledge Base; a single born-digital methodology PDF is read directly.
**Related:** [[Knowledge Base]] [[Anu Research]]

---

## 10. Common Source Acronyms

### BEA
**Full name:** Bureau of Economic Analysis (U.S. Department of Commerce)
**Definition:** U.S. agency publishing the National Income and Product Accounts and historical Long Term Economic Growth tables.
**Example:** S001-A is drawn from BEA's 1966 *Long Term Economic Growth*, Table A-15.
**Related:** [[NIPA]] [[FRED]]

### NIPA
**Full name:** National Income and Product Accounts
**Definition:** BEA's headline accounting framework reporting GDP, income, consumption, investment, and saving at quarterly and annual frequency.
**Example:** Net Operating Surplus used in [[ROP]] series traces to NIPA Table 1.10.
**Related:** [[BEA]] [[NOS]]

### FRED
**Full name:** Federal Reserve Economic Data (St. Louis Fed)
**Definition:** Public time-series database aggregating thousands of macro and financial series; the default API for Anu extensions.
**Example:** `FRED_INDPRO_20260307.json` is the vintage-stamped pull powering `S001-EXT`.
**Related:** [[BEA]] [[Extension]]

### BLS
**Full name:** Bureau of Labor Statistics
**Definition:** U.S. agency publishing employment, earnings, productivity, and consumer/producer price indices.
**Example:** Wage and CPI series in a reference project's registry 5 are extended from BLS APIs.
**Related:** [[WPI]]

### OECD
**Full name:** Organisation for Economic Co-operation and Development
**Definition:** Intergovernmental publisher of cross-country macroeconomic, labor, and trade statistics used for international comparisons.
**Example:** Cross-country profit-rate scatter plots draw on OECD STAN industry data.
**Related:** [[PWT]]

### IRS SOI
**Full name:** Internal Revenue Service, Statistics of Income
**Definition:** U.S. tax-return-based statistics on corporate income, individual income, and capital stocks; primary source for several long-run profit-rate measures.
**Example:** Pre-1929 corporate-profits series in a reference project are reconstructed from IRS SOI annual reports.
**Related:** [[ROP]]

### PWT
**Full name:** Penn World Table
**Definition:** Cross-country panel of real GDP, capital stock, and prices using purchasing-power-parity exchange rates, maintained by the University of Groningen.
**Example:** PWT 10.0 supplies the [[PPP]]-adjusted capital stock for cross-country profit comparisons.
**Related:** [[Maddison Project]] [[PPP]]

### Maddison Project
**Full name:** Maddison Project Database
**Definition:** Long-run cross-country GDP-per-capita database (Bolt & van Zanden) extending Angus Maddison's historical estimates back to 1820 and earlier.
**Example:** Pre-1929 international GDP-per-capita comparisons in a reference project use Maddison Project 2020.
**Related:** [[PWT]] [[MeasuringWorth]]

### MeasuringWorth
**Definition:** Public historical-data project (Officer & Williamson) publishing long-run U.S. price indices, exchange rates, GDP, and interest rates back to 1774.
**Example:** Long-run U.S. WPI series in a project chapter 5 are spliced from MeasuringWorth's "Annual Wholesale Prices in the United States".
**Related:** [[WPI]]

### IO
**Full name:** Input-Output
**Definition:** Cross-sectional accounting framework describing inter-industry flows; classified `content_type: "cross_sectional"` and therefore not extended via API.
**Example:** BEA's 71-industry IO tables enter the reference project as point-in-time snapshots, never extended.
**Related:** [[Content Type]]

---

## 11. Methodological Terms

### IROP
**Full name:** Incremental Rate of Profit
**Definition:** The ratio of the change in profit to the change in capital stock over an interval — a marginal counterpart to the average rate of profit.
**Example:** Shaikh computes IROP series alongside ROP to distinguish marginal from average profitability.
**Related:** [[ROP]] [[NOS]]

### ROP
**Full name:** Rate of Profit
**Definition:** Ratio of a profit measure (Net Operating Surplus, corporate profits) to a capital stock measure; central explanatory variable in Shaikh's framework.
**Example:** S026 in a reference project is a U.S. rate-of-profit series 1947–2024 with `CS026-N` (NOS) and `CS026-D` (capital stock) as concurrent components.
**Related:** [[NOS]] [[CS###-N]] [[CS###-D]] [[IROP]]

### HP-filter
**Full name:** Hodrick-Prescott filter
**Definition:** Two-sided smoother decomposing a time series into trend and cyclical components; smoothing parameter λ controls trend rigidity.
**Example:** `HP(100)` denotes the filter with λ=100, the standard choice for annual data.
**Related:** [[HP(100)]]

### HP(100)
**Definition:** Hodrick-Prescott filter applied at λ=100, the convention for annual macroeconomic series.
**Example:** Trend rate of profit in a reference project is computed as `HP(100)` of S026.
**Related:** [[HP-filter]]

### NOS
**Full name:** Net Operating Surplus
**Definition:** NIPA accounting concept measuring business sector profits net of capital consumption but before interest and tax — the numerator of the standard rate of profit.
**Example:** `CS026-N` is the NOS series from NIPA Table 1.10 feeding the S026 profit-rate computation.
**Related:** [[NIPA]] [[ROP]]

### WPI
**Full name:** Wholesale Price Index
**Definition:** Historical price index of producer goods at wholesale, the predecessor to the modern Producer Price Index (PPI) before 1978.
**Example:** S010 long-run U.S. WPI 1774–2020 splices MeasuringWorth historical WPI with BLS PPI after 1913.
**Related:** [[BLS]] [[MeasuringWorth]]

### PPP
**Full name:** Purchasing Power Parity
**Definition:** Conversion of national-currency values to a common unit using price-level ratios rather than market exchange rates, enabling real cross-country comparison.
**Example:** PWT's `rgdpe` series reports GDP in 2017 international dollars at PPP.
**Related:** [[PWT]] [[OECD]]

---

## External Disclosure Policy

The following rule governs every artifact that crosses the packaging boundary into outward-facing distribution (GitHub publish, Drive package, public methodology PDF, README files, per-series docs visible to outside scholars):

> External-facing packages refer to content by its public name. Quote the book directly. Cite public data by its public source (FRED, BEA, BLS, OECD). The PDF-extraction step may be honestly disclosed as the method by which book text and tables were captured, with the caveat that extraction errors are possible. All other workspace-internal nomenclature is scrubbed at the packaging boundary.

**Scrubbed at the boundary (internal-only):** internal tooling/agent names, internal OCR-engine names, extraction chunk identifiers, batch numbers, workspace-internal filesystem paths, and raw Knowledge Base filenames.

**Allowed in external artifacts:** Series IDs (S###, CS###-N/D, -EXT, -F, -COMBINED), public source names (BEA, NIPA, FRED, BLS, OECD, IRS SOI, PWT, Maddison Project, MeasuringWorth), methodological terms (ROP, IROP, HP(100), NOS, WPI, PPP), direct author quotes, public URLs.

**Honest-disclosure exceptions:** A `METHODS_AND_LIMITATIONS.md` or equivalent section may disclose that data and methodology were extracted from PDFs via agent-vision-plus-OCR, with the explicit caveat that extraction errors are possible and the published source is authoritative.

See [[D14 Outward-Facing Intelligibility]] and [[Anu Publish]] for enforcement.

---

## Cross-References

- [`SERIES_ID_SPECIFICATION.md`](./SERIES_ID_SPECIFICATION.md) — canonical grammar for every series ID in this glossary
- [`ANU_FRAMEWORK_OVERVIEW.md`](./ANU_FRAMEWORK_OVERVIEW.md) — skill catalog, stage diagram, and architectural rationale
- [`DATA_PROVENANCE_STANDARDS.md`](./DATA_PROVENANCE_STANDARDS.md) — full specification of DPR, EPR, FPR, VPR field structures (sister document)

---

*Anu Framework v10 — Glossary v1.0 — 2026-05-13*
