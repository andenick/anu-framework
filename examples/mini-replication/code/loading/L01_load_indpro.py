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
# The committed CSV IS the offline cache and is never overwritten by a fetch,
# so a network round-trip can never silently change the tracked inputs. A fresh
# download lands beside it; promote it deliberately if you want to re-baseline.
cache = out_dir / "indpro_monthly.csv"
out = out_dir / "indpro_monthly.fetched.csv"

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO"
print(f"  Fetching {URL}")
try:
    with urlopen(URL, timeout=30) as r:
        text = r.read().decode("utf-8")
    out.write_text(text)
    print(f"  Wrote {out.relative_to(PROJECT)} ({len(text)} bytes)")
    print(f"  NOTE: {cache.name} (the tracked offline cache) is unchanged. "
          f"To re-baseline, copy {out.name} over it and re-run P01/P02 + V01/V02.")
except Exception as e:
    print(f"  WARN: fetch failed ({e}); continuing with the committed offline "
          f"cache at {cache.relative_to(PROJECT)}.")
