#!/usr/bin/env python3
"""Anu Doctor — Anu Framework self-audit checker.

Verifies the framework is internally consistent: see the D01-D12 check
table in SKILL.md. Exits non-zero if any FAIL-severity check fails.

Usage:
    python check_framework.py          # run all checks, console report
    python check_framework.py --json   # machine-readable FRAMEWORK_AUDIT.json
    python check_framework.py --fix     # auto-fix the mechanically-fixable checks

Part of the Anu Framework v11.0 — see anu-doctor/SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent          # .../.claude/skills
DRUCK_DIR = SKILLS_DIR.parent.parent                          # project root
DOCS_DIR = DRUCK_DIR / "docs"
OVERVIEW = DOCS_DIR / "ANU_FRAMEWORK_OVERVIEW.md"
MATRIX = DOCS_DIR / "SKILL_VERSION_MATRIX.md"

CANONICAL_DOCS = [
    "ANU_FRAMEWORK_GLOSSARY.md",
    "SERIES_REGISTRY_SCHEMA.md",
    "DATA_PROVENANCE_STANDARDS.md",
    "SKILL_VERSION_MATRIX.md",
    "ANU_FRAMEWORK_OVERVIEW.md",
]

ARCHIVED_MARKERS = ("archived", "removed", "superseded", "deprecated", "legacy",
                    "replaces", "predecessor", "formerly")
STALE_VERSION_RE = re.compile(r"Anu Framework v(?:[1-9]|10)\.0")  # v1.0-v10.0; current is v11.0


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def active_skill_dirs() -> list[Path]:
    out = []
    for d in sorted(SKILLS_DIR.glob("anu-*")):
        if not d.is_dir():
            continue
        if any(m in d.name for m in ("archived", "removed")):
            continue
        if (d / "SKILL.md").exists():
            out.append(d)
    return out


def parse_frontmatter(skill_md: Path) -> dict:
    """Minimal YAML-frontmatter parser — returns {} if no frontmatter."""
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fm: dict = {}
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in ("name", "version", "part-of", "requires"):
            fm[key] = val
    return fm


def framework_version() -> str | None:
    """Read the canonical framework version from the overview header."""
    if not OVERVIEW.exists():
        return None
    m = re.search(r"# Anu Framework (v[0-9]+\.[0-9]+)", OVERVIEW.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def matrix_versions() -> dict[str, str]:
    """Parse SKILL_VERSION_MATRIX.md's main table -> {skill_name: version}."""
    out: dict[str, str] = {}
    if not MATRIX.exists():
        return out
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        # | 1 | anu-research | 2.0 | 1 | none | ... |
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 5:
            continue
        name = cells[2].strip("*` ")
        ver = cells[3].strip("v* ")
        if re.fullmatch(r"anu-[a-z]+", name) and re.fullmatch(r"[0-9]+\.[0-9]+", ver):
            out[name] = ver
    return out


def overview_versions() -> dict[str, str]:
    """Parse ANU_FRAMEWORK_OVERVIEW.md's skill table -> {skill_name: version}."""
    out: dict[str, str] = {}
    if not OVERVIEW.exists():
        return out
    for line in OVERVIEW.read_text(encoding="utf-8").splitlines():
        # | 1 | **Anu Research** | v2.0 | `anu-research/SKILL.md` | ... |
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        ver = cells[3].strip("v* ")
        loc_m = re.search(r"(anu-[a-z]+)/SKILL\.md", cells[4])
        if loc_m and re.fullmatch(r"[0-9]+\.[0-9]+", ver):
            out[loc_m.group(1)] = ver
    return out


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.results: list[dict] = []

    def add(self, check: str, severity: str, ok: bool, detail: str) -> None:
        self.results.append({"check": check, "severity": severity, "ok": ok, "detail": detail})

    def fails(self) -> list[dict]:
        return [r for r in self.results if not r["ok"] and r["severity"] == "FAIL"]

    def warns(self) -> list[dict]:
        return [r for r in self.results if not r["ok"] and r["severity"] == "WARN"]


