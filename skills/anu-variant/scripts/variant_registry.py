#!/usr/bin/env python3
"""
Variant Registry — Central catalog for methodological variants
================================================================

Part of the Anu Variant Standard v1.0.

Provides CRUD operations on VARIANT_REGISTRY.json files:
  - Register, update, list, validate, and summarize variants
  - Parse and validate Variant IDs (V-{DOMAIN}{METRIC}-{METHOD})
  - Export summary tables for reporting

Usage:
  python variant_registry.py init    --path REGISTRY.json --project "Project Name"
  python variant_registry.py register --path REGISTRY.json --id V-SW01-AS2 ...
  python variant_registry.py list    --path REGISTRY.json [--domain SW] [--metric SW01]
  python variant_registry.py get     --path REGISTRY.json --id V-SW01-AS2
  python variant_registry.py validate --path REGISTRY.json --id V-SW01-AS2
  python variant_registry.py summary --path REGISTRY.json
"""

import json
import re
import sys
import argparse
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ── Variant ID Pattern ─────────────────────────────────────────────────
VARIANT_ID_PATTERN = re.compile(r'^V-([A-Z]{2})(\d{2})-([A-Z0-9]{2,3})$')

DOMAIN_CODES = {
    "SW": "Social Wage",
    "PR": "Profit Rate",
    "EX": "Exploitation",
    "WG": "Wages",
    "CA": "Capital",
    "MP": "Market Prices",
    "IO": "Input-Output",
}


# ── VariantEntry Dataclass ─────────────────────────────────────────────

@dataclass
class VariantEntry:
    variant_id: str
    domain: str
    metric: str
    method_code: str
    name: str
    method_name: str
    description: str
    is_baseline: bool = False
    config_parameters: dict = field(default_factory=dict)
    source_series: dict = field(default_factory=dict)
    nipa_tables_used: list = field(default_factory=list)
    output_files: dict = field(default_factory=dict)
    coverage: dict = field(default_factory=lambda: {"start_year": 0, "end_year": 0, "book_period": ""})
    benchmark_values: dict = field(default_factory=dict)
    linked_series: list = field(default_factory=list)
    calculator_script: str = ""
    calculator_class: str = ""
    calculator_instance: str = ""
    vpr_file: str = ""
    created: str = ""
    last_computed: str = ""
    data_vintage: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "VariantEntry":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in known}
        return cls(**filtered)


# ── VariantRegistry ────────────────────────────────────────────────────

