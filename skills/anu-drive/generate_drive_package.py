#!/usr/bin/env python3
"""Anu Drive — consumer-facing distribution package generator.

Builds a single shareable folder from an Anu Framework project's
canonical outputs: a master data workbook, a machine-readable CSV, a
codebook, the per-series Excel workbooks, the methodology PDF, and
plain-text README / CITATION files.

Usage:
    python generate_drive_package.py <project_root> [--version X.Y]

If --version is omitted the script reads drive_config.drive_version from
the registry and, if a Drive package at that version already exists,
recommends the next minor bump.

Source of truth: {project}/Technical/series_registry.json
Source data:     {project}/Technical/ANU_REPLICATOR/data/final-data/
Output:          {project}/Outputs/{PROJECT}_Drive_v{VERSION}/

Part of the Anu Framework v11.0 — see anu-drive/SKILL.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    print("ERROR: pandas is required (pip install pandas openpyxl).", file=sys.stderr)
    sys.exit(2)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def snake_case(name: str, max_len: int = 50) -> str:
    """Registry name -> snake_case file descriptor."""
    s = name.lower()
    s = re.sub(r"[()/,.:;]", "", s)
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:max_len]


def series_units(entry: dict) -> str:
    """Best-effort unit string for a series.

    The registry does not carry a single canonical ``units`` field, so we
    try, in order: an explicit ``units`` key, the final (bare-id) subseries,
    the last subseries with a non-empty units value, then empty.
    """
    if entry.get("units"):
        return str(entry["units"])
    subs = entry.get("subseries", {}) or {}
    # Last subseries with a units value tends to be the final/spliced one.
    for sub in reversed(list(subs.values())):
        u = sub.get("units")
        if u:
            return str(u)
    return ""


def content_type(entry: dict) -> str:
    """Normalize the registry's data_type into a content_type label."""
    dt = (entry.get("content_type") or entry.get("data_type") or "time_series").lower()
    if "cross" in dt:
        return "cross_sectional"
    if "theor" in dt:
        return "theoretical"
    if "deriv" in dt:
        return "derived"
    return "time_series"


def primary_source(entry: dict) -> str:
    """First source reference, human-readable."""
    refs = entry.get("source_refs") or []
    if refs:
        return str(refs[0])
    subs = entry.get("subseries", {}) or {}
    for sub in subs.values():
        if sub.get("source"):
            return str(sub["source"])
    return ""


def extension_source(entry: dict) -> str:
    ext = entry.get("extension")
    if isinstance(ext, dict):
        api = ext.get("api", "")
        sid = ext.get("api_series_id", "")
        return f"{api} {sid}".strip()
    return ""


# --------------------------------------------------------------------------
# Package builders
# --------------------------------------------------------------------------

def collect_final_series(final_series_dir: Path) -> dict[str, pd.Series]:
    """Read every series CSV into a dict of year-indexed Series.

    Tries glob `*_final.csv` first (the canonical anu-replicator convention);
    falls back to `*.csv` (Chopped CSVs named directly by SID, e.g. `ES1001.csv`).
    Skips files whose first column isn't year-like.
    """
    out: dict[str, pd.Series] = {}
    candidates = sorted(final_series_dir.glob("*_final.csv"))
    if not candidates:
        # Fall back to raw SID naming (chopped/ layout)
        candidates = sorted(final_series_dir.glob("*.csv"))
    for csv_path in candidates:
        sid = csv_path.stem.replace("_final", "")
        # Chopped CSV files have metadata in rows 1-2; year-data starts row 3.
        # Standard final CSVs have header in row 1, data from row 2.
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        if df.shape[1] < 2:
            continue
        year_col, val_col = df.columns[0], df.columns[1]
        # Detect Chopped 3-row format: if column 0 isn't year-like, skip header rows.
        first_val = df.iloc[0, 0] if len(df) else None
        try:
            int(first_val)
        except (TypeError, ValueError):
            # First row is a header annotation; try skiprows=1 (Chopped Row 2 is IDs)
            df = pd.read_csv(csv_path, skiprows=1)
            if df.shape[1] < 2:
                continue
            year_col, val_col = df.columns[0], df.columns[1]
        s = pd.Series(
            pd.to_numeric(df[val_col], errors="coerce").values,
            index=pd.to_numeric(df[year_col], errors="coerce").astype("Int64"),
            name=sid,
        )
        s = s[s.index.notna()]
        # Some final CSVs carry duplicate year rows; keep the last occurrence.
        if s.index.has_duplicates:
            s = s[~s.index.duplicated(keep="last")]
        out[sid] = s
    return out


