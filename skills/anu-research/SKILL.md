---
name: anu-research
version: "2.1"
description: Systematically mine every quote, reference, footnote, methodology description, and piece of information relevant to constructing a particular data series. v2.1 adds a `port` sub-command that ingests an existing predecessor project's research JSONs and rewrites IDs against an external mapping table (used by the anu-rebuild meta-skill to salvage prior research effort instead of re-mining the KB).
when-to-use: User needs to mine a Knowledge Base for quotes, methodology, footnotes, or research context before constructing a data series; OR port research JSONs from a predecessor project under a new ID scheme.
search-hints: research mine quotes methodology footnote knowledge base series dossier port predecessor migrate
argument-hint: [action] [series_id]
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: none
part-of: Anu Framework v11.0
---

# Anu Research Standard v2.1

Systematically find **every possible quote, reference, footnote, methodology description, and piece of information** relevant to constructing a particular data series. Store as structured JSON associated with each series ID. This research dossier is the foundation for all downstream outputs.

---

## Purpose

Before constructing or extending any data series, an agent must deeply understand what the original author did. The Anu Research skill produces a structured `S###_research.json` file that captures:

- Direct quotes from book text about the series
- Appendix methodology descriptions (construction instructions)
- Footnote and endnote source citations
- Figure context (how the series is discussed in the narrative)
- Data caveats, known issues, or author notes
- Reindexing notes (why a particular base year was chosen)
- Splicing notes (how series were combined)
- Cross-references to other series that share sources or interact

---

## When to Use

Use Anu Research **before** any of the following:

- Creating a series decomposition (`S###_DECOMPOSITION.md`)
- Building loading or processing scripts (L## / P##)
- Writing DPRs or EPRs
- Populating the `series_registry.json`

The research output is a **prerequisite** for Anu Ingestion and feeds programmatically into all downstream outputs.

---

## Prerequisites

1. **Knowledge Base exists**: HDARP extractions of book text, appendices, footnotes available (typically in `Inputs/Robert/` or a KB directory)
2. **Series ID assigned**: The series has a canonical ID (S001, S002, etc.) per the Series ID Specification v2.0
3. **Chopped data available**: The Anu Chopped CSV for the series exists in the project's Chopped directory
4. **Adequacy Check passed** (recommended): `CH{N}_ADEQUACY_REPORT.json` exists for the chapter with `overall_adequacy` >= ADEQUATE. If absent, warn but proceed — adequacy can be assessed retroactively

---

## Data Extraction Obligation

When mining the KB for a series, the agent MUST check whether the HDARP extraction contains actual annual data tables — not just benchmark summaries or narrative descriptions. If annual data tables exist in any chunk:

1. **Flag them explicitly** in the research output
2. **Include table location** (chunk, page, table number)
3. **Extract the data** as part of the research process — do not defer to a later stage
4. **Never approximate** what can be extracted directly

Common failure mode: an HDARP extraction contains a complete 28-year annual data table, but the agent reads only the narrative summary and generates synthetic data from the summary statistics. This is unacceptable — always extract the actual table data.

---

## Workflow

### Step 0: Verify Adequacy

Before beginning research, check if `Technical/docs/chapters/CH{N}_ADEQUACY_REPORT.json` exists for the chapter. If it exists and `overall_adequacy` is ADEQUATE or EXEMPLARY, proceed. If INSUFFICIENT or BLOCKED, run `/anu-adequacy check [chapter]` first to identify and remediate gaps. If no report exists, warn the user and proceed with research (adequacy can be assessed retroactively).

### Step 1: Identify the Series

Determine the series ID, chapter, and associated figures. Check the `series_registry.json` if it exists, or the Chopped CSV README.

### Step 2: Search Knowledge Base

For the given series, systematically search:

1. **Appendix methodology text** — The primary source. Search for the series name, figure number, and data source names. Extract every sentence that describes how the data was constructed.
2. **Chapter body text** — Search for figure references (e.g., "Figure 2.1"), data discussions, and interpretive context.
3. **Footnotes and endnotes** — Search for source citations, data access dates, and methodological notes.
4. **Other chapters** — Search for cross-references where this series or its sources appear in other chapters.
5. **Bibliography** — Identify full citations for all sources mentioned.

### Step 3: Classify Each Finding

Classify each finding by type. Two entry formats are supported (see Output Format below):

| Type | Description |
|------|-------------|
| `methodology_description` | How the series was constructed |
| `source_citation` | Citation of an original data source |
| `figure_context` | How the series appears in a figure or narrative |
| `data_caveat` | Known limitations, adjustments, or warnings |
| `reindexing_note` | Why/how a base year change was made |
| `splicing_note` | How two series were combined |
| `units_note` | Unit definitions, conversions, or clarifications |
| `cross_reference` | Reference to another series sharing sources |
| `errata` | Known errors or corrections |

### Step 4: Record Confidence Level

| Confidence | Meaning |
|------------|---------|
| `exact_quote` | Verbatim text from the source |
| `paraphrase` | Faithful restatement of the source |
| `inference` | Deduced from context, not explicitly stated |

### Step 5: Compile Citations

For each original data source referenced, create a citation entry with:
- `citation_id` (C001, C002, ...)
- `full_citation` (complete bibliographic reference)
- `short_cite` (abbreviated form for inline use)
- `subseries` (which subseries this source feeds)
- `type` (primary_source, secondary_source, methodology_reference)

### Step 6: Write Methodology Summary

Synthesize all findings into a concise `methodology_summary` paragraph that explains the complete construction in plain language.

### Step 7: Write S###_research.json

Save the compiled research to `Technical/research/S###_research.json` using the output format below.

---

## Output Format

File: `S###_research.json`

Two entry formats are supported within the `entries` array:

### Full Format (preferred for complex multi-subseries construction)

The v2.0 schema adds `entry_id`, `subseries_affected`, `confidence`, `source_refs`, and `kb_reference` fields to each entry. These fields enable cross-referencing with the SourceReference system in `series_registry.json` and the provenance index.

```json
{
  "series_id": "S001",
  "series_name": "US Industrial Production Index",
  "chapter": 2,
  "figures": ["Fig2.1"],
  "research_date": "2026-03-07",
  "researcher": "agent",
  "kb_sources_searched": [
    "ch02_turbulent_trends.md",
    "ch18_appendices.md",
    "appendix_methodology_summary.json"
  ],
  "entries": [
    {
      "entry_id": "R001",
      "type": "methodology_description",
      "source_location": "Appendix 2, p. 843",
      "quote": "The industrial production index is constructed from...",
      "relevance": "primary_construction",
      "subseries_affected": ["S001-A", "S001-B", "S001-C", "S001-D"],
      "confidence": "exact_quote",
      "source_refs": ["SRC-BEA-LTEG", "SRC-FRB-INDPRO"],
      "kb_reference": "ch02_turbulent_trends.md#section-industrial-production"
    }
  ],
  "citations": [
    {
      "citation_id": "C001",
      "full_citation": "Bureau of Economic Analysis, Long Term Economic Growth, 1860-1970, Table A-15, p.185",
      "short_cite": "BEA LTEG 1966, TA15",
      "subseries": ["S001-A"],
      "type": "primary_source"
    }
  ],
  "methodology_summary": "The author constructs the series by splicing two industrial production indices...",
  "known_issues": [],
  "cross_references": ["S007 (uses same BEA LTEG source for manufacturing)"],
  "adequacy_refs": {
    "L1_kb_pages": ["page_120_methodology.md", "page_310_table_E2.csv"],
    "L3_data_sources": ["BEA NIPA Table 6.2D", "BEA LTEG Table A-15"],
    "L5_validation": ["Mohun_2013_exploitation_rates.csv"]
  }
}
```

### Compact Format (acceptable for batch creation)

When creating research files for many series in a chapter simultaneously, a streamlined entry format is acceptable. **Example (CD2, S034):**

```json
{
  "series_id": "S034",
  "series_name": "US Industry Average Rates of Profit",
  "chapter": 7,
  "figures": ["Fig7.15"],
  "research_date": "2026-03-06",
  "researcher": "agent",
  "kb_sources_searched": ["ch07_real_competition.md", "ch18_appendices.md"],
  "entries": [
    {
      "entry_type": "methodology_description",
      "content": "Average rate of profit for 30 competitive US industries...",
      "source_ref": "Appendix 7.1, section III (Shaikh 2008)"
    },
    {
      "entry_type": "source_citation",
      "content": "BEA GDP-by-Industry tables (NAICS) 1987-2005...",
      "source_ref": "BEA NIPA, Wealth Tables"
    }
  ],
  "citations": [
    {
      "id": "Shaikh_2008",
      "full": "Shaikh, Anwar. 2008. 'Competition and Industrial Rates of Return.'"
    }
  ],
  "methodology_summary": "S034 computes the cross-sectional average ROP...",
  "known_issues": ["Data only covers 1987-2005"],
  "cross_references": ["Appendix7_ropdataUSind.csv (S217)"],
  "adequacy_refs": {
    "L1_kb_pages": ["ch07_real_competition.md", "ch18_appendices.md"],
    "L3_data_sources": ["BEA GDP-by-Industry NAICS tables"],
    "L5_validation": []
  }
}
```

**Key differences**: Compact entries use `entry_type`/`content`/`source_ref` instead of `entry_id`/`type`/`source_location`/`quote`/`relevance`/`subseries_affected`/`confidence`. Compact citations use `id`/`full` instead of `citation_id`/`full_citation`/`short_cite`/`subseries`/`type`. Both formats are valid and consumed correctly by downstream outputs.

### v2.0 Entry Fields (Full Format)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entry_id` | string | Yes | Unique ID within the file (R001, R002, ...) |
| `type` | string | Yes | Entry classification (see Step 3 above) |
| `source_location` | string | Yes | Page/section reference in KB |
| `quote` | string | Yes | Verbatim or paraphrased text |
| `relevance` | string | Yes | How this relates to construction |
| `subseries_affected` | array | Yes (v2.0) | Which subseries IDs this finding impacts |
| `confidence` | string | Yes (v2.0) | `exact_quote`, `paraphrase`, or `inference` |
| `source_refs` | array | New (v2.0) | SourceReference IDs from `series_registry.json` sources block (e.g., `["SRC-BEA-LTEG"]`) |
| `kb_reference` | string | New (v2.0) | Path to the KB file and section where this finding originates |

### adequacy_refs Field (v1.3+)

The optional `adequacy_refs` object traces research findings back to adequacy-verified sources across three layers:
- **L1_kb_pages**: KB files that were the primary sources for this research (links to Adequacy Layer 1)
- **L3_data_sources**: Raw data sources identified for construction/extension (links to Adequacy Layer 3)
- **L5_validation**: External validation datasets identified for this series (links to Adequacy Layer 5)

This field is populated during research and later cross-checked by Anu Review to verify that all adequacy-identified sources were actually used.

---

## Programmatic Incorporation

The `S###_research.json` is consumed by every downstream output:

| Output | How Research is Used |
|--------|---------------------|
| **Anu Extenbook** | "Research" sheet: one row per entry with columns entry_id, type, source_location, quote, subseries_affected |
| **Anu Chopped CSV** | Row 1 metadata: methodology_summary appended to source description |
| **Anu Visualize (Dash)** | "Research Notes" panel: filterable table of all entries for selected series |
| **Anu Replicator** | Console output: prints methodology_summary in series header; P## scripts load research for context |
| **DPR** | Citations section populated from research.json citations array |
| **EPR** | Methodology comparison section references research entries |
| **series_registry.json** | Research file path recorded; entry count tracked |

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-research mine [series_id]` | Mine KB for all references to a series |
| `/anu-research mine-chapter [chapter]` | Mine KB for all series in a chapter |
| `/anu-research validate [series_id]` | Check research.json completeness |
| `/anu-research summary [series_id]` | Print methodology summary |
| `/anu-research citations [series_id]` | List all citations for a series |
| `/anu-research cross-refs [series_id]` | Find cross-references to other series |

---

## Quality Checklist

For each `S###_research.json`:

- [ ] At least one `methodology_description` entry exists
- [ ] All original data sources have corresponding `source_citation` entries
- [ ] All figures referencing this series have `figure_context` entries
- [ ] `methodology_summary` accurately describes the full construction
- [ ] `citations` array has full bibliographic info for every source
- [ ] `cross_references` lists all related series
- [ ] `kb_sources_searched` lists all KB files consulted

For full-format entries (preferred when time permits):
- [ ] All reindexing operations have `reindexing_note` entries
- [ ] All splicing operations have `splicing_note` entries
- [ ] `confidence` is set correctly for every entry (prefer `exact_quote`)
- [ ] `subseries_affected` is populated for each entry

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Ingestion** | Research is a prerequisite; decomposition documents reference research entries |
| **Anu Extension** | EPRs reference research entries for methodology comparison |
| **Anu Replicator** | P## scripts load research.json; console reporter prints methodology summary |
| **Anu Extenbook** | Research sheet auto-generated from research.json |
| **Anu Visualize** | Research Notes panel reads research.json |
| **Anu Review** | D3 Research Coverage dimension scores research completeness |
| **Anu Pipeline** | Research stage runs before Ingestion stage |

---

## Template

Template file: `templates/RESEARCH_TEMPLATE.json`

---

## Anu Framework Context

- **Pipeline Stage**: 1 (RESEARCH)
- **Upstream**: Stage 0 Adequacy (gated — requires ADEQUATE rating)
- **Downstream**: Stage 2 Ingestion, Stage 3 Extension, Anu Extenbook
- **Adequacy Relevance**: Research traces findings back to adequacy-verified KB sources via `adequacy_refs` field
- **Key Handoff**: S###_research.json consumed by Ingestion (decompositions, DPRs), Extension (EPRs), Extenbook (Research sheet)

## Version History

- **v1.0** (March 2026) - Initial release
- **v1.1** (March 2026) - Added compact entry format as valid alternative; updated quality checklist for both formats; updated template to use compact format
- **v1.2** (March 2026) - Generalized: replaced project-specific methodology text with generic terms; labeled CD2 examples
- **v1.3** (March 2026) - Added adequacy_refs field for traceability to adequacy-verified sources
- **v2.0** (April 2026) - research.json v2.0 schema: added entry_id, subseries_affected, confidence as required fields in full format; added source_refs (links to SourceReference system in series_registry.json) and kb_reference fields; v2.0 entry fields table

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `S###_research.json` in `Technical/research/` |
| **Expects** | KB files in `Inputs/Robert/KB/`, series ID assigned |
| **Must Update on Completion** | No additional updates required — the research.json itself is the deliverable |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v11.0 — Comprehensive Data Construction Framework*