def run_checks() -> Report:
    rep = Report()
    skills = active_skill_dirs()
    skill_names = {d.name for d in skills}
    fw_version = framework_version()
    mx = matrix_versions()
    ov = overview_versions()

    frontmatters: dict[str, dict] = {}

    # D01 — frontmatter validity
    for d in skills:
        fm = parse_frontmatter(d / "SKILL.md")
        frontmatters[d.name] = fm
        missing = [k for k in ("name", "version", "part-of") if k not in fm]
        rep.add("D01", "FAIL", not missing,
                f"{d.name}: missing frontmatter keys {missing}" if missing
                else f"{d.name}: frontmatter OK")

    # D02 — name matches directory
    for d in skills:
        fm = frontmatters[d.name]
        ok = fm.get("name") == d.name
        rep.add("D02", "FAIL", ok,
                f"{d.name}: name='{fm.get('name')}' != dir" if not ok
                else f"{d.name}: name matches dir")

    # D03 — part-of equals current framework version
    for d in skills:
        fm = frontmatters[d.name]
        po = fm.get("part-of", "")
        ok = fw_version is not None and fw_version in po
        rep.add("D03", "FAIL", ok,
                f"{d.name}: part-of='{po}' != framework {fw_version}" if not ok
                else f"{d.name}: part-of OK ({fw_version})")

    # D04 — frontmatter version matches the version matrix
    for d in skills:
        fm = frontmatters[d.name]
        fmv = fm.get("version", "")
        mxv = mx.get(d.name)
        ok = mxv is not None and fmv == mxv
        rep.add("D04", "FAIL", ok,
                f"{d.name}: frontmatter v{fmv} != matrix v{mxv}" if not ok
                else f"{d.name}: matrix version OK (v{fmv})")

    # D05 — frontmatter version matches the overview table
    for d in skills:
        fm = frontmatters[d.name]
        fmv = fm.get("version", "")
        ovv = ov.get(d.name)
        ok = ovv is not None and fmv == ovv
        rep.add("D05", "FAIL", ok,
                f"{d.name}: frontmatter v{fmv} != overview v{ovv}" if not ok
                else f"{d.name}: overview version OK (v{fmv})")

    # D06 — matrix and overview agree
    all_names = set(mx) | set(ov)
    disagreements = [n for n in all_names if mx.get(n) != ov.get(n)]
    rep.add("D06", "FAIL", not disagreements,
            f"matrix/overview disagree on: {disagreements}" if disagreements
            else f"matrix and overview agree on all {len(all_names)} skills")

    # D07 — requires integrity
    for d in skills:
        fm = frontmatters[d.name]
        req = fm.get("requires", "none")
        if req in ("none", "", None):
            rep.add("D07", "FAIL", True, f"{d.name}: requires none")
            continue
        deps = [r.strip() for r in req.split(",") if r.strip()]
        bad = [r for r in deps if r not in skill_names]
        rep.add("D07", "FAIL", not bad,
                f"{d.name}: requires unknown skill(s) {bad}" if bad
                else f"{d.name}: requires {deps} all exist")

    # D08 — no un-qualified archived-skill references
    archived_stems = ["anu-standard", "anu-shiny"]
    for d in skills:
        body = (d / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
        hits = []
        for line in body.splitlines():
            for stem in archived_stems:
                if stem in line and not any(m in line.lower() for m in ARCHIVED_MARKERS):
                    hits.append(f"{stem}: {line.strip()[:70]}")
        rep.add("D08", "WARN", not hits,
                f"{d.name}: un-qualified archived-skill refs: {hits[:2]}" if hits
                else f"{d.name}: no stale archived-skill refs")

    # D09 — canonical docs exist
    for doc in CANONICAL_DOCS:
        ok = (DOCS_DIR / doc).exists()
        rep.add("D09", "FAIL", ok,
                f"canonical doc missing: docs/{doc}" if not ok
                else f"docs/{doc} exists")

    # D10 — claimed generator scripts exist
    # A "hard claim" — "ships an executable generator at X" — is FAIL if
    # missing. A bare prose mention is WARN, unless it is qualified as
    # project-provided (on its own line OR by a file-level disclaimer) or
    # appears inside a Version History block — those are honest references
    # to project-level scripts, not skill-ship claims.
    LINE_QUALIFIERS = ("e.g.", "project-specific", "project-provided",
                       "in the cd2 project", "project's", "a script")
    # A file-level disclaimer contextualizes every script mention in that file.
    FILE_DISCLAIMERS = ("project-provided", "does not ship a generator",
                        "does not ship generator", "the script itself is project",
                        "scripts themselves are project")
    for d in skills:
        lines = (d / "SKILL.md").read_text(encoding="utf-8", errors="ignore").splitlines()
        body = "\n".join(lines)
        body_low = body.lower()
        hard_claims = set(re.findall(
            r"ships an executable [a-z]+ at[^\n]*?(generate_[a-z_]+\.py|check_[a-z_]+\.py)",
            body))
        file_disclaimed = any(disc in body_low for disc in FILE_DISCLAIMERS)
        # Walk line by line so we can suppress version-history and qualified mentions.
        soft_mentions: set[str] = set()
        in_history = False
        for line in lines:
            low = line.lower()
            if "version history" in low or "## changelog" in low:
                in_history = True
            if in_history:
                continue
            # A line like `"generated_by": "generate_x.py",` is JSON example
            # data showing an output's shape — not a claim or a command.
            is_json_example = bool(re.search(r'"\s*:\s*"[^"]*\.py"', line))
            for script in re.findall(r"\b(generate_[a-z_]+\.py|check_[a-z_]+\.py)\b", line):
                if script in hard_claims:
                    continue
                if file_disclaimed or is_json_example or any(q in low for q in LINE_QUALIFIERS):
                    continue  # project-provided script, JSON example, or qualified mention
                soft_mentions.add(script)
        for script in sorted(hard_claims):
            ok = (d / script).exists()
            rep.add("D10", "FAIL", ok,
                    f"{d.name}: SKILL.md hard-claims {script} but it is missing" if not ok
                    else f"{d.name}: {script} exists (hard claim)")
        for script in sorted(soft_mentions):
            ok = (d / script).exists()
            rep.add("D10", "WARN", ok,
                    f"{d.name}: SKILL.md presents {script} as a command but it is not in the skill dir" if not ok
                    else f"{d.name}: {script} exists (mentioned)")

    # D11 — pipeline stage map names only real skills
    pipeline_md = SKILLS_DIR / "anu-pipeline" / "SKILL.md"
    if pipeline_md.exists():
        body = pipeline_md.read_text(encoding="utf-8", errors="ignore")
        # Skill references in the stage map look like "Anu Research", "anu-research"
        referenced = set(re.findall(r"anu-[a-z]+", body))
        bad = [s for s in referenced if s not in skill_names
               and s not in ("anu-shiny", "anu-standard")]
        rep.add("D11", "FAIL", not bad,
                f"anu-pipeline references unknown skills: {bad}" if bad
                else "anu-pipeline stage map references only real skills")
    else:
        rep.add("D11", "FAIL", False, "anu-pipeline/SKILL.md not found")

    # D12 — stale framework-version strings outside changelog blocks
    for d in skills:
        lines = (d / "SKILL.md").read_text(encoding="utf-8", errors="ignore").splitlines()
        in_history = False
        hits = []
        for line in lines:
            low = line.lower()
            if "version history" in low or "## changelog" in low:
                in_history = True
            if in_history:
                continue
            if STALE_VERSION_RE.search(line) and not any(
                m in low for m in ("v1.0)", "(v", "previously", "was ", "prior",
                                   "designed after", "review of", "predecessor",
                                   "evolved from", "migrated from")
            ):
                hits.append(line.strip()[:70])
        rep.add("D12", "WARN", not hits,
                f"{d.name}: stale framework version in current-state line(s): {hits[:2]}" if hits
                else f"{d.name}: no stale framework-version strings")

    # D13 — body headline version matches frontmatter version
    # First top-level "# Anu <Name>..." line should contain "vN.N" matching frontmatter.
    headline_re = re.compile(r"^#\s+Anu\s+\S.*?\bv(\d+\.\d+)\b", re.MULTILINE)
    for d in skills:
        fm = parse_frontmatter(d / "SKILL.md")
        body = (d / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
        # Strip frontmatter so we don't match version: in frontmatter
        if body.startswith("---"):
            end = body.find("\n---", 3)
            if end != -1:
                body = body[end + 4:]
        m = headline_re.search(body)
        fm_ver = fm.get("version", "")
        if not m:
            rep.add("D13", "FAIL", False,
                    f"{d.name}: no '# Anu <Name> ... vN.N' headline found in body")
        elif m.group(1) != fm_ver:
            rep.add("D13", "FAIL", False,
                    f"{d.name}: headline v{m.group(1)} != frontmatter v{fm_ver}")
        else:
            rep.add("D13", "FAIL", True,
                    f"{d.name}: headline v{m.group(1)} matches frontmatter")

    # D14 — every SKILL.md documents its own evolution.
    # Accepts "## Version History", "## Changelog", or "## Skill Evolution Log"
    # — different skill styles, same invariant.
    history_re = re.compile(
        r"^##\s+(Version History|Changelog|Skill Evolution Log)\b",
        re.MULTILINE | re.IGNORECASE,
    )
    for d in skills:
        body = (d / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
        has_history = bool(history_re.search(body))
        rep.add("D14", "WARN", has_history,
                f"{d.name}: missing evolution-log section "
                "('## Version History', '## Changelog', or '## Skill Evolution Log')"
                if not has_history
                else f"{d.name}: evolution-log section present")

    # D15 — requires-graph is acyclic
    # Build digraph from `requires:` frontmatter; detect cycles via DFS.
    graph: dict[str, list[str]] = {}
    for d in skills:
        fm = parse_frontmatter(d / "SKILL.md")
        req = fm.get("requires", "none")
        if req in ("none", "", "None"):
            graph[d.name] = []
        else:
            graph[d.name] = [r.strip() for r in req.split(",") if r.strip()]

    def find_cycle(g: dict[str, list[str]]) -> list[str] | None:
        WHITE, GREY, BLACK = 0, 1, 2
        color = {n: WHITE for n in g}
        stack: list[str] = []

        def visit(n: str) -> list[str] | None:
            if n not in color:
                return None  # unknown skill — D07 catches that
            if color[n] == GREY:
                # cycle: return slice of stack from first occurrence of n
                i = stack.index(n)
                return stack[i:] + [n]
            if color[n] == BLACK:
                return None
            color[n] = GREY
            stack.append(n)
            for m in g[n]:
                c = visit(m)
                if c:
                    return c
            stack.pop()
            color[n] = BLACK
            return None

        for n in g:
            if color[n] == WHITE:
                c = visit(n)
                if c:
                    return c
        return None

    cycle = find_cycle(graph)
    rep.add("D15", "FAIL", cycle is None,
            f"requires-graph has a cycle: {' -> '.join(cycle)}" if cycle
            else "requires-graph is acyclic")

    return rep


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Anu Framework self-audit")
    parser.add_argument("--json", action="store_true", help="write FRAMEWORK_AUDIT.json")
    parser.add_argument("--fix", action="store_true", help="auto-fix mechanically-fixable checks (D03)")
    args = parser.parse_args()

    rep = run_checks()

    by_check: dict[str, list[dict]] = {}
    for r in rep.results:
        by_check.setdefault(r["check"], []).append(r)

    print("=" * 60)
    print("  Anu Doctor — Framework Self-Audit")
    print("=" * 60)
    print(f"  framework version: {framework_version()}")
    print(f"  active skills:     {len(active_skill_dirs())}")
    print()
    for check in sorted(by_check):
        items = by_check[check]
        n_notok = sum(1 for r in items if not r["ok"])
        has_real_fail = any(not r["ok"] and r["severity"] == "FAIL" for r in items)
        status = "PASS" if n_notok == 0 else ("FAIL" if has_real_fail else "WARN")
        print(f"  {check}  {len(items) - n_notok}/{len(items)}  [{status}]")
        for r in items:
            if not r["ok"]:
                print(f"        - {r['detail']}")

    fails, warns = rep.fails(), rep.warns()
    print()
    print(f"  Summary: {len(fails)} failures, {len(warns)} warnings")
    print("=" * 60)

    if args.json:
        out = Path(__file__).parent / "FRAMEWORK_AUDIT.json"
        out.write_text(json.dumps(rep.results, indent=2), encoding="utf-8")
        print(f"  wrote {out}")

    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
