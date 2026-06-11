---
name: anu-docs
version: "3.0"
description: "Per-series documentation standard for Anu Framework projects. Defines three documentation tiers (Thin/Adequate/Enriched), a quality scoring rubric, an enrichment workflow (KB reading, research JSON upgrade, doc regeneration), validation rules, and the Anu Explainer — the web-facing per-series artifact (What it is / Where the data comes from / How it was constructed / Why it matters / From the book) rendered below the chart on series pages. Produces scrubbed, publication-ready per-series markdown docs from series_registry.json + research JSONs + KB extractions."
when-to-use: "User wants to generate, score, enrich, or validate per-series documentation; audit doc quality across a project; upgrade thin placeholder docs to enriched docs with theoretical context"
search-hints: "docs documentation series per-series enrich thin placeholder methodology generate score audit quality"
argument-hint: "[generate|score|enrich|audit|validate] [project_path|chapter|series]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
requires: anu-research, anu-ingestion
part-of: Anu Framework v12.2
---

# Anu Docs v3.0

Per-series documentation lifecycle: generation, scoring, enrichment, and validation. Bridges the gap between machine-readable artifacts (registry, CSVs, extenbooks) and a scholar's understanding of what was built, why, and how. Since v3.0 it also owns the **Anu Explainer** — the web-facing per-series entry rendered on data-site series pages.

---

## Stage Position

**Floating** — can run at any stage; most valuable after Stage 5 (Replication) when all data artifacts exist. Anu Publish and Anu Drive should not run until Anu Docs validation passes.

---

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| `series_registry.json` | anu-ingestion output | Yes |
| `S###_research.json` | anu-research output | Yes (even if auto-generated) |
| `Inputs/Robert/KB/ch##_*.md` | HDARP extractions | Recommended (enables T3) |
| `S###_DECOMPOSITION.md` | anu-ingestion output | Recommended (enrichment fallback) |
| `S###_EPR.md` | anu-extension output | Recommended (extension section) |
| `ANU_LEDGER.json` | anu-ledger output | Recommended (gap analysis) |

---

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Per-series docs | `docs/series/S###.md` | Publication-ready per-series documentation |
| **Anu Explainers** | `docs/explainers/{SID}_EXPLAINER.md` | Web-facing per-series entry rendered below the chart on series pages (v3.0) |
| Master index | `docs/README.md` | Index of all generated docs |
| Validation report | `DOCS_VALIDATION_REPORT.md` | PASS/WARN/FAIL/INFO per rule |
| Score report | Console / doc output | Tier breakdown and project score |

---

## Commands

| Command | Description |
|---------|-------------|
| `/anu-docs generate [--series S###] [--chapter N]` | Generate per-series docs from registry + research JSONs |
| `/anu-docs score [--chapter N]` | Score all docs and show tier breakdown |
| `/anu-docs audit` | Full audit: tier distribution, KB coverage gaps, placeholder count, project score |
| `/anu-docs enrich [chapter]` | Batch-enrich all T1 docs in a chapter (upgrade research JSONs, regenerate docs) |
| `/anu-docs validate` | Check scrub compliance, template conformance, broken links |
| `/anu-docs diff [series]` | Show what changed between current doc and registry/research state |

---

## The Documentation Gap

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

## The Anu Explainer (v3.0)

The Explainer is the **web-facing** per-series artifact — what a site visitor reads directly below the chart on a series page. It is a standard pipeline output (registered in the anu-build cascade), generated per published series, and shipped by anu-publish's `web` profile under `docs/explainers/`.

**Division of labor**: the Explainer is for humans browsing the website; the classic **DPR remains the full-provenance "agent context" artifact** and is offered as a download link under the Explainer (`Full provenance record (download)`), never rendered inline.

### Explainer Template (fixed five sections)

```markdown
# {display_name}

**Series**: {SID} | **Period**: {YYYY}-{YYYY} | **Units**: {units}

## What this series is
{2-4 plain-language sentences. No jargon without definition.}

## Where the data comes from
{Institutional sources as a definition list — NEVER a wide markdown table:}
**{Source name}**
: {What it provides, period, institution, public URL if available.}

## How it was constructed
{Numbered plain-language steps; formulas stated in words first, notation second.}

## Why it matters
{Theoretical context: the role this series plays in the source work's argument.}

## From the book                                    [CONDITIONAL: if kb_quote exists]
> {Verified direct quote.}
> -- {Author} ({Year}), {exact location} <!-- kb: ch##, section anchor -->
```

### Web-Format Rules (hard requirements)

1. **No file paths of any kind** — no workspace paths, no relative repo paths; sources are named institutionally (gate: DOC03 + anu-publish P10/P11)
2. **No tables wider than 2 columns** — narrow panels make wide markdown tables unreadable; use definition lists for sources
3. **No internal links** — the explainer renders standalone inside a site template
4. **Every quote carries a KB anchor** — an HTML comment `<!-- kb: ch##, ... -->` verifiable against `Inputs/Robert/KB/` (gate: DOC12)
5. **Sourced from the research JSON only** — fixing explainer content means fixing `{SID}_research.json` and regenerating, identical to the doc contract

