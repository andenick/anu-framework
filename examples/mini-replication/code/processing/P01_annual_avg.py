"""P01: Monthly INDPRO -> Annual averages (S001)
====================
Phase:   Processing
Purpose: Convert monthly INDPRO to annual averages.
Inputs:  data/raw-data/indpro_monthly.csv (from L01)
Outputs: data/final-data/S001_indpro.csv
"""
import csv
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
src = PROJECT / "data" / "raw-data" / "indpro_monthly.csv"
dst = PROJECT / "data" / "final-data" / "S001_indpro.csv"
dst.parent.mkdir(parents=True, exist_ok=True)

if not src.exists():
    print(f"  ERROR: {src.relative_to(PROJECT)} missing (run L01 first)")
    raise SystemExit(1)

annual = defaultdict(list)
with src.open() as f:
    reader = csv.reader(f)
    next(reader)  # header
    for row in reader:
        if len(row) < 2 or not row[0]:
            continue
        year = row[0][:4]
        try:
            val = float(row[1])
        except ValueError:
            continue
        annual[year].append(val)

with dst.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "S001"])
    for year in sorted(annual):
        avg = sum(annual[year]) / len(annual[year])
        w.writerow([year, f"{avg:.4f}"])
print(f"  Wrote {dst.relative_to(PROJECT)} ({len(annual)} years)")
