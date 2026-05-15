"""V01: Validate S001 against reference values from registry
====================
Phase:   Validation
Purpose: Check S001 hits the reference values declared in series_registry.json.
Inputs:  data/final-data/S001_indpro.csv, series_registry.json
Outputs: outputs/validation/V01_S001.json
"""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
reg = json.loads((PROJECT / "series_registry.json").read_text())
ref_values = reg["series"]["S001"]["reference_values"]
src = PROJECT / "data" / "final-data" / "S001_indpro.csv"

data = {}
with src.open() as f:
    reader = csv.reader(f); next(reader)
    for y, v in reader:
        data[y] = float(v)

results = {"series": "S001", "checks": []}
all_pass = True
for year, expected in ref_values.items():
    actual = data.get(year)
    if actual is None:
        results["checks"].append({"year": year, "status": "MISSING", "expected": expected})
        all_pass = False
        continue
    diff_pct = abs(actual - expected) / expected * 100 if expected else 0
    status = "PASS" if diff_pct < 5.0 else "FAIL"  # 5% tolerance
    if status == "FAIL":
        all_pass = False
    results["checks"].append({
        "year": year, "expected": expected, "actual": round(actual, 4),
        "diff_pct": round(diff_pct, 3), "status": status,
    })
results["status"] = "PASS" if all_pass else "FAIL"

out = PROJECT / "outputs" / "validation" / "V01_S001.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2))
print(f"  V01: {results['status']}  ({len(results['checks'])} ref values)")
if not all_pass:
    raise SystemExit(1)
