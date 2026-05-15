"""P02: Derive INDPRO annual growth (S002 = formula on S001)
====================
Phase:   Processing
Purpose: Year-over-year growth rate of S001.
Inputs:  data/final-data/S001_indpro.csv (from P01)
Outputs: data/final-data/S002_indpro_growth.csv
Formula: S002[t] = (S001[t] - S001[t-1]) / S001[t-1]
"""
import csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "data" / "final-data" / "S001_indpro.csv"
dst = PROJECT / "data" / "final-data" / "S002_indpro_growth.csv"

with src.open() as f:
    rows = list(csv.reader(f))
header, data = rows[0], rows[1:]
data = [(int(y), float(v)) for y, v in data]

with dst.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "S002"])
    for i in range(1, len(data)):
        y, v = data[i]
        _, v_prev = data[i - 1]
        if v_prev == 0:
            continue
        growth = (v - v_prev) / v_prev * 100
        w.writerow([y, f"{growth:.4f}"])
print(f"  Wrote {dst.relative_to(PROJECT)} ({len(data) - 1} growth observations)")
