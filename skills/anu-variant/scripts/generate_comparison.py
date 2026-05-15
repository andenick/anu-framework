#!/usr/bin/env python3
"""
Cross-Variant Comparison Generator
====================================

Part of the Anu Variant Standard v1.0.

Generates standardized comparison outputs for all variants of a given metric:
  1. Combined CSV with year-indexed columns per variant
  2. Correlation matrix
  3. Sign-change analysis
  4. Summary statistics

Usage:
  python generate_comparison.py --registry REGISTRY.json --metric SW01 \
      --output comparison_output.csv [--report comparison_report.md]
"""

import json
import sys
import argparse
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

sys.path.insert(0, str(Path(__file__).parent))
from variant_registry import VariantRegistry


def load_variant_data(registry: VariantRegistry, metric: str, project_root: Path) -> dict:
    """Load output CSVs for all variants of a metric. Returns {variant_id: DataFrame}."""
    variants = registry.get_metric_variants(metric)
    data = {}
    for v in variants:
        # Try full_period first, then book_period
        for key in ["full_period", "moos_period", "book_period"]:
            rel_path = v.output_files.get(key)
            if rel_path:
                full_path = project_root / rel_path
                if full_path.exists():
                    df = pd.read_csv(full_path)
                    data[v.variant_id] = df
                    print(f"  Loaded {v.variant_id}: {full_path.name} ({len(df)} rows)")
                    break
        else:
            print(f"  WARNING: No output file found for {v.variant_id}")
    return data


def build_comparison_csv(variant_data: dict, output_path: Path) -> pd.DataFrame:
    """Build combined comparison CSV."""
    # Collect all years
    all_years = set()
    for df in variant_data.values():
        if "year" in df.columns:
            all_years.update(df["year"].tolist())
    all_years = sorted(all_years)

    rows = []
    for year in all_years:
        row = {"year": int(year)}
        for vid, df in variant_data.items():
            yr_data = df[df["year"] == year]
            if not yr_data.empty:
                r = yr_data.iloc[0]
                row[f"{vid}_nsw"] = r.get("NSW", np.nan)
                row[f"{vid}_nsw_gdp"] = r.get("NSW_GDP_ratio", np.nan)
                for col in ["E1", "E2", "T1", "T2", "LS"]:
                    if col in r:
                        row[f"{vid}_{col}"] = r[col]
        rows.append(row)

    comp_df = pd.DataFrame(rows)
    comp_df.to_csv(output_path, index=False)
    print(f"\n  Saved comparison CSV: {output_path} ({len(comp_df)} rows)")
    return comp_df


def compute_correlation_matrix(comp_df: pd.DataFrame, variant_ids: list) -> pd.DataFrame:
    """Compute pairwise correlations for NSW values."""
    nsw_cols = [f"{vid}_nsw" for vid in variant_ids if f"{vid}_nsw" in comp_df.columns]
    sub = comp_df[nsw_cols].dropna()
    if sub.empty:
        return pd.DataFrame()
    return sub.corr()


def compute_sign_changes(comp_df: pd.DataFrame, variant_ids: list) -> pd.DataFrame:
    """Find years where variants disagree on sign."""
    nsw_cols = [f"{vid}_nsw" for vid in variant_ids if f"{vid}_nsw" in comp_df.columns]
    disagreements = []
    for _, row in comp_df.iterrows():
        signs = {}
        for col in nsw_cols:
            val = row.get(col)
            if pd.notna(val):
                signs[col] = "POS" if val >= 0 else "NEG"
        if len(set(signs.values())) > 1:
            disagreements.append({
                "year": int(row["year"]),
                **{col.replace("_nsw", "_sign"): s for col, s in signs.items()},
                **{col: row[col] for col in nsw_cols if pd.notna(row.get(col))},
            })
    return pd.DataFrame(disagreements)


