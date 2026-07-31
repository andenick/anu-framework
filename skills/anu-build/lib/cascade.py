#!/usr/bin/env python3
"""Documentation cascade — the four append/regenerate files anu-build owns.

Writes and reads:

  <project>/PIPELINE_STATE.json        stage-level orchestration state
  <project>/ANU_LEDGER.json            per-series artifact inventory
  <project>/Build/STEP_LOG.jsonl       append-only event stream
  <project>/Build/BUILD_NARRATIVE.md   append-only human/LLM narrative

The ledger is *regenerated*, never patched in place: every field is
derived from the registry plus what is actually on disk, so it cannot
drift from reality. Artifact detection is filesystem presence only — this
module never inspects the contents of a loader, validator, or CSV, and
never infers that a step "probably" ran.

Stdlib only. Part of the Anu Framework v12.2 — see anu-build/SKILL.md.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

FRAMEWORK_VERSION = "v12.2"

STAGE_LABELS = {
    0: "INVENTORY",
    1: "RESEARCH",
    2: "ADEQUACY",
    3: "INGESTION",
    4: "EXTENSION",
    5: "REPLICATION",
    6: "OUTPUT",
    7: "VISUALIZATION",
    8: "DISTRIBUTION",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def build_dir(project: Path) -> Path:
    return Path(project) / "Build"


def pipeline_state_path(project: Path) -> Path:
    return Path(project) / "PIPELINE_STATE.json"


def ledger_path(project: Path) -> Path:
    return Path(project) / "ANU_LEDGER.json"


def step_log_path(project: Path) -> Path:
    return build_dir(project) / "STEP_LOG.jsonl"


def narrative_path(project: Path) -> Path:
    return build_dir(project) / "BUILD_NARRATIVE.md"


# --------------------------------------------------------------------------
# Read
# --------------------------------------------------------------------------

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def read_pipeline_state(project: Path) -> dict:
    return _read_json(pipeline_state_path(project))


def read_ledger(project: Path) -> dict:
    return _read_json(ledger_path(project))


def read_step_log(project: Path) -> list[dict]:
    path = step_log_path(project)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# --------------------------------------------------------------------------
# Write
# --------------------------------------------------------------------------

def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def init_cascade(project: Path, project_name: str, mode: str) -> dict:
    """Create the cascade files if absent; leave existing state intact.

    `init` is idempotent by design — `--mode resume` must not erase the
    history of a part-built project.
    """
    project = Path(project)
    build_dir(project).mkdir(parents=True, exist_ok=True)

    state = read_pipeline_state(project)
    if not state:
        state = {
            "project": project_name,
            "framework": f"Anu Framework {FRAMEWORK_VERSION}",
            "mode": mode,
            "current_stage": 0,
            "created": now_iso(),
            "last_updated": now_iso(),
            "stages": {
                str(n): {
                    "label": label,
                    "status": "pending",
                    "series_complete": 0,
                    "series_total": 0,
                    "gate_passed": False,
                }
                for n, label in STAGE_LABELS.items()
            },
        }
    else:
        state["mode"] = mode
        state["last_updated"] = now_iso()
    _write_json(pipeline_state_path(project), state)

    if not step_log_path(project).exists():
        step_log_path(project).write_text("", encoding="utf-8")

    if not narrative_path(project).exists():
        narrative_path(project).write_text(
            f"# Build Narrative — {project_name}\n\n"
            f"Chronological record of every step `anu-build` took. Append-only; "
            f"one entry per STEP_LOG line.\n\n"
            f"Framework: Anu Framework {FRAMEWORK_VERSION}\n\n---\n\n",
            encoding="utf-8",
        )

    return state


def append_step_log(project: Path, record: dict) -> None:
    """Append one JSON object to STEP_LOG.jsonl."""
    path = step_log_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_narrative(project: Path, text: str, step_id: str) -> None:
    """Append a narrative block, tagged with the STEP_LOG id it explains."""
    path = narrative_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"<!-- step_id: {step_id} -->\n{text}\n---\n\n")


def advance_stage(project: Path, stage: int, label: str | None = None,
                  gate_passed: bool | None = None) -> dict:
    """Set the current stage and stamp its status in PIPELINE_STATE.json."""
    project = Path(project)
    state = read_pipeline_state(project)
    if not state:
        raise FileNotFoundError(
            f"PIPELINE_STATE.json not found under {project}. Run `build.py init` first.")

    label = label or STAGE_LABELS.get(stage, "UNKNOWN")
    stages = state.setdefault("stages", {})
    entry = stages.setdefault(str(stage), {})
    entry["label"] = label
    entry.setdefault("series_complete", 0)
    entry.setdefault("series_total", 0)
    entry["status"] = "in_progress"
    if gate_passed is not None:
        entry["gate_passed"] = bool(gate_passed)
    entry.setdefault("gate_passed", False)

    for n in range(stage):
        prior = stages.setdefault(str(n), {"label": STAGE_LABELS.get(n, "UNKNOWN")})
        if prior.get("status") in (None, "pending"):
            prior["status"] = "complete"

    state["current_stage"] = stage
    state["last_updated"] = now_iso()
    _write_json(pipeline_state_path(project), state)
    return state


# --------------------------------------------------------------------------
# Ledger regeneration
# --------------------------------------------------------------------------

# artifact key -> (subdirectory, filename pattern with {sid})
ARTIFACT_PATTERNS = {
    "research": ("research", "{sid}_research.json"),
    "dpr": ("docs/series", "{sid}_DPR.md"),
    "epr": ("docs/series", "{sid}_EPR.md"),
    "decomposition": ("docs/series", "{sid}_DECOMPOSITION.md"),
    "explainer": ("docs/explainers", "{sid}_EXPLAINER.md"),
    "chopped": ("chopped", "{sid}.csv"),
}

# artifact key -> (subdirectory, glob) for the L01/P02/V03 triad
TRIAD_PATTERNS = {
    "loader": ("code/L01_loaders", "L01_{sid}*.py"),
    "processor": ("code/P02_processors", "P02_{sid}*.py"),
    "validator": ("code/V03_validators", "V03_{sid}*.py"),
}


def _artifact_present(project: Path, subdir: str, name: str) -> bool:
    return (project / subdir / name).exists()


def _triad_present(project: Path, subdir: str, pattern: str) -> bool:
    directory = project / subdir
    if not directory.is_dir():
        return False
    return any(directory.glob(pattern))


def regenerate_ledger(project: Path, registry_path: Path) -> dict:
    """Rebuild ANU_LEDGER.json from the registry plus files on disk."""
    project = Path(project)
    registry = _read_json(Path(registry_path))
    series = registry.get("series") or {}

    entries: dict[str, dict] = {}
    for sid, sdef in series.items():
        record: dict = {
            "name": sdef.get("name", ""),
            "status": sdef.get("status", "unknown"),
            "subseries_count": len(sdef.get("subseries") or {}),
        }
        for key, (subdir, name_tpl) in ARTIFACT_PATTERNS.items():
            record[key] = _artifact_present(project, subdir, name_tpl.format(sid=sid))
        for key, (subdir, glob_tpl) in TRIAD_PATTERNS.items():
            record[key] = _triad_present(project, subdir, glob_tpl.format(sid=sid))
        record["triad_complete"] = all(record[k] for k in TRIAD_PATTERNS)
        entries[sid] = record

    total = len(entries) or 1
    tracked = list(ARTIFACT_PATTERNS) + list(TRIAD_PATTERNS)
    coverage = {
        key: round(100.0 * sum(1 for r in entries.values() if r.get(key)) / total, 1)
        for key in tracked
    }

    ledger = {
        "project": registry.get("project", project.name),
        "framework": f"Anu Framework {FRAMEWORK_VERSION}",
        "generated_at": now_iso(),
        "generated_by": "anu-build/lib/cascade.py regenerate_ledger",
        "registry": str(Path(registry_path).name),
        "series_count": len(entries),
        "coverage_pct": coverage,
        "series": entries,
        "note": ("Artifact flags are filesystem-presence checks only. Presence "
                 "means the file exists, not that its contents are correct — "
                 "correctness is anu-doctor project mode and anu-review."),
    }
    _write_json(ledger_path(project), ledger)
    return ledger