YEAR_MIN, YEAR_MAX = 1500, 2100


def build_master_frame(registry: dict, series_data: dict[str, pd.Series]) -> pd.DataFrame:
    """Year x series matrix of final values for time-series content only.

    Cross-sectional and theoretical series are excluded from the master
    workbook's time-series sheet — their indices are not years. They still
    ship as individual workbooks under Series/.
    """
    sids = []
    for sid in sorted(series_data.keys()):
        entry = registry["series"].get(sid, {})
        if content_type(entry) not in ("time_series", "derived"):
            continue
        s = series_data[sid]
        # Keep only plausible calendar years — guards against panel CSVs
        # whose first column is a positional index, not a year.
        s = s[(s.index >= YEAR_MIN) & (s.index <= YEAR_MAX)]
        if s.empty:
            continue
        series_data[sid] = s
        sids.append(sid)
    frame = pd.DataFrame({sid: series_data[sid] for sid in sids})
    frame = frame.sort_index()
    frame.index.name = "Year"
    return frame


def write_master_csv(frame: pd.DataFrame, registry: dict, path: Path) -> None:
    """Write the master CSV: row1 names, row2 IDs, row3 units, row4+ data."""
    series = registry["series"]
    sids = list(frame.columns)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([""] + [series.get(s, {}).get("name", s) for s in sids])
        w.writerow(["Year"] + sids)
        w.writerow([""] + [series_units(series.get(s, {})) for s in sids])
        for year, row in frame.iterrows():
            w.writerow([int(year)] + [
                "" if pd.isna(v) else v for v in row.tolist()
            ])


def write_master_xlsx(frame: pd.DataFrame, registry: dict, path: Path) -> None:
    """Write the master XLSX with name/ID/units header rows."""
    series = registry["series"]
    sids = list(frame.columns)
    header = pd.DataFrame(
        [
            [series.get(s, {}).get("name", s) for s in sids],
            sids,
            [series_units(series.get(s, {})) for s in sids],
        ],
        columns=sids,
    )
    body = frame.reset_index()
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        # Header block (3 rows) then data, all on one sheet.
        header.to_excel(xl, sheet_name="All Time Series", index=False, header=False, startrow=0)
        body.to_excel(xl, sheet_name="All Time Series", index=False, startrow=3)


def write_codebook(registry: dict, series_data: dict[str, pd.Series], path: Path) -> int:
    """Write the 16-column codebook CSV. Returns row count."""
    cols = [
        "series_id", "name", "definition", "units", "frequency",
        "coverage_start", "coverage_end", "n_observations", "content_type",
        "chapter", "figures", "source_primary", "source_extension",
        "extended", "splice_year", "notes",
    ]
    rows = 0
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for sid in sorted(series_data.keys()):
            entry = registry["series"].get(sid, {})
            s = series_data[sid].dropna()
            ext = entry.get("extension") if isinstance(entry.get("extension"), dict) else None
            w.writerow({
                "series_id": sid,
                "name": entry.get("name", sid),
                "definition": entry.get("description") or entry.get("name", sid),
                "units": series_units(entry),
                "frequency": (ext or {}).get("frequency", "annual"),
                "coverage_start": int(s.index.min()) if len(s) else "",
                "coverage_end": int(s.index.max()) if len(s) else "",
                "n_observations": int(len(s)),
                "content_type": content_type(entry),
                "chapter": entry.get("chapter", ""),
                "figures": ", ".join(entry.get("figures", []) or []),
                "source_primary": primary_source(entry),
                "source_extension": extension_source(entry),
                "extended": "Yes" if ext else "No",
                "splice_year": (ext or {}).get("splice_year", ""),
                "notes": entry.get("notes", "") or "",
            })
            rows += 1
    return rows


