# Absorption Report: Chapter [N]

## Overview

| Field | Value |
|-------|-------|
| Project | [PROJECT] |
| Chapter | [N] |
| Date | [YYYY-MM-DD] |
| Series Count | [N] |
| Source Files | [N] Chopped CSVs |

## Source Files Absorbed

| Source File | Series | Columns | Rows | Format |
|------------|--------|---------|------|--------|
| [filename.csv] | S### | [N] | [N] | time_series |

## Column ID Migration

| Old ID (v1.0) | New ID (v2.0) | Change |
|---------------|---------------|--------|
| S001A | S001-A | Dash notation |
| S001_EXT | S001-EXT | Dash notation |

## Absorbed Database

Output: `Technical/absorbed/chapter_##_absorbed.csv`

| Field | Value |
|-------|-------|
| Format | Long-format CSV |
| Columns | series_id, subseries_id, year, value, source, units, is_reindexed, transform_type |
| Total Rows | [N] |
| Series Coverage | S### through S### |

---

*Generated from Anu Ingestion v3.0 — Absorption Report Template*
