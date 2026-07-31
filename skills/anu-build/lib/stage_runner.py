#!/usr/bin/env python3
"""Stage map, acceptance gates, and next-action selection for anu-build.

Scope, stated plainly: `anu-build` is an orchestration *state machine*, not
a task runner. It computes the construction order, maintains the
documentation cascade, evaluates each stage's acceptance gate, and names
the next concrete action. The stage work itself — reading a source,
writing a loader, extending a series — is performed by an agent invoking
the individual skills. Nothing in this module executes another skill.

Every gate below is an **artifact-presence** check, plus a numeric read
where the project genuinely records a number (adequacy scores). A gate
passing means the required files exist; it does not mean their contents
are correct. Content correctness is `anu-doctor` project mode (P01-P39)
and `anu-review`.

Stdlib only. Part of the Anu Framework v12.2 — see anu-build/SKILL.md.
"""
from __future__ import annotations

import json
from pathlib import Path

from cascade import ARTIFACT_PATTERNS, TRIAD_PATTERNS, read_ledger  # noqa: F401

# stage number -> (label, owning skill)
STAGE_MAP: dict[int, tuple[str, str]] = {
    0: ("INVENTORY", "anu-build"),
    1: ("RESEARCH", "anu-research"),
    2: ("ADEQUACY", "anu-adequacy"),
    3: ("INGESTION", "anu-ingestion"),
    4: ("EXTENSION", "anu-extension"),
    5: ("REPLICATION", "anu-scaffold + anu-replicator"),
    6: ("OUTPUT", "anu-chopped + anu-extenbook"),
    7: ("VISUALIZATION", "anu-visualize"),
    8: ("DISTRIBUTION", "anu-publish + anu-drive + anu-archive"),
}

STAGE_DESCRIPTIONS: dict[int, str] = {
    0: ("Detect mode, salvage any predecessor material, finalize the registry "
        "enough to compute the graph, topologically sort it, and write the "
        "manifest and subseries plan."),
    1: "Mine the Knowledge Base for every series: quotes, footnotes, methodology.",
    2: "Score research adequacy across six layers. Gate: score >= 80 to advance.",
    3: "Finalize series_registry.json; write a DPR per series and decompositions.",
    4: "Define and document extension methodology; write EPRs and the divergence register.",
    5: ("Construct every subseries in topological order: L01 load, P02 derive/splice, "
        "V03 validate. V03 must PASS before the node is complete."),
    6: "Emit machine-readable Anu Chopped CSVs and human-readable Anu Extenbook workbooks.",
    7: "Build the interactive app and confirm every published series is visible.",
    8: ("Produce the three sibling distribution channels: GitHub replication package, "
        "Drive consumer package, audit-grade archive."),
}


def describe_stage(stage: int) -> str:
    label, skill = STAGE_MAP.get(stage, ("UNKNOWN", "?"))
    body = STAGE_DESCRIPTIONS.get(stage, "No description recorded for this stage.")
    return f"  {label} (skill: {skill})\n  {body}"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _registry(project: Path) -> dict:
    path = Path(project) / "series_registry.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _series_ids(project: Path) -> list[str]:
    return sorted((_registry(project).get("series") or {}).keys())


def _extending_series(project: Path) -> list[str]:
    out = []
    for sid, sdef in (_registry(project).get("series") or {}).items():
        if sdef.get("extension"):
            out.append(sid)
    return sorted(out)


def _missing(project: Path, sids: list[str], key: str) -> list[str]:
    """Series ids whose ledger artifact `key` is absent, recomputed from disk."""
    ledger = read_ledger(project).get("series") or {}
    return [sid for sid in sids if not (ledger.get(sid) or {}).get(key)]


def _glob_any(project: Path, subdir: str, pattern: str) -> bool:
    directory = Path(project) / subdir
    return directory.is_dir() and any(directory.glob(pattern))


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

