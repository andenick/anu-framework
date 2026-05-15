#!/usr/bin/env python3
"""
validate_dpr.py - DPR (Data Provenance Record) Validation Module

Part of the Anu Review tool suite.
Validates DPR files for completeness and compliance with Anu Standard v2.1.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DPRValidationResult:
    """Result of validating a single DPR file."""
    series_id: str
    file_exists: bool
    quick_reference: bool
    context_quotes: bool
    subsources: bool
    transformation_chain: bool
    validation_record: bool
    hdarp_linkage: bool
    score: float
    issues: List[str]


# Required sections in a DPR file
REQUIRED_SECTIONS = [
    ("Quick Reference", r"##\s*Quick Reference|^\|.*\|.*\|"),
    ("Context/Quotes", r"##\s*(Context|Theoretical|Shaikh)|>\s*[\"']"),
    ("Subsources", r"##\s*Subsources|S\d{3}[A-Z]"),
    ("Transformation Chain", r"##\s*Transformation|T\d{3}"),
    ("Validation Record", r"##\s*Validation|validated|verified"),
]


def validate_dpr_file(dpr_path: Path) -> DPRValidationResult:
    """
    Validate a single DPR file for completeness.
    
    Args:
        dpr_path: Path to the DPR markdown file
        
    Returns:
        DPRValidationResult with scores and issues
    """
    series_id = dpr_path.stem.replace("_DPR", "")
    issues = []
    
    # Check file existence
    if not dpr_path.exists():
        return DPRValidationResult(
            series_id=series_id,
            file_exists=False,
            quick_reference=False,
            context_quotes=False,
            subsources=False,
            transformation_chain=False,
            validation_record=False,
            hdarp_linkage=False,
            score=0.0,
            issues=["DPR file does not exist"]
        )
    
    # Read file content
    try:
        content = dpr_path.read_text(encoding='utf-8')
    except Exception as e:
        return DPRValidationResult(
            series_id=series_id,
            file_exists=True,
            quick_reference=False,
            context_quotes=False,
            subsources=False,
            transformation_chain=False,
            validation_record=False,
            hdarp_linkage=False,
            score=0.0,
            issues=[f"Error reading file: {e}"]
        )
    
    # Check for required sections
    quick_reference = bool(re.search(r"##\s*Quick Reference|\|\s*Series\s*\|", content, re.IGNORECASE))
    if not quick_reference:
        issues.append("Missing Quick Reference section")
    
    context_quotes = bool(re.search(r">\s*[\"'].+[\"']|##\s*(Context|Theoretical)", content, re.IGNORECASE))
    if not context_quotes:
        issues.append("Missing context quotes or theoretical section")
    
    subsources = bool(re.search(r"##\s*Subsources|S\d{3}[A-Z]", content, re.IGNORECASE))
    if not subsources:
        issues.append("Missing subsources documentation")
    
    transformation_chain = bool(re.search(r"##\s*Transformation|T\d{3}|transform", content, re.IGNORECASE))
    if not transformation_chain:
        issues.append("Missing transformation chain documentation")
    
    validation_record = bool(re.search(r"##\s*Validation|validated|verified|faithfulness", content, re.IGNORECASE))
    if not validation_record:
        issues.append("Missing validation record")
    
    hdarp_linkage = bool(re.search(r"HDARP|hdarp|extraction", content, re.IGNORECASE))
    if not hdarp_linkage:
        issues.append("No HDARP linkage documented (may be acceptable)")
    
    # Calculate score (weighted)
    score_items = [
        (quick_reference, 0.25),
        (context_quotes, 0.20),
        (subsources, 0.20),
        (transformation_chain, 0.20),
        (validation_record, 0.10),
        (hdarp_linkage, 0.05),
    ]
    score = sum(weight for present, weight in score_items if present)
    
    return DPRValidationResult(
        series_id=series_id,
        file_exists=True,
        quick_reference=quick_reference,
        context_quotes=context_quotes,
        subsources=subsources,
        transformation_chain=transformation_chain,
        validation_record=validation_record,
        hdarp_linkage=hdarp_linkage,
        score=score,
        issues=issues
    )


def validate_chapter_dprs(
    docs_dir: Path,
    series_ids: List[str]
) -> Tuple[float, List[DPRValidationResult]]:
    """
    Validate all DPR files for a chapter.
    
    Args:
        docs_dir: Path to docs/series directory
        series_ids: List of series IDs to validate
        
    Returns:
        Tuple of (overall_score, list of individual results)
    """
    results = []
    
    for series_id in series_ids:
        dpr_path = docs_dir / f"{series_id}_DPR.md"
        result = validate_dpr_file(dpr_path)
        results.append(result)
    
    # Calculate overall score
    if not results:
        return 0.0, results
    
    total_score = sum(r.score for r in results) / len(results)
    return total_score, results


def format_dpr_report(results: List[DPRValidationResult]) -> str:
    """Format DPR validation results as a report section."""
    lines = ["## DPR Completeness Analysis\n"]
    
    # Summary table
    lines.append("| Series | Exists | Quick Ref | Context | Subsources | Transform | Validation | Score |")
    lines.append("|--------|--------|-----------|---------|------------|-----------|------------|-------|")
    
    for r in results:
        check = lambda x: "✓" if x else "✗"
        lines.append(
            f"| {r.series_id} | {check(r.file_exists)} | {check(r.quick_reference)} | "
            f"{check(r.context_quotes)} | {check(r.subsources)} | {check(r.transformation_chain)} | "
            f"{check(r.validation_record)} | {r.score:.0%} |"
        )
    
    # Issues section
    all_issues = [(r.series_id, issue) for r in results for issue in r.issues]
    if all_issues:
        lines.append("\n### Issues Found\n")
        for series_id, issue in all_issues:
            lines.append(f"- **{series_id}**: {issue}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: validate_dpr.py <docs_dir> <series_id1> [series_id2] ...")
        sys.exit(1)
    
    docs_dir = Path(sys.argv[1])
    series_ids = sys.argv[2:]
    
    score, results = validate_chapter_dprs(docs_dir, series_ids)
    print(f"\nOverall DPR Score: {score:.0%}")
    print(format_dpr_report(results))
