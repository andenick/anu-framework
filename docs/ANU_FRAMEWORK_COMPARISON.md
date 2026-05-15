# How the Anu Framework Compares to Other Standards

**Version**: 1.0
**Date**: May 2026

This document maps the Anu Framework's capabilities against the major reproducible research standards in economics and data science.

---

## Feature Comparison Matrix

| Feature | Project TIER 4.0 | Gentzkow-Shapiro | AEA Data Editor | FAIR | dbt | Anu Framework |
|---------|-----------------|------------------|-----------------|------|-----|---------------|
| **Folder structure standard** | Prescribed hierarchy | Flexible, principles-based | README must document | N/A | Convention-based | Anu Architecture (8-phase) |
| **Master script** | Required | Recommended | Required | N/A | `dbt run` | `replicate.py` |
| **Relative paths** | Required (v4.0) | Recommended | Required | N/A | Built-in | `lib/paths.py` (all relative) |
| **Data provenance** | README documentation | Not formalized | Data Availability Statement | R1.2 (detailed provenance) | Model docs | DPR + EPR per series |
| **Automated testing** | Not required | "Write tests" | Verification by data editor | N/A | `dbt test` | V## scripts (8 checks) |
| **Quality audit** | Not formalized | Not formalized | Editor review | N/A | Not formalized | anu-review (12+ dimensions) |
| **Registry-driven** | No | No | No | No | Yes (schema.yml) | Yes (series_registry.json) |
| **No synthetic data** | Not explicit | Not explicit | Implied | N/A | N/A | Explicit, mandatory, enforced |
| **Extension methodology** | N/A | N/A | N/A | N/A | N/A | anu-extension (faithful extension standard) |
| **Data lineage graph** | No | No | No | Provenance metadata | DAG auto-generated | Script Dependencies + registry |
| **Hash integrity** | No | No | No | N/A | No | V08 (SHA-256 all files) |
| **Multi-format output** | No | No | No | I1 (standard formats) | No | Chopped CSV + Extenbook Excel |
| **Visualization** | No | No | No | N/A | No | anu-visualize (Dash/Shiny) |
| **Publication pipeline** | No | No | Submission checklist | F1, A1 (DOI, access) | No | anu-publish (scrub, validate, package) |
| **Containerization** | No | No | Encouraged | N/A | Docker optional | Dockerfile template |
| **Persistent identifiers** | No | No | DOI encouraged | F1 (required) | No | Zenodo/Dataverse at publication |
| **License** | Not required | Not required | Required | R1.1 (required) | MIT | MIT or CC-BY-4.0 |
| **Machine-readable metadata** | No | No | README only | F2 (required) | schema.yml | series_registry.json |

---

## What the Anu Framework Does That Others Don't

### 1. Anti-Fabrication Absolutism
No standard explicitly prohibits synthetic data, proxy substitution, or lazy splices the way the Anu Framework does. Most standards focus on documenting what was done; Anu Framework prescribes what may NOT be done. This was formalized after discovering a 21% proxy error rate in CD2.

### 2. Extension Methodology
No standard addresses the problem of extending historical data series with modern API data. The Anu Extension Standard defines faithful extension methodology: exact source matching, formula-level replication for derived quantities, and documented splice quality assessment.

### 3. Integrated Quality Scoring
ACRE provides reproduction assessment scores, but they're applied externally. The Anu Framework's anu-review provides 12+ dimensions of quality scoring that agents apply during construction, not after publication.

### 4. Registry-Driven Everything
Like dbt's schema.yml, the series_registry.json drives all output formats. But Anu goes further: the registry also drives script generation, validation targets, visualization labels, and provenance documentation. Every output is derived from the registry — nothing is manually maintained.

---

## What the Anu Framework Can Learn From Others

| Source | Lesson | Status in Anu Framework |
|--------|--------|------------------------|
| **Project TIER 4.0** | Explicit folder structure documentation for students | Anu Architecture covers this, but could have a visual "cheat sheet" |
| **Gentzkow-Shapiro** | "Make functions shy" — minimize side effects | Good practice, not yet encoded as a rule |
| **AEA Data Editor** | Data Availability Statement as a standard document | Added via anu-publish template (v1.0) |
| **FAIR** | DOI assignment for datasets, JSON-LD metadata | Not yet implemented — planned for publication phase |
| **dbt** | Automatic DAG visualization from code | Planned: generate_dag.py template parses script Dependencies |
| **Whole Tale** | Full containerized reproducibility | Dockerfile template added to anu-publish |

---

*Part of the Anu Framework v10.0*

Sources:
- [Project TIER](https://www.projecttier.org/)
- [Gentzkow & Shapiro](https://web.stanford.edu/~gentzkow/research/CodeAndData.xhtml)
- [AEA Data Editor](https://aeadataeditor.github.io/aea-de-guidance/)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)
- [dbt](https://docs.getdbt.com/docs/introduction)
- [ACRE/BITSS](https://bitss.github.io/ACRE/intro.html)
- [Whole Tale](https://labs.globus.org/projects/wholetale.html)
