# S001 — Industrial Production Index

## Source

- **Agency**: Federal Reserve Board (via FRED)
- **Series ID**: INDPRO
- **Public URL**: https://fred.stlouisfed.org/series/INDPRO
- **Download**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO

## Description

Industrial Production Index — a measure of the real output of the
manufacturing, mining, and electric/gas utilities industries in the United
States. Published monthly by the Federal Reserve Board; reindexed to 2017=100.

## Construction

- **Type**: Direct column (no derivation)
- **Loading script**: `code/loading/L01_load_indpro.py`
- **Processing script**: `code/processing/P01_annual_avg.py`
  - Aggregates monthly observations to annual averages (simple arithmetic mean)
- **Validation script**: `code/validation/V01_validate_levels.py`

## Units

Index, 2017 = 100.

## Period

1919–2024 (depending on FRED's current vintage).

## Reference values (from FRED, used for V01 validation)

| Year | Expected |
|------|----------|
| 1929 | 7.6 |
| 1950 | 15.8 |
| 2017 | 100.0 |
| 2023 | 100.8 |

## Known divergences

None — this is a direct download of the FRED-published series.
