#!/usr/bin/env python3
"""Anu Build — Master orchestrator CLI for the Anu Framework v12.0.

Drives every Anu Framework skill through a methodical 9-stage pipeline
with computed construction order, mandatory gates, and a 4-file
documentation cascade.

Usage:
    python build.py init --project <path> --mode {fresh,rebuild,resume}
    python build.py plan
    python build.py status
    python build.py advance
    python build.py run-stage <N>
    python build.py run-to-completion
    python build.py audit
    python build.py handoff

Part of the Anu Framework v12.0 — see anu-build/SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
LIB_DIR = SKILL_DIR / "lib"
sys.path.insert(0, str(LIB_DIR))

from construction_graph import generate_plan
from cascade import (
    init_cascade,
    read_pipeline_state,
    read_ledger,
    advance_stage,
    append_step_log,
    append_narrative,
    regenerate_ledger,
)
from stage_runner import STAGE_MAP, check_gate, describe_stage, next_action


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_project(args_project: str | None) -> Path:
    if args_project:
        p = Path(args_project).resolve()
    else:
        p = Path.cwd()
    if (p / "series_registry.json").exists():
        return p
    if (p / "Technical" / "series_registry.json").exists():
        return p / "Technical"
    print(f"ERROR: Cannot find series_registry.json under {p}", file=sys.stderr)
    sys.exit(2)


def cmd_init(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    mode = args.mode
    print(f"Initializing anu-build in {mode} mode at {project}")

    registry_path = project / "series_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    series_count = len(registry.get("series", {}))
    project_name = registry.get("project", project.parent.name)

    init_cascade(project, project_name, mode)

    plan = generate_plan(registry_path)
    plan_path = project / "Build" / "SUBSERIES_PLAN.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest_path = project / "Build" / "ANU_BUILD_MANIFEST.json"
    manifest = json.loads(
        (SKILL_DIR / "templates" / "MANIFEST_TEMPLATE.json").read_text(encoding="utf-8")
    )
    manifest["project"] = project_name
    manifest["generated_at"] = now_iso()
    manifest["mode"] = mode
    manifest["series_count"] = series_count
    manifest["subseries_count"] = plan.get("subseries_count", 0)
    prefix_scheme = registry.get("prefix_scheme", {})
    if prefix_scheme:
        manifest["prefix_scheme"] = prefix_scheme
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    ledger = regenerate_ledger(project, registry_path)
    advance_stage(project, 0, "INVENTORY")

    append_step_log(project, {
        "ts": now_iso(), "step_id": "init-0001", "mode": mode,
        "stage": 0, "cohort": None, "series": None,
        "action": "init_cascade",
        "inputs": [str(registry_path)],
        "outputs": [str(plan_path), str(manifest_path)],
        "doctor_check_ids": [],
        "outcome": "pass",
        "artifacts_emitted": ["SUBSERIES_PLAN.json", "ANU_BUILD_MANIFEST.json"],
        "notes": f"Initialized {mode} build for {project_name} with {series_count} series",
    })

    append_narrative(project,
        f"## Stage 0 — Initialization\n\n"
        f"Initialized anu-build in **{mode}** mode for project **{project_name}**. "
        f"Registry contains **{series_count}** series and **{plan.get('subseries_count', 0)}** subseries. "
        f"Construction graph has **{len(plan.get('layers', []))}** topological layers "
        f"and **{len(plan.get('edges', []))}** dependency edges. "
        f"Cascade files created under `Technical/Build/`.\n",
        "init-0001")

    print(f"  project:    {project_name}")
    print(f"  series:     {series_count}")
    print(f"  subseries:  {plan.get('subseries_count', 0)}")
    print(f"  topo layers: {len(plan.get('layers', []))}")
    print(f"  edges:      {len(plan.get('edges', []))}")
    print(f"  mode:       {mode}")
    print(f"  cascade:    Technical/Build/")
    print("  INIT COMPLETE")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    plan_path = project / "Build" / "SUBSERIES_PLAN.json"
    if not plan_path.exists():
        print("ERROR: SUBSERIES_PLAN.json not found. Run `build.py init` first.", file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    print(f"Subseries Construction Plan — {plan.get('project', '?')}")
    print(f"  Series: {plan['series_count']}  Subseries: {plan['subseries_count']}")
    print(f"  Layers: {len(plan['layers'])}  Edges: {len(plan['edges'])}")
    print()
    for layer in plan["layers"]:
        print(f"  Layer {layer['layer']}: {', '.join(layer['subseries'][:10])}"
              + (f" ... (+{len(layer['subseries'])-10} more)" if len(layer["subseries"]) > 10 else ""))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    state = read_pipeline_state(project)
    ledger = read_ledger(project)

    current = state.get("current_stage", 0)
    print(f"Pipeline Status — {state.get('project', '?')}")
    print(f"  Current stage: {current} ({STAGE_MAP.get(current, ('?','?'))[0]})")
    print(f"  Last updated:  {state.get('last_updated', '?')}")
    print()

    for key in sorted(state.get("stages", {})):
        s = state["stages"][key]
        status = s.get("status", "?")
        label = s.get("label", "?")
        sc = s.get("series_complete", 0)
        st = s.get("series_total", 0)
        gate = "GATE PASSED" if s.get("gate_passed") else ""
        print(f"  {key} ({label}): {status}  [{sc}/{st}] {gate}")

    if ledger:
        print()
        print(f"  Ledger: {ledger.get('series_count', 0)} series")
        for k, v in ledger.get("coverage_pct", {}).items():
            print(f"    {k}: {v:.1f}%")
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    state = read_pipeline_state(project)
    ledger = read_ledger(project)
    current = state.get("current_stage", 0)

    plan_path = project / "Build" / "SUBSERIES_PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}

    action = next_action(project, current, ledger, plan)
    print(f"Next action at Stage {current} ({STAGE_MAP.get(current, ('?','?'))[0]}):")
    print(f"  Action:  {action.get('action', '?')}")
    print(f"  Series:  {action.get('series', 'N/A')}")
    print(f"  Skill:   {action.get('skill', '?')}")
    print(f"  Details: {action.get('details', '?')}")
    return 0


def cmd_run_stage(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    stage = args.stage_num
    if stage not in STAGE_MAP:
        print(f"ERROR: Unknown stage {stage}. Valid: 0-8", file=sys.stderr)
        return 2
    label, skill = STAGE_MAP[stage]
    print(f"Running Stage {stage} — {label} (skill: {skill})")
    print(describe_stage(stage))
    print()
    gate = check_gate(project, stage)
    if gate["passed"]:
        print(f"  Gate for Stage {stage} already PASSED")
    else:
        print(f"  Gate failures: {gate['failures']}")
        print(f"  Gate warnings: {gate['warnings']}")
    return 0 if gate["passed"] else 1


def cmd_audit(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    print(f"Auditing project at {project}")
    state = read_pipeline_state(project)
    current = state.get("current_stage", 0)
    for stage in range(current + 1):
        gate = check_gate(project, stage)
        label = STAGE_MAP.get(stage, ("?", "?"))[0]
        status = "PASS" if gate["passed"] else "FAIL"
        print(f"  Stage {stage} ({label}): {status}")
        for f in gate.get("failures", []):
            print(f"    FAIL: {f}")
        for w in gate.get("warnings", []):
            print(f"    WARN: {w}")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    project = find_project(args.project)
    state = read_pipeline_state(project)
    ts = now_iso()
    ts_file = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    handoffs_dir = project / "Handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)
    handoff_path = handoffs_dir / f"HANDOFF_{ts_file}.md"

    current = state.get("current_stage", 0)
    label = STAGE_MAP.get(current, ("?", "?"))[0]

    handoff_path.write_text(
        f"# Handoff — {state.get('project', '?')}\n\n"
        f"**Date**: {ts}\n"
        f"**Current Stage**: {current} ({label})\n"
        f"**Framework**: Anu Framework v12.0\n\n"
        f"## Status\n\nSee `Technical/Build/BUILD_NARRATIVE.md` for recent work.\n"
        f"See `Technical/PIPELINE_STATE.json` for stage progress.\n"
        f"See `Technical/ANU_LEDGER.json` for per-series state.\n\n"
        f"## Next Steps\n\nRun `/anu-build status` to see current progress.\n"
        f"Run `/anu-build advance` to see the next action.\n",
        encoding="utf-8",
    )

    append_step_log(project, {
        "ts": ts, "step_id": f"handoff-{ts_file}", "mode": "handoff",
        "stage": current, "cohort": None, "series": None,
        "action": "handoff",
        "inputs": [], "outputs": [str(handoff_path)],
        "doctor_check_ids": [], "outcome": "pass",
        "artifacts_emitted": [f"Handoffs/HANDOFF_{ts_file}.md"],
        "notes": f"Session handoff at Stage {current} ({label})",
    })
    append_narrative(project,
        f"## Handoff — {ts}\n\nSession ended at Stage {current} ({label}). "
        f"Handoff written to `{handoff_path.name}`. "
        f"Next agent: run `/anu-build status` then `/anu-build advance`.\n",
        f"handoff-{ts_file}")

    print(f"  Handoff written: {handoff_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Anu Build — Master orchestrator for Anu Framework v12.0")
    parser.add_argument("--project", type=str, default=None,
                        help="Project root (default: cwd)")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize or resume a build")
    p_init.add_argument("--mode", choices=["fresh", "rebuild", "resume"],
                        default="resume")

    sub.add_parser("plan", help="Print SUBSERIES_PLAN topo order")
    sub.add_parser("status", help="Print stage/cohort/series progress")
    sub.add_parser("advance", help="Show the next action to take")

    p_stage = sub.add_parser("run-stage", help="Run all steps in a stage")
    p_stage.add_argument("stage_num", type=int)

    sub.add_parser("run-to-completion", help="Run all remaining stages")
    sub.add_parser("audit", help="Read-only conformance check")
    sub.add_parser("handoff", help="Close session, write handoff doc")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "plan": cmd_plan,
        "status": cmd_status,
        "advance": cmd_advance,
        "run-stage": cmd_run_stage,
        "audit": cmd_audit,
        "handoff": cmd_handoff,
    }

    if not args.command:
        parser.print_help()
        return 0

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
