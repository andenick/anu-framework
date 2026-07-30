#!/usr/bin/env python3
"""Thin wrapper around skills/anu-doctor/check_framework.py at repo root.

check_framework.py resolves its own paths from its location, so this simply
forwards arguments to it (kept as a stable entry point for CI).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCTOR = REPO_ROOT / "skills" / "anu-doctor" / "check_framework.py"

if not DOCTOR.exists():
    print(f"check_framework.py not found at {DOCTOR}", file=sys.stderr)
    sys.exit(1)

sys.exit(subprocess.run([sys.executable, str(DOCTOR)] + sys.argv[1:]).returncode)
