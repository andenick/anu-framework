#!/usr/bin/env python3
"""anu-doctor project — Project-level consistency audit.

Sibling to `check_framework.py`. Where `check_framework.py` audits the Anu
Framework itself (skill versions, requires-graph, cross-references),
`check_project.py` audits an individual Anu Framework project for internal
consistency.

The 10 P##-checks (severity in parens):

  P01 (FAIL)  Every registry entry has a docs/series/<sid>_DPR.md
  P02 (FAIL)  Every L01_<sid>_*.py has a matching P02 and V03 (or the series
              is registered as derived and has no L01)
  P03 (FAIL)  Every research JSON's series_id matches a registry entry
  P04 (FAIL)  Every chopped CSV's Row 2 column IDs match the registry's
              subseries declarations
  P05 (FAIL)  No scripts reference a renamed/deleted series (stale refs)
  P06 (FAIL)  Every status field matches the standardized enum
              (anu-ingestion v4.1 schema)
  P07 (WARN)  Every series has data/intermediate/validation/<sid>.json
  P08 (WARN)  Provenance chain resolves end-to-end for every series
  P09 (FAIL)  No series has status: synthetic / estimated_from_benchmarks
  P10 (WARN)  Divergences from predecessor appear in DIVERGENCE_REGISTER.json

Usage:
  python check_project.py                 # audit cwd
  python check_project.py --project PATH  # audit a different project
  python check_project.py --check P01,P02 # run a subset of checks
  python check_project.py --strict        # fail on WARN-severity hits too

Part of the Anu Framework v11.0 — see anu-doctor/SKILL.md.

Derived from the RMWND build, where 10+ ad-hoc consistency cross-checks
were done by hand. This skill formalizes them.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


# Standardized status enum (anu-ingestion v4.1).
# Pattern allows "validated:<scope>" and "pending:<dep>" and "partial:<reason>".
VALID_STATUS_RE = re.compile(
    r"^(data_unavailable|data_available|loaded|"
    r"validated(:[a-z_0-9]+)?|"
    r"pending:[a-z_0-9]+|"
    r"partial:[a-z_0-9]+|"
    r"book_period_validated|"          # legacy — accepted but deprecated
    r"validated_book_and_extension(_partial)?|"  # legacy
    r"book_period_partial_[0-9_]+|"    # legacy
    r"pending_[a-z_]+|"                # legacy
    r"benchmark_only_matrix_derived"   # legacy
    r")$"
)

PROHIBITED_STATUS = {"synthetic", "estimated_from_benchmarks", "fabricated", "interpolated_only"}


class Result:
    def __init__(self) -> None:
        self.checks: dict[str, dict] = {}

    def add(self, check: str, severity: str, ok: bool, detail: str, items: list | None = None) -> None:
        self.checks[check] = {
            "severity": severity, "ok": ok, "detail": detail,
            "items": items or [],
        }


def load_registry(project: Path) -> dict | None:
    p = project / "series_registry.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# -------------------------- Checks --------------------------

def check_P01_dpr_coverage(project: Path, reg: dict, res: Result) -> None:
    """Every registry entry has docs/series/<sid>_DPR.md."""
    missing = []
    for sid in reg.get("series", {}):
        if not (project / "docs" / "series" / f"{sid}_DPR.md").exists():
            missing.append(sid)
    res.add("P01", "FAIL", not missing,
            f"{len(missing)} series missing DPR" if missing
            else f"all {len(reg.get('series', {}))} series have DPR",
            missing[:10])


def check_P02_lpv_triad(project: Path, reg: dict, res: Result) -> None:
    """Every L01 has matching P02 and V03 (derived series have P02+V03 but no L01)."""
    code = project / "code"
    if not code.exists():
        res.add("P02", "FAIL", False, "code/ directory missing", [])
        return
    l01_dir = code / "L01_loaders"
    p02_dir = code / "P02_processors"
    v03_dir = code / "V03_validators"
    l01 = {f.stem.replace("L01_", "") for f in l01_dir.glob("L01_*.py")} if l01_dir.exists() else set()
    p02 = {f.stem.replace("P02_", "") for f in p02_dir.glob("P02_*.py")} if p02_dir.exists() else set()
    v03 = {f.stem.replace("V03_", "") for f in v03_dir.glob("V03_*.py")} if v03_dir.exists() else set()

    # L01 must have matching P02 and V03
    orphaned_l01 = sorted(l01 - p02) + sorted(l01 - v03)
    # P02 without V03 = bad (every processor needs a validator)
    p02_no_v03 = sorted(p02 - v03)
    bad = list(dict.fromkeys(orphaned_l01 + p02_no_v03))
    res.add("P02", "FAIL", not bad,
            f"{len(bad)} L01/P02/V03 triad mismatches" if bad
            else f"all {len(p02)} processors have validators",
            bad[:10])


def check_P03_research_registry_align(project: Path, reg: dict, res: Result) -> None:
    """Every research JSON's series_id matches a registry entry."""
    research_dir = project / "research"
    if not research_dir.exists():
        res.add("P03", "WARN", True, "research/ directory absent (skipped)", [])
        return
    registry_sids = set(reg.get("series", {}).keys())
    stale = []
    for f in research_dir.glob("*_research.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            sid = r.get("series_id")
            if sid and sid not in registry_sids:
                stale.append(f"{f.name}: series_id={sid}")
        except Exception:
            stale.append(f"{f.name}: parse error")
    res.add("P03", "FAIL", not stale,
            f"{len(stale)} research JSONs reference unknown series" if stale
            else f"all research JSONs align to registry",
            stale[:10])


def check_P04_chopped_subseries_match(project: Path, reg: dict, res: Result) -> None:
    """Chopped CSV Row 2 column IDs match registry subseries declarations."""
    chopped_dir = project / "chopped"
    if not chopped_dir.exists():
        res.add("P04", "WARN", True, "chopped/ directory absent (skipped)", [])
        return
    mismatches = []
    for f in chopped_dir.glob("*.csv"):
        sid = f.stem
        entry = reg.get("series", {}).get(sid)
        if entry is None:
            continue
        registry_subs = set(entry.get("subseries", {}).keys())
        with f.open(encoding="utf-8") as fh:
            rdr = csv.reader(fh)
            try:
                next(rdr)            # Row 1 metadata
                ids_row = next(rdr)  # Row 2 column IDs
            except StopIteration:
                mismatches.append(f"{f.name}: file too short")
                continue
            # First column is 'Year'; rest should be subseries IDs
            csv_subs = {col.strip() for col in ids_row[1:] if col.strip()}
            extra = csv_subs - registry_subs
            missing = registry_subs - csv_subs
            if extra or missing:
                mismatches.append(f"{sid}: extra={extra} missing={missing}")
    res.add("P04", "FAIL", not mismatches,
            f"{len(mismatches)} chopped CSVs with subseries mismatch" if mismatches
            else "all chopped CSVs align to registry subseries",
            mismatches[:10])


def check_P05_no_stale_refs(project: Path, reg: dict, res: Result) -> None:
    """No scripts reference a renamed/deleted series.

    Approximation: scan all .py files under code/ for series-ID-looking
    tokens that don't appear in the registry.
    """
    registry_sids = set(reg.get("series", {}).keys())
    sid_re = re.compile(r"\b([SE]?S\d{3,4}|AS\d{3})\b")
    suspicious = []
    code_dir = project / "code"
    if not code_dir.exists():
        res.add("P05", "WARN", True, "code/ directory absent (skipped)", [])
        return
    for f in code_dir.rglob("*.py"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in sid_re.finditer(text):
            tok = m.group(1)
            # Strip suffix
            base = re.sub(r"-[A-Z0-9_]+$", "", tok)
            if base not in registry_sids:
                suspicious.append(f"{f.relative_to(project)}: references {tok}")
                break  # one per file is enough to surface
    res.add("P05", "FAIL", not suspicious,
            f"{len(suspicious)} scripts reference unknown series IDs" if suspicious
            else f"no stale series-ID references in code/",
            suspicious[:10])


def check_P06_status_taxonomy(project: Path, reg: dict, res: Result) -> None:
    """Every status matches the standardized enum (with legacy compatibility)."""
    bad = []
    for sid, entry in reg.get("series", {}).items():
        status = entry.get("status", "")
        if status and not VALID_STATUS_RE.match(status):
            bad.append(f"{sid}: status={status!r}")
    res.add("P06", "FAIL", not bad,
            f"{len(bad)} series with non-conforming status" if bad
            else f"all {len(reg.get('series', {}))} statuses conform to enum",
            bad[:10])


def check_P07_validation_artifacts(project: Path, reg: dict, res: Result) -> None:
    """Every series has data/intermediate/validation/<sid>.json (WARN)."""
    val_dir = project / "data" / "intermediate" / "validation"
    if not val_dir.exists():
        res.add("P07", "WARN", True, "validation/ directory absent (skipped)", [])
        return
    missing = []
    for sid in reg.get("series", {}):
        if not (val_dir / f"{sid}.json").exists():
            missing.append(sid)
    res.add("P07", "WARN", not missing,
            f"{len(missing)} series without validation artifacts" if missing
            else f"all series have validation artifacts",
            missing[:10])


def check_P08_provenance_chain(project: Path, reg: dict, res: Result) -> None:
    """Provenance chain end-to-end for every series (WARN)."""
    prov_path = project / "PROVENANCE_INDEX.json"
    if not prov_path.exists():
        res.add("P08", "WARN", True, "PROVENANCE_INDEX.json absent (skipped)", [])
        return
    prov = json.loads(prov_path.read_text(encoding="utf-8")).get("series", {})
    incomplete = []
    for sid in reg.get("series", {}):
        entry = prov.get(sid, {})
        if not entry.get("dpr") or not (entry.get("processor") or entry.get("loader")):
            incomplete.append(sid)
    res.add("P08", "WARN", not incomplete,
            f"{len(incomplete)} series with incomplete provenance chain" if incomplete
            else "all series have complete provenance chain",
            incomplete[:10])


def check_P09_no_synthetic(project: Path, reg: dict, res: Result) -> None:
    """No series has status: synthetic / estimated_from_benchmarks."""
    bad = []
    for sid, entry in reg.get("series", {}).items():
        status = entry.get("status", "")
        if status in PROHIBITED_STATUS:
            bad.append(f"{sid}: status={status!r}")
        if entry.get("data_quality") == "synthetic":
            bad.append(f"{sid}: data_quality=synthetic")
    # Also grep for np.random in code/
    code_dir = project / "code"
    if code_dir.exists():
        for f in code_dir.rglob("*.py"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"\bnp\.random\b", text):
                bad.append(f"{f.relative_to(project)}: contains np.random")
    res.add("P09", "FAIL", not bad,
            f"{len(bad)} synthetic-data markers found" if bad
            else "no synthetic-data markers (D13 prerequisite GREEN)",
            bad[:10])


def check_P10_divergences_logged(project: Path, reg: dict, res: Result) -> None:
    """Divergences appear in DIVERGENCE_REGISTER.json (WARN — register may be empty
    if there are no documented divergences, which is fine)."""
    dr_path = project / "DIVERGENCE_REGISTER.json"
    ad_hoc = (project / "MIGRATION").glob("divergences_*.md") if (project / "MIGRATION").exists() else []
    ad_hoc_list = list(ad_hoc)
    if not dr_path.exists() and ad_hoc_list:
        res.add("P10", "WARN", False,
                f"divergence ad-hoc docs exist ({[p.name for p in ad_hoc_list]}) but DIVERGENCE_REGISTER.json missing",
                [p.name for p in ad_hoc_list])
        return
    res.add("P10", "WARN", True,
            "divergence register present or no divergences",
            [])


CHECKS = {
    "P01": check_P01_dpr_coverage,
    "P02": check_P02_lpv_triad,
    "P03": check_P03_research_registry_align,
    "P04": check_P04_chopped_subseries_match,
    "P05": check_P05_no_stale_refs,
    "P06": check_P06_status_taxonomy,
    "P07": check_P07_validation_artifacts,
    "P08": check_P08_provenance_chain,
    "P09": check_P09_no_synthetic,
    "P10": check_P10_divergences_logged,
}


def run(project: Path, checks: list[str], strict: bool) -> int:
    reg = load_registry(project)
    if reg is None:
        print(f"ERROR: {project / 'series_registry.json'} not found.")
        return 2

    res = Result()
    for key in checks:
        if key not in CHECKS:
            print(f"  unknown check: {key}")
            continue
        CHECKS[key](project, reg, res)

    print("=" * 60)
    print(f"  anu-doctor project — {project}")
    print("=" * 60)
    print(f"  registry: {len(reg.get('series', {}))} series")
    print()

    fails = 0
    warns = 0
    for key in checks:
        if key not in res.checks: continue
        r = res.checks[key]
        status = "PASS" if r["ok"] else r["severity"]
        if not r["ok"]:
            if r["severity"] == "FAIL": fails += 1
            else: warns += 1
        print(f"  {key}  [{status}] {r['detail']}")
        if r["items"] and not r["ok"]:
            for item in r["items"][:5]:
                print(f"          - {item}")
            if len(r["items"]) > 5:
                print(f"          ...({len(r['items']) - 5} more)")

    print()
    print(f"  Summary: {fails} failures, {warns} warnings")
    print("=" * 60)

    if fails: return 1
    if strict and warns: return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="anu-doctor project — project consistency audit")
    p.add_argument("--project", default=".")
    p.add_argument("--check", default=",".join(CHECKS.keys()),
                   help="Comma-separated list of P##-checks to run (default: all)")
    p.add_argument("--strict", action="store_true", help="Fail on WARN-severity hits too")
    args = p.parse_args()
    checks = [c.strip() for c in args.check.split(",") if c.strip()]
    return run(Path(args.project).resolve(), checks, args.strict)


if __name__ == "__main__":
    sys.exit(main())
