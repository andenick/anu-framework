# S002 — INDPRO Annual Growth Rate

## Source

Derived from S001. No external data source — fully computed.

## Description

Year-over-year percentage growth rate of S001 (Industrial Production Index).

## Construction

- **Type**: Formula
- **Formula**: `S002[t] = (S001[t] - S001[t-1]) / S001[t-1] × 100`
- **Components**: S001
- **Processing script**: `code/processing/P02_compute_growth.py`
- **Validation script**: `code/validation/V02_validate_growth.py`

## Units

Percent per year.

## Period

1920–2024 (one year shorter than S001 — no growth observation for the first
year).

## Reference values (computed from FRED INDPRO; used for V02 validation)

| Year | Expected (%) | Note |
|------|--------------|------|
| 2009 | −11.43 | Great Recession trough |
| 2010 | 5.57 | Recovery |
| 2020 | −7.09 | COVID-19 |

## Why a derived series rather than a separate download?

FRED publishes growth rates as separate series, but computing them from the
level series ensures internal consistency: S001 and S002 are guaranteed to
agree by construction. This is the Anu Framework's "no lazy splices on derived
quantities" principle in miniature — the derived value is computed from
extended components, not splice-merged from an external derived series.
