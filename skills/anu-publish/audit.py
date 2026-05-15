#!/usr/bin/env python3
"""anu-publish audit — Pre-publication scrub auditor.

Walks the project tree, applies `.publish_ignore` exclusion rules, then greps
every remaining text file for internal references that must NOT leak into the
public release. Reports findings per-file with line numbers; exit non-zero
on findings (zero on clean).

This is the canonical implementation of `/anu-publish audit`. It runs BEFORE
`anu-publish package` so agents can identify and remediate leaks early
(catching them during package would require a re-run after fixes).

Scrub patterns flag the categories of internal reference seen in real
Arcanum projects:

  D:/Arcanum            — hard-coded workspace path
  /Council/             — internal infrastructure directory
  \\bDruck\\b           — internal performance-monitoring tool name
  \\bRobin/             — internal data-acquisition tool name (NOT the
                          person-name "Robin", which appears as a citation
                          surname). The pattern requires '/' suffix so
                          "Robin Cherry et al." doesn't false-positive.
  DEC-[A-Z0-9]+         — internal decision-log codes inherited from
                          predecessor projects (e.g. ST2's <decision-ref> marker)

The `.publish_ignore` file uses fnmatch glob syntax, one pattern per line.
Trailing '/' marks a directory pattern (and its subtree).

False-positive exclusions:
  - The audit script itself (contains the patterns in its docstring)
  - docs/chapters/*_REVIEW_REPORT.json (review reports document the policy)
  - MIGRATION/divergences_from_ST2.md (legacy doc that names patterns)

Usage:
  python audit.py                       # report findings (exit non-zero if any)
  python audit.py --strict              # additionally fail on WARN-severity hits
  python audit.py --report json         # machine-readable JSON output
  python audit.py --project <path>      # audit a different project root

Part of the Anu Framework v11.0 — see anu-publish/SKILL.md.

Derived from the RMWND build's code/S00_setup/S06_publish_scrub_audit.py.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


# Patterns that flag real internal references.
# Severity FAIL — must be scrubbed before publication.
# Severity WARN — review before publication (some may be intentional in
# documentation that explicitly explains the framework boundary).
SCRUB_PATTERNS_FAIL = [
    (re.compile(r"D:[/\\]Arcanum"),         "D:/Arcanum path"),
    (re.compile(r"/Council/|\\Council\\"),   "/Council/ directory"),
    (re.compile(r"\bDruck\b"),               "Druck tool name"),
    (re.compile(r"\bRobin/|\bRobin\\"),     "Robin/ tool directory"),
]
SCRUB_PATTERNS_WARN = [
    (re.compile(r"DEC-[A-Z0-9]+"),           "<decision-ref> internal decision code"),
]


def load_ignore_patterns(project_root: Path) -> list[str]:
    path = project_root / ".publish_ignore"
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


# Files that legitimately describe the scrub policy itself; flagging them
# would create false positives. Configurable per project.
ALWAYS_SKIP = (
    ".git/", "__pycache__/", ".venv/", "venv/", "data/raw/",
)

POLICY_DESCRIBING_FILES = (
    # Files that describe / document the scrub policy. They reference the
    # very patterns we audit for; flagging them would be circular.
)


def is_ignored(rel_path: str, patterns: list[str]) -> bool:
    if any(rel_path.startswith(s) for s in ALWAYS_SKIP):
        return True
    # The audit script itself
    if rel_path.endswith("anu-publish/audit.py") or rel_path.endswith("code/S00_setup/S06_publish_scrub_audit.py"):
        return True
    # Chapter REVIEW reports document the scrub policy by definition
    if "docs/chapters/" in rel_path and rel_path.endswith("_REVIEW_REPORT.json"):
        return True
    # MIGRATION/divergences_*.md describe predecessor branding
    if rel_path.startswith("MIGRATION/divergences_"):
        return True
    # Apply .publish_ignore patterns
    for pat in patterns:
        if pat.endswith("/"):
            if rel_path.startswith(pat) or f"/{pat}" in rel_path:
                return True
        else:
            if fnmatch.fnmatch(rel_path, pat) or rel_path == pat:
                return True
    return False


def scan_file(path: Path) -> list[tuple[int, str, str, str]]:
    """Return [(line_no, severity, pattern_name, line_content_trimmed), ...]."""
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat, name in SCRUB_PATTERNS_FAIL:
            if pat.search(line):
                findings.append((lineno, "FAIL", name, line.strip()[:120]))
                break
        else:
            for pat, name in SCRUB_PATTERNS_WARN:
                if pat.search(line):
                    findings.append((lineno, "WARN", name, line.strip()[:120]))
                    break
    return findings


TEXT_EXTENSIONS = {
    ".md", ".py", ".json", ".csv", ".tex", ".yaml", ".yml", ".cff",
    ".toml", ".txt", ".cfg", ".ini", ".html", ".rst",
}


def run(project_root: Path, strict: bool, report_format: str) -> int:
    patterns = load_ignore_patterns(project_root)
    total_scanned = 0
    findings_by_file: dict[str, list] = {}

    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(project_root).as_posix()
        if is_ignored(rel, patterns):
            continue
        if path.suffix not in TEXT_EXTENSIONS:
            continue
        total_scanned += 1
        f = scan_file(path)
        if f:
            findings_by_file[rel] = f

    n_fail = sum(1 for hits in findings_by_file.values() for h in hits if h[1] == "FAIL")
    n_warn = sum(1 for hits in findings_by_file.values() for h in hits if h[1] == "WARN")

    if report_format == "json":
        out = {
            "files_scanned": total_scanned,
            "files_with_findings": len(findings_by_file),
            "fail_count": n_fail,
            "warn_count": n_warn,
            "findings": {rel: [
                {"line": ln, "severity": sev, "pattern": pat, "content": c}
                for (ln, sev, pat, c) in hits
            ] for rel, hits in findings_by_file.items()},
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"    [anu-publish audit] Scanned {total_scanned} text files (excluding .publish_ignore)")
        if not findings_by_file:
            print(f"    [anu-publish audit] CLEAN — zero internal references in public-eligible files.")
        else:
            print(f"    [anu-publish audit] {n_fail} FAIL + {n_warn} WARN findings in {len(findings_by_file)} files:")
            for rel, hits in findings_by_file.items():
                print(f"      {rel}:")
                for lineno, sev, pat, line in hits[:5]:
                    print(f"        L{lineno} [{sev}] [{pat}] {line}")
                if len(hits) > 5:
                    print(f"        ...({len(hits) - 5} more)")

    if n_fail:
        return 1
    if strict and n_warn:
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="anu-publish audit — pre-publication scrub")
    p.add_argument("--project", default=".", help="Project root (default: cwd)")
    p.add_argument("--strict", action="store_true", help="Fail on WARN-severity hits too")
    p.add_argument("--report", default="text", choices=["text", "json"])
    args = p.parse_args()
    return run(Path(args.project).resolve(), args.strict, args.report)


if __name__ == "__main__":
    sys.exit(main())
