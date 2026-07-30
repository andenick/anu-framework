# mini-replication — minimal Anu Framework example

A two-series replication package that exercises the Anu Replicator loading,
processing and validation phases (L## → P## → V##) plus output formatting (O##).
It does **not** contain an M## manual-adjustment phase — nothing here needs a
manual adjustment, and the framework forbids inventing one.

## The two series

| ID | Source | Type |
|---|---|---|
| S001 | FRED INDPRO (Industrial Production Index) | Direct column |
| S002 | INDPRO real growth rate | Derived (yearly growth of S001) |

Both are sourced from FRED's public download URL — no API key required.

## What runs

```bash
python run.py
```

Sequence:

1. `code/loading/L01_load_indpro.py` — fetch FRED CSV
2. `code/processing/P01_annual_avg.py` — monthly → annual
3. `code/processing/P02_compute_growth.py` — derive S002
4. `code/validation/V01_validate_levels.py` — check S001
5. `code/validation/V02_validate_growth.py` — check S002 against benchmarks
6. `code/outputs/O01_chopped_csv.py` — write Anu Chopped format

## What you get

- `data/final-data/S001_indpro.csv` — levels
- `data/final-data/S002_indpro_growth.csv` — growth rates
- `data/final-data/chopped.csv` — Anu Chopped 3-row format (metadata, IDs, data)
- `outputs/validation/*.json` — per-series validation reports
- `docs/series/S001_DPR.md` and `S002_DPR.md` — Data Provenance Records

## Validate

```bash
python ../../skills/anu-doctor/check_project.py --project .
```

**This example does not pass the project doctor cleanly, and the gaps are
listed rather than hidden.** It fails P25/P26/P27 because it has no
`ANU_LEDGER.json` and no `PIPELINE_STATE.json`: those are artifacts the
`anu-build` cascade generates during a real run, and hand-writing them would be
inventing a pipeline history that never happened. It also warns on P23 because
its scripts use the flat `code/{loading,processing,validation,outputs}/` layout
rather than the `code/{L01_loaders,P02_processors,V03_validators}/` triad the
doctor looks for. Everything the example *does* claim — sources, units, year
ranges, the S002 formula, complete-year-only annual aggregation — is checked
and true.

## Why this example

This is the *minimum* exercise of the Anu Framework that demonstrates:

- A direct column load (S001)
- A derived series (S002 = year-over-year growth of S001)
- Validation gates (V01, V02)
- The Chopped CSV output format
- Per-series provenance records (DPRs)

For the full reference implementation (64 series, 100% PASS, three
distribution channels), see the Shaikh-Tonak replication notes in
[`docs/LESSONS_LEARNED_RMWND_2026.md`](../../docs/LESSONS_LEARNED_RMWND_2026.md).