def compute_summary_stats(comp_df: pd.DataFrame, variant_ids: list) -> pd.DataFrame:
    """Compute summary statistics per variant."""
    stats = []
    for vid in variant_ids:
        col = f"{vid}_nsw"
        if col not in comp_df.columns:
            continue
        series = comp_df[col].dropna()
        if series.empty:
            continue
        stats.append({
            "variant_id": vid,
            "count": len(series),
            "mean": round(series.mean(), 2),
            "std": round(series.std(), 2),
            "min": round(series.min(), 2),
            "min_year": int(comp_df.loc[series.idxmin(), "year"]),
            "max": round(series.max(), 2),
            "max_year": int(comp_df.loc[series.idxmax(), "year"]),
            "n_positive": int((series >= 0).sum()),
            "n_negative": int((series < 0).sum()),
        })
    return pd.DataFrame(stats)


def generate_report(comp_df: pd.DataFrame, variant_ids: list,
                    corr_matrix: pd.DataFrame, sign_changes: pd.DataFrame,
                    summary_stats: pd.DataFrame, report_path: Path) -> None:
    """Generate a markdown comparison report."""
    lines = [
        "# Cross-Variant Comparison Report",
        "",
        f"**Metric**: {variant_ids[0].split('-')[1] if variant_ids else 'Unknown'}",
        f"**Variants**: {', '.join(variant_ids)}",
        f"**Years**: {int(comp_df['year'].min())}-{int(comp_df['year'].max())}",
        f"**Generated**: {pd.Timestamp.now().isoformat()}",
        "",
        "---",
        "",
        "## Summary Statistics",
        "",
        summary_stats.to_markdown(index=False) if not summary_stats.empty else "No data.",
        "",
        "---",
        "",
        "## Correlation Matrix (NSW Values)",
        "",
        corr_matrix.to_markdown() if not corr_matrix.empty else "Insufficient data.",
        "",
        "---",
        "",
        "## Sign Disagreements",
        "",
        f"Years where variants disagree on sign: **{len(sign_changes)}**",
        "",
    ]
    if not sign_changes.empty:
        lines.append(sign_changes.to_markdown(index=False))
    else:
        lines.append("No sign disagreements found.")

    lines.extend(["", "---", "", "*Generated following Anu Variant Standard v1.0*"])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved report: {report_path}")


def main():
    if not HAS_DEPS:
        print("ERROR: pandas and numpy required. Install with: pip install pandas numpy")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate cross-variant comparison")
    parser.add_argument("--registry", required=True, help="Path to VARIANT_REGISTRY.json")
    parser.add_argument("--metric", required=True, help="Metric code (e.g., SW01)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--project-root", help="Project root (default: registry parent's parent)")
    args = parser.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.exists():
        print(f"ERROR: Registry not found: {reg_path}")
        sys.exit(1)

    registry = VariantRegistry(reg_path)
    registry.load()

    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = reg_path.parent.parent.parent

    print(f"Loading variant data for metric: {args.metric}")
    variant_data = load_variant_data(registry, args.metric, project_root)
    if not variant_data:
        print("ERROR: No variant data loaded.")
        sys.exit(1)

    variant_ids = list(variant_data.keys())
    output_path = Path(args.output)

    # Build comparison CSV
    comp_df = build_comparison_csv(variant_data, output_path)

    # Analyses
    print("\nAnalyses:")
    corr = compute_correlation_matrix(comp_df, variant_ids)
    if not corr.empty:
        print("\n  Correlation Matrix:")
        print(corr.to_string())

    sign_changes = compute_sign_changes(comp_df, variant_ids)
    print(f"\n  Sign disagreements: {len(sign_changes)} years")

    summary = compute_summary_stats(comp_df, variant_ids)
    if not summary.empty:
        print("\n  Summary Statistics:")
        print(summary.to_string(index=False))

    # Optional report
    if args.report:
        generate_report(comp_df, variant_ids, corr, sign_changes, summary, Path(args.report))

    print("\nDone.")


if __name__ == "__main__":
    main()