class VariantRegistry:
    """Manages a VARIANT_REGISTRY.json file."""

    def __init__(self, registry_path: Path):
        self.path = Path(registry_path)
        self._data = None

    def load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = self._empty_registry()
        return self._data

    def save(self) -> None:
        if self._data is None:
            raise RuntimeError("No data loaded. Call load() or init() first.")
        self._data["generated"] = datetime.now(timezone.utc).isoformat()
        self._data["total_variants"] = len(self._data.get("variants", {}))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def init(self, project: str) -> None:
        self._data = self._empty_registry(project=project)
        self.save()

    def register_variant(self, entry: VariantEntry) -> None:
        if self._data is None:
            self.load()
        if not self.validate_id(entry.variant_id):
            raise ValueError(f"Invalid variant ID: {entry.variant_id}")
        self._data["variants"][entry.variant_id] = entry.to_dict()
        # Ensure domain registry is populated
        if entry.domain not in self._data["domain_registry"]:
            self._data["domain_registry"][entry.domain] = {
                "name": DOMAIN_CODES.get(entry.domain, entry.domain),
                "metrics": {}
            }
        metric_key = f"{entry.domain}{entry.metric}" if not entry.metric.startswith(entry.domain) else entry.metric
        if metric_key not in self._data["domain_registry"][entry.domain]["metrics"]:
            self._data["domain_registry"][entry.domain]["metrics"][metric_key] = {
                "name": entry.name.split(" - ")[0] if " - " in entry.name else entry.name,
                "formula": ""
            }
        self.save()

    def get_variant(self, variant_id: str) -> Optional[VariantEntry]:
        if self._data is None:
            self.load()
        d = self._data.get("variants", {}).get(variant_id)
        if d is None:
            return None
        return VariantEntry.from_dict(d)

    def list_variants(self, domain: str = None, metric: str = None) -> list:
        if self._data is None:
            self.load()
        results = []
        for vid, vdata in self._data.get("variants", {}).items():
            if domain and vdata.get("domain") != domain:
                continue
            if metric and vdata.get("metric") != metric:
                continue
            results.append(VariantEntry.from_dict(vdata))
        return results

    def update_variant(self, variant_id: str, updates: dict) -> None:
        if self._data is None:
            self.load()
        if variant_id not in self._data.get("variants", {}):
            raise KeyError(f"Variant {variant_id} not found")
        self._data["variants"][variant_id].update(updates)
        self.save()

    def validate_id(self, variant_id: str) -> bool:
        return bool(VARIANT_ID_PATTERN.match(variant_id))

    def parse_id(self, variant_id: str) -> Optional[dict]:
        m = VARIANT_ID_PATTERN.match(variant_id)
        if not m:
            return None
        return {
            "domain": m.group(1),
            "metric_num": m.group(2),
            "method_code": m.group(3),
            "metric": f"{m.group(1)}{m.group(2)}",
        }

    def get_metric_variants(self, metric_code: str) -> list:
        """Get all variants for a metric code (e.g., 'SW01')."""
        return self.list_variants(metric=metric_code)

    def get_baseline(self, metric_code: str) -> Optional[VariantEntry]:
        """Get the baseline variant for a metric."""
        for v in self.get_metric_variants(metric_code):
            if v.is_baseline:
                return v
        return None

    def update_computation_timestamp(self, variant_id: str, vintage: str = "") -> None:
        updates = {"last_computed": datetime.now(timezone.utc).isoformat()}
        if vintage:
            updates["data_vintage"] = vintage
        self.update_variant(variant_id, updates)

    def export_summary(self):
        """Export a summary table. Returns a pandas DataFrame if available, else list of dicts."""
        if self._data is None:
            self.load()
        rows = []
        for vid, vdata in self._data.get("variants", {}).items():
            rows.append({
                "variant_id": vid,
                "name": vdata.get("name", ""),
                "domain": vdata.get("domain", ""),
                "metric": vdata.get("metric", ""),
                "method_code": vdata.get("method_code", ""),
                "is_baseline": vdata.get("is_baseline", False),
                "coverage": f"{vdata.get('coverage', {}).get('start_year', '')}-{vdata.get('coverage', {}).get('end_year', '')}",
                "last_computed": vdata.get("last_computed", ""),
                "data_vintage": vdata.get("data_vintage", ""),
                "vpr_file": vdata.get("vpr_file", ""),
            })
        if HAS_PANDAS:
            return pd.DataFrame(rows)
        return rows

    @staticmethod
    def _empty_registry(project: str = "") -> dict:
        return {
            "anu_variant_version": "1.0",
            "project": project,
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_variants": 0,
            "domain_registry": {},
            "variants": {},
            "cross_variant_comparisons": [],
            "vintage_tracking": {},
        }


# ── CLI ────────────────────────────────────────────────────────────────

def cli_init(args):
    reg = VariantRegistry(args.path)
    reg.init(project=args.project)
    print(f"Initialized registry: {args.path}")

def cli_register(args):
    reg = VariantRegistry(args.path)
    reg.load()
    parsed = reg.parse_id(args.id)
    if not parsed:
        print(f"ERROR: Invalid variant ID '{args.id}'")
        sys.exit(1)
    entry = VariantEntry(
        variant_id=args.id,
        domain=parsed["domain"],
        metric=parsed["metric"],
        method_code=parsed["method_code"],
        name=args.name or args.id,
        method_name=args.method_name or parsed["method_code"],
        description=args.description or "",
        is_baseline=args.baseline,
        created=datetime.now(timezone.utc).isoformat(),
    )
    if args.config:
        entry.config_parameters = json.loads(args.config)
    reg.register_variant(entry)
    print(f"Registered: {args.id} ({entry.name})")

