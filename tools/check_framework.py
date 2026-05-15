#!/usr/bin/env python3
"""Thin wrapper around skills/anu-doctor/check_framework.py.

Adapts the path constants to the public-repo layout (skills/ + docs/ at root).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCTOR = REPO_ROOT / "skills" / "anu-doctor" / "check_framework.py"

if not DOCTOR.exists():
    print(f"check_framework.py not found at {DOCTOR}", file=sys.stderr)
    sys.exit(1)

src = DOCTOR.read_text(encoding="utf-8")
src = src.replace(
    "SKILLS_DIR = Path(__file__).resolve().parent.parent",
    f"SKILLS_DIR = Path({str(REPO_ROOT)!r}) / 'skills'"
)
src = src.replace(
    "DRUCK_DIR = SKILLS_DIR.parent.parent",
    f"DRUCK_DIR = Path({str(REPO_ROOT)!r})"
)
exec(compile(src, str(DOCTOR), "exec"),
     {"__name__": "__main__", "__file__": str(DOCTOR)})
