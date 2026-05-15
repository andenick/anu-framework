---
name: anu-docs
version: "1.0"
description: "Per-series documentation standard for Anu Framework projects. Defines three documentation tiers (Thin/Adequate/Enriched), a quality scoring rubric, an enrichment workflow (KB reading, research JSON upgrade, doc regeneration), and validation rules. Produces scrubbed, publication-ready per-series markdown docs from series_registry.json + research JSONs + KB extractions."
when-to-use: "User wants to generate, score, enrich, or validate per-series documentation; audit doc quality across a project; upgrade thin placeholder docs to enriched docs with theoretical context"
search-hints: "docs documentation series per-series enrich thin placeholder methodology generate score audit quality"
argument-hint: "[generate|score|enrich|audit|validate] [project_path|chapter|series]"
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
requires: anu-research, anu-ingestion
part-of: Anu Framework v11.0
---

# Anu Docs Standard v1.0

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Docs |
| Version | 1.0 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-12 |
| Purpose | Per-series documentation lifecycle: generation, scoring, enrichment, and validation |

---

## Purpose

Per-series documentation is the **human-facing explanation** of every constructed data series. It bridges the gap between machine-readable artifacts (registry, CSVs, extenbooks) and a scholar's understanding of what was built, why, and how.

### The Documentation Gap

| Artifact | Audience | What It Explains |
|----------|----------|-----------------|
| `series_registry.json` | Machines/agents | Structure, subseries, construction ops, extension config |
| `S###_research.json` | Agents | KB quotes, methodology descriptions, source citations |
| `S###_DECOMPOSITION.md` | Internal agents | Step-by-step construction blueprint |
| `S###_EPR.md` | Internal agents | Extension provenance and faithfulness |
| **Per-series doc (`S###.md`)** | **Scholars/humans** | **What this measures, why it matters, how it was built** |

Anu Docs owns the last row. Every other artifact feeds into it.

### Design Principles

1. **Registry-driven**: All structural content (construction steps, subseries, extensions) is generated from `series_registry.json` — never hardcoded
2. **Research-enriched**: Methodology descriptions and author quotes come from `S###_research.json` — enrichment means improving research JSONs, not editing docs directly
3. **Tier-progressive**: Documentation quality improves incrementally (T1 -> T2 -> T3) as more source material becomes available
4. **Scrub-safe**: Generated docs never contain internal paths, API keys, or Arcanum-specific references
5. **Regenerable**: Any doc can be regenerated from its source artifacts without loss

---

## Documentation Tiers

Every per-series doc is classified into one of three quality tiers:

### T1: THIN

The minimum viable doc. Generated entirely from registry metadata with no KB reading.

**Indicators**:
- `methodology_description` starts with "Construction steps from registry" or "Data sources:"
- Research JSON has `"researcher": "auto-generated"` with empty `kb_sources_searched`
- "What This Measures" is a single sentence copied from the registry `description` field
- No "From the Book" section
- No theoretical context

**Typical score**: 25-35 points

### T2: ADEQUATE

A functional doc with real methodology content composed from available sources.

**Indicators**:
- Has real `methodology_description` written from reading DECOMPOSITION, EPR, or appendix methodology
- "What This Measures" is 2+ sentences explaining what the series measures and how it was constructed
- Data sources table includes institutional provenance (not just column IDs)
- Construction steps have human-readable descriptions (not just op codes)
- Research JSON has `"researcher": "agent"` (not "auto-generated")

**Typical score**: 55-70 points

### T3: ENRICHED

The gold standard. Includes theoretical context from the original author's text.

**Indicators**:
- Everything in T2 PLUS:
- "From the Book" section with at least one direct author quote and source reference
- Theoretical context paragraph explaining why the series matters to the author's argument
- Connects the series to the broader analytical framework of the source work
- Research JSON has `kb_quote` and `theoretical_context` entry types

**Typical score**: 85-100 points

### Tier Determination Algorithm

```
IF research.researcher == "auto-generated" AND len(research.kb_sources_searched) == 0:
    tier = T1
ELIF has_entry_type(research, "kb_quote") AND has_entry_type(research, "theoretical_context"):
    tier = T3
ELIF has_real_methodology(research):  # methodology_description doesn't start with placeholder prefix
    tier = T2
ELSE:
    tier = T1
```

---

## Per-Series Doc Template

