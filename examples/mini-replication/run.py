"""Master orchestrator for mini-replication example.

Sequences L## → P## → V## → O## scripts by glob discovery.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
PHASE_DIRS = {"L": "loading", "P": "processing", "V": "validation", "O": "outputs"}


def discover(phase: str):
    d = PROJECT / "code" / PHASE_DIRS[phase]
    if not d.exists():
        return []
    return sorted([p for p in d.iterdir()
                   if p.is_file() and p.name.startswith(phase)
                   and p.suffix == ".py" and p.name[1:3].isdigit()],
                  key=lambda p: int(p.name[1:3]))


def main():
    order = "LPVO"
    for ph in order:
        for s in discover(ph):
            print(f"\n[{ph}] {s.name}")
            r = subprocess.run([sys.executable, str(s)], cwd=PROJECT)
            if r.returncode != 0:
                print(f"FAILED at {s.name}", file=sys.stderr)
                sys.exit(r.returncode)
    print("\n[run] DONE")


if __name__ == "__main__":
    main()
