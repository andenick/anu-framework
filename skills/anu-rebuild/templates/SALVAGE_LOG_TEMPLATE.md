# Salvage Log — {{ PROJECT_NAME }}

**Predecessor**: {{ PATH_TO_PREDECESSOR }}
**Salvage date**: {{ YYYY-MM-DD }}

`Inputs/Salvaged/` is read-only after this log is finalized. Every artifact
that ended up under `Inputs/Salvaged/<predecessor>/` has one row here; every
artifact that was deliberately skipped has one row explaining why.

## Copied

| Predecessor path | Copied to | Why |
|---|---|---|
| `Technical/series_registry.json` | `Inputs/Salvaged/<pred>/series_registry.json` | Authoritative predecessor state |
| `research/*.json` | `Inputs/Salvaged/<pred>/research/` | Per-series research dossiers |
| `docs/series/*_DPR.md` | `Inputs/Salvaged/<pred>/docs/series/` | Predecessor's provenance work |
| `data/final/*.csv` | `Inputs/Salvaged/<pred>/data/final/` | Reference benchmarks (re-derive, don't ship) |
| `MIGRATION/divergences_from_*.md` | `Inputs/Salvaged/<pred>/MIGRATION/` | Predecessor's logged deviations |

## Skipped

| Predecessor path | Why |
|---|---|
| `data/raw/` | Regenerable from public APIs |
| `__pycache__/`, `.pytest_cache/` | Build artifacts |
| `.git/` | History stays with predecessor |
| `Technical/internal_tools/` | Predecessor-internal infrastructure (not part of public release) |
| Anything matching `<internal-codename>/` | Internal references unsuitable for the new rebuild |

## Sentinel

`Inputs/Salvaged/.read_only` marks this directory as immutable for the rest
of the rebuild. If a salvaged file needs amendment, copy it to the new
project's working tree first and edit the copy.
