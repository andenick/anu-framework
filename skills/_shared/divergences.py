"""Shared divergence register helper — used by anu-ingestion, anu-extension,
anu-replicator, and anu-rebuild.

A divergence is any deliberate departure from a predecessor implementation or
from an authoritative source — picked up during ingestion (e.g., catching a
proxy that's miscategorized), extension (e.g., choosing one API over another
when the book's table is no longer published), or manual adjustment.

The register lives at `<project_root>/DIVERGENCE_REGISTER.json` and is the
canonical record for `anu-review` D13 (data authenticity) reporting and for
the public methodology PDF.

Usage (from any skill):

    from _shared.divergences import register_divergence

    register_divergence(
        project_root=Path("Projects/RMWND/Technical"),
        series_id="S507",
        skill="anu-ingestion",
        category="ingestion",
        predecessor_value="0.5698 from T509_surplus_ratio NIPA proxy",
        new_value="0.6296 from algebraic identity S/Y = e/(1+e)",
        rationale="Book defines S/Y = e/(1+e); predecessor's NIPA proxy violates the identity over the same accounting universe."
    )

Part of the Anu Framework v11.0.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

VALID_CATEGORIES = (
    "ingestion",          # caught during series_registry / DPR construction
    "extension",          # caught during API splice / EPR construction
    "manual_adjustment",  # documented adjustment (K-to-K*, ec_u/ec_p, etc.)
    "scaffolding",        # caught during anu-scaffold review
    "scrub",              # caught during anu-publish audit (predecessor branding etc.)
)


def register_divergence(
    project_root: Path,
    series_id: str,
    skill: str,
    category: str,
    predecessor_value: str,
    new_value: str,
    rationale: str,
) -> Path:
    """Append a divergence entry to <project_root>/DIVERGENCE_REGISTER.json.

    Creates the file if it doesn't exist. Returns the path to the register.

    Raises ValueError if `category` is not in VALID_CATEGORIES.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"category must be one of {VALID_CATEGORIES}; got {category!r}"
        )

    path = Path(project_root) / "DIVERGENCE_REGISTER.json"
    if path.exists():
        register = json.loads(path.read_text(encoding="utf-8"))
    else:
        register = {"schema_version": "1.0", "divergences": []}

    register["divergences"].append({
        "series_id":         series_id,
        "skill":             skill,
        "category":          category,
        "logged_at":         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "predecessor_value": predecessor_value,
        "new_value":         new_value,
        "rationale":         rationale,
    })

    path.write_text(json.dumps(register, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_divergences(project_root: Path) -> list[dict]:
    """Return the list of divergence entries from <project_root>/DIVERGENCE_REGISTER.json.

    Returns [] if the register doesn't exist.
    """
    path = Path(project_root) / "DIVERGENCE_REGISTER.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("divergences", [])


def divergence_count_by_category(project_root: Path) -> dict[str, int]:
    """For anu-review D13 reporting — count divergences per category."""
    counts = {cat: 0 for cat in VALID_CATEGORIES}
    for d in load_divergences(project_root):
        cat = d.get("category", "")
        counts[cat] = counts.get(cat, 0) + 1
    return counts
