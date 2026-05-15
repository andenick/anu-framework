#!/usr/bin/env python3
"""
Variant Validator — Checks variant completeness and correctness
================================================================

Part of the Anu Variant Standard v1.0.

Validates that a registered variant has:
  1. Valid ID format
  2. Registry entry with complete fields
  3. VPR file exists and is non-trivial
  4. Output files exist at registered paths
  5. Benchmark values are defined
  6. Calculator script linkage is valid
  7. Config parameters are non-empty

Usage:
  python validate_variant.py --registry REGISTRY.json --id V-SW01-AS2
  python validate_variant.py --registry REGISTRY.json --all
"""

import json
import sys
import argparse
from pathlib import Path

# Import sibling module
sys.path.insert(0, str(Path(__file__).parent))
from variant_registry import VariantRegistry, VARIANT_ID_PATTERN


def validate_single(registry: VariantRegistry, variant_id: str, project_root: Path) -> dict:
    """Validate a single variant. Returns dict of check_name -> (passed, detail)."""
    checks = {}

    # 1. ID format
    valid_id = bool(VARIANT_ID_PATTERN.match(variant_id))
    checks["id_format"] = (valid_id, f"Pattern match: {valid_id}")

    # 2. Registry entry exists
    entry = registry.get_variant(variant_id)
    if entry is None:
        checks["registry_entry"] = (False, "Not found in registry")
        # Can't continue without entry
        return checks
    checks["registry_entry"] = (True, "Found")

    # 3. VPR file exists
    if entry.vpr_file:
        vpr_path = project_root / entry.vpr_file
        vpr_exists = vpr_path.exists()
        vpr_size = vpr_path.stat().st_size if vpr_exists else 0
        checks["vpr_exists"] = (vpr_exists, f"{'Found' if vpr_exists else 'Missing'}: {entry.vpr_file}")
        checks["vpr_nontrivial"] = (vpr_size > 500, f"Size: {vpr_size} bytes")
    else:
        checks["vpr_exists"] = (False, "No VPR path registered")
        checks["vpr_nontrivial"] = (False, "No VPR path registered")

    # 4. Output files exist
    if entry.output_files:
        all_exist = True
        details = []
        for label, rel_path in entry.output_files.items():
            full_path = project_root / rel_path
            exists = full_path.exists()
            if not exists:
                all_exist = False
            details.append(f"{label}: {'OK' if exists else 'MISSING'}")
        checks["output_files"] = (all_exist, "; ".join(details))
    else:
        checks["output_files"] = (False, "No output files registered")

    # 5. Config parameters
    has_config = bool(entry.config_parameters)
    n_params = len(entry.config_parameters) if has_config else 0
    checks["config_parameters"] = (has_config, f"{n_params} parameters")

    # 6. Benchmark values
    has_benchmarks = bool(entry.benchmark_values)
    n_benchmarks = len(entry.benchmark_values) if has_benchmarks else 0
    checks["benchmark_values"] = (has_benchmarks, f"{n_benchmarks} benchmark years")

    # 7. Calculator linkage
    if entry.calculator_script:
        script_path = project_root / entry.calculator_script
        script_exists = script_path.exists()
        checks["calculator_script"] = (script_exists, f"{'Found' if script_exists else 'Missing'}: {entry.calculator_script}")
    else:
        checks["calculator_script"] = (False, "No calculator script registered")

    # 8. Coverage defined
    start = entry.coverage.get("start_year", 0)
    end = entry.coverage.get("end_year", 0)
    checks["coverage"] = (start > 0 and end > start, f"{start}-{end}")

    # 9. Exactly one baseline per metric (informational)
    metric_variants = registry.get_metric_variants(entry.metric)
    baselines = [v for v in metric_variants if v.is_baseline]
    checks["baseline_uniqueness"] = (
        len(baselines) == 1,
        f"{len(baselines)} baseline(s) for metric {entry.metric}"
    )

    return checks


def print_validation(variant_id: str, checks: dict) -> bool:
    """Print validation results. Returns True if all pass."""
    print(f"\nValidation: {variant_id}")
    print("=" * 60)
    all_pass = True
    for name, (passed, detail) in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status:4s}] {name:<25s} {detail}")
    print("-" * 60)
    overall = "PASS" if all_pass else "FAIL"
    print(f"  Overall: {overall}")
    return all_pass


def main():
    parser = argparse.ArgumentParser(description="Validate variant completeness")
    parser.add_argument("--registry", required=True, help="Path to VARIANT_REGISTRY.json")
    parser.add_argument("--id", help="Variant ID to validate")
    parser.add_argument("--all", action="store_true", help="Validate all variants")
    parser.add_argument("--project-root", help="Project root (default: registry parent's parent)")
    args = parser.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.exists():
        print(f"ERROR: Registry not found: {reg_path}")
        sys.exit(1)

    registry = VariantRegistry(reg_path)
    registry.load()

    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        # Default: assume registry is at Project/Technical/catalogs/VARIANT_REGISTRY.json
        project_root = reg_path.parent.parent.parent

    results = {}

    if args.all:
        variants = registry.list_variants()
        for v in variants:
            checks = validate_single(registry, v.variant_id, project_root)
            results[v.variant_id] = print_validation(v.variant_id, checks)
    elif args.id:
        checks = validate_single(registry, args.id, project_root)
        results[args.id] = print_validation(args.id, checks)
    else:
        parser.print_help()
        sys.exit(1)

    # Summary
    if len(results) > 1:
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"  {passed}/{total} variants fully validated")
        for vid, ok in results.items():
            print(f"  {'PASS' if ok else 'FAIL'}: {vid}")

    all_ok = all(results.values())
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
