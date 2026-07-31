#!/usr/bin/env python3
"""Generate docs/schemas/skill_graph.json from the shipped SKILL.md frontmatter.

The graph is derived, never authored: every node and every edge is read
out of a real `skills/anu-*/SKILL.md` frontmatter block at generation
time. If a skill is added, removed, or its `requires:` changes, re-run
this script — do not hand-edit the JSON.

    python tools/generate_skill_graph.py           # write the file
    python tools/generate_skill_graph.py --check    # exit 1 if stale

Stdlib only. Part of the Anu Framework v12.2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
OUT_PATH = REPO_ROOT / "docs" / "schemas" / "skill_graph.json"

# Stage assignment is owned by anu-build's canonical stage sequence
# (skills/anu-build/SKILL.md, "Canonical Stage Sequence"). Kept here so the
# generated graph can be sorted by pipeline position; anu-doctor D19 checks
# each SKILL.md against the same table.
CANONICAL_STAGES = {
    "anu-research": "Stage 1",
    "anu-adequacy": "Stage 2",
    "anu-ingestion": "Stage 3",
    "anu-extension": "Stage 4",
    "anu-scaffold": "Stage 5",
    "anu-replicator": "Stage 5",
    "anu-chopped": "Stage 6",
    "anu-extenbook": "Stage 6",
    "anu-visualize": "Stage 7",
    "anu-publish": "Stage 8",
    "anu-drive": "Stage 8",
    "anu-archive": "Stage 8",
    "anu-review": "Floating",
    "anu-docs": "Floating",
    "anu-variant": "Floating",
    "anu-ledger": "Infrastructure",
    "anu-architecture": "Infrastructure",
    "anu-doctor": "Infrastructure",
    "anu-build": "Orchestrator",
}

# The two skills superseded by anu-build in v12.0. Still shipped in full;
# marked so consumers of the graph can exclude them from "current pipeline".
SUPERSEDED = {"anu-pipeline": "anu-build", "anu-rebuild": "anu-build"}


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict = {}
    for line in text[3:end].splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        if key in ("name", "version", "part-of", "requires"):
            fm[key] = val.strip().strip('"').strip("'")
    return fm


def framework_version() -> str:
    overview = REPO_ROOT / "docs" / "ANU_FRAMEWORK_OVERVIEW.md"
    m = re.search(r"# Anu Framework (v[0-9]+\.[0-9]+)",
                  overview.read_text(encoding="utf-8"))
    return m.group(1) if m else "unknown"


def build() -> dict:
    skills: dict[str, dict] = {}
    edges: list[dict] = []

    for d in sorted(SKILLS_DIR.glob("anu-*")):
        if not d.is_dir() or not (d / "SKILL.md").exists():
            continue
        fm = parse_frontmatter(d / "SKILL.md")
        raw_requires = fm.get("requires", "none")
        requires = ([] if raw_requires in ("none", "", "None")
                    else [r.strip() for r in raw_requires.split(",") if r.strip()])
        node = {
            "version": fm.get("version", ""),
            "stage": CANONICAL_STAGES.get(d.name, "Superseded"),
            "requires": requires,
            "status": "superseded" if d.name in SUPERSEDED else "current",
        }
        if d.name in SUPERSEDED:
            node["superseded_by"] = SUPERSEDED[d.name]
        skills[d.name] = node
        for dep in requires:
            edges.append({"from": dep, "to": d.name})

    dangling = sorted({e["from"] for e in edges} - set(skills))

    return {
        "schema": "anu_skill_graph/1.0",
        "framework": f"Anu Framework {framework_version()}",
        "generated_by": "tools/generate_skill_graph.py",
        "source": "the `requires:` frontmatter of each skills/anu-*/SKILL.md",
        "note": ("Derived artifact — do not hand-edit. Re-run the generator after "
                 "any frontmatter change. An edge from A to B means B declares "
                 "`requires: A`, i.e. A must be satisfied before B runs."),
        "skill_count": len(skills),
        "edge_count": len(edges),
        "dangling_requires": dangling,
        "skills": skills,
        "edges": sorted(edges, key=lambda e: (e["to"], e["from"])),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed file differs from the generated one")
    args = ap.parse_args()

    graph = build()
    payload = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not OUT_PATH.exists():
            print(f"MISSING: {OUT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        current = OUT_PATH.read_text(encoding="utf-8")
        # generated_by/source/note are stable; only the data may drift.
        a = json.loads(current)
        b = json.loads(payload)
        for key in ("skills", "edges", "skill_count", "edge_count", "dangling_requires"):
            if a.get(key) != b.get(key):
                print(f"STALE: skill_graph.json differs from frontmatter in '{key}'. "
                      "Re-run tools/generate_skill_graph.py", file=sys.stderr)
                return 1
        print("skill_graph.json is current.")
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} "
          f"({graph['skill_count']} skills, {graph['edge_count']} edges)")
    if graph["dangling_requires"]:
        print(f"  WARNING: requires names no shipped skill: {graph['dangling_requires']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