def copy_extenbooks(registry: dict, extenbook_dir: Path, series_ids: list[str],
                    dest: Path) -> int:
    """Copy per-series extenbooks, renaming to descriptive snake_case.

    Tries `{sid}_extenbook.xlsx` first (canonical); falls back to `{sid}.xlsx`.
    """
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for sid in series_ids:
        src = extenbook_dir / f"{sid}_extenbook.xlsx"
        if not src.exists():
            src = extenbook_dir / f"{sid}.xlsx"
        if not src.exists():
            continue
        name = registry["series"].get(sid, {}).get("name", sid)
        dst = dest / f"{sid}_{snake_case(name)}.xlsx"
        shutil.copy2(src, dst)
        copied += 1
    return copied


def write_readme(registry: dict, version: str, series_count: int,
                 year_min: int, year_max: int, path: Path) -> None:
    cfg = registry.get("drive_config", {})
    ow = cfg.get("original_work", {})
    title = ow.get("title", "the source work")
    lines = [
        "=" * 64,
        f"  {title}",
        "  Empirical Data Replication and Extension Package",
        f"  Data Package Version {version}",
        "=" * 64,
        "",
        "WHAT IS THIS?",
        "-------------",
        f"This folder contains {series_count} constructed economic data",
        f"series covering {year_min} to {year_max}, based on the empirical",
        "work in:",
        "",
        f"  {ow.get('author', '')}, \"{title}\" ({ow.get('year', '')})",
        f"  {ow.get('publisher', '')}",
        "",
        "Every series has been reconstructed from its original public",
        "source, validated against the book's published tables, and",
        "extended through the present where the underlying source",
        "remains available.",
        "",
        "",
        "HOW TO READ A SERIES ID",
        "-----------------------",
        "Each series has an identifier of the form S### (S001, S002, ...).",
        "Composite series may carry suffixes: -A/-B (raw historical",
        "sources), -EXT (modern API extension), -COMBINED (spliced final",
        "series). The bare S### is always the final published series.",
        "",
        "",
        "CONTENTS",
        "--------",
        f"All_Series_v{version}.xlsx        All series (Excel)",
        f"All_Series_v{version}.csv         All series (CSV)",
        f"Codebook_v{version}.csv           Data dictionary (one row per series)",
        f"Methodology_v{version}.pdf        Full methodology",
        "README_codebook_columns.md         Codebook column reference",
        "README_per_series_excel_format.md  Per-series workbook layout reference",
        "CITATION.txt                       How to cite this data",
        "Series/                            Individual series workbooks",
        "README.txt                         This file",
        "",
        "",
        "CONTACT",
        "-------",
        f"{cfg.get('author', {}).get('first_name', '')} "
        f"{cfg.get('author', {}).get('last_name', '')}".strip(),
        cfg.get("institution", ""),
        cfg.get("email", ""),
        "",
        "",
        "LICENSE",
        "-------",
        cfg.get("license", ""),
        "",
        "=" * 64,
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_citation(registry: dict, version: str, path: Path) -> None:
    cfg = registry.get("drive_config", {})
    ow = cfg.get("original_work", {})
    author = cfg.get("author", {})
    last = author.get("last_name", "")
    first = author.get("first_name", "")
    title = ow.get("title", "the source work")
    lines = [
        "=" * 64,
        "  HOW TO CITE THIS DATA",
        "=" * 64,
        "",
        "If you use this data in your research, please cite:",
        "",
        f"  {last}, {first}. (2026).",
        f"  {title} -- Empirical Data Replication and Extension",
        f"  Package [Data set], Data Package Version {version}.",
        f"  {cfg.get('institution', '')}.",
        f"  Based on: {ow.get('author', '')}, \"{title}\"",
        f"  ({ow.get('year', '')}). {ow.get('publisher', '')}.",
        "",
        "",
        "ORIGINAL WORK",
        "-------------",
        "Please also cite the original work when using this data:",
        "",
        f"  {ow.get('author', '')}. ({ow.get('year', '')}).",
        f"  {title}.",
        f"  {ow.get('publisher', '')}.",
        "",
        "=" * 64,
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an Anu Drive distribution package")
    parser.add_argument("project_root", help="Path to the project root")
    parser.add_argument("--version", help="Drive package version (e.g. 1.3)")
    args = parser.parse_args()

    project = Path(args.project_root).resolve()
    registry_path = project / "Technical" / "series_registry.json"
    if not registry_path.exists():
        print(f"ERROR: registry not found at {registry_path}", file=sys.stderr)
        return 2

    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)

    cfg = registry.get("drive_config", {})
    # Synthesize drive_config from top-level fields if absent. Lets older
    # projects ship without a registry edit at the cost of placeholder values
    # (institution, license, contact) the user should override.
    if not cfg:
        cfg = {
            "drive_version": "1.0",
            "original_work": {
                "title": registry.get("original_work", registry.get("book", "")),
                "author": "",
                "year": "",
                "publisher": "",
            },
            "author": {
                "first_name": registry.get("author", "").split()[0] if registry.get("author") else "",
                "last_name": " ".join(registry.get("author", "").split()[1:]) if registry.get("author") else "",
            },
            "institution": "",
            "email": "",
            "license": "CC-BY-4.0",
        }
    # write_readme / write_citation read cfg from registry["drive_config"];
    # propagate any synthesized values so the downstream helpers see them.
    registry["drive_config"] = cfg
    project_name = registry.get("project", "Project")
    version = args.version or cfg.get("drive_version", "1.0")

    # Canonical anu-replicator layout; falls back to project-root chopped/extenbooks
    # for older or non-replicator projects.
    final_data = project / "Technical" / "ANU_REPLICATOR" / "data" / "final-data"
    final_series_dir = final_data / "series"
    extenbook_dir = final_data / "extenbooks"
    if not final_series_dir.exists():
        alt_series = project / "Technical" / "chopped"
        alt_extenbooks = project / "Technical" / "extenbooks"
        if alt_series.exists():
            final_series_dir = alt_series
            extenbook_dir = alt_extenbooks
            print(f"  using fallback paths: chopped={final_series_dir}, extenbooks={extenbook_dir}")
        else:
            print(f"ERROR: final series dir not found at {final_data / 'series'} or {alt_series}",
                  file=sys.stderr)
            return 2

    out_dir = project / "Outputs" / f"{project_name}_Drive_v{version}"
    series_out = out_dir / "Series"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Anu Drive — generating {project_name} Drive package v{version}")
    print(f"  output: {out_dir}")

    series_data = collect_final_series(final_series_dir)
    print(f"  collected {len(series_data)} final series")

    frame = build_master_frame(registry, series_data)
    year_min, year_max = int(frame.index.min()), int(frame.index.max())

    write_master_csv(frame, registry, out_dir / f"{project_name}_All_Series_v{version}.csv")
    write_master_xlsx(frame, registry, out_dir / f"{project_name}_All_Series_v{version}.xlsx")
    print(f"  wrote master CSV + XLSX ({len(frame.columns)} series, {year_min}-{year_max})")

    rows = write_codebook(registry, series_data, out_dir / f"{project_name}_Codebook_v{version}.csv")
    print(f"  wrote codebook ({rows} rows)")

    copied = copy_extenbooks(registry, extenbook_dir, sorted(series_data.keys()), series_out)
    print(f"  copied {copied} per-series workbooks to Series/")

    # Methodology PDF — newest match in Technical/ or an existing Drive package.
    pdf_candidates = sorted(
        list((project / "Technical").glob(f"{project_name}_Methodology*.pdf"))
        + list((project / "Outputs").glob(f"{project_name}_Drive_v*/{project_name}_Methodology*.pdf")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if pdf_candidates:
        shutil.copy2(pdf_candidates[0], out_dir / f"{project_name}_Methodology_v{version}.pdf")
        print(f"  copied methodology PDF from {pdf_candidates[0].name}")
    else:
        print("  WARNING: no methodology PDF found — package incomplete")

    # Carry forward the two human-readable explainer files if a prior package has them.
    for explainer in ("README_codebook_columns.md", "README_per_series_excel_format.md"):
        prior = sorted(
            (project / "Outputs").glob(f"{project_name}_Drive_v*/{explainer}"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        if prior:
            shutil.copy2(prior[0], out_dir / explainer)

    write_readme(registry, version, len(series_data), year_min, year_max,
                 out_dir / "README.txt")
    write_citation(registry, version, out_dir / "CITATION.txt")
    print("  wrote README.txt + CITATION.txt")

    # Currency check: registry series vs what we shipped.
    registry_series = set(registry["series"].keys())
    shipped = set(series_data.keys())
    missing = sorted(registry_series - shipped)
    if missing:
        print(f"  NOTE: {len(missing)} registry series have no final CSV and were "
              f"not shipped: {', '.join(missing[:10])}"
              + (" ..." if len(missing) > 10 else ""))

    print(f"Done. Package at {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
