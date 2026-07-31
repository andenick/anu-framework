#!/usr/bin/env python3
"""Construction graph — compute the topological build order for a project.

Reads `series_registry.json` and derives the dependency DAG that
`anu-build` Stage 5 walks. Nodes are subseries where a series declares
them (`{SID}-{SUB}`) and the series itself (`{SID}`) where it does not.
Edges run from input to output, so a Kahn topological sort yields layers
that can be constructed left to right.

Dependencies are read from the registry fields that actually carry them
(see `docs/SERIES_REGISTRY_SCHEMA.md`):

  series level      `components`, `source_series`, `construction[].inputs`
  subseries level   `derived_from`, `transform.inputs`, `transform.input`,
                    `transform.match_to`, `transform.deflator`

Nothing is inferred from names. A dependency that names an ID absent from
the registry is reported in `unresolved_edges` rather than dropped.

Stdlib only. Part of the Anu Framework v12.2 — see anu-build/SKILL.md.
"""
from __future__ import annotations

import json
from pathlib import Path


# --------------------------------------------------------------------------
# Node identity
# --------------------------------------------------------------------------

def _node(series_id: str, subseries_id: str | None = None) -> str:
    return series_id if subseries_id is None else f"{series_id}-{subseries_id}"


def _as_list(value) -> list[str]:
    """Normalize a registry field that may be a string, list, or None."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if isinstance(v, str) and v.strip()]
    return []


def _resolve(ref: str, series_id: str, known: set[str]) -> str | None:
    """Resolve a dependency reference to a node id, or None if unknown.

    A reference may be a bare subseries id (`"A"`, resolved within the
    declaring series), a qualified subseries id (`"D003-A"`), or a series
    id (`"D003"`). Compound notation such as `"A+B"` is split by the
    caller, not here.
    """
    ref = ref.strip()
    if not ref:
        return None
    if ref in known:
        return ref
    qualified = _node(series_id, ref)
    if qualified in known:
        return qualified
    return None


def _split_refs(raw: str) -> list[str]:
    """Split `derived_from`-style compound notation (`"A+B"`) into refs."""
    out: list[str] = []
    for piece in raw.replace(",", "+").split("+"):
        piece = piece.strip()
        if piece:
            out.append(piece)
    return out


# --------------------------------------------------------------------------
# Graph construction
# --------------------------------------------------------------------------

def _collect_nodes(series: dict) -> tuple[list[str], dict[str, str]]:
    """Return (ordered node ids, node -> owning series id)."""
    nodes: list[str] = []
    owner: dict[str, str] = {}
    for sid, sdef in series.items():
        subs = sdef.get("subseries") or {}
        if isinstance(subs, dict) and subs:
            for sub_id in subs:
                n = _node(sid, sub_id)
                nodes.append(n)
                owner[n] = sid
        else:
            nodes.append(sid)
            owner[sid] = sid
    return nodes, owner


def _dependencies_for_subseries(sub_def: dict) -> list[str]:
    refs: list[str] = []
    if isinstance(sub_def.get("derived_from"), str):
        refs.extend(_split_refs(sub_def["derived_from"]))
    transform = sub_def.get("transform")
    if isinstance(transform, dict):
        for key in ("input", "match_to", "deflator"):
            refs.extend(_as_list(transform.get(key)))
        refs.extend(_as_list(transform.get("inputs")))
    return refs


def _dependencies_for_series(sdef: dict) -> list[str]:
    refs: list[str] = []
    refs.extend(_as_list(sdef.get("components")))
    refs.extend(_as_list(sdef.get("source_series")))
    construction = sdef.get("construction")
    if isinstance(construction, list):
        for step in construction:
            if isinstance(step, dict):
                refs.extend(_as_list(step.get("inputs")))
                refs.extend(_as_list(step.get("input")))
    return refs


def build_graph(registry: dict) -> dict:
    """Build the dependency DAG. Returns nodes, edges, unresolved_edges."""
    series = registry.get("series") or {}
    nodes, owner = _collect_nodes(series)
    known = set(nodes)

    edges: list[dict] = []
    unresolved: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add_edge(src_ref: str, dst: str, sid: str, origin: str) -> None:
        resolved = _resolve(src_ref, sid, known)
        if resolved is None:
            unresolved.append({"from": src_ref, "to": dst, "declared_in": origin})
            return
        if resolved == dst:
            return
        key = (resolved, dst)
        if key in seen:
            return
        seen.add(key)
        edges.append({"from": resolved, "to": dst})

    for sid, sdef in series.items():
        subs = sdef.get("subseries") or {}
        if isinstance(subs, dict) and subs:
            for sub_id, sub_def in subs.items():
                if not isinstance(sub_def, dict):
                    continue
                dst = _node(sid, sub_id)
                for ref in _dependencies_for_subseries(sub_def):
                    add_edge(ref, dst, sid, f"{sid}.subseries.{sub_id}")
            # A series-level dependency on another series becomes an edge into
            # every one of this series' subseries that declares no parent of
            # its own — the whole series waits on it.
            series_refs = _dependencies_for_series(sdef)
            if series_refs:
                for sub_id, sub_def in subs.items():
                    if not isinstance(sub_def, dict):
                        continue
                    if _dependencies_for_subseries(sub_def):
                        continue
                    dst = _node(sid, sub_id)
                    for ref in series_refs:
                        add_edge(ref, dst, sid, f"{sid}.construction")
        else:
            for ref in _dependencies_for_series(sdef):
                add_edge(ref, sid, sid, f"{sid}.construction")

    return {"nodes": nodes, "edges": edges, "unresolved_edges": unresolved,
            "owner": owner}


# --------------------------------------------------------------------------
# Topological sort (Kahn)
# --------------------------------------------------------------------------

def topological_layers(nodes: list[str], edges: list[dict]) -> tuple[list[list[str]], list[str]]:
    """Kahn's algorithm. Returns (layers, nodes_in_cycles).

    Layer 0 has no unbuilt dependencies; layer N depends only on layers
    < N. Any node left over is part of a dependency cycle and is returned
    separately rather than silently placed in a layer.
    """
    indeg = {n: 0 for n in nodes}
    succ: dict[str, list[str]] = {n: [] for n in nodes}
    for e in edges:
        src, dst = e["from"], e["to"]
        if src not in indeg or dst not in indeg:
            continue
        succ[src].append(dst)
        indeg[dst] += 1

    layers: list[list[str]] = []
    frontier = sorted(n for n in nodes if indeg[n] == 0)
    placed = 0
    while frontier:
        layers.append(frontier)
        placed += len(frontier)
        nxt: list[str] = []
        for n in frontier:
            for m in succ[n]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    nxt.append(m)
        frontier = sorted(nxt)

    in_cycle = sorted(n for n in nodes if indeg[n] > 0) if placed < len(nodes) else []
    return layers, in_cycle


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def generate_plan(registry_path: str | Path) -> dict:
    """Compute SUBSERIES_PLAN.json content from a series registry."""
    registry_path = Path(registry_path)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    series = registry.get("series") or {}

    graph = build_graph(registry)
    layers, in_cycle = topological_layers(graph["nodes"], graph["edges"])

    subseries_count = sum(
        len(s.get("subseries") or {}) for s in series.values()
        if isinstance(s.get("subseries"), dict)
    )

    return {
        "project": registry.get("project", registry_path.parent.name),
        "registry": registry_path.name,
        "series_count": len(series),
        "subseries_count": subseries_count,
        "node_count": len(graph["nodes"]),
        "layers": [{"layer": i, "subseries": layer} for i, layer in enumerate(layers)],
        "edges": graph["edges"],
        "unresolved_edges": graph["unresolved_edges"],
        "cycle_nodes": in_cycle,
    }


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    import sys
    print(json.dumps(generate_plan(sys.argv[1]), indent=2))
