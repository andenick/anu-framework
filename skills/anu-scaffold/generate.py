#!/usr/bin/env python3
"""anu-scaffold — Generate L01/P02/V03 script stubs from series_registry.json.

Reads a registry entry, picks a template (or uses the one specified),
renders it with the entry's fields, and writes three files to the project's
code/ tree.

Templates (in templates/):
  L01_direct_column.py.j2 / P02_direct_column.py.j2 / V03_direct_column.py.j2
  L01_derived.py.j2       / P02_derived.py.j2       / V03_derived.py.j2
  L01_matrix_summary.py.j2 / P02_matrix_summary.py.j2 / V03_matrix_summary.py.j2

Usage:
  python generate.py --series S501
  python generate.py --cohort wave_1_ch5 --template auto
  python generate.py --all-pending [--dry-run] [--force]

Project root is inferred from --project (or cwd by default). Project root must
contain series_registry.json. The generator picks templates from this skill's
templates/ directory, or from <project_root>/code/_scaffold_templates/ if that
override directory exists.

Part of the Anu Framework v11.0 — see anu-scaffold/SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATES = SKILL_DIR / "templates"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return re.sub(r"_+", "_", s)


def load_registry(project_root: Path) -> dict:
    reg_path = project_root / "series_registry.json"
    if not reg_path.exists():
        sys.exit(f"ERROR: {reg_path} not found. anu-scaffold requires a populated registry.")
    return json.loads(reg_path.read_text(encoding="utf-8"))


def select_template(entry: dict) -> str:
    """Auto-select a template name from the registry entry."""
    ctype = entry.get("content_type", "")
    construction = entry.get("construction", [])
    if ctype == "derived" or not any(s.get("op") == "load" for s in construction):
        return "derived"
    if ctype == "benchmark_only" or any("matrix" in str(s).lower() for s in construction):
        return "matrix_summary"
    return "direct_column"


def find_templates_dir(project_root: Path) -> Path:
    override = project_root / "code" / "_scaffold_templates"
    return override if override.is_dir() else DEFAULT_TEMPLATES


def render(template_path: Path, context: dict) -> str:
    """Minimal Jinja-style substitution — handles {{ key }} and {{ key|default("x") }}.

    Full Jinja2 is not a hard dependency for the framework; this lightweight
    substitution is enough for the three shipped templates.
    """
    text = template_path.read_text(encoding="utf-8")
    # {{ key|default("x") }}
    text = re.sub(
        r"\{\{\s*([a-z_]+)\s*\|\s*default\(\"([^\"]*)\"\)\s*\}\}",
        lambda m: str(context.get(m.group(1), m.group(2))),
        text,
    )
    # {{ key }}
    text = re.sub(
        r"\{\{\s*([a-z_]+)\s*\}\}",
        lambda m: str(context.get(m.group(1), f"<MISSING:{m.group(1)}>")),
        text,
    )
    return text


def build_context(sid: str, entry: dict) -> dict:
    """Extract registry fields the templates reference."""
    subseries = entry.get("subseries", {})
    first_sub_id, first_sub = (
        next(iter(subseries.items())) if subseries else (f"{sid}-A", {})
    )
    construction = entry.get("construction") or []
    validation = entry.get("validation") or {}
    benchmarks = validation.get("reference_values") or {}

    return {
        "sid": sid,
        "slug": slugify(entry.get("name", sid)),
        "name": entry.get("name", ""),
        "chapter": entry.get("chapter", ""),
        "units": entry.get("units", ""),
        "content_type": entry.get("content_type", ""),
        "source_file": entry.get("source_file", "") or first_sub.get("source", ""),
        "source_column": first_sub.get("source_column", ""),
        "first_subseries": first_sub_id,
        "unit_scale": entry.get("unit_scale", 1.0),
        "tolerance_class": validation.get("tolerance", "rate_series"),
        "benchmarks_dict": repr(benchmarks),
        "construction_summary": "; ".join(
            f"step{s.get('step','?')}: {s.get('op','?')}" for s in construction
        ) if construction else "(none)",
        "period_start": (entry.get("year_range") or [None, None])[0],
        "period_end":   (entry.get("year_range") or [None, None])[1],
    }


def scaffold_one(
    sid: str, entry: dict, template_name: str | None,
    project_root: Path, force: bool, dry_run: bool,
) -> list[str]:
    """Scaffold the L01/P02/V03 trio for one series. Returns list of written paths."""
    tmpl_name = template_name or select_template(entry)
    tmpl_dir = find_templates_dir(project_root)
    ctx = build_context(sid, entry)

    written = []
    for phase, subdir in (("L01", "L01_loaders"), ("P02", "P02_processors"), ("V03", "V03_validators")):
        tmpl = tmpl_dir / f"{phase}_{tmpl_name}.py.j2"
        if not tmpl.exists():
            print(f"  [{sid}] WARN: template missing: {tmpl}; skipping {phase}")
            continue
        # Derived templates may have no L01 (the registry's construction doesn't load)
        if phase == "L01" and tmpl_name == "derived":
            continue
        out_dir = project_root / "code" / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{phase}_{sid}_{ctx['slug']}.py"
        if out_path.exists() and not force:
            print(f"  [{sid}] EXISTS (skip; pass --force to overwrite): {out_path.name}")
            continue
        body = render(tmpl, ctx)
        if dry_run:
            print(f"  [{sid}] DRY-RUN would write: {out_path.name} ({len(body)} chars)")
            continue
        out_path.write_text(body, encoding="utf-8")
        written.append(str(out_path.relative_to(project_root)))
    return written


def filter_cohort(reg: dict, cohort: str) -> list[str]:
    """Pick series matching cohort name. Looks up registry.cohorts[<name>] first,
    then falls back to chapter or wave fields."""
    cohorts = reg.get("cohorts", {})
    if cohort in cohorts:
        return list(cohorts[cohort])
    out = []
    for sid, entry in reg.get("series", {}).items():
        if str(entry.get("wave", "")) == cohort or str(entry.get("chapter", "")) == cohort:
            out.append(sid)
    return out


def filter_pending(reg: dict) -> list[str]:
    out = []
    for sid, entry in reg.get("series", {}).items():
        status = entry.get("status", "")
        if status in ("loaded", "data_available", "data_unavailable"):
            out.append(sid)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="anu-scaffold — code stubs from registry")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--project", default=".", help="Project root (contains series_registry.json)")
    g.add_argument("--series", default=None, help="Single series ID")
    g.add_argument("--cohort", default=None, help="Cohort name (wave, chapter, or registry cohort)")
    g.add_argument("--all-pending", action="store_true")
    g.add_argument("--template", default=None,
                   choices=["auto", "direct_column", "derived", "matrix_summary"])
    g.add_argument("--force", action="store_true")
    g.add_argument("--dry-run", action="store_true")

    sub.add_parser("list-templates")

    args = p.parse_args()

    if args.cmd == "list-templates":
        tmpl_dir = DEFAULT_TEMPLATES
        if not tmpl_dir.exists():
            print(f"Templates dir missing: {tmpl_dir}")
            return 1
        for t in sorted(tmpl_dir.glob("*.py.j2")):
            print(f"  {t.name}")
        return 0

    project_root = Path(args.project).resolve()
    reg = load_registry(project_root)

    if args.series:
        series_list = [args.series]
    elif args.cohort:
        series_list = filter_cohort(reg, args.cohort)
        if not series_list:
            sys.exit(f"ERROR: no series found for cohort '{args.cohort}'")
    elif args.all_pending:
        series_list = filter_pending(reg)
    else:
        sys.exit("ERROR: specify --series, --cohort, or --all-pending")

    template = args.template if args.template and args.template != "auto" else None
    total_written = []
    for sid in series_list:
        entry = reg.get("series", {}).get(sid)
        if entry is None:
            print(f"  [{sid}] not in registry; skipping")
            continue
        written = scaffold_one(sid, entry, template, project_root, args.force, args.dry_run)
        total_written.extend(written)

    print()
    print(f"  anu-scaffold: {len(total_written)} files {'would be written' if args.dry_run else 'written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
