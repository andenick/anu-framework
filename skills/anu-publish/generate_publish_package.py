#!/usr/bin/env python3
"""Anu Publish — GitHub-replication distribution package generator.

Transforms an internal Anu Framework project into a clean, publishable
GitHub export: scrubbed replication code, final data, README, CITATION.cff,
LICENSE, and a machine-readable MANIFEST.json. Runs the P01-P12
pre-publication validation gate and writes an optional PUBLISH_AUDIT.json.

This is the canonical implementation of the ``/anu-publish package`` and
``/anu-publish validate`` commands.

Usage:
    python generate_publish_package.py <project_root>
        [--profile data-only|data+pipeline|data+pipeline+viz|full]
        [--version X.Y.Z] [--json]

Profiles (each is a superset of the one before):
    data-only          final-data CSVs + codebook + README + CITATION.cff + LICENSE
    data+pipeline      + replicator code (loading/, processing/, lib/, config/,
                       replicate.py, requirements.txt)  [default]
    data+pipeline+viz  + visualization app
    full               + per-series docs (DPR/EPR/decomposition)

Source of truth: {project}/Technical/series_registry.json
Output:          {project}/Outputs/{Project}_Publish_v{VERSION}/

Part of the Anu Framework v11.0 — see anu-publish/SKILL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Constants — patterns shared with the sibling anu-archive generator
# --------------------------------------------------------------------------

EXCLUDE_DIR_NAMES = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", "cache",
    ".ipynb_checkpoints", ".claude", ".codex", ".cursor", ".venv", "venv",
    "node_modules",
}
EXCLUDE_FILE_NAMES = {"api_keys.env", ".env", "PROGRESS_LOG.md"}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+]{20,}"),
]
ABS_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:[\\/]|/home/|/Users/|\\\\[A-Za-z])")
ARCANUM_REF_PATTERN = re.compile(r"(?i)\b(arcanum|council/druck|\bfreenic\b|\bRobin\b)")

TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".py", ".csv", ".yml", ".yaml", ".cff",
    ".tex", ".r", ".cfg", ".ini", ".toml", ".rst", ".sh",
}

PROFILES = ("data-only", "data+pipeline", "data+pipeline+viz", "full")


# --------------------------------------------------------------------------
# Filesystem helpers
# --------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path) -> int:
    """Copy a directory tree, skipping noise dirs and excluded files.

    Returns the number of files copied.
    """
    count = 0
    if not src.exists():
        return 0
    for item in src.rglob("*"):
        if any(part in EXCLUDE_DIR_NAMES for part in item.parts):
            continue
        if item.is_file() and item.name not in EXCLUDE_FILE_NAMES:
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            count += 1
    return count


def copy_glob(src_dir: Path, patterns: list[str], dst: Path) -> int:
    """Copy files matching any glob pattern from a directory. Returns count."""
    count = 0
    if not src_dir.exists():
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for item in sorted(src_dir.glob(pattern)):
            if item.is_file() and item.name not in EXCLUDE_FILE_NAMES:
                shutil.copy2(item, dst / item.name)
                count += 1
    return count


def copy_file(src: Path, dst: Path) -> bool:
    """Copy a single file if it exists. Returns True on success."""
    if src.exists() and src.is_file() and src.name not in EXCLUDE_FILE_NAMES:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def first_existing(*candidates: Path) -> Path | None:
    """Return the first path that exists, or None."""
    for c in candidates:
        if c.exists():
            return c
    return None


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

class Report:
    """Accumulates PASS/WARN/FAIL check results for the pre-publication gate."""

    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, check_id: str, severity: str, passed: bool, detail: str) -> None:
        """Record a check result. severity is FAIL or WARN."""
        self.checks.append({
            "id": check_id,
            "severity": severity,
            "status": "PASS" if passed else severity,
            "passed": passed,
            "detail": detail,
        })

    @property
    def failures(self) -> list[dict]:
        return [c for c in self.checks if not c["passed"] and c["severity"] == "FAIL"]

    @property
    def warnings(self) -> list[dict]:
        return [c for c in self.checks if not c["passed"] and c["severity"] == "WARN"]

    def print_summary(self) -> None:
        """Print every check result to stdout."""
        for c in self.checks:
            marker = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}[c["status"]]
            print(f"  {marker}  {c['id']}: {c['detail']}")
        print(f"  Summary: {len(self.failures)} failures, "
              f"{len(self.warnings)} warnings, "
              f"{len(self.checks)} checks total")


# --------------------------------------------------------------------------
# Scrubbing
# --------------------------------------------------------------------------

def scan_text_file(path: Path) -> dict:
    """Scan a single text file for secrets, absolute paths, Arcanum refs.

    Returns a dict with boolean flags and the first offending snippet for
    each category.
    """
    result = {
        "secret": False, "secret_snippet": "",
        "abs_path": False, "abs_path_snippet": "",
        "arcanum_ref": False, "arcanum_ref_snippet": "",
    }
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return result
    for pat in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            result["secret"] = True
            result["secret_snippet"] = m.group(0)[:80]
            break
    m = ABS_PATH_PATTERN.search(text)
    if m:
        result["abs_path"] = True
        # Capture a little context around the match for the report.
        start = max(0, m.start() - 10)
        result["abs_path_snippet"] = text[start:m.start() + 40].replace("\n", " ")
    m = ARCANUM_REF_PATTERN.search(text)
    if m:
        result["arcanum_ref"] = True
        result["arcanum_ref_snippet"] = m.group(0)
    return result


def scrub_export(export_dir: Path) -> dict:
    """Scan every text file in the export directory tree.

    Returns a dict of category -> list of {path, snippet} hits.
    """
    hits: dict[str, list[dict]] = {"secrets": [], "abs_paths": [], "arcanum_refs": []}
    for item in sorted(export_dir.rglob("*")):
        if not item.is_file():
            continue
        if item.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = str(item.relative_to(export_dir)).replace("\\", "/")
        scan = scan_text_file(item)
        if scan["secret"]:
            hits["secrets"].append({"path": rel, "snippet": scan["secret_snippet"]})
        if scan["abs_path"]:
            hits["abs_paths"].append({"path": rel, "snippet": scan["abs_path_snippet"]})
        if scan["arcanum_ref"]:
            hits["arcanum_refs"].append({"path": rel, "snippet": scan["arcanum_ref_snippet"]})
    return hits


# --------------------------------------------------------------------------
# Publication artifact generation
# --------------------------------------------------------------------------

def citation_key(cfg: dict, project_name: str) -> str:
    """Build a BibTeX-style citation key: {author_last}{year}_{project_slug}."""
    last = cfg.get("author", {}).get("last_name", "author").lower()
    last = re.sub(r"[^a-z]", "", last) or "author"
    slug = re.sub(r"[^a-z0-9]", "", project_name.lower()) or "project"
    return f"{last}{datetime.now().year}_{slug}"


def write_citation_cff(export_dir: Path, registry: dict, version: str) -> None:
    """Render CITATION.cff from drive_config metadata."""
    cfg = registry.get("drive_config", {})
    author = cfg.get("author", {})
    ow = cfg.get("original_work", {})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "cff-version: 1.2.0",
        'message: "If you use this data, please cite it as below."',
        f'title: "{cfg.get("project_title", registry.get("project", "Project"))}"',
        f'version: "{version}"',
        f'date-released: "{today}"',
        "authors:",
        f'  - family-names: "{author.get("last_name", "")}"',
        f'    given-names: "{author.get("first_name", "")}"',
    ]
    if author.get("orcid"):
        lines.append(f'    orcid: "{author["orcid"]}"')
    if cfg.get("institution"):
        lines.append(f'    affiliation: "{cfg["institution"]}"')
    lines += [
        f'repository-code: "{cfg.get("repo_url", "")}"',
        f'license: {_spdx_license(cfg.get("license", "MIT"))}',
        "keywords:",
        "  - economics",
        "  - data-replication",
        "  - reproducible-research",
    ]
    if ow:
        lines += [
            "references:",
            "  - type: book",
            "    authors:",
            f'      - name: "{ow.get("author", "")}"',
            f'    title: "{ow.get("title", "")}"',
            f'    year: {ow.get("year", "")}',
        ]
        if ow.get("publisher"):
            lines += [
                "    publisher:",
                f'      name: "{ow["publisher"]}"',
            ]
    (export_dir / "CITATION.cff").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _spdx_license(license_str: str) -> str:
    """Best-effort map of a free-text license field to an SPDX identifier."""
    s = (license_str or "").upper()
    if "MIT" in s:
        return "MIT"
    if "CC-BY-4" in s or "CC BY 4" in s:
        return "CC-BY-4.0"
    if "APACHE" in s:
        return "Apache-2.0"
    if "GPL" in s:
        return "GPL-3.0-or-later"
    if "BSD" in s:
        return "BSD-3-Clause"
    return "MIT"


MIT_LICENSE_TEMPLATE = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def ensure_license(export_dir: Path, registry: dict, existing: Path | None) -> None:
    """Copy an existing LICENSE, or synthesize an MIT LICENSE if absent."""
    if existing is not None and copy_file(existing, export_dir / "LICENSE"):
        return
    cfg = registry.get("drive_config", {})
    author = cfg.get("author", {})
    name = f"{author.get('first_name', '')} {author.get('last_name', '')}".strip() or "the authors"
    (export_dir / "LICENSE").write_text(
        MIT_LICENSE_TEMPLATE.format(year=datetime.now().year, author=name),
        encoding="utf-8",
    )


def write_readme(export_dir: Path, registry: dict, version: str, profile: str,
                 series_count: int) -> None:
    """Render README.md from drive_config metadata and the chosen profile."""
    cfg = registry.get("drive_config", {})
    ow = cfg.get("original_work", {})
    author = cfg.get("author", {})
    project_name = registry.get("project", "Project")
    title = cfg.get("project_title", f"{project_name}: Data Replication Package")
    repo = cfg.get("repo_url", "")
    has_pipeline = profile != "data-only"
    has_viz = profile in ("data+pipeline+viz", "full")

    lines = [
        f"# {title}",
        "",
        f"A reproducible replication and extension of the empirical data in "
        f"*{ow.get('title', 'the source work')}* "
        f"({ow.get('author', '')}, {ow.get('year', '')}, {ow.get('publisher', '')}). "
        f"This package ships {series_count} constructed economic data series "
        "with full provenance.",
        "",
        f"**Package version:** {version}  ",
        f"**Profile:** `{profile}`  ",
        f"**Framework:** Anu Framework v11.0",
        "",
    ]

    if has_pipeline:
        lines += [
            "## Quick Start",
            "",
            f"1. Clone: `git clone {repo}`" if repo else "1. Clone this repository",
            "2. Install: `pip install -r requirements.txt`",
            "3. API keys: `cp config/api_keys.env.example config/api_keys.env` "
            "and fill in your own (free) keys",
            "4. Run: `python replicate.py`",
            "",
            "Re-running the pipeline regenerates every series from its public "
            "source. No internal tools, private databases, or Arcanum "
            "infrastructure are required.",
            "",
        ]
    else:
        lines += [
            "## Quick Start",
            "",
            "This is a **data-only** release. The constructed series live under "
            "`data/` as CSV files, with a codebook describing every variable. "
            "Import `data/` directly into R, Python, Stata, or Excel.",
            "",
        ]

    lines += [
        "## Contents",
        "",
        "| Path | Description |",
        "|---|---|",
        "| `data/` | Final constructed data series (CSV) and codebook. |",
        "| `README.md` | This file. |",
        "| `CITATION.cff` | Machine-readable citation metadata. |",
        "| `LICENSE` | License terms. |",
        "| `MANIFEST.json` | Inventory of every file with size and SHA-256. |",
    ]
    if has_pipeline:
        lines += [
            "| `replicate.py` | Pipeline entry point — regenerates all series. |",
            "| `requirements.txt` | Python dependencies. |",
            "| `loading/` | L## loader scripts (fetch raw source data). |",
            "| `processing/` | P## processor scripts (transform, splice, extend). |",
            "| `lib/` | Shared replication library. |",
            "| `config/` | Registry, chapter map, API-key template. |",
            "| `validation/` | V## validation checks. |",
        ]
    if has_viz:
        lines.append("| `visualization/` | Interactive visualization app. |")
    if profile == "full":
        lines.append("| `docs/series/` | Per-series provenance records (DPR/EPR/decomposition). |")
    lines += [
        "",
        "## Data Sources",
        "",
        "Every series is reconstructed from its original public source and, "
        "where the underlying source remains available, extended to the present "
        "using public statistical APIs. See the per-series codebook "
        "(`data/`) for the source of each variable.",
        "",
        "## Citation",
        "",
        f"> {author.get('last_name', '')}, {author.get('first_name', '')}. "
        f"({datetime.now().year}). *{title}* "
        f"[Data set, v{version}]. {cfg.get('institution', '')}.",
        "",
        "See `CITATION.cff` for machine-readable citation metadata. Please also "
        f"cite the original work: {ow.get('author', '')}. ({ow.get('year', '')}). "
        f"*{ow.get('title', '')}*. {ow.get('publisher', '')}.",
        "",
        "## License",
        "",
        cfg.get("license", "MIT") + ". See `LICENSE` for full terms.",
        "",
    ]
    (export_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gitignore(export_dir: Path) -> None:
    """Write a standard .gitignore for a published replication package."""
    lines = [
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        ".venv/",
        "venv/",
        ".pytest_cache/",
        ".mypy_cache/",
        "",
        "# Secrets — never commit real API keys",
        "config/api_keys.env",
        ".env",
        "",
        "# Cached / regenerated data",
        "data/cache/",
        "data/raw-data/api/",
        "*.log",
        "",
        "# OS noise",
        ".DS_Store",
        "Thumbs.db",
    ]
    (export_dir / ".gitignore").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Package assembly
# --------------------------------------------------------------------------

def assemble_export(project: Path, registry: dict, version: str,
                    profile: str) -> tuple[Path, dict]:
    """Build the export directory for the given profile.

    Returns (export_dir, stats) where stats records per-section file counts.
    """
    project_name = registry.get("project", "Project")
    export_dir = project / "Outputs" / f"{project_name}_Publish_v{version}"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    export_dir.mkdir(parents=True)

    stats: dict[str, int] = {}

    print(f"Anu Publish — generating {project_name} Publish v{version} "
          f"[profile: {profile}]")
    print(f"  output: {export_dir}")

    replicator = first_existing(
        project / "Technical" / f"{project_name.lower()}-replicator",
        project / "Technical" / "reference-replicator",
        project / "Technical" / "ANU_REPLICATOR",
    )
    final_data = project / "Technical" / "ANU_REPLICATOR" / "data" / "final-data"

    # ----- data/ — final-data CSVs + codebook (all profiles) -----
    data_dst = export_dir / "data"
    n_data = 0
    final_series = final_data / "series"
    if final_series.exists():
        n_data += copy_glob(final_series, ["*_final.csv"], data_dst / "series")
    chopped = final_data / "chopped"
    if chopped.exists():
        n_data += copy_glob(chopped, ["*_chopped.csv"], data_dst / "chopped")
    # Codebook — look in a prior Drive package or the final-data reports dir.
    codebook = first_existing(
        *sorted((project / "Outputs").glob(f"{project_name}_Drive_v*/{project_name}_Codebook_v*.csv"),
                key=lambda p: p.stat().st_mtime, reverse=True),
        *sorted((final_data / "reports").glob("*odebook*.csv")) if (final_data / "reports").exists() else [],
    )
    if codebook is not None and copy_file(codebook, data_dst / "codebook.csv"):
        n_data += 1
    stats["data"] = n_data
    print(f"  data/            {n_data} files")

    # ----- pipeline (data+pipeline and up) -----
    if profile != "data-only" and replicator is not None:
        n_pipe = 0
        for sub in ("loading", "processing", "lib", "config", "validation", "tests"):
            n_pipe += copy_tree(replicator / sub, export_dir / sub)
        for fname in ("replicate.py", "requirements.txt", "INSTALL.md", "CHANGELOG.md"):
            if copy_file(replicator / fname, export_dir / fname):
                n_pipe += 1
        # Replicator docs (decision log, assumptions) land under docs/.
        n_pipe += copy_glob(replicator / "docs",
                            ["DECISION_LOG.md", "ASSUMPTIONS.md", "*.md"],
                            export_dir / "docs")
        stats["pipeline"] = n_pipe
        print(f"  pipeline         {n_pipe} files")
    elif profile != "data-only":
        print("  pipeline         SKIPPED — no replicator directory found")
        stats["pipeline"] = 0

    # ----- visualization (data+pipeline+viz and up) -----
    if profile in ("data+pipeline+viz", "full"):
        viz_src = first_existing(
            project / "Technical" / "ANU_VIZ",
            project / "Technical" / "ShinyApp",
        )
        n_viz = copy_tree(viz_src, export_dir / "visualization") if viz_src else 0
        stats["visualization"] = n_viz
        print(f"  visualization/   {n_viz} files"
              + ("" if viz_src else " — no viz app found"))

    # ----- per-series docs (full only) -----
    if profile == "full":
        docs_series = project / "Technical" / "docs" / "series"
        n_docs = copy_glob(docs_series,
                           ["*_DPR.md", "*_EPR.md", "*_DECOMPOSITION.md"],
                           export_dir / "docs" / "series")
        stats["docs"] = n_docs
        print(f"  docs/series/     {n_docs} files")

    # ----- publication artifacts (all profiles) -----
    registry_dst = export_dir / "config" / "series_registry.json"
    registry_dst.parent.mkdir(parents=True, exist_ok=True)
    copy_file(project / "Technical" / "series_registry.json", registry_dst)

    series_count = len(registry.get("series", {}))

    # README/LICENSE/CITATION — prefer existing replicator copies, else synth.
    existing_readme = replicator / "README.md" if replicator else None
    # We always regenerate the README to guarantee profile-accurate content,
    # but a project-supplied LICENSE/CITATION is preferred over a synthesized one.
    write_readme(export_dir, registry, version, profile, series_count)
    existing_license = (replicator / "LICENSE") if replicator and (replicator / "LICENSE").exists() else None
    ensure_license(export_dir, registry, existing_license)
    existing_cff = (replicator / "CITATION.cff") if replicator else None
    if existing_cff and existing_cff.exists():
        copy_file(existing_cff, export_dir / "CITATION.cff")
    else:
        write_citation_cff(export_dir, registry, version)
    write_gitignore(export_dir)
    print("  artifacts        README.md, LICENSE, CITATION.cff, .gitignore")

    return export_dir, stats


# --------------------------------------------------------------------------
# MANIFEST
# --------------------------------------------------------------------------

def write_manifest(export_dir: Path, registry: dict, version: str,
                   profile: str) -> dict:
    """Write MANIFEST.json listing every file with size + sha256."""
    cfg = registry.get("drive_config", {})
    files = []
    total_bytes = 0
    for item in sorted(export_dir.rglob("*")):
        if not item.is_file() or item.name in ("MANIFEST.json", "PUBLISH_AUDIT.json"):
            continue
        rel = str(item.relative_to(export_dir)).replace("\\", "/")
        size = item.stat().st_size
        total_bytes += size
        files.append({
            "path": rel,
            "size": size,
            "sha256": sha256_file(item),
        })
    author = cfg.get("author", {})
    manifest = {
        "project": registry.get("project", "Project"),
        "publish_version": version,
        "profile": profile,
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
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
    }
    (export_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


# --------------------------------------------------------------------------
# Pre-publication validation gate (P01-P12)
# --------------------------------------------------------------------------

def validate_export(export_dir: Path, profile: str, scrub_hits: dict) -> Report:
    """Run the P01-P12 pre-publication gate. Returns a populated Report."""
    report = Report()
    has_pipeline = profile != "data-only"

    # P01 — README present
    readme = export_dir / "README.md"
    report.add("P01_README_EXISTS", "FAIL", readme.exists(),
               "README.md present" if readme.exists() else "README.md missing")

    # P02 — LICENSE present
    lic = export_dir / "LICENSE"
    report.add("P02_LICENSE_EXISTS", "FAIL", lic.exists(),
               "LICENSE present" if lic.exists() else "LICENSE missing")

    # P03 — CITATION.cff present and parseable as YAML-ish (cff-version line)
    cff = export_dir / "CITATION.cff"
    cff_ok = False
    cff_detail = "CITATION.cff missing"
    if cff.exists():
        text = cff.read_text(encoding="utf-8", errors="ignore")
        cff_ok = "cff-version:" in text and "title:" in text and "authors:" in text
        cff_detail = ("CITATION.cff parseable" if cff_ok
                      else "CITATION.cff missing required keys (cff-version/title/authors)")
    report.add("P03_CITATION_PARSEABLE", "FAIL", cff_ok, cff_detail)

    # P04 — MANIFEST.json present and valid JSON
    manifest_path = export_dir / "MANIFEST.json"
    manifest_ok = False
    manifest_detail = "MANIFEST.json missing"
    if manifest_path.exists():
        try:
            json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_ok = True
            manifest_detail = "MANIFEST.json valid"
        except json.JSONDecodeError as exc:
            manifest_detail = f"MANIFEST.json invalid JSON: {exc}"
    report.add("P04_MANIFEST_VALID", "FAIL", manifest_ok, manifest_detail)

    # P05 — data/ contains at least one final CSV
    data_dir = export_dir / "data"
    has_data = data_dir.exists() and any(data_dir.rglob("*.csv"))
    report.add("P05_DATA_PRESENT", "FAIL", has_data,
               "data/ contains CSV files" if has_data else "data/ has no CSV files")

    # P06 — codebook present
    codebook = data_dir / "codebook.csv"
    report.add("P06_CODEBOOK_PRESENT", "WARN", codebook.exists(),
               "data/codebook.csv present" if codebook.exists()
               else "data/codebook.csv missing — recommended for data releases")

    # P07 — runnable entry point (pipeline profiles only)
    if has_pipeline:
        entry = export_dir / "replicate.py"
        report.add("P07_ENTRY_POINT", "FAIL", entry.exists(),
                   "replicate.py present" if entry.exists()
                   else "replicate.py missing — no runnable entry point")
    else:
        report.add("P07_ENTRY_POINT", "WARN", True,
                   "data-only profile — no entry point required")

    # P08 — requirements.txt (pipeline profiles only)
    if has_pipeline:
        reqs = export_dir / "requirements.txt"
        report.add("P08_REQUIREMENTS", "FAIL", reqs.exists(),
                   "requirements.txt present" if reqs.exists()
                   else "requirements.txt missing")
    else:
        report.add("P08_REQUIREMENTS", "WARN", True,
                   "data-only profile — no requirements.txt required")

    # P09 — NO_SECRETS
    n_secrets = len(scrub_hits["secrets"])
    report.add("P09_NO_SECRETS", "FAIL", n_secrets == 0,
               "no secrets detected" if n_secrets == 0
               else f"{n_secrets} possible secret(s): "
                    + ", ".join(h["path"] for h in scrub_hits["secrets"][:5]))

    # P10 — NO_ABSOLUTE_PATHS
    n_paths = len(scrub_hits["abs_paths"])
    report.add("P10_NO_ABSOLUTE_PATHS", "WARN", n_paths == 0,
               "no absolute machine paths" if n_paths == 0
               else f"{n_paths} file(s) with absolute paths: "
                    + ", ".join(h["path"] for h in scrub_hits["abs_paths"][:5]))

    # P11 — NO_ARCANUM_REFS
    n_arc = len(scrub_hits["arcanum_refs"])
    report.add("P11_NO_ARCANUM_REFS", "WARN", n_arc == 0,
               "no internal Arcanum references" if n_arc == 0
               else f"{n_arc} file(s) with internal references: "
                    + ", ".join(h["path"] for h in scrub_hits["arcanum_refs"][:5]))

    # P12 — NO_PYCACHE / no excluded artifacts leaked into the export
    pycache = [str(p.relative_to(export_dir)).replace("\\", "/")
               for p in export_dir.rglob("*")
               if p.is_dir() and p.name == "__pycache__"]
    leaked = [str(p.relative_to(export_dir)).replace("\\", "/")
              for p in export_dir.rglob("*")
              if p.is_file() and p.name in EXCLUDE_FILE_NAMES]
    clean = not pycache and not leaked
    report.add("P12_NO_BUILD_ARTIFACTS", "FAIL", clean,
               "no __pycache__ or secret files in export" if clean
               else f"leaked artifacts: {(pycache + leaked)[:5]}")

    return report


def write_audit(export_dir: Path, registry: dict, version: str, profile: str,
                stats: dict, scrub_hits: dict, report: Report) -> Path:
    """Write PUBLISH_AUDIT.json with the full machine-readable audit."""
    audit = {
        "project": registry.get("project", "Project"),
        "publish_version": version,
        "profile": profile,
        "generated": datetime.now(timezone.utc).isoformat(),
        "section_file_counts": stats,
        "scrub": {
            "secrets": scrub_hits["secrets"],
            "absolute_paths": scrub_hits["abs_paths"],
            "arcanum_references": scrub_hits["arcanum_refs"],
        },
        "validation": {
            "checks": report.checks,
            "failure_count": len(report.failures),
            "warning_count": len(report.warnings),
            "passed": len(report.failures) == 0,
        },
    }
    path = export_dir / "PUBLISH_AUDIT.json"
    path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    """CLI entry point. Returns a process exit code (0 = clean, 1 = failures)."""
    parser = argparse.ArgumentParser(
        description="Generate an Anu Publish GitHub-replication package")
    parser.add_argument("project_root", help="Path to the project root")
    parser.add_argument("--profile", choices=PROFILES, default="data+pipeline",
                        help="Packaging profile (default: data+pipeline)")
    parser.add_argument("--version", help="Publish package version (e.g. 1.0.0)")
    parser.add_argument("--json", action="store_true",
                        help="Write PUBLISH_AUDIT.json with the full audit")
    args = parser.parse_args()

    project = Path(args.project_root).resolve()
    registry_path = project / "Technical" / "series_registry.json"
    if not registry_path.exists():
        print(f"ERROR: registry not found at {registry_path}", file=sys.stderr)
        return 2

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: registry is not valid JSON: {exc}", file=sys.stderr)
        return 2

    cfg = registry.get("drive_config", {})
    version = args.version or cfg.get("publish_version") or cfg.get("drive_version", "1.0.0")

    export_dir, stats = assemble_export(project, registry, version, args.profile)

    # Scrub the assembled tree before manifesting.
    print()
    print("-- Scrubbing --")
    scrub_hits = scrub_export(export_dir)
    print(f"  secrets: {len(scrub_hits['secrets'])}  "
          f"absolute paths: {len(scrub_hits['abs_paths'])}  "
          f"arcanum refs: {len(scrub_hits['arcanum_refs'])}")

    manifest = write_manifest(export_dir, registry, version, args.profile)
    print(f"  MANIFEST: {manifest['file_count']} files, "
          f"{manifest['total_bytes'] / 1024 / 1024:.1f} MB")

    print()
    print("-- Pre-publication gate (P01-P12) --")
    report = validate_export(export_dir, args.profile, scrub_hits)
    report.print_summary()

    if args.json:
        audit_path = write_audit(export_dir, registry, version, args.profile,
                                 stats, scrub_hits, report)
        print(f"  audit: {audit_path.name}")

    print(f"Done. Package at {export_dir}")
    return 0 if not report.failures else 1


if __name__ == "__main__":
    sys.exit(main())
