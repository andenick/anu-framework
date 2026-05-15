#!/usr/bin/env python3
"""
Vintage Data Downloader
========================

Part of the Anu Variant Standard v1.0.

Downloads and catalogs historical data vintages from:
  - ALFRED (Archival FRED) — Federal Reserve Bank of St. Louis
  - BEA NIPA Archives — Bureau of Economic Analysis
  - Philadelphia Fed RTDSM — Real-Time Data Set for Macroeconomists

Follows the pattern established in:
  Projects/Capitalism Data/Technical/scripts/alfred_vintages/

Usage:
  python vintage_downloader.py --series GDP CPIAUCSL --source alfred \
      --vintage 2024Q4 --output data/vintages/

  python vintage_downloader.py --catalog data/vintages/VINTAGE_DOWNLOAD_LOG.json
"""

import json
import sys
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ── ALFRED Configuration ───────────────────────────────────────────────

ALFRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
ALFRED_VINTAGE_URL = "https://api.stlouisfed.org/fred/series/vintagedates"

# ── BEA Configuration ─────────────────────────────────────────────────

BEA_BASE_URL = "https://apps.bea.gov/api/data"

# ── Philadelphia Fed RTDSM ────────────────────────────────────────────

PHILLY_FED_URL = "https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists"


class VintageDownloadLog:
    """Manages VINTAGE_DOWNLOAD_LOG.json."""

    def __init__(self, log_path: Path):
        self.path = Path(log_path)
        self._data = None

    def load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {
                "anu_variant_version": "1.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "total_downloads": 0,
                "downloads": [],
            }
        return self._data

    def save(self) -> None:
        if self._data is None:
            self.load()
        self._data["total_downloads"] = len(self._data.get("downloads", []))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def log_download(self, entry: dict) -> None:
        if self._data is None:
            self.load()
        entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        entry.setdefault("download_id", f"DL{len(self._data['downloads']) + 1:04d}")
        self._data["downloads"].append(entry)
        self.save()

    def list_downloads(self, series: str = None, source: str = None) -> list:
        if self._data is None:
            self.load()
        results = self._data.get("downloads", [])
        if series:
            results = [d for d in results if d.get("series") == series]
        if source:
            results = [d for d in results if d.get("source") == source]
        return results


def download_alfred_vintage(series_id: str, api_key: str, vintage_date: str,
                           output_dir: Path) -> dict:
    """Download a specific ALFRED vintage for a series."""
    if not HAS_REQUESTS:
        return {"status": "ERROR", "detail": "requests library not installed"}

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": vintage_date,
        "realtime_end": vintage_date,
    }

    try:
        resp = requests.get(ALFRED_BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Save raw response
        series_dir = output_dir / series_id
        series_dir.mkdir(parents=True, exist_ok=True)
        out_file = series_dir / f"{series_id}_{vintage_date}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        observations = data.get("observations", [])
        sha256 = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]

        return {
            "series": series_id,
            "source": "ALFRED",
            "vintage_date": vintage_date,
            "status": "OK",
            "observations": len(observations),
            "output_file": str(out_file),
            "sha256_prefix": sha256,
        }
    except Exception as e:
        return {
            "series": series_id,
            "source": "ALFRED",
            "vintage_date": vintage_date,
            "status": "ERROR",
            "detail": str(e),
        }


def get_alfred_vintage_dates(series_id: str, api_key: str) -> list:
    """Get available vintage dates for a series from ALFRED."""
    if not HAS_REQUESTS:
        return []
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }
    try:
        resp = requests.get(ALFRED_VINTAGE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("vintage_dates", [])
    except Exception:
        return []


def cli_download(args):
    """Download vintage data for specified series."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "VINTAGE_DOWNLOAD_LOG.json"
    log = VintageDownloadLog(log_path)
    log.load()

    api_key = args.api_key or ""
    if not api_key:
        print("WARNING: No API key provided. Set --api-key or FRED_API_KEY env var.")
        print("         Downloads will likely fail without a valid key.")

    for series_id in args.series:
        print(f"\nDownloading {series_id} (vintage: {args.vintage})...")
        if args.source == "alfred":
            result = download_alfred_vintage(series_id, api_key, args.vintage, output_dir)
        else:
            result = {"series": series_id, "source": args.source, "status": "ERROR",
                      "detail": f"Source '{args.source}' not yet implemented"}

        status = result.get("status", "ERROR")
        print(f"  Status: {status}")
        if status == "OK":
            print(f"  Observations: {result.get('observations', 0)}")
            print(f"  File: {result.get('output_file', '')}")
        else:
            print(f"  Detail: {result.get('detail', 'Unknown error')}")

        log.log_download(result)

    print(f"\nLog saved: {log_path}")


def cli_catalog(args):
    """Show catalog of downloaded vintages."""
    log_path = Path(args.catalog)
    if not log_path.exists():
        print(f"No download log found at: {log_path}")
        sys.exit(1)

    log = VintageDownloadLog(log_path)
    log.load()

    downloads = log.list_downloads(series=args.series, source=args.source)
    print(f"Total downloads: {len(downloads)}")
    print(f"{'ID':<10} {'Series':<15} {'Source':<10} {'Vintage':<12} {'Status':<8} {'Obs':<6}")
    print("-" * 65)
    for d in downloads:
        print(f"{d.get('download_id', '?'):<10} "
              f"{d.get('series', '?'):<15} "
              f"{d.get('source', '?'):<10} "
              f"{d.get('vintage_date', '?'):<12} "
              f"{d.get('status', '?'):<8} "
              f"{d.get('observations', '-'):<6}")


def main():
    import os

    parser = argparse.ArgumentParser(description="Vintage Data Downloader (Anu Variant Standard)")
    sub = parser.add_subparsers(dest="command")

    # download
    p_dl = sub.add_parser("download", help="Download vintage data")
    p_dl.add_argument("--series", nargs="+", required=True, help="Series IDs to download")
    p_dl.add_argument("--source", default="alfred", choices=["alfred", "bea", "philly_fed"],
                      help="Data source")
    p_dl.add_argument("--vintage", required=True, help="Vintage date (YYYY-MM-DD for ALFRED)")
    p_dl.add_argument("--output", required=True, help="Output directory")
    p_dl.add_argument("--api-key", default=os.environ.get("FRED_API_KEY", ""),
                      help="API key (or set FRED_API_KEY env var)")

    # catalog
    p_cat = sub.add_parser("catalog", help="Show download catalog")
    p_cat.add_argument("--catalog", required=True, help="Path to VINTAGE_DOWNLOAD_LOG.json")
    p_cat.add_argument("--series", help="Filter by series")
    p_cat.add_argument("--source", help="Filter by source")

    args = parser.parse_args()

    if args.command == "download":
        cli_download(args)
    elif args.command == "catalog":
        cli_catalog(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
