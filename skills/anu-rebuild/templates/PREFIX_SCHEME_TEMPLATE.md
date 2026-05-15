# Prefix Scheme — {{ PROJECT_NAME }}

**Decided**: {{ YYYY-MM-DD }}
**Decided by**: {{ AGENT_OR_USER }}

## Scheme

| Prefix | Role | Example | Notes |
|---|---|---|---|
| `D` | **Primary** — Data Series from the book/study being replicated | `D001`, `D042` | Canonical (Anu Framework default) |
| `AD` | **Additional** — Everything else: series from other studies, derivative analytical series, comparison datasets, theoretical-construct series | `AD1001`, `AD2001` | Canonical (Anu Framework default) |

<!--
If your project genuinely requires a third prefix, add it here with a one-line
justification. This should be rare. Example only:

| `CD` | **Cross-sectional** — point-in-time IO matrices that don't fit the D/AD frame | `CD001` | Project-specific; data lacks time dimension |

Delete this comment block if no extensions are needed.
-->

## Why D/AD and not S/ES?

The earlier S/ES scheme collided with `anu-architecture`'s `S##` Setup-phase
script prefixes (e.g. `S00_run_all.py`). `D` reads as "Data" and is collision-
free against the eight phase prefixes (S, L, P, V, M, A, O, E). `AD` extends
naturally and avoids the conceptual split between "external" and "analytical."

## Registry declaration

This scheme is also declared in `Technical/series_registry.json`:

```json
"prefix_scheme": {
  "primary": "D",
  "additional": "AD"
}
```

`anu-doctor` P12 validates that every series ID in the registry matches one
of these prefixes.

## Series-ID format

Format: `{PREFIX}{NNN}[-{LETTER}][-EXT|-COMBINED]`

| Pattern | Example |
|---|---|
| Base | `D001`, `AD1001` |
| Subseries | `D001-A`, `AD1001-B` |
| Extension data | `D001-EXT` |
| Final combined | `D001-COMBINED` |
