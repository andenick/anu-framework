# Anu Framework

**Version 12.2** · A **19-active-skill** framework (plus 2 deprecated redirect
stubs) for **agent-driven data construction, empirical research, and
reproducible publication** — designed so the outputs reproduce without agents.

The framework covers the full lifecycle, orchestrated by `anu-build`:

- **Researching** source materials (mining quotes, methodology, footnotes)
- **Ingesting** data into a registry-driven structure with full provenance
- **Extending** historical series with modern API data under strict
  faithfulness rules
- **Producing** machine-readable CSVs and human-readable Excel workbooks
- **Building** self-contained replication packages
- **Visualizing** results interactively
- **Auditing** quality across 14 dimensions with two hard gates
- **Distributing** through three sibling channels: GitHub repo (`anu-publish`),
  Google Drive package (`anu-drive`), audit-grade archive (`anu-archive`)
- **Orchestrating** the whole pipeline with `anu-build` (9 stages, computed
  construction order, mandatory gates, multi-agent handoff cascade)

The framework is self-auditing: `anu-doctor` checks framework invariants across
all skills, and every change to a `SKILL.md` is gated by CI.

---

## The 19 active skills

See [`docs/SKILL_VERSION_MATRIX.md`](docs/SKILL_VERSION_MATRIX.md) for the
authoritative table, or [`docs/ANU_FRAMEWORK_OVERVIEW.md`](docs/ANU_FRAMEWORK_OVERVIEW.md)
for the full architecture write-up.

| Stage | Skill | What it does |
|---|---|---|
| 1 | [`anu-research`](skills/anu-research/) | Mine the Knowledge Base for every quote, footnote, methodology note |
| 2 | [`anu-adequacy`](skills/anu-adequacy/) | Post-research readiness gate |
| 3 | [`anu-ingestion`](skills/anu-ingestion/) | Build `series_registry.json`, decompose series, write DPRs |
| 4 | [`anu-extension`](skills/anu-extension/) | Faithful data extension methodology (EPRs) |
| 5 | [`anu-scaffold`](skills/anu-scaffold/) | Generate L01/P02/V03 stubs from registry |
| 5 | [`anu-replicator`](skills/anu-replicator/) | Self-contained L##/P##/V##/M## reproduction package |
| 6a | [`anu-chopped`](skills/anu-chopped/) | Machine-readable CSV format |
| 6b | [`anu-extenbook`](skills/anu-extenbook/) | Human-readable Excel workbook (4 sheets) |
| 7 | [`anu-visualize`](skills/anu-visualize/) | Interactive Plotly Dash / R Shiny app |
| 8a | [`anu-publish`](skills/anu-publish/) | GitHub replication channel + `web` export contract |
| 8b | [`anu-drive`](skills/anu-drive/) | Google Drive consumer package |
| 8c | [`anu-archive`](skills/anu-archive/) | Audit-grade transparency archive |
| Float | [`anu-review`](skills/anu-review/) | 14-dimension quality audit (D1–D12 weighted + D13/D14 gates) |
| Float | [`anu-docs`](skills/anu-docs/) | Per-series documentation (T1/T2/T3 tiers) + the Anu Explainer |
| Float | [`anu-variant`](skills/anu-variant/) | Methodology variant tracking |
| Infra | [`anu-ledger`](skills/anu-ledger/) | Artifact inventory |
| Infra | [`anu-architecture`](skills/anu-architecture/) | 8-phase econometric research scaffold (also available [standalone on GitHub](https://github.com/andenick/anu-architecture)) |
| Infra | [`anu-doctor`](skills/anu-doctor/) | Framework + project self-audit |
| Orch | [`anu-build`](skills/anu-build/) | **Master orchestrator** — 9-stage pipeline + documentation cascade |

**Deprecated (redirect stubs, not counted in the 19):**
[`anu-pipeline`](skills/anu-pipeline/) → `anu-build`, and
[`anu-rebuild`](skills/anu-rebuild/) → `anu-build` (mode=rebuild). Both were
merged into `anu-build` in v12.0.

---

## Core principles

1. **No synthetic data.** Every value traces to a real source. If unavailable,
   the series is `data_unavailable` — never filled. `np.random` in a data
   construction script is always wrong.
2. **No proxies without justification.** CPI is not PPI. Earnings is not
   compensation. Concept substitutions are documented in the registry with
   `"proxy": true` and a written justification.
3. **No lazy splices on derived quantities.** If the original used a formula,
   the extension must compute the same formula with new component data — not
   growth-rate splice the result.
4. **Reproducibility without agents.** A researcher clones the package, sets
   API keys, runs `python replicate.py`, gets validated output with full
   SHA-256 audit trail.
5. **Audit trail everywhere.** Every transformation, parameter choice, and
   model run is logged in structured JSON. Manual adjustments require a
   five-field audit manifest.

Full statement: [`docs/ANU_FRAMEWORK_OVERVIEW.md`](docs/ANU_FRAMEWORK_OVERVIEW.md).

---

## Reference implementation

The Shaikh & Tonak (1994) replication built the framework: 64 series, 100%
PASS, three distribution channels, 21 commits. The 12 friction points
surfaced during that build drove the v11.0 absorption — see
[`docs/LESSONS_LEARNED_RMWND_2026.md`](docs/LESSONS_LEARNED_RMWND_2026.md)
and [`docs/ANU_FRAMEWORK_IMPROVEMENTS_RFC.md`](docs/ANU_FRAMEWORK_IMPROVEMENTS_RFC.md).

A minimal worked example ships at
[`examples/mini-replication/`](examples/mini-replication/).

---

## Using the framework

The skills are designed to be invoked by an AI agent (Claude Code, Cursor,
GLM, etc.) via slash commands or direct skill invocation. Each `SKILL.md`
declares its frontmatter (`name`, `version`, `requires`, `argument-hint`)
and prescribes its sub-commands.

For human use:

1. Read [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).
2. Set up a project with [`anu-architecture`](skills/anu-architecture/) (or
   `pip install anu-architecture` for the standalone version).
3. Use [`anu-research`](skills/anu-research/) → [`anu-adequacy`](skills/anu-adequacy/) →
   [`anu-ingestion`](skills/anu-ingestion/) → [`anu-extension`](skills/anu-extension/) →
   [`anu-replicator`](skills/anu-replicator/) to construct data.
4. Use [`anu-review`](skills/anu-review/) to audit quality.
5. Use [`anu-publish`](skills/anu-publish/) / [`anu-drive`](skills/anu-drive/) /
   [`anu-archive`](skills/anu-archive/) to distribute.

---

## Self-audit

Every change to the framework is gated by `anu-doctor`:

```bash
python tools/check_framework.py
```

The D##-checks verify version consistency across the matrix/overview/frontmatter
triangle, requires-graph acyclicity, headline-version match, evolution-log
presence, canonical-doc existence, stage-map coherence, and stale-version-string
detection. CI runs this on every PR.

---

## Standalone components

- **`anu-architecture`** is also available as a standalone repo:
  [github.com/andenick/anu-architecture](https://github.com/andenick/anu-architecture).
  `git clone` it and `pip install -e .` to get the `anu-architecture` CLI
  without adopting the full framework. (Not currently on PyPI.)

---

## License

MIT. See [`LICENSE`](LICENSE).

---

## Citing

If you use the framework in academic work:

```bibtex
@software{anu_framework_2026,
  title  = {Anu Framework: agent-driven data construction and reproducible
            publication},
  author = {Anu Framework contributors},
  year   = {2026},
  url    = {https://github.com/andenick/anu-framework},
  version = {12.2.0}
}
```
