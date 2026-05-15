"""O01: Write Anu Chopped CSV (3-row format)
====================
Phase:   Output
Purpose: Combine S001 + S002 into a single Chopped CSV with metadata header.
Inputs:  data/final-data/S001_indpro.csv, S002_indpro_growth.csv, series_registry.json
Outputs: data/final-data/chopped.csv
"""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
reg = json.loads((PROJECT / "series_registry.json").read_text())

# Read both series
def read(name):
    out = {}
    with (PROJECT / "data" / "final-data" / name).open() as f:
        reader = csv.reader(f); next(reader)
        for y, v in reader:
            out[y] = v
    return out

s001 = read("S001_indpro.csv")
s002 = read("S002_indpro_growth.csv")
years = sorted(set(s001) | set(s002))

dst = PROJECT / "data" / "final-data" / "chopped.csv"
with dst.open("w", newline="") as f:
    w = csv.writer(f)
    # Row 1: metadata (units)
    w.writerow(["year",
                reg["series"]["S001"]["units"],
                reg["series"]["S002"]["units"]])
    # Row 2: column IDs
    w.writerow(["year", "S001", "S002"])
    # Row 3+: data
    for y in years:
        w.writerow([y, s001.get(y, ""), s002.get(y, "")])

print(f"  Wrote {dst.relative_to(PROJECT)} ({len(years)} years × 2 series)")
