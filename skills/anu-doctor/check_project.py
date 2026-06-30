#!/usr/bin/env python3
"""anu-doctor project — Project-level consistency audit.

Sibling to `check_framework.py`. Where `check_framework.py` audits the Anu
Framework itself (skill versions, requires-graph, cross-references),
`check_project.py` audits an individual Anu Framework project for internal
consistency.

The 38 P##-checks (P01-P39; P11 is a skipped number) — severity in parens:

  P01 (FAIL)  Every registry entry has a docs/series/<sid>_DPR.md
  P02 (FAIL)  Every L01_<sid>_*.py has a matching P02 and V03 (or the series
              is registered as derived and has no L01)
  P03 (FAIL)  Every research JSON's series_id matches a registry entry
  P04 (FAIL)  Every chopped CSV's Row 2 column IDs match the registry's
              subseries declarations (pipeline-stage-aware: -EXT/-COMBINED
              exempt when extension stage incomplete)
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
  P21 (FAIL)  Every series entry has minimum required fields
  P22 (WARN)  Subseries IDs follow naming conventions
  P23 (WARN)  Series-to-downstream artifact correspondence matrix
  P24 (WARN)  ANU_LEDGER.generated is fresh relative to STEP_LOG and PIPELINE_STATE
  P25 (FAIL)  ANU_LEDGER.series_inventory size matches registry series count
  P26 (FAIL)  Stage transitions in PIPELINE_STATE are backed by STEP_LOG entries
  P27 (FAIL)  framework_audit.anu_doctor_status != "not_run" when any stage > 0 is complete
  P28 (WARN)  Decision documents follow NNNN_*.md numbering and approval-timestamp convention
  P29 (WARN)  Registry year_range matches chopped CSV min/max year per series
  P30 (WARN)  Registry top-level by_status/by_content_type rollups match per-series data
  P31 (WARN)  DPR markdown Status line matches registry series[sid].status
  P32 (FAIL)  V03 hardcoded reference values match registry validation.reference_values
  P33 (WARN)  Inputs/ contains no nested .git directories
  P34 (WARN)  Top-level figures are referenced by at least one series
  P35 (WARN)  PROJECT_INDEX.md exists at project root
  P36 (FAIL)  Extension binary invariant: subseries with -EXT iff extension block populated
  P37 (FAIL)  Every Inputs/Robin/[SOURCE]/ has a valid PROVENANCE.md (schema)
  P38 (FAIL)  Every Inputs/Robin/ checkout's file SHA-256s match PROVENANCE
              (strict — re-hashes every file; slow on large checkouts)
  P39 (WARN)  No code hardcodes Council/Robin/DATA/ paths (read via Inputs/Robin/ instead)

Usage:
  python check_project.py                 # audit cwd
  python check_project.py --project PATH  # audit a different project
  python check_project.py --check P01,P02 # run a subset of checks
  python check_project.py --strict        # fail on WARN-severity hits too

Part of the Anu Framework v12.0 — see anu-doctor/SKILL.md.

Derived from the reference-replication build, where 10+ ad-hoc consistency cross-checks
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
    r"benchmark_only_matrix_derived|"  # legacy
    r"study_complete|"
    r"extension_methodology_documented"
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
    l01 = {f.stem.replace("L01_", "") for f in l01_dir.glob("L01_*.py")
           if not f.stem.startswith("shared_")} if l01_dir.exists() else set()
    p02 = {f.stem.replace("P02_", "") for f in p02_dir.glob("P02_*.py")} if p02_dir.exists() else set()
    v03 = {f.stem.replace("V03_", "") for f in v03_dir.glob("V03_*.py")} if v03_dir.exists() else set()

    # data_unavailable series legitimately have no data and therefore need no
    # L01/P02/V03 triad — exempt them from triad-completeness.
    data_unavailable = {
        sid for sid, e in reg.get("series", {}).items()
        if (e.get("status") or "").startswith("data_unavailable")
    }
    # L01 must have matching P02 and V03
    orphaned_l01 = sorted(l01 - p02) + sorted(l01 - v03)
    # P02 without V03 = bad (every processor needs a validator)
    p02_no_v03 = sorted(p02 - v03)
    bad = [x for x in dict.fromkeys(orphaned_l01 + p02_no_v03)
           if x not in data_unavailable]
    res.add("P02", "FAIL", not bad,
            f"{len(bad)} L01/P02/V03 triad mismatches" if bad
            else f"all {len(p02)} processors have validators "
                 f"({len(data_unavailable)} data_unavailable series exempt)",
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


def _extension_stage_complete(project: Path) -> bool:
    """Check PIPELINE_STATE.json to determine if extension (stage 4) has completed."""
    ps_path = project / "PIPELINE_STATE.json"
    if not ps_path.exists():
        return True  # no pipeline state => strict mode
    try:
        ps = json.loads(ps_path.read_text(encoding="utf-8"))
    except Exception:
        return True
    stages = ps.get("stages", ps.get("pipeline", {}))
    for key in ("extension", "stage_4", "EXTENSION", "4"):
        stage = stages.get(key, {})
        if isinstance(stage, dict):
            if stage.get("status") == "complete":
                return True
            if stage.get("completed") is True:
                return True
            if stage.get("state") == "complete":
                return True
    return False


def check_P04_chopped_subseries_match(project: Path, reg: dict, res: Result) -> None:
    """Chopped CSV format matches registry subseries declarations.

    Format-aware per Decision 0005 (chopped_format: wide|long):
      - wide-form (default): Row 1 metadata, Row 2 subseries IDs, Row 3+ data.
        Validates that Row 2 columns match registry subseries.
      - long-form: Row 1 column headers, Row 2+ data with subseries_id column.
        Validates that the distinct subseries_id values in column 3 match registry.
    """
    chopped_dir = project / "chopped"
    if not chopped_dir.exists():
        res.add("P04", "WARN", True, "chopped/ directory absent (skipped)", [])
        return

    chopped_format = (reg.get("chopped_format") or "wide").lower()
    ext_complete = _extension_stage_complete(project)
    mismatches = []
    warnings = []
    for f in chopped_dir.glob("*.csv"):
        sid = f.stem
        entry = reg.get("series", {}).get(sid)
        if entry is None:
            continue
        registry_subs = set(entry.get("subseries", {}).keys())
        with f.open(encoding="utf-8") as fh:
            rdr = csv.reader(fh)
            try:
                row1 = next(rdr)
            except StopIteration:
                mismatches.append(f"{f.name}: file too short")
                continue

            # Format detection: if Row 1 column 0 is 'year' (case-insensitive), it's long-form
            if row1 and row1[0].strip().lower() == "year" or chopped_format == "long":
                # Long-form: scan column 3 (subseries_id) for distinct values
                # row1 is the header; columns: year, value, subseries_id, source_id, units
                csv_subs = set()
                for row in rdr:
                    if len(row) >= 3 and row[2].strip():
                        csv_subs.add(row[2].strip())
            else:
                # Wide-form: Row 2 is column IDs
                try:
                    ids_row = next(rdr)
                except StopIteration:
                    mismatches.append(f"{f.name}: file too short for wide-form")
                    continue
                csv_subs = {col.strip() for col in ids_row[1:] if col.strip()}
            extra = csv_subs - registry_subs
            missing = registry_subs - csv_subs

            # cross_sectional series store one long-form subseries_id per
            # category (industry, country, ...). Those category IDs extend a
            # declared subseries (e.g. S705-A-Accom under declared S705-A) and
            # are data, not registry-declared subseries — a category that
            # prefixes onto a declared subseries (or the series id) is not an
            # "extra". Only flag categories that prefix nothing declared.
            if entry.get("content_type") == "cross_sectional":
                declared_prefixes = registry_subs | {sid}
                extra = {
                    e for e in extra
                    if not any(e == d or e.startswith(d + "-") for d in declared_prefixes)
                }
                # a declared subseries is satisfied if >=1 CSV category extends it
                missing = {
                    d for d in missing
                    if not any(c.startswith(d + "-") for c in csv_subs)
                }

            if extra:
                mismatches.append(f"{sid}: extra in CSV={extra}")

            if missing:
                if not ext_complete:
                    exempt = {s for s in missing if s.endswith(("-EXT", "-COMBINED"))}
                    hard_missing = missing - exempt
                    if hard_missing:
                        mismatches.append(f"{sid}: missing from CSV={hard_missing}")
                    if exempt:
                        warnings.append(f"{sid}: extension not complete, exempt={exempt}")
                else:
                    mismatches.append(f"{sid}: missing from CSV={missing}")

    items = mismatches + [f"(WARN) {w}" for w in warnings]
    res.add("P04", "FAIL", not mismatches,
            f"{len(mismatches)} chopped CSVs with subseries mismatch"
            + (f" (+{len(warnings)} extension-exempt warnings)" if warnings else "")
            if mismatches or warnings
            else "all chopped CSVs align to registry subseries",
            items[:10])


def _code_only_text(src: str) -> str:
    """Return source with COMMENT and STRING tokens stripped.

    Series-ID mentions inside docstrings/comments are informational
    (e.g. predecessor-ID lineage notes), not live code references — P05
    must not flag them. Falls back to raw text if the file won't tokenize.
    """
    import io
    import tokenize
    # COMMENT + STRING + (Python 3.12+) f-string content tokens are all
    # "not live code" — series-ID mentions inside them are informational.
    skip = {tokenize.COMMENT, tokenize.STRING}
    for _name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        _t = getattr(tokenize, _name, None)
        if _t is not None:
            skip.add(_t)
    out: list[str] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in skip:
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src
    return " ".join(out)


def check_P05_no_stale_refs(project: Path, reg: dict, res: Result) -> None:
    """No *live code* references a renamed/deleted series (WARN).

    Scans .py files under code/ for series-ID-looking tokens absent from the
    registry. COMMENT and STRING tokens are excluded — predecessor-ID mentions
    in docstrings/comments are informational lineage, not stale references.
    Severity is WARN: a surfaced token is usually a docstring artifact, not a bug.
    """
    registry_sids = set(reg.get("series", {}).keys())
    sid_re = re.compile(r"\b([SE]?S\d{3,4}|AS\d{3})\b")
    suspicious = []
    code_dir = project / "code"
    if not code_dir.exists():
        res.add("P05", "WARN", True, "code/ directory absent (skipped)", [])
        return
    for f in code_dir.rglob("*.py"):
        text = _code_only_text(f.read_text(encoding="utf-8", errors="ignore"))
        for m in sid_re.finditer(text):
            tok = m.group(1)
            # Strip suffix
            base = re.sub(r"-[A-Z0-9_]+$", "", tok)
            if base not in registry_sids:
                suspicious.append(f"{f.relative_to(project)}: references {tok}")
                break  # one per file is enough to surface
    res.add("P05", "WARN", not suspicious,
            f"{len(suspicious)} scripts reference unknown series IDs in live code" if suspicious
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
    """No series has status: synthetic / estimated_from_benchmarks.

    np.random is anti-fabrication-forbidden in empirical loaders, but is allowed
    in `theoretical` series (rendering analytical curves from declared parameters).
    Such files MUST be matched to a series whose `content_type == "theoretical"`
    AND must use a seeded RNG (np.random.default_rng(SEED) or np.random.seed(...)).
    """
    bad = []
    for sid, entry in reg.get("series", {}).items():
        status = entry.get("status", "")
        if status in PROHIBITED_STATUS:
            bad.append(f"{sid}: status={status!r}")
        if entry.get("data_quality") == "synthetic":
            bad.append(f"{sid}: data_quality=synthetic")

    # Build a lookup of which SIDs are theoretical
    theoretical_sids = {
        sid for sid, e in reg.get("series", {}).items()
        if e.get("content_type") == "theoretical"
    }

    code_dir = project / "code"
    if code_dir.exists():
        # SID may be terminal in compact-form filenames (L01_S1301.py — stem
        # "L01_S1301") or followed by _/. in descriptive legacy names.
        sid_in_filename_re = re.compile(r"_([A-Z]{1,3}\d{3,4})(?:_|\.|$)")
        seeded_rng_re = re.compile(
            r"np\.random\.default_rng\s*\(\s*(?:SEED|seed|\d+)\b"
            r"|np\.random\.seed\s*\(\s*(?:SEED|seed|\d+)\b"
        )
        for f in code_dir.rglob("*.py"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            if not re.search(r"\bnp\.random\b", text):
                continue
            # Identify which series this script belongs to from the filename
            m = sid_in_filename_re.search(f.stem)
            file_sid = m.group(1) if m else None
            if file_sid in theoretical_sids and seeded_rng_re.search(text):
                continue  # exempt: theoretical illustration with declared seed
            bad.append(f"{f.relative_to(project)}: contains np.random"
                       + (f" (series {file_sid} is theoretical but RNG is not declared-seeded — review)"
                          if file_sid in theoretical_sids else ""))
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
    canonical {primary: "D", extra: "XS"} (Series ID Spec v2.2) and flags
    the absence as a finding (registries should declare it explicitly).

    Legacy prefixes AS/ES/AD (pre-v2.2) are rejected even if declared —
    projects carrying them must run the AS/ES->XS migrate-scheme recipe.

    Accepts two shapes for prefix_scheme:
      flat:   {"primary": "D", "extra": "XS"}
      nested: {"primary": {"prefix": "D", "meaning": "..."}, ...}
    """
    LEGACY_PREFIXES = ("AS", "ES", "AD")
    scheme = reg.get("prefix_scheme", {})
    if not scheme:
        scheme = {"primary": "D", "extra": "XS"}
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

    # Legacy prefixes are invalid even when a registry still declares them.
    declared_legacy = [p for p in prefixes if p in LEGACY_PREFIXES]
    prefixes = [p for p in prefixes if p not in LEGACY_PREFIXES]
    if not prefixes:
        res.add("P12", "FAIL", False,
                f"prefix_scheme declares only legacy prefixes "
                f"{declared_legacy} (run AS/ES->XS migrate-scheme)", [])
        return

    # Build regex: ^(D|XS|...)\d{3,4}(-[A-Z]|-EXT|-COMBINED)?$
    prefix_group = "|".join(re.escape(p) for p in prefixes)
    sid_re = re.compile(rf"^({prefix_group})\d{{3,4}}(-[A-Z]|-EXT|-COMBINED)?$")
    legacy_re = re.compile(r"^(AS|ES|AD)\d")

    bad = []
    for sid in reg.get("series", {}):
        if legacy_re.match(sid):
            bad.append(f"{sid}: legacy AS/ES/AD prefix (Series ID Spec v2.2 "
                       f"requires XS; run migrate-scheme)")
        elif not sid_re.match(sid):
            bad.append(f"{sid}: doesn't match prefix scheme {prefixes}")
    if declared_legacy and not bad:
        bad.append(f"prefix_scheme still declares legacy prefixes "
                    f"{declared_legacy}")
    res.add("P12", "FAIL", not bad,
            f"{len(bad)} series IDs don't match {scheme_source} prefix scheme "
            f"({prefixes}) or carry legacy AS/ES/AD prefixes" if bad
            else f"all {len(reg.get('series', {}))} series IDs match "
                 f"{scheme_source} prefix scheme ({prefixes}), no legacy prefixes",
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
        elif status == "study_complete":
            if not epr_exists:
                bad.append(f"{sid}: status=study_complete but EPR missing")

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


def check_P15_build_manifest(project: Path, reg: dict, res: Result) -> None:
    """Technical/Build/ANU_BUILD_MANIFEST.json exists and is valid JSON."""
    manifest = project / "Build" / "ANU_BUILD_MANIFEST.json"
    if not manifest.exists():
        res.add("P15", "WARN", False, "Build/ANU_BUILD_MANIFEST.json missing (anu-build not initialized)", [])
        return
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        schema_ok = data.get("schema_version", "").startswith("anu-build-manifest")
        res.add("P15", "FAIL", schema_ok,
                f"manifest schema_version='{data.get('schema_version')}' (expected anu-build-manifest-*)"
                if not schema_ok else "Build manifest valid",
                [])
    except Exception as e:
        res.add("P15", "FAIL", False, f"manifest parse error: {e}", [])


def check_P16_subseries_plan(project: Path, reg: dict, res: Result) -> None:
    """SUBSERIES_PLAN.json topo-sort is acyclic and covers every subseries."""
    plan_path = project / "Build" / "SUBSERIES_PLAN.json"
    if not plan_path.exists():
        res.add("P16", "WARN", False, "Build/SUBSERIES_PLAN.json missing", [])
        return
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan_subs = set()
        for layer in plan.get("layers", []):
            plan_subs.update(layer.get("subseries", []))
        registry_subs = set()
        for sid, entry in reg.get("series", {}).items():
            for sub_id in entry.get("subseries", {}):
                registry_subs.add(sub_id)
        missing = registry_subs - plan_subs
        res.add("P16", "FAIL", not missing or len(missing) < 5,
                f"{len(missing)} subseries in registry but not in plan" if missing
                else f"plan covers all {len(plan_subs)} subseries",
                sorted(list(missing))[:10])
    except Exception as e:
        res.add("P16", "FAIL", False, f"SUBSERIES_PLAN parse error: {e}", [])


def check_P17_schema_versions(project: Path, reg: dict, res: Result) -> None:
    """LEDGER and PIPELINE_STATE schema_version match framework."""
    issues = []
    ledger_path = project / "ANU_LEDGER.json"
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        sv = ledger.get("schema_version", ledger.get("registry_version", "unknown"))
        if "v12" not in sv and "12.0" not in sv:
            issues.append(f"LEDGER schema_version={sv} (expected v12.0)")
    pipeline_path = project / "PIPELINE_STATE.json"
    if pipeline_path.exists():
        ps = json.loads(pipeline_path.read_text(encoding="utf-8"))
        sv = ps.get("schema_version", "unknown")
        if "v12" not in sv and "12.0" not in sv:
            issues.append(f"PIPELINE_STATE schema_version={sv} (expected v12.0)")
    res.add("P17", "WARN", not issues,
            "; ".join(issues) if issues else "schema versions match v12.0",
            issues)


def check_P18_step_log_valid(project: Path, reg: dict, res: Result) -> None:
    """Every entry in STEP_LOG.jsonl parses as valid JSON."""
    log_path = project / "Build" / "STEP_LOG.jsonl"
    if not log_path.exists():
        res.add("P18", "WARN", False, "STEP_LOG.jsonl missing", [])
        return
    bad_lines = []
    total = 0
    for i, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        total += 1
        try:
            json.loads(line)
        except Exception:
            bad_lines.append(f"line {i}")
    res.add("P18", "FAIL", not bad_lines,
            f"{len(bad_lines)} unparseable lines in STEP_LOG.jsonl ({total} total)" if bad_lines
            else f"all {total} STEP_LOG entries valid",
            bad_lines[:10])


def _ledger_artifact_present(ledger: dict, sid: str, artifact: str) -> bool:
    """True if the ledger records the named artifact for the series.

    Tolerates three different ledger shapes seen in the wild:
      A) flat / per-series:  ledger.artifacts[sid][artifact] = bool
      B) per-series wrap:    ledger.series_inventory[sid].artifacts[artifact] = bool
      C) artifact-major:     ledger.artifacts[artifact][sid] = path  (existence => True)
    """
    arts_a = (ledger.get("artifacts") or {}).get(sid)
    if isinstance(arts_a, dict) and isinstance(arts_a.get(artifact), bool):
        return arts_a[artifact]
    inv_b = (ledger.get("series_inventory") or {}).get(sid)
    if isinstance(inv_b, dict):
        sub = inv_b.get("artifacts") or {}
        if isinstance(sub.get(artifact), bool):
            return sub[artifact]
    art_c = (ledger.get("artifacts") or {}).get(artifact)
    if isinstance(art_c, dict) and sid in art_c:
        return True
    return False


def check_P19_loader_ledger_sync(project: Path, reg: dict, res: Result) -> None:
    """Every series with a non-stub L01 has loader=true in the ledger."""
    ledger_path = project / "ANU_LEDGER.json"
    if not ledger_path.exists():
        res.add("P19", "WARN", False, "ANU_LEDGER.json missing", [])
        return
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    l01_dir = project / "code" / "L01_loaders"
    if not l01_dir.exists():
        res.add("P19", "WARN", True, "code/L01_loaders/ absent (skipped)", [])
        return
    issues = []
    for f in l01_dir.glob("L01_*.py"):
        content = f.read_text(encoding="utf-8", errors="ignore")
        is_stub = "stub" in content[:200].lower() or "scaffold" in content[:200].lower() or "placeholder" in content[:200].lower()
        if is_stub:
            continue
        sid_match = re.search(r"L01_([A-Z]+\d+)", f.stem)
        if not sid_match:
            continue
        sid = sid_match.group(1)
        if not _ledger_artifact_present(ledger, sid, "loader"):
            issues.append(f"{sid}: non-stub L01 exists but ledger records no loader")
    res.add("P19", "WARN", not issues,
            f"{len(issues)} loader/ledger sync issues" if issues
            else "all non-stub L01s reflected in ledger",
            issues[:10])


def check_P20_cascade_consistency(project: Path, reg: dict, res: Result) -> None:
    """BUILD_NARRATIVE last-entry timestamp approximates STEP_LOG last-entry timestamp."""
    log_path = project / "Build" / "STEP_LOG.jsonl"
    narr_path = project / "Build" / "BUILD_NARRATIVE.md"
    if not log_path.exists() or not narr_path.exists():
        res.add("P20", "WARN", False,
                "STEP_LOG or BUILD_NARRATIVE missing (cascade not initialized)", [])
        return
    lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        res.add("P20", "WARN", True, "STEP_LOG empty (nothing to check)", [])
        return
    try:
        last_entry = json.loads(lines[-1])
        log_ts = last_entry.get("ts", "")
    except Exception:
        log_ts = ""
    narr_text = narr_path.read_text(encoding="utf-8")
    narr_timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", narr_text)
    if not narr_timestamps:
        res.add("P20", "WARN", False, "BUILD_NARRATIVE has no timestamps", [])
        return
    narr_last = narr_timestamps[-1]
    log_prefix = log_ts[:16] if log_ts else ""
    ok = narr_last == log_prefix if log_prefix else True
    res.add("P20", "WARN", ok,
            f"NARRATIVE last ts={narr_last} vs STEP_LOG last ts={log_prefix}" if not ok
            else "cascade timestamps consistent",
            [])


VALID_CONTENT_TYPES = {"time_series", "cross_sectional", "theoretical", "derived"}


def check_P21_minimum_fields(project: Path, reg: dict, res: Result) -> None:
    """Every series entry has the minimum required fields."""
    bad = []
    for sid, entry in reg.get("series", {}).items():
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            bad.append(f"{sid}: name missing or empty")
            continue
        chapter = entry.get("chapter")
        if not isinstance(chapter, int) or chapter < 0:
            bad.append(f"{sid}: chapter must be int >= 0 (got {chapter!r})")
        status = entry.get("status")
        if not isinstance(status, str) or not status.strip():
            bad.append(f"{sid}: status missing or empty")
        units = entry.get("units")
        if not isinstance(units, str) or not units.strip():
            bad.append(f"{sid}: units missing or empty")
        ct = entry.get("content_type")
        if not isinstance(ct, str) or ct not in VALID_CONTENT_TYPES:
            bad.append(f"{sid}: content_type must be one of {VALID_CONTENT_TYPES} (got {ct!r})")
        if ct in ("time_series", "derived"):
            # Series with status='data_unavailable' have no data and therefore
            # no defensible year_range; this is the schema's exempted case.
            if (entry.get("status") or "").startswith("data_unavailable"):
                pass
            else:
                yr = entry.get("year_range")
                if not (isinstance(yr, list) and len(yr) == 2
                        and all(isinstance(y, int) for y in yr)):
                    bad.append(f"{sid}: year_range must be [int, int] for {ct} (got {yr!r})")
        if not isinstance(entry.get("subseries"), dict):
            bad.append(f"{sid}: subseries must be a dict")
    res.add("P21", "FAIL", not bad,
            f"{len(bad)} series with missing/invalid required fields" if bad
            else f"all {len(reg.get('series', {}))} series have required fields",
            bad[:10])


def check_P22_subseries_convention(project: Path, reg: dict, res: Result) -> None:
    """Subseries IDs follow naming conventions relative to parent series."""
    bad = []
    for sid, entry in reg.get("series", {}).items():
        subs = entry.get("subseries", {})
        ext_block = entry.get("extension", {}) or {}
        expected_ext = ext_block.get("output_subseries")
        expected_combined = ext_block.get("combined_subseries")
        has_ext_sub = False
        has_b_sub = False

        for sub_id, sub_meta in subs.items():
            if not sub_id.startswith(f"{sid}-"):
                bad.append(f"{sub_id}: must start with '{sid}-'")
            if sub_id.endswith("-EXT"):
                has_ext_sub = True
            if re.match(rf"^{re.escape(sid)}-B$", sub_id):
                has_b_sub = True
            if not isinstance(sub_meta, dict):
                continue
            sub_name = sub_meta.get("name")
            if not isinstance(sub_name, str) or not sub_name.strip():
                bad.append(f"{sub_id}: name missing or empty")
            sub_period = sub_meta.get("period")
            if not isinstance(sub_period, list):
                bad.append(f"{sub_id}: period must be a list")
            sub_units = sub_meta.get("units")
            if not isinstance(sub_units, str) or not sub_units.strip():
                bad.append(f"{sub_id}: units missing or empty")

        # Check the subseries NAMED by output_subseries/combined_subseries
        # exists — not a hardcoded {sid}-EXT (output_subseries may legitimately
        # name a non-"-EXT" subseries, e.g. a study-replication's primary col).
        if expected_ext and expected_ext not in subs:
            bad.append(f"{sid}: extension.output_subseries={expected_ext!r} not in subseries")
        if expected_combined and expected_combined not in subs:
            bad.append(f"{sid}: extension.combined_subseries={expected_combined!r} not in subseries")
        if has_b_sub and has_ext_sub:
            bad.append(f"{sid}: -B and -EXT subseries coexist (naming conflict)")

    res.add("P22", "WARN", not bad,
            f"{len(bad)} subseries convention issues" if bad
            else "all subseries follow naming conventions",
            bad[:10])


_EPR_REQUIRED_STATUSES = {
    "validated_book_and_extension", "validated_book_and_extension_partial",
    "study_complete", "extension_methodology_documented",
}


def check_P23_correspondence_matrix(project: Path, reg: dict, res: Result) -> None:
    """Build and write a series-to-downstream artifact correspondence matrix."""
    series = reg.get("series", {})
    docs_series = project / "docs" / "series"
    code = project / "code"
    chopped_dir = project / "chopped"

    matrix: dict[str, dict] = {}
    total_score = 0.0
    count = 0

    for sid, entry in series.items():
        status = entry.get("status", "")
        dpr = (docs_series / f"{sid}_DPR.md").exists()
        epr_applicable = status in _EPR_REQUIRED_STATUSES
        epr = (docs_series / f"{sid}_EPR.md").exists()

        l01_dir = code / "L01_loaders"
        l01 = any(l01_dir.glob(f"L01_{sid}*.py")) if l01_dir.exists() else False
        p02_dir = code / "P02_processors"
        p02 = any(p02_dir.glob(f"P02_{sid}*.py")) if p02_dir.exists() else False
        v03_dir = code / "V03_validators"
        v03 = any(v03_dir.glob(f"V03_{sid}*.py")) if v03_dir.exists() else False
        chopped = (chopped_dir / f"{sid}.csv").exists()

        # Derived series may legitimately have no L01: P02 reads upstream
        # series outputs from data/final/ (or a chopped source CSV) rather than
        # loading from a raw source via L01. Recorded per-series in the
        # registry under artifacts.derived_no_l01 (see reference-replication v1.2 iter2).
        derived_no_l01 = bool((entry.get("artifacts") or {}).get("derived_no_l01"))

        applicable = ["dpr", "p02", "v03", "chopped"]
        present = [dpr, p02, v03, chopped]
        if not derived_no_l01:
            applicable.append("l01")
            present.append(l01)
        if epr_applicable:
            applicable.append("epr")
            present.append(epr)

        n_applicable = len(applicable)
        n_present = sum(present)
        completeness = n_present / n_applicable if n_applicable else 1.0
        total_score += completeness
        count += 1

        matrix[sid] = {
            "dpr": dpr,
            "epr": epr,
            "epr_applicable": epr_applicable,
            "l01": l01,
            "l01_applicable": not derived_no_l01,
            "p02": p02,
            "v03": v03,
            "chopped": chopped,
            "completeness": round(completeness, 3),
        }

    avg_completeness = round(total_score / count, 3) if count else 1.0
    # data_unavailable series legitimately have no chopped CSV / partial
    # artifacts (the data does not exist) — they carry a data_unavailable_reason
    # and must not be fabricated. Exempt them from the gaps list (cf. P02).
    gaps = [f"{sid} ({m['completeness']:.0%})" for sid, m in matrix.items()
            if m["completeness"] < 1.0
            and not (series.get(sid, {}).get("status") or "").startswith("data_unavailable")]

    out_path = project / "SERIES_CORRESPONDENCE_MATRIX.json"
    try:
        out_path.write_text(
            json.dumps({"series": matrix, "summary_completeness": avg_completeness},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass

    res.add("P23", "WARN", not gaps,
            f"{len(gaps)} series with incomplete artifacts "
            f"(avg completeness {avg_completeness:.0%})" if gaps
            else f"all {count} series have complete artifact coverage",
            gaps[:10])


# ============================ P24-P29 (v2.2.0) ============================
# Added in response to a comparative rebuild review.
# See the framework rebuild review for context.

def _parse_iso(ts: str) -> str:
    """Normalize an ISO timestamp string to YYYY-MM-DDTHH:MM:SS for comparison."""
    if not ts:
        return ""
    s = str(ts).strip().replace("Z", "+00:00")
    # Trim subsecond and timezone for lexicographic comparison
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", s)
    return m.group(1) if m else s[:19]


def check_P24_ledger_freshness(project: Path, reg: dict, res: Result) -> None:
    """ANU_LEDGER.generated must be >= the latest STEP_LOG entry and PIPELINE_STATE.last_updated.

    Catches the reference-replication failure mode: ledger regenerated on 2026-05-16; later sessions
    wrote new artifacts; ledger was never refreshed; downstream counts under-reported.
    """
    ledger_path = project / "ANU_LEDGER.json"
    if not ledger_path.exists():
        res.add("P24", "WARN", False, "ANU_LEDGER.json missing", [])
        return
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as e:
        res.add("P24", "WARN", False, f"ANU_LEDGER.json parse error: {e}", [])
        return

    ledger_ts = _parse_iso(ledger.get("generated") or ledger.get("last_updated") or "")
    issues = []

    log_path = project / "Build" / "STEP_LOG.jsonl"
    if log_path.exists():
        lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            try:
                last_entry = json.loads(lines[-1])
                step_ts = _parse_iso(last_entry.get("ts", ""))
                if step_ts and ledger_ts and step_ts > ledger_ts:
                    issues.append(f"STEP_LOG last ts={step_ts} > ledger.generated={ledger_ts}")
            except Exception:
                pass

    ps_path = project / "PIPELINE_STATE.json"
    if ps_path.exists():
        try:
            ps = json.loads(ps_path.read_text(encoding="utf-8"))
            ps_ts = _parse_iso(ps.get("last_updated", ""))
            if ps_ts and ledger_ts and ps_ts > ledger_ts:
                issues.append(f"PIPELINE_STATE.last_updated={ps_ts} > ledger.generated={ledger_ts}")
        except Exception:
            pass

    res.add("P24", "WARN", not issues,
            "; ".join(issues) if issues else "ledger is fresh relative to STEP_LOG and PIPELINE_STATE",
            issues)


def check_P25_ledger_inventory(project: Path, reg: dict, res: Result) -> None:
    """ANU_LEDGER.series_inventory size must match registry series count.

    Catches a predecessor-project failure mode: ledger contains 1 exemplar entry (S201) while
    the registry has 118 series. Ledger consumers cannot rely on it as truth.
    """
    ledger_path = project / "ANU_LEDGER.json"
    if not ledger_path.exists():
        res.add("P25", "FAIL", False, "ANU_LEDGER.json missing", [])
        return
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as e:
        res.add("P25", "FAIL", False, f"ANU_LEDGER.json parse error: {e}", [])
        return

    # Accept any of the canonical inventory keys (the v12 schema is in flux).
    # Try in priority order, take the first dict whose keys look like series IDs.
    candidates = [
        ledger.get("series_inventory"),
        ledger.get("series"),
        ledger.get("artifacts"),
    ]
    inventory = next(
        (c for c in candidates if isinstance(c, dict) and c
         and any(re.match(r"^[A-Z]{1,3}\d{3,4}$", k) for k in list(c.keys())[:5])),
        {},
    )
    inv_count = len(inventory) if isinstance(inventory, dict) else 0
    reg_count = len(reg.get("series", {}))
    ok = inv_count == reg_count
    detail = (f"ledger inventory has {inv_count} entries vs registry {reg_count} series"
              if not ok else f"ledger inventory matches registry ({reg_count} series)")
    items = []
    if not ok and inv_count == 1:
        items.append("ledger appears to contain only an exemplar entry — full inventory not populated")
    elif not ok and inv_count < reg_count:
        missing = sorted(set(reg.get("series", {}).keys()) - set(inventory.keys()))
        items = [f"missing from ledger: {sid}" for sid in missing[:5]]
    res.add("P25", "FAIL", ok, detail, items)


def check_P26_step_log_pipeline_consistency(project: Path, reg: dict, res: Result) -> None:
    """Every PIPELINE_STATE stage marked 'complete' must have STEP_LOG entries for that stage.

    Catches a predecessor-project failure mode: stages 3-6 all reported started_at = same minute
    and completed_at = same minute, hand-populated without orchestration. STEP_LOG
    is the authoritative event log.
    """
    ps_path = project / "PIPELINE_STATE.json"
    log_path = project / "Build" / "STEP_LOG.jsonl"
    if not ps_path.exists():
        res.add("P26", "FAIL", False, "PIPELINE_STATE.json missing", [])
        return
    if not log_path.exists():
        res.add("P26", "FAIL", False, "Build/STEP_LOG.jsonl missing — cannot verify stage transitions", [])
        return

    try:
        ps = json.loads(ps_path.read_text(encoding="utf-8"))
    except Exception as e:
        res.add("P26", "FAIL", False, f"PIPELINE_STATE.json parse error: {e}", [])
        return

    # Collect stage numbers seen in STEP_LOG
    stages_in_log: dict[int, int] = {}
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        st = entry.get("stage")
        if isinstance(st, int):
            stages_in_log[st] = stages_in_log.get(st, 0) + 1

    issues = []
    stages = ps.get("stages", {})
    # Stages whose completion is attested by filesystem inventory rather than
    # per-stage STEP_LOG instrumentation are exempt from STEP_LOG-backing and
    # timestamp-clustering sub-checks (the stage declares this explicitly).
    fs_verified = {
        key for key, st in stages.items()
        if isinstance(st, dict) and st.get("verification_method") == "filesystem_inventory"
    }
    for key, stage in stages.items():
        if not isinstance(stage, dict):
            continue
        if stage.get("status") != "complete":
            continue
        if key in fs_verified:
            continue  # verification_method: filesystem_inventory — STEP_LOG not required
        # Extract stage number from key like "stage_3"
        m = re.search(r"\d+", key)
        if not m:
            continue
        n = int(m.group(0))
        if n == 0:
            continue  # stage 0 init is allowed without per-stage log entries
        if stages_in_log.get(n, 0) == 0:
            issues.append(f"{key} marked complete but no STEP_LOG entries with stage={n}")

    # Detect identical-timestamp clustering (hand-population signature)
    starts: dict[str, list] = {}
    completes: dict[str, list] = {}
    for key, stage in stages.items():
        if not isinstance(stage, dict):
            continue
        if key in fs_verified:
            continue  # filesystem-inventory-verified stages share timestamps legitimately
        s = stage.get("started_at")
        c = stage.get("completed_at")
        if s:
            starts.setdefault(_parse_iso(s), []).append(key)
        if c:
            completes.setdefault(_parse_iso(c), []).append(key)
    for ts, keys in starts.items():
        if len(keys) >= 3:
            issues.append(f"{len(keys)} stages share started_at={ts} ({', '.join(keys)}) — possible hand-population")
    for ts, keys in completes.items():
        if len(keys) >= 3:
            issues.append(f"{len(keys)} stages share completed_at={ts} ({', '.join(keys)}) — possible hand-population")

    res.add("P26", "FAIL", not issues,
            f"{len(issues)} STEP_LOG/PIPELINE_STATE consistency issues" if issues
            else "all complete stages backed by STEP_LOG entries",
            issues[:10])


def check_P27_anu_doctor_mandatory(project: Path, reg: dict, res: Result) -> None:
    """framework_audit.anu_doctor_status MUST NOT be 'not_run' when any stage > 0 is complete.

    Catches a predecessor-project failure mode: PIPELINE_STATE.framework_audit explicitly admits
    'anu-* skills not loaded in this session', yet stages 1-8 are marked complete.
    """
    ps_path = project / "PIPELINE_STATE.json"
    if not ps_path.exists():
        res.add("P27", "FAIL", False, "PIPELINE_STATE.json missing", [])
        return
    try:
        ps = json.loads(ps_path.read_text(encoding="utf-8"))
    except Exception as e:
        res.add("P27", "FAIL", False, f"PIPELINE_STATE.json parse error: {e}", [])
        return

    audit = ps.get("framework_audit", {}) or {}
    audit_status = (audit.get("anu_doctor_status") or "").lower()

    stages_completed_beyond_0 = []
    for key, stage in (ps.get("stages") or {}).items():
        if not isinstance(stage, dict):
            continue
        m = re.search(r"\d+", key)
        if not m:
            continue
        n = int(m.group(0))
        if n == 0:
            continue
        if stage.get("status") == "complete":
            stages_completed_beyond_0.append(key)

    if not stages_completed_beyond_0:
        res.add("P27", "FAIL", True,
                "no stages beyond Stage 0 are complete — anu-doctor not yet required",
                [])
        return

    if audit_status in ("", "not_run", "skipped", "deferred"):
        res.add("P27", "FAIL", False,
                f"framework_audit.anu_doctor_status='{audit_status or 'absent'}' "
                f"while {len(stages_completed_beyond_0)} stages beyond Stage 0 are complete",
                stages_completed_beyond_0[:10])
        return

    if audit_status not in ("pass", "passed", "fail", "warn"):
        res.add("P27", "FAIL", False,
                f"framework_audit.anu_doctor_status='{audit_status}' is not a recognised value",
                [])
        return

    res.add("P27", "FAIL", True,
            f"anu-doctor has been run (status={audit_status}) covering "
            f"{len(stages_completed_beyond_0)} completed stages",
            [])


def check_P28_decision_log_convention(project: Path, reg: dict, res: Result) -> None:
    """Decision documents follow NNNN_*.md numbering and carry an approval timestamp.

    Catches retroactive approvals (a predecessor project's Decision 0006 approved 18:45;
    dependent fanout started 19:00 same day).
    """
    dec_dir = project / "docs" / "decisions"
    if not dec_dir.exists():
        res.add("P28", "WARN", True, "docs/decisions/ absent (no decisions logged yet)", [])
        return

    # Accept both kebab-case and snake_case slugs after the NNNN_ prefix.
    name_re = re.compile(r"^(\d{4})_[A-Za-z0-9_-]+\.md$")
    seen_numbers: list[int] = []
    issues = []
    decisions: list[tuple[int, str, str]] = []  # (num, decision_id, approved_at)

    for f in sorted(dec_dir.glob("*.md")):
        m = name_re.match(f.name)
        if not m:
            issues.append(f"{f.name}: filename does not match NNNN_kebab-case.md")
            continue
        n = int(m.group(1))
        seen_numbers.append(n)

        text = f.read_text(encoding="utf-8", errors="ignore")
        # Look for status: approved AND an approved_at timestamp
        status_m = re.search(r"^\s*status\s*[:=]\s*[\"']?(approved|proposed|rejected|superseded)",
                             text, re.MULTILINE | re.IGNORECASE)
        approved_m = re.search(r"^\s*approved_at\s*[:=]\s*[\"']?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)",
                               text, re.MULTILINE | re.IGNORECASE)
        if not status_m:
            issues.append(f"{f.name}: missing status field in frontmatter")
            continue
        if status_m.group(1).lower() == "approved" and not approved_m:
            issues.append(f"{f.name}: status=approved but approved_at missing")
            continue
        if approved_m:
            decisions.append((n, f.stem, _parse_iso(approved_m.group(1))))

    # Sequential numbering check
    if seen_numbers:
        expected = list(range(1, max(seen_numbers) + 1))
        gaps = sorted(set(expected) - set(seen_numbers))
        if gaps:
            issues.append(f"decision numbering has gaps: missing {gaps[:5]}")

    # Retroactive-approval check against STEP_LOG
    log_path = project / "Build" / "STEP_LOG.jsonl"
    if log_path.exists() and decisions:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            entry_ts = _parse_iso(entry.get("ts", ""))
            text_blob = (str(entry.get("notes", "")) + " " +
                         str(entry.get("inputs", "")) + " " +
                         str(entry.get("outputs", ""))).lower()
            for n, did, approved_at in decisions:
                if not approved_at or not entry_ts:
                    continue
                # Heuristic: match decision_id stem or the four-digit number
                num_token = f"{n:04d}"
                if num_token in text_blob and entry_ts < approved_at:
                    issues.append(
                        f"step_log entry {entry.get('step_id', '?')} at {entry_ts} "
                        f"depends on decision {num_token} approved later at {approved_at}"
                    )
                    break

    res.add("P28", "WARN", not issues,
            f"{len(issues)} decision-log convention issues across {len(seen_numbers)} decisions"
            if issues else f"all {len(seen_numbers)} decisions follow convention",
            issues[:10])


def check_P29_year_range_integrity(project: Path, reg: dict, res: Result) -> None:
    """Registry year_range matches the min/max year in the chopped CSV per series.

    Catches a predecessor-project failure mode: 12 series with registry year_range vs chopped CSV
    start/end mismatch (marked Q6-informational in viz, but a real signal of drift).

    v2.3.1 (reference-replication v1.2 iter2): when the registry validation block declares
    ``extension_year_range: [start, end]`` the effective accepted range becomes
    the UNION of ``year_range`` and ``extension_year_range``. This preserves
    book-period authority in ``year_range`` while permitting downstream -EXT /
    -COMBINED subseries to extend the chopped CSV beyond the book window.
    """
    chopped_dir = project / "chopped"
    if not chopped_dir.exists():
        res.add("P29", "WARN", True, "chopped/ directory absent (skipped — pre-output stage)", [])
        return

    issues = []
    checked = 0
    for sid, entry in reg.get("series", {}).items():
        yr = entry.get("year_range")
        if not (isinstance(yr, list) and len(yr) == 2):
            continue
        ct = entry.get("content_type", "")
        if ct not in ("time_series", "derived"):
            continue
        if (entry.get("status") or "").strip() == "data_unavailable":
            continue

        # Optional extension_year_range lives in the validation block. When
        # present it widens the accepted bounds (UNION with year_range).
        ext_yr = (entry.get("validation") or {}).get("extension_year_range")

        csv_path = chopped_dir / f"{sid}.csv"
        if not csv_path.exists():
            continue
        try:
            years: list[int] = []
            with csv_path.open(encoding="utf-8") as fh:
                rdr = csv.reader(fh)
                row1 = next(rdr, None)
                row2 = next(rdr, None)
                # Detect format:
                #   Anu Chopped wide-form: Row 1 = metadata strings, Row 2 = column IDs
                #     starting with "Year"/"year", data from row 3
                #   Long-form (tidy):       Row 1 = column headers including "year" first,
                #                           data from row 2
                long_form = bool(
                    row1 and row1[0] and row1[0].strip().lower() == "year"
                )
                if long_form:
                    # row2 was already the first data row; capture it
                    if row2:
                        try:
                            years.append(int(row2[0]))
                        except (ValueError, IndexError):
                            pass
                for row in rdr:
                    if not row:
                        continue
                    try:
                        years.append(int(row[0]))
                    except (ValueError, IndexError):
                        continue
            if not years:
                continue
            csv_min, csv_max = min(years), max(years)
            reg_min, reg_max = int(yr[0]), int(yr[1])
            checked += 1

            # Compute effective accepted bounds: UNION of year_range and
            # extension_year_range when the latter is declared. If only
            # year_range is present the check behaves exactly as before.
            eff_min, eff_max = reg_min, reg_max
            ext_used = False
            if isinstance(ext_yr, list) and len(ext_yr) == 2:
                try:
                    ext_min, ext_max = int(ext_yr[0]), int(ext_yr[1])
                    eff_min = min(eff_min, ext_min)
                    eff_max = max(eff_max, ext_max)
                    ext_used = True
                except (TypeError, ValueError):
                    pass

            # When extension_year_range is declared the check is a containment
            # test: the chopped CSV bounds must lie WITHIN the effective range
            # (CSV may start later than the book period if -EXT subseries
            # introduce a new origin, e.g. reference-replication Ch7 proxies). Without the
            # extension declaration the original strict-equality semantics
            # apply, preserving the original drift detection.
            if ext_used:
                if csv_min < eff_min or csv_max > eff_max:
                    issues.append(
                        f"{sid}: registry year_range=[{reg_min},{reg_max}] "
                        f"+ extension_year_range=[{int(ext_yr[0])},{int(ext_yr[1])}] "
                        f"(effective=[{eff_min},{eff_max}]) vs chopped=[{csv_min},{csv_max}] "
                        f"(chopped extends beyond effective range)"
                    )
            elif csv_min != eff_min or csv_max != eff_max:
                issues.append(
                    f"{sid}: registry year_range=[{reg_min},{reg_max}] vs chopped=[{csv_min},{csv_max}]"
                )
        except Exception as e:
            issues.append(f"{sid}: chopped CSV read error: {e}")

    res.add("P29", "WARN", not issues,
            f"{len(issues)} year_range mismatches across {checked} checked series" if issues
            else f"all {checked} checked series have matching year_range and chopped CSV bounds",
            issues[:10])


# ============================ P30-P36 (v2.3.0) ============================
# Added after a comprehensive framework rebuild review session.
# See the framework rebuild review and its decision records for context.

from collections import Counter as _Counter


def check_P30_rollup_freshness(project: Path, reg: dict, res: Result) -> None:
    """Top-level by_status / by_content_type rollups match per-series data."""
    issues = []
    actual_status: dict[str, int] = {}
    actual_ct: dict[str, int] = {}
    for e in reg.get("series", {}).values():
        s = e.get("status", "unset")
        c = e.get("content_type", "unset")
        actual_status[s] = actual_status.get(s, 0) + 1
        actual_ct[c] = actual_ct.get(c, 0) + 1

    declared_status = reg.get("by_status") or {}
    declared_ct = reg.get("by_content_type") or {}

    if declared_status and dict(actual_status) != dict(declared_status):
        issues.append(f"by_status mismatch: actual={actual_status} declared={declared_status}")
    if declared_ct and dict(actual_ct) != dict(declared_ct):
        issues.append(f"by_content_type mismatch: actual={actual_ct} declared={declared_ct}")
    res.add("P30", "WARN", not issues,
            f"{len(issues)} rollup staleness issues" if issues
            else "rollups match per-series data (or absent)",
            issues)


def check_P31_dpr_status_sync(project: Path, reg: dict, res: Result) -> None:
    """DPR markdown 'Status:' line matches registry series[sid].status."""
    docs_dir = project / "docs" / "series"
    if not docs_dir.exists():
        res.add("P31", "WARN", True, "docs/series/ absent (skipped)", [])
        return
    status_re = re.compile(
        r"^[\s\*\-]*\*?\*?Status\*?\*?\s*[:|]?\s*(.+?)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    mismatches = []
    for sid, entry in reg.get("series", {}).items():
        dpr = docs_dir / f"{sid}_DPR.md"
        if not dpr.exists():
            continue
        canonical = (entry.get("status") or "").strip()
        if not canonical:
            continue
        text = dpr.read_text(encoding="utf-8", errors="ignore")
        m = status_re.search(text)
        if not m:
            continue
        doc_status = m.group(1).strip().rstrip(".,;")
        if doc_status != canonical:
            mismatches.append(f"{sid}: doc='{doc_status}' vs registry='{canonical}'")
    res.add("P31", "WARN", not mismatches,
            f"{len(mismatches)} DPRs out of sync with registry status"
            if mismatches else "all DPR Status lines align to registry",
            mismatches[:10])


def check_P32_validator_registry_match(project: Path, reg: dict, res: Result) -> None:
    """V03 hardcoded reference values match registry validation.reference_values.

    Parses simple `BENCHMARKS = {YYYY: value, ...}` style dicts from V03 files
    and compares to registry. Flags drift only where BOTH sides declare values.
    """
    v03_dir = project / "code" / "V03_validators"
    if not v03_dir.exists():
        res.add("P32", "FAIL", True, "V03_validators/ absent (skipped)", [])
        return
    bench_re = re.compile(
        r"(?:BENCHMARKS|REFERENCE_VALUES|EXPECTED|CD2_SPOTCHECK)\s*[:=]\s*\{([^}]+)\}",
        re.DOTALL,
    )
    year_val_re = re.compile(r"(?:[\"\']?)(\d{4})(?:[\"\']?)\s*:\s*([\-\d.eE+]+)")
    issues = []
    for sid, entry in reg.get("series", {}).items():
        v_path = next(v03_dir.glob(f"V03_{sid}*.py"), None)
        if v_path is None:
            continue
        reg_refs = (entry.get("validation") or {}).get("reference_values")
        if not isinstance(reg_refs, dict) or not reg_refs:
            continue
        text = v_path.read_text(encoding="utf-8", errors="ignore")
        m = bench_re.search(text)
        if not m:
            continue
        code_refs = {}
        for ym in year_val_re.finditer(m.group(1)):
            try:
                code_refs[int(ym.group(1))] = float(ym.group(2))
            except ValueError:
                continue
        for yr_str, reg_val in reg_refs.items():
            try:
                yr = int(yr_str)
                rv = float(reg_val)
            except (ValueError, TypeError):
                continue
            if yr not in code_refs:
                continue
            cv = code_refs[yr]
            if rv == 0:
                if cv != 0:
                    issues.append(f"{sid}: year={yr} registry=0 vs V03={cv}")
                continue
            rel = abs(cv - rv) / abs(rv)
            if rel > 0.005:  # 0.5% tolerance for value comparison
                issues.append(f"{sid}: year={yr} registry={rv} vs V03={cv} (rel={rel:.4f})")
    res.add("P32", "FAIL", not issues,
            f"{len(issues)} V03↔registry reference value drifts" if issues
            else "V03 reference values align with registry",
            issues[:10])


def check_P33_no_nested_git(project: Path, reg: dict, res: Result) -> None:
    """Inputs/ contains no nested .git directories (rebuild anti-pattern)."""
    inputs_dir = project.parent / "Inputs" if (project.parent / "Inputs").exists() else None
    if inputs_dir is None:
        # Try at project root level (Technical/../Inputs)
        inputs_dir = project.parent / "Inputs"
    if not inputs_dir.exists():
        res.add("P33", "WARN", True, "Inputs/ absent (skipped)", [])
        return
    nested = []
    for p in inputs_dir.rglob(".git"):
        if p.is_dir():
            nested.append(str(p.relative_to(inputs_dir)))
    res.add("P33", "WARN", not nested,
            f"{len(nested)} nested .git directories in Inputs/" if nested
            else "no nested .git directories in Inputs/",
            nested[:10])


def check_P34_orphan_figures(project: Path, reg: dict, res: Result) -> None:
    """Top-level figures must be referenced by at least one series."""
    figs = reg.get("figures") or {}
    if not figs:
        res.add("P34", "WARN", True, "no top-level figures block (skipped)", [])
        return
    referenced: set = set()
    for entry in reg.get("series", {}).values():
        for fid in entry.get("figures") or []:
            if isinstance(fid, str):
                referenced.add(fid)
        # Also figure references in subseries
        for sub in (entry.get("subseries") or {}).values():
            if isinstance(sub, dict):
                for fid in sub.get("figures") or []:
                    if isinstance(fid, str):
                        referenced.add(fid)
    orphans = sorted(set(figs.keys()) - referenced)
    res.add("P34", "WARN", not orphans,
            f"{len(orphans)} orphan top-level figures (declared but unreferenced)" if orphans
            else f"all {len(figs)} top-level figures referenced",
            orphans[:10])


def check_P35_project_index(project: Path, reg: dict, res: Result) -> None:
    """PROJECT_INDEX.md exists at the project root."""
    # project is Technical/; root is its parent
    pidx = project.parent / "PROJECT_INDEX.md"
    if pidx.exists():
        res.add("P35", "WARN", True, f"PROJECT_INDEX.md present at {pidx}", [])
    else:
        res.add("P35", "WARN", False,
                f"PROJECT_INDEX.md missing at {pidx}", [str(pidx)])


def check_P36_extension_binary_invariant(project: Path, reg: dict, res: Result) -> None:
    """Extension binary invariant (Decision 0003):
       - If any subseries ends with -EXT or -COMBINED → extension block must be populated
       - If extension is null/absent → no -EXT or -COMBINED subseries allowed
       - If extension is populated → output_subseries and combined_subseries must exist as subseries
    """
    bad = []
    for sid, entry in reg.get("series", {}).items():
        ext = entry.get("extension")
        subs = entry.get("subseries") or {}
        has_ext_sub = any(s.endswith("-EXT") for s in subs)
        has_comb_sub = any(s.endswith("-COMBINED") for s in subs)

        if ext is None or ext == {}:
            if has_ext_sub:
                bad.append(f"{sid}: extension=null but -EXT subseries exists")
            if has_comb_sub:
                bad.append(f"{sid}: extension=null but -COMBINED subseries exists")
        elif isinstance(ext, dict):
            out_sub = ext.get("output_subseries")
            comb_sub = ext.get("combined_subseries")
            if not out_sub or not comb_sub:
                bad.append(f"{sid}: extension populated but missing output_subseries/combined_subseries")
                continue
            if out_sub not in subs:
                bad.append(f"{sid}: extension.output_subseries={out_sub!r} not in subseries")
            if comb_sub not in subs:
                bad.append(f"{sid}: extension.combined_subseries={comb_sub!r} not in subseries")
            # Required fields for populated extension
            for req in ("api", "splice_year", "splice_method", "provenance"):
                if not ext.get(req):
                    bad.append(f"{sid}: extension missing required field '{req}'")
    res.add("P36", "FAIL", not bad,
            f"{len(bad)} extension-binary-invariant violations" if bad
            else "all series satisfy the extension binary invariant",
            bad[:10])


def _find_project_inputs_robin(project: Path) -> Path | None:
    """Locate `Inputs/Robin/` relative to the project root.

    Anu projects can live at the project root itself, under Technical/, or
    nested deeper (e.g., Project/Technical/AnuData/). Walk up until we find
    a sibling Inputs/Robin/, stopping at the workspace root.
    """
    # Workspace root resolved from this script's location, not hardcoded:
    # this checker lives in skills/anu-doctor/ within the workspace.
    workspace = Path(__file__).resolve().parents[5]
    cur = project.resolve()
    while cur != workspace and cur.parent != cur:
        candidate = cur / "Inputs" / "Robin"
        if candidate.exists() and candidate.is_dir():
            return candidate
        cur = cur.parent
    return None


def check_P37_robin_checkouts(project: Path, reg: dict, res: Result) -> None:
    """Every `Inputs/Robin/[SOURCE]/` has a valid PROVENANCE.md (schema + files present).

    Calls the canonical robin_loader.validate_checkout() for each source. Does NOT
    re-hash files (P38 is the strict-hash variant). FAIL severity because broken
    PROVENANCE indicates a contract violation.
    """
    robin_dir = _find_project_inputs_robin(project)
    if robin_dir is None:
        res.add("P37", "FAIL", True,
                "no Inputs/Robin/ folder (project consumes no Robin sources)",
                [])
        return

    # Import robin_loader from Robin's canonical location
    import importlib.util
    loader_path = (Path(__file__).resolve().parents[5]
                   / "Council" / "Robin" / "PACKAGES" / "python" / "robin_loader.py")
    if not loader_path.exists():
        res.add("P37", "WARN", True,
                f"robin_loader not found at {loader_path} - skipping",
                [])
        return
    spec = importlib.util.spec_from_file_location("robin_loader", loader_path)
    if spec is None or spec.loader is None:
        res.add("P37", "WARN", True, "could not load robin_loader spec", [])
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    issues = []
    n_ok = 0
    for d in sorted(robin_dir.iterdir()):
        if not d.is_dir():
            continue
        try:
            mod.validate_checkout(d, strict=False, verify_hashes=False)
            n_ok += 1
        except (mod.RobinCheckoutError, mod.RobinSchemaError) as e:
            issues.append(f"{d.name}: {type(e).__name__}: {str(e)[:120]}")
        except Exception as e:  # pragma: no cover - defensive
            issues.append(f"{d.name}: unexpected: {type(e).__name__}: {str(e)[:120]}")

    res.add("P37", "FAIL", not issues,
            f"{n_ok} Robin checkout(s) valid" if not issues
            else f"{len(issues)} Robin checkout schema problem(s) ({n_ok} OK)",
            issues[:10])


def check_P38_robin_hash_drift(project: Path, reg: dict, res: Result) -> None:
    """Every Robin checkout's file SHA-256s match the values recorded in PROVENANCE.md.

    Strict variant of P37 — actually re-hashes every file. Slow on large checkouts.
    Run with `--check P38` selectively before publication. FAIL severity.
    """
    robin_dir = _find_project_inputs_robin(project)
    if robin_dir is None:
        res.add("P38", "FAIL", True, "no Inputs/Robin/ folder (skip)", [])
        return

    import importlib.util
    loader_path = (Path(__file__).resolve().parents[5]
                   / "Council" / "Robin" / "PACKAGES" / "python" / "robin_loader.py")
    if not loader_path.exists():
        res.add("P38", "WARN", True, "robin_loader not found - skipped", [])
        return
    spec = importlib.util.spec_from_file_location("robin_loader", loader_path)
    if spec is None or spec.loader is None:
        res.add("P38", "WARN", True, "could not load robin_loader spec", [])
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    issues = []
    n_pass = 0
    for d in sorted(robin_dir.iterdir()):
        if not d.is_dir():
            continue
        try:
            mod.validate_checkout(d, strict=False, verify_hashes=True)
            n_pass += 1
        except mod.RobinDriftError as e:
            issues.append(f"{d.name}: DRIFT: {str(e)[:160]}")
        except (mod.RobinCheckoutError, mod.RobinSchemaError):
            # already caught by P37 — don't double-report
            continue
        except Exception as e:  # pragma: no cover
            issues.append(f"{d.name}: unexpected: {type(e).__name__}: {str(e)[:120]}")

    res.add("P38", "FAIL", not issues,
            f"{n_pass} Robin checkout(s) hash-match" if not issues
            else f"{len(issues)} hash drift(s) ({n_pass} OK)",
            issues[:10])


def check_P39_no_hardcoded_robin_data_paths(project: Path, reg: dict, res: Result) -> None:
    """Code under project does not hardcode `Council/Robin/DATA/` paths.

    Projects should read through `Inputs/Robin/[SOURCE]/` checkouts. Direct reads
    of the canonical store skip PROVENANCE / drift detection. WARN severity
    because some scripts intentionally reference the canonical path in comments
    or fallback logic (e.g., a private data layer's checkout-with-fallback pattern).
    """
    code_dirs = [project / "code", project / "scripts", project / "src"]
    code_dirs = [d for d in code_dirs if d.exists()]
    if not code_dirs:
        res.add("P39", "WARN", True, "no code/scripts/src/ — skipped", [])
        return

    hits = []
    pat = re.compile(r"(?:Council[/\\]Robin[/\\]DATA|Arcanum[/\\]Council[/\\]Robin[/\\]DATA)")
    for cd in code_dirs:
        for f in cd.rglob("*.py"):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    hits.append(f"{f.relative_to(project)}:{i}: {line.strip()[:100]}")
    res.add("P39", "WARN", not hits,
            f"{len(hits)} hardcoded Council/Robin/DATA reference(s) in code" if hits
            else "no hardcoded Robin canonical paths in code",
            hits[:10])


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
    "P15": check_P15_build_manifest,
    "P16": check_P16_subseries_plan,
    "P17": check_P17_schema_versions,
    "P18": check_P18_step_log_valid,
    "P19": check_P19_loader_ledger_sync,
    "P20": check_P20_cascade_consistency,
    "P21": check_P21_minimum_fields,
    "P22": check_P22_subseries_convention,
    "P23": check_P23_correspondence_matrix,
    "P24": check_P24_ledger_freshness,
    "P25": check_P25_ledger_inventory,
    "P26": check_P26_step_log_pipeline_consistency,
    "P27": check_P27_anu_doctor_mandatory,
    "P28": check_P28_decision_log_convention,
    "P29": check_P29_year_range_integrity,
    "P30": check_P30_rollup_freshness,
    "P31": check_P31_dpr_status_sync,
    "P32": check_P32_validator_registry_match,
    "P33": check_P33_no_nested_git,
    "P34": check_P34_orphan_figures,
    "P35": check_P35_project_index,
    "P36": check_P36_extension_binary_invariant,
    "P37": check_P37_robin_checkouts,
    "P38": check_P38_robin_hash_drift,
    "P39": check_P39_no_hardcoded_robin_data_paths,
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
