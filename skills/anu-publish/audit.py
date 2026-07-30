#!/usr/bin/env python3
"""anu-publish audit — Pre-publication scrub auditor.

Walks the project tree, applies any `.publish_ignore` exclusion rules, then
greps every remaining text file for internal references that must NOT leak into
the public release. Reports findings per-file with line numbers; exit non-zero
on findings (zero on clean).

This is the canonical implementation of `/anu-publish audit`. It runs BEFORE
`anu-publish package` so agents can identify and remediate leaks early
(catching them during package would require a re-run after fixes).

Where the deny-list comes from
------------------------------
The patterns are DATA, not source. They live in `scrub_patterns.json` next to
this script, in the shape `{"fail": [{"pattern", "label"}, ...], "warn": [...]}`.

The shipped `scrub_patterns.json` is deliberately organization-neutral: it
matches the *classes* of reference that leak — absolute Windows drive paths,
POSIX home directories, UNC shares, email addresses, decision-log codes. It
does not enumerate any organization's private directory names, tool names,
project codenames or usernames, because a published deny-list of private names
is itself a disclosure of those names.

Add your own organization-specific names in a private overlay file that you do
not commit. Resolution order (each step wins over the next):

  1. --patterns <file>
  2. $ANU_SCRUB_PATTERNS
  3. <project>/.anu_scrub_patterns.json
  4. scrub_patterns.json shipped beside this script

Steps 1-3 are ADDITIVE overlays: they extend the neutral defaults rather than
replacing them, so a malformed overlay can never silently disarm the gate.

Because a scrubber that matches nothing reports CLEAN, the empty deny-list is
treated as a hard error, and `--self-test` runs the effective patterns against
built-in positive and negative fixtures. Run it in CI alongside the audit —
per GATE_DESIGN §6(c), a gate that cannot fail is not a gate.

An optional `.publish_ignore` at the project root uses fnmatch glob syntax, one
pattern per line; a trailing '/' marks a directory subtree. THIS REPOSITORY
SHIPS NONE, deliberately — exempting the files that actually carry leaks turns
the gate into decoration. Per GATE_DESIGN §6(a), any exemption you do add should
record a reason, an owner and a review-by date.

Self-exemptions (hard-coded, narrow — GATE_DESIGN §6(b)):
  - this audit script, which carries the self-test fixtures;
  - the deny-list files, which carry the patterns.

Usage:
  python audit.py                       # report findings (exit non-zero if any)
  python audit.py --strict              # additionally fail on WARN-severity hits
  python audit.py --report json         # machine-readable JSON output
  python audit.py --project <path>      # audit a different project root
  python audit.py --patterns <file>     # additional deny-list overlay
  python audit.py --self-test           # prove the deny-list is armed

Part of the Anu Framework v12.2 — see anu-publish/SKILL.md.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_PATTERN_FILE = Path(__file__).resolve().parent / "scrub_patterns.json"
OVERLAY_FILENAME = ".anu_scrub_patterns.json"
OVERLAY_ENV_VAR = "ANU_SCRUB_PATTERNS"

# Fixtures for --self-test. They live here, in the one file the audit exempts
# from itself, so that no fixture line can be mistaken for a real finding.
SELF_TEST_MUST_FLAG = [
    'OUTPUT = "D:/Workspace/Project/Outputs"',
    r'path = "C:\Users\someone\Documents"',
    "cache = /home/someone/.cache/anu",
    r"share = \\fileserver\team\data",
    "maintainer: someone@example.org",
]
SELF_TEST_MUST_NOT_FLAG = [
    "See https://fred.stlouisfed.org/docs/api/api_key.html",
    "from pathlib import Path",
    'registry = json.load(open("series_registry.json"))',
    "| S001 | Industrial production | index_2017=100 |",
]


class PatternConfigError(RuntimeError):
    """The effective deny-list is missing, malformed, or empty."""


def _compile_entries(entries: object, source: Path, key: str
                     ) -> list[tuple[re.Pattern, str]]:
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise PatternConfigError(f"{source}: '{key}' must be a list")
    out = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or "pattern" not in entry:
            raise PatternConfigError(
                f"{source}: {key}[{i}] must be an object with a 'pattern' key")
        label = entry.get("label") or entry["pattern"]
        try:
            out.append((re.compile(entry["pattern"]), label))
        except re.error as exc:
            raise PatternConfigError(
                f"{source}: {key}[{i}] is not a valid regex — {exc}") from exc
    return out


def _read_pattern_file(path: Path) -> tuple[list, list]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatternConfigError(f"{path}: not valid JSON — {exc}") from exc
    if not isinstance(data, dict):
        raise PatternConfigError(f"{path}: top level must be an object")
    return (_compile_entries(data.get("fail"), path, "fail"),
            _compile_entries(data.get("warn"), path, "warn"))


def load_scrub_patterns(project_root: Path, overlay: Path | None = None
                        ) -> tuple[list, list, list[str]]:
    """Return (fail_patterns, warn_patterns, sources).

    The shipped neutral defaults are always loaded. Organization-specific
    overlays are merged ON TOP of them, never in place of them, so a missing or
    mistyped overlay path degrades to "fewer patterns", never to "no patterns" —
    and an empty effective deny-list raises instead of reporting CLEAN.
    """
    if not DEFAULT_PATTERN_FILE.exists():
        raise PatternConfigError(
            f"deny-list not found at {DEFAULT_PATTERN_FILE} — refusing to run "
            "an unarmed scrub audit")
    fail, warn = _read_pattern_file(DEFAULT_PATTERN_FILE)
    sources = [str(DEFAULT_PATTERN_FILE)]

    candidates: list[Path] = []
    if overlay is not None:
        candidates.append(overlay)
    env_overlay = os.environ.get(OVERLAY_ENV_VAR)
    if env_overlay:
        candidates.append(Path(env_overlay))
    candidates.append(project_root / OVERLAY_FILENAME)

    for cand in candidates:
        if not cand.exists():
            if overlay is not None and cand == overlay:
                raise PatternConfigError(f"--patterns file not found: {cand}")
            continue
        extra_fail, extra_warn = _read_pattern_file(cand)
        fail.extend(extra_fail)
        warn.extend(extra_warn)
        sources.append(str(cand))

    if not fail and not warn:
        raise PatternConfigError(
            "effective deny-list is empty — a scrub audit that matches nothing "
            "would report CLEAN for every project. Fix the pattern file(s): "
            + ", ".join(sources))
    return fail, warn, sources


def self_test(fail_patterns: list, warn_patterns: list) -> int:
    """Prove the deny-list can actually fail. Returns a process exit code."""
    all_patterns = list(fail_patterns) + list(warn_patterns)
    problems: list[str] = []
    for line in SELF_TEST_MUST_FLAG:
        if not any(pat.search(line) for pat, _ in all_patterns):
            problems.append(f"NOT FLAGGED (should be): {line!r}")
    for line in SELF_TEST_MUST_NOT_FLAG:
        hit = next((name for pat, name in all_patterns if pat.search(line)), None)
        if hit:
            problems.append(f"FALSE POSITIVE [{hit}]: {line!r}")
    if problems:
        print("    [anu-publish audit] SELF-TEST FAILED — the deny-list is not "
              "behaving as specified:")
        for p in problems:
            print(f"      {p}")
        return 1
    print(f"    [anu-publish audit] SELF-TEST PASSED — {len(all_patterns)} "
          f"pattern(s) armed; {len(SELF_TEST_MUST_FLAG)} positive and "
          f"{len(SELF_TEST_MUST_NOT_FLAG)} negative fixtures behave correctly.")
    return 0


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


ALWAYS_SKIP = (
    ".git/", "__pycache__/", ".venv/", "venv/", "data/raw/",
)


def is_ignored(rel_path: str, patterns: list[str]) -> bool:
    if any(rel_path.startswith(s) for s in ALWAYS_SKIP):
        return True
    # The ONE narrow self-exemption (GATE_DESIGN §6(b)): the gate itself and the
    # deny-list it is defined by necessarily contain matching lines (this script
    # carries the self-test fixtures; the pattern files carry the patterns).
    # Nothing else is exempt — a file that carries a real leak must fail.
    if (rel_path.endswith("anu-publish/audit.py")
            or rel_path.endswith("anu-publish/scrub_patterns.json")
            or rel_path.endswith(OVERLAY_FILENAME)):
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


def scan_file(path: Path, fail_patterns: list, warn_patterns: list
              ) -> list[tuple[int, str, str, str]]:
    """Return [(line_no, severity, pattern_name, line_content_trimmed), ...]."""
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat, name in fail_patterns:
            if pat.search(line):
                findings.append((lineno, "FAIL", name, line.strip()[:120]))
                break
        else:
            for pat, name in warn_patterns:
                if pat.search(line):
                    findings.append((lineno, "WARN", name, line.strip()[:120]))
                    break
    return findings


TEXT_EXTENSIONS = {
    ".md", ".py", ".json", ".csv", ".tex", ".yaml", ".yml", ".cff",
    ".toml", ".txt", ".cfg", ".ini", ".html", ".rst",
    # v2.2 gate fix: run/build outputs are text and DID carry real leaks
    ".out", ".log",
}


# Codename-shaped folder names. Distribution bundles should use descriptive
# slugs (e.g. `measuring-wealth-of-nations-replication_Drive_v1.0`), not opaque
# internal project codenames (e.g. `XY2_Drive_v2.0`).
# WARN-severity — historical bundles get flagged for renaming.
CODENAME_FOLDER_RE = re.compile(r"(?:^|/)[A-Z]{2,4}\d*_(?:Drive|Publish|Archive)_v")


def scan_folder_names(project_root: Path, patterns: list[str]) -> list[tuple[str, str]]:
    """Return [(rel_path, pattern_name), ...] for codename-shaped folder names.

    Walks directories under the project root; flags ones whose path matches
    the codename pattern. Each finding is a WARN.
    """
    findings = []
    for path in project_root.rglob("*"):
        if not path.is_dir():
            continue
        rel = path.relative_to(project_root).as_posix()
        if is_ignored(rel + "/", patterns):
            continue
        if CODENAME_FOLDER_RE.search("/" + rel):
            findings.append((rel, "codename-shaped folder name"))
    return findings


def run(project_root: Path, strict: bool, report_format: str,
        fail_patterns: list, warn_patterns: list, sources: list[str]) -> int:
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
        f = scan_file(path, fail_patterns, warn_patterns)
        if f:
            findings_by_file[rel] = f

    # Folder-name scan (WARN-severity)
    folder_findings = scan_folder_names(project_root, patterns)

    n_fail = sum(1 for hits in findings_by_file.values() for h in hits if h[1] == "FAIL")
    n_warn = sum(1 for hits in findings_by_file.values() for h in hits if h[1] == "WARN")
    n_warn += len(folder_findings)

    if report_format == "json":
        out = {
            "pattern_sources": sources,
            "patterns_armed": len(fail_patterns) + len(warn_patterns),
            "files_scanned": total_scanned,
            "files_with_findings": len(findings_by_file),
            "fail_count": n_fail,
            "warn_count": n_warn,
            "findings": {rel: [
                {"line": ln, "severity": sev, "pattern": pat, "content": c}
                for (ln, sev, pat, c) in hits
            ] for rel, hits in findings_by_file.items()},
            "folder_findings": [
                {"path": rel, "pattern": pat} for rel, pat in folder_findings
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"    [anu-publish audit] Deny-list: "
              f"{len(fail_patterns)} FAIL + {len(warn_patterns)} WARN pattern(s) "
              f"from {len(sources)} source(s): {', '.join(sources)}")
        print(f"    [anu-publish audit] Scanned {total_scanned} text files (excluding .publish_ignore)")
        if not findings_by_file and not folder_findings:
            print(f"    [anu-publish audit] CLEAN — zero internal references in public-eligible files.")
        else:
            total_files = len(findings_by_file) + (1 if folder_findings else 0)
            print(f"    [anu-publish audit] {n_fail} FAIL + {n_warn} WARN findings across "
                  f"{total_files} item(s):")
            for rel, hits in findings_by_file.items():
                print(f"      {rel}:")
                for lineno, sev, pat, line in hits[:5]:
                    print(f"        L{lineno} [{sev}] [{pat}] {line}")
                if len(hits) > 5:
                    print(f"        ...({len(hits) - 5} more)")
            if folder_findings:
                print(f"      folder-name findings:")
                for rel, pat in folder_findings[:10]:
                    print(f"        [WARN] [{pat}] {rel}")
                if len(folder_findings) > 10:
                    print(f"        ...({len(folder_findings) - 10} more)")

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
    p.add_argument("--patterns", default=None,
                   help="Additional deny-list overlay (JSON); merged ON TOP of "
                        "the shipped neutral defaults")
    p.add_argument("--self-test", action="store_true",
                   help="Prove the effective deny-list matches its fixtures, "
                        "then exit (run this in CI beside the audit)")
    args = p.parse_args()

    project_root = Path(args.project).resolve()
    try:
        fail_patterns, warn_patterns, sources = load_scrub_patterns(
            project_root, Path(args.patterns) if args.patterns else None)
    except PatternConfigError as exc:
        print(f"    [anu-publish audit] DENY-LIST ERROR: {exc}", file=sys.stderr)
        return 2

    if args.self_test:
        return self_test(fail_patterns, warn_patterns)

    return run(project_root, args.strict, args.report,
               fail_patterns, warn_patterns, sources)


if __name__ == "__main__":
    sys.exit(main())