### Generation Contract

The project's `generate_series_docs.py` (the same project-provided generator) emits both artifacts per series:

```bash
python generate_series_docs.py --explainers            # regenerate all explainers
python generate_series_docs.py --series S201 --explainers
```

Section sources: *What this series is* ← `methodology_description` (first sentences, plain-language pass); *Where the data comes from* ← `source_citation` entries; *How it was constructed* ← registry `construction[]` + DECOMPOSITION prose; *Why it matters* ← `theoretical_context`; *From the book* ← `kb_quote` entries with their KB anchors.

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
skill's contract (the reference implementation is CD2's
`Technical/ANU_REPLICATOR/scripts/utils/`). The expected invocation:

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
| Explainer coverage | DOC11 | Every `publish: true` series has `docs/explainers/{SID}_EXPLAINER.md` | FAIL (at publication) |
| Quote anchors verifiable | DOC12 | Every "From the book" quote (doc + explainer) carries a `<!-- kb: ch##, ... -->` anchor AND the quoted text is findable in the referenced KB chapter file | FAIL |

---

## Acceptance Gates

| Gate | Condition |
|------|-----------|
| Generation | Registry populated, research JSONs exist (even if auto-generated), Replicator output complete |
| Publication readiness | Zero DOC01/DOC03/DOC09/DOC11/DOC12 failures, project score >= 60 |
| T3 eligibility | KB chapter file exists for the target chapter |
| External distribution | DOC03 scrub compliance PASS for all distributed docs; explainers pass the Web-Format Rules |

---

## Documentation Cascade Writes

| File | When written |
|------|-------------|
| `docs/series/S###.md` | After generation or enrichment |
| `docs/explainers/{SID}_EXPLAINER.md` | After generation or enrichment (every published series) |
| `docs/README.md` | After any generation run (master index) |
| `DOCS_VALIDATION_REPORT.md` | After validation run |
| `ANU_LEDGER.json` | Regenerate after generation (`/anu-ledger generate`) to record doc coverage |

---

## Integration with Anu Framework

| Upstream Skill | Input Artifact | This Skill Uses It For |
|----------------|----------------|------------------------|
| **Anu Research** | `S###_research.json` | Primary content source (methodology, quotes, context) |
| **Anu Ingestion** | DECOMPOSITIONs, DPRs | Enrichment fallback (construction detail) |
| **Anu Extension** | EPRs | Extension section content |
| **Anu Review** | D12 Documentation dimension | Delegates to Anu Docs project score |
| **Anu Ledger** | Artifact tracking | Ledger tracks doc artifact coverage; Anu Docs reads for gap analysis |
| **Anu Publish** | Downstream consumer | Published docs must pass DOC03 scrub |
| **Anu Drive** | Downstream consumer | Methodology PDF sections generated from same research JSONs |

### Pipeline Position

```
Stage 5: Replicator -> Stage 6: Chopped/Extenbook
                    -> FLOATING: Anu Docs (generate + score + enrich)
                    -> Stage 7: Visualize
                    -> Stage 8: Publish/Drive (docs validated first)
```

---

## Anti-Patterns

- **DO NOT** generate docs before research JSONs exist — produces T1 placeholders that mask gaps
- **DO NOT** edit generated docs directly — changes lost on next generation; enrich the research JSON instead
- **DO NOT** skip scrub check before publication — internal paths leak to scholars
- **DO NOT** enrich without reading KB when KB exists — misses author quotes, stays at T2
- **DO NOT** accept T1 docs as "done" — placeholder content is not documentation
- **DO NOT** hardcode theoretical context in the generator — store in research JSON `theoretical_context` entries
- **DO NOT** generate docs for non-existent series — produces broken links and empty sections

---

## Robin Integration

For per-series docs sourcing from Robin, the Adequate-tier doc must cite the `robin_source_id` and `canonical_path` from the project's `Inputs/Robin/[SOURCE]/PROVENANCE.md`. Enriched tier additionally cites the upstream paper/URL from Robin's per-source README.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-12 | Initial release: tier system, scoring rubric, enrichment workflow, validation rules, generator integration, pipeline position |
| 2.0 | 2026-05-16 | Rewritten to v12.0 common template. Added stage position, cascade writes, acceptance gates, anti-patterns sections. Updated `part-of` to Anu Framework v12.0. |
| 3.0 | 2026-06-10 | **The Anu Explainer**: new web-facing per-series artifact (`docs/explainers/{SID}_EXPLAINER.md`) with a fixed five-section template (What it is / Where the data comes from / How constructed / Why it matters / From the book) and hard Web-Format Rules (no file paths, no wide tables, sources as definition lists, KB-anchored quotes). DPR repositioned as the downloadable full-provenance "agent context" artifact. New validation rules DOC11 (explainer coverage, FAIL at publication) + DOC12 (KB-verifiable quote anchors, FAIL). Consumed by anu-publish `web` profile; registered in the anu-build cascade. |

---

## Canonical References

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary for all framework terms.

---

*Part of the Anu Framework v12.0 — Per-Series Documentation Standard*
