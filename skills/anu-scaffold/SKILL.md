---
name: anu-scaffold
version: "1.0"
description: "**Template renderer** — not a code generator. Given a populated registry entry, fills L##/P##/V## script templates with the entry's metadata (SID, name, units, source filename, benchmark dict) and writes them to the right location. Every rendered stub has `# TODO:` markers where the agent must fill in the construction logic. The skill chooses ZERO construction logic: template selection is a deterministic lookup from the registry's `content_type` field; the agent does all real work."
when-to-use: "Agent has a populated registry entry (or a cohort of them) and wants to save keystrokes on the boilerplate header/import/path lines. Invoke from `anu-rebuild` Wave W.7 in the runbook."
search-hints: "scaffold generate code stub loader processor validator template registry-driven boilerplate"
allowed-tools: Read, Write, Glob, Bash
argument-hint: "[generate|list-templates] [--series SID | --cohort NAME] [--template direct_column|derived|matrix_summary]"
requires: anu-ingestion
part-of: Anu Framework v11.0
---

# Anu Scaffold Standard v1.0

## Overview

| Property | Value |
|----------|-------|
| Skill Name | Anu Scaffold |
| Version | 1.0 |
| Part Of | Anu Framework v11.0 |
| Created | 2026-05-15 |
| Purpose | Generate L##/P##/V## script stubs from series_registry.json |

---

## Purpose

`anu-scaffold` is a **template renderer**. It fills variables in pre-written template files with values from a registry entry and writes the result to the right location. It is the ONLY mechanical generator the agent invokes during the construction phase of a project — and it deliberately does nothing that requires judgment.

### What it does NOT do

- **Doesn't decide** which scripts to generate. The agent invokes it with explicit `--series` or `--cohort` arguments.
- **Doesn't decide** the template to use beyond a deterministic lookup: `content_type: "time_series" → direct_column.j2`; `content_type: "derived" → derived.j2`; `content_type: "matrix_summary" → matrix_summary.j2`. Three templates total.
- **Doesn't fill in construction logic.** Every rendered stub has `# TODO: agent fills in actual construction logic here` markers. The agent writes the real code.
- **Doesn't choose benchmarks.** Reference values come from the registry entry; the agent put them there.
- **Doesn't make any decision** about subseries, splicing, extension methodology, or proxy handling. Those are agent decisions, made earlier and reflected in the registry.

### What it does

Every series in an Anu Framework project needs three scripts: a loader (`L01_<sid>_<slug>.py`), a processor (`P02_<sid>_<slug>.py`), and a validator (`V03_<sid>_<slug>.py`). Each has the same header structure (imports, paths, registry-entry lookup) regardless of the series. `anu-scaffold` writes that header. The agent writes the body.

This is the same role `cookiecutter` plays for project layouts — pure templating, no decisions baked in.

`anu-scaffold` eliminates the boilerplate. Given a registry entry, it picks the right template, fills it from registry fields, and writes the three scripts to the project's `code/` tree. The agent's job is then to *fill in construction logic* — not to rewrite the same import block 64 times.

Derived from the RMWND build, where 17 hand-rolled generator scripts (`MIGRATION/_gen_*_scripts.py`) did this work informally. This skill formalizes the pattern.

---

## Templates shipped

`templates/` contains three Jinja-style templates, one per common series shape:

| Template | When to use | Example RMWND series |
|---|---|---|
| `direct_column` | Series loaded from a single column of one source CSV; pass-through processor; benchmark-only validator | S501–S506, S511, S512, S601–S606, S609, ES1001-1002, ES1401-1403, ES1701-1704 |
| `derived` | Series computed from already-built upstream series (no L01); processor reads `data/final/<upstream>.csv`; validator usually identity or round-trip check | S507, S510, S513, S514, S608, S801, S901, AS001-AS004, ES1101-1103, ES1304-1305 |
| `matrix_summary` | Series derived from benchmark IO matrices (or similar matrix per benchmark year); processor produces per-year summary statistics | S401, S402, S701, S702, S703 |

Each template lives at `templates/L01_<template>.py.j2`, `templates/P02_<template>.py.j2`, `templates/V03_<template>.py.j2`. The agent can override per-project by dropping a `code/_scaffold_templates/<template>.py.j2` file in the target project.

---

## Auto-template selection from registry

When `--template auto` (default), the skill picks a template from the registry entry:

- `content_type: time_series` + `construction[0].op: load` (no derive/splice) → `direct_column`
- `content_type: derived` OR construction has no `load` op → `derived`
- `content_type: benchmark_only` OR `matrix` mentioned in registry → `matrix_summary`

Override with `--template <name>` to force a specific template.

---

## Commands

| Command | Purpose |
|---|---|
| `anu-scaffold generate --series S###` | Scaffold trio for one series |
| `anu-scaffold generate --cohort <name>` | Scaffold trio for every series in a cohort (chapter, wave, study group) |
| `anu-scaffold generate --all-pending` | Scaffold for every registry entry with status=`loaded` or `data_available` |
| `anu-scaffold list-templates` | Print template inventory |

Cohort lookup reads the registry's `wave:` field (or `chapter:` for book series). Custom cohort definitions live in `series_registry.json` under top-level `cohorts:` (optional).

---

## Generator script

This skill ships an executable generator at `generate.py` (alongside this SKILL.md). It is the canonical implementation of all `anu-scaffold generate` commands.

```bash
python generate.py --series S501
python generate.py --cohort wave_1_ch5 --template auto
python generate.py --all-pending --dry-run
```

The generator reads `<project_root>/series_registry.json`, picks the template per series (auto or user-forced), renders it with `registry_entry` as the context, and writes to:

- `<project_root>/code/L01_loaders/L01_<sid>_<slug>.py`
- `<project_root>/code/P02_processors/P02_<sid>_<slug>.py`
- `<project_root>/code/V03_validators/V03_<sid>_<slug>.py`

`<slug>` is derived from the registry's `name` field (lowercase, underscores, alphanumeric only).

---

## Output contract

Each generated script:

- Has a docstring stating the registry source and intended construction
- Imports from the project's `lib/` (per anu-replicator v3.1 prescription)
- Includes a `run()` function callable by the project's `run.py` orchestrator
- Has a `__main__` block for direct invocation
- Includes `# TODO:` markers wherever the agent should fill in construction logic

The generator does NOT fill in construction-specific code (e.g., the actual derivation formula for a derived series). It scaffolds the skeleton; the agent reads the registry's `construction` block + DPR and writes the body.

---

## When NOT to use

| Scenario | Use instead |
|---|---|
| Registry entry doesn't exist yet | `anu-ingestion create-registry-entry` first |
| Series needs custom L01 logic outside the 3 templates | Hand-write; templates are guidance, not enforcement |
| Series is purely declarative (no script needed, just registry+validation block) | Don't scaffold; mark `status: declared_only` |

---

## Integration with Anu Framework

| Skill | Relationship |
|---|---|
| `anu-ingestion` (required) | Provides the registry that drives template selection |
| `anu-replicator` | Generated scripts target the `lib/` structure anu-replicator prescribes |
| `anu-rebuild` | The 6-wave rebuild workflow invokes `anu-scaffold generate --cohort` per wave |
| `anu-pipeline` | Generated scripts conform to the S/L/P/V/M/A/O/E phase layout anu-pipeline orchestrates |

---

## Documentation Contract

| Aspect | Detail |
|---|---|
| **Creates** | `code/L01_loaders/L01_<sid>_<slug>.py`, `code/P02_processors/P02_<sid>_<slug>.py`, `code/V03_validators/V03_<sid>_<slug>.py` |
| **Expects** | `series_registry.json` with the target series populated (name, content_type, construction, validation, source_file or subseries.source) |
| **Reads** | Registry, templates in `templates/` (or `code/_scaffold_templates/` override) |
| **Updates** | Nothing — writes new files only; refuses to overwrite without `--force` |

---

## Version History

- **v1.0** (May 2026) — Initial release. Three templates (direct_column, derived, matrix_summary), auto-template selection from registry, batch `--cohort` mode, ships `generate.py`.

---

## Canonical references

- [`ANU_FRAMEWORK_GLOSSARY.md`](../../docs/ANU_FRAMEWORK_GLOSSARY.md) — shared vocabulary
- [`SERIES_REGISTRY_SCHEMA.md`](../../docs/SERIES_REGISTRY_SCHEMA.md) — fields read by the generator
- `anu-replicator` lib/ structure prescription — where generated scripts import from

---

*Part of the Anu Framework v11.0 — Registry-driven code scaffolding.*
