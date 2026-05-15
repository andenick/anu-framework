"""L01: Load FRED INDPRO
====================
Phase:   Loading
Purpose: Download Industrial Production Index from FRED public URL.
Public Source: https://fred.stlouisfed.org/series/INDPRO
Units:   Index, 2017=100
"""
from pathlib import Path
from urllib.request import urlopen

PROJECT = Path(__file__).resolve().parent.parent.parent
out_dir = PROJECT / "data" / "raw-data"
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "indpro_monthly.csv"

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO"
print(f"  Fetching {URL}")
try:
    with urlopen(URL, timeout=30) as r:
        text = r.read().decode("utf-8")
    out.write_text(text)
    print(f"  Wrote {out.relative_to(PROJECT)} ({len(text)} bytes)")
except Exception as e:
    print(f"  WARN: fetch failed ({e}); skipping (no offline cache).")
