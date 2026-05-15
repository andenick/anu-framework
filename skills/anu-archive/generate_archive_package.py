#!/usr/bin/env python3
"""Anu Archive — comprehensive audit-grade replication archive generator.

Bundles the complete provenance trail of an Anu Framework project into a
single versioned, checksummed archive: code, data, per-series and
per-figure provenance records, knowledge-base extractions, validation
logs, decision log, review history, ledger, and glossary. Writes a
machine-readable MANIFEST.json and a sha256sum-compatible CHECKSUMS.txt,
runs the A01-A13 validation rules, and packages the result as a .zip.

Usage:
    python generate_archive_package.py <project_root> [--version X.Y] [--no-zip]

Output: {project}/Outputs/{ProjectName}_Archive_v{VERSION}/  (+ .zip)

Part of the Anu Framework v11.0 — see anu-archive/SKILL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "cache", ".ipynb_checkpoints"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
]
ABS_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:[\\/]|/home/|/Users/|\\\\)")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".py", ".csv", ".yml", ".yaml", ".cff", ".tex", ".r", ".R"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path) -> int:
    """Copy a directory tree, skipping noise dirs. Returns file count."""
    count = 0
    if not src.exists():
        return 0
    for item in src.rglob("*"):
        if any(part in EXCLUDE_DIR_NAMES for part in item.parts):
            continue
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            count += 1
    return count


def copy_glob(src_dir: Path, patterns: list[str], dst: Path) -> int:
    count = 0
    if not src_dir.exists():
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for item in src_dir.glob(pattern):
            if item.is_file():
                shutil.copy2(item, dst / item.name)
                count += 1
    return count


def copy_file(src: Path, dst: Path) -> bool:
    if src.exists() and src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def categorize(rel_path: Path) -> str:
    top = rel_path.parts[0] if rel_path.parts else ""
    return {
        "code": "code", "data": "data", "provenance": "provenance",
        "validation": "validation", "decisions": "decisions",
        "reviews": "reviews", "reference": "reference",
    }.get(top, "reference")


def build_archive(project: Path, version: str) -> tuple[Path, dict]:
    registry_path = project / "Technical" / "series_registry.json"
    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)
    project_name = registry.get("project", "Project")
    cfg = registry.get("drive_config", {})

    archive_dir = project / "Outputs" / f"{project_name}_Archive_v{version}"
    if archive_dir.exists():
        shutil.rmtree(archive_dir)
    archive_dir.mkdir(parents=True)

    print(f"Anu Archive — generating {project_name} Archive v{version}")
    print(f"  output: {archive_dir}")

    # code/ — mirror of the anu-publish repo
    code_src = project / "Technical" / "cd2-replicator"
    n_code = copy_tree(code_src, archive_dir / "code")
    print(f"  code/        {n_code} files")

    # data/ — mirror of the latest Drive package
    drive_dirs = sorted((project / "Outputs").glob(f"{project_name}_Drive_v*"),
                        key=lambda p: p.name)
    n_data = 0
    if drive_dirs:
        latest_drive = drive_dirs[-1]
        master_dst = archive_dir / "data" / "master"
        master_dst.mkdir(parents=True, exist_ok=True)
        for item in latest_drive.iterdir():
            if item.is_file():
                shutil.copy2(item, master_dst / item.name)
                n_data += 1
        series_src = latest_drive / "Series"
        if series_src.exists():
            n_data += copy_tree(series_src, archive_dir / "data" / "series")
        # Methodology PDF up one level for prominence
        for pdf in master_dst.glob("*Methodology*.pdf"):
            shutil.copy2(pdf, archive_dir / "data" / "methodology.pdf")
            break
    print(f"  data/        {n_data} files (from {drive_dirs[-1].name if drive_dirs else 'NONE'})")

    # provenance/
    docs_series = project / "Technical" / "docs" / "series"
    n_prov = copy_glob(docs_series, ["*_DPR.md", "*_EPR.md", "*_DECOMPOSITION.md"],
                       archive_dir / "provenance" / "series")
    docs_figures = project / "Technical" / "docs" / "figures"
    n_fig = copy_glob(docs_figures, ["*_FPR.md"], archive_dir / "provenance" / "figures")
    kb_src = project / "Inputs" / "Robert" / "KB"
    n_kb = copy_tree(kb_src, archive_dir / "provenance" / "knowledge_base")
    copy_file(registry_path, archive_dir / "provenance" / "registry.json")
    print(f"  provenance/  {n_prov} series records, {n_fig} figure records, {n_kb} KB files")

    # validation/
    val_log = project / "Technical" / "ANU_REPLICATOR" / "data" / "final-data" / "logs" / "VALIDATION_LOG.json"
    n_val = 1 if copy_file(val_log, archive_dir / "validation" / "VALIDATION_LOG.json") else 0
    # Any validation reports living under Reviews
    reviews_root = project / "Technical" / "Reviews"
    n_val += copy_glob(reviews_root, ["*VALIDATION*.md", "*VALIDATION*.json"],
                       archive_dir / "validation")
    print(f"  validation/  {n_val} files")

    # decisions/
    repl_docs = project / "Technical" / "ANU_REPLICATOR" / "docs"
    n_dec = copy_glob(repl_docs, ["DECISION_LOG.md", "ASSUMPTIONS.md"],
                      archive_dir / "decisions")
    print(f"  decisions/   {n_dec} files")

    # reviews/
    n_rev = copy_tree(reviews_root, archive_dir / "reviews")
    print(f"  reviews/     {n_rev} files")

    # reference/
    ref_dst = archive_dir / "reference"
    ref_dst.mkdir(parents=True, exist_ok=True)
    n_ref = 0
    n_ref += copy_file(project / "Technical" / "ANU_LEDGER.json", ref_dst / "ledger.json")
    n_ref += copy_file(project / "GLOSSARY.md", ref_dst / "glossary.md")
    n_ref += copy_file(project / "Technical" / "PIPELINE_STATE.json", ref_dst / "pipeline_state.json")
    print(f"  reference/   {n_ref} files")

    # README.md
    _write_readme(archive_dir, registry, version)

    # MANIFEST.json + CHECKSUMS.txt
    manifest = _write_manifest(archive_dir, project, registry, version)
    _write_checksums(archive_dir, manifest)

    return archive_dir, manifest


def _write_readme(archive_dir: Path, registry: dict, version: str) -> None:
    cfg = registry.get("drive_config", {})
    ow = cfg.get("original_work", {})
    author = cfg.get("author", {})
    title = ow.get("title", "the source work")
    lines = [
        f"# {title} — Comprehensive Replication Archive",
        "",
        f"**Archive version:** {version}  ",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  ",
        f"**Framework:** Anu Framework v11.0  ",
        f"**License:** {cfg.get('license', '')}",
        "",
        "## What this is",
        "",
        "This archive is the audit-grade replication package for "
        f"{author.get('first_name', '')} {author.get('last_name', '')}'s reconstruction "
        f"and extension of the empirical data in *{title}* "
        f"({ow.get('author', '')}, {ow.get('year', '')}, {ow.get('publisher', '')}).",
        "",
        "It contains everything an outside auditor needs to verify every value "
        "and every methodological decision — without reaching back into the "
        "project's live internal workspace.",
        "",
        "## How to navigate",
        "",
        "| Directory | Contents |",
        "|---|---|",
        "| `code/` | The full reproduction pipeline. Run `python replicate.py` to regenerate all series. |",
        "| `data/` | The constructed data: master workbook, codebook, per-series Excel workbooks, methodology PDF. |",
        "| `provenance/series/` | Per-series Data Provenance Records (DPR), Extension Provenance Records (EPR), and decompositions. |",
        "| `provenance/figures/` | Per-figure Provenance Records (FPR) mapping series to the book's figures. |",
        "| `provenance/knowledge_base/` | Source-text extractions from the book — the ground-truth trail. |",
        "| `provenance/registry.json` | The canonical series registry: the single source of truth. |",
        "| `validation/` | Validation logs and reports — proof the data was checked. |",
        "| `decisions/` | The decision log and assumptions register — every methodological choice with rationale. |",
        "| `reviews/` | The complete quality-audit history. |",
        "| `reference/` | Artifact ledger, glossary, and pipeline-state snapshot. |",
        "",
        "## Integrity",
        "",
        "`MANIFEST.json` is the machine-readable inventory of every file in this "
        "archive, with size, SHA-256 hash, category, and original source path. "
        "`CHECKSUMS.txt` is a `sha256sum -c` compatible checksum file — run "
        "`sha256sum -c CHECKSUMS.txt` to verify archive integrity.",
        "",
        "## How to cite",
        "",
        f"> {author.get('last_name', '')}, {author.get('first_name', '')}. (2026). "
        f"*{title} — Comprehensive Replication Archive* "
        f"[Data set, Archive v{version}]. {cfg.get('institution', '')}.",
        "",
        f"Please also cite the original work: {ow.get('author', '')}. "
        f"({ow.get('year', '')}). *{title}*. {ow.get('publisher', '')}.",
        "",
        f"Repository: {cfg.get('repo_url', '')}",
        "",
    ]
    (archive_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(archive_dir: Path, project: Path, registry: dict, version: str) -> dict:
    cfg = registry.get("drive_config", {})
    files = []
    category_counts: dict[str, int] = {}
    total_bytes = 0

    for item in sorted(archive_dir.rglob("*")):
        if not item.is_file():
            continue
        if item.name in ("MANIFEST.json", "CHECKSUMS.txt"):
            continue
        rel = item.relative_to(archive_dir)
        size = item.stat().st_size
        cat = categorize(rel)
        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_bytes += size
        files.append({
            "path": str(rel).replace("\\", "/"),
            "size": size,
            "sha256": sha256_file(item),
            "category": cat,
        })

    author = cfg.get("author", {})
    manifest = {
        "project": registry.get("project", "Project"),
        "archive_version": version,
        "generated": datetime.now(timezone.utc).isoformat(),
        "framework_version": "Anu Framework v11.0",
        "citation": {
            "title": cfg.get("project_title", ""),
            "authors": [{
                "family-names": author.get("last_name", ""),
                "given-names": author.get("first_name", ""),
            }],
            "original_work": cfg.get("original_work", {}),
            "license": cfg.get("license", ""),
            "repository_code": cfg.get("repo_url", ""),
        },
        "category_counts": category_counts,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
    }
    (archive_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _write_checksums(archive_dir: Path, manifest: dict) -> None:
    lines = [f"{entry['sha256']}  {entry['path']}" for entry in manifest["files"]]
    (archive_dir / "CHECKSUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Validation (A01-A13)
# --------------------------------------------------------------------------

def validate_archive(archive_dir: Path) -> tuple[list[str], list[str]]:
    """Return (failures, warnings)."""
    failures: list[str] = []
    warnings: list[str] = []

    manifest_path = archive_dir / "MANIFEST.json"
    checksums_path = archive_dir / "CHECKSUMS.txt"
    readme_path = archive_dir / "README.md"

    # A01
    for name, p in [("MANIFEST.json", manifest_path), ("CHECKSUMS.txt", checksums_path),
                    ("README.md", readme_path)]:
        if not p.exists():
            failures.append(f"A01: {name} missing at archive root")
    if failures:
        return failures, warnings

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_paths = {e["path"]: e for e in manifest["files"]}

    # A02 — every file on disk is in the manifest
    on_disk = set()
    for item in archive_dir.rglob("*"):
        if item.is_file() and item.name not in ("MANIFEST.json", "CHECKSUMS.txt"):
            on_disk.add(str(item.relative_to(archive_dir)).replace("\\", "/"))
    for p in sorted(on_disk - set(manifest_paths)):
        failures.append(f"A02: file on disk not in manifest: {p}")

    # A03 + A04 — manifest entries resolve, hashes match
    for p, entry in manifest_paths.items():
        fpath = archive_dir / p
        if not fpath.exists():
            failures.append(f"A03: manifest entry has no file: {p}")
            continue
        if sha256_file(fpath) != entry["sha256"]:
            failures.append(f"A04: checksum mismatch: {p}")

    # A05/A06/A07/A08 — provenance coverage
    reg_path = archive_dir / "provenance" / "registry.json"
    if reg_path.exists():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
        prov_series = archive_dir / "provenance" / "series"
        prov_figures = archive_dir / "provenance" / "figures"
        dpr = {f.name.replace("_DPR.md", "") for f in prov_series.glob("*_DPR.md")} if prov_series.exists() else set()
        epr = {f.name.replace("_EPR.md", "") for f in prov_series.glob("*_EPR.md")} if prov_series.exists() else set()
        decomp = {f.name.replace("_DECOMPOSITION.md", "") for f in prov_series.glob("*_DECOMPOSITION.md")} if prov_series.exists() else set()
        fpr = {f.name.replace("_FPR.md", "") for f in prov_figures.glob("*_FPR.md")} if prov_figures.exists() else set()
        all_figs: set[str] = set()
        for sid, entry in registry.get("series", {}).items():
            if sid not in dpr:
                failures.append(f"A05: series {sid} has no DPR")
            if isinstance(entry.get("extension"), dict) and sid not in epr:
                failures.append(f"A06: extended series {sid} has no EPR")
            if sid not in decomp:
                warnings.append(f"A07: series {sid} has no decomposition")
            for fig in entry.get("figures", []) or []:
                all_figs.add(fig.replace(".", ""))
        for fig in sorted(all_figs):
            # FPR filenames use the Fig2.1 form; normalize both sides
            if fig not in {f.replace(".", "") for f in fpr}:
                warnings.append(f"A08: figure {fig} has no FPR")

    # A09/A10 — secrets + absolute paths
    for p in sorted(manifest_paths):
        fpath = archive_dir / p
        if fpath.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                failures.append(f"A09: possible secret in {p}")
                break
        if ABS_PATH_PATTERN.search(text):
            warnings.append(f"A10: absolute machine path in {p}")

    # A11 — code/ runnable entry point
    if not (archive_dir / "code" / "replicate.py").exists():
        failures.append("A11: code/replicate.py missing — no runnable entry point")

    # A12 — data/ has master + at least one per-series workbook
    data_master = archive_dir / "data" / "master"
    data_series = archive_dir / "data" / "series"
    has_master = data_master.exists() and any(data_master.glob("*All_Series*"))
    has_series = data_series.exists() and any(data_series.glob("*.xlsx"))
    if not has_master:
        failures.append("A12: data/master/ has no master workbook")
    if not has_series:
        failures.append("A12: data/series/ has no per-series workbooks")

    # A13 — glossary present and non-empty
    glossary = archive_dir / "reference" / "glossary.md"
    if not glossary.exists() or glossary.stat().st_size == 0:
        warnings.append("A13: reference/glossary.md missing or empty")

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an Anu Archive comprehensive replication package")
    parser.add_argument("project_root", help="Path to the project root")
    parser.add_argument("--version", help="Archive version (e.g. 1.0)")
    parser.add_argument("--no-zip", action="store_true", help="Skip .zip packaging")
    args = parser.parse_args()

    project = Path(args.project_root).resolve()
    registry_path = project / "Technical" / "series_registry.json"
    if not registry_path.exists():
        print(f"ERROR: registry not found at {registry_path}", file=sys.stderr)
        return 2

    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)
    version = args.version or registry.get("drive_config", {}).get("drive_version", "1.0")

    archive_dir, manifest = build_archive(project, version)

    print()
    print(f"  MANIFEST: {manifest['file_count']} files, "
          f"{manifest['total_bytes'] / 1024 / 1024:.1f} MB")
    print(f"  categories: {manifest['category_counts']}")

    print()
    print("── Validation (A01-A13) ──")
    failures, warnings = validate_archive(archive_dir)
    for w in warnings[:15]:
        print(f"  WARN  {w}")
    if len(warnings) > 15:
        print(f"  ... and {len(warnings) - 15} more warnings")
    for fail in failures[:15]:
        print(f"  FAIL  {fail}")
    if len(failures) > 15:
        print(f"  ... and {len(failures) - 15} more failures")
    print(f"  Summary: {len(failures)} failures, {len(warnings)} warnings")

    if not args.no_zip:
        zip_path = archive_dir.parent / f"{archive_dir.name}.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(archive_dir.rglob("*")):
                if item.is_file():
                    zf.write(item, item.relative_to(archive_dir.parent))
        print(f"  packaged: {zip_path.name} "
              f"({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")

    print(f"Done. Archive at {archive_dir}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