def check_gate(project: Path, stage: int) -> dict:
    """Evaluate the acceptance gate for `stage`.

    Returns {"passed": bool, "failures": [str], "warnings": [str]}.
    """
    project = Path(project)
    failures: list[str] = []
    warnings: list[str] = []
    sids = _series_ids(project)

    if stage == 0:
        if not (project / "series_registry.json").exists():
            failures.append("series_registry.json not found")
        for name in ("ANU_BUILD_MANIFEST.json", "SUBSERIES_PLAN.json"):
            if not (project / "Build" / name).exists():
                failures.append(f"Build/{name} not written")
        plan_path = project / "Build" / "SUBSERIES_PLAN.json"
        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                failures.append("Build/SUBSERIES_PLAN.json does not parse")
            else:
                if plan.get("cycle_nodes"):
                    failures.append(
                        f"construction graph has a cycle: {plan['cycle_nodes'][:5]}")
                if plan.get("unresolved_edges"):
                    warnings.append(
                        f"{len(plan['unresolved_edges'])} dependency reference(s) "
                        "name an id not in the registry")

    elif stage == 1:
        missing = _missing(project, sids, "research")
        if missing:
            failures.append(f"{len(missing)} series without research JSON: {missing[:5]}")

    elif stage == 2:
        reports = sorted((project / "docs" / "chapters").glob("*ADEQUACY_REPORT.json")) \
            if (project / "docs" / "chapters").is_dir() else []
        if not reports:
            failures.append("no *_ADEQUACY_REPORT.json under docs/chapters/")
        for report in reports:
            try:
                data = json.loads(report.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                failures.append(f"{report.name} does not parse")
                continue
            score = data.get("total_score", data.get("score"))
            if score is None:
                warnings.append(f"{report.name} records no total_score")
            elif isinstance(score, (int, float)) and score < 80:
                failures.append(f"{report.name} scores {score} (gate is >= 80)")

    elif stage == 3:
        missing = _missing(project, sids, "dpr")
        if missing:
            failures.append(f"{len(missing)} series without a DPR: {missing[:5]}")

    elif stage == 4:
        extending = _extending_series(project)
        missing = _missing(project, extending, "epr")
        if missing:
            failures.append(f"{len(missing)} extending series without an EPR: {missing[:5]}")
        if not (project / "docs" / "DIVERGENCE_REGISTER.json").exists():
            warnings.append("docs/DIVERGENCE_REGISTER.json not present")
        if not extending:
            warnings.append("no series declares an extension — stage 4 is vacuous here")

    elif stage == 5:
        ledger = read_ledger(project).get("series") or {}
        incomplete = [sid for sid in sids if not (ledger.get(sid) or {}).get("triad_complete")]
        if incomplete:
            failures.append(
                f"{len(incomplete)} series without a complete L01/P02/V03 triad: {incomplete[:5]}")

    elif stage == 6:
        missing = _missing(project, sids, "chopped")
        if missing:
            failures.append(f"{len(missing)} series without a chopped CSV: {missing[:5]}")
        # Extenbook naming is not uniform across projects, so match on the
        # series id anywhere in the filename rather than assuming one scheme.
        no_book = [sid for sid in sids
                   if not _glob_any(project, "extenbooks", f"*{sid}*.xlsx")]
        if no_book:
            warnings.append(
                f"{len(no_book)} series without an extenbooks/*{{sid}}*.xlsx workbook: {no_book[:5]}")

    elif stage == 7:
        has_app = (_glob_any(project, "viz/dash", "app.py")
                   or _glob_any(project, "viz/shiny", "app.R"))
        if not has_app:
            failures.append("no viz/dash/app.py or viz/shiny/app.R found")

    elif stage == 8:
        for channel in ("Publish", "Drive", "Archive"):
            if not (project.parent / "Outputs" / channel).is_dir() \
                    and not (project / "Outputs" / channel).is_dir():
                warnings.append(f"Outputs/{channel}/ not present")

    else:
        failures.append(f"unknown stage {stage}")

    return {"passed": not failures, "failures": failures, "warnings": warnings}


# --------------------------------------------------------------------------
# Next action
# --------------------------------------------------------------------------

def next_action(project: Path, stage: int, ledger: dict, plan: dict) -> dict:
    """Name the next concrete action at `stage`. Never executes anything."""
    project = Path(project)
    label, skill = STAGE_MAP.get(stage, ("UNKNOWN", "?"))
    gate = check_gate(project, stage)
    entries = (ledger or {}).get("series") or {}
    sids = sorted(entries) or _series_ids(project)

    def first_missing(key: str, candidates: list[str] | None = None) -> str | None:
        for sid in (candidates if candidates is not None else sids):
            if not (entries.get(sid) or {}).get(key):
                return sid
        return None

    if gate["passed"] and stage < max(STAGE_MAP):
        nxt = stage + 1
        return {
            "action": "advance_stage",
            "series": None,
            "skill": STAGE_MAP[nxt][1],
            "details": (f"Stage {stage} ({label}) gate passes. Advance to Stage "
                        f"{nxt} ({STAGE_MAP[nxt][0]})."),
        }

    per_stage_key = {1: "research", 3: "dpr", 5: "triad_complete", 6: "chopped"}
    if stage in per_stage_key:
        candidates = None
        sid = first_missing(per_stage_key[stage], candidates)
        if sid:
            return {
                "action": f"produce_{per_stage_key[stage]}",
                "series": sid,
                "skill": skill,
                "details": (f"{sid} is the first series in registry order missing its "
                            f"{per_stage_key[stage]} artifact. Invoke {skill} for it."),
            }

    if stage == 4:
        sid = first_missing("epr", _extending_series(project))
        if sid:
            return {"action": "produce_epr", "series": sid, "skill": skill,
                    "details": f"{sid} declares an extension but has no EPR."}

    if stage == 5 and plan:
        for layer in plan.get("layers", []):
            for node in layer["subseries"]:
                base = node.split("-")[0]
                if not (entries.get(base) or {}).get("triad_complete"):
                    return {
                        "action": "construct_node",
                        "series": node,
                        "skill": skill,
                        "details": (f"Layer {layer['layer']} node {node} is the earliest "
                                    "incomplete node in topological order."),
                    }

    return {
        "action": "resolve_gate_failures",
        "series": None,
        "skill": skill,
        "details": ("; ".join(gate["failures"]) if gate["failures"]
                    else f"Stage {stage} ({label}) gate passes; this is the final stage."),
    }
