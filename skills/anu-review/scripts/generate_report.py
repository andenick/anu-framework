#!/usr/bin/env python3
"""
generate_report.py - Anu Review Report Generator

Part of the Anu Review tool suite.
Generates formatted markdown reports from review results.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


def generate_review_report(
    chapter_num: int,
    chapter_title: str,
    series_ids: List[str],
    dimensions: Dict[str, Any],
    overall_score: float,
    certification_level: str,
    gaps: List[str],
    action_items: List[tuple]
) -> str:
    """
    Generate a complete Anu Review report in markdown format.
    
    Args:
        chapter_num: Chapter number
        chapter_title: Chapter title
        series_ids: List of series IDs
        dimensions: Dictionary of dimension scores
        overall_score: Overall integration score
        certification_level: Certification level
        gaps: List of identified gaps
        action_items: List of (priority, action) tuples
        
    Returns:
        Formatted markdown report string
    """
    
    report_lines = []
    
    # Header
    report_lines.append(f"# Anu Review Report: Chapter {chapter_num}")
    report_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"\n**Tool:** Anu Review v1.0")
    report_lines.append("")
    
    # Quick Reference
    report_lines.append("## Quick Reference\n")
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Chapter | {chapter_num} |")
    report_lines.append(f"| Title | {chapter_title or 'N/A'} |")
    report_lines.append(f"| Series Count | {len(series_ids)} |")
    report_lines.append(f"| Series Range | {series_ids[0] if series_ids else 'N/A'} - {series_ids[-1] if series_ids else 'N/A'} |")
    report_lines.append(f"| Integration Score | **{overall_score:.0%}** |")
    report_lines.append(f"| Status | **{certification_level}** |")
    report_lines.append("")
    
    # Score interpretation
    if certification_level == "EXEMPLARY":
        report_lines.append("> This chapter is a **reference implementation** that exceeds all standards.")
    elif certification_level == "COMPLETE":
        report_lines.append("> This chapter is **fully integrated** and meets all core requirements.")
    elif certification_level == "ADEQUATE":
        report_lines.append("> This chapter is **functional** but has documented gaps that should be addressed.")
    else:
        report_lines.append("> This chapter is **incomplete** and requires attention before production use.")
    report_lines.append("")
    
    # Dimension Scores
    report_lines.append("---\n")
    report_lines.append("## Dimension Scores\n")
    report_lines.append("| Dimension | Weight | Score | Status |")
    report_lines.append("|-----------|--------|-------|--------|")
    
    for dim_key, dim in dimensions.items():
        status = "✓" if dim.score >= 0.85 else ("~" if dim.score >= 0.70 else "✗")
        report_lines.append(f"| {dim.name} | {dim.weight:.0%} | {dim.score:.0%} | {status} |")
    
    report_lines.append("")
    
    # Dimension Details
    report_lines.append("---\n")
    report_lines.append("## Dimension Details\n")
    
    for dim_key, dim in dimensions.items():
        report_lines.append(f"### {dim.name} ({dim.score:.0%})\n")
        report_lines.append(f"**Weight:** {dim.weight:.0%}")
        report_lines.append(f"\n**Details:** {dim.details}")
        
        if dim.issues:
            report_lines.append("\n**Issues:**")
            for issue in dim.issues[:5]:  # Limit to 5 issues
                report_lines.append(f"- {issue}")
            if len(dim.issues) > 5:
                report_lines.append(f"- ... and {len(dim.issues) - 5} more issues")
        else:
            report_lines.append("\n**Issues:** None")
        
        report_lines.append("")
    
    # Gap Analysis
    report_lines.append("---\n")
    report_lines.append("## Gap Analysis\n")
    
    if gaps:
        # Group gaps by severity
        high_gaps = [g for g in gaps if "not found" in g.lower() or "missing" in g.lower()]
        med_gaps = [g for g in gaps if g not in high_gaps and ("incomplete" in g.lower() or "not" in g.lower())]
        low_gaps = [g for g in gaps if g not in high_gaps and g not in med_gaps]
        
        if high_gaps:
            report_lines.append("### Critical Gaps\n")
            for gap in high_gaps[:10]:
                report_lines.append(f"- {gap}")
            report_lines.append("")
        
        if med_gaps:
            report_lines.append("### Moderate Gaps\n")
            for gap in med_gaps[:10]:
                report_lines.append(f"- {gap}")
            report_lines.append("")
        
        if low_gaps:
            report_lines.append("### Minor Gaps\n")
            for gap in low_gaps[:10]:
                report_lines.append(f"- {gap}")
            report_lines.append("")
    else:
        report_lines.append("No gaps identified. All checks passed.\n")
    
    # Action Items
    report_lines.append("---\n")
    report_lines.append("## Action Items\n")
    
    if action_items:
        high_actions = [(p, a) for p, a in action_items if p == "HIGH"]
        med_actions = [(p, a) for p, a in action_items if p == "MED"]
        low_actions = [(p, a) for p, a in action_items if p == "LOW"]
        
        if high_actions:
            report_lines.append("### High Priority\n")
            for _, action in high_actions:
                report_lines.append(f"- [ ] {action}")
            report_lines.append("")
        
        if med_actions:
            report_lines.append("### Medium Priority\n")
            for _, action in med_actions:
                report_lines.append(f"- [ ] {action}")
            report_lines.append("")
        
        if low_actions:
            report_lines.append("### Low Priority\n")
            for _, action in low_actions:
                report_lines.append(f"- [ ] {action}")
            report_lines.append("")
    else:
        report_lines.append("No action items required. Chapter is fully integrated.\n")
    
    # Series Inventory
    report_lines.append("---\n")
    report_lines.append("## Series Inventory\n")
    
    if series_ids:
        report_lines.append("| Series ID | Status |")
        report_lines.append("|-----------|--------|")
        for sid in series_ids:
            report_lines.append(f"| {sid} | Included |")
    else:
        report_lines.append("No series IDs provided for review.\n")
    
    report_lines.append("")
    
    # Footer
    report_lines.append("---\n")
    report_lines.append("## Methodology\n")
    report_lines.append("This review was conducted using the Anu Review tool, which validates compliance with:\n")
    report_lines.append("- **Anu Standard v2.1** - Data provenance and quality")
    report_lines.append("- **Anu Extension Standard v1.0** - Maximum faithfulness data extension")
    report_lines.append("- **Anu Shiny Standard v1.0** - Visualization application integration")
    report_lines.append("")
    report_lines.append("For details on scoring methodology, see `/anu-review` skill documentation.")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*Generated by Anu Review v1.0 | Part of the Anu Framework*")
    
    return "\n".join(report_lines)


def generate_checklist(
    chapter_num: int,
    dimensions: Dict[str, Any]
) -> str:
    """Generate a pass/fail checklist for a chapter."""
    
    lines = []
    lines.append(f"# Anu Review Checklist: Chapter {chapter_num}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for dim_key, dim in dimensions.items():
        passed = dim.score >= 0.70
        icon = "✓" if passed else "✗"
        lines.append(f"## {icon} {dim.name} ({dim.score:.0%})\n")
        
        # Add specific checklist items based on dimension
        if dim_key == "dpr":
            lines.append("- [ ] All series have DPR files")
            lines.append("- [ ] Quick Reference tables complete")
            lines.append("- [ ] Source quotes included")
            lines.append("- [ ] Transformation chains documented")
        elif dim_key == "epr":
            lines.append("- [ ] Extended series have EPR files")
            lines.append("- [ ] Faithfulness scores calculated")
            lines.append("- [ ] Transition analysis complete")
        elif dim_key == "data":
            lines.append("- [ ] Chapter data CSV exists")
            lines.append("- [ ] Extended CSV exists (if applicable)")
            lines.append("- [ ] Column mapping correct")
        elif dim_key == "mapping":
            lines.append("- [ ] CH[X]_SERIES_MAPPING defined")
            lines.append("- [ ] All series included")
            lines.append("- [ ] Shaikh findings documented")
        elif dim_key == "charts":
            lines.append("- [ ] Helper functions defined")
            lines.append("- [ ] Specialized builders exist (if needed)")
        elif dim_key == "tests":
            lines.append("- [ ] test_chapter_XX.R exists")
            lines.append("- [ ] All test sections present")
        elif dim_key == "catalog":
            lines.append("- [ ] Figures in catalog")
            lines.append("- [ ] series_ids correct")
        elif dim_key == "knowledge":
            lines.append("- [ ] Source URLs documented")
            lines.append("- [ ] Quotes extracted")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_gap_analysis(
    chapter_num: int,
    gaps: List[str],
    action_items: List[tuple]
) -> str:
    """Generate a detailed gap analysis document."""
    
    lines = []
    lines.append(f"# Gap Analysis: Chapter {chapter_num}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    lines.append("## Summary\n")
    lines.append(f"- **Total Gaps Identified:** {len(gaps)}")
    lines.append(f"- **Action Items:** {len(action_items)}")
    
    high_count = len([a for p, a in action_items if p == "HIGH"])
    med_count = len([a for p, a in action_items if p == "MED"])
    low_count = len([a for p, a in action_items if p == "LOW"])
    
    lines.append(f"- **High Priority:** {high_count}")
    lines.append(f"- **Medium Priority:** {med_count}")
    lines.append(f"- **Low Priority:** {low_count}")
    lines.append("")
    
    lines.append("## All Gaps\n")
    for i, gap in enumerate(gaps, 1):
        lines.append(f"{i}. {gap}")
    
    lines.append("")
    lines.append("## Remediation Plan\n")
    
    for priority, action in action_items:
        lines.append(f"### [{priority}] {action}\n")
        lines.append("**Steps:**")
        lines.append("1. Identify affected files")
        lines.append("2. Apply necessary changes")
        lines.append("3. Validate with `/anu-review`")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    print("Use this module via run_review.py or import generate_review_report()")
