"""V02: Validate S002 growth rates against registry reference values
====================
Phase:   Validation
Purpose: Check S002 hits the documented growth observations.
Inputs:  data/final-data/S002_indpro_growth.csv, series_registry.json
Outputs: outputs/validation/V02_S002.json
"""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
reg = json.loads((PROJECT / "series_registry.json").read_text())
ref_values = reg["series"]["S002"]["reference_values"]
src = PROJECT / "data" / "final-data" / "S002_indpro_growth.csv"

data = {}
with src.open() as f:
    reader = csv.reader(f); next(reader)
    for y, v in reader:
        data[y] = float(v)

results = {"series": "S002", "checks": []}
all_pass = True
for year, expected in ref_values.items():
    actual = data.get(year)
    if actual is None:
        results["checks"].append({"year": year, "status": "MISSING", "expected": expected})
        all_pass = False
        continue
    abs_diff = abs(actual - expected)
    status = "PASS" if abs_diff < 1.0 else "FAIL"  # 1pp tolerance on growth
    if status == "FAIL":
        all_pass = False
    results["checks"].append({
        "year": year, "expected": expected, "actual": round(actual, 3),
        "abs_diff": round(abs_diff, 3), "status": status,
    })
results["status"] = "PASS" if all_pass else "FAIL"

out = PROJECT / "outputs" / "validation" / "V02_S002.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2))
print(f"  V02: {results['status']}  ({len(results['checks'])} ref values)")
if not all_pass:
    raise SystemExit(1)
