#!/usr/bin/env python3
"""Thin wrapper around skills/anu-publish/audit.py at repo root."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT = REPO_ROOT / "skills" / "anu-publish" / "audit.py"

if not AUDIT.exists():
    print(f"audit.py not found at {AUDIT}", file=sys.stderr)
    sys.exit(1)

sys.exit(subprocess.run(
    [sys.executable, str(AUDIT), "--project", str(REPO_ROOT)] + sys.argv[1:]
).returncode)