def cli_list(args):
    reg = VariantRegistry(args.path)
    reg.load()
    variants = reg.list_variants(domain=args.domain, metric=args.metric)
    if not variants:
        print("No variants found.")
        return
    print(f"{'ID':<15} {'Name':<40} {'Baseline':<10} {'Coverage':<15}")
    print("-" * 80)
    for v in variants:
        cov = f"{v.coverage.get('start_year', '?')}-{v.coverage.get('end_year', '?')}"
        bl = "YES" if v.is_baseline else ""
        print(f"{v.variant_id:<15} {v.name:<40} {bl:<10} {cov:<15}")

def cli_get(args):
    reg = VariantRegistry(args.path)
    reg.load()
    v = reg.get_variant(args.id)
    if not v:
        print(f"Variant {args.id} not found.")
        sys.exit(1)
    print(json.dumps(v.to_dict(), indent=2))

def cli_validate(args):
    reg = VariantRegistry(args.path)
    reg.load()
    vid = args.id
    if not reg.validate_id(vid):
        print(f"FAIL: Invalid variant ID format: {vid}")
        sys.exit(1)
    v = reg.get_variant(vid)
    if not v:
        print(f"FAIL: Variant {vid} not found in registry")
        sys.exit(1)

    checks = []
    # ID format
    checks.append(("ID format valid", True))
    # Registry entry
    checks.append(("Registry entry exists", True))
    # VPR file
    vpr_exists = v.vpr_file and Path(v.vpr_file).exists()
    checks.append(("VPR file exists", vpr_exists))
    # Output files
    outputs_ok = True
    for label, path in v.output_files.items():
        if not Path(path).exists():
            outputs_ok = False
            break
    checks.append(("Output files exist", outputs_ok))
    # Config parameters
    checks.append(("Config parameters defined", bool(v.config_parameters)))
    # Benchmark values
    checks.append(("Benchmark values defined", bool(v.benchmark_values)))

    print(f"Validation: {vid}")
    print("-" * 50)
    all_pass = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {label}")
    print("-" * 50)
    print(f"Overall: {'PASS' if all_pass else 'FAIL'}")
    return all_pass

def cli_summary(args):
    reg = VariantRegistry(args.path)
    reg.load()
    summary = reg.export_summary()
    if HAS_PANDAS:
        print(summary.to_string(index=False))
    else:
        for row in summary:
            print(row)


def main():
    parser = argparse.ArgumentParser(description="Anu Variant Registry Manager")
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize a new registry")
    p_init.add_argument("--path", required=True, help="Path to VARIANT_REGISTRY.json")
    p_init.add_argument("--project", required=True, help="Project name")

    # register
    p_reg = sub.add_parser("register", help="Register a variant")
    p_reg.add_argument("--path", required=True)
    p_reg.add_argument("--id", required=True, help="Variant ID (e.g., V-SW01-AS2)")
    p_reg.add_argument("--name", help="Display name")
    p_reg.add_argument("--method-name", help="Method display name")
    p_reg.add_argument("--description", help="Full description")
    p_reg.add_argument("--baseline", action="store_true", help="Mark as baseline")
    p_reg.add_argument("--config", help="JSON config parameters")

    # list
    p_list = sub.add_parser("list", help="List variants")
    p_list.add_argument("--path", required=True)
    p_list.add_argument("--domain", help="Filter by domain code")
    p_list.add_argument("--metric", help="Filter by metric code")

    # get
    p_get = sub.add_parser("get", help="Get variant details")
    p_get.add_argument("--path", required=True)
    p_get.add_argument("--id", required=True)

    # validate
    p_val = sub.add_parser("validate", help="Validate a variant")
    p_val.add_argument("--path", required=True)
    p_val.add_argument("--id", required=True)

    # summary
    p_sum = sub.add_parser("summary", help="Export summary table")
    p_sum.add_argument("--path", required=True)

    args = parser.parse_args()

    commands = {
        "init": cli_init,
        "register": cli_register,
        "list": cli_list,
        "get": cli_get,
        "validate": cli_validate,
        "summary": cli_summary,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
