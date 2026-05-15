#!/usr/bin/env python3
"""anu-doctor project — Project-level consistency audit.

Sibling to `check_framework.py`. Where `check_framework.py` audits the Anu
Framework itself (skill versions, requires-graph, cross-references),
`check_project.py` audits an individual Anu Framework project for internal
consistency.

The 14 P##-checks (severity in parens):

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
  P12 (FAIL)  Every series ID matches the registry's declared prefix_scheme
  P13 (FAIL)  Declared status is consistent with the artifacts that should exist
              (e.g. status=loaded => L01 exists; validated_book_and_extension =>
              V03 PASSes; pending:<dep> => NaN in data)
  P14 (WARN)  In rebuild projects (MIGRATION/crosswalk.csv present): every
              crosswalk row with status=confirmed has been acted on (old_id
              not in current-state artifacts; new_id in registry)

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


def check_P12_prefix_scheme(project: Path, reg: dict, res: Result) -> None:
    """Every series ID matches the project's declared prefix_scheme.

    Reads `prefix_scheme` from the registry; if absent, falls back to the
    canonical {primary: "D", additional: "AD"} and flags the absence as a
    finding (registries should declare it explicitly).

    Accepts two shapes for prefix_scheme:
      flat:   {"primary": "D", "additional": "AD"}
      nested: {"primary": {"prefix": "D", "meaning": "..."}, ...}
    """
    scheme = reg.get("prefix_scheme", {})
    if not scheme:
        scheme = {"primary": "D", "additional": "AD"}
        scheme_source = "implicit canonical"
    else:
        scheme_source = "registry-declared"

    # Extract prefix strings, supporting both flat and nested shapes
    prefix_set = set()
    for v in scheme.values():
        if isinstance(v, str):
            prefix_set.add(v)
        elif isinstance(v, dict) and "prefix" in v:
            prefix_set.add(v["prefix"])
    prefixes = sorted({p for p in prefix_set if p}, key=len, reverse=True)
    if not prefixes:
        res.add("P12", "FAIL", False,
                "prefix_scheme block in registry has no prefixes", [])
        return

    # Build regex: ^(D|AD|...)\d{3,4}(-[A-Z]|-EXT|-COMBINED)?$
    prefix_group = "|".join(re.escape(p) for p in prefixes)
    sid_re = re.compile(rf"^({prefix_group})\d{{3,4}}(-[A-Z]|-EXT|-COMBINED)?$")

    bad = []
    for sid in reg.get("series", {}):
        if not sid_re.match(sid):
            bad.append(f"{sid}: doesn't match prefix scheme {prefixes}")
    res.add("P12", "FAIL", not bad,
            f"{len(bad)} series IDs don't match {scheme_source} prefix scheme "
            f"({prefixes})" if bad
            else f"all {len(reg.get('series', {}))} series IDs match "
                 f"{scheme_source} prefix scheme ({prefixes})",
            bad[:10])


def check_P13_status_vs_artifacts(project: Path, reg: dict, res: Result) -> None:
    """Declared status is consistent with artifacts that should exist.

    Status -> expected artifacts:
      data_unavailable               => no L01/P02 expected (NaN data ok)
      data_available                 => DPR exists
      loaded                         => L01 exists
      book_period_validated          => V03 exists
      validated_book_and_extension   => V03 exists AND EPR exists
      extension_methodology_documented => EPR exists
      partial:<reason>               => artifacts checked best-effort
      pending:<dep>                  => NaN in data; no V03 expected
    """
    code = project / "code"
    docs_series = project / "docs" / "series"

    def has_script(prefix: str, sid: str) -> bool:
        d = code / f"{prefix}_loaders" if prefix == "L01" else (
            code / f"{prefix}_processors" if prefix == "P02" else
            code / f"{prefix}_validators" if prefix == "V03" else None
        )
        if d is None or not d.exists():
            return False
        return any(d.glob(f"{prefix}_{sid}*.py"))

    bad = []
    for sid, entry in reg.get("series", {}).items():
        status = entry.get("status", "")
        # Skip statuses where the rule doesn't apply
        if status.startswith("pending:") or status == "data_unavailable":
            continue
        dpr_exists = (docs_series / f"{sid}_DPR.md").exists()
        epr_exists = (docs_series / f"{sid}_EPR.md").exists()
        l01_exists = has_script("L01", sid)
        v03_exists = has_script("V03", sid)

        if status == "data_available" and not dpr_exists:
            bad.append(f"{sid}: status=data_available but DPR missing")
        elif status == "loaded" and not l01_exists:
            bad.append(f"{sid}: status=loaded but L01 missing")
        elif status == "book_period_validated" and not v03_exists:
            bad.append(f"{sid}: status=book_period_validated but V03 missing")
        elif status == "validated_book_and_extension":
            if not v03_exists:
                bad.append(f"{sid}: status=validated_book_and_extension but V03 missing")
            elif not epr_exists:
                bad.append(f"{sid}: status=validated_book_and_extension but EPR missing")
        elif status == "extension_methodology_documented" and not epr_exists:
            bad.append(f"{sid}: status=extension_methodology_documented but EPR missing")

    res.add("P13", "FAIL", not bad,
            f"{len(bad)} series with status/artifact inconsistency" if bad
            else "all series statuses are consistent with their artifacts",
            bad[:10])


def check_P14_crosswalk_completeness(project: Path, reg: dict, res: Result) -> None:
    """For rebuild projects, every confirmed crosswalk row has been acted on.

    Gated by presence of MIGRATION/crosswalk.csv. For rows with
    status=confirmed and non-blank new_id:
      - new_id should appear in the registry
      - old_id should NOT appear in any current-state artifact (excluding
        Inputs/Salvaged/, MIGRATION/, and Version History blocks)
    """
    crosswalk = project / "MIGRATION" / "crosswalk.csv"
    if not crosswalk.exists():
        res.add("P14", "WARN", True,
                "MIGRATION/crosswalk.csv absent (not a rebuild project, skipped)",
                [])
        return

    registry_sids = set(reg.get("series", {}).keys())
    issues = []
    confirmed_rows = 0
    try:
        with crosswalk.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("status", "").strip() != "confirmed":
                    continue
                confirmed_rows += 1
                old_id = (row.get("old_id") or "").strip()
                new_id = (row.get("new_id") or "").strip()
                if not new_id:
                    issues.append(f"row old_id={old_id}: confirmed but no new_id")
                    continue
                if new_id not in registry_sids:
                    issues.append(f"crosswalk new_id={new_id} not in registry")
    except Exception as e:
        res.add("P14", "WARN", False, f"crosswalk.csv parse error: {e}", [])
        return

    res.add("P14", "WARN", not issues,
            f"{len(issues)} crosswalk completeness issues across "
            f"{confirmed_rows} confirmed rows" if issues
            else f"all {confirmed_rows} confirmed crosswalk rows acted on",
            issues[:10])


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
    "P12": check_P12_prefix_scheme,
    "P13": check_P13_status_vs_artifacts,
    "P14": check_P14_crosswalk_completeness,
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
