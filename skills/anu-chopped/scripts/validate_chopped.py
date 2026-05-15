#!/usr/bin/env python3
r"""
Validate Anu Chopped CSVs (v2.0 dash notation).

Rules:
  V1: Row 1 exists and contains metadata strings
  V2: Row 2 exists and contains column IDs
  V3: First column is "Year" (Row 2) or empty (Row 1)
  V4: All column IDs match regex S\d{3}(-[A-Z]|-EXT|-COMBINED)? (v2.0 dash notation)
      S017 wide table: relax for columns beyond S017-Z (allow S017AA, S017AB, etc.)
  V5: All data cells (Row 3+) are numeric or empty
  V6: No duplicate column IDs in Row 2
  V7: Row 1 has same number of columns as Row 2

Usage:
  python validate_chopped.py path/to/file.csv
  python validate_chopped.py --dir path/to/chopped/ch02/
  python validate_chopped.py --dir path/to/chopped/ --catalog path/to/ANU_CHOPPED_CATALOG.json

Exit: 0 if all pass, 1 if any fail.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


# V4: Standard regex for S###, S###-A, S###-EXT, S###-COMBINED
COLUMN_ID_REGEX = re.compile(r"^S\d{3}(-[A-Z]|-EXT|-COMBINED)?$")

# S017 wide table: multi-letter subseries (S017AA, S017AB, ... S017GX)
# Relax V4 for columns beyond S017-Z
S017_MULTI_LETTER_REGEX = re.compile(r"^S017[A-Z]{2,}$")


def _is_s017_wide_table(row2: list[str]) -> bool:
    """True if this file appears to be S017 wide table (has S017-A or similar)."""
    for cell in row2:
        if cell and cell.startswith("S017"):
            return True
    return False


def _valid_column_id(cell: str, is_s017_wide: bool) -> bool:
    """Check if column ID is valid. Relax for S017 beyond S017-Z."""
    if not cell or not cell.strip():
        return True  # Empty cells (e.g. Year col in metadata) are ok for V4
    cell = cell.strip()
    if COLUMN_ID_REGEX.match(cell):
        return True
    if is_s017_wide and S017_MULTI_LETTER_REGEX.match(cell):
        return True
    return False


def _is_numeric_or_empty(s: str) -> bool:
    if s is None or (isinstance(s, str) and s.strip() == ""):
        return True
    try:
        float(s.strip())
        return True
    except (ValueError, TypeError):
        return False


def validate_file(path: Path) -> tuple[bool, dict[str, bool], list[str]]:
    """Validate a single Chopped CSV. Returns (all_pass, results dict, failure messages)."""
    failures: list[str] = []
    results: dict[str, bool] = {}

    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        failures.append(f"Could not read file: {e}")
        return False, {f"V{i}": False for i in range(1, 8)}, failures

    # V1: Row 1 exists
    if len(rows) < 1:
        results["V1"] = False
        failures.append("V1: Row 1 (metadata) missing")
    else:
        row1 = rows[0]
        results["V1"] = len(row1) > 0
        if not results["V1"]:
            failures.append("V1: Row 1 is empty")

    # V2: Row 2 exists
    if len(rows) < 2:
        results["V2"] = False
        if "V1" not in results or results["V1"]:
            failures.append("V2: Row 2 (column IDs) missing")
    else:
        row2 = rows[1]
        results["V2"] = len(row2) > 0
        if not results["V2"]:
            failures.append("V2: Row 2 is empty")

    if len(rows) < 2:
        for r in range(3, 8):
            results[f"V{r}"] = False
        return False, results, failures

    row1, row2 = rows[0], rows[1]
    is_s017_wide = _is_s017_wide_table(row2)

    # V3: First column is "Year" (Row 2) or empty (Row 1). Both rows may have "Year" or empty for the index column.
    first1 = (row1[0] if row1 else "").strip()
    first2 = (row2[0] if row2 else "").strip()
    v3_row1 = first1 == "" or first1.lower() == "year"
    v3_row2 = first2 == "" or first2.lower() == "year"
    results["V3"] = v3_row1 and v3_row2
    if not results["V3"]:
        if not v3_row1:
            failures.append(f"V3: Row 1 first column should be 'Year' or empty, got: {repr(first1)}")
        if not v3_row2:
            failures.append(f"V3: Row 2 first column should be 'Year' or empty, got: {repr(first2)}")

    # V4: All column IDs match regex (relax for S017 beyond S017-Z)
    invalid_ids = []
    for i, cell in enumerate(row2):
        c = (cell or "").strip()
        if not c:
            continue
        if not _valid_column_id(c, is_s017_wide):
            invalid_ids.append((i, c))
    results["V4"] = len(invalid_ids) == 0
    if not results["V4"]:
        failures.append(f"V4: Invalid column IDs: {[x[1] for x in invalid_ids]}")

    # V5: All data cells (Row 3+) are numeric or empty
    v5_ok = True
    for ri, r in enumerate(rows[2:], start=3):
        for ci, cell in enumerate(r):
            if not _is_numeric_or_empty(cell):
                v5_ok = False
                failures.append(f"V5: Non-numeric at row {ri} col {ci+1}: {repr(cell)[:50]}")
                break
        if not v5_ok and len(failures) > 5:
            break
    results["V5"] = v5_ok

    # V6: No duplicate column IDs in Row 2
    ids = [c.strip() for c in row2 if c and c.strip()]
    seen: dict[str, bool] = {}
    dups = []
    for c in ids:
        if c in seen:
            dups.append(c)
        seen[c] = True
    results["V6"] = len(dups) == 0
    if not results["V6"]:
        failures.append(f"V6: Duplicate column IDs: {dups}")

    # V7: Row 1 has same number of columns as Row 2
    n1, n2 = len(row1), len(row2)
    results["V7"] = n1 == n2
    if not results["V7"]:
        failures.append(f"V7: Row 1 has {n1} columns, Row 2 has {n2}")

    all_pass = all(results.get(f"V{i}", False) for i in range(1, 8))
    return all_pass, results, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Anu Chopped CSVs (v2.0)")
    parser.add_argument("path", nargs="?", help="Path to a single CSV file")
    parser.add_argument("--dir", "-d", help="Directory containing Chopped CSVs")
    parser.add_argument("--catalog", "-c", help="Path to generate/update ANU_CHOPPED_CATALOG.json")
    args = parser.parse_args()

    files: list[Path] = []
    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"Error: --dir {args.dir} is not a directory", file=sys.stderr)
            return 1
        files = sorted(d.glob("*.csv"))
    elif args.path:
        p = Path(args.path)
        if not p.exists():
            print(f"Error: {p} does not exist", file=sys.stderr)
            return 1
        if p.is_file():
            files = [p]
        else:
            print(f"Error: {p} is not a file", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    if not files:
        print("No CSV files found.", file=sys.stderr)
        return 1

    all_pass = True
    for fp in files:
        ok, results, failures = validate_file(fp)
        status = "PASS" if ok else "FAIL"
        print(f"\n{fp.name}: {status}")
        for r in range(1, 8):
            rule_ok = results.get(f"V{r}", False)
            print(f"  V{r}: {'PASS' if rule_ok else 'FAIL'}")
        if failures:
            for f in failures[:10]:
                print(f"  - {f}")
            if len(failures) > 10:
                print(f"  ... and {len(failures) - 10} more")
            all_pass = False

    if args.catalog and files:
        # Generate/update catalog (minimal: just list validated files)
        catalog_path = Path(args.catalog)
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        from datetime import date
        catalog = {
            "version": "2.0",
            "generated": date.today().isoformat(),
            "files": [{"filename": f.name, "validation_status": "PASS" if validate_file(f)[0] else "FAIL"} for f in files],
        }
        import json
        with open(catalog_path, "w", encoding="utf-8") as out:
            json.dump(catalog, out, indent=2)
        print(f"\nCatalog written to {catalog_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