Every per-series doc follows this structure. Sections marked REQUIRED must always be present. Sections marked CONDITIONAL appear only when the tier or data supports them.

```markdown
# S###: {Series Name}

**Chapter N: {Chapter Title}** | **Figures**: {FigN.M} | **Period**: {YYYY}-{YYYY}

## What This Measures                              [REQUIRED]

{Description of what this series measures.}

{For T2+: 2+ sentences with construction summary and institutional provenance.}

{For T3: Additional paragraph with theoretical context from the source work.}

## From the Book                                   [CONDITIONAL: T3 only]

> {Direct quote from the author's text.}
>
> -- Author (Year), {source reference}

## Construction                                    [REQUIRED]

{Table or numbered list of construction steps.}

## Data Sources                                    [REQUIRED]

| Subseries | Source | Period | Units |
|-----------|--------|--------|-------|
| S###-A    | ...    | ...    | ...   |

## Extension                                       [REQUIRED]

{Extension details OR "This series is not extended beyond the original period."}

## Validation                                      [CONDITIONAL: if reference_values exist]

| Year | Value |
|------|-------|
| ...  | ...   |

## Code                                            [REQUIRED]

- Loading: [`loading/ch##.py`](../../loading/ch##.py)
- Processing: [`processing/ch##.py`](../../processing/ch##.py)
```

### Section Content Sources

| Section | Primary Source | Fallback Source |
|---------|---------------|-----------------|
| What This Measures | `research.methodology_description` | Registry `description` field |
| From the Book | `research.kb_quote` entries | None (section omitted) |
| Construction | Registry `construction[]` array | Research JSON construction entries |
| Data Sources | Registry `subseries{}` dict | None |
| Extension | Registry `extension{}` block | Research `extension_provenance` entries |
| Validation | Registry `validation.reference_values{}` | None (section omitted) |
| Code | Registry `chapter` field (derive path) | None |

---

## Enrichment Workflow

The enrichment workflow upgrades docs from T1 to T2 or T3. It operates on **research JSONs**, not on docs directly — docs are always regenerated from their sources.

### Source Priority Order

When enriching a series, read sources in this order (highest priority first):

```
1. KB chapter file (Inputs/Robert/KB/ch##_*.md)         -> enables T3
2. Appendix methodology (KB/ch18_appendices.md)          -> cross-references
3. S###_DECOMPOSITION.md (Technical/docs/series/)        -> rich construction detail
4. S###_EPR.md (Technical/docs/series/)                  -> extension methodology
5. series_registry.json                                  -> structural data only (T2 ceiling)
```

### Step 1: KB Availability Check

```
For target chapter:
  IF KB file exists (Inputs/Robert/KB/ch##_*.md):
    -> Full enrichment possible (target T3)
    -> Read KB, extract quotes and theoretical context
  ELSE:
    -> Registry-deep enrichment only (target T2)
    -> Read DECOMPOSITION, EPR, appendix for cross-refs
```

### Step 2: Research JSON Upgrade

For each series with `"researcher": "auto-generated"`:

**With KB (target T3)**:
1. Read the KB chapter file
2. Search for mentions of the series' figures, data sources, methodology
3. Extract and add entries:
   - `methodology_description`: What the series measures, 2+ sentences (replace placeholder)
   - `source_citation`: Full bibliographic references with institutional provenance
   - `kb_quote`: Direct author quotes about the series' significance
   - `figure_context`: What the figure shows and why the author included it
   - `theoretical_context`: How the series connects to the author's broader argument
4. Update metadata:
   - Set `"researcher": "agent"`
   - Add `kb_sources_searched` entries
   - Set `"confidence": "high"` for KB-sourced entries

**Without KB (target T2)**:
1. Read `S###_DECOMPOSITION.md` for rich construction prose
2. Read `S###_EPR.md` for extension methodology narrative
3. Read `ch18_appendices.md` for any cross-references
4. Compose 2-3 sentence methodology description from DECOMPOSITION + registry
5. Update metadata:
   - Set `"researcher": "agent"`
   - Set `"confidence": "medium"` (no KB verification)

### Step 3: Doc Regeneration

Each project provides its own doc-regeneration script implementing this
skill's contract (the reference implementation is a reference project's `Technical/ANU_REPLICATOR/scripts/utils/`). The expected invocation:

```bash
python generate_series_docs.py --chapter N    # regenerate chapter
python generate_series_docs.py                # regenerate all
```

### Step 4: Score and Validate

```bash
python generate_series_docs.py --score-only   # tier breakdown without regenerating
```

> The `generate_series_docs.py` invocations above are the **contract** this
> skill defines — the script itself is project-provided, like the L##/P##
> scripts an `anu-replicator` package supplies. This skill does not ship a
> generator binary; it specifies what one must do.

---

## Quality Scoring Rubric

Each per-series doc is scored on 6 dimensions (total 100 points):

| Dimension | Max Points | T1 Typical | T2 Typical | T3 Typical |
|-----------|-----------|------------|------------|------------|
| **D1: What This Measures** | 30 | 5 | 20 | 30 |
| **D2: From the Book** | 20 | 0 | 0 | 20 |
| **D3: Construction** | 15 | 10 | 15 | 15 |
| **D4: Data Sources** | 15 | 10 | 15 | 15 |
| **D5: Extension** | 10 | 5 | 10 | 10 |
| **D6: Scrub Compliance** | 10 | 0-10 | 0-10 | 0-10 |

### D1: What This Measures (30 points)

| Score | Criteria |
|-------|----------|
| 0 | Section missing |
| 5 | 1 sentence from registry `description` field only |
| 10 | 1-2 sentences, includes construction summary |
| 20 | 2+ sentences with institutional provenance and methodology |
| 25 | Rich methodology + context connecting to chapter theme |
| 30 | Rich methodology + theoretical context from source work |

### D2: From the Book (20 points)

| Score | Criteria |
|-------|----------|
| 0 | Section absent (T1, T2) |
| 10 | Has author quote but no source reference |
| 15 | Has author quote with source reference |
| 20 | Has author quote with source reference AND theoretical context paragraph in D1 |

### D3: Construction (15 points)

| Score | Criteria |
|-------|----------|
| 0 | Section missing |
| 5 | Construction steps listed but no descriptions |
| 10 | Auto-generated from registry `construction[]` with op codes |
| 15 | Human-readable descriptions for each step |

### D4: Data Sources (15 points)

| Score | Criteria |
|-------|----------|
| 0 | Section missing |
| 5 | Table present but sources are column IDs only |
| 10 | Table with source names from registry |
| 15 | Table with institutional provenance and full source descriptions |

### D5: Extension (10 points)

| Score | Criteria |
|-------|----------|
| 0 | Section missing |
| 5 | "Not extended" or API name only |
| 8 | API, splice method, splice year documented |
| 10 | API, method, year, continuity justification, and source URL |

### D6: Scrub Compliance (10 points)

| Score | Criteria |
|-------|----------|
| 0 | Contains absolute paths, API keys, or Arcanum-internal references |
| 10 | Clean — no internal references detected |

### Project-Level Score

```
Project Doc Score = mean(all series scores)
```

| Score | Rating |
|-------|--------|
| >=85 | EXEMPLARY |
| >=60 | ADEQUATE |
| <60 | INCOMPLETE |

---

## Commands

| Command | Purpose |
|---------|---------|
| `/anu-docs generate [--series S###] [--chapter N]` | Generate per-series docs from registry + research JSONs |
| `/anu-docs score [--chapter N]` | Score all docs and show tier breakdown |
| `/anu-docs audit` | Full audit: tier distribution, KB coverage gaps, placeholder count, project score |
| `/anu-docs enrich [chapter]` | Batch-enrich all T1 docs in a chapter (upgrade research JSONs, regenerate docs) |
| `/anu-docs validate` | Check scrub compliance, template conformance, broken links |
| `/anu-docs diff [series]` | Show what changed between current doc and registry/research state |

### Command Details

**`/anu-docs audit`** output:

```
Anu Docs Audit — the reference project
====================
Total series docs: 114
  T3 (ENRICHED):  50  (44%)
  T2 (ADEQUATE):  63  (55%)
  T1 (THIN):       1  ( 1%)

KB Coverage:
  Chapters WITH KB:    2, 5, 6, 7, 10  (50 series)
  Chapters WITHOUT KB: 8, 9, 11, 12, 14, 15, 16, 17  (64 series)

Project Doc Score: 72 / 100 (ADEQUATE)

Recommendations:
  - 1 series still at T1: [S###] — needs research JSON upgrade
  - 64 series capped at T2 — HDARP extraction of Ch8-17 would enable T3
```

---

## Validation Rules

| Rule | ID | Description | Severity |
|------|----|-------------|----------|
| Template conformance | DOC01 | Doc has all REQUIRED sections (What This Measures, Construction, Data Sources, Extension, Code) | FAIL |
| Placeholder detection | DOC02 | "What This Measures" does not start with "Construction steps from registry" or "Data sources:" | WARN |
| Scrub compliance | DOC03 | No absolute paths, API keys, Arcanum/Robin/Council/Druck/freenic references | FAIL |
| Link integrity | DOC04 | Code section links point to existing files | WARN |
| Research JSON exists | DOC05 | Corresponding `S###_research.json` exists | WARN |
| Research JSON quality | DOC06 | Research JSON has `researcher != "auto-generated"` | WARN |
| Author quote present | DOC07 | "From the Book" section present (T3 indicator) | INFO |
| Year range accuracy | DOC08 | Period in header matches actual data coverage | WARN |
| No duplicate docs | DOC09 | No two docs describe the same series ID | FAIL |
| Index completeness | DOC10 | Master index lists every generated doc | WARN |

### Running Validation

```bash
/anu-docs validate
```

Output: `DOCS_VALIDATION_REPORT.md` with PASS/WARN/FAIL/INFO per rule.

---

## Integration with Anu Framework

| Skill | Relationship |
|-------|-------------|
| **Anu Research** | Upstream: produces `S###_research.json` that Anu Docs consumes |
| **Anu Ingestion** | Upstream: produces DECOMPOSITIONs and DPRs used in enrichment fallback |
| **Anu Extension** | Upstream: produces EPRs referenced in extension section |
| **Anu Review** | Sibling: D12 Documentation dimension delegates to Anu Docs project score |
| **Anu Ledger** | Integration: Ledger tracks doc artifact coverage; Anu Docs reads ledger for gap analysis |
| **Anu Publish** | Downstream: published docs must pass Anu Docs validation (DOC03 scrub) |
| **Anu Drive** | Downstream: methodology PDF sections are generated from the same research JSONs |

### Pipeline Position

```
Stage 5: Replicator -> Stage 6: Chopped/Extenbook
                    -> FLOATING: Anu Docs (generate + score + enrich)
                    -> Stage 7: Visualize
                    -> Stage 8: Publish/Drive (docs validated first)
```

Anu Docs is a FLOATING skill (like Anu Review). It can run at any stage, but is most valuable after Stage 5 when all data artifacts exist. Anu Publish and Anu Drive should not run until Anu Docs validation passes.

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Do This Instead |
|-------------|----------------|-----------------|
| Generating docs before research JSONs exist | Produces T1 placeholders that mask gaps | Run anu-research first, then generate |
| Editing generated docs directly | Changes lost on next generation | Enrich the research JSON, then regenerate |
| Skipping scrub check before publication | Internal paths leak to scholars | Always run `/anu-docs validate` |
| Enriching without reading KB when KB exists | Misses author quotes, stays at T2 | Read KB files first for T3 potential |
| Accepting T1 docs as "done" | Placeholder content is not documentation | Target zero T1 docs before publication |
| Hardcoding theoretical context in the generator | Brittle, project-specific, not regenerable | Store in research JSON `theoretical_context` entries |
| Generating docs for non-existent series | Produces broken links and empty sections | Filter to series with final data on disk |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-12 | Initial release: tier system, scoring rubric, enrichment workflow, validation rules, generator integration, pipeline position |

---

## Documentation Contract

| Aspect | Detail |
|--------|--------|
| **Creates** | `docs/series/S###.md` per-series docs, `docs/README.md` master index |
| **Reads** | `series_registry.json`, `S###_research.json`, `Inputs/Robert/KB/`, `S###_DECOMPOSITION.md`, `S###_EPR.md` |
| **Expects** | Registry populated, research JSONs exist (even if auto-generated), Replicator output complete |
| **Integrates With** | Anu Review D12, Anu Ledger artifact tracking, Anu Publish/Drive scrub validation |
| **Must Update on Completion** | Regenerate Ledger (`/anu-ledger generate`) to record doc coverage |

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v11.0 — Per-Series Documentation Standard*
*v1.0 — May 2026*
